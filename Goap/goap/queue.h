#pragma once
#include <math.h>
#include <string>
using namespace std;

template <class Type>
class MinMaxHeap
{
public:
    /* Constructor */
    MinMaxHeap(Type *arr, const int mSize, const int cSize);

    /* Destructor */
    ~MinMaxHeap();

	/* Accessors */
    void getFirstTenElements() const;
    void getLastTenElements() const;
	int getNumOfComparisons() const;
	double getCpuCycles() const;

private:
	/* Variables */
    Type *Heap;	                // MinMaxHeap array
    int curSize, maxSize;       // Heap current size, Heap max Size
	int compCount;              // Holds number of comparisons per run
	double cpuTime;             // Holds the number of cpu cycles

	/* Modifiers */
    void buildMinMaxHeap();
    void percolateDown(const int pos);
    void percolateDownMax( const int pos );
    void percolateDownMin( const int pos );
    void swap(const int indexOne, const int indexTwo);

	/* Accessors */
	bool isMaxLevel(const int pos);
    int GetMaxGrandChild(int pos);
    int GetMinGrandChild(int pos);
    bool isLeafPos(int pos);
    int GetMaxDescendant(int pos);
    int GetMinDescendant(int pos);
};
