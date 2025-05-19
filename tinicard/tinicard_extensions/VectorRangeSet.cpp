#include <utility>
#include <vector>
#include <cstdio>

#include "VectorRangeSet.h"
using namespace std;

VectorRangeSet::VectorRangeSet() {
	buffer_capacity=0;
	clear();
}
void VectorRangeSet::clear() {
	data_size=0;
	buffer_size=0;
	buffer.clear();
}
void VectorRangeSet::check_increase_capacity(int size) {
	if (size>buffer_capacity) {
		buffer_capacity = size < 64 ? 64 : size*2;
		buffer.reserve(buffer_capacity);
		buffer_capacity *= 2;
	}
}
void VectorRangeSet::add(int m) {
	// specific case that the buffer is totally empty.
	if (buffer_size==0) {
		check_increase_capacity(buffer_size+1);
		buffer.push_back(make_pair(m,m));
		buffer_size++;
		data_size++;
		return;
	}
	// if datapoint is greater than the rightmost data
	if (m>buffer[buffer_size-1].second) {
		if (m == buffer[buffer_size-1].second+1) {
			buffer[buffer_size-1].second += 1;
		} else {
			check_increase_capacity(buffer_size+1);
			buffer.push_back(make_pair(m,m));
			buffer_size++;
		}
		data_size++;
		return;
	}
	// if datapoint is less than the leftmost data
	if (m<buffer[0].first) {
		if (m == buffer[0].first-1) {
			buffer[0].first -= 1;
		} else {
			check_increase_capacity(buffer_size+1);
			buffer.insert(buffer.begin(), make_pair(m,m));
			buffer_size++;
		}
		data_size++;
		return;
	}
	// if datapoint is in the leftmost data-range
	if (m<=buffer[0].second) return;
	// if datapoint is in the rightmost data-range
	if (m>=buffer[buffer_size-1].first) return;
	// otherwise data is within the range of the buffer
	int left = 0;
	int right = buffer_size-1;
	while (left+1<right) {
		int middle = (left+right)/2;
		bool less_than_second = (m <= buffer[middle].second);
		bool greater_than_first = (m >= buffer[middle].first);
		if (less_than_second) {
			if (greater_than_first) return; // already contained in middle, just return
			else right = middle; // to the left of middle
		} else left = middle; // to the right of middle
	}
	// ok, fail to find, datapoint is between right and left
	// three cases, either extend left, extend right, merge left and right, or singleton
	bool extend_left = (m == buffer[left].second+1);
	bool extend_right = (m == buffer[right].first-1);
	if (extend_left) {
		if (extend_right) { // merge left and right
			buffer[left].second = buffer[right].second;
			buffer.erase(buffer.begin()+right);
			buffer_size--;
		} else { // simply extend left
			buffer[left].second += 1;
		}
	} else {
	if (extend_right) { // simply extend right
		buffer[right].first -= 1;
		} else { // add singleton
			check_increase_capacity(buffer_size+1);
			buffer.insert(buffer.begin()+right,make_pair(m,m));
			buffer_size++;
		}
	}
	data_size++;
}
void VectorRangeSet::insert(int m) {
	add(m);
}
bool VectorRangeSet::find(int m) {
	// specific case that the buffer is totally empty.
	if (buffer_size==0) return false;
	// if datapoint is less than the leftmost data
	if (m<buffer[0].first) return false;

	// if datapoint is greater than the rightmost data
	if (m>buffer[buffer_size-1].second) return false;
	// if datapoint is in the leftmost data-range
	if (m<=buffer[0].second) return true;
	// if datapoint is in the rightmost data-range
	if (m>=buffer[buffer_size-1].first) return true;
	// otherwise data is within the range of the buffer
	int left = 0;
	int right = buffer_size-1;
	while (left+1<right) {
		int middle = (left+right)/2;
		bool less_than_second = (m <= buffer[middle].second);
		bool greater_than_first = (m >= buffer[middle].first);
		if (less_than_second) {
			if (greater_than_first) return true; // already contained in middle, just return true
			else right = middle; // to the left of middle
		} else left = middle; // to the right of middle
	}
	return false;
}
void VectorRangeSet::print() {
	printf("VectorRangeSet: ");
	for (auto it = buffer.begin(); it!=buffer.end(); it++)
		printf("[%i %i] ",(*it).first,(*it).second);
	printf(", %i pairs, %i elements\n",buffer_size,data_size);
}
int VectorRangeSet::size() {
	return data_size;
}



