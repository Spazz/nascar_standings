import json
import random
import time

def generate_pit_stops():
    """Generate random pit stop data for a driver."""
    pit_stops = []
    for i in range(random.randint(3, 5)):  # Match the number of pit stops with the example
        pit_stops.append({
            "pit_in_elapsed_time": round(random.uniform(0, 10000), 3),
            "pit_in_lap_count": random.randint(0, 100),
            "pit_in_leader_lap": random.randint(0, 100),
            "pit_in_rank": random.randint(1, 40),
            "pit_out_elapsed_time": round(random.uniform(0, 10000), 3),
            "pit_out_rank": random.randint(1, 40),
            "positions_gained_lossed": random.randint(-30, 5)
        })
    return pit_stops

def generate_car_data(car_number):
    """Generate mock car data for each driver."""
    manufacturers = ['Frd', 'Chv', 'Tyt']
    sponsors = ['BuildSubmarines.com', 'WeatherTech', 'The Beast Unleashed', 'Monster Energy']
    
    laps_completed = random.randint(50, 100)
    last_update_time = time.time()

    car_data = {
        "car_number": str(car_number),
        "driver_name": f"Driver {car_number}",
        "is_on_dvp": random.choice([True, False]),
        "is_on_track": random.choice([True, False]),
        "laps_completed": laps_completed,
        "last_update": last_update_time,
        "manufacturer": random.choice(manufacturers),
        "pit_stops": generate_pit_stops(),
        "position": None,  # We'll set this after randomizing the positions
        "prev_pit_stops": len(generate_pit_stops()),  # Mock previous pit stops count
        "recent_pit_stop": random.choice([True, False]),
        "sponsor": random.choice(sponsors),
        "status": random.choice([1, 2, 3])  # 1=Active, 2=Inactive, 3=Finished
    }
    return car_data

def generate_race_data():
    """Generate the race data with vehicles and race info."""
    # Generate car data for all cars
    car_data = [generate_car_data(i) for i in range(1, 39)]
    
    # Randomize positions
    random_positions = random.sample(range(1, 39), 38)  # Get unique positions for each car
    
    # Assign positions and update position_change based on prev_position
    for i, car in enumerate(car_data):
        car['position'] = random_positions[i]
    
    # Sort car data by the newly randomized position
    car_data = sorted(car_data, key=lambda d: d["position"])
    
    # Race details
    race_data = {
        "current_lap": random.randint(1, 100),
        "elapsed_time": round(random.uniform(0, 10000), 2),
        "flag_state": random.randint(0, 9),
        "laps_in_race": 92,
        "laps_to_go": random.randint(0, 100),
        "race_id": random.randint(1000, 9999),
        "run_name": "Go Bowling at The Glen",
        "track_length": 2.45,
        "track_name": "Watkins Glen International"
    }
    
    return {"car_data": car_data, "race_data": race_data}

def save_mock_data():
    # Generate the mock data
    race_data = generate_race_data()

    # Output the JSON
    json_output = json.dumps(race_data, indent=4)
    print(json_output)

if __name__ == "__main__":
    save_mock_data()