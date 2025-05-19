#include "../ImplicationExtension.h"
#include "../SatSolver.h"
#include "../progressbar/progressbar.h"
#include "stdio.h"
#include <Python.h>
#include "constants.h"
#include "ExtensionUtils.h"

struct FastMemoryImplicationExtensionArraySlice {
	_ULL_** array;
	int offset;
	int size;
};

class FastMemoryImplicationExtension : public ImplicationExtension {
private:

	FastMemoryImplicationExtensionArraySlice* array_slices;
	int index_bits;
	_ULL_ index_mask;
	int index_bitshift;

	void resetMasks();

	int array_width_blocks;
	long array_length;
	long array_halflength;
	int array_width;

	_ULL_* masks;

	inline long wrap(long i, long halfsize)
		{return (i < halfsize ? i+1 : i-2*halfsize);}

public:

	FastMemoryImplicationExtension(SatSolver* s, PyObject* binary_queries, int array_width, int index_bits, int not_silent);
	~FastMemoryImplicationExtension();

	inline int getVariableNum() {
		return 0;
	}
	inline int getBlockSize(int lit) {
		return 0;
	}
	inline int getBlockSizeNonZero(int lit) {
		return 0;
	}
	inline int* getBlock(int lit) {
		return NULL;
	}
	inline int getActivity(int lit) {
		return 0;
	}
};



FastMemoryImplicationExtension::FastMemoryImplicationExtension(SatSolver* s, PyObject* binary_queries, int original_array_width, int index_bits, int not_silent) : index_bits(index_bits) {
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

	if (not_silent) printf("extracting query arrays\n");
	_ULL_ **array = (_ULL_**)calloc(sizeof(_ULL_*),array_length);
	_ULL_ *buffer = (_ULL_*)malloc(sizeof(_ULL_)*original_array_width_blocks);
	for (long i=0; i<array_length; i++) { // buffer input from python
		PyObject* query = PyList_GetItem(binary_queries, i);
		if (!PyLong_Check(query)) ERROR("could not parse the long argument, parse check fail\n")
		if (_PyLong_AsByteArray((PyLongObject *)query,(unsigned char*)buffer,sizeof(_ULL_)*original_array_width_blocks, 1, 0)!=0)
			ERROR("could not parse the long argument\n")
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
	array_slices = (FastMemoryImplicationExtensionArraySlice*)calloc( sizeof(FastMemoryImplicationExtensionArraySlice), _ULLONE_<<index_bits);
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


	
	if (not_silent) printf("beginning implication generation loop\n");
	progressbar *bar = NULL;
	if (not_silent) bar = progressbar_new("Implications",array_length);

	long update_span = array_length/1000 + 1;
	//for (int oj=0, update_count=0; oj<=array_halflength; oj++, update_count++) {
	for (int oj=0, update_count=0; oj<array_length; oj++, update_count++) {
		_ULL_* line = array[oj];
		_ULL_ line_index_mask = (line[0]>>index_bitshift) ^ index_mask;
		for (int k=0; k<array_width_blocks; k++)
			masks[k] ^= (masks[k] & line[k]);
		_ULL_ maskk0 = masks[0];
		_ULL_ start = get_smallest_after_mask(line[0]>>index_bitshift, line_index_mask);
		for (_ULL_ i=start; i<=index_mask; i=((i+1)|line_index_mask)) {
			if (array_slices[i].array!=NULL) {
				for (_ULL_* array = array_slices[i].array[0]; *array; array++) {
					if (( (*array)&maskk0)^maskk0) // first hurdle failed
						continue;
					int point_index = array - array_slices[i].array[0];
					long var1,var2;
					for (int k=1; k<array_width_blocks; k++) {
						_ULL_ maskk = masks[k];
						if (( (array_slices[i].array[k][point_index])&maskk)^maskk)
							goto FastMemoryImplicationExtension_next_iteration;
					}
					var1 = wrap(oj,array_halflength);
					var2 = wrap(point_index+array_slices[i].offset,array_halflength);
					if (var1==-var2)
						continue;
					if (point_index+array_slices[i].offset>=oj)
						s->addImplication(-var1,-var2);
					FastMemoryImplicationExtension_next_iteration:;
				}
			}
		}
		resetMasks();
		if (update_count==update_span) {
			if (bar!=NULL) progressbar_update(bar,bar->value+update_span);
			update_count=0;
		}
	}
	if (bar!=NULL) progressbar_finish(bar);

	if (not_silent) printf("completed implication generation loop\n");
	free(masks);
	for (long i=0; i<array_length; i++) free(array[i]);
	free(array);
}

FastMemoryImplicationExtension::~FastMemoryImplicationExtension() {
	for (_ULL_ i=0; i<(_ULLONE_<<index_bits); i++)
		if (array_slices[i].array!=NULL) {
			for (int k=0; k<array_width_blocks; k++)
				free(array_slices[i].array[k]);
			free(array_slices[i].array);
		}
	free(array_slices);
}


void FastMemoryImplicationExtension::resetMasks() {
	for (int k=0; k<array_width_blocks; k++) {
		if ((k<array_width_blocks-1) || (array_width==(int)(array_width_blocks*_ULLBITS_))) {
			masks[k] = _ULLONES_;
		} else {
			masks[k] = ~((_ULLONE_<<(array_width_blocks*_ULLBITS_ - array_width))-1);
		}
	}
}




