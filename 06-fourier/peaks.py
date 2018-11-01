import wave
import sys
import struct
import numpy as np
import pylab

# Open wav file
wavefile = wave.open(sys.argv[1], 'r')
nframes = wavefile.getnframes()
framerate = wavefile.getframerate()
  
# Read samples from buffer
frames = np.frombuffer(wavefile.readframes(nframes), dtype = np.int16)
wavefile.close()

array = []
# Convert samples to float
for sample in frames:
    array.append(float(struct.unpack('h', sample)[0] / 32767.0))

# Window size
# Used 5 from here http://support.ircam.fr/docs/AudioSculpt/3.0/co/Window%20Size.html
window_size = 5 * framerate
# Splits at given positions
split_at = [i for i in range(window_size, nframes, window_size)] 
# Split array
split = np.array_split(np.array(array), split_at)

global_min = sys.float_info.max
global_max = sys.float_info.min

# For each window
for s in split:
    # Calculate amplitudes and put them in absolute value
    c = np.abs(np.fft.rfft(s))
    print(len(s))
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
# Write out the peaks
print("Min: " + str(int(global_min)))
print("Max: " + str(int(global_max)))
    
# DELETE
pylab.plot(t, array)
pylab.show()
    
