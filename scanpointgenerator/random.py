

class Random(object):

    # See: https://en.wikipedia.org/wiki/Mersenne_Twister - MT19937

    w = 32              # Word size
    n = 624             # Degree of recurrence
    m = 397             # Middle word offset
    r = 31              # Lower bit mask length
    a = 0x9908B0DF      # Twist matrix elements
    f = 1812433253      # Initialisation constant

    lower_mask = (1 << r) - 1  # Mask of `r` 1s
    upper_mask = 0xFFFFFFFF & (~lower_mask)  # 32 LSB of (NOT lower_mask)

    s_shift = 7         # Tempering bit shifts and masks
    t_shift = 15
    b_mask = 0x9D2C5680
    c_mask = 0xEFC60000

    u_shift = 11        # Additional bit shifts and mask
    l_shift = 18
    d_mask = 0xFFFFFFFF

    def __init__(self, seed):

        self.index = 0
        self.seeds = [seed]  # Initialize the initial state to the seed
        for i in range(1, self.n):
            self.seeds.append(self._int32(
                self.f * (self.seeds[i - 1] ^ self.seeds[i - 1] >> 30) + i))

        self.twist()

    def generate_number(self):

        number = 0
        while len(str(number)) != 10:

            if self.index >= self.n:
                self.twist()
                self.index = 0

            number = self.seeds[self.index]

            # Do some bit shifting and XOR-ing
            number ^= number >> self.u_shift
            number ^= number << self.s_shift & self.b_mask
            number ^= number << self.t_shift & self.c_mask
            number ^= number >> self.l_shift

            self.index += 1

        return self._int32(number)

    def twist(self):
        for i in range(self.n):
            # Get the most significant bit and add it to the less significant
            # bits of the next number
            y = self._int32((self.seeds[i] & self.upper_mask) +
                            (self.seeds[(i + 1) % self.n] & self.lower_mask))
            self.seeds[i] = self.seeds[(i + self.m) % self.n] ^ y >> 1

            if y % 2 != 0:
                self.seeds[i] ^= self.a

    def random(self):

        rand = str(self.generate_number())[::-1]

        decimal = float(rand[0] + '.' + rand[1:])  # -> 0.0 to 10.0
        decimal %= 2                               # -> 0.0 to 1.0
        decimal -= 1.0                             # -> -1.0 to 1.0
        
        return decimal

    @staticmethod
    def _int32(number):
        # Get the 32 least significant bits.
        return int(0xFFFFFFFF & number)


# class Random2(object):
#
#     def __init__(self, seed=1):
#         self.x = seed
#
#     def random(self):
#
#         self.x ^= self.x >> 12
#         self.x ^= self.x << 25
#         self.x ^= self.x >> 27
#
#         rand = str(self.x * 2685821657736338717)
#         decimal = float(rand[0] + '.' + rand[1:25])
#
#         while decimal > 1.0:
#             decimal -= 2.0
#
#         return decimal
