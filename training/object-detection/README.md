# Object Detection Training

Fine-tune SmolVLM-256M on household objects and export to ONNX for on-device inference on the Qualcomm QCS6490 NPU.

## Base Model

- **SmolVLM-256M** from HuggingFace (HuggingFaceTB/SmolVLM-256M-Instruct)
- Small enough for edge NPU inference (~256M parameters)
- Vision-language model - handles both detection and scene description

## Dataset Format

Organize training images in COCO-style format:

```
datasets/
  household-v1/
    images/
      train/
        000001.jpg
        000002.jpg
      val/
        001000.jpg
    annotations/
      train.json    # COCO format: images, annotations, categories
      val.json
```

Each annotation entry:

```json
{
  "id": 1,
  "image_id": 1,
  "category_id": 3,
  "bbox": [x, y, width, height],
  "area": 1234,
  "iscrowd": 0
}
```

## Target Categories

Focus on objects people actually lose or ask about:

| Category | Examples |
|----------|----------|
| portable | keys, phone, wallet, glasses, remote, bag |
| semi_fixed | shoes, jacket, laptop, tablet, book |
| fixed | couch, table, chair, tv |

## Training on Local Workstation

Requires: NVIDIA GPU with 8+ GB VRAM, Python 3.11+, CUDA 12.x

```bash
# Set up environment
python -m venv .venv
source .venv/bin/activate
pip install transformers[torch] accelerate datasets pillow

# Fine-tune with LoRA (saves VRAM)
python train.py \
  --model_name HuggingFaceTB/SmolVLM-256M-Instruct \
  --dataset_dir datasets/household-v1 \
  --output_dir checkpoints/household-v1 \
  --lora_r 16 \
  --lora_alpha 32 \
  --epochs 10 \
  --batch_size 4 \
  --learning_rate 2e-4
```

## ONNX Export for Qualcomm NPU

After training, export to ONNX and then quantize for the QCS6490:

```bash
# Export to ONNX
python export_onnx.py \
  --checkpoint checkpoints/household-v1/best \
  --output models/household-detector.onnx \
  --input_size 640 640

# Quantize to INT8 for NPU
python -m onnxruntime.quantization.preprocess \
  --input models/household-detector.onnx \
  --output models/household-detector-quant.onnx

# Convert to QNN format for Qualcomm NPU (requires Qualcomm AI Engine SDK)
qnn-onnx-converter \
  --input_network models/household-detector-quant.onnx \
  --output_path models/household-detector.qnn
```

## Validation

```bash
python evaluate.py \
  --model models/household-detector.onnx \
  --dataset datasets/household-v1/val \
  --iou_threshold 0.5
```

Target metrics:
- mAP@0.5 > 0.80 for portable objects
- Inference latency < 50ms on QCS6490 NPU
- Model size < 100MB (ONNX quantized)

## Privacy

All training data is collected locally from Scout's own cameras during operation. No images are uploaded to any cloud service. Training runs entirely on the local workstation.
