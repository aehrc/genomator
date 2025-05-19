#include "../ImplicationExtension.h"
#include "../SatSolver.h"
#include "../progressbar/progressbar.h"
#include "stdio.h"
#include <Python.h>
#include "constants.h"
#include "ExtensionUtils.h"


struct FastCompactMemoryImplicationExtensionArraySlice {
	_ULL_** array;
	int offset;
	int size;
};

class FastCompactMemoryImplicationExtension : public ImplicationExtension {
private:
	int* block_buffer;
	int loaded_block;
	int loaded_block_size;
	int* activities;

	FastCompactMemoryImplicationExtensionArraySlice* array_slices;
	int index_bits;
	_ULL_ index_mask;
	int index_bitshift;

	void resetMasks();

	int array_width_blocks;
	long array_length;
	long array_halflength;
	int array_width;

	_ULL_* masks;
	_ULL_** array;

	inline long wrap(long i, long halfsize)
		{return (i < halfsize ? i+1 : i-2*halfsize);}
	inline long unwrap(long i, long size)
		{return (i>=0 ? i-1 : i+size);}

public:

	FastCompactMemoryImplicationExtension(SatSolver* s, PyObject* binary_queries, int array_width, int index_bits, int not_silent);
	~FastCompactMemoryImplicationExtension();

	inline int getVariableNum() {
		return array_halflength;
	}
	inline int getBlockSize(int lit) {
		long oj = unwrap(-lit, array_length);
		if (loaded_block != oj)
			loadBlock(lit);
		return loaded_block_size;
	}
	inline int getBlockSizeNonZero(int lit) {
    return 1;
	}
	inline int* getBlock(int lit) {
		long oj = unwrap(-lit, array_length);
		if (loaded_block != oj)
			loadBlock(lit);
		return block_buffer;
	}
	inline void loadBlock(int lit) {
		long oj = unwrap(-lit, array_length);
		if (loaded_block == oj)
			return;
		loaded_block_size=0;
		loaded_block=oj;

		_ULL_* line = array[oj];
		_ULL_ line_index_mask = (line[0]>>index_bitshift) ^ index_mask;
		for (int k=0; k<array_width_blocks; k++)
			masks[k] ^= (masks[k] & (~line[k]));
		_ULL_ maskk0 = masks[0];
		for (_ULL_ i=line_index_mask; i<=index_mask; i=((i+1)|line_index_mask)) {
			if (array_slices[i].array!=NULL) {
				for (_ULL_* array_iterator = array_slices[i].array[0]; *array_iterator; array_iterator++) {
					if (( (*array_iterator)&maskk0)^maskk0) // first hurdle failed
						continue;
					int point_index = array_iterator - array_slices[i].array[0];
					long var2;
					for (int k=1; k<array_width_blocks; k++) {
						_ULL_ maskk = masks[k];
						if (( (array_slices[i].array[k][point_index])&maskk)^maskk)
							goto FastCompactMemoryImplicationExtension_next_iteration;
					}
					var2 = wrap(point_index+array_slices[i].offset,array_halflength);
					block_buffer[loaded_block_size++] = -var2;
					FastCompactMemoryImplicationExtension_next_iteration:;
				}
			}
		}
    block_buffer[loaded_block_size+1] = 0;
		resetMasks();
	}
	inline int getActivity(int lit) {
		return 1;//activities[unwrap(-lit, array_length)];
	}
};



