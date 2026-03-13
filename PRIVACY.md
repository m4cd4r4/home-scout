# Privacy Policy

Scout is a home companion robot. It sees your home, hears your family, and navigates your rooms. That is a significant trust boundary. This document explains exactly what Scout does with that trust.

## Privacy Pledge

**Scout never connects to the internet. Period.**

No cloud sync. No telemetry. No analytics. No phone-home. No OTA updates pulled from a remote server. No data leaves your home network - because Scout does not have a route to the internet in the first place.

Scout creates its own isolated WiFi network. It has no default gateway. It cannot reach the internet even if you wanted it to. Every byte of data Scout processes stays on the NVMe SSD inside the Arduino VENTUNO Q board sitting in your home.

This is not a policy decision. It is an architectural decision. The network stack has no outbound route. The `verify-privacy.sh` script confirms it. You can audit it yourself.

## What Data Scout Stores

### Object Sightings

Scout detects and logs objects it sees during patrols and interactions.

| Field | Example | Purpose |
|-------|---------|---------|
| `object_name` | `backpack` | What was seen |
| `room` | `kitchen` | Which room |
| `zone` | `counter_left` | Zone within room |
| `position_x/y/z` | `1.2, 0.8, 0.9` | 3D coordinates in map frame |
| `confidence` | `0.87` | Detection confidence score |
| `timestamp` | `2026-03-13T08:41:00Z` | When it was seen |

Stored in local SQLite. No images are saved - only structured metadata about what was detected.

### Face Embeddings

Scout can recognize enrolled household members. It stores **512-dimensional numerical vectors only**. These are abstract mathematical representations. They are not photos. They cannot be reversed into a face image.

- Encrypted at rest with AES-256-GCM
- Encryption key derived from user passphrase via Argon2id (memory-hard KDF)
- Without the passphrase, embeddings are unreadable ciphertext

### Conversation Logs

- 1-hour rolling circular buffer in memory
- Used for context during active conversations
- Automatically discarded after 1 hour
- Never written to persistent storage

### SLAM Maps

Occupancy grids representing walls, obstacles, and navigable space. These are geometric data - coordinates and grid cells. They contain no personal information, no object labels, no images.

### Patrol Logs

Timestamps and route data from patrol runs. Used to track patrol coverage and timing. Contains no sensor data beyond position.

## Where Data Lives

All data resides on the Arduino VENTUNO Q's local NVMe SSD in a SQLite database at `/home/scout/data/scout.db`.

- No cloud sync
- No replication to external services
- No sidecar processes that export data
- Database file permissions: `0600` (owner read/write only)

## Data Lifecycle

Scout applies automatic retention policies. All retention periods are configurable in `config/privacy.yaml`.

| Data Category | Default Retention | Examples |
|---------------|-------------------|----------|
| Personal items | 30 days | "Where is my backpack?" |
| Household items | 14 days | Furniture positions, room layouts |
| Transient objects | 2 days | Delivery boxes, temporary items |
| Conversation logs | 1 hour | Voice interaction context |
| Face embeddings | Until manually deleted | Enrolled household members |
| SLAM maps | Indefinite (no personal data) | Navigation grids |
| Patrol logs | 30 days | Route and timing data |

### Manual Purge

```bash
# Delete all object sightings older than N days
scout-cli data purge --older-than 7d --type objects

# Delete all face embeddings for a specific person
scout-cli face delete --name "Alice"

# Delete all conversation logs immediately
scout-cli data purge --type conversations --all

# Nuclear option: wipe all personal data, keep maps and config
scout-cli data purge --personal --all
```

### Backup and Export

```bash
# Export all data to encrypted local archive
scout-cli data export --output /media/usb/scout-backup.enc

# Import from backup
scout-cli data import --input /media/usb/scout-backup.enc
```

Backups are AES-256-GCM encrypted with your passphrase. They are local files. There is no cloud backup target. You choose where the file goes.

## Face Data Consent Model

Face recognition is opt-in per person. Scout does not silently learn faces.

### Enrollment

1. A household member explicitly runs enrollment: `scout-cli face enroll --name "Alice"`
2. Scout captures embedding vectors during a guided enrollment session
3. Scout stores only the 512-dimensional embedding, encrypted
4. No photos are saved at any point in the pipeline

### Deletion

```bash
# One command removes all face data for a person
scout-cli face delete --name "Alice"
```

This is a hard delete. The encrypted embedding is overwritten with zeros, then the file is removed. There is no "soft delete" or recycle bin.

### What Is Not Stored

- No photographs
- No video clips
- No thumbnails or crops
- No raw camera frames
- No "face images" of any kind

The embedding is a list of 512 floating-point numbers. It is derived from a face but cannot reconstruct one.

### Encryption Details

