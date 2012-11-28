#pragma once
#include <vector>
#include <map>

class ANode
{
public:
	int* mapping; 
	int* volume;
	int nodeLength; 
	int domLength;
	int costs; 
	int prio;
	bool root; 
	ANode* pred;

public:
	ANode();
	ANode(int* mapping, int* volume, int domLength, int nodeLength);
	ANode(int* mapping, int* volume, int domLength, int nodeLength, bool root);
	
	bool valid();
	unsigned hash();
	bool operator()(ANode* a, ANode* b);
	bool equals(ANode* b);
	inline bool operator==(const ANode& a);
	inline bool operator <(const ANode& a);
	std::pair<std::vector<ANode*>, std::vector<int>> childs(ANode*, std::multimap<int, ANode*>&);
	void dump();
	int h(ANode* end);
};

