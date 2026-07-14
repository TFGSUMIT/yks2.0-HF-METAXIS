import SwiftUI

struct ContentView: View {
    @StateObject private var model = AppModel()
    @State private var selection = "Phase 0 delivery"

    private let tasks = [
        "Phase 0 delivery",
        "HIGH / NOFORN gate",
        "Proxmox profile",
        "Model evaluation"
    ]

    var body: some View {
        NavigationSplitView {
            sidebar
                .navigationSplitViewColumnWidth(min: 218, ideal: 244, max: 280)
        } content: {
            workspace
                .navigationSplitViewColumnWidth(min: 580, ideal: 720)
        } detail: {
            inspector
                .navigationSplitViewColumnWidth(min: 292, ideal: 330, max: 380)
        }
        .background(Color(nsColor: .windowBackgroundColor))
        .task { await model.refresh() }
    }

    private var sidebar: some View {
        VStack(alignment: .leading, spacing: 0) {
            HStack(spacing: 10) {
                ZStack {
                    RoundedRectangle(cornerRadius: 9)
                        .fill(.white)
                        .frame(width: 32, height: 32)
                    Image(systemName: "mountain.2.fill")
                        .foregroundStyle(.black)
                }
                VStack(alignment: .leading, spacing: 1) {
                    Text("NemaShells").font(.headline)
                    Text("METAXIS operator").font(.caption).foregroundStyle(.secondary)
                }
                Spacer()
            }
            .padding(16)

            Button(action: {}) {
                Label("New task", systemImage: "square.and.pencil")
                    .frame(maxWidth: .infinity, alignment: .leading)
            }
            .buttonStyle(.borderedProminent)
            .tint(Color.white.opacity(0.12))
            .padding(.horizontal, 12)

            Text("TASKS")
                .font(.caption2.weight(.semibold))
                .foregroundStyle(.secondary)
                .padding(.horizontal, 16)
                .padding(.top, 22)
                .padding(.bottom, 7)

            ForEach(tasks, id: \.self) { task in
                Button {
                    selection = task
                } label: {
                    HStack(spacing: 9) {
                        Image(systemName: taskIcon(task))
                            .frame(width: 18)
                        Text(task).lineLimit(1)
                        Spacer()
                    }
                    .padding(.horizontal, 12)
                    .padding(.vertical, 8)
                    .background(
                        RoundedRectangle(cornerRadius: 7)
                            .fill(selection == task ? Color.white.opacity(0.10) : .clear)
                    )
                }
                .buttonStyle(.plain)
                .padding(.horizontal, 6)
            }

            Spacer()
            Divider()
            HStack(spacing: 8) {
                Circle()
                    .fill(model.state?.service.status == "HEALTHY" ? .green : .orange)
                    .frame(width: 8, height: 8)
                VStack(alignment: .leading, spacing: 1) {
                    Text(model.state?.service.profile ?? "connecting")
                        .font(.caption.weight(.medium))
                    Text("OrbStack · Docker · loopback")
                        .font(.caption2).foregroundStyle(.secondary)
                }
            }
            .padding(14)
        }
        .background(Color.black.opacity(0.22))
    }

