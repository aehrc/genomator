#include "constants.h"

#ifndef _EXTENSIONUTILS
#define _EXTENSIONUTILS


_ULL_ get_smallest_after_mask(_ULL_ a, _ULL_ b);
int get_set_bit_count(_ULL_ a);
int generate_random(float exception_space);

unsigned int scramble(unsigned int a);
int scramble_with_mod(float mod, unsigned int a);

#endif
