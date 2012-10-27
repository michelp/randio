from hashlib import sha512
from random import Random, randrange
import rtlsdr


class Randio(Random):

    def __init__(self,
                 dev_index=0,
                 freq_range=(64e6, 1100e6, 1000),
                 freq_count=32,
                 sample_size=1024,
                 sample_rate=1.2e6,
                 refresh_rate=None,
                 gain=42):
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

    def sha512(self):
        return sha512("".join(map(str, randio.randio())))


randio = Randio(1, refresh_rate=4)
