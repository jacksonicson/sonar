#include "stdafx.h"
#include "queue.h"


/* Gets the heap structure and heapifies it. */
template <class Type>
MinMaxHeap<Type>::MinMaxHeap(Type *arr, const int mSize, const int cSize)
{
    Heap = arr;
    curSize = cSize;
    maxSize = mSize;
	compCount = 0;
    buildMinMaxHeap();
}

/* Deallocated memory allocated for the Heap. */
template <class Type>
MinMaxHeap<Type>::~MinMaxHeap()
{
    if (Heap != NULL)
        delete [] Heap;
}

/* Prints the first 10 elements of the heap. */
template <class Type>
void MinMaxHeap<Type>::getFirstTenElements() const
{
	int max = 10;
	if (curSize < max)
		max = curSize;
    for (int i=0;i<max;i++)
	    cout << Heap[i] << " ";
}

/* Prints the last 10 elements of the heap. */
template <class Type>
void MinMaxHeap<Type>::getLastTenElements() const
{
	int max = 10;
	if (curSize < max)
		max = curSize;
    for (int i=curSize-max;i<curSize;i++)
		cout << Heap[i] << " ";
}

/* Returns the number of comparisons made during the heapify process. */
template <class Type>
int MinMaxHeap<Type>::getNumOfComparisons() const
{
	return compCount;
}

/* Returns the number of cycles for the heapify	process. */
template <class Type>
double MinMaxHeap<Type>::getCpuCycles() const
{
	return cpuTime;
}

/* Returns the maximum grandchild of a position. */
template <class Type>
int MinMaxHeap<Type>::GetMaxGrandChild(int pos)
{
    /* Initializing values */
    bool maxValInit = false;
    Type maxVal;
    int maxIndex = pos;
    int curIndex;

    /* Get a grandchild */
    curIndex = 2*(2*pos);

    /* Check for valid position */
    compCount++;
    if (curIndex <= curSize)
    {
        /* Check if maxVal isn't initialized or 
        /* current index is greater than maxVal
        /*/
        compCount++;
        if ((!maxValInit) || (Heap[curIndex] > maxVal)) 
        {
            maxIndex = curIndex;
            maxVal = Heap[maxIndex];
            maxValInit = true;
        }
    }

    /* Get the other grandchild */
    curIndex = 2*((2*pos)+1);
    compCount++;
    if (curIndex <= curSize)
    {
        compCount++;
        if ((!maxValInit) || (Heap[curIndex] > maxVal))
        {
            maxIndex = curIndex;
            maxVal = Heap[maxIndex];
            maxValInit = true;
        }
    }

    curIndex = 2*(2*pos)+1;
    compCount++;
    if (curIndex <= curSize)
    {
        compCount++;
        if ((!maxValInit) || (Heap[curIndex] > maxVal))
        {
            maxIndex = curIndex;
            maxVal = Heap[maxIndex];
            maxValInit = true;
        }
    }

    curIndex = (2*((2*pos)+1))+1;
    compCount++;
    if (curIndex <= curSize)
    {
        compCount++;
        if ((!maxValInit) || (Heap[curIndex] > maxVal))
        {
            maxIndex = curIndex;
            maxVal = Heap[maxIndex];
            maxValInit = true;
        }
    }
    return maxIndex;
}

/* Returns the position of the minimum */
template <class Type>
int MinMaxHeap<Type>::GetMinGrandChild(int pos)
{
    bool maxValInit = false;
    Type minVal;
    int minIdx = pos;
    int curIndex;

    curIndex = 2*(2*pos);
    compCount++;
    if (curIndex <= curSize)
    {
        compCount++;
        if ((!maxValInit) || (Heap[curIndex] < minVal))
        {
            minIdx = curIndex;
            minVal = Heap[minIdx];
            maxValInit = true;
        }
    }

    curIndex = 2*((2*pos)+1);
    compCount++;
    if (curIndex <= curSize)
    {
        compCount++;
        if ((!maxValInit) || (Heap[curIndex] < minVal))
        {
            minIdx = curIndex;
            minVal = Heap[minIdx];
            maxValInit = true;
        }
    }

    curIndex = 2*(2*pos)+1;
    compCount++;
    if (curIndex <= curSize)
    {
        compCount++;
        if ((!maxValInit) || (Heap[curIndex]<minVal))
        {
            minIdx = curIndex;
            minVal = Heap[minIdx];
            maxValInit = true;
        }
    }

    curIndex = (2*((2*pos)+1))+1;
    compCount++;
    if (curIndex <= curSize)
    {
        compCount++;
        if ((!maxValInit) || (Heap[curIndex] < minVal))
        {
            minIdx = curIndex;
            minVal = Heap[minIdx];
            maxValInit = true;
        }
    }
return minIdx;
}

/* Returns the maximum child of a position. */
template <class Type>
int MinMaxHeap<Type>::GetMaxDescendant(int pos)
{
    bool maxValInit = false;
    Type maxVal;
    int maxIndex = pos;
    int curIndex;

    maxIndex = GetMaxGrandChild(pos);
    compCount++;
    if (maxIndex != pos)
    {
        maxVal = Heap[maxIndex];
        maxValInit = false;
    }

    curIndex = 2*pos;
    compCount++;
    if ((curIndex <= curSize)&&(isLeafPos(curIndex)))
    {
        compCount++;
        if ((!maxValInit)||(Heap[curIndex] > maxVal))
        {
            maxIndex = curIndex;
            maxVal = Heap[curIndex];
            maxValInit = true;
        }
    }

    curIndex = (2*pos)+1;
    compCount++;
    if ((curIndex <= curSize)&&(isLeafPos(curIndex)))
    {
        compCount++;
        if ((!maxValInit)||(Heap[curIndex] > maxVal))
        {
            maxIndex = curIndex;
            maxVal = Heap[curIndex];
            maxValInit = true;
        }
    }
return maxIndex;
}

