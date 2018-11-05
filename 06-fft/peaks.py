#!/usr/bin/env python3

import wave
import struct
import sys
# import matplotlib.pyplot as plt
import numpy as np

def process(file, windowLen=None, factor=20):
    windowSize = int(file.getframerate() * windowLen)
    # print(file.getnchannels())
    maxpeak = (-1, -1)
    minpeak = (float('inf'), -1)
    for _ in range(file.getnframes() // windowSize):
        x=file.readframes(windowSize)
        sample2 = np.mean(np.reshape(struct.unpack("<{}h".format(windowSize * file.getnchannels()), x), (-1, file.getnchannels())), axis=1)
        # sample = struct.unpack("<{}h".format(windowSize), x)
        vals = np.abs(np.fft.rfft(sample2))
        # plt.plot(range(len(vals)), vals)
        # plt.show()
        a = np.average(vals)
        peaks = [(idx, x) for (idx,), x in np.ndenumerate(vals) if x >= factor * a and x != 0]
        # print(a, peaks)
        if len(peaks) > 0:
            localhigh = max(peaks)
            locallow = min(peaks)
            maxpeak = max(maxpeak, localhigh)
            minpeak = min(minpeak, locallow)
    if maxpeak[0] == -1 or minpeak[0] == float('inf'):
        print('no peaks')
    else:
        print('low = {}, high = {}'.format(minpeak[0] // windowLen, maxpeak[0] // windowLen))

def main(args):
    process(wave.open(args[0], 'r'), windowLen=1)

if __name__ == '__main__':
    main(sys.argv[1:])
