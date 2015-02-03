#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#=======================================================================
#
# siphash.py
# ---------
# Simple model of the Siphash stream cipher. Used as a reference for
# the HW implementation. The code follows the structure of the
# HW implementation as much as possible.
#
#
# Copyright (c) 2013 Secworks Sweden AB
# Author: Joachim Strömbergson
#
# Redistribution and use in source and binary forms, with or
# without modification, are permitted provided that the following
# conditions are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
# STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#=======================================================================

#-------------------------------------------------------------------
# Python module imports.
#-------------------------------------------------------------------
import sys


#-------------------------------------------------------------------
# Constants.
#-------------------------------------------------------------------
TAU   = [0x61707865, 0x3120646e, 0x79622d36, 0x6b206574]
SIGMA = [0x61707865, 0x3320646e, 0x79622d32, 0x6b206574]


#-------------------------------------------------------------------
# ChaCha()
#-------------------------------------------------------------------
class SipHash():

    #---------------------------------------------------------------
    # __init__()
    #
    # Given the key, iv initializes the state of the cipher.
    # The number of rounds used can be set. By default 8 rounds
    # are used. Accepts a list of either 16 or 32 bytes as key.
    # Accepts a list of 8 bytes as IV.
    #---------------------------------------------------------------
    def __init__(self, key, iv, rounds = 8, verbose = 0):
        self.state = [0] * 16
        self.x = [0] * 16
        self.rounds = rounds
        self.verbose = verbose
        self.set_key_iv(key, iv)


    #---------------------------------------------------------------
    # set_key()
    #
    # Set key.
    #---------------------------------------------------------------
    def set_key(self, key):
        self.v0 = k[0] ^ 0x736f6d6570736575
        self.v1 = k[1] ^ 0x646f72616e646f6d
        self.v2 = k[0] ^ 0x6c7967656e657261
        self.v3 = k[1] ^ 0x7465646279746573


    #---------------------------------------------------------------
    # next()
    #
    # Encyp/decrypt the next block. This also updates the
    # internal state and increases the block counter.
    #---------------------------------------------------------------
    def next(self, data_in):
        # Copy the current internal state to the temporary state x.
        self.x = self.state[:]

        if self.verbose:
            print("State before round processing.")
            self._print_state()

        if self.verbose:
            print("X before round processing:")
            self._print_x()

        # Update the internal state by performing
        # (rounds / 2) double rounds.
        for i in range(int(self.rounds / 2)):
            if (self.verbose > 1):
                print("Doubleround 0x%02x:" % i)
            self._doubleround()
            if (self.verbose > 1):
                print("")

        if self.verbose:
            print("X after round processing:")
            self._print_x()

        # Update the internal state by adding the elements
        # of the temporary state to the internal state.
        self.state = [((self.state[i] + self.x[i]) & 0xffffffff) for i in range(16)]

        if self.verbose:
            print("State after round processing.")
            self._print_state()

        bytestate = []
        for i in self.state:
            bytestate += self._w2b(i)

        # Create the data out words.
        data_out = [data_in[i] ^ bytestate[i] for i in range(64)]

        # Update the block counter.
        self._inc_counter()

        return data_out


    #---------------------------------------------------------------
    # _doubleround()
    #
    # Perform the two complete rounds that comprises the
    # double round.
    #---------------------------------------------------------------
    def _doubleround(self):
        if (self.verbose > 0):
            print("Start of double round processing.")

        self._quarterround(0, 4,  8, 12)
        if (self.verbose > 1):
            print("X after QR 0")
            self._print_x()
        self._quarterround(1, 5,  9, 13)
        if (self.verbose > 1):
            print("X after QR 1")
            self._print_x()
        self._quarterround(2, 6, 10, 14)
        if (self.verbose > 1):
            print("X after QR 2")
            self._print_x()
        self._quarterround(3, 7, 11, 15)
        if (self.verbose > 1):
            print("X after QR 3")
            self._print_x()

        self._quarterround(0, 5, 10, 15)
        if (self.verbose > 1):
            print("X after QR 4")
            self._print_x()
        self._quarterround(1, 6, 11, 12)
        if (self.verbose > 1):
            print("X after QR 5")
            self._print_x()
        self._quarterround(2, 7,  8, 13)
        if (self.verbose > 1):
            print("X after QR 6")
            self._print_x()
        self._quarterround(3, 4,  9, 14)
        if (self.verbose > 1):
            print("X after QR 7")
            self._print_x()

        if (self.verbose > 0):
            print("End of double round processing.")


    #---------------------------------------------------------------
    #  _quarterround()
    #
    # Updates four elements in the state vector x given by
    # their indices.
    #---------------------------------------------------------------
    def _quarterround(self, ai, bi, ci, di):
        # Extract four elemenst from x using the qi tuple.
        a, b, c, d = self.x[ai], self.x[bi], self.x[ci], self.x[di]

        if (self.verbose > 1):
            print("Indata to quarterround:")
            print("X state indices:", ai, bi, ci, di)
            print("a = 0x%08x, b = 0x%08x, c = 0x%08x, d = 0x%08x" %\
                  (a, b, c, d))
            print("")

        a0 = (a + b) & 0xffffffff
        d0 = d ^ a0
        d1 = ((d0 << 16) + (d0 >> 16)) & 0xffffffff
        c0 = (c + d1) & 0xffffffff
        b0 = b ^ c0
        b1 = ((b0 << 12) + (b0 >> 20)) & 0xffffffff
        a1 = (a0 + b1) & 0xffffffff
        d2 = d1 ^ a1
        d3 = ((d2 << 8) + (d2 >> 24)) & 0xffffffff
        c1 = (c0 + d3) & 0xffffffff
        b2 = b1 ^ c1
        b3 = ((b2 << 7) + (b2 >> 25)) & 0xffffffff

        if (self.verbose > 2):
            print("Intermediate values:")
            print("a0 = 0x%08x, a1 = 0x%08x" % (a0, a1))
            print("b0 = 0x%08x, b1 = 0x%08x, b2 = 0x%08x, b3 = 0x%08x" %\
                  (b0, b1, b2, b3))
            print("c0 = 0x%08x, c1 = 0x%08x" % (c0, c1))
            print("d0 = 0x%08x, d1 = 0x%08x, d2 = 0x%08x, d3 = 0x%08x" %\
                  (d0, d1, d2, d3))
            print("")

        a_prim = a1
        b_prim = b3
        c_prim = c1
        d_prim = d3

        if (self.verbose > 1):
            print("Outdata from quarterround:")
            print("a_prim = 0x%08x, b_prim = 0x%08x, c_prim = 0x%08x, d_prim = 0x%08x" %\
                  (a_prim, b_prim, c_prim, d_prim))
            print("")

        # Update the four elemenst in x using the qi tuple.
        self.x[ai], self.x[bi] = a_prim, b_prim
        self.x[ci], self.x[di] = c_prim, d_prim


    #---------------------------------------------------------------
    # _inc_counter()
    #
    # Increase the 64 bit block counter.
    #---------------------------------------------------------------
    def _inc_counter(self):
        self.block_counter[0] += 1 & 0xffffffff
        if not (self.block_counter[0] % 0xffffffff):
            self.block_counter[1] += 1 & 0xffffffff


    #---------------------------------------------------------------
    # _b2w()
    #
    # Given a list of four bytes returns the little endian
    # 32 bit word representation of the bytes.
    #---------------------------------------------------------------
    def _b2w(self, bytes):
        return (bytes[0] + (bytes[1] << 8)
                + (bytes[2] << 16) + (bytes[3] << 24)) & 0xffffffff


    #---------------------------------------------------------------
    # _w2b()
    #
    # Given a 32-bit word returns a list of set of four bytes
    # that is the little endian byte representation of the word.
    #---------------------------------------------------------------
    def _w2b(self, word):
        return [(word & 0x000000ff), ((word & 0x0000ff00) >> 8),
                ((word & 0x00ff0000) >> 16), ((word & 0xff000000) >> 24)]


    #---------------------------------------------------------------
    # _print_state()
    #
    # Print the internal state.
    #---------------------------------------------------------------
    def _print_state(self):
        print(" 0: 0x%08x,  1: 0x%08x,  2: 0x%08x,  3: 0x%08x" %\
              (self.state[0], self.state[1], self.state[2], self.state[3]))
        print(" 4: 0x%08x,  5: 0x%08x,  6: 0x%08x,  7: 0x%08x" %\
              (self.state[4], self.state[5], self.state[6], self.state[7]))
        print(" 8: 0x%08x,  9: 0x%08x, 10: 0x%08x, 11: 0x%08x" %\
              (self.state[8], self.state[9], self.state[10], self.state[11]))
        print("12: 0x%08x, 13: 0x%08x, 14: 0x%08x, 15: 0x%08x" %\
              (self.state[12], self.state[13], self.state[14], self.state[15]))
        print("")


    #---------------------------------------------------------------
    # _print_x()
    #
    # Print the temporary state X.
    #---------------------------------------------------------------
    def _print_x(self):
        print(" 0: 0x%08x,  1: 0x%08x,  2: 0x%08x,  3: 0x%08x" %\
              (self.x[0], self.x[1], self.x[2], self.x[3]))
        print(" 4: 0x%08x,  5: 0x%08x,  6: 0x%08x,  7: 0x%08x" %\
              (self.x[4], self.x[5], self.x[6], self.x[7]))
        print(" 8: 0x%08x,  9: 0x%08x, 10: 0x%08x, 11: 0x%08x" %\
              (self.x[8], self.x[9], self.x[10], self.x[11]))
        print("12: 0x%08x, 13: 0x%08x, 14: 0x%08x, 15: 0x%08x" %\
              (self.x[12], self.x[13], self.x[14], self.x[15]))
        print("")


