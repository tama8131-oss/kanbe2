"""
BGM と効果音をプログラムで作る（著作権の心配ゼロ・お金ゼロ）。

- BGM：ローファイ風のゆったりした曲。動画ごとに調とコード進行を変えて、毎回同じにならんようにする
- 効果音：字幕が出るときの「ポンッ」、セリフが切り替わるときの「シュッ」、最後の「キラーン」
- 声が出ている間は BGM を小さくして（ダッキング）、声を聞き取りやすくする
"""
import numpy as np

NOTE = {"C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6, "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11}

# コード進行（ルートからの半音の距離で書く）。動画ごとに選ぶ
PROGRESSIONS = [
    # IVmaj7 - V - iii7 - vi7（王道の前向き進行）
    [(5, [0, 4, 7, 11]), (7, [0, 4, 7, 10]), (4, [0, 3, 7, 10]), (9, [0, 3, 7, 10])],
    # I - V - vi - IV
    [(0, [0, 4, 7, 11]), (7, [0, 4, 7]), (9, [0, 3, 7, 10]), (5, [0, 4, 7, 11])],
    # vi - IV - I - V
    [(9, [0, 3, 7, 10]), (5, [0, 4, 7, 11]), (0, [0, 4, 7, 14]), (7, [0, 4, 7])],
    # ii7 - V7 - Imaj7 - vi7（ジャジー）
    [(2, [0, 3, 7, 10]), (7, [0, 4, 7, 10]), (0, [0, 4, 7, 11]), (9, [0, 3, 7, 10])],
]
KEYS = [0, 2, -3, 5, -2, 3, -5]  # 調（半音でずらす）
TEMPOS = [88, 92, 84, 96, 90]


def midi_hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def _env(n, rate, attack, decay):
    t = np.arange(n) / rate
    a = np.clip(t / max(attack, 1e-4), 0, 1)
    return a * np.exp(-t / max(decay, 1e-4))


def _lowpass(x, k):
    if k <= 1:
        return x
    kernel = np.ones(k) / k
    return np.convolve(x, kernel, mode="same")


def make_bgm(n, rate, variant=0, seed=0):
    """長さ n サンプルの BGM（-1〜1 の float32）"""
    rng = np.random.default_rng(seed)
    prog = PROGRESSIONS[variant % len(PROGRESSIONS)]
    key = KEYS[variant % len(KEYS)]
    bpm = TEMPOS[variant % len(TEMPOS)]
    beat = 60.0 / bpm
    bar = beat * 4
    out = np.zeros(n, dtype=np.float32)
    t_all = np.arange(n) / rate

    total_bars = int(np.ceil(n / rate / bar)) + 1
    for b in range(total_bars):
        root_off, chord = prog[b % len(prog)]
        start = int(b * bar * rate)
        if start >= n:
            break
        length = min(int(bar * rate), n - start)
        tt = np.arange(length) / rate
        base = 57 + key + root_off  # A3 あたり

        # パッド（やわらかい和音）
        pad = np.zeros(length)
        for iv in chord:
            f = midi_hz(base + iv)
            for det in (0.997, 1.003):
                pad += np.sin(2 * np.pi * f * det * tt)
        pad_env = np.clip(tt / 0.4, 0, 1) * np.clip((bar - tt) / 0.3, 0, 1)
        out[start:start + length] += 0.035 * pad * pad_env

        # ベース（1拍目と3拍目）
        for bt in (0, 2):
            s = int(bt * beat * rate)
            if s >= length:
                continue
            m = min(int(beat * 1.8 * rate), length - s)
            ts = np.arange(m) / rate
            f = midi_hz(base - 12)
            bass = np.sin(2 * np.pi * f * ts) + 0.3 * np.sin(2 * np.pi * 2 * f * ts)
            out[start + s:start + s + m] += 0.12 * bass * _env(m, rate, 0.01, 0.5)

        # アルペジオ（8分音符でポロポロ）
        notes = [base + 12 + chord[i % len(chord)] for i in range(8)]
        for i, mn in enumerate(notes):
            s = int(i * beat / 2 * rate)
            if s >= length or rng.random() < 0.2:
                continue
            m = min(int(0.5 * rate), length - s)
            ts = np.arange(m) / rate
            f = midi_hz(mn)
            tri = 2 / np.pi * np.arcsin(np.sin(2 * np.pi * f * ts))
            out[start + s:start + s + m] += 0.03 * tri * _env(m, rate, 0.005, 0.18)

        # キック（1・3拍目）とハイハット（裏拍）
        for bt in range(4):
            s = int(bt * beat * rate)
            if s >= length:
                continue
            if bt in (0, 2):
                m = min(int(0.18 * rate), length - s)
                ts = np.arange(m) / rate
                freq = 50 + 70 * np.exp(-ts / 0.03)
                phase = 2 * np.pi * np.cumsum(freq) / rate
                out[start + s:start + s + m] += 0.18 * np.sin(phase) * _env(m, rate, 0.002, 0.08)
            hs = s + int(beat / 2 * rate)
            if hs < length:
                m = min(int(0.04 * rate), length - hs)
                noise = rng.standard_normal(m)
                noise = np.diff(noise, prepend=0)  # 高い音だけ残す
                out[start + hs:start + hs + m] += 0.012 * noise * _env(m, rate, 0.001, 0.012)

    out = _lowpass(out, 3)
    peak = np.max(np.abs(out)) or 1.0
    out = out / peak
    # フェードイン・フェードアウト
    fade_in = np.clip(t_all / 0.4, 0, 1)
    fade_out = np.clip((t_all[-1] - t_all) / 1.0, 0, 1)
    return (out * fade_in * fade_out).astype(np.float32)


