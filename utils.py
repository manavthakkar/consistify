import cv2
import numpy as np

def stackImages(imgArray,scale,lables=[]):
    rows = len(imgArray)
    cols = len(imgArray[0])
    rowsAvailable = isinstance(imgArray[0], list)
    width = imgArray[0][0].shape[1]
    height = imgArray[0][0].shape[0]
    if rowsAvailable:
        for x in range ( 0, rows):
            for y in range(0, cols):
                imgArray[x][y] = cv2.resize(imgArray[x][y], (0, 0), None, scale, scale)
                if len(imgArray[x][y].shape) == 2: imgArray[x][y]= cv2.cvtColor( imgArray[x][y], cv2.COLOR_GRAY2BGR)
        imageBlank = np.zeros((height, width, 3), np.uint8)
        hor = [imageBlank]*rows
        hor_con = [imageBlank]*rows
        for x in range(0, rows):
            hor[x] = np.hstack(imgArray[x])
            hor_con[x] = np.concatenate(imgArray[x])
        ver = np.vstack(hor)
        ver_con = np.concatenate(hor)
    else:
        for x in range(0, rows):
            imgArray[x] = cv2.resize(imgArray[x], (0, 0), None, scale, scale)
            if len(imgArray[x].shape) == 2: imgArray[x] = cv2.cvtColor(imgArray[x], cv2.COLOR_GRAY2BGR)
        hor= np.hstack(imgArray)
        hor_con= np.concatenate(imgArray)
        ver = hor
    if len(lables) != 0:
        eachImgWidth= int(ver.shape[1] / cols)
        eachImgHeight = int(ver.shape[0] / rows)
        #print(eachImgHeight)
        for d in range(0, rows):
            for c in range (0,cols):
                cv2.rectangle(ver,(c*eachImgWidth,eachImgHeight*d),(c*eachImgWidth+len(lables[d][c])*13+27,30+eachImgHeight*d),(255,255,255),cv2.FILLED)
                cv2.putText(ver,lables[d][c],(eachImgWidth*c+10,eachImgHeight*d+20),cv2.FONT_HERSHEY_COMPLEX,0.7,(255,0,255),2)
    return ver


def rectContour(contours): 
    '''
    It takes the contours as input and returns the rectangle contours

    '''
    rectCon = []                        # List to store all rectangle contours
    for i in contours:
        area = cv2.contourArea(i)
        # print(area)
        if area > 50:                    # Minimum area of rectangle
            peri = cv2.arcLength(i, True) # Calculate the perimeter of the contour (True: closed contour)
            approx = cv2.approxPolyDP(i, 0.02 * peri, True) # Approximate the polygon (how many corner points it has) (contour, resolution, closed)
            if len(approx) == 4: # If the contour has 4 corners
                rectCon.append(i)
    rectCon = sorted(rectCon, key=cv2.contourArea,reverse=True) # Sort the contours by area in descending order
    #print(len(rectCon))
    return rectCon

def getCornerPoints(cont):
    """
    This function takes the contour as input and returns the corner points of the contour

    """
    peri = cv2.arcLength(cont, True) # LENGTH OF CONTOUR
    approx = cv2.approxPolyDP(cont, 0.02 * peri, True) # APPROXIMATE THE POLY TO GET CORNER POINTS
    return approx

def reorder(myPoints):
    """
    This function takes the points as input and returns the arranged points (of the rectangle)
    for example, it will return the points in the following order:
    [top-left, top-right, bottom-left, bottom-right]
    
    """
    myPoints = myPoints.reshape((4, 2)) # REMOVE EXTRA BRACKET
    #print(myPoints)
    myPointsNew = np.zeros((4, 1, 2), np.int32) # NEW MATRIX WITH ARRANGED POINTS
    add = myPoints.sum(1)
    #print(add)
    #print(np.argmax(add))
    myPointsNew[0] = myPoints[np.argmin(add)]  #[0,0]    # origin point has the smallest sum
    myPointsNew[3] =myPoints[np.argmax(add)]   #[w,h]    # w+h gives the largest sum
    diff = np.diff(myPoints, axis=1)
    myPointsNew[1] =myPoints[np.argmin(diff)]  #[w,0]    
    myPointsNew[2] = myPoints[np.argmax(diff)] #[h,0]    

    return myPointsNew


