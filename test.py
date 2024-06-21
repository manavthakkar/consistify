import cv2
import numpy as np
import utils

habits = 6
threshold = 550 # Threshold for checking if a box is marked or not

# Load the image
img = cv2.imread('habit-tracker-marked.jpg')  


# Preprocess the image
# img = cv2.resize(img, (1024, 576)) 
imgContours = img.copy()
imgBlank = np.zeros_like(img) # Create a blank image with the same dimensions as the original image
imgBiggestContours = img.copy() # for displaying the three biggest contours

# Convert the image to grayscale
gray_image = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 

# Apply GaussianBlur to the image
blurred_image = cv2.GaussianBlur(gray_image, (5, 5), 0) # (5, 5) is the kernel size and 0 is the standard deviation

# Apply Canny edge detection
canny_image = cv2.Canny(blurred_image, 10, 50) # 100 is the lower threshold and 200 is the upper threshold

# Find the contours in the image
contours, hierarchy = cv2.findContours(canny_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 3)

# Get the rectangle contours
rectCon = utils.rectContour(contours)
# print("Number of rectangle contours: ",len(rectCon)) # Number of rectangle contours
biggest_rectCon = utils.getCornerPoints(rectCon[0])
second_biggest_rectCon = utils.getCornerPoints(rectCon[1])
third_biggest_rectCon = utils.getCornerPoints(rectCon[2])

if biggest_rectCon.size != 0 and second_biggest_rectCon.size != 0 and third_biggest_rectCon.size != 0:
    cv2.drawContours(imgBiggestContours, biggest_rectCon, -1, (255, 50, 255), 20)
    cv2.drawContours(imgBiggestContours, second_biggest_rectCon, -1, (255, 0, 0), 20)
    cv2.drawContours(imgBiggestContours, third_biggest_rectCon, -1, (0, 0, 255), 20)

    biggest_rectCon = utils.reorder(biggest_rectCon)
    second_biggest_rectCon = utils.reorder(second_biggest_rectCon)
    third_biggest_rectCon = utils.reorder(third_biggest_rectCon)

    # Warp the image
    pt1 = np.float32(biggest_rectCon)
    pt2 = np.float32([[0, 0], [1024, 0], [0, 576], [1024, 576]])
    matrix = cv2.getPerspectiveTransform(pt1, pt2)
    imgWarpColored = cv2.warpPerspective(img, matrix, (1024, 576))
    cv2.imshow('Warped Image', imgWarpColored)

    # Warp the second biggest rectangle
    ptS1 = np.float32(second_biggest_rectCon)
    ptS2 = np.float32([[0, 0], [1024, 0], [0, 576], [1024, 576]])
    matrixS = cv2.getPerspectiveTransform(ptS1, ptS2)
    imgWarpColoredS = cv2.warpPerspective(img, matrixS, (1024, 576))
    # cv2.imshow('Warped Image Second', imgWarpColoredS)

    # Warp the third biggest rectangle
    ptT1 = np.float32(third_biggest_rectCon)
    ptT2 = np.float32([[0, 0], [1024, 0], [0, 576], [1024, 576]])
    matrixT = cv2.getPerspectiveTransform(ptT1, ptT2)
    imgWarpColoredT = cv2.warpPerspective(img, matrixT, (1024, 576))
    # cv2.imshow('Warped Image Third', imgWarpColoredT)

    # Convert the warped image to grayscale
    imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
    imgWarpGrayS = cv2.cvtColor(imgWarpColoredS, cv2.COLOR_BGR2GRAY)
    imgWarpGrayT = cv2.cvtColor(imgWarpColoredT, cv2.COLOR_BGR2GRAY)

    # Apply threshold to the warped image
    imgThresh = cv2.threshold(imgWarpGray, 170, 255, cv2.THRESH_BINARY_INV)[1]
    imgThreshS = cv2.threshold(imgWarpGrayS, 170, 255, cv2.THRESH_BINARY_INV)[1]
    imgThreshT = cv2.threshold(imgWarpGrayT, 170, 255, cv2.THRESH_BINARY_INV)[1]

    boxes = utils.splitBoxes(imgThresh)

    # Display the boxes one by one
    # for i in range(0, 185):
    #     cv2.imshow('test', boxes[i]) # 0 - 185 boxes
    #     cv2.waitKey(0)

    # Getting the non-zero pixel values of each box
    countR = 0
    countC = 0
    myPixelVal = np.zeros((habits, 31))
    for image in boxes:
        totalPixels = cv2.countNonZero(image)
        myPixelVal[countR][countC] = totalPixels
        countC += 1
        if countC == 31:
            countR += 1
            countC = 0
    print(myPixelVal)     # Print the non-zero pixel values of each box
    # print("The size of the pixel values array: ", myPixelVal.shape)         # (6,31)

    # Create a new array with 1 where the pixel value is greater than threshold, and 0 otherwise (Check if marked or not)
    binary_array = np.where(myPixelVal > threshold, 1, 0)
    print(binary_array)

    # Display the marked boxes
    imgMarked = imgWarpColored.copy()
    imgMarked = utils.draw_circles_on_image(imgMarked, binary_array)
    cv2.imshow('Marked Image', imgMarked)
    

# Display the image
#cv2.imshow('Original Image', img)

imgArray = ([img, gray_image, blurred_image, canny_image],
            [imgContours, imgBiggestContours, imgBlank, imgBlank])

# Display the stacked images
stacked_images = utils.stackImages(imgArray, 0.5)
#cv2.imshow('Stacked Images', stacked_images)

cv2.waitKey(0)