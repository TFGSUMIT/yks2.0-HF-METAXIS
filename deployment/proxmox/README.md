# Proxmox deployment profile

This profile preserves the same NemaShells workload used in OrbStack while
moving the virtualization boundary to the YKS production-standard stack:

`Proxmox/KVM -> Debian-compatible VM -> systemd -> Docker -> METAXIS`

The VM baseline must provide Docker Engine, systemd, a loopback-only published
port for the service, approved administration, snapshot/restore, storage,
logging, time sync, and network policy. Copy a release into `/opt/metaxis`,
build or load the pinned `metaxis/nemashells:<revision>` image, install
`deployment/systemd/nemashells.service`, and set the exact image in
`/etc/metaxis/nemashells.env`.

This repository does not claim a Proxmox deployment until the target host,
VM identity, bridge, storage, snapshot, Docker version, image digest, access
boundary, and health/denial readback are recorded. HIGH/NOFORN remains blocked
until the complete U.S.-person, U.S.-location, egress, custody, provenance, and
authority gate passes.
