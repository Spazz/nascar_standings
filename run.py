from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import requests, json
from time import time, sleep
from digit_patterns import digit_patterns  # Assuming you have this file with digit patterns
from utils import get_color, get_driver_status_color, get_flag_state_color

##### -- Global Variables for LED base configuration -- #####
ROWS_PER_CAR = 12  # Number of LED rows per car
FETCH_INTERVAL = 5  # In seconds
last_fetch_time = 0
DISPLAY_CAR_LIMIT = 40

##### -- Global Variables for various statuses -- #####
previous_positions = {}
status_lights = {}
STATUS_LIGHT_DURATION = 3  # Duration for status light (in seconds)

##### -- rpi-rgb-led-matrix Setup -- #####
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 1
options.parallel = 1
options.brightness = 90
options.gpio_slowdown = 5
options.pixel_mapper_config = "Rotate:90"
matrix = RGBMatrix(options=options)

font = graphics.Font()
font.LoadFont("../rpi-rgb-led-matrix/fonts/7x13.bdf")
white = graphics.Color(255, 255, 255)
yellow = graphics.Color(255, 0, 255)
red = graphics.Color(255, 0, 0)
blue = graphics.Color(0, 0, 255)
green = graphics.Color(0, 255, 0)

##### -- Helper Functions -- #####
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


def convert_to_graphics_color(tuple):
    return graphics.Color(tuple[0], tuple[1], tuple[2])

##### -- Display Car Information and Status Lights -- #####
def display_car_info(canvas, car, row, flag_state):
    car_number = car['car_number']
    position = car['position']
    status = car['status']

    # Display Position
    position_digits = [int(d) for d in str(position)]
    cblack = convert_to_graphics_color(get_color('black'))

    position_str = str(position)
    graphics.DrawText(canvas, font, 8, row + 13, cblack, position_str)

    car_number_str = str(car_number)
    color = convert_to_graphics_color(get_driver_status_color(status))

    graphics.DrawText(canvas, font, 18, row + 13, color, car_number_str)

    # if len(position_digits) == 1:
    #     draw_digit(canvas, position_digits[0], row, 8, cblack)  # Single digit
    # else:
    #     draw_digit(canvas, position_digits[0], row, 1, cblack)  # Tens
    #     draw_digit(canvas, position_digits[1], row, 8, cblack)  # Ones

    # # Display Car Number
    # car_number_digits = [int(d) for d in str(car_number)]
    # color = get_driver_status_color(status)
    # if len(car_number_digits) == 1:
    #     draw_digit(canvas, car_number_digits[0], row, 25, color)
    # else:
    #     draw_digit(canvas, car_number_digits[0], row, 18, color)
    #     draw_digit(canvas, car_number_digits[1], row, 25, color)

    # Display status lights for position change
    if car_number in status_lights:
        light_info = status_lights[car_number]
        elapsed_time = time() - light_info['time']
  
        if elapsed_time < STATUS_LIGHT_DURATION:  # Light stays on for the set duration
            # Display car info and update status lights
            display_status_lights(car_number, row, canvas, light_info)
        else:
            # Remove the status light after the duration
            del status_lights[car_number]

##### -- Track Position Changes and Update Status Lights -- #####
def display_position_status(car):
    car_number = car['car_number']
    position = car['position']

    # Track position changes
    previous_position = previous_positions.get(car_number)
    if previous_position is not None and previous_position != position:
        if position < previous_position:
            # Car moved up (green LED)
            status_lights[car_number] = {'color': (0, 0, 255), 'time': time()}
        elif position > previous_position:
            # Car moved down (red LED)
            status_lights[car_number] = {'color': (255, 0, 0), 'time': time()}

    # Update the previous position
    previous_positions[car_number] = position

def display_status_lights(car_number, row, canvas, light_info):
    elapsed_time = time() - light_info['time']
    r, g, b = light_info['color']
    
    # Define how much time each light in the sequence should be delayed
    delay_per_light = 0.05  # 100 milliseconds between each light

    # Check if the lights should still be on
    if elapsed_time < STATUS_LIGHT_DURATION:
        if r > 1 and g == 0:
            for i in range(11):  # Loop over 15 LEDs in the vertical row
                # Calculate when each light should turn on based on its position
                light_delay = i * delay_per_light
                
                # Only light up LEDs if their individual "turn-on" time has passed
                if elapsed_time > light_delay:
                    canvas.SetPixel(15, row + i, r, g, b)

        else:  # Red light (position lost)
            # Light from top to bottom
            for i in range(15):
                light_delay = i * delay_per_light
                if elapsed_time > light_delay:
                    canvas.SetPixel(15, row + (11 - i), r, g, b)  # Light moves from row + 14 down to row

    else:
        # Remove the status light after the duration
        del status_lights[car_number]

##### -- Fetch Car Data from API -- #####
def fetch_car_data():
    try:
        response = requests.get('http://127.0.0.1:5000/mock-data')  # Replace with your API URL
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data: {e}")
        return []  # Return empty list if error

# Main loop
try:
    canvas = matrix.CreateFrameCanvas()
    
    while True:
        current_time = time()
        canvas.Clear()

        # Fetch new data every FETCH_INTERVAL
        if current_time - last_fetch_time >= FETCH_INTERVAL:
            response_data = fetch_car_data()
        
            if response_data:
                race_data = response_data.get('race_data', {})
                car_data = response_data.get('car_data', [])
            last_fetch_time = current_time # Reset the timer

        # Draw background
        draw_background(canvas, race_data.get('flag_state', 1))

        # Display car info and status lights for each car
        for i, car in enumerate(car_data[:DISPLAY_CAR_LIMIT]):
            display_car_info(canvas, car, (i * ROWS_PER_CAR), race_data.get('flag_state', 1))

        # Track car position changes and update status lights
        for car in car_data:
            display_position_status(car)

        # Swap the canvas to show the changes
        canvas = matrix.SwapOnVSync(canvas)

        # Sleep to limit the refresh rate (you can adjust this)
        sleep(0.1)
except KeyboardInterrupt:
    print("Exiting...")
    matrix.Clear()  # Clear the matrix when exiting