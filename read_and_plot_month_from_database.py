"""
This script reads the habit data for a specific month and year from Firestore and
displays the corresponding month template with the habit data filled in.
"""

from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
import calendar

import firebase_admin
from firebase_admin import credentials, firestore

# Check if the app is already initialized
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase.json")
    firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

def add_text_to_image(image, text, font_path, size, position, color):
    # Convert the image from OpenCV (BGR) to PIL (RGB) format
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Initialize ImageDraw
    draw = ImageDraw.Draw(image_pil)

    # Load your custom TTF font
    font = ImageFont.truetype(font_path, size=size)

    # Add text to image
    draw.text(position, text, font=font, fill=color)

    # Convert the image back from PIL (RGB) to OpenCV (BGR)
    return cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

def draw_circular_progress_bar_on_image(img, percentage, position, bar_color=(254, 168, 148)):
    # Load the existing image

    # Determine the size based on the position you want the circle
    radius = 58 #min(img.shape[0], img.shape[1]) // 6  # Radius of the circle based on the image size
    thickness = 18 #int(radius / 4)  # Thickness of the progress bar based on the radius

    # Draw the circular background (progress bar background)
    cv2.circle(img, position, radius, (248, 74, 141), thickness)

    # Calculate the angle for the progress bar, starting from the top (-90 degrees)
    angle = int(360 * (percentage / 100))

    # Start from the top (-90 degrees), and draw the progress arc
    cv2.ellipse(img, position, (radius, radius), 0, -90, -90 + angle, bar_color, thickness)

    return img

def draw_circles_on_image(image, circle_array):
    # Define circle parameters
    start_x = 55                      # Initial x-coordinate of the first circle
    start_y = 169                     # Initial y-coordinate of the first row
    radius = 23                       # Radius of the circles
    color = (0, 255, 0)               # Color in BGR (Green in this case)
    thickness = -1                    # Thickness of the circle (-1 to fill the circle)
    center_to_center_distance_x = 81  # Center-to-center distance between adjacent circles in the same row
    center_to_center_distance_y = 76  # Center-to-center distance between rows

    # Draw circles based on the array values
    for idx, val in enumerate(circle_array):
        if val == 1:
            row = idx // 7
            col = idx % 7
            center_coordinates = (
                start_x + col * center_to_center_distance_x,
                start_y + row * center_to_center_distance_y
            )
            cv2.circle(image, center_coordinates, radius, color, thickness)

    # Return the image with the circles drawn
    return image

def longest_streak(arr):
    """
    Finds the longest streak of consecutive 1's in a binary array.

    Args:
    arr (list): A binary list containing only 0s and 1s.

    Returns:
    int: The length of the longest streak of 1's.
    """
    max_streak = 0
    current_streak = 0

    for num in arr:
        if num == 1:
            current_streak += 1
            max_streak = max(max_streak, current_streak)
        else:
            current_streak = 0

    return max_streak

