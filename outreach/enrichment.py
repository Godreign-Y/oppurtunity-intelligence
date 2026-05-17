"""Enrichment module for finding key decision makers.

This module provides functionality to enrich job opportunities by querying
the Hunter API to find decision makers for a given company domain.
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

from schemas import DecisionMaker

# Load environment variables
load_dotenv()

HUNTER_API_KEY: str = os.getenv("HUNTER_API_KEY", "")

async def find_decision_makers(domain: str, target_departments: list[str]) -> list[DecisionMaker]:
    """Finds key decision makers for a given company domain using the Hunter API.

    Args:
        domain (str): The domain of the company (e.g., "example.com").
        target_departments (list[str]): A list of target departments to search for.

    Returns:
        list[DecisionMaker]: A list of DecisionMaker objects if successful, 
                             or an empty list if the API call fails.
    """
    if not HUNTER_API_KEY:
        print("Warning: HUNTER_API_KEY is not set.")
        return []

    url: str = "https://api.hunter.io/v2/domain-search"
    
    # Use the first department provided
    department: str = target_departments[0] if target_departments else ""
    
    params: dict = {
        "domain": domain,
        "department": department,
        "api_key": HUNTER_API_KEY,
        "limit": 2
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            emails = data.get("data", {}).get("emails", [])
            
            decision_makers: list[DecisionMaker] = []
            for item in emails:
                dm = DecisionMaker(
                    first_name=item.get("first_name"),
                    last_name=item.get("last_name"),
                    title=item.get("position"),
                    email=item.get("value")
                )
                decision_makers.append(dm)
                
            return decision_makers
            
    except httpx.HTTPStatusError as e:
        print(f"Hunter API returned an error for domain {domain}: {e}")
        print(f"Hunter API Error Details: {e.response.text}")
        return []
    except Exception as e:
        print(f"Failed to fetch decision makers for domain {domain}: {e}")
        return []
