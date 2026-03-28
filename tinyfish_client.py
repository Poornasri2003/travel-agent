import os
from dataclasses import dataclass

import httpx

from dotenv import load_dotenv


load_dotenv()


class TinyFishError(Exception):
    pass


@dataclass(frozen=True)
class TinyFishConfig:
    api_key: str
    base_url: str
    run_path: str
    timeout_seconds: int


def get_config() -> TinyFishConfig:
    api_key = os.getenv("TINYFISH_API_KEY", "").strip()
    if not api_key:
        raise TinyFishError("TINYFISH_API_KEY is missing in .env")

    base_url = os.getenv("TINYFISH_BASE_URL", "https://agent.tinyfish.ai/v1").strip().rstrip("/")
    run_path = os.getenv("TINYFISH_RUN_PATH", "/automation/run").strip()
    timeout_seconds = int(os.getenv("REQUEST_TIMEOUT_SECONDS", "90"))
    return TinyFishConfig(
        api_key=api_key,
        base_url=base_url,
        run_path=run_path,
        timeout_seconds=timeout_seconds,
    )


def run_agent(payload: dict) -> dict | list:
    config = get_config()
    url = f"{config.base_url}{config.run_path}"
    headers = {
        "X-API-Key": config.api_key,
        "Content-Type": "application/json",
    }

    timeout = httpx.Timeout(config.timeout_seconds)
    last_error: Exception | None = None
    last_response_text = ""
    last_status_code: int | None = None

    for _ in range(3):
        try:
            with httpx.Client(timeout=timeout) as client:
                response = client.post(url, headers=headers, json=payload)
                if response.status_code >= 400:
                    last_status_code = response.status_code
                    last_response_text = response.text[:1200]
                    response.raise_for_status()
                return response.json()
        except (httpx.HTTPError, ValueError) as exc:
            last_error = exc

    if last_status_code is not None:
        raise TinyFishError(
            f"TinyFish call failed with status {last_status_code}. Response: {last_response_text}"
        )
    raise TinyFishError(f"TinyFish call failed after retries: {last_error}")
