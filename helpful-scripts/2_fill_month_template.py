# Add custom font to the image (provide proper path to the image and font)
 
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np

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

# Example usage
image = cv2.imread('31-month.png')  # provide the path to the image
text = "OCTOBER' 24"
font_path = 'Rubik-SemiBold.ttf'
size = 48
position =  (29, 16)  # X and Y coordinates
color = (255, 255, 255)  # White color

# Array representing where circles should be drawn
circle_array = [
    1, 1, 1, 1, 1, 0, 1,
    1, 1, 1, 1, 1, 1, 0,
    1, 0, 1, 1, 1, 1, 1,
    1, 1, 0, 1, 1, 1, 1,
    1, 0, 1
]

# Add text to image
image_with_text = add_text_to_image(image, text, font_path, size, position, color)

image_with_text = add_text_to_image(image_with_text, "Exercise", 'Rubik-Regular.ttf', 32, (29, 82), (148, 168, 254))

image_with_text = add_text_to_image(image_with_text, "26", font_path, 36, (106, 590), (148, 168, 254))

image_with_text = add_text_to_image(image_with_text, "October ' 24", 'Rubik-Medium.ttf', 24, (208, 686), (77, 87, 200))

image_with_text = add_text_to_image(image_with_text, "7", 'Rubik-Bold.ttf', 24, (430, 686), (77, 87, 200))

image_with_text = add_text_to_image(image_with_text, "46", 'Rubik-Bold.ttf', 24, (430, 776), (77, 87, 200))

image_with_text = add_text_to_image(image_with_text, "87 %", 'Rubik-Bold.ttf', 36, (416, 515), (154, 162, 253))

image_with_text = draw_circular_progress_bar_on_image(image_with_text, 87, (455, 535))

# Draw circles on the image
image_with_text = draw_circles_on_image(image_with_text, circle_array)

# Display the image using OpenCV
cv2.imshow('October 2024', image_with_text)
cv2.waitKey(0)
cv2.destroyAllWindows()