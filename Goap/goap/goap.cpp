// goap.cpp : Defines the entry point for the console application.
//

#include "stdafx.h"
#include <stdio.h>


class ANode
{
public:
	ANode();
public:
	int* domains; 
	int* nodes;
};

ANode::ANode()
{
	this->domains = new int[100];
	for(int i=0; i<100; i++)
	{
		this->domains[i] = i;
	}
}

int main()
{
	const long amount = 99900; 
	ANode* data[amount];
	for(int i=0; i<amount; i++)
	{
		data[i] = new ANode();
	}
	
	printf("ok");

	for(int i=0; i<amount; i++)
	{
		delete data[i];
	}
	printf("deleted");

	return 0;
}

