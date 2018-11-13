import wave
import sys
import struct
import numpy as np
from math import log2

def clean_cluster(amp):
    mean = np.mean(amp)
    peaks = np.argwhere(amp >= 20 * mean)
    if peaks.size == 0:
        return []
    expected = None
    run = []    
    clusters = [run]
    # Filter clusters
    for p in peaks:
        if p == expected or expected is None:
            run.append(p)
        else:
            run = [p]
            clusters.append(run)
        expected = p + 1

    clean_peaks = []
    for c in clusters:
        peaks_amp = np.take(amp, c)
        max = np.max(peaks_amp)
        if np.count_nonzero(peaks_amp == max) == 1:
            clean_peaks.append(c[np.argmax(peaks_amp)][0]) # Take the highest peak
        else: # If multiple highest peaks, take one closest to the middle
            maxes = np.argmax(peaks_amp)
            idx = np.abs(maxes - c.size / 2).argmin()
            clean_peaks.append(c[maxes[idx]][0])
    return clean_peaks

def join_windows(window_peaks):
    joined_windows = []
    last = 0
    for i in range(1, len(window_peaks)):
        if not np.array_equal(window_peaks[i], window_peaks[i-1]):
            joined_windows.append((last, i, window_peaks[i-1]))
            last = i
    joined_windows.append((last, len(window_peaks), window_peaks[len(window_peaks) - 1]))
    return joined_windows

def format_freq(frequencies, base_freq):
    names = ["C", "Cis", "D", "Es", "E", "F", "Fis", "G", "Gis", "A", "Bes", "B"]
    s = ""
    for f in frequencies:
        pitch = 12 * log2(f / (base_freq * pow(2, -1.75)))
        octave = int(round(pitch)) // 12
        tone = int(round(pitch)) % 12
        cents = int(round(100 * (pitch - round(pitch))))
        cents_s = str(cents) if cents < 0 else ("+" + str(cents))
        s += " "
        if octave >= 0: 
            s += names[tone].lower() + ("’" * (octave)) + cents_s
        else:
            s += names[tone] + ("," * (abs(octave) - 1)) + cents_s
    return s

def format_output(window_peaks, base_freq):
    for (b, e, f) in window_peaks:
        print(str(b / 10.0) + "-" + str(e / 10.0) + "" + format_freq(f, base_freq))
    
    
    
a = float(sys.argv[1])
# Open wav file
file = sys.argv[2]
wavefile = wave.open(file, 'r')
nframes = wavefile.getnframes()
framerate = wavefile.getframerate()
nchannels = wavefile.getnchannels()
# Read samples from buffer
frames = np.frombuffer(wavefile.readframes(nframes), dtype = np.int16)
wavefile.close()

samples = []

if nchannels == 1:
    for sample in frames:
        unpacked = struct.unpack('h', sample)
        samples.append(float(struct.unpack('h', sample)[0]))
elif nchannels == 2:
    for i in range(0, len(frames), 2):
        unpacked1 = struct.unpack('h', frames[i])[0]
        unpacked2 = struct.unpack('h', frames[i+1])[0]
        s = (float(unpacked1) + float(unpacked2)) / 2.0
        samples.append(s)
else:
    raise ValueError("Not recognized number of channels")

window_size = framerate // 10
nwindows = nframes // window_size - 9 # Ignore last second

window_peaks = []
# For each window
for i in range(nwindows):
    # Calculate amplitudes and put them in absolute value
    amp = np.abs(np.fft.rfft(samples[i * window_size: i * window_size + framerate]))
    
    peaks = clean_cluster(amp)
    
    peak_amps = np.take(amp, peaks)
    
    maxes = np.sort(peak_amps.argsort()[-3:])
    
    max_peaks = np.take(peaks, maxes)
    
    window_peaks.append(max_peaks)
    
window_peaks = join_windows(window_peaks)

format_output(window_peaks, a)