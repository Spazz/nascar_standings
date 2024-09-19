from rgbmatrix import RGBMatrix, RGBMatrixOptions, graphics
import requests, json, math
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
previous_pit_stops = {}
status_lights = {}
STATUS_LIGHT_DURATION = 3  # Duration for status light (in seconds)
PIT_STOP_STATUS_LIGHT_DURATION = 120 # Duration for pit stops (in seconds)

##### -- rpi-rgb-led-matrix Setup -- #####
options = RGBMatrixOptions()
options.rows = 32
options.cols = 64
options.chain_length = 3
options.parallel = 1
options.brightness = 50
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
    for y in range(options.cols * options.chain_length):
        for x in range(15):  # Left part of the matrix (you can adjust this)
            canvas.SetPixel(x, y, bg_color[0], bg_color[1], bg_color[2])

def convert_to_graphics_color(tuple):
    return graphics.Color(tuple[0], tuple[1], tuple[2])

##### -- Display Car Information and Status Lights -- #####
def display_car_info(canvas, car, row):
    shifted_row = row - 1
    car_number = car['car_number']
    position = car['position']
    status = car['status']
    pit_stops = car['pit_stops']

    # Display Position
    cblack = convert_to_graphics_color(get_color('black'))

    position_str = str(position)
    
    if len(position_str) == 1:
        graphics.DrawText(canvas, font, 8, shifted_row + ROWS_PER_CAR, cblack, position_str)
    else:
        graphics.DrawText(canvas, font, 1, shifted_row + ROWS_PER_CAR, cblack, position_str[0])
        graphics.DrawText(canvas, font, 8, shifted_row + ROWS_PER_CAR, cblack, position_str[1])

    car_number_str = str(car_number)
    color = convert_to_graphics_color(get_driver_status_color(status))

    graphics.DrawText(canvas, font, 18, shifted_row + ROWS_PER_CAR, color, car_number_str)

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
    if car_number not in status_lights:
        status_lights[car_number] = {}
    if car_number in status_lights and 'position' in status_lights[car_number]:
        light_info = status_lights[car_number]['position']
        elapsed_time = time() - light_info['time']
  
        if elapsed_time < STATUS_LIGHT_DURATION:  # Light stays on for the set duration
            # Display car info and update status lights
            display_status_lights(car_number, shifted_row, canvas, light_info)
        else:
            # Remove the status light after the duration
            del status_lights[car_number]['position']

    # Check pit stop array and display the status LED in the 16th column if necessary
    display_pit_stop_status(car_number, shifted_row, canvas, pit_stops)

    # Display DVP status
    display_dvp_status(car_number, shifted_row, canvas, car)


##### -- Track Position Changes and Update Status Lights -- #####
def display_position_status(car):
    car_number = car['car_number']
    position = car['position']

    # Track position changes
    previous_position = previous_positions.get(car_number)
    if previous_position is not None and previous_position != position:
        if position < previous_position:
            # Car moved up (green LED)
            status_lights[car_number]['position'] = {'color': (0, 0, 255), 'time': time()}
        elif position > previous_position:
            # Car moved down (red LED)
            status_lights[car_number]['position'] = {'color': (255, 0, 0), 'time': time()}

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
            for i in range(ROWS_PER_CAR - 1):  # THIS IS RED!!!!!!!
                # Calculate when each light should turn on based on its position
                light_delay = i * delay_per_light
                
                # Only light up LEDs if their individual "turn-on" time has passed
                if elapsed_time > light_delay:
                    canvas.SetPixel(15, (row + 2) + i, r, g, b)

        else:  
            
            for i in range(ROWS_PER_CAR - 1): # THIS IS GREEN!!!!!!
                light_delay = i * delay_per_light
                if elapsed_time > light_delay:
                    canvas.SetPixel(15, row + (ROWS_PER_CAR - i), r, g, b)

    else:
        # Remove the status light after the duration
        del status_lights[car_number]['position']

def display_pit_stop_status(car_number, row, canvas, current_pit_stops):
    previous_length = previous_pit_stops.get(car_number, 0)
    current_length = len(current_pit_stops)

    # if the pit stop count has increased, show the status light
    if current_length > previous_length:
        if car_number not in status_lights:
            status_lights[car_number] = {}
        status_lights[car_number]['pit'] = {'time': time(), 'color': (0,255,0)}
        
    if car_number in status_lights and 'pit' in status_lights[car_number]:
        light_info = status_lights[car_number]['pit']
        elapsed_time = time() - light_info['time']

        if elapsed_time < PIT_STOP_STATUS_LIGHT_DURATION:
            r,g,b = light_info['color']
            canvas.SetPixel(16, row + 4, r,g,b)
            canvas.SetPixel(16, row + 5, r,g,b)
            canvas.SetPixel(17, row + 4, r,g,b)
            canvas.SetPixel(17, row + 5, r,g,b)
        else:
            del status_lights[car_number]['pit']
    
    # Update the previous pit stop length
    previous_pit_stops[car_number] = current_length

def display_dvp_status(car_number, row, canvas, car):
    is_on_dvp = car['is_on_dvp']
    car_status = car['status']

    # Only display DVP if the car is on DVP and the status is 1
    if is_on_dvp and car_status == 1:
        r,g,b = (255,0,0)

        base_r = 255
        fade_duration = 2.0
        current_time = time()

        fade_position = (math.sin((current_time % fade_duration) / fade_duration * 2 * math.pi) + 1) / 2

        r = int(base_r * fade_position)
        
        # Light On
        canvas.SetPixel(16, row + 7, r,g,b)
        canvas.SetPixel(16, row + 8, r,g,b)
        canvas.SetPixel(17, row + 7, r,g,b)
        canvas.SetPixel(17, row + 8, r,g,b)

    else:
        # Set the pixel color
        
        canvas.SetPixel(16, row + 7, 0,0,0)
        canvas.SetPixel(16, row + 8, 0,0,0)
        canvas.SetPixel(17, row + 7, 0,0,0)
        canvas.SetPixel(17, row + 8, 0,0,0)

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
            display_car_info(canvas, car, (i * ROWS_PER_CAR))

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