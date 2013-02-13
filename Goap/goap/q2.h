#ifndef _PRIORITYQUEUE_H_ 
#define _PRIORITYQUEUE_H_ 

///////////////////////////////////////////////////////////// 
// A mutable min-priority queue, based on a list. Allows 
// to modify the key of an item on runtime, which eventually 
// will cause a rearrangement. 
///////////////////////////////////////////////////////////// 

#include <list> 
#include <algorithm> 
#include <functional> 

template<typename T, typename K> 
class PriorityQueue 
{ 
public: 
    struct Element 
    { 
        Element(const T& v) : value(v) { } 
        Element(const T& v, const K& k) : value(v), key(k) { } 
        bool operator==(const Element& other) const { return (value == other.value); }  
        bool operator<(const Element& other) const { return key < other.key; } 
        T value; 
        K key; 
    }; 

    PriorityQueue(); 
    PriorityQueue(const PriorityQueue&); 
    PriorityQueue& operator=(const PriorityQueue&);  
    ~PriorityQueue(); 
    bool empty() const; 
    size_t size() const; 
    void clear(); 
    void push(const T&, const K&); 
    void update(const T&, const K&); 
    T top() const; 
    void pop(); 
    void print() const; 

private: 
    std::list<Element> m_list; 
}; 

template<typename T, typename K> 
PriorityQueue<T, K>::PriorityQueue() 
{ 
} 

template<typename T, typename K> 
PriorityQueue<T, K>::PriorityQueue(const PriorityQueue<T, K>& rhs) 
{ 
    *this = rhs; 
} 

template<typename T, typename K> 
PriorityQueue<T, K>& PriorityQueue<T, K>::operator=(const PriorityQueue<T, K>& rhs) 
{  
    if(this == &rhs) 
        return *this;  

    m_list = rhs.m_list; 

    return *this; 
} 

template<typename T, typename K> 
PriorityQueue<T, K>::~PriorityQueue()    
{ 
} 

template<typename T, typename K> 
bool PriorityQueue<T, K>::empty() const 
{ 
    return m_list.empty(); 
} 

template<typename T, typename K> 
size_t PriorityQueue<T, K>::size() const 
{ 
    return m_list.size(); 
} 

template<typename T, typename K> 
void PriorityQueue<T, K>::clear() 
{ 
    m_list.clear(); 
} 

template<typename T, typename K> 
void PriorityQueue<T, K>::push(const T& x, const K& key) 
{ 
    std::list<PriorityQueue::Element>::iterator it; 

    for(it = m_list.begin(); it != m_list.end(); it++) { 
        if((*it).key > key) { 
            m_list.insert(it, Element(x, key)); 
            return; 
        } 
    } 

    m_list.push_back(Element(x, key)); 
} 

template<typename T, typename K> 
T PriorityQueue<T, K>::top() const 
{ 
    return m_list.front().value; 
} 

template<typename T, typename K> 
void PriorityQueue<T, K>::pop() 
{ 
    m_list.pop_front(); 
} 

template<typename T, typename K> 
void PriorityQueue<T, K>::update(const T& x, const K& k) 
{ 
    std::list<PriorityQueue::Element>::iterator it; 

    it = std::find(m_list.begin(), m_list.end(), Element(x)); 

    (*it).key = k; 

    m_list.sort();    // Comparisons are performed using operator< 
} 

template<typename T, typename K> 
void PriorityQueue<T, K>::print() const 
{ 
    std::list<PriorityQueue::Element>::const_iterator it; 

    for(it = m_list.begin(); it != m_list.end(); it++) { 
        std::cout << (*it).value << ":" << (*it).key << std::endl; 
    } 
} 

#endif  