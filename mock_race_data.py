import json
import random

def generate_pit_stops():
    """Generate random pit stop data for a driver."""
    pit_stops = []
    for i in range(random.randint(1, 3)):
        pit_stops.append({
            "positions_gained_lost": random.randint(-5, 5),
            "pit_in_elapsed_time": round(random.uniform(0, 5000), 3),
            "pit_in_lap_count": random.randint(0, 100),
            "pit_in_leader_lap": random.randint(0, 50),
            "pit_out_elapsed_time": round(random.uniform(0, 5000), 3),
            "pit_in_rank": random.randint(1, 40),
            "pit_out_rank": random.randint(1, 40)
        })
    return pit_stops

def generate_drivers_data():
    """Generate mock driver data."""
    drivers_data = []
    for i in range(1, 39):  # 38 drivers
        driver_data = {
            "driver": {
                "driver_id": i,
                "full_name": f"Driver {i}",
                "first_name": f"FirstName{i}",
                "last_name": f"LastName{i}",
                "is_in_chase": random.choice([True, False])
            },
            "pit_stops": generate_pit_stops(),
            "running_position": random.randint(1, 38),
            "status": random.choice([1, 2, 3]),  # 1=Active, 2=Inactive, 3=Finished
            "sponsor_name": f"Sponsor {i}",
            "is_on_track": random.choice([True, False]),
            "is_on_dvp": random.choice([True, False])
        }
        drivers_data.append(driver_data)
    return drivers_data

def generate_race_data():
    """Generate the race data with drivers."""
    race_data = {
        "lap_number": random.randint(1, 100),
        "elapsed_time": round(random.uniform(0, 5000), 2),
        "flag_state": random.randint(0, 5),
        "race_id": 10000,
        "laps_in_race": 100,
        "laps_to_go": random.randint(0, 100),
        "vehicles": generate_drivers_data()
    }
    return race_data

def save_mock_data():
    # Generate the mock data
    race_data = generate_race_data()

    # Output the JSON
    json_output = json.dumps(race_data, indent=4)
    print(json_output)

if __name__ == "__main__":
    save_mock_data()