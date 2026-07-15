import SwiftUI

@main
struct NemaShellsApp: App {
    var body: some Scene {
        WindowGroup {
            ContentView()
                .frame(minWidth: 1120, minHeight: 720)
                .preferredColorScheme(.dark)
        }
        .windowStyle(.hiddenTitleBar)
        .commands {
            CommandGroup(replacing: .newItem) {}
        }
    }
}
