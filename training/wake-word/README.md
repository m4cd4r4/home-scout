# Wake Word Training

Train a custom "Hey Scout" wake word model using openWakeWord for low-power always-on listening.

## Overview

- **Framework**: [openWakeWord](https://github.com/dscripka/openWakeWord)
- **Architecture**: Small CNN (~500KB) running on CPU or DSP
- **Latency**: < 100ms detection
- **False accept rate target**: < 1 per 24 hours of background audio

## Recording Samples

Collect positive and negative samples for training.

### Positive Samples ("Hey Scout")

Record at least 100 clips of the wake phrase from household members:

```bash
# Record 3-second clips at 16kHz mono
python record_samples.py \
  --output_dir datasets/wake-word/positive \
  --phrase "hey scout" \
  --duration 3.0 \
  --sample_rate 16000 \
  --count 20
```

Guidelines for positive samples:
- Record from each household member (different voices)
- Vary distance from mic (0.5m, 1m, 2m, 3m)
- Vary speaking speed and volume
- Include some recordings with background noise (TV, music, kitchen)
- Aim for 100+ unique clips total

### Negative Samples

Collect ambient audio that should NOT trigger the wake word:

```bash
# Record 10-minute ambient segments
python record_ambient.py \
  --output_dir datasets/wake-word/negative \
  --duration 600 \
  --sample_rate 16000
```

Include:
- Normal conversation (without "Hey Scout")
- TV/radio/podcast audio
- Kitchen sounds, music, household noise
- Similar-sounding phrases ("hey, scoot over", "hey, Scott")

## Data Augmentation

openWakeWord applies augmentation automatically, but you can add more:

```python
# augment.py - expand positive samples
import audiomentations as A

augment = A.Compose([
    A.AddGaussianNoise(min_amplitude=0.001, max_amplitude=0.015, p=0.5),
    A.TimeStretch(min_rate=0.8, max_rate=1.2, p=0.5),
    A.PitchShift(min_semitones=-2, max_semitones=2, p=0.5),
    A.Gain(min_gain_db=-6, max_gain_db=6, p=0.5),
    A.AddBackgroundNoise(
        sounds_path="datasets/wake-word/negative",
        min_snr_db=3, max_snr_db=30, p=0.5
    ),
])
```

Target: 500+ augmented positive clips from 100 originals.

## Training

```bash
# Install openWakeWord
pip install openwakeword

# Train custom model
python -m openwakeword.train \
  --positive_dir datasets/wake-word/positive \
  --negative_dir datasets/wake-word/negative \
  --output_dir models/hey-scout \
  --model_name hey_scout \
  --epochs 50 \
  --target_false_accept_rate 0.5
```

## Testing

```bash
# Run detection on test audio
python test_wake_word.py \
  --model models/hey-scout/hey_scout.onnx \
  --audio_dir datasets/wake-word/test \
  --threshold 0.5

# Live mic test
python -m openwakeword.listen \
  --model models/hey-scout/hey_scout.onnx \
  --threshold 0.5
```

## Deployment

The trained model is a small ONNX file (~500KB) loaded by the `wake_word_node` in the `scout_voice` ROS 2 package. It runs continuously on the CPU/DSP with minimal power draw.

```
models/
  hey_scout.onnx      # Wake word model (~500KB)
  hey_scout_meta.json  # Threshold and config
```

## Tuning Threshold

- Higher threshold (0.7+) = fewer false wakes, might miss quiet triggers
- Lower threshold (0.3-0.5) = catches more triggers, more false positives
- Start at 0.5 and adjust based on real-world testing in the home
