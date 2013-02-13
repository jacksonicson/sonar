#include "StdAfx.h"
#include "ANode.h"
#include <iostream>
#include <map>

using namespace std; 

int *pool = NULL; 
int poolCount = 0; 
int*  pooled(const int domLength)
{
	if(pool == NULL) {
		cout << "new pool" << endl; 
		pool = new int[100000 * domLength];
	}

	if(poolCount > 100000)
		pool = new int[100000 * domLength];

	poolCount++;
	return pool + domLength * poolCount; 
}

ANode::ANode(int* mapping, int* volume, int domLength, int nodeLength, int modifyIndex, int modifyValue)
{
	this->mapping = mapping; 
	this->volume = volume; 
	this->domLength = domLength; 
	this->nodeLength = nodeLength; 
	this->costs = 9999; 
	this->prio = 0; 
	this->pred = NULL; 
	this->root = false; 

	this->modify_index = modifyIndex;
	this->modify_value = modifyValue; 
}

int* ANode::load; 

bool ANode::valid()
{
	if(ANode::load == NULL)
		ANode::load = new int[nodeLength];

	for(int i=0; i<nodeLength; i++)
		ANode::load[i] = 0;

	for(int i=0; i<domLength; i++)
	{
		ANode::load[value(i)] += volume[i];
		if(ANode::load[value(i)] > 100)
		{
			return false;
		}

	}

	return true; 
}

unsigned ANode::hash()
{
	unsigned sum = 0; 
	for(int i=0; i<domLength; i++)
	{
		sum += value(i);
	}
	return sum; 
}

bool ANode::operator()(ANode* a, ANode* b)
{
	return a->hash() < b->hash(); 
}

bool ANode::equals(ANode* b)
{
	for(int i=0; i<domLength; i++)
	{
		if(value(i) != b->value(i))
			return false; 
	}

	return true; 
}

inline bool ANode::operator==(const ANode& a) {
	ANode* b = (ANode*)&a; 
	return this->equals(b);
}

inline bool ANode::operator <(const ANode& a) {
	ANode* b = (ANode*)&a; 
	return this->hash() < b->hash(); 
}

void ANode::dump() {
	cout << "node: ";
	for(int i=0; i<domLength; i++)
	{
		cout << value(i) << " ,";
	}
	cout << endl;
}

int ANode::h(ANode* end)
{
	int sum = 0; 
	for(int i=0; i<domLength; i++)
	{
		if(value(i) != end->value(i))
			sum += 1;
	}
	return sum; 
}

int ANode::value(int index)
{
	int value = mapping[index];
	if(index == this->modify_index)
		value = this->modify_value;
	return value; 
}


pair<vector<ANode*>, vector<int>> ANode::childs(ANode* end, multimap<int, ANode*>& mesh)
{
	vector<ANode*> result; 
	vector<int> costs; 
	
	int* mapping2 = NULL; 

	for(int d=0; d<domLength; d++)
	{
		for(int n=0; n<this->nodeLength; n++)
		{
			if(this->mapping[d] == n)
				continue;

			int cc = 1;
			if(end->value(d) == this->value(d))
				cc += 1;

			// Check if node exists already without creating it
			int swap = this->mapping[modify_index];
			this->mapping[modify_index] =  modify_value;

			int swap_index = this->modify_index;
			this->modify_index = -1; 
			
			int backup = this->mapping[d];
			this->mapping[d] = n;
			
			bool exist = false;
			pair<multimap<int, ANode*>::iterator, multimap<int, ANode*>::iterator> found;
			found = mesh.equal_range(this->hash());
			for (multimap<int, ANode*>::iterator it2 = found.first; it2 != found.second; ++it2)
			{
				if((*it2).second->equals(this))
				{
					exist = true;
					result.insert(result.begin(), (*it2).second);
					costs.insert(costs.begin(), cc);
					break;
				}
			}

			// Restore mapping
			this->mapping[d] = backup;
			this->mapping[modify_index] = swap; 
			this->modify_index = swap_index;
			
			// Continue if exists
			if(exist)
				continue; 

			if(mapping2 == NULL)
			{
				// Create the new node for real now
				// mapping2 = pooled(domLength); // new int[domLength];
				mapping2 = new int[domLength];
				memcpy(mapping2, this->mapping, sizeof(int) * domLength); 
				mapping2[this->modify_index] = this->modify_value;
			}

			// Create new instance of the node (Give mapping as pointer) 
			ANode* newNode = new ANode(mapping2, volume, domLength, nodeLength, d, n);

			if(newNode->valid())
			{
				mesh.insert(pair<int, ANode*>(newNode->hash(), newNode));

				result.insert(result.begin(), newNode);
				costs.insert(costs.begin(), cc);
			}
		}
	}

	return pair<vector<ANode*>, vector<int>>(result, costs); 
}