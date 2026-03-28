# Autonomous Travel Planning & Booking Agent

An intelligent travel coordination tool that uses the **TinyFish Web Agent API** to autonomously search live travel sites (flights, hotels, buses, trains). It negotiates dynamic booking UIs, compares prices against a firm budget, and returns a verified, bookable itinerary with explicit evidence links—exportable as a clean PDF.

## Why this fits the TinyFish Agentic Web Hackathon

| Criterion | How this project satisfies it |
|-----------|-------------------------------|
| **Real web agent work** | Calls `POST https://agent.tinyfish.ai/v1/automation/run` to perform deeply authenticated, live navigation across dynamic travel UIs. |
| **Multi-step / complex web** | Handles search flows on consumer portals without static APIs (e.g., MakeMyTrip, RedBus). |
| **Not a thin chat wrapper** | Built as an operational coordinator with live retrieval, data normalization, ranking, and UI parsing. No simple LLM text-chat. |
| **Business value** | Transforms hours of manual, frustrating tab-switching into a unified, one-click B2B or B2C travel planning flow. |

## Architecture Overview

```
Browser (Sleek UI Dashboard)
  → FastAPI (Orchestration Engine)
      → TinyFish Web Agent API (Live execution on external sites)
      → Wikipedia API (Dynamic hero images for destination)
      → CountriesNow API (Free UI helper for geography data)
```

**Note:** All prices, booking URLs, and availability statuses are guaranteed live by the TinyFish agent interacting directly with the web, preventing hallucination.

## Features Built to Win
- **Full-Screen Interaction Loader**: Dark overlays show exactly what the backend agent is doing ("Consulting local travel guides...", "Finding flight routes...") to keep the user engaged.
- **One-Click Itinerary Export**: Easily save your end-to-end trip manifest as a clean, offline-ready PDF to share with managers or family members.
- **Structured Data Normalization**: Pydantic models automatically sanitize messy web agent logs into deterministic JSON blocks.

---

## 🚀 Setup & Execution (How to Run Locally)

1. **Prerequisites**: Python 3.11+ is recommended.
2. **Set up Virtual Environment**:
   ```bash
   cd travel-agent
   python -m venv .venv
   
   # Windows:
   .venv\Scripts\activate
   
   # macOS / Linux:
   source .venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Environment Variables**:
   Create a `.env` file in the root directory (where `main.py` is called) and provide your TinyFish key:
   ```env
   TINYFISH_API_KEY=sk-tinyfish-...
   TINYFISH_BASE_URL=https://agent.tinyfish.ai/v1
   TINYFISH_RUN_PATH=/automation/run
   REQUEST_TIMEOUT_SECONDS=180
   ```
5. **Run the FastAPI Server**:
   ```bash
   uvicorn app.main:app --reload
   ```
6. **Access the App**:
   Open `http://127.0.0.1:8000` in your browser.

---

## API Reference

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/api/tinyfish/config` | Shows TinyFish base URL + whether a key is set. |
| `GET` | `/api/geography/states` | India states API wrapper (CountriesNow). |
| `POST` | `/api/geography/cities` | Cities for a state calculation. |
| `GET` | `/api/place-image` | Wikipedia hero thumbnail URL. |
| `POST` | `/api/plan` | Core endpoint: Builds payload, dispatches TinyFish agent, and normalizes output. |

## Winning Demo Script (2 minutes)

1. **State the Problem**: Explain how manual trip planning across 5+ sites is slow and painful.
2. **Execute on UI**: Pick **state + city + date + budget**, click **Search & plan**.
3. **Highlight the Wait Screen**: Show off the dynamic "Agentic Loader" parsing multiple steps in the background.
4. **Show Results**: Expand **Flights / Buses / Hotels** and open the live **Book** links the agent fetched. 
5. **Verify**: Point to **Evidence URLs** showing exactly which sites the agent securely navigated.
6. **Export**: Click the **"Export Itinerary (PDF)"** button to showcase its professional B2B/consumer value!