def splitBoxes(img, rows=6, cols=31):
    """
    This function takes the image as input and returns the split boxes (rowsxcols)
    """
    rows = np.vsplit(img, rows)  # SPLIT THE IMAGE INTO GIVEN ROWS
    boxes = []  # array to store all boxes
    
    for r in rows:
        # Calculate the width of each column
        col_width = r.shape[1] // cols
        extra_pixels = r.shape[1] % cols
        
        for i in range(cols):
            if i < extra_pixels:
                col = r[:, i*col_width + i:(i+1)*col_width + i + 1]  # Add an extra pixel for the first 'extra_pixels' columns
            else:
                col = r[:, i*col_width + extra_pixels:(i+1)*col_width + extra_pixels]
            boxes.append(col)
    
    return boxes

def draw_circles_on_image(image, binary_array):
    """
    Draws circles on the provided image based on the binary_array where 1s indicate the positions of the circles.

    Parameters:
    - image: np.array (The image on which to draw the circles)
    - binary_array: np.array (A binary array indicating where to draw circles)

    Returns:
    - np.array: The image with circles drawn on it.
    """
    # Get the dimensions of the image and the binary array
    img_height, img_width = image.shape[:2]
    array_height, array_width = binary_array.shape

    # Calculate the dimensions of each grid cell for the circles
    cell_width = img_width // array_width
    cell_height = img_height // array_height
    circle_radius = min(cell_width, cell_height) // 2  # Radius based on the smaller dimension

    # Loop through the binary array to draw circles at positions with 1s
    for i in range(array_height):
        for j in range(array_width):
            if binary_array[i, j] == 1:
                # Calculate the center of the circle
                x_center = j * cell_width + cell_width // 2
                y_center = i * cell_height + cell_height // 2
                # Draw the circle on the image
                cv2.circle(image, (x_center, y_center), circle_radius, (0, 0, 255), -1)  # -1 fills the circle

    return image

def apply_stats_to_image(image, stats, suffix_text="", vertical_adjustment_factor=0.1):
    """
    Apply stats to an image with evenly distributed boxes and return the annotated image.

    Args:
    image (np.array): Image to annotate.
    stats (list of int): List of stats to display on the image.
    suffix_text (str): Suffix text to display after each stat.
    vertical_adjustment_factor (float): Factor to adjust vertical position of text.

    Returns:
    np.array: Annotated image as a numpy array.
    """

    # Calculate the width of each box assuming they are evenly spaced
    box_width = image.shape[1] // len(stats)

    # Define font, size, and color for the text
    font = cv2.FONT_HERSHEY_SIMPLEX
    font_scale_large = 1
    font_scale_small = 0.5
    font_color = (255, 0, 0)  
    thickness = 2

    # Place each stat dynamically adjusted above the center of each box
    for i, stat in enumerate(stats):
        number_text = str(stat)
        total_text = number_text + " " + suffix_text
        
        # Calculate total text size
        total_size_large = cv2.getTextSize(number_text, font, font_scale_large, thickness)[0]
        total_size_small = cv2.getTextSize(suffix_text, font, font_scale_small, thickness)[0]
        total_width = total_size_large[0] + total_size_small[0] + 5  # 5 pixels spacing

        text_x = int((box_width * i) + (box_width - total_width) / 2)
        center_y = int(image.shape[0] / 2)
        vertical_shift = int(image.shape[0] * vertical_adjustment_factor)
        text_y = center_y - vertical_shift  # Move text up by a fraction of the image height

        # Calculate position for the suffix text
        suffix_x = text_x + total_size_large[0] + 5  # Adjust x position to be after the number
        suffix_y = text_y + total_size_large[1] - total_size_small[1]  # Adjust y position to be in line with the number

        # Put the number and the suffix text on the image
        cv2.putText(image, number_text, (text_x, text_y), font, font_scale_large, font_color, thickness)
        if suffix_text:
            cv2.putText(image, suffix_text, (suffix_x, suffix_y), font, font_scale_small, font_color, thickness)

    return image

