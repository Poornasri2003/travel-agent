from __future__ import annotations

from typing import Any

import httpx

STATES_FALLBACK = [
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Chhattisgarh",
    "Goa",
    "Gujarat",
    "Haryana",
    "Himachal Pradesh",
    "Jharkhand",
    "Karnataka",
    "Kerala",
    "Madhya Pradesh",
    "Maharashtra",
    "Manipur",
    "Meghalaya",
    "Mizoram",
    "Nagaland",
    "Odisha",
    "Punjab",
    "Rajasthan",
    "Sikkim",
    "Tamil Nadu",
    "Telangana",
    "Tripura",
    "Uttar Pradesh",
    "Uttarakhand",
    "West Bengal",
    "Andaman and Nicobar Islands",
    "Chandigarh",
    "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi",
    "Jammu and Kashmir",
    "Ladakh",
    "Lakshadweep",
    "Puducherry",
]

CITIES_FALLBACK: dict[str, list[str]] = {
    "Karnataka": ["Bengaluru", "Mysuru", "Mangaluru", "Hubballi", "Belagavi"],
    "Goa": ["Panaji", "Margao", "Vasco da Gama", "Calangute", "Anjuna"],
    "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Nashik", "Aurangabad"],
    "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli"],
    "Kerala": ["Kochi", "Thiruvananthapuram", "Kozhikode"],
    "Delhi": ["New Delhi"],
}


def fetch_india_states() -> list[str]:
    timeout = httpx.Timeout(20.0)
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(
                "https://countriesnow.space/api/v0.1/countries/states",
                json={"country": "India"},
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()
    except (httpx.HTTPError, ValueError):
        return sorted(STATES_FALLBACK)

    if not data.get("data", {}).get("states"):
        return sorted(STATES_FALLBACK)

    names: list[str] = []
    for item in data["data"]["states"]:
        name = item.get("name")
        if isinstance(name, str) and name.strip():
            names.append(name.strip())
    return sorted(set(names)) if names else sorted(STATES_FALLBACK)


def fetch_state_cities(state: str) -> list[str]:
    state_clean = state.strip()
    if not state_clean:
        return []

    timeout = httpx.Timeout(20.0)
    try:
        with httpx.Client(timeout=timeout) as client:
            response = client.post(
                "https://countriesnow.space/api/v0.1/countries/state/cities",
                json={"country": "India", "state": state_clean},
            )
            response.raise_for_status()
            data: dict[str, Any] = response.json()
    except (httpx.HTTPError, ValueError):
        return sorted(CITIES_FALLBACK.get(state_clean, []))

    cities = data.get("data", [])
    if not isinstance(cities, list):
        return sorted(CITIES_FALLBACK.get(state_clean, []))

    names = [str(c).strip() for c in cities if isinstance(c, str) and str(c).strip()]
    if not names:
        return sorted(CITIES_FALLBACK.get(state_clean, []))
    names = sorted(set(names))[:120]
    return names
