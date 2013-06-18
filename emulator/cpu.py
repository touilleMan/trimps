#! /usr/bin/env python

import struct
import threading
from datetime import datetime
import time

DEFAULT_START_ADDRESS = 0x0
# 12.5 MHz CPU
DEFAULT_FREQUENCY = 12500000
DEFAULT_MEMORY_SIZE = 1024 * 1024
DEFAULT_MEMORY_BASE_ADDRESS = 0x0

class Memory():
    """Representation of the virtual memory
       physical RAM and I/O (through bindings on callbacks)
       are stored here
    """
    def __init__(self, size=DEFAULT_MEMORY_SIZE, base_address=DEFAULT_MEMORY_BASE_ADDRESS):
        # Create the requested memory area
        if size % 4 != 0:
            raise Exception("Memory size must be 4 bytes alligned")
        self.mem_uint32 = [0x00 for _ in xrange(size/4)]
        self.base_address = base_address
        self.upper_end = size + base_address
        self.bindings = []

    def __getitem__(self, address):
        # Check if the address is not out of bound
        if self.base_address <= address < self.upper_end:
            index = (address - self.base_address) >> 2
            return self.mem_uint32[index]
        else:
            # Memory out of bound, return default 0ed memory
            return 0x00000000

    def __setitem__(self, address, item):
        # If address is out of bound, nothing to do
        if self.base_address <= address < self.upper_end:
            index = (address - self.base_address) >> 2
            self.mem_uint32[index] = item

    def bind(self, address, bitmask=0xFF, callback=None):
        """Connect a memory region to a callback.
           This typically used handle IO
           bitmask : bits of interest
           callback(byte) ==> byte will receive the byte present in memory address
           and must return another byte which will be stored at this address
        """
        self.bindings.append({ 'address' : address, 'bitmask' : bitmask, 'callback' : callback })

    def synchronise(self):
        """Execute the bindings to update their value to the real one stored in memory"""
        for b in self.bindings:
            # Make sure address is not outside memory bounds
            if self.base_address <= b['address'] < self.upper_end:
                # Convert the address into the index in the memory array
                index = (b['address'] - self.base_address)
                bitmask = b['bitmask']
                new_value = b['callback']((self.mem_uint32[index] >> 24) & bitmask)
                (self.mem_uint32[index] >> 24) &= ~bitmask
                (self.mem_uint32[index] >> 24) |= new_value & bitmask
            else:
                # Call with dummy stuff if we are outside
                b['callback'](0x00)


class Cpu():
    """MIPS-1 CPU"""
    def __init__(self, memory=None, frequency=DEFAULT_FREQUENCY):
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
        # stuff to make the cpu run in continuous
        self.thread = threading.Thread(None, self.__run)
        self.timeslice = 1 / frequency
        self.running = 0

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

    def __run(self):
        while self.running:
            t1 = datetime.now()
            self.step()
            dt = (datetime.now() - t1).total_seconds()
            if dt < self.timeslice:
                time.sleep(dt)

    def run(self):
        """Make the CPU run in continuous until self.stop() is called"""
        self.running = 1
        self.thread.start()

    def stop(self):
        """Stop the CPU execution"""
        self.running = 0
        self.thread.join()

    def step(self, count=1):
        """Run the CPU count times (i.e. execute the count next instructions)"""
        for i in xrange(count):
            self.__step()

    def __step(self):
        # If no program is loaded or if pc is out of it bounds,
        # the cpu has no instruction to compute
        if self.program is None or self.fake_pc >= self.program_size:
            self.fake_pc += 1
            return
        # Otherwise, it's time to execute the next instruction
        instruction = self.program[self.fake_pc]

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
            self.r[rd] = self.r[rs] + self.r[rt]
        elif funct == 0x22:  # SUB
            self.r[rd] = self.r[rs] - self.r[rt]
        elif funct == 0x00:  # SLL
            self.r[rd] = self.r[rt] << shamt
        elif funct == 0x02:  # SRL
            self.r[rd] = self.r[rt] >> shamt
        elif funct == 0x2a:  # SLT
            self.r[rd] = self.r[rs] < self.r[rt]
        else:
            raise Exception("Address {} : bad funct in R instruction".format(self.fake_pc * 4))

    def __execute_I_BEQ(self, rs, rt, immed):
        # Branch is only on equal
        if self.r[rs] != self.r[rt]:
            return
        if immed & 1 << 15 == 1:
            self.fake_pc = 0x3FFF << 16 | immed
        else:
            self.fake_pc += immed

    def __execute_I_LW(self, rs, rt, immed):
        if rt != 0:
            self.r[rt] = self.memory[self.r[rs] + immed]

    def __execute_I_SW(self, rs, rt, immed):
        self.memory[self.r[rs] + immed] = self.r[rt]

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
        self.fake_pc = (self.fake_pc & (0xF << 26)) + addr
