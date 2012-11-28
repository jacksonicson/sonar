#pragma once
#include "anode.h"
#include <vector>

class Scoreboard
{
private:
	std::vector<ANode*> processed; 
public:
	Scoreboard(void);
	void report(ANode*);
	
};

