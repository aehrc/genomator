#include "IntPool.h"

IntPool::IntPool(int initial_size, int expansion_factor) {
	pools.clear();
	int* block = (int*)calloc(sizeof(int),initial_size);
	if (block==NULL) {
		fprintf(stderr,"cannot allocate memory\n");
		exit(1);
	}
	pools.push_back(block);
	current_block_size = initial_size;
	current_block_upto = 0;
	factor = expansion_factor;
}

int* IntPool::alloc(int size) {
	if (current_block_upto+size > current_block_size) { // need to allocate a new block
		if (size*factor > current_block_size)
			current_block_size = size*factor; // need to boost the size of the block
		current_block_upto=0;
		int* block = (int*)calloc(sizeof(int),current_block_size);
		if (block==NULL) {
			fprintf(stderr,"cannot allocate memory\n");
			exit(1);
		}
		pools.push_back(block);
	}
	int* ret = &(pools.back()[current_block_upto]);
	current_block_upto += size;
	return ret;
}

IntPool::~IntPool() {
	for (auto it = pools.begin(); it!=pools.end(); it++)
		free(*it);
}
