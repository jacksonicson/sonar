#include "StdAfx.h"
#include "ANode.h"
#include <iostream>
#include <map>

using namespace std; 

ANode::ANode() {
	// Empty
}

ANode::ANode(int* mapping, int* volume, int domLength, int nodeLength)
{
	this->mapping = mapping;
	this->volume = volume; 
	this->domLength = domLength;
	this->nodeLength = nodeLength; 
	this->costs = 9999; 
	this->prio = 0; 
	this->pred = NULL; 
	this->root = false; 
}

ANode::ANode(int* mapping, int* volume, int domLength, int nodeLength, bool root)
{
	ANode(mapping, volume, domLength, nodeLength);
	this->root = root;
}

bool ANode::valid()
{
	int* load = new int[nodeLength];
	for(int i=0; i<nodeLength; i++)
		load[i] = 0;

	for(int i=0; i<domLength; i++)
	{
		load[mapping[i]] += volume[i];
		if(load[mapping[i]] > 100)
			return false;
	}

	return true; 
}

unsigned ANode::hash()
{
	unsigned sum = 0; 
	for(int i=0; i<domLength; i++)
	{
		sum += mapping[i];
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
		if(mapping[i] != b->mapping[i])
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
		cout << mapping[i] << " ,";
	}
	cout << endl;
}

int ANode::h(ANode* end)
{
	int sum = 0; 
	for(int i=0; i<domLength; i++)
	{
		if(mapping[i] != end->mapping[i])
			sum += 1;
	}
	return sum; 
}


pair<vector<ANode*>, vector<int>> ANode::childs(ANode* end, multimap<int, ANode*>& mesh)
{
	vector<ANode*> result; 
	vector<int> costs; 
	
	for(int d=0; d<domLength; d++)
	{
		for(int n=0; n<this->nodeLength; n++)
		{
			if(this->mapping[d] == n)
				continue;

			int cc = 1;
			if(end->mapping[d] == mapping[d])
				cc += 3;

			// Check if node exists already without creating it
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
				
			// Continue if exists
			if(exist)
				continue; 

			// Create the new node for real now
			int* mapping2 = new int[domLength];
			memcpy(mapping2, this->mapping, sizeof(int) * domLength); 
			mapping2[d] = n;

			ANode* newNode = new ANode(mapping2, volume, domLength, nodeLength);

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