// goap.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include <cstdlib>
#include <queue>
#include <string>
#include <hash_map>
#include <map>
#include <set>
#include <iostream>
#include <algorithm>
#include "queue.h"
#include <stdlib.h>
#include "q2.h"

using namespace std; 

// Array length template
template<typename T, int size>
int len(T(&)[size]){return size;}

class ANode
{
public:
	int* mapping; 
	int* volume;
	int nodeLength; 
	int domLength;
	int costs; 
	int prio;
	ANode* pred;

public:
	ANode(int* mapping, int* volume, int domLength, int nodeLength)
	{
		this->mapping = mapping;
		this->volume = volume; 
		this->domLength = domLength;
		this->nodeLength = nodeLength; 
		this->costs = 9999; 
		this->prio = 0; 
		this->pred = NULL; 
	}

	ANode() {
	}

	bool valid()
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

	unsigned hash()
	{
		unsigned sum = 0; 
		for(int i=0; i<domLength; i++)
		{
			sum += mapping[i];
		}
		return sum; 
	}


	bool operator()(ANode* a, ANode* b)
	{
		// TODO: FAIL this odes not work!!!
		return a->hash() < b->hash(); 
		// return a->costs > b->costs; 
	}
	
	bool equals(ANode* b)
	{
		for(int i=0; i<domLength; i++)
		{
			if(mapping[i] != b->mapping[i])
				return false; 
		}

		return true; 
	}

	inline bool operator==(const ANode& a) {
		ANode* b = (ANode*)&a; 
		return this->equals(b);
	}

	inline bool operator <(const ANode& a) {
		ANode* b = (ANode*)&a; 
		return this->hash() < b->hash(); 
	}

	vector<ANode*> childs();

	void dump() {
		cout << "node: ";
		for(int i=0; i<domLength; i++)
		{
			cout << mapping[i] << " ,";
		}
		cout << endl;
	}

	int h(ANode* end)
	{
		int sum = 0; 
		for(int i=0; i<domLength; i++)
		{
			if(mapping[i] != end->mapping[i])
				sum += 1;
		}
		return sum; 
	}
};

// Priority list
PriorityQueue<ANode*, unsigned int> pqopen; 
multimap<int, ANode*> openLookup;

// Closed list
set<ANode*, ANode> closed; 

// Mesh lookup
multimap<int, ANode*> mesh;

void addOpen(ANode* node)
{
	openLookup.insert(pair<int, ANode*>(node->hash(), node));
}

bool isInOpen(ANode* node)
{
	pair<multimap<int, ANode*>::iterator, multimap<int, ANode*>::iterator> found;
	found = openLookup.equal_range(node->hash());
	for (multimap<int, ANode*>::iterator it2 = found.first; it2 != found.second; ++it2)
	{
		if((*it2).second->equals(node))
		{
			return true;
		}
	}

	return false;
}

void remOpen(ANode* node)
{

	pair<multimap<int, ANode*>::iterator, multimap<int, ANode*>::iterator> found;

	found = openLookup.equal_range(node->hash());

	for (multimap<int, ANode*>::iterator it2 = found.first; it2 != found.second; ++it2)
	{
		if((*it2).second->equals(node))
		{
			openLookup.erase(it2);
			break;
		}
	}
}

vector<ANode*> ANode::childs()
{
	vector<ANode*> result; 
	
	for(int d=0; d<domLength; d++)
	{
		for(int n=0; n<this->nodeLength; n++)
		{
			if(this->mapping[d] == n)
				continue;

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
					if((*it2).second == this)
						cout << "POBELM" <<endl;

					exist = true;
					result.insert(result.begin(), (*it2).second);
					break;
				}
			}

			this->mapping[d] = backup;

			if(exist) {
				continue; 
			}



			// Create the new node for real
			int* mapping2 = new int[domLength];
			int* volume2 = new int[domLength];
			memcpy(mapping2, this->mapping, sizeof(int) * domLength); 
			memcpy(volume2, this->volume, sizeof(int) * domLength); 
			mapping2[d] = n;
			ANode* newNode = new ANode(mapping2, volume2, domLength, nodeLength);
			if(newNode->valid())
			{
				mesh.insert(pair<int, ANode*>(newNode->hash(), newNode));
				result.insert(result.begin(), newNode);
			}
		}
	}

	return result; 
}


void expand(ANode* node, ANode* end)
{
	// node->dump();
	// Generate a list of known childs
	vector<ANode*> childs = node->childs(); 
	a: for(int i=0; i<childs.size(); i++)
	{
		ANode* child = childs[i];
		if(child == node)
		{
			cout << "warn" << endl;
			continue;
		}

		// Check if it is in closed list!
		set<ANode*, ANode>::iterator it = closed.find(childs[i]);
		bool skip = false;
		for (;it!=closed.end(); it++)
		{
			// Skip child if closed
			if((*it)->equals(child))
			{
				skip = true;
				break;
			}
		}

		if(skip)
			continue;

		// Check if it is in open list!
		bool inOpen = isInOpen(child);

		// Cost relaxion (Attention: weight has to be implemented)
		int costs = node->costs + 1;
		if(inOpen && costs >= child->costs)
			continue;

		child->pred = node; 
		child->costs = costs;

		int prio = costs + 3*child->h(end); // todo: heuristic implementation
		child->prio = child->costs + prio;
		if(!inOpen)
		{
			pqopen.push(child, child->prio);
			addOpen(child); 
		} else {
			pqopen.update(child, child->prio); 
		}
	}
}

