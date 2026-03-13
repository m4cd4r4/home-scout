# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.x (latest) | Yes - security updates |
| 0.x (pre-release) | Best effort only |

Once version 1.0 ships, the latest minor release of each major version receives security updates. Older minor releases do not. Upgrade to the latest minor release to stay protected.

## Reporting Vulnerabilities

**Do not open a public GitHub issue for security vulnerabilities.**

Use **GitHub Security Advisories** to report vulnerabilities privately:

1. Go to the [Security Advisories page](../../security/advisories/new) for this repository
2. Click "New draft security advisory"
3. Fill in the vulnerability details
4. Submit

### What to Include

- Description of the vulnerability
- Steps to reproduce
- Affected components (firmware, ROS2 nodes, scripts, hardware design)
- Severity assessment (your estimate is fine)
- Proof of concept if you have one

### Response Timeline

| Stage | Target |
|-------|--------|
| Acknowledgment | 48 hours |
| Triage and severity assessment | 7 days |
| Fix development | 30 days (critical), 60 days (high), 90 days (medium/low) |
| Public disclosure | After fix is released, or 90 days from report - whichever comes first |

We will credit you in the advisory unless you prefer to remain anonymous.

## Scope

### In Scope

These are security issues. Report them via Security Advisories.

**Privacy bypasses:**
- Any code path that transmits data outside ScoutNet (the local network)
- Camera or microphone activation that bypasses hardware indicators
- Face embedding extraction without the encryption passphrase
- Conversation log persistence beyond the 1-hour buffer
- Object sighting data accessible without local authentication

**Firmware vulnerabilities:**
- STM32H5 firmware flaws that bypass speed limits or safety modes
- Watchdog timer bypass or misconfiguration
- Heartbeat protocol spoofing that prevents safe mode activation
- E-stop GPIO handling flaws

**Unsafe motor control:**
- Speed limit bypass (exceeding 0.3 m/s through any code path)
- Motor activation during E-stop state
- Cliff sensor or bump sensor bypass
- Geofence violation through crafted Nav2 commands

**Network security:**
- ScoutNet WPA3 implementation flaws
- Services listening on unintended interfaces
- Default credentials in any component
- Authentication bypass on the management interface

**Supply chain:**
- Compromised dependencies in ROS2 packages, Python packages, or firmware libraries
- Build reproducibility issues that could mask tampering

### Out of Scope

These are known limitations or non-issues. Do not report them as vulnerabilities.

**Physical access attacks when E-stop is available:**
Scout is a home robot. Anyone in your home has physical access. The E-stop button is the mitigation for physical threats. "An attacker with physical access can disconnect the battery" is not a vulnerability - it is the E-stop working as designed.

**Qualcomm NPU closed-source firmware:**
We know the QCS6490 NPU firmware is closed-source. We cannot audit it. Network isolation is our mitigation. See [PRIVACY.md](PRIVACY.md) for the full threat model. Theoretical NPU firmware concerns are not actionable without a specific exploit.

**Denial of service via radio jamming:**
ScoutNet uses WiFi. WiFi can be jammed. This is a physical-layer limitation of all WiFi systems. Not a Scout-specific vulnerability.

**Social engineering of household members:**
"Convince someone to run `scout-cli face enroll`" is a social engineering attack, not a software vulnerability.

**3D-printed part strength:**
Mechanical failure of 3D-printed parts under normal use is a hardware design issue, not a security issue. File a regular GitHub issue for these.

## Disclosure Policy

We follow a **90-day coordinated disclosure** policy.

### Timeline

1. **Day 0**: You report the vulnerability via GitHub Security Advisories.
2. **Day 0-2**: We acknowledge receipt and begin triage.
3. **Day 0-7**: We assess severity and confirm the vulnerability.
4. **Day 7-90**: We develop, test, and release a fix.
5. **Day 90** (or fix release, whichever is first): Public disclosure via GitHub Security Advisory.

### Extensions

If we need more than 90 days, we will:
1. Notify you with a specific reason and revised timeline
2. Request a maximum 30-day extension (120 days total)
3. If we cannot fix it in 120 days, you may disclose publicly

### Credit

We credit security researchers in:
- The GitHub Security Advisory
- The CHANGELOG entry for the fix
- The project's security hall of fame (if/when created)

Tell us how you want to be credited (name, handle, organization) or if you prefer anonymity.

## Security Architecture Overview

For context when evaluating potential vulnerabilities, here is Scout's security architecture.

### Trust Boundaries

```
[Internet] --(no route)-- [ScoutNet 10.0.77.0/24]
                                |
                    +-----------+-----------+
                    |                       |
             [VENTUNO Q]             [ESP32-CAMs x4]
             Linux + ROS2           Camera streams
                    |
              [STM32H5]
           Safety controller
           (independent MCU)
```

### Key Security Properties

1. **Network isolation**: No internet gateway. No DNS. No default route.
2. **Hardware safety independence**: STM32H5 enforces speed limits and E-stop independently of Linux.
3. **Encrypted face data**: AES-256-GCM, key from Argon2id-derived passphrase.
4. **No persistent audio**: Audio exists only as a transient signal, never written to disk.
5. **Physical hardware indicators**: Camera LED wired to power line, microphone mute is a hardware switch.

### What a Compromised Linux Side Can Do

If an attacker gains root on the VENTUNO Q:

- Read unencrypted SQLite data (object sightings, patrol logs, SLAM maps)
- Access camera streams from ESP32-CAMs
- Send motor commands to STM32H5 (but speed-limited to 0.3 m/s by STM32H5 firmware)
- **Cannot**: exceed speed limits, bypass E-stop, disable camera LED, mute microphone hardware switch, access encrypted face embeddings without passphrase, reach the internet

### What a Compromised STM32H5 Can Do

If an attacker flashes malicious firmware to the STM32H5:

- Bypass software speed limits and safety modes
- Ignore heartbeat protocol
- **Cannot**: access any data (STM32H5 has no storage), access the network (STM32H5 has no network interface), bypass the physical E-stop relay (wired independently)
- **Mitigation**: STM32H5 firmware flashing requires physical USB access. No OTA update path exists.

## Contact

For security questions that are not vulnerability reports, open a regular GitHub Discussion or reach out to the maintainers listed in the project README.

For vulnerability reports: [GitHub Security Advisories](../../security/advisories/new). Not email. Not public issues. Not Discussions.
