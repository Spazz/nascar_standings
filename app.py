from flask import Flask, jsonify, render_template
from nascar import NASCARFeed
import random, threading, json

# Create the Flask app
app = Flask(__name__)

# Global state for each car (car number as key)
car_states = {
    car_number: {"is_on_track": True, "is_on_dvp": False, "locked_position": None}
    for car_number in range(1, 39)
}

# NASCAR API URL
API_URL = "https://cf.nascar.com/live/feeds/live-feed.json"


# Other URLS
# https://cf.nascar.com/cacher/2024/2/5451/weekend-feed.json
# https://cf.nascar.com/cacher/2024/2/5451/live-stage-points.json
# https://cf.nascar.com/cacher/2024/2/5451/lap-averages.json
# https://cf.nascar.com/cacher/tracks.json
# https://cf.nascar.com/cacher/2024/race_list_basic.json



# Route to return car data as JSON
@app.route('/data')
def data():
    nascar_feed = NASCARFeed(API_URL)
    nascar_feed.fetch_data()
    
    race_info = {
        'race_data':{
            'race_id': nascar_feed.race.race_id,
            'track_name': nascar_feed.race.track_name,
            'current_lap': nascar_feed.race.current_lap,
            'flag_state': nascar_feed.race.flag_state,
            'elapsed_time': nascar_feed.race.elapsed_time,
            'laps_to_go': nascar_feed.race.laps_to_go,
            'laps_in_race': nascar_feed.race.laps_in_race,
            'run_name': nascar_feed.race.run_name,
            'track_length': nascar_feed.race.track_length
            },
        'car_data': [car.__dict__ for car in nascar_feed.race.cars]
    }
    return jsonify(race_info)

def generate_mock_data():
    from mock_race_data import generate_race_data
    return generate_race_data()

# Route to return mock car data as JSON
@app.route('/mock-data')
def mock_data():

    race_data = generate_mock_data()
    # print(json.dumps(race_data, indent=1))

    return jsonify(race_data)

    # nascar_feed = NASCARFeed(API_URL)
    # nascar_feed.fetch_data()

    # Generate mock data
    # mock_car_data = []
    
    # for car in nascar_feed.cars:
    #     car_number = car.car_number
    #     # Use the current state for DVP and on_track, or the real API values
    #     mock_car_data.append({
    #         'position': car.position,
    #         'car_number': car_number,
    #         'is_on_track': car_states[car_number]['is_on_track'],
    #         'is_on_dvp': car_states[car_number]['is_on_dvp']
    #     })

    # return jsonify(mock_car_data)

# Console listener function to update car states dynamically
def console_listener():
    while True:
        command = input("Enter command (e.g., 'track 1 false' or 'dvp 3 true'): ")
        parts = command.split()
        
        if len(parts) == 3:
            car_number = int(parts[1])
            value = parts[2].lower() == 'true'
            
            if parts[0] == 'track' and car_number in car_states:
                car_states[car_number]['is_on_track'] = value
                print(f"Updated car {car_number}: is_on_track = {value}")
                
            elif parts[0] == 'dvp' and car_number in car_states:
                car_states[car_number]['is_on_dvp'] = value
                print(f"Updated car {car_number}: is_on_dvp = {value}")
        else:
            print("Invalid command format. Use 'track <car_number> <true/false>' or 'dvp <car_number> <true/false>'.")

# Start a thread to listen to console input while the API runs
console_thread = threading.Thread(target=console_listener)
console_thread.daemon = True  # Ensures thread exits when the main program exits
console_thread.start()


# Route to serve the main page
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)