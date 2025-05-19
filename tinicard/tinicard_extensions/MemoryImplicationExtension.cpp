#include "../ImplicationExtension.h"
#include "../SatSolver.h"
#include "../progressbar/progressbar.h"
#include "stdio.h"
#include <Python.h>
#include "constants.h"


class MemoryImplicationExtension : public ImplicationExtension {
private:
	inline long wrap(long i, long halfsize)
		{return (i < halfsize ? i+1 : i-2*halfsize);}

public:

	MemoryImplicationExtension(SatSolver* s, PyObject* binary_queries, int array_width, int not_silent) {
		if (not_silent) printf("parsing query arrays\n");
		if (!PyList_Check(binary_queries)) ERROR("first argument must be a list\n")
		long array_length = PyList_Size(binary_queries);
		if (array_length %2 != 0) ERROR("number of queries must be even")
		int array_width_blocks = ((array_width-1) / _ULLBITS_)+1;

		if (not_silent) printf("extracting query arrays\n");
		_ULL_ **array = (_ULL_**)calloc(sizeof(_ULL_*),array_length);
		if (array==NULL) ERROR("failed to construct")
		for (long i=0; i<array_length; i++) {
			PyObject* query = PyList_GetItem(binary_queries, i);
			if (!PyLong_Check(query)) ERROR("could not parse the long argument, parse check fail\n")
			array[i] = (_ULL_*)calloc(sizeof(_ULL_),array_width_blocks);
			if (_PyLong_AsByteArray((PyLongObject *)query,(unsigned char*)array[i],sizeof(_ULL_)*array_width_blocks, 1, 0)!=0)
				ERROR("could not parse the long argument\n")
		}

		if (array_length%2!=0) ERROR("Cannot create RandomAccessArrayExtension from odd array")
		long array_halflength = array_length>>1;

		if (not_silent) printf("allocating masks\n");
		_ULL_* masks = (_ULL_*)calloc(sizeof(_ULL_),array_width_blocks);
		for (int k=0; k<array_width_blocks; k++) {
			if ((k<array_width_blocks-1) || (array_width==(int)(array_width_blocks*_ULLBITS_))) {
				masks[k] = _ULLONES_;
			} else {
				masks[k] = (_ULLONE_<<(array_width-k*_ULLBITS_))-1;
			}
		}
		
		if (not_silent) printf("beginning implication generation loop\n");
		progressbar *bar = NULL;
		if (not_silent) bar = progressbar_new("Implications",array_length);

		long update_span = array_length/1000 + 1;
		for (long i=0, update_count=0; i<array_length; i++, update_count++) {
			long wrapped_i = wrap(i,array_halflength);
			long wrapped_j;
			for (long j=i; j<array_length; j++) {
				//if (i==j) continue; ///NOTE: this is fine
				for (int k=0; k<array_width_blocks; k++)
					if ((array[i][k] | array[j][k]) != masks[k])
						goto iterate_next_j;
				wrapped_j = wrap(j,array_halflength);
				if (wrapped_i==-wrapped_j)
					continue;
				s->addImplication(-wrapped_i,-wrapped_j);
				iterate_next_j:;
			}
			if (update_count==update_span) {
				if (bar!=NULL) progressbar_update(bar,bar->value+update_span);
				update_count=0;
			}
		}
		if (bar!=NULL) progressbar_finish(bar);

		free(masks);
		for (long i=0; i<array_length; i++) free(array[i]);
		free(array);
	}

	~MemoryImplicationExtension() {
	}

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
