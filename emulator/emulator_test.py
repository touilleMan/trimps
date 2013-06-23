#! /usr/bin/env python

import unittest
from emulator import Cpu, Memory


class Test_memory(unittest.TestCase):
    mem = 0

    def testSimple(self):
        memory = Memory(64)

        memory[0x0] = 0x11
        self.assertEqual(memory[0x0], 0x11)
        memory[0x0] = 0x0
        self.assertEqual(memory[0x0], 0x0)
        memory[0x1] = 0xFF
        self.assertEqual(memory[0x1], 0xFF)

        for i in xrange(0xFF):
            memory[0x2] = i
            self.assertEqual(memory[0x2], i)

        memory[63] = 0xFF
        self.assertEqual(memory[63], 0xFF)

        # out of bounds !
        memory[64] = 0xFF
        self.assertEqual(memory[64], 0x0)
        # Address must be > 0
        self.assertRaises(OverflowError, memory.__getitem__, -1)

    def testSigned(self):
        memory = Memory(64)

        memory.set_byte(0x0, -0x1)
        self.assertEqual(memory.get_sbyte(0x0), -0x1)
        self.assertEqual(memory.get_ubyte(0x0), 0xFF)
        memory.set_byte(0x0, 0xFF)
        self.assertEqual(memory.get_sbyte(0x0), -0x1)
        self.assertEqual(memory.get_ubyte(0x0), 0xFF)

        memory.set_word(0x0, 0xFFFFFFFF)
        self.assertEqual(memory.get_uword(0x0), 0xFFFFFFFF)
        self.assertEqual(memory.get_sword(0x0), -1)

    def testByte(self):
        memory = Memory(64)

        memory.set_byte(0x0, 0x7F)
        self.assertEqual(memory.get_ubyte(0x0), 0x7F)
        self.assertEqual(memory.get_sbyte(0x0), 0x7F)
        # __getitem__ can be used to get back a byte
        memory.set_byte(0x1, 0x7F)
        self.assertEqual(memory[0x1], 0x7F)
        # __getitem__ is unsigned
        memory.set_byte(0x1, 0xFF)
        self.assertEqual(memory[0x1], 0xFF)
        # __setitem__ can be used to set a byte
        memory[0x2] = 0x7F
        self.assertEqual(memory.get_ubyte(0x2), 0x7F)
        # Address must be > 0
        self.assertRaises(OverflowError, memory.get_ubyte, -1)
        self.assertRaises(OverflowError, memory.get_sbyte, -1)

    def testWord(self):
        memory = Memory(64)

        memory.set_word(0x11, 0x4242)
        self.assertEqual(memory.get_uword(0x11), 0x4242)
        self.assertEqual(memory.get_sword(0x11), 0x4242)

        memory.set_word(0x11, 0x01020304)
        self.assertEqual(memory[0x11], 0x4)
        self.assertEqual(memory[0x12], 0x3)
        self.assertEqual(memory[0x13], 0x2)
        self.assertEqual(memory[0x14], 0x1)
        # Out of bounds !
        memory.set_word(61, 0xFFFFFFFF)
        self.assertEqual(memory.get_uword(61), 0)
        self.assertEqual(memory.get_sword(61), 0)
        # Address must be > 0
        self.assertRaises(OverflowError, memory.get_uword, -1)
        self.assertRaises(OverflowError, memory.get_sword, -1)

def cmp_regs(regs1, regs2):
    for i in xrange(len(regs1)):
        if regs1[i] != regs2[i]:
            return False
    return True

class Test_execute(unittest.TestCase):


    def testGeneric(self):
        good_r = [ 0x00000000 for _ in xrange(32) ]
        cpu = Cpu()

        cpu.r[1] = 1
        cpu.execute(0b00000000001000000000100000100100)
        self.assertTrue(cmp_regs(cpu.r, good_r), 'AND $1, $1, $0 failed')

        cpu.r[1] = 1
        good_r[1] = 1
        cpu.execute(0b00000000001000000000100000100101)
        self.assertTrue(cmp_regs(cpu.r, good_r), 'OR $1, $1, $0 failed')

        cpu.r[1] = 42
        cpu.r[6] = 0xFFFFFFFF
        good_r[1] = 42
        good_r[6] = 0xFFFFFFFF
        good_r[3] = 42
        cpu.execute(0b00000000001001100001100000100100)
        self.assertTrue(cmp_regs(cpu.r, good_r), 'AND $3, $1, $6 failed')

cpu_execute_R = lambda cpu, rs, rt, rd, shamt, funct : \
                      cpu.execute( (0 & 0x3F) << 26 | \
                      (rs & 0x1F) << 21 |     \
                      (rt & 0x1F) << 16 |     \
                      (rd & 0x1F) << 11 |     \
                      (shamt & 0x1F) << 6 |   \
                      (funct & 0x3F) )

