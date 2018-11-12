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
        cents = cents - 100
    if toneOffset >= 12:
        toneOffset = toneOffset - 12
        octavesOffset += 1
    return '{}{:+d}'.format(formatNote(octavesOffset, toneOffset), cents)

def formatwin(win, windowLen, baseFreq):
    begin = win['range']['from'] * windowLen
    end = (win['range']['to'] + 1) * windowLen
    tones = ' '.join([freq2note(w, baseFreq) for w in win['window']])
    return '{:04.1f}-{:04.1f} {}'.format(begin, end, tones)


def clearCluster(peaks):
    runs = []
    for f, a in peaks:
        if (runs[-1][-1][0] if runs else None) == f - 1:
            runs[-1].append((f, a))
        else:
            runs.append([(f, a)])
    cleared = []
    for run in runs:
        if len(run) == 1:
            cleared.append(run[0])
        else:
            cleared.append(max(run, key=lambda x: x[1]))
    return cleared

def process(baseF, file, windowLen, factor=20):
    windowSize = int(file.getframerate() * windowLen)
    rolling = []
    for _ in range(9):
        rolling += struct.unpack("<{}h".format(windowSize * file.getnchannels()), file.readframes(windowSize))
    windows = []
    for window in range(file.getnframes() // windowSize - 9):
        rolling += struct.unpack("<{}h".format(windowSize * file.getnchannels()), file.readframes(windowSize))
        sample = np.mean(np.reshape(rolling, (-1, file.getnchannels())), axis=1)
        del rolling[:windowSize * file.getnchannels()]
        vals = np.abs(np.fft.rfft(sample))
        a = np.average(vals)
        peaks = sorted([f for f, _ in sorted(clearCluster([(int(idx / windowLen / 10), x) for (idx,), x in np.ndenumerate(vals) if x >= factor * a and x != 0]), key=lambda x: -x[1])[:3]])
        windows.append(peaks)
    mergedWindows = []
    for idx, window in enumerate(windows):
        lst = mergedWindows[-1]['window'] if mergedWindows else None
        if lst == window:
            mergedWindows[-1]['range']['to'] = idx
        else:
            mergedWindows.append({'range': {'from': idx, 'to': idx}, 'window': window})
    for win in mergedWindows:
        if len(win['window']) != 0:
            print(formatwin(win, windowLen, baseF))
        

def main(args):
    process(int(args[0]), wave.open(args[1], 'r'), windowLen=0.1)

if __name__ == '__main__':
    main(sys.argv[1:])
