#ifndef _MEMORY_HH_
#define _MEMORY_HH_

#include <cstdint>
#include <mutex>

#define DEFAULT_MEMORY_SIZE (1024 * 1024)

class Memory {
public:
	Memory(const uint32_t size=DEFAULT_MEMORY_SIZE);
	virtual ~Memory(void);

	uint32_t __getitem__(const uint32_t address);
	void __setitem__(const uint32_t address, const uint32_t item);

private:
	std::mutex mutex_;
	const uint32_t memory_size_;
	uint32_t *a_memory_;
};

#endif // _MEMORY_HH_
