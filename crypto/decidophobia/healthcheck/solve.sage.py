

# This file was *autogenerated* from the file ../healthcheck/solve.sage
from sage.all_cmdline import *   # import sage library

_sage_const_512 = Integer(512); _sage_const_384 = Integer(384); _sage_const_2 = Integer(2); _sage_const_0x10001 = Integer(0x10001); _sage_const_1 = Integer(1); _sage_const_0p6 = RealNumber('0.6'); _sage_const_0p36 = RealNumber('0.36'); _sage_const_3 = Integer(3); _sage_const_0 = Integer(0)
from pwn import *

server = process("./server.py")
# server = remote("127.0.0.1", 1337)

"""
	Get RSA-encrypted ticket `enc` and the modulus `n`
"""
server.sendlineafter(">>>", "1")
server.recvuntil("n = ")
n = int(server.recvline().decode().strip())
server.recvuntil("enc = ")
enc = int(server.recvline().decode().strip())

"""
	Get information provided by RSA-based OT, notice that we don't need to know `x3` 
"""
server.sendlineafter(">>>", "2")
server.sendlineafter(">>>", "2") # Ignore Mercury for sure
server.recvuntil("N = ")
N = int(server.recvline().decode().strip())
server.recvuntil("x1 = ")
x1 = int(server.recvline().decode().strip())
server.recvuntil("x2 = ")
x2 = int(server.recvline().decode().strip())

"""
	Compute the cool value `v` so that the linear combination `hint` of p and q can be revealed
"""
nbits, mbits = _sage_const_512 , _sage_const_384 
k = _sage_const_2  * mbits - nbits
a = -_sage_const_2 **k
ae = int(pow(a, _sage_const_0x10001 , N))
v = (ae * x2 - x1) * inverse_mod(ae - _sage_const_1 , N) % N

server.sendlineafter("Gimme your response: ", str(int(v)))
server.recvuntil("c1 = ")
c1 = int(server.recvline().decode().strip())
server.recvuntil("c2 = ")
c2 = int(server.recvline().decode().strip())

"""
	Calculate the coefficients, which will be used later
		`q_h`: higher bits of q
		`p_l`: lower bits of p
		`s`  : the sum of lower bits of q and higher bits of p
"""
hint = (c1 - a * c2) % N
q_h = hint >> nbits
p_l = hint % _sage_const_2 **k
s = (hint >> k) % _sage_const_2 **(nbits-k)

"""
	Construct the polynomial and run Coopersmith with suitable parameters
"""
PR = PolynomialRing(Zmod(n), names=('x',)); (x,) = PR._first_ngens(1)
f = (q_h * _sage_const_2 **(nbits-k) + (s-x)) * (x * _sage_const_2 **k + p_l)
f = f.monic()
x = f.small_roots(X = _sage_const_2 **(nbits-k), beta = _sage_const_0p6 , epsilon = _sage_const_0p36  - (nbits-k)/(_sage_const_3 *nbits-_sage_const_1 ))
for xx in x:
	p = int(xx) * _sage_const_2 **k + p_l
	if n % p == _sage_const_0 :
		q = (hint - p) // _sage_const_2 **k
		r = n // p // q
		d = int(pow(_sage_const_0x10001 , -_sage_const_1 , (p-_sage_const_1 )*(q-_sage_const_1 )*(r-_sage_const_1 )))
		ticket = pow(enc, d, n)

		server.sendlineafter(">>>", "4")
		server.sendlineafter("Give me your ticket. ", str(int(ticket)))
		_ = server.recvline() 
		flag = server.recvline()
		print(flag)
		exit(_sage_const_0 )
exit(_sage_const_1 )
		

