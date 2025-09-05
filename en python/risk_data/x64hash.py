import mmh3

def x64hash128(key, seed=0):
    # The JS implementation is MurmurHash3_x64_128. The mmh3 library can compute this.
    # Note: mmh3 returns a signed integer, so we format it to get the unsigned hex representation.
    hash_val = mmh3.hash128(key, seed, signed=False)
    return f'{hash_val:032x}'