#ifndef VECTORRANGESET_HH
#define VECTORRANGESET_HH

#include <utility>
#include <vector>
#include <cstdio>

using namespace std;
// A simple vector of pairs of integers, identifying that the container contains integers of set {[a,b],[c,d],[e,f],[g,g],[h,i]} etc.
// where each of the pairs is a begin/end of range
class VectorRangeSet {
private:
	void check_increase_capacity(int size);
public:
  vector<pair<int,int>> buffer;
  int buffer_size;
  int buffer_capacity;
  int data_size;
  VectorRangeSet();
  void clear();
  void add(int m);
  void insert(int m);
  bool find(int m);
  void print();
  int size();
};

#endif



