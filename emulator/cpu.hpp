#ifndef _CPU_H_
#define _CPU_H_

#include <vector>
#include <string>
#include <exception>

#define DEFAULT_PROGRAM_SIZE 0x0

class EmulatorException : public std::exception {
public:
    EmulatorException(std::string &msg);
    const char* what(void);

private:
    std::string _msg;
};

class Memory;

class Cpu {
public:
    Cpu(Memory *memory=nullptr, const unsigned int start_address=0);
    virtual ~Cpu(void);

    void step(const unsigned int count=1);
    void execute(const unsigned int intruction);
    void load(const char *path, const unsigned int program_size=DEFAULT_PROGRAM_SIZE);
    /// Get back the CPU's program counter
    unsigned int get_pc(void) { return this->fake_pc * 4; }

    /// CPU registers
    std::vector<unsigned int> r = std::vector<unsigned int>(32);
    Memory *memory = nullptr;
    /// Starting address of the program
    unsigned int program_start = 0;
    /// Number of instructions in the program
    unsigned int program_size = 0;
    /// Array of the program's instructions
    std::vector<unsigned int> program = std::vector<unsigned int>();
    // CPU program counter aligned on 4 bytes
    unsigned int fake_pc = 0;

private:
    // Keep track of allocated Memory object if any
    Memory *_inner_memory = nullptr;
};

#endif // _CPU_H_
