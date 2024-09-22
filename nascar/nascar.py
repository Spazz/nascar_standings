import requests
import logging
from nascar import Race

class NASCARFeed:
    def __init__(self, api_url):
        self.api_url = api_url
        self.race = None
        self.logger = logging.getLogger(self.__class__.__name__)

    def fetch_data(self):
        self.logger.info(f"Fetching data from {self.api_url}")
        try:
            response = requests.get(self.api_url)
            response.raise_for_status()
            data = response.json()

            # Create or update the race object
            if not self.race:
                self.logger.info("Creating new Race object")
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
            self.logger.info(f"Race data updated for race ID {self.race.race_id}")

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Failed to fetch data from NASCAR API: {e}")