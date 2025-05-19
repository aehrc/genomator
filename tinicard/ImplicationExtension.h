#ifndef _SAT_SOLVER_IMPLICATION_EXTENSION
#define _SAT_SOLVER_IMPLICATION_EXTENSION

class ImplicationExtension {
  public:
  virtual int getVariableNum()=0;
  virtual int getBlockSize(int lit)=0;
  virtual int getBlockSizeNonZero(int lit)=0;
  virtual int* getBlock(int lit)=0;
  virtual int getActivity(int lit)=0;
  virtual ~ImplicationExtension() {};
};

#endif
