#include <fstream>

#include "cpu.hpp"
#include "memory.hpp"

Cpu::Cpu(Memory *memory, const unsigned int start_address)
	: start_address(start_address), program(nullptr)
{
	if (memory != nullptr) {
		// If a memory was given, use this one
		this->memory = memory;
		this->_inner_memory = nullptr;
	} else {
		// Otherwise, create a new memory object
		this->_inner_memory = new Memory();
		this->memory = this->_inner_memory;
	}
}

Cpu::~Cpu(void)
{
	if (this->program != nullptr) {
		delete this->program;
	}
	if (this->_inner_memory != nullptr) {
		// If a memory object has been created, we have to destroy it now
		delete this->_inner_memory;
	}
}

void Cpu::step(const unsigned int count)
{
	for (unsigned int i = 0; i < count; ++i) {
		;
	}
}

void Cpu::load(const char *path)
{
	// Unload previous program if present
	if (this->program != nullptr)
		delete this->program;

	// Actually do the loading
	std::ifstream fs(path);

	// First thing to do is to make sure the file is made of 4bytes int
    fs.seekg(0, std::ifstream::end);
    auto size = fs.tellg();
    fs.seekg(0, std::ifstream::beg);

	if (size % 4)
		throw "Ma bite !" ;
	this->program = new unsigned int[size / 4];
	for (unsigned int i = 0; fs.good(); ++i) {
		fs >> this->program[i];
	}
	fs.close();

	// Reset program counter
	this->_fake_pc = this->start_address / 4;
}

void Cpu::execute(const unsigned int instruction)
{
	const unsigned char opcode = instruction >> 26;
    const unsigned char rs = (instruction >> 21) & 0x1F;
    const unsigned char rt = (instruction >> 16) & 0x1F;
    const unsigned char rd = (instruction >> 11) & 0x1F;
    const unsigned char shamt = (instruction >> 6) & 0x1F;
    const unsigned char funct = instruction & 0x3F;
    const unsigned int immed = instruction & 0xFFFF;
    const unsigned int addr = instruction & 0x03FFFFFF;

	switch (opcode)
	{
		case 0: // R instruction
		if (rd == 0)
			break;
		switch (funct)
		{
	        case 0x24:  // AND
	            this->r[rd] = this->r[rs] & this->r[rt];
	        case 0x25:  // OR
	            this->r[rd] = this->r[rs] | this->r[rt];
	            break;
	        case 0x27:  // XOR
	            this->r[rd] = this->r[rs] ^ this->r[rt];
	            break;
	        case 0x20:  // ADD
	            this->r[rd] = (this->r[rs] + this->r[rt]) & 0xFFFFFFFF;
	            break;
	        case 0x22:  // SUB
	            this->r[rd] = (this->r[rs] - this->r[rt]) & 0xFFFFFFFF;
	            break;
	        case 0x00:  // SLL
	            this->r[rd] = (this->r[rt] << shamt) & 0xFFFFFFFF;
	            break;
	        case 0x02:  // SRL
	            this->r[rd] = (this->r[rt] >> shamt) & 0xFFFFFFFF;
	            break;
	        case 0x2a:  // SLT
	            this->r[rd] = this->r[rs] < this->r[rt];
	            break;
	        default:
		        // Unknown funct
	            break;
        }
		break;

        case 0x04: // I instruction, BEQ
        if (this->r[rs] == this->r[rt]) {
	        if ((immed & (1 << 15)) == 1) {
	            this->_fake_pc = (0x3FFF << 16) | immed;
        	} else {
            	this->_fake_pc += immed;
        	}
		}
        break;

        case 0x23: // I instruction, LW
        if (rt != 0)
            this->r[rt] = this->memory->get_sword(this->r[rs] + immed);
        break;

        case 0x2b: // I instruction, SW
        this->memory->set_word(this->r[rs] + immed, this->r[rt]);
		break;

        case 0x0c: // I instruction, ANDI
        if (rt != 0)
            this->r[rt] = this->r[rs] & immed;
        break;

        case 0x0d: // I instruction, ORI
        if (rt != 0)
            this->r[rt] = this->r[rs] | immed;
        break;

        case 0x08: // I instruction, ADDI
        if (rt != 0)
            this->r[rt] = this->r[rs] + immed;
        break;

        case 0x02: // J instruction, JUMP
        this->_fake_pc = (this->_fake_pc & (0x3F << 26)) | addr;
        break;

        default:
        // Unknown opcode
        break;
	}
}
