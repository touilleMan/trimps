#include <Python.h>

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <stdio.h>
#include <time.h>
#include <pthread.h>

#define MEMORY_SIZE 1024 * 1024
// TODO : handle various memory start address
#define MIPS_START_ADDRESS 0x0

typedef enum {
	CPU_STOPPED = 0,
	CPU_RUNNING,
	CPU_STEP
} e_cpu_state;

// 12.5MHz cpu
#define CPU_TIMESLICE (1 / 12500000)

// Memory pool
static pthread_mutex_t memory_mutex = PTHREAD_MUTEX_INITIALIZER;
static uint32_t memory[MEMORY_SIZE];

// CPU specific ressources
static pthread_t cpu_thread;
static uint32_t cpu_op_counter = 0;
static pthread_mutex_t cpu_state_mutex = PTHREAD_MUTEX_INITIALIZER;
static uint8_t cpu_state = CPU_STOPPED;
static long cpu_nsec_slice = 0;

static uint32_t program_size = 0;
static uint32_t *program = NULL;

// MIPS architecture
static uint32_t r[32];
/*
 * Program is an array of uint32, but pc points on byte,
 * then we use a fake_pc (i.e. pc / 4) to save divisions
 */
static uint32_t fake_pc = 0;

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

PyObject *program_load(PyObject* self __attribute__((unused)), PyObject* args)
{
	char *path = NULL;
    if (!PyArg_ParseTuple(args, "s", &path))
        return NULL;

	pthread_mutex_lock(&cpu_state_mutex);
	cpu_state = CPU_STOPPED;

    // If another program was already loaded, we have to remove it
	if (program != NULL)
	{
		free(program);
		program = NULL;
	}

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
	pthread_mutex_unlock(&cpu_state_mutex);
    Py_RETURN_NONE;
}

PyObject *get_memory(PyObject* self __attribute__((unused)), PyObject* args)
{
	uint32_t address;
    if (!PyArg_ParseTuple(args, "i", &address))
        return NULL;

    // Address out of bounds, returns 0 data
    if (address < MEMORY_SIZE)
	{
		pthread_mutex_lock(&memory_mutex);
		const uint32_t value = memory[address];
		pthread_mutex_unlock(&memory_mutex);
	    return Py_BuildValue("i", value);
	}
   	else
	    return Py_BuildValue("i", 0);
}

PyObject *set_memory(PyObject* self __attribute__((unused)), PyObject* args)
{
	uint32_t address;
	uint32_t value;

    if (!PyArg_ParseTuple(args, "ii", &address, &value))
        return NULL;

    // In case of address out of bounds, do nothing
    if (address < MEMORY_SIZE)
    {
		pthread_mutex_lock(&memory_mutex);
   		memory[address] = value;
		pthread_mutex_unlock(&memory_mutex);
   	}

    Py_RETURN_NONE;
}

static void cpu_step(void)
{
	// If fake_pc points outside the program, we just
	// have to increment pc
	if (fake_pc > program_size - 1)
	{
		++fake_pc;
		goto end;
	}

	const uint32_t instruction = program[fake_pc];
	// Switch on opcode
	switch ((instruction >> 26) & 0x3F)
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
}

static void *cpu_main(void * p_data __attribute__((unused)))
{
	uint8_t running = 0;
	struct timespec time_sleep = {
		.tv_sec = 0,
		.tv_nsec = 0
	};
	const uint64_t NSECS_PER_CLOCK = 1000000000 / CLOCKS_PER_SEC;

	// cpu_state is volatile and can be changed by another function call
	while (1)
	{
		pthread_mutex_lock(&cpu_state_mutex);
		running = (cpu_state == CPU_RUNNING);
		pthread_mutex_unlock(&cpu_state_mutex);

		if (running)
		{
		    const clock_t clock_1 = clock();
			// Make the CPU run at the given frequency
			cpu_step();
			++cpu_op_counter;
			// Wait before the next instruction if needed
	    	time_sleep.tv_nsec = cpu_nsec_slice - (clock() - clock_1) * NSECS_PER_CLOCK;
	    	if (time_sleep.tv_nsec > 0)
	    		nanosleep(&time_sleep, NULL);
		}
	}
	return NULL;
}

static PyObject *cpu_run(PyObject* self __attribute__((unused)),
	PyObject* args __attribute__((unused)))
{
	uint32_t frequency = 0;
	// TODO : exception if frequency == 0
	// TODO : make sure frequency is not too big
	if (!PyArg_ParseTuple(args, "i", &frequency) || frequency == 0)
        return NULL;

	pthread_mutex_lock(&cpu_state_mutex);
	// Compute from the frequency the time slice for a single insruction
    cpu_nsec_slice = (CLOCKS_PER_SEC / frequency) * 1000000000;
	cpu_state = CPU_RUNNING;
	pthread_mutex_unlock(&cpu_state_mutex);

	Py_RETURN_NONE;
}

static PyObject *cpu_stop(PyObject* self __attribute__((unused)),
	PyObject* args __attribute__((unused)))
{
	pthread_mutex_lock(&cpu_state_mutex);
	cpu_state = CPU_STOPPED;
	pthread_mutex_unlock(&cpu_state_mutex);
	printf("done %u operations\n", cpu_op_counter);
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
	{
		pthread_mutex_lock(&memory_mutex);
		r[rt] = memory[addr];
		pthread_mutex_unlock(&memory_mutex);
	}
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
	{
		pthread_mutex_lock(&memory_mutex);
		memory[addr] = r[rt];
		pthread_mutex_unlock(&memory_mutex);
	}
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
     {"cpu_run", cpu_run, METH_VARARGS, "Start the CPU at the given ferquency"},
     {"cpu_stop", cpu_stop, METH_VARARGS, "Stop the execution of the CPU"},
     {"program_load", program_load, METH_VARARGS, "Load a MIPS binary program in memory"},
     {NULL, NULL, 0, NULL}
};

// Initialise the python module
PyMODINIT_FUNC initemulator(void)
{
    (void) Py_InitModule("emulator", EmulatorMethods);
    pthread_create(&cpu_thread, NULL, cpu_main, NULL);
}
