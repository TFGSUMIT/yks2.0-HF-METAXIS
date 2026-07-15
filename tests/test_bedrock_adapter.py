import os
import tempfile
import unittest

from metaxis.bedrock_adapter import (
    BedrockAdapter,
    BedrockConfig,
    read_assumed_role_credentials,
)
from metaxis.contracts import BrainRequest
from metaxis.policy import RouteProfile


class FakeBedrockClient:
    def __init__(self) -> None:
        self.calls = []

    def converse(self, **arguments):
        self.calls.append(arguments)
        return {
            "output": {
                "message": {
                    "content": [
                        {"text": "development response"},
                        {
                            "toolUse": {
                                "toolUseId": "call-1",
                                "name": "read_status",
                                "input": {"scope": "local"},
                            }
                        },
                    ]
                }
            },
            "usage": {"inputTokens": 100, "outputTokens": 20},
        }


def development_route() -> RouteProfile:
    return RouteProfile(
        route_id="aws-bedrock-super-development",
        provider="aws-bedrock",
        model_repository="nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16",
        model_revision="d51eab0d1f979ebc26b546e634a04f450d99158e",
        model_developer_country="US",
        runtime="amazon-bedrock-converse",
        placement="aws-us-east-1-provider-managed",
        us_person_admin_only=False,
        us_person_user_only=False,
        us_location_only=True,
        egress_default_deny=False,
        external_telemetry_disabled=False,
        credential_custody_approved=False,
        authority_record=None,
    )


class BedrockAdapterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.client = FakeBedrockClient()
        self.adapter = BedrockAdapter(
            BedrockConfig(
                region="us-east-1",
                model_id="nvidia.nemotron-super-3-120b",
                route=development_route(),
                max_output_tokens=128,
                max_input_chars=1000,
                max_request_cost_usd=0.01,
                runtime_version="boto3/test",
            ),
            self.client,
        )

    def request(self, **overrides) -> BrainRequest:
        values = {
            "request_id": "bedrock-proof",
            "messages": ({"role": "user", "content": "public test"},),
            "tools": (
                {
                    "type": "function",
                    "function": {
                        "name": "read_status",
                        "description": "Read local status",
                        "parameters": {"type": "object", "properties": {}},
                    },
                },
            ),
            "max_output_tokens": 32,
            "authority_context": {"classification": "DEVELOPMENT"},
        }
        values.update(overrides)
        return BrainRequest(**values)

    def test_development_call_is_normalized_with_cost_and_provenance(self) -> None:
        response = self.adapter.generate(self.request())

        self.assertIsNone(response.error)
        self.assertEqual(response.text, "development response")
        self.assertEqual(response.provenance.route, "aws-bedrock-super-development")
        self.assertEqual(response.input_tokens, 100)
        self.assertEqual(response.output_tokens, 20)
        self.assertAlmostEqual(response.cost_usd, 0.000028)
        self.assertEqual(response.tool_calls[0].name, "read_status")
        self.assertEqual(len(self.client.calls), 1)
        self.assertEqual(
            self.client.calls[0]["modelId"], "nvidia.nemotron-super-3-120b"
        )

    def test_system_contract_is_promoted_for_registered_nvidia_route(self) -> None:
        response = self.adapter.generate(
            self.request(
                messages=(
                    {"role": "system", "content": "return registered JSON"},
                    {"role": "user", "content": "report status"},
                )
            )
        )

        self.assertIsNone(response.error)
        call = self.client.calls[0]
        self.assertNotIn("system", call)
        first_text = call["messages"][0]["content"][0]["text"]
        self.assertIn("METAXIS CONTROL-PLANE DIRECTIVE", first_text)
        self.assertIn("return registered JSON", first_text)
        self.assertIn("OPERATOR REQUEST:\nreport status", first_text)

    def test_high_noforn_is_denied_before_client_call(self) -> None:
        response = self.adapter.generate(
            self.request(authority_context={"classification": "HIGH/NOFORN"})
        )

        self.assertEqual(response.error.code, "route_blocked")
        self.assertEqual(self.client.calls, [])

    def test_output_ceiling_is_denied_before_client_call(self) -> None:
        response = self.adapter.generate(self.request(max_output_tokens=129))

        self.assertEqual(response.error.code, "quota_exceeded")
        self.assertEqual(self.client.calls, [])

    def test_input_ceiling_is_denied_before_client_call(self) -> None:
        response = self.adapter.generate(
            self.request(messages=({"role": "user", "content": "x" * 1001},))
        )

        self.assertEqual(response.error.code, "quota_exceeded")
        self.assertEqual(self.client.calls, [])

    def test_cost_ceiling_is_denied_before_client_call(self) -> None:
        adapter = BedrockAdapter(
            BedrockConfig(
                region="us-east-1",
                model_id="nvidia.nemotron-super-3-120b",
                route=development_route(),
                max_request_cost_usd=0.000001,
            ),
            self.client,
        )
        response = adapter.generate(self.request())

        self.assertEqual(response.error.code, "cost_ceiling_exceeded")
        self.assertEqual(self.client.calls, [])

    def test_credentials_require_owner_only_file_and_expected_role(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as value:
            value.write(
                "[metaxis-bedrock]\n"
                "aws_access_key_id = test-access\n"
                "aws_secret_access_key = test-secret\n"
                "aws_session_token = test-session\n"
                "x_metaxis_principal_arn = "
                "arn:aws:sts::237575223942:assumed-role/"
                "METAXISBedrockDevelopmentRole/test\n"
            )
            path = value.name
        os.chmod(path, 0o600)
        try:
            credentials = read_assumed_role_credentials(path)
            self.assertEqual(credentials["aws_access_key_id"], "test-access")
            self.assertNotIn("x_metaxis_principal_arn", credentials)
        finally:
            os.unlink(path)

    def test_credentials_reject_root_principal(self) -> None:
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as value:
            value.write(
                "[metaxis-bedrock]\n"
                "aws_access_key_id = test-access\n"
                "aws_secret_access_key = test-secret\n"
                "aws_session_token = test-session\n"
                "x_metaxis_principal_arn = arn:aws:iam::237575223942:root\n"
            )
            path = value.name
        os.chmod(path, 0o600)
        try:
            with self.assertRaises(ValueError):
                read_assumed_role_credentials(path)
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
