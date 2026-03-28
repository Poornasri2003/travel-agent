from __future__ import annotations

import re
import json
from typing import Any

from .models import (
    BusOption,
    DayPlan,
    FlightOption,
    HotelOption,
    TourGuideInfo,
    TourOperator,
    TrainOption,
    TripRequest,
    TripResponse,
)


# Starting URL used to begin web browsing. Results must be discovered by the agent live.
START_URL = "https://www.makemytrip.com/"


def build_agent_payload(req: TripRequest) -> dict[str, Any]:
    trip_summary = (
        f"Plan a {req.trip_days}-day trip from {req.from_city} to {req.to_city} "
        f"for {req.travelers} traveler(s) under INR {req.max_budget_inr}."
    )
    if req.from_state:
        trip_summary += f" From state/region: {req.from_state}."
    if req.to_state:
        trip_summary += f" To state/region: {req.to_state}."
    if req.start_date:
        trip_summary += f" Start date is {req.start_date}."
    if req.preferences:
        trip_summary += f" Preferences: {req.preferences}."

    goal = (
        f"{trip_summary}\n\n"
        "Use live web browsing starting from the provided page, and navigate to multiple sites as needed to: "
        "1) find flight options for the given route and dates (if dates provided), "
        "2) find budget hotel options for the trip, "
        "3) find bus options for the route, "
        "4) find train options where applicable (IRCTC or authorized rail aggregators; include train number/class if visible), "
        "5) recommend tourist places/day activities aligned with the itinerary, "
        "6) estimate total cost and whether it fits the budget, "
        "7) create a day-wise itinerary,\n"
        "8) add practical tour-guide information from live pages,\n"
        "9) find 2-4 real tour operators or DMCs that sell end-to-end packages for this destination; include official website URL and phone/email only if shown on a live page you visited.\n\n"
        "For every flight, bus, train, and hotel: booking_url MUST be a full https URL. "
        "Critical for trains/flights/buses: do NOT return only the site's homepage or an empty search form. "
        "On the booking site, enter the user's exact from_city and to_city (and journey date if provided), submit search, "
        "then copy the browser address bar URL after results load—that URL should encode origin, destination, and often date. "
        "If the site keeps form state in session only and the URL stays generic, use the best results-page URL you have and note it in availability_status. "
        "Hotel booking_url should be the property or search URL for the destination city, not only the global homepage. "
        "If the site shows seat/berth counts, waitlist, or availability text, copy it into seats_available and availability_status; use null if not shown (never invent numbers).\n\n"
        "Return ONLY valid JSON with exactly these keys:\n"
        "{\n"
        '  "summary": string,\n'
        '  "flights": [\n'
        "    {\n"
        '      "source": string,\n'
        '      "title": string,\n'
        '      "price_inr": number | null,\n'
        '      "departure_time": string | null,\n'
        '      "arrival_time": string | null,\n'
        '      "cabin_class": string | null,\n'
        '      "stops_info": string | null,\n'
        '      "seats_available": string | null,\n'
        '      "availability_status": string | null,\n'
        '      "booking_url": string\n'
        "    }\n"
        "  ],\n"
        '  "hotels": [\n'
        "    {\n"
        '      "source": string,\n'
        '      "name": string,\n'
        '      "price_per_night_inr": number | null,\n'
        '      "locality": string | null,\n'
        '      "rooms_note": string | null,\n'
        '      "availability_status": string | null,\n'
        '      "booking_url": string\n'
        "    }\n"
        "  ],\n"
        '  "buses": [\n'
        "    {\n"
        '      "source": string,\n'
        '      "title": string,\n'
        '      "price_inr": number | null,\n'
        '      "duration": string | null,\n'
        '      "departure_time": string | null,\n'
        '      "arrival_time": string | null,\n'
        '      "coach_type": string | null,\n'
        '      "seats_available": string | null,\n'
        '      "availability_status": string | null,\n'
        '      "booking_url": string\n'
        "    }\n"
        "  ],\n"
        '  "trains": [\n'
        "    {\n"
        '      "source": string,\n'
        '      "title": string,\n'
        '      "train_number": string | null,\n'
        '      "price_inr": number | null,\n'
        '      "duration": string | null,\n'
        '      "departure_time": string | null,\n'
        '      "arrival_time": string | null,\n'
        '      "class_type": string | null,\n'
        '      "seats_available": string | null,\n'
        '      "availability_status": string | null,\n'
        '      "waitlist_info": string | null,\n'
        '      "booking_url": string\n'
        "    }\n"
        "  ],\n"
        '  "itinerary": [\n'
        "    {\n"
        '      "day": number,\n'
        '      "title": string,\n'
        '      "details": string,\n'
        '      "attractions": [string]\n'
        "    }\n"
        "  ],\n"
        '  "estimated_total_inr": number | null,\n'
        '  "within_budget": boolean | null,\n'
        '  "evidence_urls": [string],\n'
        '  "tour_guide": {\n'
        '    "best_time_to_visit": string,\n'
        '    "local_tips": [string],\n'
        '    "food_and_drinks": string,\n'
        '    "safety_and_transport": string,\n'
        '    "cultural_notes": string\n'
        "  },\n"
        '  "tour_operators": [\n'
        "    {\n"
        '      "name": string,\n'
        '      "website_url": string,\n'
        '      "phone": string | null,\n'
        '      "email": string | null,\n'
        '      "description": string | null\n'
        "    }\n"
        "  ]\n"
        "}\n"
    )

    return {"url": START_URL, "goal": goal}


