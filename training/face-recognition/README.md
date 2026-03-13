# Face Recognition Training

MobileFaceNet enrollment pipeline for household member recognition. Privacy-first: only 512-dim embeddings are stored, never photographs.

## Architecture

- **MobileFaceNet** - lightweight face recognition model (~1M parameters)
- Generates a 512-dimensional embedding per face
- Embeddings are compared via cosine similarity at query time
- Runs on-device; no cloud calls

## Enrollment Pipeline

1. **Capture** - Scout's camera captures 10-15 frames of the person's face from different angles during a guided enrollment session
2. **Detect** - Face detection crops each frame to the face region
3. **Embed** - MobileFaceNet generates a 512-dim embedding per crop
4. **Average** - Embeddings are averaged into a single representative vector
5. **Store** - The averaged embedding vector is saved to SQLite with the person's name
6. **Discard** - All captured images and intermediate crops are deleted immediately

## Embedding Generation

```python
from scout_faces.embedding import generate_embedding

# During enrollment
embeddings = []
for frame in enrollment_frames:
    face_crop = detect_and_crop(frame)
    emb = generate_embedding(face_crop)  # -> np.ndarray shape (512,)
    embeddings.append(emb)

# Average and normalize
avg_embedding = np.mean(embeddings, axis=0)
avg_embedding = avg_embedding / np.linalg.norm(avg_embedding)

# Store in DB (no photos kept)
store_embedding(person_name="Alice", embedding=avg_embedding)
```

## Recognition at Runtime

```python
# Live frame -> detect face -> embed -> compare
live_embedding = generate_embedding(live_face_crop)
matches = compare_against_enrolled(live_embedding, threshold=0.6)
```

Cosine similarity threshold:
- **> 0.7** - high confidence match
- **0.6 - 0.7** - probable match (ask for confirmation)
- **< 0.6** - no match / unknown person

## Data Stored

| What | Stored | Format |
|------|--------|--------|
| Person name | Yes | Text in SQLite |
| 512-dim embedding | Yes | BLOB in SQLite |
| Photos/frames | No | Deleted after embedding |
| Face crops | No | Deleted after embedding |

## Re-Enrollment

Embeddings drift over time (haircuts, glasses, aging). Re-enrollment can be triggered:
- Manually by the user ("Scout, re-learn my face")
- Automatically when recognition confidence drops below threshold for a known person

## Model Files

```
models/
  mobilefacenet.onnx        # Base model (~4MB)
  face_detector_slim.onnx   # Face detection model (~2MB)
```

Both models run on the Qualcomm QCS6490 NPU for real-time performance.
