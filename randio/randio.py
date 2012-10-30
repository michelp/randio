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
                 freq_count=None,
                 sample_rate=None,
                 gain=None):

        eget = os.environ.get
        if dev_index is None:
            dev_index = int(eget('RANDIO_DEV_INDEX', 0))

        if freq_range is None:
            low = int(eget('RANDIO_FREQ_LOW', 64)) * MHZ
            high = int(eget('RANDIO_FREQ_HIGH', 1100)) * MHZ
            freq_range = (low, high, 1000)

        if freq_count is None:
            freq_count = int(eget('RANDIO_FREQ_COUNT', 32))

        if sample_rate is None:
            sample_rate = float(eget('RANDIO_SAMPLE_RATE', 1.2)) * MHZ

        if gain is None and 'RANDIO_GAIN' in os.environ:
            gain = int(eget('RANDIO_GAIN'))
        else:
            gain = 'auto'

        self.pool_size = freq_count * SHA_SIZE
        self.pool = bytearray(" " * self.pool_size)
        self.poolblocks = range(0, self.pool_size, SHA_SIZE)
        self.radio = rtlsdr.RtlSdr(dev_index)
        self.radio.rs = sample_rate
        self.radio.gain = gain
        self.freq_range = freq_range
        self.freq_count = freq_count
        self.sample()
        super(Randio, self).__init__()

    def _sample_block(self, start, view):
        """Take a block offset, resample the block.

        Hashes the block, then updates the hash with radio data of
        SAMPLE_BLOCK_SIZE from a random frequency in the freq_range.
        The updated hash is then written back to the block.
        """
        end = start + SHA_SIZE
        frompool = sha512(view[start:end].tobytes())
        freq = randrange(*self.freq_range)
        self.radio.fc = freq
        fromradio = self.radio.read_bytes(SAMPLE_BLOCK_SIZE)
        frompool.update(fromradio)
        view[start:end] = frompool.digest()

    def sample(self):
        """ Sample some radio data over all blocks, stirring the data
        into the pool.

        This shuffles the pool block order and resamples them in
        shuffled order.  Every block has a random frequencies worth of
        radio data hashed into it.
        """
        view = memoryview(self.pool)
        blocks = self.poolblocks[:]
        shuffle(blocks)
        for start in blocks:
            self._sample_block(start, view)

    def random(self):
        """Takes a random block from the pool, casts it to a long,
        then seeds the RNG with it.  The block is then resampled.
        """
        blocks = self.poolblocks[:]
        block = choice(blocks)
        view = memoryview(self.pool)
        stuff = view[block:block+SHA_SIZE].tobytes()
        a = long(hexlify(stuff), 16)
        self.seed(a)
        self._sample_block(block, view)
        return super(Randio, self).random()

    def sha512(self):
        """Return a sha512 hash of a random block in the pool, then
        resample that block.
        """
        blocks = self.poolblocks[:]
        block = choice(blocks)
        view = memoryview(self.pool)
        result = sha512(view[block:block+SHA_SIZE].tobytes())
        self._sample_block(block, view)
        return result
