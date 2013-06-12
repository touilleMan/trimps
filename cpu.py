import struct

class LoaderError(Exception):
    def __init__(self, value):
        super(LoaderError, self).__init__()
        self.value = value
    def __str__(self):
        return repr(self.value)


class Program():
    """Handle de input MIPS binary"""
    instructions = []

    def load(self, path):
        # Get the input binary as bit array
        with open(path, "rb") as fd:
            data = fd.read()
            if len(data) % 4 != 0:
                raise LoaderError('"{}" must be a multiple of 4 bytes'
                    '(size : {} byts'.format(path, len(data)))
            for i in xrange(len(data) / 4):
                unpacked = struct.unpack(">i", data[i * 4 : i * 4 + 4])
                self.instructions.append(unpacked[0])

    def fetch(self, pc):
        """Return the requested instruction if it exists or 0x00000000"""
        if len(self.instructions) > (pc / 4):
            return self.instructions[pc / 4]
        else:
            return 0x00000000


class Memory():
    """RAM and I/O are stored here"""

    def __init__(self):
        self.mem = {}

    def __getitem__(self, address):
        # Check if the address point on something
        if self.mem[address] is None:
            return 0x0
        return self.mem[address]

    def __setitem__(self, address, item):
        self.mem[address] = item

class Cpu():
    """Emulate the embedded MIPS CPU"""

    def __init__(self):
        self.pc = 0
        # MIPS has 31 general-purpose registers plus r0 (always 0 register)
        self.r = [ 0x00000000 for _ in xrange(32) ]
        self.program = Program()
        self.memory = Memory()

    def step(self):
        """Run the CPU to compute the next operation"""
        instruction = self.program.fetch(self.pc)
        print "pc : " + str(self.pc),
        self.execute(instruction)
        # r0 is always == 0x0, reset it in case it has changed
        self.r[0] = 0x00000000
        self.pc += 4

    def execute(self, instruction):
        """Make the CPU run the given instruction"""

        OPCODES_R = {
        0 : self.execute_R
        }

        OPCODES_I = {
        0x04 : [ self.execute_I_BEQ, "BEQ" ],
        0x23 : [ self.execute_I_LW, "LW" ],
        0x2b : [ self.execute_I_SW, "SW" ],
        0x0c : [ self.execute_I_ANDI, "ANDI" ],
        0x0d : [ self.execute_I_ORI, "ORI" ],
        0x08 : [ self.execute_I_ADDI, "ADDI" ]
        }

        OPCODES_J = {
        0x02 : self.execute_J_JUMP
        }

        # Get the instruction type (R, I or J) from the opcode and execute it
        opcode = (instruction >> 26) & 0x3F
        if opcode in OPCODES_R:
            rs = (instruction >> 21) & 0x1F
            rt = (instruction >> 16) & 0x1F
            rd = (instruction >> 11) & 0x1F
            shamt = (instruction >> 6) & 0x1F
            funct = instruction & 0x3F
            print "R funct : " + hex(funct)
            OPCODES_R[opcode](rs, rt, rd, shamt, funct)

        elif opcode in OPCODES_I:
            rs = (instruction >> 21) & 0x1F
            rt = (instruction >> 16) & 0x1F
            immed = instruction & 0xFFFF
            print "I immed : " + hex(immed) + " " + OPCODES_I[opcode][1]
            OPCODES_I[opcode][0](rs, rt, immed)

        elif opcode in OPCODES_J:
            addr = instruction & 0x03FFFFFF
            print "J addr : " + hex(addr)
            OPCODES_J[opcode](addr)

        else:
            raise TypeError('instruction #{} ("{}") : Bad opcode'.format(self.pc / 4, bin(instruction)))

    def execute_R(self, rs, rt, rd, shamt, funct):
        """Execute R type instruction"""

        R_DIC = {
         0x24 : lambda rs_reg, rt_reg, shamt: rs_reg & rt_reg, # AND
         0x25 : lambda rs_reg, rt_reg, shamt: rs_reg | rt_reg, # OR
         0x27 : lambda rs_reg, rt_reg, shamt: rs_reg ^ rt_reg, # XOR
         0x20 : lambda rs_reg, rt_reg, shamt: rs_reg + rt_reg, # ADD
         0x22 : lambda rs_reg, rt_reg, shamt: rs_reg - rt_reg, # SUB
         0x00 : lambda rs_reg, rt_reg, shamt: rt_reg << shamt, # SLL
         0x02 : lambda rs_reg, rt_reg, shamt: rt_reg >> shamt, # SRL
         0x2a : lambda rs_reg, rt_reg, shamt: rs_reg < rt_reg  # SLT
        }

        # Execute the instruction and make sure no overflow occured
        if funct not in R_DIC:
            raise LoaderError("Instruction #{} : bad funct ({}) in R instruction".format(self.pc / 4, hex(funct)))
        res = R_DIC[funct](self.r[rs], self.r[rt], shamt)
        res %= 0x100000000
        # Store in output register
        self.r[rd] = res

    def execute_I_BEQ(self, rs, rt, immed):
        print "Branch ! " + str(rs == rt)
        if immed & 1 << 15 == 1:
            branch_addr = 0b1111 << 28
        else:
            branch_addr = 0x00000000
        branch_addr |= (immed << 2)
        if rs == rt:
            self.pc += branch_addr

    def execute_I_LW(self, rs, rt, immed):
        self.r[rt] = self.memory[self.r[rs] + immed]

    def execute_I_SW(self, rs, rt, immed):
        self.memory[self.r[rs] + immed] = self.r[rt]

    def execute_I_ANDI(self, rs, rt, immed):
        self.r[rt] = self.r[rs] & immed

    def execute_I_ORI(self, rs, rt, immed):
        self.r[rt] = self.r[rs] | immed

    def execute_I_ADDI(self, rs, rt, immed):
        self.r[rt] = self.r[rs] + immed

    def execute_J_JUMP(self, addr):
        print "Jump ! " + hex(addr)
        self.pc = (self.pc & (0xF << 28)) + addr * 4


if __name__ == '__main__':
    cpu = Cpu()
    cpu.program.load("../gopiler/a.out")
    while True:
        cpu.step()
