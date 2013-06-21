#ifndef _CPU_H_
#define _CPU_H_

class Cpu {
public:
	void Cpu(void);
	virtual void ~Cpu(void);

	uint32_t r[32] = { 0 };
	uint32_t fake_pc = 0;

private:

};

#endif // _CPU_H_
