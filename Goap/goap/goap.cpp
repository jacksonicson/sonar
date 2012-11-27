// goap.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include <stdio.h>
#include <cstdlib>
#include <queue>
#include <string>


class ANode
{
public:
	ANode(int a, int* b, int c);
	void dump(); 
public:
	int lenDomains; 
	int lenNodes; 
	int* domains; 
	int* nodes;
	int g;
	bool operator()(ANode&, ANode&);
};

class AStar {
public:
	AStar(); 
	void run(ANode* start, ANode* end, unsigned* domainload); 
	void expand(); 
};

bool ANode::operator()(ANode& a, ANode& b) {
	if(a.g < b.g) return true; 
	return false; 
}

ANode::ANode(int countDomains, int* nodes, int lenNodes)
{
	domains = new int[countDomains];
	this->lenDomains = countDomains;
	this->nodes = nodes;
	this->lenNodes = lenNodes; 
}

void ANode::dump() {
	printf("Dumping node...\n"); 
	/*for(unsigned i=0; i<lenDomains; i++)
	{
		printf("%i ", domains[i]); 
	}*/
	printf("\n"); 
}

AStar::AStar() {
	using namespace std; 
	priority_queue<int> asdf;
}

void AStar::run(ANode* start, ANode* end, unsigned* domainload) {

}

void AStar::expand() {

}

int main()
{
	int* nodes = new int[3];
	int domainCount = 5; 

	ANode start(domainCount, nodes, 10); 
	ANode end(domainCount,nodes,10); 

	
	
	start.domains[0] = 1;
	start.domains[1] = 2;
	start.domains[2] = 1;
	start.domains[3] = 1;
	start.domains[4] = 2;

	end.domains[0] = 1;
	end.domains[1] = 2;
	end.domains[2] = 1;
	end.domains[3] = 1;
	end.domains[4] = 2;

	unsigned domainload[] = {10,30,20,33,44};

	AStar star; 
	star.run(&start, &end, domainload); 
	
	using namespace std; 


	priority_queue<ANode> nodes; 

	return 0;
}

