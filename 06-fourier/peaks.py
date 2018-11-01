import wave
import sys
import struct
import numpy as np

# Open wav file
wavefile = wave.open(sys.argv[1], 'r')
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
        samples.append(float(struct.unpack('h', sample)[0] / 32767.0))
elif nchannels == 2: 
    for i in range(0, len(frames), 2):
        unpacked1 = struct.unpack('h', frames[i])[0]
        unpacked2 = struct.unpack('h', frames[i+1])[0]
        s = (float(unpacked1 / 32767.0) + float(unpacked2 / 32767.0)) / 2.0
        samples.append(s)
else:
    raise ValueError("Not recognized number of channels")
# Window size
# Used 5 from here http://support.ircam.fr/docs/AudioSculpt/3.0/co/Window%20Size.html
window_size = 5 * framerate
# Splits at given positions
split_at = [i for i in range(window_size, nframes, window_size)] 
# Split array
split = np.array_split(np.array(samples), split_at)

global_min = sys.float_info.max
global_max = sys.float_info.min

# For each window
for s in split:
    # Calculate amplitudes and put them in absolute value
    c = np.abs(np.fft.rfft(s))
    # Calculate mean
    mean = np.mean(c)
    # Filter peaks
    filtered = c[c >= 20 * mean]
    
    # If there are peaks, find the biggest one
    if filtered.size > 0:
        min = np.min(filtered)
        max = np.max(filtered)
        
        if min < global_min:
            global_min = min
        if max > global_max:
            global_max = max

if global_min != sys.float_info.max:
    print("low = " + str(int(global_min)) + ", high = " + str(int(global_max)))
else:
    print("no peaks")
