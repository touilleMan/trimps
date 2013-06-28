#! /usr/bin/env python

from memory import Memory
import struct

DEFAULT_PROGRAM_START = 0x0

def signExtImmed(immed):
    if (immed & 0x8000):
        return immed - 0x10000
    else:
        return immed

class Cpu():
    """MIPS-1 CPU"""

    class CpuError(Exception):
        pass

    def __init__(self, memory=None):
        self.program_start = 0x0
        # PC is 4 bytes alligned, then we use instead a fake_pc divided by 4
        self.fake_pc = 0
        # MIPS has 31 general-purpose registers plus r0 (always 0 register)
        self.r = [0x00000000 for _ in xrange(32)]
        # If no memory was given, it's time to create one
        if memory is None:
            self.memory = Memory()
        else:
            self.memory = memory
        # No program loaded so far
        self.program_size = 0
        self.program = None
        self.OPCODES_I = {
        0x04 : self.__execute_I_BEQ,
        0x23 : self.__execute_I_LW,
        0x2b : self.__execute_I_SW,
        0x0c : self.__execute_I_ANDI,
        0x0d : self.__execute_I_ORI,
        0x08 : self.__execute_I_ADDI
        }

        self.OPCODES_J = {
        0x02 : self.__execute_J_JUMP
        }

    def __str__(self):
        string = 'Dump cpu registers :\n'
        string += 'pc : {}\n'.format(self.fake_pc * 4)
        for i in xrange(len(self.r)):
            string += '\tr{} : 0b{}\n'.format(i, bin(self.r[i]))
        return string

    def load(self, path, program_start=DEFAULT_PROGRAM_START):
        """Load MIPS binary and reset the CPU"""
        if program_start % 4 != 0:
            raise Exception("Cpu program_start must be 4 bytes alligned !")
        self.program_start = program_start
        # Get the input binary as bit array
        with open(path, "rb") as fd:
            data = fd.read()
            if len(data) % 4 != 0:
                raise Exception('"{}" must be 4 bytes alligned !'
                    '(size : {} bytes)'.format(path, len(data)))
            # Now copy the raw bytes into an array of MIPS instructions
            self.program_size = len(data) / 4
            self.program = [ struct.unpack_from("i", data, i * 4)[0] for i in xrange(self.program_size)]
        # Finally, set the PC to be ready to start the program
        self.set_pc(self.program_start)

    def set_pc(self, address):
        """Set the PC"""
        self.fake_pc = (address - self.program_start) >> 2

    def get_pc(self):
        """Get the current value of the PC"""
        return (self.fake_pc << 2) + self.program_start

    def step(self, count=1):
        """Run the CPU count times (i.e. execute the count next instructions)"""
        if self.program is None:
            raise CpuError("No program loaded !")

        for _ in xrange(count):
            # Fetch and execute the next instruction
            self.execute(self.program[self.fake_pc])

    def execute(self, instruction):
        """Make the CPU execute the given MIPS instruction"""
        # Get the instruction type (R, I or J) from the opcode and execute it
        opcode = (instruction >> 26) & 0x3F
        if opcode == 0:
            # R instruction
            rs = (instruction >> 21) & 0x1F
            rt = (instruction >> 16) & 0x1F
            rd = (instruction >> 11) & 0x1F
            shamt = (instruction >> 6) & 0x1F
            funct = instruction & 0x3F
            # r[rd] must always be 0, nothing to do if it's the destination register
            if rd != 0:
                self.__execute_R(rs, rt, rd, shamt, funct)
            # Finally update the program counter
            self.fake_pc += 1

        elif opcode in self.OPCODES_I:
            rs = (instruction >> 21) & 0x1F
            rt = (instruction >> 16) & 0x1F
            immed = instruction & 0xFFFF
            self.OPCODES_I[opcode](rs, rt, immed)
            # Finally update the program counter
            self.fake_pc += 1

        elif opcode in self.OPCODES_J:
            addr = instruction & 0x03FFFFFF
            self.OPCODES_J[opcode](addr)
            # No need to update the program counter in a jump

        else:
            raise TypeError('Address {} : bad opcode'.format(hex(self.fake_pc * 4)))

    # Functions to execute MIPS instructions

    def __execute_R(self, rs, rt, rd, shamt, funct):
        """Execute R type instruction"""
        if funct == 0x24:  # AND
            self.r[rd] = self.r[rs] & self.r[rt]
        elif funct == 0x25:  # OR
            self.r[rd] = self.r[rs] | self.r[rt]
        elif funct == 0x27:  # XOR
            self.r[rd] = self.r[rs] ^ self.r[rt]
        elif funct == 0x20:  # ADD
            self.r[rd] = (self.r[rs] + self.r[rt]) & 0xFFFFFFFF
        elif funct == 0x22:  # SUB
            self.r[rd] = (self.r[rs] - self.r[rt]) & 0xFFFFFFFF
        elif funct == 0x00:  # SLL
            self.r[rd] = (self.r[rt] << shamt) & 0xFFFFFFFF
        elif funct == 0x02:  # SRL
            self.r[rd] = (self.r[rt] >> shamt) & 0xFFFFFFFF
        elif funct == 0x2a:  # SLT
            self.r[rd] = self.r[rs] < self.r[rt]

    def __execute_I_BEQ(self, rs, rt, immed):
        # Branch is only on equal
        if self.r[rs] != self.r[rt]:
            return
        self.fake_pc += signExtImmed(immed)

    def __execute_I_LW(self, rs, rt, immed):
        if rt != 0:
            self.r[rt] = self.memory.get_sword(self.r[rs] + signExtImmed(immed))

    def __execute_I_SW(self, rs, rt, immed):
        self.memory.set_word(self.r[rs] + signExtImmed(immed), self.r[rt])

    def __execute_I_ANDI(self, rs, rt, immed):
        if rt != 0:
            self.r[rt] = self.r[rs] & immed

    def __execute_I_ORI(self, rs, rt, immed):
        if rt != 0:
            self.r[rt] = self.r[rs] | immed

    def __execute_I_ADDI(self, rs, rt, immed):
        if rt != 0:
            self.r[rt] = (self.r[rs] + signExtImmed(immed)) & 0xFFFFFFFF

    def __execute_J_JUMP(self, addr):
        self.fake_pc = (self.fake_pc & (0x3F << 26)) | addr
