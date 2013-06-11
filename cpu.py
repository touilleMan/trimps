class LoaderError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class Instruction():
	pass

class RInstruction(Instruction):
	def __init__(raw):
		# Split the input raw 32bit instruction
		cmd = raw[0:5]
		rs = raw[6:10]
		rt = raw[11:15]
		rd = raw[16:20]
		shamt = raw[21:26]
		funct = raw[27:32]

class IInstruction(Instruction):
	pass

class JInstruction(Instruction):
	pass



class Cpu():
	"""Emulate the embedded MIPS CPU"""

	def clock(self):
	"""Run the CPU to compute the next operation"""
		instruction = self.loader.nextInstruction()