def count_total_days(habit_array):
    # Sum each row to get the number of days each habit was performed
    days_performed = np.sum(habit_array, axis=1)
    return days_performed

def get_longest_streak(habit_array):
    """
    Calculate the longest streak of consecutive days each habit was performed.

    Parameters:
    habit_array (numpy.ndarray): A 2D numpy array where each row represents a habit and each column represents a day of the month. 
                                 Elements are 1 if the habit was performed on that day and 0 otherwise.

    Returns:
    numpy.ndarray: An array where each element represents the longest streak of consecutive days the corresponding habit was performed.
    """
    def calculate_streak(row):
        max_streak = 0
        current_streak = 0
        for day in row:
            if day == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 0
        return max_streak

    streaks = np.array([calculate_streak(row) for row in habit_array])
    return streaks

def detect_month(array):
    """
    This function takes a 2D numpy array where each row represents values for 
    four consecutive months and returns the month number (1-based index) and 
    the name of the month that has the highest value.

    Parameters:
    array (numpy.ndarray): A 2D numpy array where:
                           - The first row represents values for January, February, March, and April.
                           - The second row represents values for May, June, July, and August.
                           - The third row represents values for September, October, November, and December.

    Returns:
    tuple: A tuple containing:
           - int: The month number (1-based index) with the highest value.
                  For example, 1 represents January, 2 represents February, and so on.
           - str: The name of the month with the highest value.
    
    Example:
    >>> data = np.array([[454., 425., 462., 397.],
                         [395., 711., 180., 315.],
                         [558., 372., 390., 439.]])
    >>> month_with_highest_value(data)
    (6, 'June')
    """
    # List of month names
    month_names = [
        'January', 'February', 'March', 'April',
        'May', 'June', 'July', 'August',
        'September', 'October', 'November', 'December'
    ]
    
    # Flatten the array to get all values in a single list
    flattened_array = array.flatten()
    # Find the index of the maximum value
    max_index = np.argmax(flattened_array)
    # Convert the index to month (1-based index)
    month = max_index + 1
    # Get the name of the month
    month_name = month_names[max_index]
    
    return month, month_name

def draw_month_on_image(image, month):
    """
    Annotates an image by drawing a circle in a grid cell corresponding to a specified month.

    This function divides an image into a grid of 3 rows and 4 columns, where each cell in the grid
    corresponds to a month of the year from January (top-left) to December (bottom-right). It then
    draws a red circle in the cell that corresponds to the given month number.

    Parameters:
    - image (numpy.ndarray): The image to annotate, represented as a NumPy array. The image
                             should be loaded using OpenCV and passed directly to the function.
    - month (int): The month number (1 for January, 12 for December) for which the circle
                   will be drawn. Must be in the range 1 to 12.

    Returns:
    - image (numpy.ndarray): The annotated image as a numpy array, which can be displayed or saved
                             using OpenCV functions.

    Raises:
    - ValueError: If the month number is not within the valid range of 1 to 12.

    """
    if not (1 <= month <= 12):
        raise ValueError("Month must be between 1 and 12.")

    # Get image dimensions
    height, width = image.shape[:2]
    
    # Calculate cell width and height
    cell_width = width // 4
    cell_height = height // 3
    
    # Calculate the grid position based on the month
    row = (month - 1) // 4
    column = (month - 1) % 4
    
    # Calculate the center of the cell
    center_x = column * cell_width + cell_width // 2
    center_y = row * cell_height + cell_height // 2
    
    # Radius of the circle
    radius = min(cell_width, cell_height) // 5
    
    # Circle color (BGR format) and thickness
    circle_color = (255, 0, 0)  # BGR
    thickness = 5
    
    # Draw the circle
    cv2.circle(image, (center_x, center_y), radius, circle_color, thickness)
    
    # Return the modified image
    return image




