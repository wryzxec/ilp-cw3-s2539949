import json
from pathlib import Path
from typing import List

from src.dto.drone.drone import Drone
from src.dto.drone.request import Request
from src.dto.drone.service_point import ServicePoint
from src.dto.pathfinding.path_result import PathResult
from src.service.nav_service import NavService
from src.dto.geo.lnglat import LngLat

class DroneService:

    @staticmethod
    def dronePath(start: LngLat, target: LngLat) -> PathResult:
        return NavService.shortestPath(start, target)

    @staticmethod
    def multiRequestPath(servicePoint: ServicePoint, requests: List[Request]) -> List[PathResult]:
        paths: List[PathResult] = []
        currPos: LngLat = servicePoint.location
        remaining: List[Request] = list(requests)

        while remaining:
            closest_req, _ = min(
                (
                    (req, NavService.distance(currPos, req.position))
                    for req in remaining
                ),
                key=lambda t: t[1],
            )

            path = DroneService.dronePath(currPos, closest_req.position)
            paths.append(path)

            currPos = closest_req.position
            remaining.remove(closest_req)

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
                        "to": req.id,
                        "moves": segment.moves,
                        "droneId": drone.id,
                    },
                    "geometry": {
                        "type": "LineString",
                        "coordinates": coords,
                    },
                }
            )

        features.append(
            {
                "type": "Feature",
                "properties": {
                    "kind": "stop",
                    "stopType": "servicePoint",
                    "id": servicePoint.name,
                    "index": 0,
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [
                        servicePoint.location.lng,
                        servicePoint.location.lat,
                    ],
                },
            }
        )

        for i, req in enumerate(requests, start=1):
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
    def write_multi_requests_geojson_to_file(drone: Drone, service_point: ServicePoint, requests: list[Request],
                                             paths: list[PathResult], output_file: str = "static/path.geojson") -> None:
        geojson = DroneService.multiRequestsAsGeoJson(drone=drone, servicePoint=service_point, requests=requests, paths=paths)

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with output_path.open("w", encoding="utf-8") as f:
            json.dump(geojson, f)