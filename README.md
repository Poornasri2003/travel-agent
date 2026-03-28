# Autonomous Travel Planning & Booking Agent

## Project Description
An intelligent travel coordination tool that uses the **TinyFish Web Agent API** to autonomously search live travel sites (flights, hotels, buses, trains). It negotiates dynamic booking UIs, compares prices against a firm budget, and returns a verified, bookable itinerary with explicit evidence links—automatically exportable as a professional PDF manifest.

## The Core Idea
Travel planning represents a massive operational bottleneck for both consumers and enterprise travel desks. Users spend hours manually cross-referencing flights, hotels, and local transit across multiple fragmented vendor sites to ensure their trip fits a strict budget. 

This project solves that by delegating the heavy lifting to autonomous web agents. Instead of relying on static APIs (which represent stale data and limited inventory), this tool actively navigates consumer-facing web surfaces just like a human would. It extracts live pricing and availability directly from the UI, orchestrates multi-step queries (e.g., searching flights and matching hotel dates simultaneously), and consolidates the results based on complex budget and timeline constraints.

## Architecture

```text
Browser (Sleek UI Dashboard)
  → FastAPI (Orchestration Engine)
      → TinyFish Web Agent API (Live browser automation on external vendor sites)
      → Wikipedia API (Dynamic imaging context)
      → CountriesNow API (Interactive geography helpers)
```

**Data Integrity Note:** All prices, booking URLs, and availability statuses are guaranteed live by the TinyFish agent interacting directly with the web in real-time. This entirely prevents hallucinated pricing and availability.

## What's New & The Thought Process
- **Live Action over Text Generation**: Unlike typical AI travel planners that generate text-based ideas from a frozen dataset, this project acts as an operational agent that performs real-world search flows.
- **Fail-safe Multi-Modal Transport**: If flights are prohibitively expensive for a requested budget, the agent's logic automatically pivots to checking trains or buses without requiring additional manual prompting.
- **Full-Screen Interaction Loader**: Wait screens and loaders explicitly map what the backend agent is doing ("Consulting local travel guides...", "Finding flight routes...") to keep the user looped into the execution state.
- **One-Click Itinerary Export**: Users can easily save the end-to-end trip manifest as a clean, offline-ready PDF to share with managers, families, or clients.
- **Structured Data Normalization**: Pydantic models automatically sanitize messy web agent logs into deterministic, predictable JSON blocks for the frontend UI.

---

## 🚀 Setup & Execution (How to Run Locally)

### 1. Prerequisites
- Python 3.11+ is highly recommended.

### 2. Set up Virtual Environment
```bash
cd travel-agent
python -m venv .venv

# Windows:
.venv\Scripts\activate

# macOS / Linux:
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Copy `.env.template` to a new `.env` file in the root directory (where `main.py` is called) and provide your API keys:
```env
TINYFISH_API_KEY=sk-tinyfish-...
TINYFISH_BASE_URL=https://agent.tinyfish.ai/v1
TINYFISH_RUN_PATH=/automation/run
REQUEST_TIMEOUT_SECONDS=180
```

### 5. Run the FastAPI Server
```bash
uvicorn app.main:app --reload
```

### 6. Access the App
Open `http://127.0.0.1:8000` in your web browser to start planning trips.
