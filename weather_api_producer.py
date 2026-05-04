"""
Weather API Producer Script
Task 2.4: Makes API calls every 30 minutes and stores weather data in JSON format

This script:
1. Generates 20 random user locations
2. Calls open-meteo weather API for each user every 30 minutes
3. Writes results as JSON files to user_weather/ folder
4. Each file named: user_weather/[user]_[current_timestamp]_weather.json

The Spark streaming consumer will automatically detect and process new files.
"""

import time
import requests
import json
import random
import os
from datetime import datetime
from pathlib import Path


# Configuration
BASE_DIR = r"C:\Users\KunalMajumdar\OneDrive - EPAM\EPAM Trainings\Spark for DQE"
USER_WEATHER_PATH = os.path.join(BASE_DIR, "user_weather")
POLL_INTERVAL_SECONDS = 30  # Change to 1800 for production (30 minutes)

# Ensure output directory exists
os.makedirs(USER_WEATHER_PATH, exist_ok=True)

# Generate random user locations (20 users)
user_locations = []
for i in range(20):
    user_id = f"user{i}"
    latitude = random.uniform(-90, 90)
    longitude = random.uniform(-180, 180)
    user_locations.append((user_id, latitude, longitude))

print("=" * 70)
print("Weather API Producer Started")
print("=" * 70)
print(f"Output directory: {USER_WEATHER_PATH}")
print(f"Poll interval: {POLL_INTERVAL_SECONDS} seconds")
print(f"Number of users: {len(user_locations)}")
print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 70)
print()


def get_current_weather(url):
    """Fetch current weather from open-meteo API"""
    try:
        request_response = requests.get(url, timeout=10)
        weather_request_response_json = json.loads(request_response.text)
        current_weather = weather_request_response_json.get("current_weather")
        return current_weather
    except Exception as e:
        print(f"  Error fetching weather: {e}")
        return None


def write_current_weather_to_file(file_name, current_weather):
    """Write weather data to JSON file"""
    try:
        with open(file_name, "w") as f:
            json.dump(current_weather, f)
        return True
    except Exception as e:
        print(f"  Error writing file {file_name}: {e}")
        return False


def poll_weather_api():
    """Poll weather API for all users and write results"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Polling weather API for {len(user_locations)} users...")
    
    success_count = 0
    for i, (user_id, latitude, longitude) in enumerate(user_locations):
        # Build API URL
        weather_api_url = (
            f"https://api.open-meteo.com/v1/forecast?"
            f"latitude={latitude}&longitude={longitude}&"
            f"current_weather=true&"
            f"hourly=temperature_2m,relativehumidity_2m,windspeed_10m"
        )
        
        # Get weather data
        current_weather = get_current_weather(weather_api_url)
        
        if current_weather:
            # Build file name with user_id and timestamp
            file_name = os.path.join(
                USER_WEATHER_PATH,
                f"{user_id}_{timestamp}_weather.json"
            )
            
            # Write to file
            if write_current_weather_to_file(file_name, current_weather):
                success_count += 1
                print(f"  ✓ {user_id}: {file_name}")
        
        # Small delay between API calls to avoid rate limiting
        time.sleep(0.1)
    
    print(f"  Completed: {success_count}/{len(user_locations)} files written\n")
    return success_count


def main():
    """Main loop - continuously poll API at specified interval"""
    iteration = 0
    try:
        while True:
            iteration += 1
            print(f"--- Iteration {iteration} ---")
            poll_weather_api()
            
            print(f"Next poll in {POLL_INTERVAL_SECONDS} seconds...")
            print(f"(Press Ctrl+C to stop)\n")
            time.sleep(POLL_INTERVAL_SECONDS)
            
    except KeyboardInterrupt:
        print("\n" + "=" * 70)
        print("Weather API Producer Stopped")
        print("=" * 70)
        print(f"Stopped at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Total iterations: {iteration}")


if __name__ == "__main__":
    main()