def fill_month_template(month, year, habit_name, total_days, habit_array):
    # Create the heading for the month
    heading = f"{calendar.month_name[month].upper()} '{str(year)[-2:]}"

    # Get no. of days in the month
    days_in_month = calendar.monthrange(year, month)[1]

    # Load the month template image
    month_images = {
    28: 'assets/28-month-1.png',
    29: 'assets/29-month-1.png',
    30: 'assets/30-month-1.png',
    31: 'assets/31-month-1.png'}

    image = cv2.imread(month_images.get(days_in_month, 'assets/31-month.png'))

    # Limit the circle array to the number of days in the month
    habit_array = habit_array[:days_in_month]

    # Calculate the number of days the habit was performed
    days_habit_performed = sum(habit_array)

    # Calculate the longest streak of the habit in the month
    habit_streak = longest_streak(habit_array)

    success_rate = int(days_habit_performed / days_in_month * 100)

    # Add text to the image
    image = add_text_to_image(image, heading, 'assets/Rubik-SemiBold.ttf', 48, (29, 16), (255, 255, 255))
    image = add_text_to_image(image, habit_name, 'assets/Rubik-Regular.ttf', 32, (29, 82), (148, 168, 254))

    # Adjust the position of the text based on the number of digits
    if days_habit_performed < 10:
        image = add_text_to_image(image, str(days_habit_performed), 'assets/Rubik-SemiBold.ttf', 36, (123, 590), (148, 168, 254))
    else:
        image = add_text_to_image(image, str(days_habit_performed), 'assets/Rubik-SemiBold.ttf', 36, (106, 590), (148, 168, 254))

    if habit_streak < 10:
        image = add_text_to_image(image, str(habit_streak), 'assets/Rubik-Bold.ttf', 24, (444, 686), (77, 87, 200))
    else:
        image = add_text_to_image(image, str(habit_streak), 'assets/Rubik-Bold.ttf', 24, (430, 686), (77, 87, 200))

    if total_days < 10:
        image = add_text_to_image(image, str(total_days), 'assets/Rubik-Bold.ttf', 24, (444, 776), (77, 87, 200))
    elif total_days < 100:
        image = add_text_to_image(image, str(total_days), 'assets/Rubik-Bold.ttf', 24, (430, 776), (77, 87, 200))
    else:
        image = add_text_to_image(image, str(total_days), 'assets/Rubik-Bold.ttf', 24, (416, 776), (77, 87, 200))

    if success_rate < 10:
        image = add_text_to_image(image, str(success_rate) + " %", 'assets/Rubik-Bold.ttf', 36, (424, 515), (154, 162, 253))
    elif success_rate < 100:
        image = add_text_to_image(image, str(success_rate) + " %", 'assets/Rubik-Bold.ttf', 36, (416, 515), (154, 162, 253))
    else:
        image = add_text_to_image(image, str(success_rate) + " ", 'assets/Rubik-Bold.ttf', 36, (420, 515), (154, 162, 253))


    # Draw circular progress bar on the image
    image = draw_circular_progress_bar_on_image(image, success_rate, (455, 535))

    # Draw circles on the image
    image = draw_circles_on_image(image, habit_array)

    return image

def get_habit_data_and_cumulative_sum(data, year, month, habit):
    """
    Retrieves the binary array for a specific habit in a given year and month,
    along with the cumulative number of days the habit was performed from January
    to the specified month.

    Parameters:
    - data (dict): The dictionary containing habit data.
    - year (str): The year as a string (e.g., '2024').
    - month (str): The month as a string (e.g., 'March').
    - habit (str): The habit as a string (e.g., 'Workout').

    Returns:
    - tuple: (binary_array, cumulative_sum)
      - binary_array: The binary array corresponding to the habit for the specified month.
      - cumulative_sum: The cumulative sum of days the habit was performed from January to the specified month.
    - tuple of (None, None): If the year, month, or habit is not found.
    """
    try:
        # List of months in order to calculate cumulative sum
        months_in_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                           'July', 'August', 'September', 'October', 'November', 'December']
        
        if year not in data:
            raise KeyError(f"Year '{year}' not found in the data.")
        
        if month not in months_in_order:
            raise ValueError(f"Invalid month '{month}'.")
        
        if month not in data[year]:
            raise KeyError(f"Month '{month}' not found in the data for year '{year}'.")
        
        if habit not in data[year][month]:
            raise KeyError(f"Habit '{habit}' not found in the data for year '{year}', month '{month}'.")
        
        # Binary array for the specified month
        binary_array = data[year][month][habit]

        # Cumulative sum calculation
        cumulative_sum = 0
        for m in months_in_order:
            if m in data[year]:
                if habit in data[year][m]:
                    cumulative_sum += sum(data[year][m][habit])
            if m == month:
                break

        return binary_array, cumulative_sum
    
    except KeyError as e:
        print(f"KeyError: {e}")
        return None, None
    except ValueError as e:
        print(f"ValueError: {e}")
        return None, None

def get_month_number(month_name):
    import calendar
    try:
        month_name = month_name.capitalize()  
        month_number = list(calendar.month_name).index(month_name)
        return month_number
    except ValueError:
        return "Invalid month name"


if __name__ == "__main__":

    # Example usage
    month = "February"          # from user
    year = 2024                 # from user
    habit_name = "Read"      # from user

    month_number = get_month_number(month)

    # Retrieve user data from Firestore
    def get_user_data(user_id):
        doc = db.collection("users").document(user_id).get()
        if doc.exists:
            return doc.to_dict()
        else:
            return None
        
    user_id = "123456789"       # will be obtained from Google Authentication

    # retrieve all data from the user_id
    user_data = get_user_data(user_id)

    # Retrieve the binary array for the habit in the specified month
    habit_array, total_days = get_habit_data_and_cumulative_sum(user_data, str(year), month, habit_name)

    # Fill the month template
    filled_image = fill_month_template(month_number, year, habit_name, total_days, habit_array)

    # Display the image using OpenCV
    cv2.imshow(f'{month} / {year}', filled_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()