    private var workspace: some View {
        VStack(spacing: 0) {
            HStack {
                VStack(alignment: .leading, spacing: 2) {
                    Text(selection).font(.title3.weight(.semibold))
                    Text("Capability #474 · Story #475 · Task #476")
                        .font(.caption).foregroundStyle(.secondary)
                }
                Spacer()
                StatusPill(
                    text: model.state?.classification.status ?? "CONNECTING",
                    color: model.state?.classification.status == "BLOCKED" ? .red : .orange
                )
                Button {
                    Task { await model.refresh() }
                } label: {
                    Image(systemName: "arrow.clockwise")
                }
                .buttonStyle(.borderless)
                .help("Refresh local readback")
            }
            .padding(.horizontal, 22)
            .padding(.vertical, 14)
            .background(.ultraThinMaterial)

            ScrollView {
                LazyVStack(alignment: .leading, spacing: 22) {
                    MessageRow(role: "NS", name: "NemaShells", tint: .mint) {
                        VStack(alignment: .leading, spacing: 12) {
                            Text("The local METAXIS plane is ready for development.")
                                .font(.body.weight(.medium))
                            Text("This installed application is connected to the Docker service inside OrbStack. External model calls are disabled; HIGH/NOFORN remains fail-closed until its complete Proxmox execution profile is accepted.")
                                .foregroundStyle(.secondary)
                            HStack {
                                Tag(text: "native app")
                                Tag(text: "loopback only")
                                Tag(text: "mock brain")
                            }
                        }
                    }

                    MessageRow(role: "YO", name: "Operator outcome", tint: .blue) {
                        VStack(alignment: .leading, spacing: 11) {
                            Text("Start machine → log in → open NemaShells")
                                .font(.body.weight(.semibold))
                            OutcomeRow(icon: "desktopcomputer", text: "OrbStack substitutes for Proxmox on this laptop")
                            OutcomeRow(icon: "shippingbox.fill", text: "The same hardened Docker image moves to the Proxmox VM")
                            OutcomeRow(icon: "lock.shield.fill", text: "The Mac app owns presentation only")
                        }
                    }

                    if let error = model.errorMessage {
                        MessageRow(role: "!", name: "Local service unavailable", tint: .orange) {
                            VStack(alignment: .leading, spacing: 8) {
                                Text(error)
                                Text("Start the Ubuntu machine and run `nemashells` again. No external provider fallback was attempted.")
                                    .foregroundStyle(.secondary)
                            }
                        }
                    }

                    if let state = model.state {
                        MessageRow(role: "MX", name: "Deterministic readback", tint: .purple) {
                            VStack(alignment: .leading, spacing: 10) {
                                Text(state.nextSafeAction)
                                HStack {
                                    Tag(text: state.proof.posture)
                                    Tag(text: state.model.sufficiency.lowercased())
                                    Tag(text: state.operatorContext.cadence)
                                }
                            }
                        }
                    }

                    ForEach(model.turns) { turn in
                        MessageRow(role: "YO", name: "You", tint: .blue) {
                            Text(turn.operatorText)
                        }
                        MessageRow(role: "NS", name: "NemaShells · \(turn.route)", tint: .mint) {
                            Text(turn.assistantText)
                        }
                    }
                }
                .padding(24)
                .frame(maxWidth: 820, alignment: .leading)
                .frame(maxWidth: .infinity)
            }

            composer
        }
    }

    private var composer: some View {
        VStack(spacing: 8) {
            HStack(alignment: .bottom, spacing: 10) {
                TextField("Message NemaShells (development route)", text: $model.draft, axis: .vertical)
                    .textFieldStyle(.plain)
                    .lineLimit(1...5)
                    .padding(11)
                    .onSubmit { Task { await model.submit() } }
                Button {
                    Task { await model.submit() }
                } label: {
                    Image(systemName: "arrow.up")
                        .font(.system(size: 14, weight: .bold))
                        .frame(width: 29, height: 29)
                }
                .buttonStyle(.borderedProminent)
                .tint(.white)
                .foregroundStyle(.black)
                .disabled(
                    model.isSending
                    || model.draft.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty
                )
                .padding(7)
            }
            .background(RoundedRectangle(cornerRadius: 12).fill(Color.white.opacity(0.055)))
            .overlay(RoundedRectangle(cornerRadius: 12).stroke(Color.white.opacity(0.09)))
            HStack {
                Image(systemName: "shield.lefthalf.filled")
                Text("DEVELOPMENT · synthetic/public data only · consequential actions disabled")
                Spacer()
            }
            .font(.caption2)
            .foregroundStyle(.secondary)
        }
        .padding(14)
        .background(.ultraThinMaterial)
    }

