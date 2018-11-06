#!/usr/bin/env python3
import math
import wave
import struct
import sys
import numpy as np

def formatNote(octave, tone):
    names = ['C', 'Cis', 'D', 'Es', 'E', 'F', 'Fis', 'G', 'Gis', 'A', 'Bes', 'B']
    t = names[tone]
    if octave >= 0:
        return t.lower() + ("'" * octave)
    else:
        return t + (',' * (-1 * octave))

def freq2note(f, baseFreq):
    c = baseFreq * pow(2, -(12 + 9)/12)
    n = 12*(math.log2(f) - math.log2(c))
    octavesOffset = int(n // 12)
    toneOffset = int(n % 12)
    cents = int(100*(n % 1))
    if cents >= 50:
        toneOffset += 1
        cents = 100 - cents
    if toneOffset >= 12:
        toneOffset = toneOffset - 12
        octavesOffset += 1
    return '{}{:+d}'.format(formatNote(octavesOffset, toneOffset), cents)

def formatwin(win, windowLen, baseFreq):
    begin = win['range']['from'] * windowLen
    end = win['range']['to'] * windowLen
    tones = ' '.join([freq2note(w, baseFreq) for w in win['window']])
    return '{:04.1f}-{:04.1f} {}'.format(begin, end, tones)


def process(baseF, file, windowLen, factor=20):
    windowSize = int(file.getframerate() * windowLen)
    windows = []
    for window in range(file.getnframes() // windowSize):
        x = file.readframes(windowSize)
        sample = np.mean(np.reshape(struct.unpack("<{}h".format(windowSize * file.getnchannels()), x), (-1, file.getnchannels())), axis=1)
        vals = np.abs(np.fft.rfft(sample))
        a = np.average(vals)
        peaks = sorted([f for f, _ in sorted([(int(idx / windowLen), x) for (idx,), x in np.ndenumerate(vals) if x >= factor * a and x != 0], key=lambda x: -x[1])[:3]])
        windows.append(peaks)
    mergedWindows = []
    for idx, window in enumerate(windows):
        if window == []:
            continue
        lst = mergedWindows[-1]['window'] if mergedWindows else None
        if lst == window:
            mergedWindows[-1]['range']['to'] = idx
        else:
            mergedWindows.append({'range': {'from': idx, 'to': idx}, 'window': window})
    for win in mergedWindows:
        print(formatwin(win, windowLen, baseF))
        

def main(args):
    process(int(args[0]), wave.open(args[1], 'r'), windowLen=0.1)

if __name__ == '__main__':
    main(sys.argv[1:])