| Parameter | Value |
|-----------|-------|
| Algorithm | AES-256-GCM |
| Key derivation | Argon2id |
| Argon2id memory | 64 MB |
| Argon2id iterations | 3 |
| Argon2id parallelism | 4 |
| Nonce | 12 bytes, randomly generated per encryption |

The encryption key is derived from a user-chosen passphrase. Scout does not store the passphrase. If you forget it, enrolled face data is unrecoverable. This is by design.

## Audio Processing

### Voice Interaction Pipeline

1. Wake word detection runs on the VENTUNO Q's DSP co-processor
2. DSP listens for "Hey Scout" using a small keyword-spotting model
3. Wake word detection does **not** record audio - it processes a rolling buffer and discards non-matching frames
4. On wake word detection, audio streams to the on-device ASR (Automatic Speech Recognition) model
5. ASR produces text transcription
6. Raw audio is discarded immediately after transcription
7. Transcription enters the 1-hour rolling conversation buffer
8. After 1 hour, transcription is deleted

### What Is Never Stored

- Raw audio waveforms
- Compressed audio files
- Audio spectrograms
- Speaker voiceprints

Audio exists only as a transient signal being processed. It is never persisted to disk.

## Hardware Privacy Guarantees

These are physical, verifiable guarantees. They cannot be overridden by software, firmware updates, or configuration changes.

### Physical Microphone Mute Switch

A slide switch on Scout's chassis **disconnects the I2S clock line** between the microphone array and the VENTUNO Q. When the switch is in the MUTE position, the microphones receive no clock signal and cannot transmit data. This is a hardware disconnect, not a software mute. No firmware can override it.

**How to verify:** Slide the switch to MUTE. Run `scout-cli audio test`. The test will report zero audio input. Inspect the schematic in `hardware/schematics/audio-mute.kicad_sch` to confirm the clock line is physically interrupted.

### Camera Indicator LED

The camera indicator LED is **wired in series with the camera module's power line**. If the camera has power, the LED is on. If the LED is off, the camera has no power. There is no GPIO controlling this LED independently. No software can turn the camera on without illuminating the LED.

**How to verify:** Inspect the schematic in `hardware/schematics/camera-power.kicad_sch`. Trace the power line from the regulator through the LED to the camera module.

### Emergency Stop Button

A red mushroom-head button on Scout's top panel. Pressing it physically disconnects motor power via a relay. The STM32H5 safety controller detects the GPIO interrupt and enters safe mode. The relay disconnect is independent of the microcontroller - even if the STM32H5 is hung, the relay opens.

## Network Isolation

### ScoutNet (Default Configuration)

Scout creates its own WiFi access point:

| Parameter | Value |
|-----------|-------|
| SSID | `ScoutNet` (hidden) |
| Security | WPA3-SAE |
| Subnet | `10.0.77.0/24` |
| Gateway | None (no default route) |
| Internet access | None |
| DHCP range | `10.0.77.100-10.0.77.200` |

Scout is the access point. ESP32-CAM modules and your management device connect to ScoutNet. There is no upstream connection. There is no NAT. There is no route to the internet.

### Network Verification

```bash
# Run the privacy audit script
./scripts/verify-privacy.sh

# What it checks:
# 1. No default gateway configured on any interface
# 2. No DNS resolver configured
# 3. No outbound connections on any port
# 4. No listening services on WAN-facing interfaces
# 5. iptables rules block all FORWARD and OUTPUT to non-local subnets
# 6. All ESP32-CAM modules are on ScoutNet only
```

### VLAN Isolation (Advanced)

If you want to connect your management device to Scout without a separate WiFi network, you can place Scout on an isolated VLAN on your home network.

```bash
# Example: VLAN 77, no internet gateway
# On your managed switch:
# 1. Create VLAN 77
# 2. Assign Scout's Ethernet port to VLAN 77 (untagged)
# 3. Do NOT add a gateway or internet uplink to VLAN 77
# 4. Assign your management device to VLAN 77 (tagged or untagged)

# On Scout, verify isolation:
./scripts/verify-privacy.sh --interface eth0
```

## What We Will Never Do

This is not a "current policy" that might change. These are architectural constraints enforced by design.

- **Cloud sync**: Scout has no internet connectivity to sync with
- **Telemetry**: No metrics collection endpoint exists in the codebase
- **Analytics**: No analytics SDK, no tracking pixels, no usage reporting
- **Phone-home**: No hardcoded URLs, no update servers, no beacon endpoints
- **Sell data**: Scout is MIT-licensed open-source hardware and software. There is no business model that involves your data
- **Partner integrations**: No third-party service integrations. No Alexa. No Google. No HomeKit. Scout is self-contained
- **Advertising**: No ad SDK. No ad network integration. Not now, not ever

If any of these constraints are violated in a pull request, it is a security vulnerability. Report it via our [security policy](SECURITY.md).

## Threat Model

