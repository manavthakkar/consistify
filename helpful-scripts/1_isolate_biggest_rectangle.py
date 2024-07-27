'''
This script processes an image to isolate and highlight the largest rectangular contour by masking the area 
outside the rectangle with white pixels.

'''

import cv2
import numpy as np
import utils

# Example usage:
img = cv2.imread('assets/test3.jpg')

# Convert the image to grayscale
imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply GaussianBlur to the image
imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)

# Apply Canny edge detection
imgCanny = cv2.Canny(imgBlur, 40, 150) 

# Find the contours in the image
contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

# Get the biggest rectangle contour
rectCon = utils.rectContour(contours)
biggest_rectCon = utils.getCornerPoints(rectCon[0])
biggest_rectCon = utils.reorder(biggest_rectCon)

result_image = utils.mask_outside_rectangle(img, biggest_rectCon, offset=5)

cv2.imshow('Original', img)
cv2.imshow('Result', result_image)
cv2.waitKey(0)
cv2.destroyAllWindows()
