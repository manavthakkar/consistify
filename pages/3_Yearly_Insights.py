import calendar
import io

import cv2
import numpy as np
import streamlit as st
from PIL import Image, ImageDraw, ImageFont

import auth_functions
import firebase_utils as fb_utils
import utils

st.set_page_config(page_title="Yearly Insights", page_icon="📈")

# Initialize Firebase
db = fb_utils.initialize_firestore()

def draw_bar_chart_on_image(image: np.ndarray, 
                            percentage_array: list[float], 
                            display_array: list[int], 
                            font_path: str) -> np.ndarray:
    # Define given parameters for the bar chart
    lower_left_corner = (73, 525)   # Lower left corner of the first rectangle
    width = 23                      # Width of each rectangle
    top_100_height_y = 185          # Y coordinate at 100% height
    bottom_y = 538                  # Y coordinate of the bottom
    gap_between_bars = 18           # Gap between adjacent bars

    # Calculate the full height of a bar (from bottom to top 100% height)
    full_height = bottom_y - top_100_height_y

    # Find the maximum value in the percentage array
    max_value = max(percentage_array)

    # Draw the rectangles on the original OpenCV image
    for i, percentage in enumerate(percentage_array):
        # Calculate the height of the current rectangle based on the percentage
        current_height = int(full_height * (percentage / 100.0))

        # Calculate the top-left and bottom-right coordinates for the current rectangle
        top_left_corner = (
            lower_left_corner[0] + i * (width + gap_between_bars),
            bottom_y - current_height,
        )
        bottom_right_corner = (
            top_left_corner[0] + width,
            bottom_y,
        )

        # Define the color and thickness for the filled rectangle
        if percentage == max_value:
            color = (26, 223, 232)  # RGB color for the bar with the highest value
        else:
            color = (255, 121, 137)  # Default color in BGR

        thickness = -1  # Fill the rectangle

        # Draw the filled rectangle using OpenCV
        cv2.rectangle(image, top_left_corner, bottom_right_corner, color, thickness)

    # Convert OpenCV image to PIL image for drawing text
    pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Create a draw object for the PIL image
    draw = ImageDraw.Draw(pil_image)

    # Load the custom font
    font = ImageFont.truetype(font_path, 14)

    # Draw the numbers on the bars
    for i, value in enumerate(display_array):
        # Calculate the top-left coordinates for the current rectangle (for placing text)
        top_left_corner = (
            lower_left_corner[0] + i * (width + gap_between_bars),
            bottom_y - int(full_height * (percentage_array[i] / 100.0)),
        )

        # Define the position for the text (number) to be displayed on top of each bar
        text_position = (top_left_corner[0] + 3, top_left_corner[1] - 18)

        # Check if the value is a single digit and format it
        if value < 10:
            text_position = (top_left_corner[0] + 8, top_left_corner[1] - 18)

        # Draw the text (number) using PIL
        draw.text(text_position, str(value), font=font, fill=(142, 151, 253))

    # Convert the PIL image back to OpenCV format
    output_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Return the image with the bars and numbers drawn
    return output_image

def draw_circular_progress_bar_on_image(img: np.ndarray, 
                                        percentage: float, 
                                        position: tuple[int, int], 
                                        radius: int = 58, 
                                        thickness: int =18, 
                                        bar_color: tuple[int, int, int]=(254, 168, 148)) -> np.ndarray:
    # Draw the circular background (progress bar background)
    cv2.circle(img, position, radius, (248, 74, 141), thickness)

    # Calculate the angle for the progress bar, starting from the top (-90 degrees)
    angle = int(360 * (percentage / 100))

    # Start from the top (-90 degrees), and draw the progress arc
    cv2.ellipse(img, position, (radius, radius), 0, -90, -90 + angle, bar_color, thickness)

    return img

def add_text_to_image(image: np.ndarray, 
                      text: str, 
                      font_path: str, 
                      size: int, 
                      position: tuple[int, int], 
                      color: tuple[int, int, int]) -> np.ndarray:
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

