#ifndef _CPU_H_
#define _CPU_H_

class Memory;

class Cpu {
public:
	Cpu(Memory *memory=nullptr, const unsigned int start_address=0);
	virtual ~Cpu(void);

	void step(const unsigned int count=1);
	void execute(const unsigned int intruction);
	void load(const char *path);
	/// Get back the CPU's program counter
	unsigned int get_pc(void) { return this->_fake_pc * 4; }

	/// CPU registers
	int r[32] = { 0 };
	Memory *memory;
	unsigned int start_address;
	unsigned int *program;

private:
	// CPU program counter aligned on 4 bytes
	unsigned int _fake_pc = 0;
	// Keep track of allocated Memory object if any
	Memory *_inner_memory;
};

#endif // _CPU_H_