    private var inspector: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 18) {
                InspectorHeader(title: "Runtime", icon: "waveform.path.ecg")
                ReadbackCard(rows: [
                    ("Service", model.state?.service.status ?? "connecting"),
                    ("Profile", model.state?.service.profile ?? "—"),
                    ("Transport", model.state?.service.transport ?? "—"),
                    ("Surface", "native installed app")
                ])

                InspectorHeader(title: "Classification", icon: "lock.shield")
                VStack(alignment: .leading, spacing: 10) {
                    StatusPill(text: "HIGH / NOFORN", color: .red)
                    Text(model.state?.classification.reasons.first ?? "Waiting for deterministic policy readback.")
                        .font(.caption).foregroundStyle(.secondary)
                    Label("No public API fallback", systemImage: "xmark.circle.fill")
                        .font(.caption.weight(.medium)).foregroundStyle(.red)
                }
                .cardStyle()

                InspectorHeader(title: "Brain", icon: "cpu")
                ReadbackCard(rows: [
                    ("Candidate", "Nemotron 3 Nano 30B-A3B"),
                    ("Active", model.state?.model.activeRoute ?? "—"),
                    ("Quality", model.state?.model.sufficiency ?? "—"),
                    ("External API", "denied")
                ])

                InspectorHeader(title: "Deployment", icon: "server.rack")
                VStack(alignment: .leading, spacing: 8) {
                    DeploymentStep(number: "1", title: "OrbStack", detail: "laptop development")
                    DeploymentStep(number: "2", title: "Docker", detail: "immutable workload")
                    DeploymentStep(number: "3", title: "Proxmox", detail: "target substrate")
                }
                .cardStyle()

                InspectorHeader(title: "Proof", icon: "checkmark.seal")
                ReadbackCard(rows: [
                    ("Posture", model.state?.proof.posture ?? "—"),
                    ("Production", "not claimed"),
                    ("HIGH/NOFORN", "blocked")
                ])
            }
            .padding(16)
        }
        .background(Color.black.opacity(0.14))
    }

    private func taskIcon(_ task: String) -> String {
        switch task {
        case "HIGH / NOFORN gate": return "lock.shield"
        case "Proxmox profile": return "server.rack"
        case "Model evaluation": return "cpu"
        default: return "bubble.left.and.text.bubble.right"
        }
    }
}

private struct StatusPill: View {
    let text: String
    let color: Color
    var body: some View {
        HStack(spacing: 6) {
            Circle().fill(color).frame(width: 6, height: 6)
            Text(text).font(.caption2.weight(.bold))
        }
        .padding(.horizontal, 9).padding(.vertical, 5)
        .background(Capsule().fill(color.opacity(0.13)))
        .overlay(Capsule().stroke(color.opacity(0.30)))
    }
}

private struct Tag: View {
    let text: String
    var body: some View {
        Text(text)
            .font(.caption2.weight(.medium))
            .padding(.horizontal, 8).padding(.vertical, 4)
            .background(Capsule().fill(Color.white.opacity(0.07)))
            .foregroundStyle(.secondary)
    }
}

private struct MessageRow<Content: View>: View {
    let role: String
    let name: String
    let tint: Color
    @ViewBuilder let content: Content

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            Text(role)
                .font(.caption2.weight(.black))
                .foregroundStyle(.black)
                .frame(width: 30, height: 30)
                .background(RoundedRectangle(cornerRadius: 8).fill(tint))
            VStack(alignment: .leading, spacing: 9) {
                Text(name).font(.caption.weight(.semibold)).foregroundStyle(.secondary)
                content
            }
            Spacer(minLength: 0)
        }
    }
}

private struct OutcomeRow: View {
    let icon: String
    let text: String
    var body: some View {
        Label(text, systemImage: icon)
            .font(.callout)
            .foregroundStyle(.secondary)
    }
}

private struct InspectorHeader: View {
    let title: String
    let icon: String
    var body: some View {
        Label(title, systemImage: icon)
            .font(.caption.weight(.bold))
            .foregroundStyle(.secondary)
            .textCase(.uppercase)
    }
}

private struct ReadbackCard: View {
    let rows: [(String, String)]
    var body: some View {
        VStack(spacing: 9) {
            ForEach(Array(rows.enumerated()), id: \.offset) { index, row in
                HStack(alignment: .firstTextBaseline) {
                    Text(row.0).foregroundStyle(.secondary)
                    Spacer()
                    Text(row.1).multilineTextAlignment(.trailing)
                }
                .font(.caption)
                if index < rows.count - 1 { Divider().opacity(0.5) }
            }
        }
        .cardStyle()
    }
}

private struct DeploymentStep: View {
    let number: String
    let title: String
    let detail: String
    var body: some View {
        HStack {
            Text(number)
                .font(.caption2.weight(.bold))
                .frame(width: 21, height: 21)
                .background(Circle().fill(Color.white.opacity(0.10)))
            VStack(alignment: .leading, spacing: 1) {
                Text(title).font(.caption.weight(.semibold))
                Text(detail).font(.caption2).foregroundStyle(.secondary)
            }
            Spacer()
        }
    }
}

private extension View {
    func cardStyle() -> some View {
        self
            .padding(12)
            .background(RoundedRectangle(cornerRadius: 10).fill(Color.white.opacity(0.045)))
            .overlay(RoundedRectangle(cornerRadius: 10).stroke(Color.white.opacity(0.07)))
    }
}
