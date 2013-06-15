#include <Python.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>

#define MEMORY_SIZE 1024 * 1024
#define MIPS_START_ADDRESS 0x0

// MIPS architecture
static uint32_t memory[MEMORY_SIZE];
static uint32_t program_size = 0;
static uint32_t *program = NULL;
/*
 * Program is an array of uint32, but pc points on byte,
 * then we use a fake_pc (i.e. pc / 4) to save divisions
 */
static uint32_t fake_pc = 0;
static uint32_t r[32];

// MIPS instructions
static void instruction_R(uint32_t instruction);
static void instruction_J_JUMP(uint32_t instruction);
static void instruction_I_BEQ(uint32_t instruction);
static void instruction_I_LW(uint32_t instruction);
static void instruction_I_SW(uint32_t instruction);
static void instruction_I_ANDI(uint32_t instruction);
static void instruction_I_ORI(uint32_t instruction);
static void instruction_I_ADDI(uint32_t instruction);
static void instruction_J_JUMP(uint32_t instruction);

static PyObject *program_load(PyObject* self __attribute__((unused)), PyObject* args)
{
	char *path = NULL;
    if (!PyArg_ParseTuple(args, "s", &path))
        return NULL;

    // If another program was already loaded, we have to remove it
	if (program != NULL)
		free(program);

	// Load the new program in a buffer
    int fd = open(path, O_RDONLY);
    if (fd == -1)
    	return NULL;
	struct stat st;
	stat(path, &st);
	program_size = st.st_size / 4;
    program = malloc(st.st_size);
    read(fd, program, st.st_size);
    close(fd);

	// Finally, reset the fake_pc to the beginning of the code
	fake_pc = MIPS_START_ADDRESS;

    Py_RETURN_NONE;
}

static PyObject *get_memory(PyObject* self __attribute__((unused)), PyObject* args)
{
	uint32_t address;

    if (!PyArg_ParseTuple(args, "i", &address))
        return NULL;

    // Address out of bounds, returns 0 data
    if (address < MEMORY_SIZE)
	    return Py_BuildValue("i", memory[address]);
   	else
	    return Py_BuildValue("i", 0);
}

static PyObject *set_memory(PyObject* self __attribute__((unused)), PyObject* args)
{
	uint32_t address;
	uint32_t value;

    if (!PyArg_ParseTuple(args, "ii", &address, &value))
        return NULL;

    // In case of address out of bounds, do nothing
    if (address < MEMORY_SIZE)
   		memory[address] = value;

    Py_RETURN_NONE;
}

static PyObject *cpu_step(PyObject* self __attribute__((unused)),
	PyObject* args __attribute__((unused)))
{
	// If fake_pc points outside the program, we just
	// have to increment pc
	if (fake_pc > program_size - 1)
	{
		++fake_pc;
		goto end;
	}

	const uint32_t instruction = program[fake_pc];
	const uint32_t opcode = (instruction >> 26) & 0x3F;

	switch (opcode)
	{
	case 0x00:
		instruction_R(instruction);
		break;

	case 0x02:
		instruction_J_JUMP(instruction);
		break;

	case 0x04:
		instruction_I_BEQ(instruction);
		break;

	case 0x23:
		instruction_I_LW(instruction);
		break;

	case 0x2B:
		instruction_I_SW(instruction);
		break;

	case 0x0C:
		instruction_I_ANDI(instruction);
		break;

	case 0x0D:
		instruction_I_ORI(instruction);
		break;

	case 0x08:
		instruction_I_ADDI(instruction);
		break;

	default:
	// Unknown instruction...
	break;
	}

end:
	++fake_pc;

    Py_RETURN_NONE;
}

