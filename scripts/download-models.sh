#!/bin/bash
# Home Scout - Download AI Model Weights
# Downloads all required models for local inference

set -e

MODELS_DIR="${1:-$(dirname "$0")/../models}"
mkdir -p "$MODELS_DIR"

echo "=== Home Scout Model Download ==="
echo "Downloading to: $MODELS_DIR"

# Whisper Small English (ASR)
echo ""
echo "[1/5] Whisper Small English (ASR)..."
if [ ! -f "$MODELS_DIR/whisper-small-en.bin" ]; then
    echo "TODO: Download from Qualcomm AI Hub or huggingface.co/ggerganov/whisper.cpp"
    echo "Expected: whisper-small-en quantized for Hexagon NPU"
    echo "Size: ~500MB"
else
    echo "Already exists, skipping."
fi

# Piper TTS voice
echo ""
echo "[2/5] Piper TTS Voice (en_US-amy-medium)..."
if [ ! -d "$MODELS_DIR/piper" ]; then
    mkdir -p "$MODELS_DIR/piper"
    echo "TODO: Download from https://github.com/rhasspy/piper/releases"
    echo "Expected: en_US-amy-medium.onnx + en_US-amy-medium.onnx.json"
    echo "Size: ~100MB"
else
    echo "Already exists, skipping."
fi

# SmolVLM-256M (Object Detection VLM)
echo ""
echo "[3/5] SmolVLM-256M (Object Detection)..."
if [ ! -f "$MODELS_DIR/smolvlm-256m.onnx" ]; then
    echo "TODO: Download from Hugging Face and quantize for Hexagon NPU"
    echo "Expected: smolvlm-256m INT4 quantized"
    echo "Size: ~1.5GB"
else
    echo "Already exists, skipping."
fi

# Llama 3.2 1B Instruct (Conversation LLM)
echo ""
echo "[4/5] Llama 3.2 1B Instruct (Conversation)..."
if [ ! -f "$MODELS_DIR/llama-3.2-1b-instruct.onnx" ]; then
    echo "TODO: Download from Qualcomm AI Hub"
    echo "See: https://aihub.qualcomm.com/mobile/models/llama_v3_2_1b_instruct"
    echo "Expected: INT4 quantized for Hexagon NPU"
    echo "Size: ~1.5GB"
else
    echo "Already exists, skipping."
fi

# MobileFaceNet (Face Recognition)
echo ""
echo "[5/5] MobileFaceNet ArcFace (Face Recognition)..."
if [ ! -f "$MODELS_DIR/mobilefacenet.onnx" ]; then
    echo "TODO: Download from InsightFace"
    echo "See: https://github.com/deepinsight/insightface"
    echo "Expected: mobilefacenet ONNX model"
    echo "Size: ~10MB"
else
    echo "Already exists, skipping."
fi

echo ""
echo "=== Download complete ==="
echo "Total estimated size: ~3.6GB"
echo ""
echo "Note: Actual download links will be added when the VENTUNO Q"
echo "ships and Qualcomm AI Hub model formats are finalized."
