import requests

from src.dto.drone.drone import Drone
from src.dto.drone.service_point import ServicePoint

class EndpointService:
    ILP_URL = "https://ilp-rest-2025-bvh6e9hschfagrgy.ukwest-01.azurewebsites.net/"

    @staticmethod
    def _get(specifier: str):
        url = EndpointService.ILP_URL + specifier
        resp = requests.get(url,timeout=10)
        resp.raise_for_status()
        return resp.json()

    @staticmethod
    def fetchDrones():
        data = EndpointService._get("/drones")
        return [Drone(**item) for item in data]
    
    @staticmethod
    def fetchServicePoints():
        data = EndpointService._get("/service-points")
        return [ServicePoint.model_validate(item) for item in data]