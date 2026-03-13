# Contributing to Home Scout

We build this together.

Home Scout is a family project. Parents build it with kids. Students build it in dorms. Makers build it in garages. Every contribution - from a one-line typo fix to a full chassis redesign - makes Scout better for everyone.

This guide covers how to contribute effectively.

## Ways to Contribute

There are many ways to help, and not all of them require hardware.

### Code

- ROS 2 nodes (Python)
- STM32/ESP32 firmware (C++)
- Tests and CI improvements
- Simulation environments
- Developer tooling

### Hardware

- Chassis improvements (STEP + STL)
- Mount designs for new sensors
- Cable management solutions
- Alternative assembly methods

### Documentation

- Build guides and tutorials
- Troubleshooting tips
- Translations
- Phase walkthroughs with photos

### Testing

- Run test suites and report results
- Test builds on your hardware
- Verify docs by following them step-by-step
- Stress-test edge cases

### Translations

- Translate docs to your language
- Add Whisper language model configs
- Translate personality response templates

### Photos and Videos

- Build progress photos for guides
- Assembly videos
- Demo videos showing Scout in action

### Personality Configs

- Create new personality YAML files
- Tune response templates for different household styles
- Design wake word alternatives

### Training Data

- Label wake word audio samples
- Contribute anonymized test utterances
- Help curate face recognition test datasets (synthetic only)

## Development Setup

### Option 1: Docker (Recommended)

One command gets you a full development environment.

```bash
git clone https://github.com/YOUR_USERNAME/home-scout.git
cd home-scout
docker compose up dev
```

This starts a container with ROS 2 Jazzy, PlatformIO, all Python dependencies, and a pre-built workspace. Changes to your local files sync into the container automatically.

### Option 2: Manual Setup

If you prefer a native install:

**Requirements:**
- Ubuntu 24.04 (or WSL2 with Ubuntu 24.04)
- ROS 2 Jazzy Jalisco
- Python 3.12+
- PlatformIO Core (for firmware)

```bash
# Clone
git clone https://github.com/YOUR_USERNAME/home-scout.git
cd home-scout

# Install ROS 2 dependencies
sudo apt update
rosdep install --from-paths ros2_ws/src --ignore-src -y

# Build ROS 2 workspace
cd ros2_ws
colcon build --symlink-install
source install/setup.bash

# Install Python tools
pip install ruff mypy pytest pytest-cov

# Install PlatformIO (for firmware work)
pip install platformio
```

### Running Tests

```bash
# Python tests (from ros2_ws/)
colcon test
colcon test-result --verbose

# Firmware build check
cd firmware/stm32_motor_control
pio run

cd firmware/esp32_cam_stream
pio run

# Linting
ruff check .
mypy ros2_ws/src --strict
```

## Branch Naming

Use this format for branch names:

| Pattern | Use For | Example |
|---------|---------|---------|
| `phase-N/feature-name` | Phase-specific features | `phase-1/wake-word-tuning` |
| `hardware/description` | Hardware changes | `hardware/chassis-v2` |
| `firmware/description` | Firmware changes | `firmware/motor-pid-tuning` |
| `docs/description` | Documentation | `docs/phase-3-guide` |
| `fix/description` | Bug fixes | `fix/voice-timeout` |
| `ci/description` | CI/CD changes | `ci/add-stl-validation` |

Always branch from latest `main`:

```bash
git checkout main && git pull origin main
git checkout -b phase-2/lidar-integration
```

## Commit Format

