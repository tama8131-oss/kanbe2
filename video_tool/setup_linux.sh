#!/usr/bin/env bash
# はじめに1回だけ実行する準備スクリプト（Linux / Claude Code のクラウド環境用）
# フォント・ffmpeg・Pythonの部品・VOICEVOX Engine をそろえる
set -e
cd "$(dirname "$0")"

echo "== フォントと ffmpeg を入れます =="
if ! fc-list | grep -q "Noto Sans CJK JP:style=Bold" || ! command -v ffmpeg >/dev/null; then
  SUDO=""; [ "$(id -u)" != "0" ] && SUDO="sudo"
  $SUDO apt-get update -y >/dev/null
  $SUDO apt-get install -y fonts-noto-cjk ffmpeg >/dev/null
fi

echo "== Python の部品を入れます =="
python3 -m pip install -q pillow pyyaml py7zr

echo "== VOICEVOX Engine 0.26.1 を用意します（約1.9GB・数分かかります） =="
if [ ! -x voicevox_engine/linux-cpu-x64/run ]; then
  mkdir -p voicevox_engine
  curl -L --fail -o voicevox_engine/engine.7z \
    https://github.com/VOICEVOX/voicevox_engine/releases/download/0.26.1/voicevox_engine-linux-cpu-x64-0.26.1.7z.001
  python3 -c "import py7zr; py7zr.SevenZipFile('voicevox_engine/engine.7z').extractall('voicevox_engine')"
  rm voicevox_engine/engine.7z
  chmod +x voicevox_engine/linux-cpu-x64/run
fi
echo "準備おわり！ 次は ./start_voicevox.sh を実行してください。"