ANode* peek()
{
	ANode* node = pqopen.top(); 
	pqopen.pop(); 
	remOpen(node); 

	return node; 
}

void runAstar()
{
	/*int lenDomains = 50; 
	int lenNodes = 30; 
	int* mapping = new int[lenDomains];
	int* volume = new int[lenDomains];*/

	int lenDomains = 3; 
	int lenNodes = 3; 
	int mapping[] = {0,  1,  2};
	int volume[] =  {80, 25, 10};
	
	/*for(int i=0; i<lenDomains; i++)
	{
		mapping[i] = rand() % lenNodes;
		volume[i] = rand() % 30;
	}*/

	int* mapping2 = new int[lenDomains];
	int* volume2 = new int[lenDomains];
	memcpy(mapping2, mapping, lenDomains * sizeof(int)); 
	memcpy(volume2, volume, lenDomains * sizeof(int)); 

	mapping2[0] = 1;
	mapping2[1] = 0;

	ANode start(mapping, volume, lenDomains, lenNodes);
	ANode end(mapping2, volume2, lenDomains, lenNodes); 
	
	if(!start.valid())
	{
		cout << "invalid start" << endl; 
		return;
	}
	if(!end.valid())
	{
		cout << "invalid end" << endl; 
		return; 
	}

	start.dump();
	end.dump();

	start.prio = 0; 
	start.costs = 0; 

	pqopen.push(&start, start.prio); 
	addOpen(&start); 
	
	unsigned expansions = 0;
	ANode* found = NULL; 
	while(!pqopen.empty())
	{
		ANode* current = peek();
		if(current == NULL)
		{
			break;
		}

		if(current->equals(&end))
		{
			cout << "Solution found... " << endl;
			cout << "expansion: " << expansions << " open size " << pqopen.size() << " close size " << closed.size() << endl; 
			found = current; 
			break;
		}

		expand(current, &end); 

		expansions++; 
		if(expansions % 1000 == 0)
			cout << "expansion: " << expansions << " open size " << pqopen.size() << " close size " << closed.size() << endl; 

		closed.insert(current); 
	}

	
	if(found != NULL)
	{
		while(true)
		{	
			found->dump();
			if(found->pred == NULL)
				break;
			found = found->pred; 
		}
	} else {
		cout << "expansion: " << expansions << " open size " << pqopen.size() << " close size " << closed.size() << endl; 
		cout << "no solution" << endl;
	}
	
}


class Node {
public:
	int value; 
public:
	Node(int value) {
		this->value = value; 
	}

}; 

struct CompareNode : public std::binary_function<Node*, Node*, bool>                                                                                       
{  
  bool operator()(const Node* lhs, const Node* rhs) const  
  {  
     return lhs->value < rhs->value;  
  }  
};  

struct cmp_str
{
   bool operator()(const Node* a, const Node* b)
   {
      return a->value < b->value; 
   }
};

void testStlContainer()
{
	using namespace std; 
	
	// Testing priority queue
	priority_queue<Node*, vector<Node*>, CompareNode> test;
	test.push(&Node(2));
	test.push(&Node(20));

	printf("Testing map \n"); 
	// Testing hash map functionality
	//hash_map<const char*, int, hash<const char*>, eqstr> test1; 
	multimap<string, Node*> multi;
	multi.insert(pair<string, Node*>("test", &Node(200)));
	
	pair<multimap<string, Node*>::iterator, multimap<string, Node*>::iterator> ppp;

	ppp = multi.equal_range("test");

	for (multimap<string, Node*>::iterator it2 = ppp.first; it2 != ppp.second; ++it2)
    {

	}

	// Testing sets
	set<string> tset; 
	set<Node*, cmp_str> aset; 
	aset.insert(&Node(20)); 
	set<Node*, cmp_str>::iterator it = aset.find(&Node(20)); 
	
	if(it == aset.end())
	{
	} else {
	}
}

int main()
{
	// testStlContainer(); 
	runAstar(); 
/*
	PriorityQueue<std::string, unsigned int> pq; 
*/
/*
	pq.push("A", 3); 
	pq.push("C", 1); 
	pq.push("F", 2); 
	pq.push("Z", 44); 
	pq.push("H", 32); 
	pq.push("Y", 111); 

	pq.print(); 

	cout << "Toping..." << endl; 

	cout << pq.top() << endl; 

	cout << "Poping..." << endl; 

	pq.pop(); 

	pq.print(); 

	cout << "Changing A to 400..." << endl; 

	pq.update("A", 400); 

	pq.print(); 
	*/

	return 0;
}