| Threat Actor | Attack Vector | Impact | Mitigation |
|-------------|--------------|--------|------------|
| **Physical theft** | Steal the robot, extract NVMe SSD | Access to object sighting database and encrypted face embeddings | Face embeddings encrypted with AES-256-GCM. Without passphrase, embeddings are unreadable. Object data is plaintext SQLite - consider full-disk encryption if this threat matters to you. |
| **Network neighbor** | Connect to ScoutNet, access Scout's services | Access management interface, view sighting data | WPA3-SAE on ScoutNet. Management interface requires local authentication. Hidden SSID reduces discoverability. |
| **Malicious firmware** | Flash compromised firmware to VENTUNO Q or STM32H5 | Full system compromise | Firmware updates require physical USB access. No OTA update mechanism exists. Verify firmware checksums against this repository. |
| **Household overreach** | Family member accesses another member's face data | Privacy violation within household | Face data encrypted per-person with individual passphrases. One household member cannot decrypt another's embeddings without their passphrase. |
| **Manufacturer backdoor** | Qualcomm NPU firmware contains hidden exfiltration | Data leakage via covert channel | NPU has no network access. ScoutNet has no internet gateway. Even if the NPU firmware is compromised, there is no route for data to leave the local network. See "Accepted Risks" below. |
| **Malicious contributor** | Submit PR that adds network exfiltration | Data leakage | Code review required. `verify-privacy.sh` runs in CI. Any new network endpoint or outbound connection triggers CI failure. |

## Accepted Risks

### Qualcomm NPU Firmware

The Qualcomm QCS6490 NPU runs closed-source firmware. We cannot audit it. We cannot verify it does not contain backdoors or covert channels.

**Why we accept this risk:**

1. The NPU has no direct network interface. All network traffic goes through the Linux kernel, which we control.
2. ScoutNet has no internet gateway. Even if the NPU firmware tried to exfiltrate data, packets have nowhere to go.
3. `verify-privacy.sh` monitors all network interfaces for unexpected traffic. Any covert channel attempt would be flagged.
4. The alternative (building custom NPU silicon) is not feasible for an open-source project.

Network isolation is our primary mitigation. It is defense in depth - even a compromised component cannot reach the internet.

### Physical Access

If an attacker has prolonged physical access to Scout, they can extract the NVMe SSD and read unencrypted data (object sightings, SLAM maps, patrol logs). Face embeddings remain protected by AES-256-GCM encryption.

Users who need stronger protection against physical theft should enable full-disk encryption on the VENTUNO Q's Linux installation. Instructions are in `docs/full-disk-encryption.md`.

## Privacy Verification Checklist

Run through this checklist to verify Scout's privacy guarantees yourself.

### Network Isolation

- [ ] Run `./scripts/verify-privacy.sh` and confirm all checks pass
- [ ] Run `ip route` on Scout - confirm no default gateway
- [ ] Run `cat /etc/resolv.conf` on Scout - confirm no DNS servers
- [ ] Run `ss -tunlp` on Scout - confirm no services listening on non-ScoutNet interfaces
- [ ] From your home network (not ScoutNet), try to ping Scout - confirm it fails

### Audio Privacy

- [ ] Slide the mute switch to MUTE
- [ ] Run `scout-cli audio test` - confirm zero audio input
- [ ] Slide the mute switch back to ACTIVE
- [ ] Run `scout-cli audio test` - confirm audio input works
- [ ] Say "Hey Scout" and interact - then check that no audio files exist: `find /home/scout -name "*.wav" -o -name "*.mp3" -o -name "*.ogg"`

### Camera Privacy

- [ ] Cover all cameras - confirm indicator LEDs are off
- [ ] Uncover cameras - confirm indicator LEDs turn on
- [ ] Verify no image files are stored: `find /home/scout -name "*.jpg" -o -name "*.png" -o -name "*.bmp"`

### Face Data

- [ ] Enroll a test face: `scout-cli face enroll --name "Test"`
- [ ] Verify only encrypted embeddings exist (no photos): `ls /home/scout/data/faces/`
- [ ] Delete the test face: `scout-cli face delete --name "Test"`
- [ ] Verify deletion: `ls /home/scout/data/faces/` should show no "Test" files

### Data Retention

- [ ] Check retention config: `cat config/privacy.yaml`
- [ ] Verify retention enforcement: `scout-cli data stats` shows no data older than configured limits

### Source Code Audit

- [ ] Search the codebase for URLs: `grep -rn "http://" ros2_ws/ firmware/ scripts/` - should find only localhost references
- [ ] Search for hardcoded IPs: `grep -rn "[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+" ros2_ws/` - should find only `10.0.77.*` and `127.0.0.1`
- [ ] Search for telemetry keywords: `grep -rni "telemetry\|analytics\|tracking\|phone.home" ros2_ws/ firmware/ scripts/`
