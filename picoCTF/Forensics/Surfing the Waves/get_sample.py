from scipy.io import wavfile

rate, data = wavfile.read("main.wav")

print(data[:100])

