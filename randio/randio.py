import os
from hashlib import sha512
from random import Random, randrange

import rtlsdr


MHZ = 1e6

class Randio(Random):

    def __init__(self,
                 dev_index=None,
                 freq_range=None,
                 freq_count=32,
                 sample_size=1024,
                 sample_rate=1.2e6,
                 refresh_rate=None,
                 gain=42):

        if dev_index is None:
            dev_index = int(os.environ.get('RANDIO_DEV_INDEX', 0))

        if freq_range is None:
            low = int(os.environ.get('RANDIO_FREQ_LOW', 64)) * MHZ
            high = int(os.environ.get('RANDIO_FREQ_HIGH', 1100)) * MHZ
            freq_range = (low, high, 1000)

        self.radio = rtlsdr.RtlSdr(dev_index)
        self.radio.rs = sample_rate
        self.freq_range = freq_range
        self.freq_count = freq_count
        self.sample_size = sample_size
        self.refresh_rate = refresh_rate
        self.remaining = refresh_rate
        super(Randio, self).__init__(self.randio())

    def random(self):
        if self.remaining is not None:
            if self.remaining <= 0:
                self.seed(self.randio())
                self.remaining = self.refresh_rate
            else:
                self.remaining -= 1
        return super(Randio, self).random()

    def randio(self):
        samples = []
        for i in xrange(self.freq_count):
            rrange = randrange(*self.freq_range)
            self.radio.fc = rrange
            samples.append(tuple(self.radio.read_samples(self.sample_size)))
        return tuple(samples)

    def strandio(self):
        return "".join(map(str, self.randio()))

    def sha512(self):
        return sha512(self.strandio())