def _parse_int(value: Any) -> int | None:
    if value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return int(value)
    if isinstance(value, str):
        digits = re.sub(r"[^\d]", "", value)
        if digits:
            return int(digits)
    return None


def _first_present(source: dict, keys: list[str], default: Any = None) -> Any:
    for key in keys:
        if key in source and source[key] is not None:
            return source[key]
    return default


def _normalize_payload_data(raw: dict | list | str) -> dict[str, Any]:
    if isinstance(raw, dict):
        result = raw.get("result")
        if isinstance(result, dict):
            return result
        if isinstance(result, str):
            text = result.strip()
            if text.startswith("```"):
                text = text.strip("`")
                if text.lower().startswith("json"):
                    text = text[4:].strip()
            try:
                parsed = json.loads(text)
                if isinstance(parsed, dict):
                    return parsed
            except ValueError:
                return {"summary": text}
        return raw

    if isinstance(raw, str):
        text = raw.strip()
        if text.startswith("```"):
            text = text.strip("`")
            if text.lower().startswith("json"):
                text = text[4:].strip()
        try:
            parsed = json.loads(text)
            if isinstance(parsed, dict):
                return parsed
        except ValueError:
            return {"summary": text}
        return {"summary": text}

    return {"summary": "Agent returned list response.", "raw": raw}


def _pick_recommended_flight(flights: list[FlightOption]) -> FlightOption | None:
    priced = [flight for flight in flights if flight.price_inr is not None]
    if priced:
        return sorted(priced, key=lambda item: item.price_inr)[0]
    return flights[0] if flights else None


def _pick_recommended_hotel(hotels: list[HotelOption]) -> HotelOption | None:
    priced = [hotel for hotel in hotels if hotel.price_per_night_inr is not None]
    if priced:
        return sorted(priced, key=lambda item: item.price_per_night_inr)[0]
    return hotels[0] if hotels else None


def _parse_tour_guide(data: dict[str, Any]) -> TourGuideInfo | None:
    raw = _first_present(data, ["tour_guide", "guide", "tourGuide"], None)
    if not isinstance(raw, dict):
        return None

    tips_raw = _first_present(raw, ["local_tips", "tips", "practical_tips"], [])
    tips: list[str] = []
    if isinstance(tips_raw, list):
        tips = [str(x) for x in tips_raw if isinstance(x, str) and x.strip()]
    elif isinstance(tips_raw, str) and tips_raw.strip():
        tips = [tips_raw.strip()]

    guide = TourGuideInfo(
        best_time_to_visit=_first_present(raw, ["best_time_to_visit", "best_time", "best_months"]),
        local_tips=tips,
        food_and_drinks=_first_present(raw, ["food_and_drinks", "food", "eat"]),
        safety_and_transport=_first_present(raw, ["safety_and_transport", "safety", "transport"]),
        cultural_notes=_first_present(raw, ["cultural_notes", "etiquette", "culture"]),
    )
    if not (
        guide.best_time_to_visit
        or guide.local_tips
        or guide.food_and_drinks
        or guide.safety_and_transport
        or guide.cultural_notes
    ):
        return None
    return guide


