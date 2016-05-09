randio
======

[DON'T USE THIS You should really go here https://github.com/pwarren/rtl-entropy](https://github.com/pwarren/rtl-entropy)

Random number generator from rtl-sdr supported radio dongles.

    WARNING: I am not a cryptographer and have not formally verified
    the quality of the random data that Randio produces.

Randio data is based on data samples from random radio frequencies.
Randio maintains an "entropy pool" of bytes that is continuously
sha512 hashed with bytes read from the radio.  The pool size frequency
range, and number of radio samples per random frequency hop can be
configured.

Placing your antenna in a high RF environment (outdoors in an urban
area) or sampling a narrower, more active band of frequencies (like
broadcast television) may produce better data by introducing more
radio "noise" into the pool.

Randio provides a subclass of random.Random that acts like a normal
Python random number generator.  There are two versions, a "blocking"
version that refreshes the pool with new entropy every time random
data is asked for (and thus is slow) and a "non-blocking" version
where a background thread polls radio data at regular intervals and
refreshes the pool entropy.

Usage
=====

randio can be installed from Pypi with pip or easy_install:

    pip install randio

And tested interactively from the interpreter by running the module:

    python -i -m 'randio'

When run as a script, the module creates a default randio object that
looks for rtl-sdr dongle number 0.  To have it use another dongle, set
the 'RANDIO_DEV_INDEX' environment variable before running the script.

    $ RANDIO_DEV_INDEX=1 python -i -m randio

When the module imported, there is a couple of second delay while
radio signals are sampled to provide a random number generator seed.
By default randio takes 1024 samples from 32 randomly chosen
frequencies between 64Mhz and 1100Mhz.  To sample a narrower (and
perhaps "noiser") range of frequencies the RANDIO_FREQ_LOW and
RANDIO_FREQ_HIGH environment variables can be set:

    $ RANDIO_FREQ_LOW=470 RANDIO_FREQ_HIGH=692 python -i -m randio
    Found Elonics E4000 tuner
    >>> randio.freq_range
    (470000000.0, 692000000.0, 1000)

The number of samples, frequencies, and frequency range can all be
adjusted with arguments to the Randio class constructor.  See the
source code for details.

A randio object works like any other python Random subclass:

    >>> randio.random()
    0.8497721577857263
    >>> 

Randio objects also provide a 'sha512' hash function that returns a
hash object of the accumulated sample radio data.

    >>> randio.sha512().hexdigest()
    '61bb7e4a1170f2fbdc170ffd8760b192e0d0f3631358c94a87606594571af1beb6507877d3b2838706fc692fdae4ff503393765941d2b44bc0bd7f9e27cf19dd'

The 'sha512' method always gets fresh sample data per call, so will
allways take a few seconds to collect the samples.
