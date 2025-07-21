#!/usr/bin/env python3
import wave
import numpy as np
import scipy.fftpack as fft
import sys
import subprocess

# --- 1. Reverse audio (nếu muốn tự động trong Python) ---
def reverse_wav(in_path, out_path):
    # Dùng sox nếu đã cài: sox infile.wav outfile.wav reverse
    subprocess.run(['sox', in_path, out_path, 'reverse'], check=True)

# --- 2. Đọc WAV vào numpy array ---
def load_wav(path):
    wf = wave.open(path, 'rb')
    sr = wf.getframerate()
    data = wf.readframes(wf.getnframes())
    # giả sử 16‑bit PCM
    samples = np.frombuffer(data, dtype=np.int16)
    wf.close()
    return samples, sr

# --- 3. Extract XOR key từ tín hiệu tần số ---
def extract_xor_key(rev_samples, sr, window_ms=100):
    win_size = int(sr * window_ms/1000)
    key_bits = []
    for start in range(0, len(rev_samples) - win_size, win_size):
        frame = rev_samples[start:start+win_size] * np.hanning(win_size)
        # FFT
        spectrum = np.abs(fft.fft(frame))[:win_size//2]
        freqs = np.fft.fftfreq(win_size, 1/sr)[:win_size//2]
        # tìm biên độ tại ~500Hz và ~1000Hz
        idx500 = np.argmin(np.abs(freqs - 500))
        idx1000= np.argmin(np.abs(freqs -1000))
        amp500 = spectrum[idx500]
        amp1000= spectrum[idx1000]
        bit = 1 if amp1000 > amp500 else 0
        key_bits.append(bit)
    # gom mỗi 8 bit thành 1 byte
    key_bytes = []
    for i in range(0, len(key_bits)//8*8, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | key_bits[i+j]
        key_bytes.append(byte)
    return bytes(key_bytes)

# --- 4. Lấy LSB payload từ cuối file ---
def extract_lsb_payload(samples, sr, noise_seconds=10):
    # giả định payload nằm trong last noise_seconds giây
    tail = samples[-noise_seconds*sr:]
    # lấy 1 bit LSB
    bits = tail & 1
    # gom 8 bit thành 1 byte
    data = []
    for i in range(0, len(bits)//8*8, 8):
        byte = 0
        for j in range(8):
            byte = (byte << 1) | int(bits[i+j])
        data.append(byte)
    return bytes(data)

# --- 5. XOR decode và tìm flag ---
def xor_decode(data, key):
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))

# === Main ===
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} chant_of_the_drones.wav")
        sys.exit(1)

    orig = sys.argv[1]
    rev = 'reversed.wav'

    print('[*] Reversing audio…')
    reverse_wav(orig, rev)

    print('[*] Loading reversed audio…')
    samples, sr = load_wav(rev)

    print('[*] Extracting XOR key from 500/1000 Hz pattern…')
    key = extract_xor_key(samples, sr)
    print(f'    -> Key bytes: {key.hex()}')

    print('[*] Loading original audio for payload extraction…')
    orig_samples, orig_sr = load_wav(orig)
    if orig_sr != sr:
        print('Warning: sample rates differ!')

    print('[*] Extracting LSB payload from last 10 seconds…')
    payload = extract_lsb_payload(orig_samples, sr, noise_seconds=10)
    print(f'    -> Raw payload ({len(payload)} bytes)')

    print('[*] XOR‑decoding payload…')
    decoded = xor_decode(payload, key)

    # Tìm chuỗi BDSEC{…}
    text = decoded.decode('utf-8', errors='ignore')
    start = text.find('BDSEC{')
    end   = text.find('}', start) + 1
    flag  = text[start:end] if start != -1 and end != -1 else None

    if flag:
        print(f'\n*** FLAG: {flag} ***\n')
    else:
        print('\n[!] Không tìm thấy flag—hãy kiểm tra lại vị trí payload, độ dài key, hoặc tăng giảm window_ms / noise_seconds.\n')

