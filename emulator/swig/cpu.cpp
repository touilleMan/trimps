#include "cpu.hpp"
#include "memory.hpp"

Cpu::Cpu(Memory *memory)
{
	if (memory == nullptr)
		memory = new Memory();
	this->memory = memory;
}

Cpu::~Cpu(void)
{

}

void Cpu::step(const unsigned count)
{
	for (unsigned i = 0; i < count; ++i) {
		;
	}
}