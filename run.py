from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import requests
from time import time, sleep
from digit_patterns import digit_patterns  # Assuming you have this file with digit patterns

##### -- Global Variables for LED base configuration -- #####
ROWS_PER_CAR = 16  # Number of LED rows per car
FETCH_INTERVAL = 5  # In seconds
DISPLAY_CAR_LIMIT = 40

##### -- Global Variables for various statuses -- #####
blink_timers = {'is_on_dvp': time(), 'is_off_track': time()}
BLINK_INTERVAL = {'is_on_dvp': 0.5, 'is_off_track': 0.5}
blink_states = {'is_on_dvp': True, 'is_off_track': False}
status_colors = {
    'is_on_dvp': (255, 0, 0),  # Red when DVP is active, off otherwise
    'is_off_track': (255, 255, 0),  # Yellow if off track
    'recent_pit_stop': (0, 0, 255)  # Blue for pit stop
}

previous_positions = {}
status_lights = {}
STATUS_LIGHT_DURATION = 3

##### -- rpi-rgb-led-matrix Setup -- #####
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.brightness = 100
options.gpio_slowdown = 5
options.pixel_mapper_config = "Rotate:90"
matrix = RGBMatrix(options=options)

font = graphics.Font()
font.LoadFont("../rpi-rgb-led-matrix/fonts/7x13.bdf")
white = graphics.Color(255, 255, 255)
yellow = graphics.Color(255, 255, 0)
red = graphics.Color(255, 0, 0)
blue = graphics.Color(0, 0, 255)
green = graphics.Color(0, 255, 0)

def draw_digit(canvas, digit, top_row, left_col, color):
    pattern = digit_patterns.get(digit, [])
    for y, row in enumerate(pattern):
        for x, col in enumerate(row):
            if col == '*':  # LED ON
                canvas.SetPixel(left_col + x, top_row + y, color[0], color[1], color[2])

def draw_background(canvas, flag_state):
    bg_color = get_flag_state_color(flag_state)
    for y in range(options.cols):
        for x in range(15):  # Left part of the matrix (you can adjust this)
            canvas.SetPixel(x, y, bg_color[0], bg_color[1], bg_color[2])

def get_flag_state_color(flag_state):
    flag_state_colors = {
        1: (255, 255, 255),  # White - Green
        2: (255, 255, 0),    # Yellow - Caution
        3: (255, 0, 0),      # Red
        4: (255, 255, 255),  # Finish
        6: (255, 255, 255),  # Stop (unknown color)
        8: (226, 81, 17),    # Orange - Warm Up
        9: (255, 255, 255)   # Not Active
    }
    return flag_state_colors.get(flag_state, (255, 255, 255))  # Default to white

def display_car_info(canvas, car, row, flag_state):
    car_number = car['car_number']
    position = car['position']
    status = car['status']

    bg_color = get_flag_state_color(flag_state)

    # Display Position
    position_digits = [int(d) for d in str(position)]
    if len(position_digits) == 1:
        draw_digit(canvas, position_digits[0], row, 8, (0, 0, 0))  # Single digit
    else:
        draw_digit(canvas, position_digits[0], row, 1, (0, 0, 0))  # Tens
        draw_digit(canvas, position_digits[1], row, 8, (0, 0, 0))  # Ones

    # Display Car Number
    car_number_digits = [int(d) for d in str(car_number)]
    color = get_driver_status_color(status)
    if len(car_number_digits) == 1:
        draw_digit(canvas, car_number_digits[0], row, 25, color)
    else:
        draw_digit(canvas, car_number_digits[0], row, 18, color)
        draw_digit(canvas, car_number_digits[1], row, 25, color)

def get_driver_status_color(status):
    driver_status_colors = {
        1: (255, 255, 255),  # White - Running
        2: (255, 255, 0),    # Yellow - In Garage
        3: (255, 0, 0)       # Red - DNF
    }
    return driver_status_colors.get(status, (255, 255, 255))  # Default

def fetch_car_data():
    try:
        response = requests.get('http://127.0.0.1:5000/data')  # Replace with your API URL
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []  # Return empty list if error

# Main loop
try:
    while True:
        canvas = matrix.CreateFrameCanvas()

        response_data = fetch_car_data()
        race_data = response_data.get('race_data', {})
        car_data = response_data.get('car_data', [])

        # Draw background
        draw_background(canvas, race_data.get('flag_state', 1))

        # Display car info for each car
        for i, car in enumerate(car_data[:DISPLAY_CAR_LIMIT]):
            display_car_info(canvas, car, (i * ROWS_PER_CAR), race_data.get('flag_state', 1))

        # Swap the canvas to show the changes
        canvas = matrix.SwapOnVSync(canvas)

        # Sleep to limit the refresh rate (you can adjust this)
        sleep(FETCH_INTERVAL)
except KeyboardInterrupt:
    print("Exiting...")
    matrix.Clear()  # Clear the matrix when exiting
