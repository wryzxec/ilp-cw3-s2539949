import json
from pathlib import Path
from typing import List

from src.dto.drone.drone import Drone
from src.dto.drone.request import Request
from src.dto.drone.service_point import ServicePoint
from src.dto.pathfinding.path_result import PathResult
from src.service.nav_service import NavService
from src.service.llm_service import LLMService, LLMDecision
from src.dto.geo.lnglat import LngLat

class DroneService:
    @staticmethod
    def dronePath(start: LngLat, target: LngLat) -> PathResult:
        return NavService.shortestPath(start, target)

    @staticmethod
    def multiRequestPath(servicePoint: ServicePoint, requests: List[Request]) -> List[PathResult]:
        # let llm assign priority and medical items for each request
        # order requests by priority

        # hard code item storage for now
        itemStorage = ["epipen", "bandage", "insulin"]

        decisions: dict[str, LLMDecision] = {}

        for req in requests:
            llmDecision =  LLMService.parseEmergencyMessage(req, itemStorage)
            decisions[req.id] = llmDecision

            # debug
            priority = llmDecision.priority
            packageContents = llmDecision.items
            print(f"Request: {req.id}")
            print(f"priority: {priority}, packageContents: {packageContents}\n")

        # for now just choose the first service point
        paths: List[PathResult] = []
        currPos: LngLat = servicePoint.location
        remaining: List[Request] = list(requests)
        while remaining:
            maxPriority = max(decisions[req.id].priority for req in remaining)
            candidates = [req for req in remaining if decisions[req.id].priority == maxPriority]

            # if multiple requests have same priority, filter by distance
            closestReq, _ = min(
                (
                    (req, NavService.distance(currPos, req.position))
                    for req in candidates
                ),
                key=lambda t: t[1],
            )
            path = DroneService.dronePath(currPos, closestReq.position)
            paths.append(path)

            # move the drone there, remove the request from remaining
            currPos = closestReq.position
            remaining.remove(closestReq)

        returnPath = DroneService.dronePath(currPos, servicePoint.location)
        paths.append(returnPath)

        return paths

    @staticmethod
    def multiRequestsAsGeoJson(drone: Drone, servicePoint: ServicePoint, requests: List[Request],
                               paths: List[PathResult]) -> dict:
        features: List[dict] = []

        requests.append(Request(id="0", position=servicePoint.location, content=""))

        for idx, (req, segment) in enumerate(zip(requests, paths)):
            coords = [[p.lng, p.lat] for p in segment.path]

            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "kind": "segment",
                        "segmentIndex": idx,
                        "from": servicePoint.name if idx == 0 else requests[idx - 1].id,
                        "to": servicePoint.name if idx == len(requests)-1 else req.id,
                        "moves": segment.moves,
                        "droneId": drone.id,
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": coords,
                    },
                }
            )

        for i, req in enumerate(requests[:-2]):
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "kind": "stop",
                        "stopType": "request",
                        "id": req.id,
                        "index": i,
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            req.position.lng,
                            req.position.lat,
                        ],
                    },
                }
            )

        return {
            "type": "FeatureCollection",
            "features": features,
        }

    @staticmethod
    def write_multi_requests_geojson_to_file(drone: Drone, servicePoint: ServicePoint, requests: list[Request],
                                             paths: list[PathResult], output_file: str = "static/path.geojson") -> None:
        geojson = DroneService.multiRequestsAsGeoJson(drone=drone, servicePoint=servicePoint, requests=requests, paths=paths)

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(geojson, f)

    @staticmethod
    def draw_service_point_on_map(servicePoints: List[ServicePoint]) -> None:
        geojson = {
            "type": "FeatureCollection",
            "features": [
                {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [sp.location.lng, sp.location.lat],
                    },
                    "properties": {
                        "id": sp.id,
                        "name": sp.name,
                    },
                }
                for sp in servicePoints
            ],
        }

        output_path = Path("static/service_points.geojson")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(geojson, f)