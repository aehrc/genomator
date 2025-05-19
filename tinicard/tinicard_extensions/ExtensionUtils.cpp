
#include "constants.h"

// gets the smallest number X >= a, such that X&b == b
_ULL_ get_smallest_after_mask(_ULL_ a, _ULL_ b) {
	_ULL_ bitwise_b_greater_than_a = b & ~(a), mask = 0;
	while(bitwise_b_greater_than_a){
		bitwise_b_greater_than_a >>= 1;
		mask = (mask << 1) | 1;
	}
	return (a & ~mask) | b;
}

// returns the number of 1's bits in the number
int get_set_bit_count(_ULL_ a) {
	int i=0;
	while (a) {
		a <<= 1;
		i++;
	}
	return i;
}

#include <stdlib.h>
#include <time.h>
#include <math.h>

int generate_random(float exception_space) {
  if (exception_space<0) {
    return (int)floor(((float)rand() / (float)RAND_MAX) * (fabs(exception_space)+1));
  } else {
    return exception_space;
  }
}
// a bad hash function
unsigned int scramble(unsigned int a) {
  unsigned int b = a*1666522483;
  a ^= b>>16;
  a ^= b<<16;
  b = b*a;
  return ((a^b)+a)&RAND_MAX;
}
int scramble_with_mod(float mod, unsigned int a) {
  return (int)(mod* scramble(a)) ;
}
