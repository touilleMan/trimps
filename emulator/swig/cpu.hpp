#ifndef _CPU_H_
#define _CPU_H_

class Memory;

class Cpu {
public:
	Cpu(Memory *memory=nullptr);
	virtual ~Cpu(void);

	void step(const unsigned count);

	int r[32] = { 0 };
	int fake_pc = 0;
	Memory *memory;

private:
};

#endif // _CPU_H_
