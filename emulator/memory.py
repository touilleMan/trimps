#! /usr/bin/env python

DEFAULT_MEMORY_SIZE = 1024 * 1024
DEFAULT_BASE_ADDRESS = 0

def signByte(byte):
    if (byte & 0x80):
        return byte - 0x100
    else:
        return byte

def unsignByte(byte):
    if (byte < 0):
        return byte + 0x100
    else:
        return byte    

def signWord(word):
    if (word & 0x80000000):
        return word - 0x100000000
    else:
        return word

def unsignWord(word):
    if (word < 0):
        return word + 0x100000000
    else:
        return word

class Memory():
    """Representation of the virtual memory
       physical RAM and I/O (through bindings on callbacks)
       are stored here
    """
    def __init__(self, size=DEFAULT_MEMORY_SIZE, base_address=DEFAULT_BASE_ADDRESS):
        # Create the requested memory area
        self.a_memory = [0x00 for _ in xrange(size)]
        self.base_address = base_address
        self.upper_end = size + base_address

    def __getitem__(self, address):
    	return self.get_ubyte(address)

    def get_ubyte(self, address):
    	"""Get the byte at address as a unsigned number"""
        # Check if the address is part of the RAM
        if self.base_address <= address < self.upper_end:
            return unsignByte(self.a_memory[address - self.base_address])
        else:
            return 0x00

    def get_sbyte(self, address):
    	"""Get the byte at address as a signed number"""
        # Check if the address is part of the RAM
        if self.base_address <= address < self.upper_end:
            return signByte(self.a_memory[address - self.base_address])
        else:
            return 0x00

    def get_uword(self, address):
    	"""Get the 32bits word starting at address as a unsigned number"""
        # Make sure the address is not out of bounds
        if self.base_address <= address and address + 4 < self.upper_end:
            index = address - self.base_address
            word = self.a_memory[index]
            word |= self.a_memory[index + 1] << 8
            word |= self.a_memory[index + 2] << 16
            word |= self.a_memory[index + 3] << 24
            return unsignWord(word)
        else:
            return 0x00000000

    def get_sword(self, address):
    	"""Get the 32bits word starting at address as a signed number"""
        # Make sure the address is not out of bounds
        if self.base_address <= address and address + 4 < self.upper_end:
            index = address - self.base_address
            word = self.a_memory[index]
            word |= self.a_memory[index + 1] << 8
            word |= self.a_memory[index + 2] << 16
            word |= self.a_memory[index + 3] << 24
            return signWord(word)
        else:
            return 0x00000000

    def __setitem__(self, address, item):
    	self.set_byte(address, item)

    def set_byte(self, address, byte):
    	"""Set the byte at address in memory"""
        # Check if the address is part of the a_memory
        if self.base_address <= address < self.upper_end:
            self.a_memory[address - self.base_address] = byte & 0xFF

    def set_word(self, address, word):
    	"""Set the 32bits word starting at address"""
        if self.base_address <= address and address + 4 < self.upper_end:
            index = address - self.base_address
            self.a_memory[index] = word & 0xFF
            self.a_memory[index + 1] = (word>>8) & 0xFF
            self.a_memory[index + 2] = (word>>16) & 0xFF
            self.a_memory[index + 3] = (word>>24) & 0xFF