def add_centered_custom_text(image: np.ndarray, 
                             text: str, 
                             font_path: str, 
                             font_size: int, 
                             position_y: int, 
                             text_color: tuple[int, int, int]) -> np.ndarray:
    # Convert OpenCV image (BGR) to PIL image (RGB)
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Get a drawing context
    draw = ImageDraw.Draw(image_pil)

    # Load the custom font
    font = ImageFont.truetype(font_path, font_size)

    # Get the size of the text using textbbox
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]

    # Calculate x-coordinate to center the text horizontally
    image_width = image_pil.width
    x = (image_width - text_width) // 2  # Center horizontally

    # Define y-coordinate (position_y) to place the text vertically
    y = position_y

    # Draw the text on the image
    draw.text((x, y), text, font=font, fill=text_color)

    # Convert the PIL image back to an OpenCV image (BGR)
    image_with_text = cv2.cvtColor(np.array(image_pil), cv2.COLOR_RGB2BGR)

    return image_with_text

def fill_year_template(year: int, habit_name: str, days_array: list[int], habit_streak: int) -> np.ndarray:

    no_of_days = 366 if calendar.isleap(year) else 365

    # Find the number of days in each month for the given year
    days_in_months = [calendar.monthrange(year, month + 1)[1] for month in range(12)]

    # Calculate the percentage array (as integers) for each month
    percentage_array = [int((days / total_days) * 100) for days, total_days in zip(days_array, days_in_months)]

    success_rate = int(sum(days_array) / no_of_days * 100)

    # Total days habit performed in the year
    total_days = sum(days_array)

    # Load the month template image
    year_images = {
    365: "assets/365-year.png",
    366: "assets/366-year.png"}

    image = cv2.imread(year_images.get(no_of_days, "assets/365-year.png"))

    # Remove trailing zeros to match the length of available data
    while days_array and days_array[-1] == 0:
        days_array.pop()

    # Draw the bar chart on the image with numbers on each bar using the custom font
    image = draw_bar_chart_on_image(image, percentage_array, days_array, "assets/Rubik-Regular.ttf")

    # Display circular progress bar
    image = draw_circular_progress_bar_on_image(image, success_rate, (474, 690), 65, 19)

    # Display the success rate
    if success_rate < 10:
        image = add_text_to_image(image, f"{success_rate}%", "assets/Rubik-Bold.ttf", 36, (447, 670), (154, 162, 253))
    elif success_rate < 100:
        image = add_text_to_image(image, f"{success_rate}%", "assets/Rubik-Bold.ttf", 36, (437, 670), (154, 162, 253))
    else:
        image = add_text_to_image(image, f"{success_rate}%", "assets/Rubik-Bold.ttf", 36, (426, 670), (154, 162, 253))

    # Display the year on the image
    image = add_text_to_image(image, str(year), "assets/Rubik-SemiBold.ttf", 48, (32, 12), (255, 255, 255))

    # Disply total days
    if total_days < 10:
        image = add_text_to_image(image, "0" + str(total_days), "assets/Rubik-SemiBold.ttf", 36, (122, 618), (77, 87, 200))
    elif total_days < 100:
        image = add_text_to_image(image, str(total_days), "assets/Rubik-SemiBold.ttf", 36, (118, 618), (77, 87, 200))
    else:
        image = add_text_to_image(image, str(total_days), "assets/Rubik-SemiBold.ttf", 36, (106, 618), (77, 87, 200))

    # Display streak
    if habit_streak < 10:
        image = add_text_to_image(image, "0" + str(habit_streak), "assets/Rubik-SemiBold.ttf", 36, (116, 722), (77, 87, 200))
    elif habit_streak < 100:
        image = add_text_to_image(image, str(habit_streak), "assets/Rubik-SemiBold.ttf", 36, (116, 722), (77, 87, 200))
    else:
        image = add_text_to_image(image, str(habit_streak), "assets/Rubik-SemiBold.ttf", 36, (106, 722), (77, 87, 200))

    # Display the habit name
    image = add_centered_custom_text(image, habit_name, "assets/Rubik-Regular.ttf", 24, 130, (231, 216, 200))

    return image

def habit_days_count_year(data: dict, year: str, habit_name: str) -> list[int]:
    """Calculate the number of days a specific habit was performed in each month for a given year.

    Args:
        data (dict): A dictionary containing habit data organized by year, month, and habit name.
        year (str): The year for which to calculate the habit days.
        habit_name (str): The name of the habit to analyze.

    Returns:
        list: A list of integers where each element corresponds to the number of days
              the habit was performed in the respective month. The length of the list 
              is based on the availability of data in the dictionary, with missing 
              months treated as 0.
    
    Example:
        Input:
            year = "2023"
            habit_name = "Workout"
        Output:
            [23, 25, 18, 14, 25, ...]

    """
    # Define the months in order
    months_order = [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December",
    ]

    # Get the data for the given year
    year_data = data.get(year, {})

    # Initialize the result array with 0 for each month
    result = [0] * 12

    for month_index, month in enumerate(months_order):
        # Check if the month exists in the data
        if month in year_data and habit_name in year_data[month]:
            # Count the number of days the habit was performed
            result[month_index] = sum(year_data[month][habit_name])

    # Remove trailing zeros to match the length of available data
    # while result and result[-1] == 0:
    #     result.pop()

    return result

