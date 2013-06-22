#ifndef _MEMORY_HH_
#define _MEMORY_HH_

#include <mutex>

#define DEFAULT_MEMORY_SIZE (1024 * 1024)
#define DEFAULT_BASE_ADDRESS 0

class Memory {
public:
	Memory(const unsigned size=DEFAULT_MEMORY_SIZE, const unsigned base_address=DEFAULT_BASE_ADDRESS);
	virtual ~Memory(void);

	// Python operator overload
	int __getitem__(unsigned address);
	void __setitem__(unsigned address, const int item);

	// Unsigned getter
	unsigned int get_ubyte(const unsigned address);
	unsigned int get_uword(const unsigned address);

	// Signed getter
	int get_sbyte(const unsigned address);
	int get_sword(const unsigned address);

	// Generic setter
	void set_byte(const unsigned address, const int byte);
	void set_word(const unsigned address, const long word);

	const unsigned memory_size;
	const unsigned base_address;

private:
	std::mutex _mutex;
	char *_a_memory;
};

#endif // _MEMORY_HH_
