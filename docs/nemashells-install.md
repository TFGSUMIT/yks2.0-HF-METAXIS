# NemaShells installation and operator journey

NemaShells is a native installed macOS application. It is not a browser UI.
The METAXIS service runs in a hardened container on OrbStack's managed Docker
engine and is published only on loopback. The Ubuntu machine provides the
isolated operator login and guest launcher; the app contains presentation state
only. This avoids running a second nested Docker daemon in a small machine.

## One-time bootstrap

From macOS Terminal, run from this repository:

```sh
./scripts/install-nemashells-orbstack.sh
```

The script does not install Homebrew, npm, Rust, Docker Desktop, or global
Python packages on macOS. It builds the checked-in Swift application with the
Apple toolchain already present, installs it under `~/Applications`, builds the
pinned `metaxis:<revision>` image on OrbStack's managed Docker engine, enables
container restart, and installs the `nemashells` launcher inside Ubuntu.
The guest launcher reaches the loopback-published service through OrbStack's
private `host.internal` bridge; it is not exposed on the LAN.

## Normal operation

```sh
orb start ubuntu
orb -m ubuntu
nemashells
```

The `nemashells` guest command health-checks the container and uses OrbStack's
host `open` bridge to launch the installed native app. It does not open a web
browser.

## Security posture

- Mac: presentation-only native app; no model, credentials, workspaces, or
  durable runtime authority.
- OrbStack managed Docker: development runtime and container lifecycle.
- OrbStack Ubuntu: isolated login and native-app launcher.
- Container: non-root, read-only root filesystem, dropped capabilities,
  no-new-privileges, loopback-only published port, external model calls off.
- Data: synthetic/public/explicitly approved non-sensitive development data
  only.
- HIGH/NOFORN: visible and fail-closed as `BLOCKED` until a separately accepted
  execution profile satisfies every hard gate.

OrbStack is the laptop development substitute for Proxmox. The production
deployment profile is Proxmox/KVM -> Debian VM -> systemd -> Docker -> the same
image and service contract.
