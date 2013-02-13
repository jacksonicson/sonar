#pragma once
#include <vector>
#include <map>

int* pooled();

class ANode
{
	
public:
	static int* load; 
	int* mapping; 
	int* volume;
	int nodeLength; 
	int domLength;
	int costs; 
	int prio;
	bool root; 
	ANode* pred;

	int modify_index; 
	int modify_value; 

public:
	ANode(int* mapping, int* volume, int domLength, int nodeLength, int modifyIndex, int modifyValue);
	
	bool valid();
	unsigned hash();
	bool operator()(ANode* a, ANode* b);
	bool equals(ANode* b);
	inline bool operator==(const ANode& a);
	inline bool operator <(const ANode& a);
	std::pair<std::vector<ANode*>, std::vector<int>> childs(ANode*, std::multimap<int, ANode*>&);
	void dump();
	int h(ANode* end);

	int value(int index); 
};

