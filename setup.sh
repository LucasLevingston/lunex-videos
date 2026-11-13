#!/usr/bin/env bash
# Prepara a máquina para produzir episódios (uma vez por sessão).
set -e
cd "$(dirname "$0")"
pip install --break-system-packages -q kokoro-onnx soundfile pillow numpy 2>/dev/null || pip install -q kokoro-onnx soundfile pillow numpy
which rsvg-convert >/dev/null || (apt-get install -y -q librsvg2-bin >/dev/null 2>&1 || true)
which ffmpeg >/dev/null || (apt-get install -y -q ffmpeg >/dev/null 2>&1 || true)
mkdir -p assets
[ -s assets/kokoro.onnx ] || curl -sSL -o assets/kokoro.onnx https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/kokoro-v1.0.onnx
[ -s assets/voices.bin ] || curl -sSL -o assets/voices.bin https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/voices-v1.0.bin
[ -s assets/Anton.ttf ] || curl -sSL -o assets/Anton.ttf https://raw.githubusercontent.com/google/fonts/main/ofl/anton/Anton-Regular.ttf
python3 -c "import kokoro_onnx, PIL, numpy; print('setup ok')"
which rsvg-convert ffmpeg
