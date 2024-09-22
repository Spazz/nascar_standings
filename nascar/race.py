import time
import logging

class Race:
    def __init__(self, race_id, lap_number, elapsed_time, flag_state, laps_to_go, run_name, track_length, track_name, laps_in_race):
        self.logger = logging.getLogger(self.__class__.__name__)
        self.logger.info(f"Initializing race {race_id}")
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

    class Car:
        def __init__(self, vehicle_data):
            self.logger = logging.getLogger(self.__class__.__name__)
            self.update_from_api(vehicle_data)
            self.prev_position = self.position
            self.recent_pit_stop = False
            self.prev_pit_stops = len(self.pit_stops)
            self.last_update = time.time()
            self.logger.info(f"Car {self.car_number} initialized")

        def update_from_api(self, vehicle_data):
            try:
                self.position = vehicle_data['running_position']
                self.driver_name = vehicle_data['driver']['full_name']
                self.car_number = vehicle_data['vehicle_number']
                self.status = vehicle_data['status']
                self.is_on_track = vehicle_data['is_on_track']
                self.is_on_dvp = vehicle_data['is_on_dvp']
                self.laps_completed = vehicle_data['laps_completed']
                self.pit_stops = vehicle_data['pit_stops']
                self.last_update = time.time()
                self.logger.info(f"Updated data for car {self.car_number}")
            except KeyError as e:
                self.logger.error(f"Missing data field in vehicle data: {e}")
            except Exception as e:
                self.logger.error(f"Error updating car data: {e}")

        def update_custom_fields(self):
            #self.check_position_change()
            self.check_pit_stop()

        def check_pit_stop(self):
            if len(self.pit_stops) > self.prev_pit_stops:
                self.recent_pit_stop = True
                self.last_pit_stop_lap = self.laps_completed
            elif self.recent_pit_stop and self.laps_completed - self.last_pit_stop_lap >= 5:
                self.recent_pit_stop = False
            self.prev_pit_stops = len(self.pit_stops)


        # New method to return only serializable fields
        def to_dict(self):
            return {
                'position': self.position,
                'driver_name': self.driver_name,
                'car_number': self.car_number,
                'status': self.status,
                'is_on_track': self.is_on_track,
                'is_on_dvp': self.is_on_dvp,
                'laps_completed': self.laps_completed,
                'pit_stops': self.pit_stops,
                'last_update': self.last_update
            }

    def get_or_create_car(self, vehicle_data):
        car_number = vehicle_data['vehicle_number']

        # Search for an existing car by the car number
        car = next((c for c in self.cars if c.car_number == car_number), None)
        
        if car:
            # If the car exists, return the existing car object
            self.logger.info(f"Updating existing car: {car_number}")
            return car
        else:
            self.logger.info(f"Creating new car: {car_number}")
            new_car = self.Car(vehicle_data)
            self.cars.append(new_car)
            return new_car

    def update_race_data(self, data):
        try:
            self.logger.info(f"Updating race data for lap {data.get('lap_number')}")
            self.current_lap = data.get('lap_number')
            self.flag_state = data.get('flag_state')

            for vehicle in data['vehicles']:
                car = self.get_or_create_car(vehicle)
                car.update_from_api(vehicle)
                car.update_custom_fields()

        except Exception as e:
            self.logger.error(f"Error updating race data: {e}")