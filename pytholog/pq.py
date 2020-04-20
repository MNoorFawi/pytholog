from collections import deque 
#from heapq import heappush, heappop #was to test implementing priority queue

## the queue object we will use to store goals we need to search
## FIFO (First In First Out)
## using FIFO ensures that if cut is used we have the first answer from the facts fed first to KB
## it is very useful in graph cases to get the shortest path first. But it depends on the order
## the facts were defined in the knowledge base.
class SearchQueue():
    def __init__(self):
        self._container = deque()  ## deque() not list [] 
                                   ## the idea is to pop from the left side
    @property
    def empty(self):
        return not self._container
    def push(self, expr):
        self._container.append(expr)
    def pop(self):
        return self._container.popleft() # FIFO popping from the left is O(1) in deque() unlike in list
    def __repr__(self):
        return repr(self._container)
        