FastCompactMemoryImplicationExtension::FastCompactMemoryImplicationExtension(SatSolver* s, PyObject* binary_queries, int original_array_width, int index_bits, int not_silent) : index_bits(index_bits) {
	if (not_silent) printf("parsing query arrays\n");
	if (!PyList_Check(binary_queries)) ERROR("first argument must be a list\n")
	array_length = PyList_Size(binary_queries);
	array_halflength = array_length>>1;
	if (array_length %2 != 0) ERROR("number of queries must be even")
	int original_array_width_blocks = ((original_array_width-1) / _ULLBITS_)+1;
	array_width_blocks = ((original_array_width-1) / (_ULLBITS_-1))+1;
	array_width = original_array_width + array_width_blocks-1; 
	index_mask = ((_ULLONE_<<index_bits)-1);
	index_bitshift = _ULLBITS_-index_bits;
	block_buffer = (int*)calloc(sizeof(int),array_length+1);
	activities = (int*)calloc(sizeof(int),array_length);
	loaded_block = -1;
	loaded_block_size = 0;

	if (not_silent) printf("extracting query arrays\n");
	array = (_ULL_**)calloc(sizeof(_ULL_*),array_length);
	_ULL_ *buffer = (_ULL_*)malloc(sizeof(_ULL_)*original_array_width_blocks);
	for (long i=0; i<array_length; i++) { // buffer input from python
		PyObject* query = PyList_GetItem(binary_queries, i);
		if (!PyLong_Check(query)) ERROR("could not parse the long argument, parse check fail\n")
		if (_PyLong_AsByteArray((PyLongObject *)query,(unsigned char*)buffer,sizeof(_ULL_)*original_array_width_blocks, 1, 0)!=0)
			ERROR("could not parse the long argument\n")

		// do bit count to get approximate activity (NOTE: Not exact)
		int bit_count = 0;
		for (int k=0; k<original_array_width_blocks; k++)
			bit_count += get_set_bit_count(buffer[k]);
		activities[unwrap(-wrap(i,array_halflength),array_length)] += (array_length >> (original_array_width - bit_count - 1)) + 1;
		
		// now load bit-reversed into array (with a guaranteed extra 1 bit)
		array[i] = (_ULL_*)calloc(sizeof(_ULL_),array_width_blocks);
		for (int k=0; k<array_width_blocks; k++)
			array[i][k]=_ULLONE_;
		for (int bit_j=0; bit_j<original_array_width; bit_j++) {
			_ULL_ buffer_bit_j = buffer[bit_j/_ULLBITS_] & (_ULLONE_<<(bit_j%_ULLBITS_) );
			if (buffer_bit_j) {
				int inverse_bit_j = original_array_width-1-bit_j;
				// reverse within _ULL_ aswell
				int shift = ((_ULLBITS_-1) - (inverse_bit_j%(_ULLBITS_-1)) );
				array[i][inverse_bit_j/ (_ULLBITS_-1)] |= (_ULLONE_<< shift);
			}
		}
	}
	free(buffer);

	if (not_silent) printf("allocating array slices\n");
	array_slices = (FastCompactMemoryImplicationExtensionArraySlice*)calloc( sizeof(FastCompactMemoryImplicationExtensionArraySlice), _ULLONE_<<index_bits);
	masks = (_ULL_*)calloc(sizeof(_ULL_),array_width_blocks);
	resetMasks();

	if (not_silent) printf("parsing into slices\n");
	// parse into slices depending on their index
	int block_width, index=0;
	for (_ULL_ i=0; i<(_ULLONE_<<index_bits); i++) {
		block_width = 0;
		while ((index+block_width<array_length)
		 && ((array[index+block_width][0] >> index_bitshift) == i))
			block_width++;
		if (block_width>0) {
			// populate array slice
			array_slices[i].offset = index;
			array_slices[i].size = block_width;
			array_slices[i].array = (_ULL_**)malloc(sizeof(_ULL_*)*array_width_blocks);
			for (int k=0; k<array_width_blocks; k++) {
				array_slices[i].array[k] = (_ULL_*)calloc(sizeof(_ULL_),block_width+1);//TEMINATING ZERO
				for (int j=0; j<block_width; j++)
					array_slices[i].array[k][j] = array[index+j][k];
			}
		}
		index += block_width;
	}
	if (index < array_length)
		ERROR("Index Searcher potentially not over sorted data")

	
	if (not_silent) printf("beginning unit generation loop\n");
	for (int oj=0; oj<array_length; oj++) {
		_ULL_* line = array[oj];
		int var1;
		for (int k=0; k<array_width_blocks; k++) {
			if (line[k]!=masks[k])
				goto FastCompactMemoryImplicationExtension_next_unit_check;
		}
		var1 = wrap(oj,array_halflength);
		s->addImplication(-var1,-var1); // unit clause add
		activities[unwrap(-var1,array_length)]++;
		FastCompactMemoryImplicationExtension_next_unit_check:;
	}

	if (not_silent) printf("completed implication generation loop\n");

	s->addImplicationExtension(this);
}

FastCompactMemoryImplicationExtension::~FastCompactMemoryImplicationExtension() {
	free(masks);
	for (long i=0; i<array_length; i++) free(array[i]);
	free(array);
	for (_ULL_ i=0; i<(_ULLONE_<<index_bits); i++)
		if (array_slices[i].array!=NULL) {
			for (int k=0; k<array_width_blocks; k++)
				free(array_slices[i].array[k]);
			free(array_slices[i].array);
		}
	free(array_slices);
	free(block_buffer);
	free(activities);
}


void FastCompactMemoryImplicationExtension::resetMasks() {
	for (int k=0; k<array_width_blocks; k++) {
		if ((k<array_width_blocks-1) || (array_width==(int)(array_width_blocks*_ULLBITS_))) {
			masks[k] = _ULLONES_;
		} else {
			masks[k] = ~((_ULLONE_<<(array_width_blocks*_ULLBITS_ - array_width))-1);
		}
	}
}