def _parse_tour_operators(data: dict[str, Any]) -> list[TourOperator]:
    raw = _first_present(data, ["tour_operators", "tourOperators", "dmc_operators"], [])
    if not isinstance(raw, list):
        return []
    operators: list[TourOperator] = []
    for item in raw:
        if not isinstance(item, dict):
            continue
        name = str(_first_present(item, ["name", "company", "operator"], "")).strip()
        website = str(_first_present(item, ["website_url", "website", "url", "site"], "")).strip()
        if not name or not website:
            continue
        operators.append(
            TourOperator(
                name=name,
                website_url=website,
                phone=_first_present(item, ["phone", "contact_phone", "mobile"]),
                email=_first_present(item, ["email", "contact_email"]),
                description=_first_present(item, ["description", "about", "services"]),
            )
        )
    return operators


def _score_response(
    flights: list[FlightOption],
    hotels: list[HotelOption],
    buses: list[BusOption],
    trains: list[TrainOption],
    within_budget: bool | None,
) -> dict[str, int]:
    coverage_score = min(
        55,
        len(flights) * 8 + len(hotels) * 8 + len(buses) * 8 + len(trains) * 8,
    )
    modes = sum(1 for group in (flights, hotels, buses, trains) if group)
    evidence_score = 28 if modes >= 4 else 18 if modes >= 2 else 10 if modes >= 1 else 0
    budget_score = 40 if within_budget is True else 20 if within_budget is None else 5
    return {
        "coverage_score": coverage_score,
        "evidence_score": evidence_score,
        "budget_score": budget_score,
        "total_score": coverage_score + evidence_score + budget_score,
    }


