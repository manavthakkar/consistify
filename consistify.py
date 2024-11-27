import cv2
import numpy as np
import utils
import calendar

##################### Constants #####################
habits = 6
threshold = 900                    # Threshold for checking if a box is marked or not
year = 2024

img_path = 'assets/testimg2.jpeg'

# Load the image
img = cv2.imread(img_path)

# Resize the image
scale_percent = 30
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
cv2.imshow('Canny Image', imgCanny)

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
    markerImgWidth = 534                 # must be divisible by 6 (columns)  # values obtained from figma
    markerImgHeight = 558                # must be divisible by 31 (rows)
    pt1 = np.float32(biggest_rectCon)
    pt2 = np.float32([[0, 0], [markerImgWidth, 0], [0, markerImgHeight], [markerImgWidth, markerImgHeight]])
    matrix = cv2.getPerspectiveTransform(pt1, pt2)
    imgWarpColored = cv2.warpPerspective(img, matrix, (markerImgWidth, markerImgHeight))
    #cv2.imshow('Warped Image', imgWarpColored)

    # Warp the second biggest rectangle
    statImgWidth = 564 #654                 # must be divisible by 6 (columns) # originally 564 from figma
    statImgHeight = 92
    ptS1 = np.float32(second_biggest_rectCon)
    ptS2 = np.float32([[0, 0], [statImgWidth, 0], [0, statImgHeight], [statImgWidth, statImgHeight]])
    matrixS = cv2.getPerspectiveTransform(ptS1, ptS2)
    imgWarpColoredS = cv2.warpPerspective(img, matrixS, (statImgWidth, statImgHeight))
    #cv2.imshow('Warped Image Second', imgWarpColoredS)

    # Warp the third biggest rectangle
    monthImgWidth = 240                         # must be divisible by 4 (columns)
    monthImgHeight = 104                        # must be divisible by 4 (rows)
    ptT1 = np.float32(third_biggest_rectCon)
    ptT2 = np.float32([[0, 0], [monthImgWidth, 0], [0, monthImgHeight], [monthImgWidth, monthImgHeight]])
    matrixT = cv2.getPerspectiveTransform(ptT1, ptT2)
    imgWarpColoredT = cv2.warpPerspective(img, matrixT, (monthImgWidth, monthImgHeight))
    cv2.imshow('Warped Image Third', imgWarpColoredT)

    ##################### Processing the checkbox area #####################

    # Convert the warped image of the biggest rect contour to grayscale and apply thresholding
    imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
    imgThresh = cv2.threshold(imgWarpGray, 150, 255, cv2.THRESH_BINARY_INV)[1]
    cv2.imshow('Thresh Image', imgThresh)

    # Get the boxes from the biggest rect contour warped image 
    boxes = utils.splitBoxes(imgThresh, 31, 6)     # 31 rows and 6 columns
    cv2.imshow('Boxes Image', boxes[2])   # Display the third box
    #print("Total boxes:" , len(boxes))                   # 186 boxes (31x6)
    #print("Size of each box: ", boxes[0].shape)               # (18, 89)         i.e. 18 x 31 = 558 and 89 x 6 = 534

    # Get the non-zero pixel values of each box
    myPixelVal = np.zeros((31, 6))  # 31x6
    countR = 0
    countC = 0
    for image in boxes:
        totalPixels = cv2.countNonZero(image)
        myPixelVal[countR][countC] = totalPixels
        countC += 1
        if countC == 6:
            countR += 1
            countC = 0
    print(myPixelVal)               # The pixel values of each box (no. of non-zero pixels i.e. white pixels)
    #print("The size of the pixel values array: ", myPixelVal.shape)         # (31,6)

    # Create a new array with 1 where the pixel value is greater than threshold, and 0 otherwise (Check if marked or not)
    binary_array = np.where(myPixelVal > threshold, 1, 0)
    binary_array = binary_array
    print(binary_array)                 # shape: (31, 6)

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
    cv2.imshow('Inverse Warped Circle Image', imgInvWarp)

    # Add the inverse warped image to the original image (another way to overlay the images)
    #imgFinal = cv2.addWeighted(img, 1, imgInvWarp, 1.5, 10)
    #cv2.imshow('Final Image', imgFinal)

    # # Overlay using mask (Replace only the non-zero pixels of imgInvWarp with the original image pixels)
    imgFinal = img.copy()
    mask = np.any(imgInvWarp != 0, axis=-1)
    imgFinal[mask] = imgInvWarp[mask]
    #cv2.imshow('Final Image', imgFinal)

    ##################### Processing the month area #####################

    # Convert the warped image of the third biggest rect contour to grayscale and apply thresholding
    imgWarpGrayT = cv2.cvtColor(imgWarpColoredT, cv2.COLOR_BGR2GRAY)
    imgThreshT = cv2.threshold(imgWarpGrayT, 170, 255, cv2.THRESH_BINARY_INV)[1]

    # Get the boxes from the third biggest rect contour warped image
    month_boxes = utils.splitBoxes(imgThreshT, 4, 4)           # 4 rows and 4 columns
    cv2.imshow('Month Boxes Image', month_boxes[4])          # Display 5th box - Jan box
    # print(len(month_boxes))                                  # 12 boxes (4x4)
    print(month_boxes[0].shape)                              # (26, 60)         i.e. 26 x 4 = 104 and 60 x 4 = 240

    # Get the non-zero pixel values of each box
    monthPixelVal = np.zeros((4, 4))  # 4x4
    countR = 0
    countC = 0
    for image in month_boxes:
        totalPixels = cv2.countNonZero(image)
        monthPixelVal[countR][countC] = totalPixels
        countC += 1
        if countC == 4:
            countR += 1
            countC = 0
    print(monthPixelVal) 

    # Remove the first row 
    monthPixelVal = monthPixelVal[1:]

    #Determine the month with the highest value
    month, month_name = utils.detect_month(monthPixelVal)
    print("The month with the highest value is:", month, "i.e.", month_name)

    # Display the month on a black image
    imgRawMonth = np.zeros_like(imgWarpColoredT)
    imgRawMonth = utils.draw_month_on_image_with_top_row(imgRawMonth, month)
    #cv2.imshow('Month Image', imgRawMonth)

    # Inverse warp the month image
    invMatrixT = cv2.getPerspectiveTransform(ptT2, ptT1)
    imgInvWarpMonth = cv2.warpPerspective(imgRawMonth, invMatrixT, (img.shape[1], img.shape[0]))
    #cv2.imshow('Inverse Warped Month Image', imgInvWarpMonth)

    # Overlay the month image on the original image
    maskMonth = np.any(imgInvWarpMonth != 0, axis=-1)
    imgFinal[maskMonth] = imgInvWarpMonth[maskMonth]

    ##################### Processing the stats area #####################

    # Display the stats on a black image
    imgRawStats = np.zeros_like(imgWarpColoredS)
    total_days = utils.count_total_days(binary_array)
    no_of_days = calendar.monthrange(year, month)[1]
    print("Total days in the month:", no_of_days)
    imgRawStats = utils.apply_stats_to_image(imgRawStats, total_days, f"/{no_of_days}", 0.15) # 0.15 is the vertical adjustment factor
    longest_streak = utils.get_longest_streak(binary_array)
    print("Longest streak of consecutive days:", longest_streak)
    imgStats = utils.apply_stats_to_image(imgRawStats, longest_streak, "day streak", -0.2) # -0.2 is the vertical adjustment factor
    cv2.imshow('Stats Image', imgStats)

    # Inverse warp the stats image
    invMatrixS = cv2.getPerspectiveTransform(ptS2, ptS1)
    imgInvWarpStats = cv2.warpPerspective(imgRawStats, invMatrixS, (img.shape[1], img.shape[0]))
    cv2.imshow('Inverse Warped Stats Image', imgInvWarpStats)

    # Overlay the stats image on the original image
    maskStats = np.any(imgInvWarpStats != 0, axis=-1)
    imgFinal[maskStats] = imgInvWarpStats[maskStats]

    # Create a collage of the original image and the final image
    collage = utils.create_collage(img, imgFinal, scale=0.8)
    

cv2.imshow('Original Image', img)
# cv2.imshow('Gray Image', imgGray)
# cv2.imshow('Blur Image', imgBlur)
# cv2.imshow('Canny Image', imgCanny)
cv2.imshow('Contours Image', imgContours)
cv2.imshow('Final Image', imgFinal)
cv2.imshow('Collage', collage)
cv2.waitKey(0)