class Test__Cpu__execute_R(unittest.TestCase):


    def testR(self):
        good_r = [ 0x00000000 for _ in xrange(32) ]
        cpu = Cpu()

        cpu.r[1] = 11
        cpu.r[2] = 10
        good_r[1] = 11
        good_r[2] = 10
        good_r[3] = 10
        cpu_execute_R(cpu, 1, 2, 3, 0, 0x24)
        self.assertTrue(cmp_regs(cpu.r, good_r), 'AND $1, $2, $3 failed')

        good_r[3] = 0
        cpu_execute_R(cpu, 0, 2, 3, 0, 0x24)
        self.assertTrue(cmp_regs(cpu.r, good_r), 'AND $0, $2, $3 failed')

    def testOR(self):
        good_r = [ 0x00000000 for _ in xrange(32) ]
        cpu = Cpu()

        cpu.r[1] = 11
        cpu.r[2] = 10
        good_r[1] = 11
        good_r[2] = 10
        good_r[3] = 11
        cpu_execute_R(cpu, 1, 2, 3, 0, 0x25)
        self.assertTrue(cmp_regs(cpu.r, good_r), 'OR $1, $2, $3 failed')

        cpu.r[31] = 0xFFFFFFFF
        good_r[31] = 0xFFFFFFFF
        cpu_execute_R(cpu, 31, 31, 31, 0, 0x25)
        self.assertTrue(cmp_regs(cpu.r, good_r), 'OR $31, $31, $31 failed')

    def testSLL(self):
        good_r = [ 0x00000000 for _ in xrange(32) ]
        cpu = Cpu()

        cpu.r[1] = 0x00000001
        good_r[1] = 0x1 << 16
        cpu_execute_R(cpu, 0, 1, 1, 16, 0x00)
        self.assertTrue(cmp_regs(cpu.r, good_r), 'SLL $1, $1, 16 failed')

        good_r[3] = 0
        cpu_execute_R(cpu, 1, 3, 0, 32, 0x24)
        self.assertTrue(cmp_regs(cpu.r, good_r), 'SLL $1, $3, 32 failed')

    def testSLR(self):
        good_r = [ 0x00000000 for _ in xrange(32) ]
        cpu = Cpu()

        cpu.r[1] = 0x80000000
        good_r[1] = 0x1 << 15
        cpu_execute_R(cpu, 0, 1, 1, 16, 0x02)
        self.assertTrue(cmp_regs(cpu.r, good_r), 'SLR $1, $1, 16 failed')

        good_r[3] = 0
        cpu_execute_R(cpu, 1, 3, 0, 32, 0x24)
        self.assertTrue(cmp_regs(cpu.r, good_r), 'SLR $1, $3, 32 failed')

cpu_execute_I = lambda cpu, opcode, rs, rt, immed : \
                      cpu.execute( (opcode & 0x3F) << 26 | \
                      (rs & 0x1F) << 21 |     \
                      (rt & 0x1F) << 16 |     \
                      (immed & 0xFFFF) )

class Test__Cpu__execute_I(unittest.TestCase):

    def testBEQ(self):
        cpu = Cpu()
        cpu_execute_I(cpu, 0x04, 0, 0, 0x42)
        self.assertEqual(cpu.fake_pc, 0x42, 'BEQ $0, $0, 0x42 failed')

        cpu.fake_pc = 0
        cpu_execute_I(cpu, 0x04, 0, 0, 0x7FFF)
        self.assertEqual(cpu.fake_pc, 0x7FFF, 'BEQ $0, $0, 0x7FFF failed')

        cpu.fake_pc = 0
        cpu.r[1] = 1
        cpu_execute_I(cpu, 0x04, 0, 1, 0xFFFF)
        self.assertEqual(cpu.fake_pc, 0x0, 'BEQ $0, $1, 0xFFFF failed')


cpu_execute_J = lambda cpu, opcode, addr : \
                      cpu.execute( (opcode & 0x3F) << 26 | \
                      (addr & 0x03FFFFFF) )

class Test__Cpu__execute_J(unittest.TestCase):

    def testJump(self):
        cpu = Cpu()
        cpu_execute_J(cpu, 0x02, 0x4)
        self.assertEqual(cpu.fake_pc, 0x4, 'JUMP 0x4 failed')

        cpu_execute_J(cpu, 0x02, 0x03FFFFFF)
        self.assertEqual(cpu.fake_pc, 0x03FFFFFF, 'JUMP 0x03FFFFFF failed')
        cpu_execute_J(cpu, 0x02, 0x4)


class Test__Cpu__registers(unittest.TestCase):

    def testIncrease(self):
        cpu = Cpu()
        for _ in xrange(0x100000):
            cpu_execute_I(cpu, 0x08, 1, 1, 0x1000)
        self.assertEqual(cpu.r[1], 0x0, 'Register stored value is bigger than 32bits ! ({})'.format(hex(cpu.r[1])))

    def testDecrease(self):
        cpu = Cpu()
        for _ in xrange(0x100000):
            cpu_execute_I(cpu, 0x08, 1, 1, -0x1000)
        self.assertEqual(cpu.r[1], 0x0, 'Register stored value is bigger than 32bits ! ({})'.format(hex(cpu.r[1])))


if __name__ == '__main__':
    unittest.main()
