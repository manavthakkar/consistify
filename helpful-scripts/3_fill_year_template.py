import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
import calendar

def draw_bar_chart_on_image(image, percentage_array, display_array, font_path):
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
            bottom_y - current_height
        )
        bottom_right_corner = (
            top_left_corner[0] + width,
            bottom_y
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
            bottom_y - int(full_height * (percentage_array[i] / 100.0))
        )

        # Define the position for the text (number) to be displayed on top of each bar
        text_position = (top_left_corner[0] + 3, top_left_corner[1] - 18)

        # Draw the text (number) using PIL
        draw.text(text_position, str(value), font=font, fill=(142, 151, 253))

    # Convert the PIL image back to OpenCV format
    output_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    # Return the image with the bars and numbers drawn
    return output_image

def draw_circular_progress_bar_on_image(img, percentage, position, radius = 58, thickness=18, bar_color=(254, 168, 148)):
    # Load the existing image

    # Determine the size based on the position you want the circle
    #radius = 58 #min(img.shape[0], img.shape[1]) // 6  # Radius of the circle based on the image size
    #thickness = 18 #int(radius / 4)  # Thickness of the progress bar based on the radius

    # Draw the circular background (progress bar background)
    cv2.circle(img, position, radius, (248, 74, 141), thickness)

    # Calculate the angle for the progress bar, starting from the top (-90 degrees)
    angle = int(360 * (percentage / 100))

    # Start from the top (-90 degrees), and draw the progress arc
    cv2.ellipse(img, position, (radius, radius), 0, -90, -90 + angle, bar_color, thickness)

    return img

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

def add_centered_custom_text(image, text, font_path, font_size, position_y, text_color):
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

def fill_year_template(year, habit_name, percentage_array, display_array, total_days, success_rate, habit_streak):

    no_of_days = 366 if calendar.isleap(year) else 365

    # Load the month template image
    year_images = {
    365: 'assets/365-year.png',
    366: 'assets/366-year.png'}

    image = cv2.imread(year_images.get(no_of_days, 'assets/365-year.png'))

    # Draw the bar chart on the image with numbers on each bar using the custom font
    image = draw_bar_chart_on_image(image, percentage_array, display_array, 'assets/Rubik-Regular.ttf')

    # Display circular progress bar
    image = draw_circular_progress_bar_on_image(image, success_rate, (474, 690), 65, 19)

    image = add_text_to_image(image, f'{success_rate}%', 'assets/Rubik-Bold.ttf', 36, (439, 670), (154, 162, 253))

    # Display the year on the image
    image = add_text_to_image(image, str(year), 'assets/Rubik-SemiBold.ttf', 48, (32, 12), (255, 255, 255))

    # Disply total days
    image = add_text_to_image(image, str(total_days), 'assets/Rubik-SemiBold.ttf', 36, (99, 618), (77, 87, 200))

    # Display streak
    image = add_text_to_image(image, str(habit_streak), 'assets/Rubik-SemiBold.ttf', 36, (110, 722), (77, 87, 200))

    # Display the habit name
    image = add_centered_custom_text(image, habit_name, 'assets/Rubik-Regular.ttf', 24, 130, (231, 216, 200))

    return image


percentage_array = [74, 45, 80, 84, 80, 87, 74, 77, 87, 97, 80, 90] # Array representing the height percentage for each month
display_array =    [23, 14, 25, 26, 25, 27, 23, 24, 27, 30, 25, 28] # Array representing the numbers to be displayed on each bar
success_rate = 81                                                   # Success rate for the habit  (in percentage)
habit_streak = 52                                                   # Current habit streak
total_days = 297                                                    # Total days habit performed in the year
year = 2022                                                         # Year
habit_name = 'Exercise'                                             # Name of the habit

output_image = fill_year_template(year, habit_name, percentage_array, display_array, total_days, success_rate, habit_streak)

# Display the image with the bar chart and numbers
cv2.imshow(f'{year}', output_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
