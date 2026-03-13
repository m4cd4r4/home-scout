# Phase 5: Scout Knows Us

After this phase, Scout recognizes family members by face and greets them by name. No new hardware needed - this uses the existing camera from Phase 2.

## What You Need

Nothing new. Phase 5 is pure software.

**Phase 5 total: $0** (cumulative: ~$995)

## Step 1: Generate Encryption Key

Face embeddings are encrypted at rest. Create the encryption key from a passphrase:

```bash
# Generate key (you'll be prompted for a passphrase)
python3 -c "
from cryptography.fernet import Fernet
import getpass, hashlib, base64
passphrase = getpass.getpass('Enter passphrase for face data encryption: ')
key = base64.urlsafe_b64encode(hashlib.sha256(passphrase.encode()).digest())
with open('/home/scout/data/face_key.bin', 'wb') as f:
    f.write(key)
print('Key saved.')
"
```

!!! warning
    Remember this passphrase. If you lose it, enrolled face data cannot be decrypted and you'll need to re-enroll everyone.

## Step 2: Enroll Family Members

Enrollment requires explicit consent. Each person stands in front of Scout's camera:

```bash
# Enroll a person (requires consent_given=true)
ros2 service call /scout/faces/enroll scout_interfaces/srv/EnrollFace \
  "{person_name: 'Dad', consent_given: true}"
```

Scout will capture multiple face samples from different angles. Hold still and slowly turn your head left and right.

Repeat for each family member.

## Step 3: Launch with Face Recognition

```bash
ros2 launch scout_bringup scout_full.launch.py
```

The recognition node runs automatically alongside vision.

## Step 4: Customize Greetings

Edit the personality config to customize per-person greetings:

```yaml
# In config/personalities/default.yaml
greetings:
  known_person:
    morning: "Good morning, {name}!"
    afternoon: "Hey {name}, welcome home!"
    evening: "Evening, {name}."
  unknown_person: "Hello there! I don't think we've met."
```

## Privacy Details

- **No photos are stored.** Only 128-dimensional embedding vectors.
- Embeddings are encrypted with AES (Fernet) at rest.
- All face processing happens on-device using the NPU.
- Enrollment requires explicit `consent_given: true` flag.
- Delete a person: `ros2 service call /scout/faces/delete ...`

## Test It

- Walk into Scout's field of view - it should greet you by name
- Have another enrolled family member walk in - different greeting
- Have someone not enrolled walk in - "Hello there! I don't think we've met."
- Test at different times of day for time-appropriate greetings
- Check that Scout doesn't greet the same person repeatedly (cooldown)

## What's Next

[Phase 6: Sky Eye](phase-6-drone.md) - add an optional drone module for aerial patrol.
