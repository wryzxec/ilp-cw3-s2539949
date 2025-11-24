import math
import heapq

from typing import Dict, List, Set, Tuple

from src.dto.geo.lnglat import LngLat
from src.dto.geo.angle import Angle
from src.dto.pathfinding.node import Node
from src.dto.pathfinding.path_result import PathResult

class NavService:
    CLOSE_THRESHOLD = 0.00015
    MOVE_SIZE = 0.00015
    SNAP = 1e-4

    VALID_DIRS = [
        0.0, 22.5, 45.0, 67.5,
        90.0, 112.5, 135.0, 157.5,
        180.0, 202.5, 225.0, 247.5,
        270.0, 292.5, 315.0, 337.5,
    ]

    @staticmethod
    def distance(p1: LngLat, p2: LngLat) -> float:
        dx = p2.lng - p1.lng
        dy = p2.lat - p1.lat
        return math.sqrt(dx * dx + dy * dy)

    @staticmethod
    def isClose(p1: LngLat, p2: LngLat) -> bool:
        return NavService.distance(p1, p2) < NavService.CLOSE_THRESHOLD

    @staticmethod
    def nextPos(startPos: LngLat, angle: Angle) -> LngLat:
        rad = angle.radians()
        dx = NavService.MOVE_SIZE * math.cos(rad)
        dy = NavService.MOVE_SIZE * math.sin(rad)
        return LngLat(lng=startPos.lng + dx, lat=startPos.lat + dy)

    @staticmethod
    def reconstructPath(targetNode: Node) -> PathResult:
        path: List[LngLat] = []
        node: Node | None = targetNode

        while node is not None:
            path.append(node.position)
            node = node.parent

        path.reverse()
        return PathResult(path=path, moves=len(path) - 1)

    @staticmethod
    def heuristic(startPos: LngLat, targetPos: LngLat) -> float:
        return NavService.distance(startPos, targetPos)

    @staticmethod
    def shortestPath(startPos: LngLat, targetPos: LngLat) -> PathResult:
        # heap elements: (f, -g, counter, node)
        heap: List[Tuple[float, float, int, Node]] = []
        counter = 0

        best: Dict[Tuple[float, float], float] = {}
        visited: Set[Tuple[float, float]] = set()

        startG = 0.0
        startH = NavService.heuristic(startPos, targetPos)

        startNode = Node(
            position=startPos,
            distanceTravelled=startG,
            distanceLeft=startH,
            parent=None,
        )

        startKey = NavService.key(startPos)
        best[startKey] = startG
        f0 = startG + startH

        heapq.heappush(heap, (f0, -startG, counter, startNode))
        counter += 1

        while heap:
            _, _, _, cur = heapq.heappop(heap)

            curKey = NavService.key(cur.position)
            if curKey in visited: continue
            visited.add(curKey)

            if NavService.isClose(cur.position, targetPos):
                return NavService.reconstructPath(cur)

            for dir in NavService.VALID_DIRS:
                nextPos = NavService.nextPos(cur.position, Angle(dir))

                # no immediate backtracking
                if cur.parent is not None:
                    parent_pos = cur.parent.position
                    if nextPos.lng == parent_pos.lng and nextPos.lat == parent_pos.lat:
                        continue

                step = NavService.distance(cur.position, nextPos)
                g = cur.distanceTravelled + step

                nextKey = NavService.key(nextPos)
                seen = best.get(nextKey)
                if seen is not None and g >= seen:
                    continue

                h = NavService.heuristic(nextPos, targetPos)
                f = g + h

                nextNode = Node(
                    position=nextPos,
                    distanceTravelled=g,
                    distanceLeft=h,
                    parent=cur,
                )

                heapq.heappush(heap, (f, -g, counter, nextNode))
                counter += 1

                best[nextKey] = g

        return PathResult(moves=[], steps=0)
    
    @staticmethod
    def key(position: LngLat) -> tuple[int, int]:
        return (
            int(round(position.lng / NavService.SNAP)),
            int(round(position.lat / NavService.SNAP)),
        )