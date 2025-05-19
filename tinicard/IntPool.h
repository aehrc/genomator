#ifndef _INTPOOL
#define _INTPOOL

#include <vector>
using namespace std;
#include "stdlib.h"
#include "stdio.h"

struct IntPool {
	vector<int*> pools;
	int current_block_size;
	int current_block_upto;
	int factor;
	IntPool(int initial_size, int expansion_factor);
	~IntPool();
	int* alloc(int size);
};

#endif
