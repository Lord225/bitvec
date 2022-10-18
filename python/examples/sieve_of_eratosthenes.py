from bitvec import Binary

primes = Binary(-1, lenght=100000)
primes[:2] = False

for i in range(2, int(len(primes)**0.5)+1):
    if primes[i]:
        primes[2*i::i] = False

# If you need just prime count
print(primes.count_ones())

# If you need primes 
primes = primes.find_ones() 
print(f'Found: {len(primes)} primes, first 10 are: {primes[:10]}') 
