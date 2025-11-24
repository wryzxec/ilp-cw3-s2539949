from typing import List
from fastapi import APIRouter

from src.dto.drone.drone import Drone
from src.dto.drone.request import Request
from src.dto.drone.service_point import ServicePoint
from src.dto.geo.lnglat import LngLat

from src.service.nav_service import NavService
from src.service.drone_service import DroneService
from src.service.endpoint_service import EndpointService

router = APIRouter(
    prefix="/api/drones",
)

DUMMY_DRONES = [
    Drone(id="1", name="alpha"),
    Drone(id="2", name="beta"),
]

@router.get("/", response_model=list[Drone])
def list_drones():
    return DUMMY_DRONES

@router.get("/{drone_id}", response_model=Drone | None)
def get_drone(drone_id: str):
    for d in DUMMY_DRONES:
        if d.id == drone_id:
            return d
    return None

@router.post("/calcDeliveryPath")
def calcDeliveryPath(requests: List[Request]):
    print("Hello World!")
    startPos = LngLat(lng=-3.189, lat=55.941)
    targetPos = requests[0].position
    return NavService.shortestPath(startPos, targetPos)

@router.post("/calcDeliveryPathAsGeoJson")
def calcDeliveryPathAsGeoJson(requests: List[Request]):
    drones = EndpointService.fetchDrones()
    servicePoints = EndpointService.fetchServicePoints()

    drone = drones[0]
    servicePoint = servicePoints[0]

    paths = DroneService.multiRequestPath(servicePoint, requests)
    geojson = DroneService.multiRequestsAsGeoJson(drone, servicePoint, requests, paths)
    DroneService.write_multi_requests_geojson_to_file(drone, servicePoint, requests, paths)
    DroneService.draw_service_point_on_map(servicePoints)
    return geojson