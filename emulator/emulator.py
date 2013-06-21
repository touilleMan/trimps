#! /usr/bin/env python

import struct
#import numpypy
import numpy

DEFAULT_START_ADDRESS = 0x0
DEFAULT_MEMORY_SIZE = 1024 * 1024
DEFAULT_MEMORY_BASE_ADDRESS = 0x0

class Memory():
    """Representation of the virtual memory
       physical RAM and I/O (through bindings on callbacks)
       are stored here
    """
    def __init__(self, size=DEFAULT_MEMORY_SIZE, ram_base_address=DEFAULT_MEMORY_BASE_ADDRESS):
        # Create the requested memory area
        if size % 4 != 0:
            raise Exception("Memory size must be 4 bytes alligned")
        self.ram = [0x00 for _ in xrange(size/4)]
        self.ram_base_address = ram_base_address
        self.ram_upper_end = size + ram_base_address
        self.bindings = []

    def set_word(self, address, item):
        print "set : {} = {}".format(hex(address), bin(item))
        if self.ram_base_address <= address and address + 4 < self.ram_upper_end:
            index = address - self.ram_base_address
            self.ram[index] = item & 0xF
            self.ram[index + 1] = (item>>8) & 0xF
            self.ram[index + 2] = (item>>16) & 0xF
            self.ram[index + 3] = (item>>24) & 0xF

    def get_word(self, address):
        # Make sure the address is not out of bounds
        if self.ram_base_address <= address and address + 4 < self.ram_upper_end:
            index = address - self.ram_base_address
            value = self.ram[index]
            value |= self.ram[index + 1] << 8
            value |= self.ram[index + 2] << 16
            value |= self.ram[index + 3] << 24
            return value
        else:
            return 0x00000000

    def __getitem__(self, address):
        # Check if the address is part of the RAM
        if self.ram_base_address <= address < self.ram_upper_end:
            index = address - self.ram_base_address
            return self.ram[index]
        else:
            # Default data if the memory address is out of bounds
            value = 0x00000000
            # Check if the address is among the IO bindings
            for b in [b for b in self.bindings if b['address'] == address]:
                value |= b['value'] & b['bitmask']
            return value

    def __setitem__(self, address, item):
        # Check if the address is part of the RAM
        if self.ram_base_address <= address < self.ram_upper_end:
            index = address - self.ram_base_address
            self.ram[index] = item
        else:
            # Else, check if the address is among the IO bindings
            for b in [b for b in self.bindings if b['address'] == address]:
                b['value'] = item & b['bitmask']

    def bind(self, address, bitmask=0xFF, callback=None):
        """Connect a memory region to a callback.
           This typically used handle IO
           bitmask : bits of interest
           callback(byte) ==> byte will receive the byte present in memory address
           and must return another byte which will be stored at this address
        """
        # If the binding address is part of the RAM, no need to create a 'value' key
        if self.ram_base_address <= address < self.ram_upper_end:
            binding = { 'address' : address, 'bitmask' : bitmask, 'callback' : callback }
        else:
            # Address outside of the RAM, it value must be stored inside the dictionnary
            binding = { 'address' : address, 'bitmask' : bitmask, 'callback' : callback , 'value' : 0x00 }
        self.bindings.append(binding)

    def synchronise(self):
        """Update the IO by callings their binding callbacks"""
        for b in self.bindings:
            if b.has_key('value'):
                # If the binding has it own value, use it
                b['value'] = b['callback'](b['value']) & b['bitmask']
            else:
                # Otherwise, the value is stored in the RAM
                # Convert the address into the index in the memory array
                index = b['address'] - self.ram_base_address
                bitmask = b['bitmask']
                new_value = b['callback'](self.ram[index] & bitmask)
                if new_value is not None:
                    self.ram[index] &= ~bitmask
                    self.ram[index] |= new_value & bitmask

class Cpu():
    """MIPS-1 CPU"""
    def __init__(self, memory=None):
        # PC is 4 bytes alligned, then we use instead a fake_pc divided by 4
        self.fake_pc = 0
        # MIPS has 31 general-purpose registers plus r0 (always 0 register)
        self.r = [numpy.int32(0) for _ in xrange(32)]
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

    def load(self, path, start_address=DEFAULT_START_ADDRESS):
        """Load MIPS binary and reset the CPU"""
        if start_address % 4 != 0:
            raise Exception("Cpu start_address must be 4 bytes alligned !")
        self.fake_pc = start_address / 4
        # Get the input binary as bit array
        with open(path, "rb") as fd:
            data = fd.read()
            if len(data) % 4 != 0:
                raise Exception('"{}" must be 4 bytes alligned !'
                    '(size : {} bytes)'.format(path, len(data)))
            # Now copy the raw bytes into an array of MIPS instructions
            self.program_size = len(data) / 4
            self.program = [ struct.unpack_from("i", data, i * 4)[0] for i in xrange(self.program_size)]

    def step(self, count=1):
        """Run the CPU count times (i.e. execute the count next instructions)"""
        for _ in xrange(count):
            # If no program is loaded or if pc is out of it bounds,
            # the cpu has no instruction to compute
            if self.program is None or self.fake_pc >= self.program_size:
                self.fake_pc += 1
                continue
            # Otherwise, it's time to fetch and execute the next instruction
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
        else:
            raise Exception("Address {} : bad funct in R instruction".format(self.fake_pc * 4))

    def __execute_I_BEQ(self, rs, rt, immed):
        # Branch is only on equal

        print "{} {}".format(self.r[rs], self.r[rt])
        if self.r[rs] != self.r[rt]:
            return
        if immed & 1 << 15 == 1:
            self.fake_pc = 0x3FFF << 16 | immed
        else:
            self.fake_pc += immed

    def __execute_I_LW(self, rs, rt, immed):
        if rt != 0:
            self.r[rt] = self.memory.get_word(self.r[rs] + immed)

    def __execute_I_SW(self, rs, rt, immed):
        self.memory.set_word(self.r[rs] + immed, self.r[rt])

    def __execute_I_ANDI(self, rs, rt, immed):
        if rt != 0:
            self.r[rt] = self.r[rs] & immed

    def __execute_I_ORI(self, rs, rt, immed):
        if rt != 0:
            self.r[rt] = self.r[rs] | immed

    def __execute_I_ADDI(self, rs, rt, immed):
        if rt != 0:
            self.r[rt] = self.r[rs] + immed

    def __execute_J_JUMP(self, addr):
        self.fake_pc = (self.fake_pc & (0x3F << 26)) | addr
