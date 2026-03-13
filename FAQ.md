# Frequently Asked Questions

## Hardware

### Do I need a 3D printer?

No. You can use the off-the-shelf 4WD chassis kit ($35) for Phase 3. If you want the custom chassis, online 3D printing services (JLCPCB, Craftcloud) work fine. Some public libraries and makerspaces also have printers.

### Can I use a Raspberry Pi instead?

No. The VENTUNO Q's 40 TOPS NPU is required for running the VLM, ASR, TTS, and face recognition models locally in real time. A Raspberry Pi 5 has no NPU and cannot run these workloads at usable speeds.

### Can I use an NVIDIA Jetson?

Technically yes, but the project is designed around the VENTUNO Q's dual-processor architecture (Qualcomm + STM32H5). A Jetson Orin Nano would need a separate microcontroller for motor control and different AI runtime configuration. Community ports are welcome.

### How much does it cost?

- Phase 1 (voice only): ~$350 (mostly the VENTUNO Q board)
- Phases 1-3 (voice + vision + movement): ~$800-900
- Full build (all phases): ~$1,100
- See [BOM.md](BOM.md) for the detailed breakdown.

## Privacy

### Does Scout need internet?

Never. Not for setup, not for operation, not for updates. Scout creates its own isolated WiFi network for the fixed cameras. It has no route to the internet.

### Is my data safe?

All data stays on the device. Face embeddings are encrypted (AES-256-GCM). Audio is never saved. Object sightings are stored in local SQLite with configurable auto-delete. Run `scripts/verify-privacy.sh` to audit network traffic yourself. See [PRIVACY.md](PRIVACY.md).

### Can someone hack Scout remotely?

Scout has no internet connection by design. An attacker would need physical access to your local network (ScoutNet WiFi) to interact with Scout. The WiFi AP uses WPA3-SAE encryption.

## Building

### What age is appropriate for building?

- Under 6: Interact with Scout, help design personality
- 6-10: Phase 1 (voice, no soldering), label training data
- 10-14: Wiring (supervised), 3D printing, software config
- 14+: All phases with basic safety training
- Phase 6 (drone): 16+ with adult supervision

See [SAFETY.md](SAFETY.md) for details.

### Can I build just one phase?

Yes. Each phase is standalone. Phase 1 (voice) works without any other phase. Many people will stop at Phase 4 - that is the "where are my keys?" experience.

### What if I only want voice?

Phase 1 is fully functional on its own. Scout becomes a local voice assistant - no cameras, no motors, no navigation. Just a microphone, speaker, and the VENTUNO Q running ASR + TTS + LLM.

## Software

### Can Scout control my smart home?

No. Scout observes and reports. It does not actuate home systems (lights, locks, thermostats). This is by design - adding home control would require network connectivity and create security risks.

### Can I run Scout headless?

Yes. SSH into the VENTUNO Q and use ROS 2 CLI tools. All functionality works without a display.

### What languages does Scout support?

English by default (Whisper models support English best). The community can add other languages by configuring different Whisper and Piper TTS models. ASR quality varies by language.

### What if the VENTUNO Q is sold out?

There is no direct alternative - the 40 TOPS NPU with integrated STM32H5 MCU is unique. Join the Arduino Store waitlist. The board is expected to ship in Q2 2026 at ~$300.