#-------------------------------------------------------------------
# print_block()
#
# Print a given block (list) of bytes ordered in
# rows of eight bytes.
#-------------------------------------------------------------------
def print_block(block):
    for i in range(0, len(block), 8):
        print("0x%02x 0x%02x 0x%02x 0x%02x 0x%02x 0x%02x 0x%02x 0x%02x" %\
              (block[i], block[i+1], block[i+2], block[i+3],
               block[i+4], block[i+5], block[i+6], block[i+7]))


#-------------------------------------------------------------------
# check_block()
#
# Compare the result block with the expected block and print
# if the result for the given test case was correct or not.
#-------------------------------------------------------------------
def check_block(result, expected, test_case):
    if result == expected:
        print("SUCCESS: %s was correct." % test_case)
    else:
        print("ERROR: %s was not correct." % test_case)
        print("Expected:")
        print_block(expected)
        print("")
        print("Result:")
        print_block(result)
    print("")


#-------------------------------------------------------------------
#-------------------------------------------------------------------
def long_tests():
    expected = [0xa3817f04ba25a8e66df67214c7550293, 0xda87c1d86b99af44347659119b22fc45,
                0x8177228da4a45dc7fca38bdef60affe4, 0x9c70b60c5267a94e5f33b6b02985ed51,
                0xf88164c12d9c8faf7d0f6e7c7bcd5579, 0x1368875980776f8854527a07690e9627,
                0x14eeca338b208613485ea0308fd7a15e, 0xa1f1ebbed8dbc153c0b84aa61ff08239,
                0x3b62a9ba6258f5610f83e264f31497b4, 0x264499060ad9baabc47f8b02bb6d71ed,
                0x00110dc378146956c95447d3f3d0fbba, 0x0151c568386b6677a2b4dc6f81e5dc18,
                0xd626b266905ef35882634df68532c125, 0x9869e247e9c08b10d029934fc4b952f7,
                0x31fcefac66d7de9c7ec7485fe4494902, 0x5493e99933b0a8117e08ec0f97cfc3d9,
                0x6ee2a4ca67b054bbfd3315bf85230577, 0x473d06e8738db89854c066c47ae47740,
                0xa426e5e423bf4885294da481feaef723, 0x78017731cf65fab074d5208952512eb1,
                0x9e25fc833f2290733e9344a5e83839eb, 0x568e495abe525a218a2214cd3e071d12,
                0x4a29b54552d16b9a469c10528eff0aae, 0xc9d184ddd5a9f5e0cf8ce29a9abf691c,
                0x2db479ae78bd50d8882a8a178a6132ad, 0x8ece5f042d5e447b5051b9eacb8d8f6f,
                0x9c0b53b4b3c307e87eaee08678141f66, 0xabf248af69a6eae4bfd3eb2f129eeb94,
                0x0664da1668574b88b935f3027358aef4, 0xaa4b9dc4bf337de90cd4fd3c467c6ab7,
                0xea5c7f471faf6bde2b1ad7d4686d2287, 0x2939b0183223fafc1723de4f52c43d35,
                0x7c3956ca5eeafc3e363e9d556546eb68, 0x77c6077146f01c32b6b69d5f4ea9ffcf,
                0x37a6986cb8847edf0925f0f1309b54de, 0xa705f0e69da9a8f907241a2e923c8cc8,
                0x3dc47d1f29c448461e9e76ed904f6711, 0x0d62bf01e6fc0e1a0d3c4751c5d3692b,
                0x8c03468bca7c669ee4fd5e084bbee7b5, 0x528a5bb93baf2c9c4473cce5d0d22bd9,
                0xdf6a301e95c95dad97ae0cc8c6913bd8, 0x801189902c857f39e73591285e70b6db,
                0xe617346ac9c231bb3650ae34ccca0c5b, 0x27d93437efb721aa401821dcec5adf89,
                0x89237d9ded9c5e78d8b1c9b166cc7342, 0x4a6d8091bf5e7d651189fa94a250b14c,
                0x0e33f96055e7ae893ffc0e3dcf492902, 0xe61c432b720b19d18ec8d84bdc63151b,
                0xf7e5aef549f782cf379055a608269b16, 0x438d030fd0b7a54fa837f2ad201a6403,
                0xa590d3ee4fbf04e3247e0d27f286423f, 0x5fe2c1a172fe93c4b15cd37caef9f538,
                0x2c97325cbd06b36eb2133dd08b3a017c, 0x92c814227a6bca949ff0659f002ad39e,
                0xdce850110bd8328cfbd50841d6911d87, 0x67f14984c7da791248e32bb5922583da,
                0x1938f2cf72d54ee97e94166fa91d2a36, 0x74481e9646ed49fe0f6224301604698e,
                0x57fca5de98a9d6d8006438d0583d8a1d, 0x9fecde1cefdc1cbed4763674d9575359,
                0xe3040c00eb28f15366ca73cbd872e740, 0x7697009a6a831dfecca91c5993670f7a,
                0x5853542321f567a005d547a4f04759bd, 0x5150d1772f50834a503e069a973fbd7c]


