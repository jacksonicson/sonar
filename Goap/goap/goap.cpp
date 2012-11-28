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
#include <time.h>
#include "ANode.h"

using namespace std; 

// Priority queue for open nodes
PriorityQueue<ANode*, unsigned int> pqopen; 
// Lookup table to check if a node is in open list
multimap<int, ANode*> openLookup;
// Closed lookup table
multimap<int, ANode*> closed; 
// Holds all nodes of the mesh but no edges
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

void expand(ANode* node, ANode* end)
{
	// Generate a list of known childs
	pair<vector<ANode*>, vector<int>> childList = node->childs(end, mesh); 
	vector<ANode*> childs = childList.first; 
	vector<int> meshCosts = childList.second; 
	for(int i=0; i<childs.size(); i++)
	{
		ANode* child = childs[i];

		// Check if it is in closed list!
		bool skip = false;
		pair<multimap<int, ANode*>::iterator, multimap<int, ANode*>::iterator> found;
		found = closed.equal_range(child->hash());
		for (multimap<int, ANode*>::iterator it2 = found.first; it2 != found.second; ++it2)
		{
			if((*it2).second->equals(child))
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
		int costs = node->costs + meshCosts[i];
		if(inOpen && costs >= child->costs)
			continue;

		child->pred = node; 
		child->costs = costs;

		int prio = costs + 4 * child->h(end); // todo: heuristic implementation
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
	srand(time(NULL));

	/*int lenDomains = 25; 
	int lenNodes = 6; 
	int* mapping = new int[lenDomains];
	int* volume = new int[lenDomains];*/

	int lenDomains = 5; 
	int lenNodes = 4; 
	int mapping[] = {0,  1,  2,  2,  3};
	int volume[] =  {90, 30, 70, 10, 75};

	int* buffer = new int[lenNodes];
	for(int i=0; i<lenNodes; i++)
		buffer[i] = 0;

	/*for(int i=0; i<lenDomains; i++)
	{
		mapping[i] = rand() % (lenNodes - 1);

		int load = rand() % 70;
		while((buffer[mapping[i]] + load) >= 100)
		{
			load = rand() % 50;
		}

		volume[i] = load;
		buffer[mapping[i]] += load;
	}*/


	int* mapping2 = new int[lenDomains];
	int* volume2 = new int[lenDomains];
	memcpy(mapping2, mapping, lenDomains * sizeof(int)); 
	memcpy(volume2, volume, lenDomains * sizeof(int)); 

	/*for(int i=0; i<5; i++)
	{
		while(true)
		{
			int domain = rand() % lenDomains;
			int to = rand() % (lenNodes ); 

			if((buffer[to] + volume2[domain]) > 100)
				continue;

			buffer[to] += volume2[domain];
			buffer[mapping[domain]] -= volume2[domain];
			mapping2[domain] = to; 
			
			break;
		}
	}*/

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
	start.root = true;

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

		closed.insert(pair<int, ANode*>(current->hash(), current));
	}

	
	if(found != NULL)
	{
		int count = 0; 
		while(true)
		{	
			found->dump();
			count++; 
			if(found->root == true)
				break;
			found = found->pred; 
		}
		cout << "Lines: " << count << endl;
	} else {
		cout << "expansion: " << expansions << " open size " << pqopen.size() << " close size " << closed.size() << endl; 
		cout << "no solution" << endl;
	}
	
}

int main()
{
	// Verify that it is a min heap
	PriorityQueue<int, int>* s =new PriorityQueue<int, int>();
	s->push(1,22);
	s->push(2,0);
	if(s->top() == 2)
		cout << "PQ Works as expected - min values hihgh priority" << endl << endl; 

	runAstar(); 
	return 0;
}

