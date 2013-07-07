#include <cstdlib>

#include "memory.hpp"

Memory::Memory(const unsigned size, const unsigned base_address)
	: memory_size(size), base_address(base_address)
{
	this->_a_memory = (char *)calloc(size, sizeof(char));
}

Memory::~Memory(void)
{
	free(this->_a_memory);
}

int Memory::__getitem__(const unsigned address)
{
	return get_ubyte(address);
}

void Memory::__setitem__(const unsigned address, const int item)
{
	set_byte(address, item);
}

unsigned int Memory::get_ubyte(const unsigned address)
{
	return this->get_sbyte(address) & 0xFF;
}

unsigned int Memory::get_uword(const unsigned address)
{
	return (unsigned int)this->get_sword(address);
}

int Memory::get_sbyte(const unsigned address)
{
	this->_mutex.lock();

	int item = 0;
	if (this->base_address <= address &&
		address < this->memory_size) {
		item = this->_a_memory[address - this->base_address];
	}

	this->_mutex.unlock();
	return item;
}

int Memory::get_sword(const unsigned address)
{
	this->_mutex.lock();

	int item = 0;
	if (this->base_address <= address &&
		address + sizeof(int) < this->memory_size) {
		item = *(int*)(this->_a_memory + address - this->base_address);
	}

	this->_mutex.unlock();
	return item;
}

void Memory::set_byte(const unsigned address, const int byte)
{
	this->_mutex.lock();

	if (this->base_address <= address &&
		address < this->memory_size) {
		this->_a_memory[address - this->base_address] = (char)byte;
	}

	this->_mutex.unlock();
}

void Memory::set_word(const unsigned address, const long word)
{
	this->_mutex.lock();

	if (this->base_address <= address &&
		address + sizeof(int) < this->memory_size) {
		*(int*)(this->_a_memory + address - this->base_address) = word;
	}

	this->_mutex.unlock();
}