def normalize_agent_response(raw: dict | list | str, budget: int) -> TripResponse:
    data = _normalize_payload_data(raw)

    flights_raw = _first_present(data, ["flights", "flight_options", "results_flights"], [])
    hotels_raw = _first_present(data, ["hotels", "hotel_options", "results_hotels"], [])
    buses_raw = _first_present(data, ["buses", "bus_options", "results_buses"], [])
    trains_raw = _first_present(data, ["trains", "train_options", "rail_options", "results_trains"], [])
    itinerary_raw = _first_present(data, ["itinerary", "day_plan", "plan"], [])

    flights: list[FlightOption] = []
    for item in flights_raw if isinstance(flights_raw, list) else []:
        if not isinstance(item, dict):
            continue
        booking_url = str(_first_present(item, ["booking_url", "url", "link"], "")).strip()
        if not booking_url:
            continue
        flights.append(
            FlightOption(
                source=str(_first_present(item, ["source", "site"], "unknown")),
                title=str(_first_present(item, ["title", "name"], "Flight option")),
                price_inr=_parse_int(_first_present(item, ["price_inr", "price", "fare"])),
                departure_time=_first_present(item, ["departure_time", "departure"]),
                arrival_time=_first_present(item, ["arrival_time", "arrival"]),
                booking_url=booking_url,
                cabin_class=_first_present(item, ["cabin_class", "class", "cabin"]),
                stops_info=_first_present(item, ["stops_info", "stops", "route_stops"]),
                seats_available=_first_present(item, ["seats_available", "seats", "seats_left"]),
                availability_status=_first_present(
                    item, ["availability_status", "availability", "status"]
                ),
            )
        )

    hotels: list[HotelOption] = []
    for item in hotels_raw if isinstance(hotels_raw, list) else []:
        if not isinstance(item, dict):
            continue
        booking_url = str(_first_present(item, ["booking_url", "url", "link"], "")).strip()
        if not booking_url:
            continue
        hotels.append(
            HotelOption(
                source=str(_first_present(item, ["source", "site"], "unknown")),
                name=str(_first_present(item, ["name", "title"], "Hotel option")),
                price_per_night_inr=_parse_int(
                    _first_present(item, ["price_per_night_inr", "price_per_night", "price"])
                ),
                locality=_first_present(item, ["locality", "location", "area"]),
                booking_url=booking_url,
                rooms_note=_first_present(item, ["rooms_note", "rooms", "room_types"]),
                availability_status=_first_present(
                    item, ["availability_status", "availability", "sold_out"]
                ),
            )
        )

    buses: list[BusOption] = []
    for item in buses_raw if isinstance(buses_raw, list) else []:
        if not isinstance(item, dict):
            continue
        booking_url = str(_first_present(item, ["booking_url", "url", "link"], "")).strip()
        if not booking_url:
            continue
        buses.append(
            BusOption(
                source=str(_first_present(item, ["source", "site"], "unknown")),
                title=str(_first_present(item, ["title", "name"], "Bus option")),
                price_inr=_parse_int(_first_present(item, ["price_inr", "price", "fare"])),
                duration=_first_present(item, ["duration", "travel_time"]),
                departure_time=_first_present(item, ["departure_time", "departure"]),
                arrival_time=_first_present(item, ["arrival_time", "arrival"]),
                booking_url=booking_url,
                coach_type=_first_present(item, ["coach_type", "bus_type", "type"]),
                seats_available=_first_present(item, ["seats_available", "seats", "berths"]),
                availability_status=_first_present(
                    item, ["availability_status", "availability", "status"]
                ),
            )
        )

    trains: list[TrainOption] = []
    for item in trains_raw if isinstance(trains_raw, list) else []:
        if not isinstance(item, dict):
            continue
        booking_url = str(_first_present(item, ["booking_url", "url", "link"], "")).strip()
        if not booking_url:
            continue
        trains.append(
            TrainOption(
                source=str(_first_present(item, ["source", "site"], "unknown")),
                title=str(_first_present(item, ["title", "name", "train_name"], "Train option")),
                train_number=_first_present(item, ["train_number", "number", "train_no"]),
                price_inr=_parse_int(_first_present(item, ["price_inr", "price", "fare"])),
                duration=_first_present(item, ["duration", "travel_time"]),
                departure_time=_first_present(item, ["departure_time", "departure"]),
                arrival_time=_first_present(item, ["arrival_time", "arrival"]),
                class_type=_first_present(item, ["class_type", "class", "travel_class"]),
                seats_available=_first_present(item, ["seats_available", "seats", "berths"]),
                availability_status=_first_present(
                    item, ["availability_status", "availability", "status"]
                ),
                waitlist_info=_first_present(item, ["waitlist_info", "waitlist", "wl"]),
                booking_url=booking_url,
            )
        )

    itinerary: list[DayPlan] = []
    for idx, item in enumerate(itinerary_raw if isinstance(itinerary_raw, list) else [], start=1):
        if isinstance(item, dict):
            attractions_raw = _first_present(item, ["attractions", "tourist_places", "places"], [])
            attractions: list[str] = []
            if isinstance(attractions_raw, list):
                attractions = [str(x) for x in attractions_raw if isinstance(x, str)]
            itinerary.append(
                DayPlan(
                    day=int(_first_present(item, ["day"], idx)),
                    title=str(_first_present(item, ["title"], f"Day {idx}")),
                    details=str(_first_present(item, ["details", "description"], "")),
                    attractions=attractions,
                )
            )
        elif isinstance(item, str):
            itinerary.append(DayPlan(day=idx, title=f"Day {idx}", details=item, attractions=[]))

    estimated_total = _parse_int(_first_present(data, ["estimated_total_inr", "total_cost", "estimated_total"]))
    within_budget = _first_present(data, ["within_budget"], None)
    if within_budget is None and estimated_total is not None:
        within_budget = estimated_total <= budget

    evidence_urls = _first_present(data, ["evidence_urls", "sources", "links"], [])
    if not isinstance(evidence_urls, list):
        evidence_urls = []

    recommended_flight = _pick_recommended_flight(flights)
    recommended_hotel = _pick_recommended_hotel(hotels)
    score_breakdown = _score_response(flights, hotels, buses, trains, within_budget)
    tour_guide = _parse_tour_guide(data)
    tour_operators = _parse_tour_operators(data)

    return TripResponse(
        summary=str(_first_present(data, ["summary", "message"], "Trip plan created.")),
        flights=flights,
        hotels=hotels,
        buses=buses,
        trains=trains,
        itinerary=itinerary,
        tour_guide=tour_guide,
        tour_operators=tour_operators,
        recommended_flight=recommended_flight,
        recommended_hotel=recommended_hotel,
        score_breakdown=score_breakdown,
        estimated_total_inr=estimated_total,
        within_budget=within_budget,
        evidence_urls=[str(url) for url in evidence_urls if isinstance(url, str)],
        raw_agent_response=raw,
    )
