#include <fstream>
#include <iostream>

#include "cpu.hpp"
#include "memory.hpp"


EmulatorException::EmulatorException(std::string &msg)
: _msg(msg)
{
}

const char* EmulatorException::what(void)
{
    return _msg.c_str();
}

Cpu::Cpu(Memory *memory, const unsigned int start_address)
{
    this->program_start = start_address;
    if (memory != nullptr) {
        // If a memory was given, use this one
        this->memory = memory;
    } else {
        // Otherwise, create a new memory object
        this->_inner_memory = new Memory();
        this->memory = this->_inner_memory;
    }
}

Cpu::~Cpu(void)
{
    if (this->_inner_memory != nullptr) {
        // If a memory object has been created, we have to destroy it now
        delete this->_inner_memory;
    }
}

void Cpu::step(const unsigned int count)
{
    for (unsigned int i = 0; i < count; ++i) {
        if (this->program_start <= this->fake_pc &&
            this->fake_pc < this->program_start + this->program_size) {
            this->execute(this->program[this->fake_pc - this->memory->base_address]);
    }
}
}

void Cpu::load(const char *path, const unsigned int program_start)
{
    unsigned int instruction;

    // Unload previous program
    this->program.clear();

    // Actually do the loading
    std::ifstream fs(path, std::fstream::in | std::fstream::binary);
    if (!fs) {
        std::string msg("Cannot open file : ");
        msg += path;
        throw EmulatorException(msg);
    }

    while (true) {
        fs.read((char*)&instruction, 4);
        if (fs.eof())
            break;
        this->program.push_back(instruction);
    }
    fs.close();
    // Finally update some variables
    this->program_start = program_start;
    this->program_size = this->program.size();

    // Reset program counter
    this->fake_pc = this->program_start;
}

static inline int signExtImmed(const unsigned int immed)
{
    if (immed & 0x8000)
        return 0xFFFF0000 | immed;
    else
        return immed;
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
        if (rd != 0) {
            switch (funct)
            {
            case 0x24:  // AND
            this->r[rd] = this->r[rs] & this->r[rt];
            break;
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
    }
    ++this->fake_pc;
    break;

        case 0x04: // I instruction, BEQ
        if (this->r[rs] == this->r[rt]) {
            if ((immed & (1 << 15)) == 1) {
                this->fake_pc = ((0x3FFF << 16) | immed) + 1;
            } else {
                this->fake_pc += immed + 1;
            }
        } else {
            ++this->fake_pc;
        }
        break;

        case 0x23: // I instruction, LW
        if (rt != 0)
            this->r[rt] = this->memory->get_sword(this->r[rs] + signExtImmed(immed));
        ++this->fake_pc;
        break;

        case 0x2b: // I instruction, SW
        this->memory->set_word(this->r[rs] + signExtImmed(immed), this->r[rt]);
        ++this->fake_pc;
        break;

        case 0x0c: // I instruction, ANDI
        if (rt != 0)
            this->r[rt] = this->r[rs] & immed;
        ++this->fake_pc;
        break;

        case 0x0d: // I instruction, ORI
        if (rt != 0)
            this->r[rt] = this->r[rs] | immed;
        ++this->fake_pc;
        break;

        case 0x08: // I instruction, ADDI
        if (rt != 0)
            this->r[rt] = this->r[rs] + signExtImmed(immed);
        ++this->fake_pc;
        break;

        case 0x02: // J instruction, JUMP
        this->fake_pc = (this->fake_pc & (0x3F << 26)) | addr;
        break;

        default:
        // Unknown opcode
        break;
    }
}
