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


def splitBoxes(img, habits=6):
    """
    This function takes the image as input and returns the split boxes (6x31)
    """
    rows = np.vsplit(img, habits)  # SPLIT THE IMAGE INTO 6 ROWS
    boxes = []  # array to store all boxes
    
    for r in rows:
        # Calculate the width of each column
        col_width = r.shape[1] // 31
        extra_pixels = r.shape[1] % 31
        
        for i in range(31):
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
                cv2.circle(image, (x_center, y_center), circle_radius, (0, 255, 0), -1)  # -1 fills the circle

    return image



