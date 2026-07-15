// swift-tools-version: 6.0
import PackageDescription

let package = Package(
    name: "NemaShells",
    platforms: [.macOS(.v14)],
    products: [
        .executable(name: "NemaShells", targets: ["NemaShells"])
    ],
    targets: [
        .executableTarget(name: "NemaShells")
    ]
)
