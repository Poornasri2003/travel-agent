from pydantic import BaseModel, Field


class TourOperator(BaseModel):
    name: str
    website_url: str
    phone: str | None = None
    email: str | None = None
    description: str | None = None


class TourGuideInfo(BaseModel):
    best_time_to_visit: str | None = None
    local_tips: list[str] = Field(default_factory=list)
    food_and_drinks: str | None = None
    safety_and_transport: str | None = None
    cultural_notes: str | None = None


class TripRequest(BaseModel):
    from_city: str = Field(min_length=2, max_length=80)
    to_city: str = Field(min_length=2, max_length=80)
    from_state: str | None = Field(default=None, max_length=80, description="State/region for better site selection")
    to_state: str | None = Field(default=None, max_length=80, description="State/region for better site selection")
    trip_days: int = Field(ge=1, le=14)
    max_budget_inr: int = Field(ge=1000, le=200000)
    travelers: int = Field(default=1, ge=1, le=10)
    start_date: str | None = Field(default=None, description="YYYY-MM-DD")
    preferences: str | None = Field(default=None, max_length=300)


class FlightOption(BaseModel):
    source: str
    title: str
    price_inr: int | None = None
    departure_time: str | None = None
    arrival_time: str | None = None
    booking_url: str
    cabin_class: str | None = None
    stops_info: str | None = None
    seats_available: str | None = None
    availability_status: str | None = None


class HotelOption(BaseModel):
    source: str
    name: str
    price_per_night_inr: int | None = None
    locality: str | None = None
    booking_url: str
    rooms_note: str | None = None
    availability_status: str | None = None


class BusOption(BaseModel):
    source: str
    title: str
    price_inr: int | None = None
    duration: str | None = None
    departure_time: str | None = None
    arrival_time: str | None = None
    booking_url: str
    coach_type: str | None = None
    seats_available: str | None = None
    availability_status: str | None = None


class TrainOption(BaseModel):
    source: str
    title: str
    train_number: str | None = None
    price_inr: int | None = None
    duration: str | None = None
    departure_time: str | None = None
    arrival_time: str | None = None
    class_type: str | None = None
    seats_available: str | None = None
    availability_status: str | None = None
    waitlist_info: str | None = None
    booking_url: str


class DayPlan(BaseModel):
    day: int
    title: str
    details: str
    attractions: list[str] = Field(default_factory=list)


class TripResponse(BaseModel):
    run_id: str | None = None
    created_at: str | None = None
    tinyfish_automation_run_id: str | None = None
    destination_image_url: str | None = None
    destination_image_attribution: str | None = None
    summary: str
    flights: list[FlightOption]
    hotels: list[HotelOption]
    buses: list[BusOption]
    trains: list[TrainOption]
    itinerary: list[DayPlan]
    tour_guide: TourGuideInfo | None = None
    tour_operators: list[TourOperator] = Field(default_factory=list)
    recommended_flight: FlightOption | None = None
    recommended_hotel: HotelOption | None = None
    score_breakdown: dict[str, int] | None = None
    estimated_total_inr: int | None = None
    within_budget: bool | None = None
    evidence_urls: list[str] = Field(default_factory=list)
    raw_agent_response: dict | list | str | None = None