Use [Conventional Commits](https://www.conventionalcommits.org/).

```
type(scope): short description

Optional body with more detail.

Refs: #123
```

**Types:**

| Type | Use For |
|------|---------|
| `feat(voice)` | New voice feature |
| `feat(vision)` | New vision feature |
| `feat(nav)` | New navigation feature |
| `feat(memory)` | New memory/context feature |
| `feat(faces)` | New face recognition feature |
| `fix(voice)` | Bug fix in voice |
| `hardware(chassis)` | Chassis design change |
| `hardware(mounts)` | Mount design change |
| `firmware(stm32)` | STM32 firmware change |
| `firmware(esp32)` | ESP32 firmware change |
| `docs` | Documentation |
| `test` | Tests |
| `ci` | CI/CD pipeline |
| `chore` | Maintenance, dependencies |

**Examples:**

```
feat(voice): add timeout for wake word detection

The wake word listener now times out after 30 seconds of silence
and returns to low-power listening mode.

Refs: #42
```

```
hardware(chassis): widen camera mount slot by 2mm

The ESP32-CAM module was too tight in the original slot.
Tested with three different ESP32-CAM boards.
```

## Pull Request Process

### Before You Open a PR

1. Rebase onto latest `main`
2. Run the full test suite
3. Run linters (`ruff check .`, `mypy --strict`)
4. Build firmware if you changed it (`pio run`)
5. Update docs if your change affects user-facing behavior

### Opening the PR

1. Fill out the PR template completely
2. Describe what changed and why
3. Link the related issue (`Closes #123`)
4. Complete the checklist

### PR Checklist

Every PR must pass these checks:

- [ ] Tests pass (`colcon test`)
- [ ] Linters pass (`ruff`, `mypy`, `clang-format`, `yamllint`)
- [ ] Documentation updated (if user-facing change)
- [ ] Privacy preserved - no new cloud calls, no new data collection
- [ ] Safety maintained - no new autonomous movement without user confirmation
- [ ] Firmware builds cleanly (if firmware changed)
- [ ] Hardware tested physically (if hardware changed)

### Review Process

1. At least one maintainer review required
2. CI must pass
3. Hardware changes need photo evidence
4. Firmware changes need testing evidence (serial output, video)

## Code Style

### Python

- Formatter: `ruff format`
- Linter: `ruff check`
- Type checker: `mypy --strict`
- Coverage target: 80% minimum for new code
- Docstrings: Google style
- Max line length: 88 characters (ruff default)

```python
def detect_wake_word(audio_chunk: np.ndarray, threshold: float = 0.85) -> bool:
    """Check if the audio chunk contains the wake word.

    Args:
        audio_chunk: Raw audio samples at 16kHz.
        threshold: Confidence threshold for detection.

    Returns:
        True if wake word detected above threshold.
    """
    ...
```

### C++ (Firmware)

- Formatter: `clang-format` (config in `.clang-format`)
- Follow PlatformIO conventions
- Use `snake_case` for functions and variables
- Use `SCREAMING_SNAKE_CASE` for constants and macros

### YAML

- Linter: `yamllint`
- 2-space indentation
- Always quote strings that could be misinterpreted

### ROS 2 Conventions

- Package names: `scout_*` (e.g., `scout_voice`, `scout_nav`)
- Node names: descriptive, lowercase (e.g., `wake_word_detector`)
- Topic names: namespaced under `/scout/` (e.g., `/scout/voice/wake_word`)

## Hardware Submissions

If you are contributing a hardware design (chassis part, mount, bracket, enclosure):

### Required Files

1. **STEP file** (.step) - the parametric CAD source
2. **STL file** (.stl) - the print-ready mesh
3. **Photos** - of the actual printed and assembled part
4. **Print settings** - material, layer height, infill, supports

### Requirements

- You must have physically printed and tested the part
- It must fit the VENTUNO Q and existing chassis
- Include measurements of critical dimensions
- Note any tolerance issues you encountered

### Submission Format

Place files in the appropriate `hardware/` subdirectory:

```
hardware/
  chassis/
    your-part-name/
      your-part-name.step
      your-part-name.stl
      README.md          # Print settings, notes, photos
      photos/
        assembled.jpg
        print-detail.jpg
```

## Contributing Without Hardware

You do not need a VENTUNO Q or any hardware to contribute. Here is how.

### Simulation

Run Scout in Gazebo simulation. The full ROS 2 stack works in sim.

```bash
ros2 launch scout_bringup simulation.launch.py
```

### Documentation

Read the existing docs. Follow the build guides. If something confuses you, that is a doc bug. Fix it.

### Tests

Write tests. Run tests. Report failures. Every test you add makes Scout more reliable.

### Personality Configs

Create YAML personality files that define how Scout responds. No hardware needed - test with the voice simulator.

```yaml
# config/personalities/friendly.yaml
name: "Friendly Scout"
wake_word: "hey scout"
greeting: "Hi there!"
personality_traits:
  formality: 0.3
  verbosity: 0.5
  humor: 0.7
```

### Wake Word Samples

Record yourself saying "hey scout" in different environments. We need diverse voice samples for robust detection.

### Training Data Labels

Help label audio and image datasets used for testing. This is critical work that directly improves Scout's accuracy.

## Good First Issues

Look for issues tagged with these labels:

| Label | Meaning |
|-------|---------|
| `good first issue` | Simple, well-scoped, great for newcomers |
| `help wanted` | We need help but it may require more context |
| `docs` | Documentation improvements |
| `testing` | Test coverage improvements |

### Finding Starter Tasks

1. Browse [issues labeled `good first issue`](../../issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)
2. Comment on the issue to claim it
3. Ask questions - we are happy to help
4. Open a draft PR early so we can give feedback

### Your First PR

If this is your first open source contribution:

1. Fork the repo
2. Clone your fork
3. Create a branch (`git checkout -b docs/fix-typo`)
4. Make your change
5. Commit with a conventional commit message
6. Push to your fork
7. Open a PR against `main`

We review all PRs and give constructive feedback. No contribution is too small.

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). This is a family-friendly project. Many contributors build Scout with their children. Please keep all interactions respectful and welcoming.

## Questions?

- Open a [Discussion](../../discussions) for general questions
- Open an [Issue](../../issues) for bugs or feature requests
- Tag `@YOUR_USERNAME` if you need maintainer input

Thank you for helping build Scout.
