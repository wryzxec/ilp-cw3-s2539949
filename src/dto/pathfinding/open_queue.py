import heapq

from typing import List, Tuple

from pathfinding.node import Node

class OpenQueue:
    def __init__(self):
        self._heap: List[Tuple[float,float,Node]] = []
    
    def push(self, node: Node):
        key = (node.distanceLeft(), -node.distanceTravelled)
        heapq.heappush(self._heap, (key[0], key[1], node))
    
    def pop(self):
        _,_,node = heapq.heappop(self._heap)
        return node

    def isEmpty(self):
        return not self._heap