def longest_habit_streak_across_year(data: dict, year: str, habit_name: str) -> int:
    """Calculate the longest streak of consecutive days a specific habit was performed
    across all months in a given year.

    Args:
        data (dict): A dictionary containing habit data organized by year, month, and habit name.
        year (str): The year for which to calculate the longest streak.
        habit_name (str): The name of the habit to analyze.

    Returns:
        int: The length of the longest streak of consecutive days the habit was performed 
             across all months in the specified year.
    
    Example:
        Input:
            year = "2023"
            habit_name = "Workout"
        Output:
            56  

    """
    # Get the data for the given year
    year_data = data.get(year, {})

    longest_streak = 0
    current_streak = 0

    # Define the months in order
    months_order = [
        "January", "February", "March", "April",
        "May", "June", "July", "August",
        "September", "October", "November", "December",
    ]

    for month in months_order:
        # Check if the month exists in the data and contains the habit
        if month in year_data and habit_name in year_data[month]:
            habit_days = year_data[month][habit_name]
            for day in habit_days:
                if day == 1:
                    current_streak += 1
                    longest_streak = max(longest_streak, current_streak)
                else:
                    current_streak = 0
        else:
            # Reset the streak if the month or habit data is missing
            current_streak = 0

    return longest_streak

def yearly_insights_main()-> None:

    utils.add_side_logo()

    # Check if the user is authenticated
    if "user_info" not in st.session_state:
        st.warning("Please log in from the Home page to access this feature.")
        st.stop()

    st.title("Yearly Insights")

    # Display user details
    #st.image(st.session_state['user_info'].get('picture'), width=80)
    #st.write(f"**Hello, {st.session_state['user_info'].get('name')}!**")
    #st.write(f"Your email: **{st.session_state['user_info'].get('email')}**")
    st.write(f"**Logged in as :** {st.session_state['user_info'].get('email')}")

    if st.sidebar.button("Log out"):
        auth_functions.sign_out()
        st.experimental_rerun()

    user_email = st.session_state["user_info"]["email"]

    # Fetch user data dynamically
    def get_user_data(user_email):
        doc = db.collection("users").document(user_email).get()
        if doc.exists:
            return doc.to_dict()
        return None

    # Fetch user data from Firebase
    user_data = get_user_data(user_email)

    if user_data:
        # Extract available years and allow selection
        available_years = sorted(user_data.keys())
        selected_year = st.selectbox("Select Year", available_years)

        # Extract habits dynamically for the selected year
        habits_in_year = set()
        for month_data in user_data[selected_year].values():
            habits_in_year.update(month_data.keys())
        habits_in_year = sorted(habits_in_year)
        selected_habit = st.selectbox("Select Habit", habits_in_year)

        # Generate visualization button
        if st.button("Generate Year Visualization"):
            try:
                # Calculate habit days count and longest streak
                days_array = habit_days_count_year(user_data, selected_year, selected_habit)
                habit_streak = longest_habit_streak_across_year(user_data, selected_year, selected_habit)

                # Generate the year visualization
                output_image = fill_year_template(
                    int(selected_year), selected_habit.title(), days_array, habit_streak,
                )

                # Convert OpenCV image (BGR) to RGB
                img_rgb = cv2.cvtColor(output_image, cv2.COLOR_BGR2RGB)

                # Convert RGB image to PIL for Streamlit display
                img_pil = Image.fromarray(img_rgb)


                # Display the generated image
                st.image(img_rgb, caption=f"{selected_habit} - {selected_year}")

                # Convert the PIL image (img_pil) to bytes for download
                img_bytes = io.BytesIO()
                img_pil.save(img_bytes, format="PNG")  # Use the PIL image here
                img_bytes.seek(0)


                # Add a download button
                st.download_button(
                    label="Download Year Visualization",
                    data=img_bytes,
                    file_name=f"{selected_habit}_{selected_year}_Year_Visualization.png",
                    mime="image/png",
                )

            except Exception as e:
                st.error(f"An error occurred: {e}")
    else:
        st.error("No data found.")

if __name__ == "__main__":
    yearly_insights_main()