static void instruction_R(const uint32_t instruction)
{
	const uint32_t rs = (instruction >> 21) & 0x1F;
	const uint32_t rt = (instruction >> 16) & 0x1F;
	const uint32_t rd = (instruction >> 11) & 0x1F;
	const uint32_t shamt = (instruction >> 6) & 0x1F;
	const uint32_t funct = instruction & 0x3;

	switch (funct)
	{
		case 0x24:
		// AND instruction
		r[rd] = r[rs] & r[rt];
		break;

		case 0x25:
		// OR instruction
		r[rd] = r[rs] | r[rt];
		break;

		case 0x27:
		// XOR instruction
		r[rd] = r[rs] ^ r[rt];
		break;

		case 0x20:
		// ADD instruction
		r[rd] = r[rs] + r[rt];
		break;

		case 0x22:
		// SUB instruction
		r[rd] = r[rs] - r[rt];
		break;

		case 0x00:
		// SLL instruction
		r[rd] = r[rs] << shamt;
		break;

		case 0x02:
		// SRL instruction
		r[rd] = r[rs] >> shamt;
		break;

		case 0x2a:
		// SLT instruction
		r[rd] = r[rs] < r[rt];
		break;

		default:
		// Unknown instruction...
		break;
     }
}

static void instruction_I_BEQ(const uint32_t instruction)
{
	const uint32_t rs = (instruction >> 21) & 0x1F;
	const uint32_t rt = (instruction >> 16) & 0x1F;
	const uint32_t immed = instruction & 0xFFFF;

    if (rs != rt)
    	return;

	if ((immed & (1 << 15)) == 1)
	    fake_pc += ((0x3FFF << 16) | immed);
	else
	    fake_pc += immed;
}

static void instruction_I_LW(const uint32_t instruction)
{
	const uint32_t rs = (instruction >> 21) & 0x1F;
	const uint32_t rt = (instruction >> 16) & 0x1F;
	const uint32_t immed = instruction & 0xFFFF;

	const uint32_t addr = r[rs] + immed;
	if (addr < MEMORY_SIZE)
		r[rt] = memory[addr];
	else
		r[rt] = 0;
}

static void instruction_I_SW(const uint32_t instruction)
{
	const uint32_t rs = (instruction >> 21) & 0x1F;
	const uint32_t rt = (instruction >> 16) & 0x1F;
	const uint32_t immed = instruction & 0xFFFF;

	const uint32_t addr = r[rs] + immed;
	if (addr < MEMORY_SIZE)
		memory[addr] = r[rt];
}

static void instruction_I_ANDI(const uint32_t instruction)
{
	const uint32_t rs = (instruction >> 21) & 0x1F;
	const uint32_t rt = (instruction >> 16) & 0x1F;
	const uint32_t immed = instruction & 0xFFFF;

	r[rt] = r[rs] & immed;
}

static void instruction_I_ORI(const uint32_t instruction)
{
	const uint32_t rs = (instruction >> 21) & 0x1F;
	const uint32_t rt = (instruction >> 16) & 0x1F;
	const uint32_t immed = instruction & 0xFFFF;

	r[rt] = r[rs]  | immed;
}

static void instruction_I_ADDI(const uint32_t instruction)
{
	const uint32_t rs = (instruction >> 21) & 0x1F;
	const uint32_t rt = (instruction >> 16) & 0x1F;
	const uint32_t immed = instruction & 0xFFFF;

	r[rt] = r[rs] + immed;
}

static void instruction_J_JUMP(const uint32_t instruction)
{
	const uint32_t addr = instruction & 0x03FFFFFF;

	fake_pc = (fake_pc & (0xF << 26)) + addr;
}


static PyMethodDef EmulatorMethods[] =
{
     {"get_memory", get_memory, METH_VARARGS, "Get the uint32 at the given address"},
     {"set_memory", set_memory, METH_VARARGS, "Set an uint32 at the given address"},
     {"cpu_step", cpu_step, METH_VARARGS, "Make the CPU execute the next operation"},
     {"program_load", program_load, METH_VARARGS, "Load a MIPS binary program in memory"},
     {NULL, NULL, 0, NULL}
};

// Initialise the python module
PyMODINIT_FUNC initemulator(void)
{
     (void) Py_InitModule("emulator", EmulatorMethods);
}
