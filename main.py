import cv2
import numpy as np
import utils

##################### Constants #####################
imgWidth = 744                      # should be divisible by 31 (days)
imgHeight = 744                     # should be divisible by 6 (habits)
habits = 6
threshold = 1000                    # Threshold for checking if a box is marked or not

img_path = 'test.jpg'

# Load the image
img = cv2.imread(img_path)

# Resize the image
scale_percent = 60
width = int(img.shape[1] * scale_percent / 100)
height = int(img.shape[0] * scale_percent / 100)
dim = (width, height)
img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)

# Create some copies of the image
imgContours = img.copy()

# Convert the image to grayscale
imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply GaussianBlur to the image
imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)

# Apply Canny edge detection
imgCanny = cv2.Canny(imgBlur, 10, 50)

# Find the contours in the image
contours, hierarchy = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

# Draw the contours
cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 3)

# Get the rectangle contours
rectCon = utils.rectContour(contours)
biggest_rectCon = utils.getCornerPoints(rectCon[0])
second_biggest_rectCon = utils.getCornerPoints(rectCon[1])
third_biggest_rectCon = utils.getCornerPoints(rectCon[2])

if biggest_rectCon.size != 0 and second_biggest_rectCon.size != 0 and third_biggest_rectCon.size != 0:
    cv2.drawContours(imgContours, biggest_rectCon, -1, (255, 50, 255), 20)
    cv2.drawContours(imgContours, second_biggest_rectCon, -1, (255, 0, 0), 20)
    cv2.drawContours(imgContours, third_biggest_rectCon, -1, (0, 0, 255), 20)

    biggest_rectCon = utils.reorder(biggest_rectCon)
    second_biggest_rectCon = utils.reorder(second_biggest_rectCon)
    third_biggest_rectCon = utils.reorder(third_biggest_rectCon)

    # Warp the image
    pt1 = np.float32(biggest_rectCon)
    pt2 = np.float32([[0, 0], [imgWidth, 0], [0, imgHeight], [imgWidth, imgHeight]])
    matrix = cv2.getPerspectiveTransform(pt1, pt2)
    imgWarpColored = cv2.warpPerspective(img, matrix, (imgWidth, imgHeight))
    cv2.imshow('Warped Image', imgWarpColored)

    # Warp the second biggest rectangle
    statImgWidth = 1200
    statImgHeight = 154
    ptS1 = np.float32(second_biggest_rectCon)
    ptS2 = np.float32([[0, 0], [statImgWidth, 0], [0, statImgHeight], [statImgWidth, statImgHeight]])
    matrixS = cv2.getPerspectiveTransform(ptS1, ptS2)
    imgWarpColoredS = cv2.warpPerspective(img, matrixS, (statImgWidth, statImgHeight))
    cv2.imshow('Warped Image Second', imgWarpColoredS)

    # Warp the third biggest rectangle
    monthImgWidth = 355
    monthImgHeight = 148
    ptT1 = np.float32(third_biggest_rectCon)
    ptT2 = np.float32([[0, 0], [monthImgWidth, 0], [0, monthImgHeight], [monthImgWidth, monthImgHeight]])
    matrixT = cv2.getPerspectiveTransform(ptT1, ptT2)
    imgWarpColoredT = cv2.warpPerspective(img, matrixT, (monthImgWidth, monthImgHeight))
    cv2.imshow('Warped Image Third', imgWarpColoredT)

    # Convert the warped image of the biggest rect contour to grayscale and apply thresholding
    imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
    imgThresh = cv2.threshold(imgWarpGray, 170, 255, cv2.THRESH_BINARY_INV)[1]
    cv2.imshow('Thresh Image', imgThresh)

    # Get the boxes from the biggest rect contour warped image 
    boxes = utils.splitBoxes(imgThresh, habits)
    cv2.imshow('Boxes Image', boxes[2])   # Display the third box
    # print(len(boxes))                   # 186 boxes (6x31)
    # print(boxes[0].shape)               # (124, 24)         i.e. 124 x 6 = 744 and 24 x 31 = 744

    # Get the non-zero pixel values of each box
    myPixelVal = np.zeros((habits, 31))  # 6x31
    countR = 0
    countC = 0
    for image in boxes:
        totalPixels = cv2.countNonZero(image)
        myPixelVal[countR][countC] = totalPixels
        countC += 1
        if countC == 31:
            countR += 1
            countC = 0
    print(myPixelVal)
    # print("The size of the pixel values array: ", myPixelVal.shape)         # (6,31)

    # Create a new array with 1 where the pixel value is greater than threshold, and 0 otherwise (Check if marked or not)
    binary_array = np.where(myPixelVal > threshold, 1, 0)
    print(binary_array)

    # Display the marked boxes
    imgMarked = imgWarpColored.copy()
    imgMarked = utils.draw_circles_on_image(imgMarked, binary_array)
    cv2.imshow('Marked Image', imgMarked)

    # Create a black image of same shape of imgWarpColored to display circles
    imgRawCircles = np.zeros_like(imgWarpColored)
    imgRawCircles = utils.draw_circles_on_image(imgRawCircles, binary_array)
    cv2.imshow('Raw Circles Image', imgRawCircles)

    # Inverse warp the raw circles image (This will be a black image with circles)
    invMatrix = cv2.getPerspectiveTransform(pt2, pt1)
    imgInvWarp = cv2.warpPerspective(imgRawCircles, invMatrix, (img.shape[1], img.shape[0])) # img.shape[1] = width, img.shape[0] = height
    cv2.imshow('Inverse Warped Image', imgInvWarp)

    # Add the inverse warped image to the original image
    # imgFinal = cv2.addWeighted(img, 1, imgInvWarp, 1.5, 10)
    # cv2.imshow('Final Image', imgFinal)

    # Overlay using mask (Replace only the non-zero pixels of imgInvWarp with the original image pixels)
    imgFinal = img.copy()
    mask = np.any(imgInvWarp != 0, axis=-1)
    imgFinal[mask] = imgInvWarp[mask]
    
    cv2.imshow('Final Image', imgFinal)
    

# cv2.imshow('Original Image', img)
# cv2.imshow('Gray Image', imgGray)
# cv2.imshow('Blur Image', imgBlur)
# cv2.imshow('Canny Image', imgCanny)
cv2.imshow('Contours Image', imgContours)
cv2.waitKey(0)