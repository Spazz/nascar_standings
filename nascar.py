import requests, time

class Race:
    def __init__(self, race_id, lap_number, elapsed_time, flag_state, laps_to_go, run_name, track_length, track_name, laps_in_race):
        self.race_id = race_id
        self.lap_number = lap_number
        self.elapsed_time = elapsed_time
        self.flag_state = flag_state
        self.laps_to_go = laps_to_go
        self.laps_in_race = laps_in_race
        self.run_name = run_name
        self.track_length = track_length
        self.track_name = track_name
        self.cars = []
        self.current_lap = 0
        self.flag_state = None

    class Car:
        def __init__(self, vehicle_data):
            # Automatically set attributes from the API data
            self.update_from_api(vehicle_data)

            # Custom fields
            self.prev_position = self.position
            self.recent_pit_stop = False
            #self.position_change = {'direction': None, 'timestamp': None}
            
            self.prev_pit_stops = len(self.pit_stops)
            self.last_update = time.time()

        def update_from_api(self, vehicle_data):
            # Efficiently update all relevant API fields from the vehicle data
            self.position = vehicle_data['running_position']
            self.driver_name = vehicle_data['driver']['full_name']
            self.car_number = vehicle_data['vehicle_number']
            self.status = vehicle_data['status']
            self.manufacturer = vehicle_data['vehicle_manufacturer']
            self.sponsor = vehicle_data['sponsor_name']
            self.is_on_track = vehicle_data['is_on_track']
            self.is_on_dvp = vehicle_data['is_on_dvp']
            self.laps_completed = vehicle_data['laps_completed']
            self.pit_stops = vehicle_data['pit_stops']
            self.last_update = time.time()

        def update_custom_fields(self):
            #self.check_position_change()
            self.check_pit_stop()

        # def check_position_change(self):
        #     self.position_change = {'direction':'up', 'timestamp':time.time()} if self.position < self.prev_position else {'direction':'down', 'timestamp':time.time()} if self.position > self.prev_position else self.position_change['direction'] == None
        #     self.prev_position = self.position

        # def display_position_change(self):
        #     if self.position_change['direction'] and (time.time() - self.position_change['timestamp']) < 3:
        #         return True
        #     return False

        def check_pit_stop(self):
            if len(self.pit_stops) > self.prev_pit_stops:
                self.recent_pit_stop = True
                self.last_pit_stop_lap = self.laps_completed
            elif self.recent_pit_stop and self.laps_completed - self.last_pit_stop_lap >= 5:
                self.recent_pit_stop = False
            self.prev_pit_stops = len(self.pit_stops)

    def get_or_create_car(self, vehicle_data):
        # Look for an existing car; otherwise, create and add a new one
        car_number = vehicle_data['vehicle_number']
        car = next((c for c in self.cars if c.car_number == car_number), None)
        if car:
            return car
        new_car = self.Car(vehicle_data)
        self.cars.append(new_car)
        return new_car

    def update_race_data(self, data):
        self.current_lap = data.get('lap_number')
        self.flag_state = data.get('flag_state')

        # Efficiently update cars
        for vehicle in data['vehicles']:
            car = self.get_or_create_car(vehicle)
            car.update_from_api(vehicle)
            car.update_custom_fields()

    def map_manufacturer(self, short_name):
        # Improved mapping with default behavior
        return {
            'Frd': 'Ford',
            'Chv': 'Chevy',
            'Tyt': 'Toyota'
        }.get(short_name, short_name)


class NASCARFeed:
    def __init__(self, api_url):
        self.api_url = api_url
        self.race = None

    def fetch_data(self):
        response = requests.get(self.api_url)
        if response.status_code == 200:
            data = response.json()
            
            # Create or update the race object
            if not self.race:
                self.race = Race(
                    race_id=data['race_id'],
                    track_name=data['track_name'],
                    laps_in_race=data['laps_in_race'],
                    lap_number=data['lap_number'],
                    elapsed_time=data['elapsed_time'],
                    flag_state=data['flag_state'],
                    laps_to_go=data['laps_to_go'],
                    run_name=data['run_name'],
                    track_length=data['track_length']
                )

            # Update race data with the latest info
            self.race.update_race_data(data)
        else:
            print("Failed to fetch data from the NASCAR API")