/* Returns the minimum element of a position. */
template <class Type>
int MinMaxHeap<Type>::GetMinDescendant(int pos) // opposite of GetMaxDescendant Idx
{
    bool maxValInit = false;
    Type minVal;
    int minIdx = pos;
    int curIndex;

    minIdx = GetMinGrandChild(pos);
    compCount++;
    if (minIdx != pos)
    {
        minVal = Heap[minIdx];
        maxValInit = true;
    }

    curIndex = 2*pos;
    compCount++;
    if ((curIndex <= curSize)&&(isLeafPos(curIndex)))
    {
        compCount++;
        if ((!maxValInit)||(Heap[curIndex] < minVal))
        {
            minIdx = curIndex;
            minVal = Heap[curIndex];
            maxValInit = true;
        }
    }

        curIndex = (2*pos)+1;
        compCount++;
        if ((curIndex <= curSize)&&(isLeafPos(curIndex)))
        {
            compCount++;
            if ((!maxValInit)||(Heap[curIndex] < minVal))
            {
                minIdx = curIndex;
                minVal = Heap[curIndex];
                maxValInit = true;
            }
        }
return minIdx;
}

/* Perculates down maximum levels until a position is in its correct location. 
 */
template <class Type>
bool MinMaxHeap<Type>::isLeafPos(int pos)
{
    bool isLeaf = false;
    compCount++;
    if ((2*pos > curSize) && ((2*pos)+1 > curSize))
        isLeaf = true;
return isLeaf;
}


/* Builds the Min-Max Heap Tree. */
template <class Type>
void MinMaxHeap<Type>::buildMinMaxHeap()
{
	Stopwatch myWatch;
	myWatch.start();
    for ( int i = curSize/2; i >= 0; i--) 
        percolateDown(i);
	myWatch.stop();
	cpuTime = myWatch.get_end_time();
}

/* Determines the level of a position and percolates it down maximum if level /* is max and percolates down minimum if level is min.
 */
template <class Type>
void MinMaxHeap<Type>::percolateDown(const int pos)
{
    if (isMaxLevel(pos))
        percolateDownMax( pos );
    else
        percolateDownMin( pos );
}

/* Perculates down minimum levels until a position is in its correct location. 
 */
template <class Type>
void MinMaxHeap<Type>::percolateDownMin(const int pos)
{
    /* Find the smallest child/grandchild position */
    int minPos = GetMinDescendant(pos);
    
    /* Check if we have a child */
    compCount++;
    if (minPos > 0) 
    {
        /* Check if minimum is a grandchild */
        compCount++;
        if (minPos >= pos * 4) 
        {
            /* Swap if less than grandparent */
            compCount++;
            if (Heap[minPos] < Heap[pos]) 
            {
                swap(pos, minPos);

                /* Swap if greater than parent */
                compCount++;
                if (Heap[minPos] > Heap[minPos/2])
                    swap(minPos, minPos/2);
                percolateDownMin( minPos );
            }
        }
        /* We don't have a grandchild */
        else 
        {
           /* Swap if less than parent */
           compCount++;
           if (Heap[minPos] < Heap[pos])
              swap(pos, minPos);
        }
    }
}


/* Perculates down maximum levels until a position is in its correct location. */
template <class Type>
void MinMaxHeap<Type>::percolateDownMax( const int pos )
{
    /* Find maximum child/grandchild */
    //int maxPos = getMaximumChild(pos*2, pos*4);
    int maxPos = GetMaxDescendant(pos);

    /* Check if we have a child */
    compCount++;
    if (maxPos > 0) 
    {
        /* Check if position is a grandchild */
        compCount++;
        if (maxPos >= pos * 4) 
        {
           /* Swap if greater than grandparent */
           compCount++;
           if (Heap[maxPos] > Heap[pos]) 
           {
              swap(pos, maxPos);

                /* Swap if less than parent */
                compCount++;
                if (Heap[maxPos] < Heap[maxPos/2])
                    swap(maxPos, maxPos/2);
                percolateDownMax( maxPos );
           }
        }
        /* Position is a child */
        else 
        {
            /* Swap if greater than parent */
            compCount++;
            if (Heap[maxPos] > Heap[pos])
                swap(pos, maxPos);
        }
    }
}

/* Returns true if a position is on maximum level and false if it is not. */
template <class Type>
bool MinMaxHeap<Type>::isMaxLevel(const int pos)
{
	return (int) (log(pos+1.0)/log(2.0))%2 == 1;
}


/* Swaps elements in the Heap array using two positions. */
template <class Type>
void MinMaxHeap<Type>::swap(const int indexOne,const int indexTwo)
{
    Type tmp = Heap[ indexOne ];
    Heap[ indexOne ] = Heap[ indexTwo ];
    Heap[ indexTwo ] = tmp;
}