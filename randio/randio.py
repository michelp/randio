import os
from binascii import hexlify
from hashlib import sha512
from random import Random, randrange, shuffle, choice

import rtlsdr


MHZ = 1e6
SHA_SIZE = 64
SAMPLE_BLOCK_SIZE = 2**14


class Randio(Random):

    def __init__(self,
                 dev_index=None,
                 freq_range=None,
                 freq_count=128,
                 sample_rate=1.2e6,
                 gain='auto'):

        if dev_index is None:
            dev_index = int(os.environ.get('RANDIO_DEV_INDEX', 0))

        if freq_range is None:
            low = int(os.environ.get('RANDIO_FREQ_LOW', 64)) * MHZ
            high = int(os.environ.get('RANDIO_FREQ_HIGH', 1100)) * MHZ
            freq_range = (low, high, 1000)

        # initialize the pool with some system randomness
        self.pool_size = freq_count * SHA_SIZE
        self.pool = bytearray(" " * self.pool_size)
        view = memoryview(self.pool)
        for i in xrange(0, self.pool_size, SHA_SIZE):
            randbits = hex(self.getrandbits(SHA_SIZE))
            view[i:i+SHA_SIZE] = sha512(randbits).digest()

        self.radio = rtlsdr.RtlSdr(dev_index)
        self.radio.rs = sample_rate
        self.freq_range = freq_range
        self.freq_count = freq_count
        super(Randio, self).__init__()

    def sample(self):
        """ Sample some radio data, stirring it into the pool. """
        view = memoryview(self.pool)
        ranges = range(0, self.pool_size, SHA_SIZE)
        shuffle(ranges)

        for start in ranges:
            rrange = randrange(*self.freq_range)
            self.radio.fc = rrange
            end = start + SHA_SIZE

            # get bytes from pool, hash again
            # read in radio data, more, better
            # update hash with radio data
            # save new hash back to pool
            frompool = sha512(view[start:end].tobytes())
            fromradio = self.radio.read_bytes(SAMPLE_BLOCK_SIZE)
            frompool.update(fromradio)
            view[start:end] = frompool.digest()

    def random(self):
        # take a random int from the pool, seed with it
        i = choice(range(0, self.pool_size, 16))
        view = memoryview(self.pool)
        stuff = view[i:i+16].tobytes()
        a = long(hexlify(stuff), 16)
        self.seed(a)
        return super(Randio, self).random()

    def sha512(self):
        self.sample()
        return sha512(memoryview(self.pool).tobytes())

