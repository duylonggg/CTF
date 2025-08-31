# Improved DTMF decoder using known timing (tone_time=0.08s, silence_time=0.10s).
# We align a fixed 0.18s stride by trying all possible offsets in [0, step) and
# choosing the one that maximizes summed tone energy across the whole file.

import numpy as np

def read_wav_int16(path):
    try:
        from scipy.io import wavfile
        fs, data = wavfile.read(path)
        if data.dtype != np.int16:
            data = (data / np.max(np.abs(data)) * 32767).astype(np.int16)
        return fs, data
    except Exception:
        import wave, struct
        with wave.open(path, 'rb') as wf:
            fs = wf.getframerate()
            nchan = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            nframes = wf.getnframes()
            raw = wf.readframes(nframes)
            if sampwidth != 2:
                raise RuntimeError(f"Unsupported sample width {sampwidth*8} bits in {path}")
            data = np.frombuffer(raw, dtype=np.int16)
            if nchan == 2:
                data = data.reshape(-1, 2).mean(axis=1).astype(np.int16)
            return fs, data

dtmf_freqs = {
    '1': (697, 1209), '2': (697, 1336), '3': (697, 1477), 'A': (697, 1633),
    '4': (770, 1209), '5': (770, 1336), '6': (770, 1477), 'B': (770, 1633),
    '7': (852, 1209), '8': (852, 1336), '9': (852, 1477), 'C': (852, 1633),
    '*': (941, 1209), '0': (941, 1336), '#': (941, 1477), 'D': (941, 1633),
}
pair_to_key = {v:k for k,v in dtmf_freqs.items()}
lows = [697, 770, 852, 941]
highs = [1209, 1336, 1477, 1633]

def dominant_pair_fft(x, fs):
    N = len(x)
    if N <= 0: return None
    w = np.hanning(N)
    X = np.fft.rfft(x * w)
    freqs = np.fft.rfftfreq(N, d=1/fs)
    mag = np.abs(X)
    def band_energy(target):
        bw = 20.0
        mask = (freqs >= target - bw) & (freqs <= target + bw)
        return mag[mask].sum()
    low_best = max(lows, key=lambda f: band_energy(f))
    high_best = max(highs, key=lambda f: band_energy(f))
    return (low_best, high_best)

def decode_dtmf_wav_fixed_timing(path):
    fs, data = read_wav_int16(path)
    sig = data.astype(np.float32) / 32768.0

    tone_len = int(0.08 * fs)     # 640 at 8kHz
    silence_len = int(0.10 * fs)  # 800 at 8kHz
    step = tone_len + silence_len # 1440 at 8kHz

    # Find best offset in [0, step)
    best_o = 0
    best_energy = -1
    for o in range(step):
        # Sample energies across all tone windows starting at offset o
        energies = []
        k = 0
        while True:
            s = o + k*step
            e = s + tone_len
            if e > len(sig): break
            # Take inner 75% to avoid any possible click at edges
            inner = sig[s + tone_len//8 : e - tone_len//8]
            energies.append(np.sum(inner*inner))
            k += 1
        total = sum(energies)
        if total > best_energy:
            best_energy = total
            best_o = o

    # Decode with best offset
    digits = []
    k = 0
    while True:
        s = best_o + k*step
        e = s + tone_len
        if e > len(sig): break
        chunk = sig[s + tone_len//8 : e - tone_len//8]
        pair = dominant_pair_fft(chunk, fs)
        if pair is None:
            k += 1
            continue
        # snap to nearest nominal freqs in case of slight bias
        low = min(lows, key=lambda f: abs(f - pair[0]))
        high = min(highs, key=lambda f: abs(f - pair[1]))
        key = pair_to_key.get((low, high))
        if key is not None and key.isdigit():
            digits.append(key)
        k += 1

    return ''.join(digits)

# Decode
p_str = decode_dtmf_wav_fixed_timing('/mnt/data/p_dial.wav')
q_str = decode_dtmf_wav_fixed_timing('/mnt/data/q_dial.wav')
c_str = decode_dtmf_wav_fixed_timing('/mnt/data/message.wav')

p, q, c = int(p_str), int(q_str), int(c_str)
n = p*q
e = 65537
phi = (p-1)*(q-1)

def egcd(a, b):
    if b == 0:
        return (1, 0, a)
    x1, y1, g = egcd(b, a % b)
    return (y1, x1 - (a // b) * y1, g)

def invmod(a, m):
    x, y, g = egcd(a, m)
    if g != 1:
        raise ValueError("No inverse")
    return x % m

d = invmod(e, phi)
m = pow(c, d, n)
byte_len = (m.bit_length() + 7)//8
flag = m.to_bytes(byte_len, 'big')
print("Decoded lengths (fixed-timing):", len(p_str), len(q_str), len(c_str))
print("Flag (UTF-8 best effort):")
print(flag.decode('utf-8', errors='ignore'))
