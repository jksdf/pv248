#!/usr/bin/env python3

# based on : www.daniweb.com/code/snippet263775.html
import math
import wave
import struct
import numpy as np

class Sound:

    def __init__(self, secs, frate, channels=1):
        self.data = np.zeros((int(frate * secs), channels), np.float)
        self.frate = frate

    def make_sine(self, freq, vol=1.0, start=0.0, end=None, channel=0):
        end = len(self.data) if end is None else end
        start, end = int(start), int(end)
        for x in range(start, end - start):
            self.data[x][channel] += vol * math.sin(2*math.pi * freq * ((x - start)/self.frate))
        return self


    def save(self, fname, amp, sampwidth = 2, comptype= "NONE", compname= "not compressed"):
        wav_file = wave.open(fname, "w")
        nframes = len(self.data)
        channels = len(self.data[0])
        wav_file.setparams((channels, sampwidth, int(self.frate), nframes, comptype, compname))
        for s in self.data:
            wav_file.writeframes(struct.pack('<{}h'.format(channels), *map(int, s * amp / 2)))
        wav_file.close()

frate = 44100.00 #that's the framerate
seconds = 3 #seconds of file
fname = "WaveTest4mono.wav"
Sound(seconds, frate, 1).make_sine(440, vol=1, start=0, end=1.5*frate, channel=0).make_sine(932.33, start=1*frate, channel=0).save(fname, 10000)