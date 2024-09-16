# utils.py

color_map = {
        'white': (255, 255, 255),
        'yellow': (255, 0, 255),
        'red': (255, 0, 0),
        'green': (0, 0, 255),
        'blue': (0, 255, 0),
        'black': (0, 0, 0),
        'orange':(255, 17, 81)
        # Add more colors as needed...
    }

def get_color(color):
    return color_map.get(color, color_map['white'])  # Default

def get_driver_status_color(status):
    """Returns the appropriate color for the driver's status."""
    status_colors = {
        1: 'white',  # Running
        2: 'yellow',  # In Garage
        3: 'red',    # DNF (Did Not Finish)
    }
    return get_color(status_colors.get(status, 'white'))  # Default

def get_flag_state_color(flag_state):
    flag_colors = {
        1: 'white',  # White - Green
        2: 'yellow',    # Yellow - Caution
        3: 'red',      # Red
        4: 'white',  # Finish
        6: 'white',  # Stop (unknown color)
        8: 'orange',    # Orange - Warm Up
        9: 'white'   # Not Active
    }
    return get_color(flag_colors.get(flag_state, 'white'))  # Default