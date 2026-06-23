import json
import logging
import os
import time
import requests
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()


def load_env_variables():
    api_secret = os.getenv('X-CG-API-Secret')
    school_code = os.getenv('X-CG-School')
    endpoint = os.getenv('endpoint')

    if not api_secret or not school_code or not endpoint:
        raise ValueError(
            "One or more environment variables are missing. Please check your .env file.")
    return api_secret, school_code, endpoint


api_secret, school_code, endpoint = load_env_variables()

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    filename=DATA_DIR / f"{school_code}-{endpoint}.log",
    filemode="a",
    encoding="utf-8",
)

api_url = (
    f"https://{school_code}.service.campusgroups.com"
    f"/data/v1/{endpoint}"
)

headers = {
    "X-CG-API-Secret": api_secret,
    "X-CG-School": school_code,
    "Accept": "application/json"
}

session = requests.Session()
session.headers.update(headers)


def save_data(data, suffix=""):
    (DATA_DIR / f"{school_code}-{endpoint}{suffix}.json").write_text(
        json.dumps(data, indent=2), encoding="utf-8"
    )


def request_with_poll(method, url, **kwargs):
    while True:
        response = session.request(method, url, timeout=120, **kwargs)
        response.raise_for_status()

        result = response.json()
        message = result.get("message", "")

        if message.lower().startswith("error"):
            raise RuntimeError(message)

        if message:
            print("Query still running, waiting 5 seconds...")
            time.sleep(5)
            continue

        return result


def request_query(updated_start, updated_end):
    url = f"{api_url}?updatedStart={updated_start}&updatedEnd={updated_end}"

    try:
        print("Requesting query ID...")
        return request_with_poll("post", url, headers=headers)

    except requests.exceptions.RequestException as e:
        logging.error("Error getting queryId: %s", e)
        return None


def get_data(query_id, token=""):
    data = []

    try:
        print(f"Fetching data for query ID {query_id}...")
        url = f"{api_url}?queryId={query_id}&token={token}"
        response = request_with_poll("get", url, headers=headers)
        data.extend(response.get('Results', []))
        print(f"Retrieved {len(data)} records from first page")

        while token := response.get('NextToken'):
            url = f"{api_url}?queryId={query_id}&token={token}"
            response = request_with_poll("get", url, headers=headers)
            data.extend(response.get('Results', []))
            print(f"Retrieved {len(data)} total records so far")

    except requests.exceptions.RequestException as e:
        save_data(data, "-partial")
        print(
            f"Saved partial data: data/{school_code}-{endpoint}-partial.json")
        logging.error(
            "Error getting data for Query ID %s at token %s: %s",
            query_id,
            token or "<first-page>",
            e,
        )
        raise e

    return data


if __name__ == "__main__":
    # Export date range in ISO 8601 UTC format.
    UPDATED_START = "2020-01-01T00:00:00Z"
    UPDATED_END = "2026-07-22T23:59:59Z"
    # OPTIONAL - Set these only when resuming an existing query manually.
    QUERY_ID = None
    TOKEN = None

    if QUERY_ID:
        data = get_data(QUERY_ID, TOKEN)
        logging.info("Retrieved %s records total", len(data))
        save_data(data)
        logging.info("Wrote data/%s-%s.json", school_code, endpoint)
    else:
        query_response = request_query(UPDATED_START, UPDATED_END)
        query_id = query_response.get('queryId') if query_response else None
        if query_id:
            data = get_data(query_id)
            logging.info("Retrieved %s records total", len(data))
            save_data(data)
            logging.info("Wrote data/%s-%s.json", school_code, endpoint)
        else:
            logging.error("Failed to retrieve query ID")
