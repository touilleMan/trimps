#! /usr/bin/env python

from memory import Memory
import struct

DEFAULT_PROGRAM_START = 0x0

def signExtImmed(immed):
    """Python int are not bounded unlike C int32,
       This function convert the given immed (16 bits long)
       into a valid python signed number
    """
    if (immed & 0x8000):
        return immed - 0x10000
    else:
        return immed

class Instruction():
    """Class representing a single instruction.
       To save runtime performances, a raw instruction (i.e. a 32bits word)
       can be "cooked" as this Instruction class.
       Then the instruction can be executed by calling Instruction.execute()
    """
    def __init__(self, cpu, instruction):
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

        self.cpu = cpu
        self.raw = instruction

        # Get the instruction type (R, I or J) from the opcode and execute it
        opcode = (instruction >> 26) & 0x3F
        if opcode == 0:
            # R instruction
            self.rs = (instruction >> 21) & 0x1F
            self.rt = (instruction >> 16) & 0x1F
            self.rd = (instruction >> 11) & 0x1F
            self.shamt = (instruction >> 6) & 0x1F
            self.funct = instruction & 0x3F
            self.execute = self.__execute_R

        elif opcode in self.OPCODES_I:
            self.rs = (instruction >> 21) & 0x1F
            self.rt = (instruction >> 16) & 0x1F
            self.immed = instruction & 0xFFFF
            self.execute = self.OPCODES_I[opcode]

        elif opcode in self.OPCODES_J:
            self.addr = instruction & 0x03FFFFFF
            self.execute = self.OPCODES_J[opcode]

        else:
            raise TypeError('bad opcode ({})'.format(hex(opcode)))

    def __index__(self):
        return self.raw

    # Functions to execute MIPS instructions

    def __execute_R(self):
        """Execute R type instruction"""
        # r[rd] must always be 0, nothing to do if it's the destination register
        if self.rd != 0:
            if self.funct == 0x24:  # AND
                self.cpu.r[self.rd] = self.cpu.r[self.rs] & self.cpu.r[self.rt]
            elif self.funct == 0x25:  # OR
                self.cpu.r[self.rd] = self.cpu.r[self.rs] | self.cpu.r[self.rt]
            elif self.funct == 0x27:  # XOR
                self.cpu.r[self.rd] = self.cpu.r[self.rs] ^ self.cpu.r[self.rt]
            elif self.funct == 0x20:  # ADD
                self.cpu.r[self.rd] = (self.cpu.r[self.rs] + self.cpu.r[self.rt]) & 0xFFFFFFFF
            elif self.funct == 0x22:  # SUB
                self.cpu.r[self.rd] = (self.cpu.r[self.rs] - self.cpu.r[self.rt]) & 0xFFFFFFFF
            elif self.funct == 0x00:  # SLL
                self.cpu.r[self.rd] = (self.cpu.r[self.rt] << self.shamt) & 0xFFFFFFFF
            elif self.funct == 0x02:  # SRL
                self.cpu.r[self.rd] = (self.cpu.r[self.rt] >> self.shamt) & 0xFFFFFFFF
            elif self.funct == 0x2a:  # SLT
                self.cpu.r[self.rd] = self.cpu.r[self.rs] < self.cpu.r[self.rt]
        # Finally update the program counter
        self.cpu.fake_pc += 1

    def __execute_I_BEQ(self):
        # Branch is only on equal
        if self.cpu.r[self.rs] == self.cpu.r[self.rt]:
           self.cpu.fake_pc += signExtImmed(self.immed)
        self.cpu.fake_pc += 1

    def __execute_I_LW(self):
        if self.rt != 0:
            self.cpu.r[self.rt] = self.cpu.memory.get_sword(self.cpu.r[self.rs] + signExtImmed(self.immed))
        self.cpu.fake_pc += 1

    def __execute_I_SW(self):
        self.cpu.memory.set_word(self.cpu.r[self.rs] + signExtImmed(self.immed), self.cpu.r[self.rt])
        self.cpu.fake_pc += 1

    def __execute_I_ANDI(self):
        if self.rt != 0:
            self.cpu.r[self.rt] = self.cpu.r[self.rs] & self.immed
        self.cpu.fake_pc += 1

    def __execute_I_ORI(self):
        if self.rt != 0:
            self.cpu.r[self.rt] = self.cpu.r[self.rs] | self.immed
        self.cpu.fake_pc += 1

    def __execute_I_ADDI(self):
        if self.rt != 0:
            self.cpu.r[self.rt] = (self.cpu.r[self.rs] + signExtImmed(self.immed)) & 0xFFFFFFFF
        self.cpu.fake_pc += 1

    def __execute_J_JUMP(self):
        self.cpu.fake_pc = (self.cpu.fake_pc & (0x3F << 26)) | self.addr
        # No need to update the program counter in a jump


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
            self.program_size = len(data) / 4
            # The program is stored as an array of Instruction objecs
            self.program = []
            for i in xrange(self.program_size):
                self.program.append(Instruction(self, struct.unpack_from("i", data, i * 4)[0]))
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
            self.program[self.fake_pc].execute()

    def execute(self, instruction):
        """Make the CPU execute the given MIPS instruction"""
        # First fetch the instruction
        i = Instruction(self, instruction)
        # Then execute it
        i.execute()
