#! /usr/bin/env python

import numpy

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
        self.mem_byte = numpy.array([numpy.byte(0x00) for _ in xrange(size)])
        self.mem_uint32 = self.mem_byte.view(numpy.uint32)
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
                new_value = b['callback'](self.mem_byte[index] & bitmask)
                self.mem_byte[index] &= ~bitmask
                self.mem_byte[index] |= new_value & bitmask
            else:
            	# Call with dummy stuff if we are outside
                b['callback'](0x00)
