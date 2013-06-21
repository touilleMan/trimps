#include "memory.hpp"

#include <cstdlib>

Memory::Memory(const uint32_t size)
	: memory_size_(size)
{
	this->a_memory_ = (uint32_t *)calloc(size, sizeof(uint32_t));
}

Memory::~Memory(void)
{

}

uint32_t Memory::__getitem__(const uint32_t address)
{
	if (address < this->memory_size_)
		return this->a_memory_[address];
	else
		return 0;
}

void Memory::__setitem__(const uint32_t address, const uint32_t item)
{
	if (address < this->memory_size_)
		this->a_memory_[address] = item;
}