#-------------------------------------------------------------------
#-------------------------------------------------------------------
def short_tests():
    expected = [0x310e0edd47db6f72, 0xfd67dc93c539f874,
                0x5a4fa9d909806c0d, 0x2d7efbd796666785,
                0xb7877127e09427cf, 0x8da699cd64557618,
                0xcee3fe586e46c9cb, 0x37d1018bf50002ab,
                0x6224939a79f5f593, 0xb0e4a90bdf82009e,
                0xf3b9dd94c5bb5d7a, 0xa7ad6b22462fb3f4,
                0xfbe50e86bc8f1e75, 0x903d84c02756ea14,
                0xeef27a8e90ca23f7, 0xe545be4961ca29a1,
                0xdb9bc2577fcc2a3f, 0x9447be2cf5e99a69,
                0x9cd38d96f0b3c14b, 0xbd6179a71dc96dbb,
                0x98eea21af25cd6be, 0xc7673b2eb0cbf2d0,
                0x883ea3e395675393, 0xc8ce5ccd8c030ca8,
                0x94af49f6c650adb8, 0xeab8858ade92e1bc,
                0xf315bb5bb835d817, 0xadcf6b0763612e2f,
                0xa5c91da7acaa4dde, 0x716595876650a2a6,
                0x28ef495c53a387ad, 0x42c341d8fa92d832,
                0xce7cf2722f512771, 0xe37859f94623f3a7,
                0x381205bb1ab0e012, 0xae97a10fd434e015,
                0xb4a31508beff4d31, 0x81396229f0907902,
                0x4d0cf49ee5d4dcca, 0x5c73336a76d8bf9a,
                0xd0a704536ba93e0e, 0x925958fcd6420cad,
                0xa915c29bc8067318, 0x952b79f3bc0aa6d4,
                0xf21df2e41d4535f9, 0x87577519048f53a9,
                0x10a56cf5dfcd9adb, 0xeb75095ccd986cd0,
                0x51a9cb9ecba312e6, 0x96afadfc2ce666c7,
                0x72fe52975a4364ee, 0x5a1645b276d592a1,
                0xb274cb8ebf87870a, 0x6f9bb4203de7b381,
                0xeaecb2a30b22a87f, 0x9924a43cc1315724,
                0xbd838d3aafbf8db7, 0x0b1a2a3265d51aea,
                0x135079a3231ce660, 0x932b2846e4d70666,
                0xe1915f5cb1eca46c, 0xf325965ca16d629f,
                0x575ff28e60381be5, 0x724506eb4c328a95]


#-------------------------------------------------------------------
# main()
#
# If executed tests the SipHash class using known test vectors.
#-------------------------------------------------------------------
def main():
    print("Testing the SipHash Python model")
    print("--------------------------------")
    print
    print


#-------------------------------------------------------------------
# __name__
# Python thingy which allows the file to be run standalone as
# well as parsed from within a Python interpreter.
#-------------------------------------------------------------------
if __name__=="__main__":
    # Run the main function.
    sys.exit(main())

#=======================================================================
# EOF chacha.py
#=======================================================================