def sfx_pop(rate):
    m = int(0.07 * rate)
    t = np.arange(m) / rate
    freq = 700 + 900 * (t / t[-1])
    phase = 2 * np.pi * np.cumsum(freq) / rate
    return (np.sin(phase) * _env(m, rate, 0.002, 0.025)).astype(np.float32)


def sfx_whoosh(rate, seed=1):
    rng = np.random.default_rng(seed)
    m = int(0.28 * rate)
    t = np.arange(m) / rate
    noise = _lowpass(rng.standard_normal(m), 6)
    env = np.sin(np.pi * t / t[-1]) ** 2
    return (noise / (np.max(np.abs(noise)) or 1) * env).astype(np.float32)


def sfx_ding(rate):
    m = int(0.9 * rate)
    t = np.arange(m) / rate
    s = np.sin(2 * np.pi * 1318.5 * t) + 0.6 * np.sin(2 * np.pi * 1975.5 * t)
    return (s / 1.6 * _env(m, rate, 0.003, 0.3)).astype(np.float32)


def add_at(buf, clip, pos, gain):
    if pos >= len(buf):
        return
    end = min(len(buf), pos + len(clip))
    buf[pos:end] += gain * clip[:end - pos]


def mix(voice_i16, rate, events, variant=0, bgm_level=0.10):
    """
    声（int16）に BGM と効果音を重ねて int16 で返す。
    events: [(秒, "pop"|"whoosh"|"ding"), ...]
    """
    voice = voice_i16.astype(np.float32) / 32768.0
    n = len(voice)
    bgm = make_bgm(n, rate, variant=variant, seed=variant)

    # ダッキング：声が出ているところは BGM を下げる
    win = int(0.05 * rate)
    env = np.sqrt(_lowpass(voice ** 2, win))
    talking = np.clip(env / 0.02, 0, 1)
    talking = _lowpass(talking, int(0.15 * rate))
    duck = 1.0 - 0.55 * talking
    out = voice + bgm * bgm_level * duck

    clips = {"pop": (sfx_pop(rate), 0.10), "whoosh": (sfx_whoosh(rate), 0.07), "ding": (sfx_ding(rate), 0.12)}
    for sec, kind in events:
        clip, gain = clips[kind]
        add_at(out, clip, int(sec * rate), gain)

    peak = np.max(np.abs(out))
    if peak > 0.98:
        out = out * (0.98 / peak)
    return (out * 32767).astype(np.int16)
