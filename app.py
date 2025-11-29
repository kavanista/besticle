import logging
import os
from html import escape

from flask import Flask
import requests

app = Flask(__name__)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
API_URL = "https://data.smartdublin.ie/cgi-bin/rtpi/realtimebusinformation?stopid={}&format=json"
REQUEST_TIMEOUT = 10  # seconds


@app.route('/')
def index():
    return "Hello world"


def format_output(js):
    """Format bus information as HTML."""
    results = js.get("results", [])
    if not results:
        return "No buses currently scheduled for this stop."

    output_lines = []
    for bus in results:
        bus_route = escape(str(bus.get("route", "Unknown")))
        arrival_time = escape(str(bus.get("arrivaldatetime", "Unknown")))
        output_lines.append(f"{bus_route} {arrival_time}")

    return "<br>".join(output_lines)


@app.route('/bus/<stopid>')
def bus_get(stopid):
    # Validate stopid - should be numeric
    if not stopid.isdigit():
        logger.warning(f"Invalid stopid requested: {stopid}")
        return "Invalid stop ID. Must be a number.", 400

    try:
        resp = requests.get(API_URL.format(stopid), timeout=REQUEST_TIMEOUT)
    except requests.Timeout:
        logger.error(f"Timeout fetching data for stop {stopid}")
        return "API request timed out. Please try again.", 504
    except requests.RequestException as e:
        logger.error(f"Request error for stop {stopid}: {e}")
        return "Cannot access API endpoint.", 502

    if resp.status_code != 200:
        logger.error(f"API returned status {resp.status_code} for stop {stopid}")
        return f"API returned error status: {resp.status_code}", 502

    try:
        js = resp.json()
    except ValueError as e:
        logger.error(f"Invalid JSON response for stop {stopid}: {e}")
        return "Invalid response from API.", 502

    error_code = js.get("errorcode", "")
    if error_code != "0":
        error_message = js.get("errormessage", "Unknown error")
        logger.warning(f"API error for stop {stopid}: {error_code} - {error_message}")
        return f"API error: {escape(error_message)}", 503

    return format_output(js)


if __name__ == '__main__':
    debug_mode = os.environ.get('FLASK_DEBUG', 'false').lower() == 'true'
    app.run(debug=debug_mode)
