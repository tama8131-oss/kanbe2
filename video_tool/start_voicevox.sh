#!/usr/bin/env bash
# VOICEVOX Engine を裏で起動して、使えるようになるまで待つ
cd "$(dirname "$0")"
if curl -s http://127.0.0.1:50021/version >/dev/null; then
  echo "VOICEVOX はもう起動しています。"; exit 0
fi
nohup voicevox_engine/linux-cpu-x64/run --host 127.0.0.1 --port 50021 > voicevox_engine/engine.log 2>&1 &
echo "VOICEVOX を起動中…"
for i in $(seq 1 120); do
  if curl -s http://127.0.0.1:50021/version >/dev/null; then
    echo "VOICEVOX の準備ができました。"; exit 0
  fi
  sleep 2
done
echo "VOICEVOX が起動しませんでした。voicevox_engine/engine.log を見てください。"; exit 1
