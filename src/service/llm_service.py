import json
from typing import List
import requests

from pydantic import ValidationError

from src.dto.drone.llm_decision import LLMDecision

class LLMService:
    MODEL = "phi3"
    BASE_URL = "http://localhost:11434"
    @staticmethod
    def _generate(model, prompt: str) -> str:
        url = f"{LLMService.BASE_URL}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "format": "json"
        }
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()

        return data["response"]
    
    @staticmethod
    def parseEmergencyMessage(message: str, itemStorage: List[str]) -> LLMDecision:
        inventory_str = ", ".join(f'"{itemName}"' for itemName in itemStorage)

        # system prompt
        system = (
            "You are an on-call, emergency response assistant. "
            "You read emergency messages and decide a priority and a list of items to send. "
            "You MUST respond with ONLY valid JSON, no extra text, no backticks."
        )

        # user prompt
        user = f"""
                Emergency message:
                \"\"\"{message}\"\"\"

                Available items (this is the ONLY set of items you may choose from):
                [{inventory_str}]

                Your task:
                1. Assign a priority:
                - 1 = low urgency
                - 2 = medium urgency
                - 3 = high urgency
                2. Choose a list of item names from the available items that should be dispatched.

                Rules:
                - "items" must contain ONLY item names that appear in the provided list.
                - If no items are needed, return an empty list: [].
                - Respond with a single JSON object with EXACTLY these keys:
                - "priority": integer (1, 2, or 3)
                - "items": array of strings

                Example of a valid response:
                {{
                "priority": 3,
                "items": ["defibrillator", "oxygen_mask", "bandages"]
                }}
                """
        
        # execute prompt
        prompt = f"[SYSTEM]\n{system}\n[USER]\n{user}"
        raw = LLMService._generate(LLMService.MODEL, prompt)

        try:
            obj = json.loads(raw)
        except json.JSONDecodeError as e:
            raise ValueError(f"LLM did not return JSON: {e}\nRaw: {raw}") from e

        # schema validation
        try:
            decision = LLMDecision.model_validate(obj)
        except ValidationError as e:
            raise ValueError(f"LLM JSON did not match schema: {e}\nRaw: {raw}") from e
        
        allowed = set(itemStorage)
        filtered_items = [item for item in decision.items if item in allowed]
        
        return LLMDecision(priority=decision.priority, items=filtered_items)