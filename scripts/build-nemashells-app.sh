#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
PACKAGE="$ROOT/apps/nemashells-macos"
BUILD_ROOT="$ROOT/.build/nemashells"
APP="$BUILD_ROOT/NemaShells.app"

swift build --package-path "$PACKAGE" --scratch-path "$BUILD_ROOT/swift" -c release
rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources"
cp "$PACKAGE/Resources/Info.plist" "$APP/Contents/Info.plist"
cp "$BUILD_ROOT/swift/release/NemaShells" "$APP/Contents/MacOS/NemaShells"
codesign --force --deep --sign - "$APP"
printf '%s\n' "$APP"
