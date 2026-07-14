import Foundation

struct OperatorState: Decodable, Sendable {
    struct Service: Decodable, Sendable {
        let name: String
        let version: String
        let status: String
        let profile: String
        let transport: String
    }

    struct Application: Decodable, Sendable {
        let name: String
        let surface: String
        let browserRequired: Bool
    }

    struct OperatorContext: Decodable, Sendable {
        let cadence: String
        let authorityEffect: String
    }

    struct ClassificationState: Decodable, Sendable {
        let requested: String
        let status: String
        let reasons: [String]
    }

    struct ModelState: Decodable, Sendable {
        let primaryCandidate: String
        let sufficiency: String
        let activeRoute: String
        let externalApiAllowed: Bool
    }

    struct ProofState: Decodable, Sendable {
        let posture: String
        let production: Bool
        let highNofornProcessing: Bool
    }

    struct StorageState: Decodable, Sendable {
        let backend: String
        let durable: Bool
        let credentialExposedToModel: Bool
    }

    let service: Service
    let application: Application
    let operatorContext: OperatorContext
    let classification: ClassificationState
    let model: ModelState
    let proof: ProofState
    let storage: StorageState
    let nextSafeAction: String
    let requirements: [String]
}

enum APIError: LocalizedError {
    case invalidResponse
    case unhealthy(Int)

    var errorDescription: String? {
        switch self {
        case .invalidResponse:
            return "The local METAXIS service returned an invalid response."
        case .unhealthy(let status):
            return "The local METAXIS service returned HTTP \(status)."
        }
    }
}

@MainActor
final class AppModel: ObservableObject {
    struct DisplayTurn: Identifiable, Sendable {
        let id: String
        let operatorText: String
        let assistantText: String
        let route: String
    }

    private struct ThreadCreated: Decodable {
        let id: String
    }

    private struct TurnCreated: Decodable {
        let id: String
        let `operator`: String
        let assistant: String
        let route: String
    }

    @Published private(set) var state: OperatorState?
    @Published private(set) var isLoading = false
    @Published private(set) var isSending = false
    @Published private(set) var errorMessage: String?
    @Published private(set) var turns: [DisplayTurn] = []
    @Published var draft = ""

    private let baseURL = URL(string: "http://127.0.0.1:4310")!
    private let stateURL = URL(string: "http://127.0.0.1:4310/api/v1/operator-state")!
    private var threadID: String?

    func refresh() async {
        isLoading = true
        defer { isLoading = false }
        do {
            let (data, response) = try await URLSession.shared.data(from: stateURL)
            guard let http = response as? HTTPURLResponse else {
                throw APIError.invalidResponse
            }
            guard http.statusCode == 200 else {
                throw APIError.unhealthy(http.statusCode)
            }
            let decoder = JSONDecoder()
            decoder.keyDecodingStrategy = .convertFromSnakeCase
            state = try decoder.decode(OperatorState.self, from: data)
            errorMessage = nil
        } catch {
            state = nil
            errorMessage = error.localizedDescription
        }
    }

    func submit() async {
        let text = draft.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty, !isSending else { return }
        isSending = true
        defer { isSending = false }
        do {
            if threadID == nil {
                let created: ThreadCreated = try await post(
                    path: "/api/v1/threads", value: ["title": "NemaShells task"]
                )
                threadID = created.id
            }
            guard let threadID else { throw APIError.invalidResponse }
            let turn: TurnCreated = try await post(
                path: "/api/v1/threads/\(threadID)/turns",
                value: ["text": text, "classification": "DEVELOPMENT"]
            )
            turns.append(
                DisplayTurn(
                    id: turn.id,
                    operatorText: turn.operator,
                    assistantText: turn.assistant,
                    route: turn.route
                )
            )
            draft = ""
            errorMessage = nil
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    private func post<Response: Decodable>(
        path: String, value: [String: String]
    ) async throws -> Response {
        var request = URLRequest(url: baseURL.appending(path: path))
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.httpBody = try JSONEncoder().encode(value)
        let (data, response) = try await URLSession.shared.data(for: request)
        guard let http = response as? HTTPURLResponse else {
            throw APIError.invalidResponse
        }
        guard 200..<300 ~= http.statusCode else {
            throw APIError.unhealthy(http.statusCode)
        }
        let decoder = JSONDecoder()
        decoder.keyDecodingStrategy = .convertFromSnakeCase
        return try decoder.decode(Response.self, from: data)
    }
}
