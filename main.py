import cv2
import numpy as np
import utils
import calendar

##################### Constants #####################
imgWidth = 744                      # should be divisible by 31 (days)
imgHeight = 744                     # should be divisible by 6 (habits)
habits = 6
threshold = 500                    # Threshold for checking if a box is marked or not
year = 2024

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
    markerImgWidth = 1054                # must be divisible by 31 (columns)  # values obtained from the template image
    markerImgHeight = 276                # must be divisible by 6 (rows)
    pt1 = np.float32(biggest_rectCon)
    pt2 = np.float32([[0, 0], [markerImgWidth, 0], [0, markerImgHeight], [markerImgWidth, markerImgHeight]])
    matrix = cv2.getPerspectiveTransform(pt1, pt2)
    imgWarpColored = cv2.warpPerspective(img, matrix, (markerImgWidth, markerImgHeight))
    #cv2.imshow('Warped Image', imgWarpColored)

    # Warp the second biggest rectangle
    statImgWidth = 1200                 # must be divisible by 6 (columns)
    statImgHeight = 154
    ptS1 = np.float32(second_biggest_rectCon)
    ptS2 = np.float32([[0, 0], [statImgWidth, 0], [0, statImgHeight], [statImgWidth, statImgHeight]])
    matrixS = cv2.getPerspectiveTransform(ptS1, ptS2)
    imgWarpColoredS = cv2.warpPerspective(img, matrixS, (statImgWidth, statImgHeight))
    #cv2.imshow('Warped Image Second', imgWarpColoredS)

    # Warp the third biggest rectangle
    monthImgWidth = 356                         # must be divisible by 4 (columns)
    monthImgHeight = 150                        # must be divisible by 3 (rows)
    ptT1 = np.float32(third_biggest_rectCon)
    ptT2 = np.float32([[0, 0], [monthImgWidth, 0], [0, monthImgHeight], [monthImgWidth, monthImgHeight]])
    matrixT = cv2.getPerspectiveTransform(ptT1, ptT2)
    imgWarpColoredT = cv2.warpPerspective(img, matrixT, (monthImgWidth, monthImgHeight))
    #cv2.imshow('Warped Image Third', imgWarpColoredT)

    ##################### Processing the checkbox area #####################

    # Convert the warped image of the biggest rect contour to grayscale and apply thresholding
    imgWarpGray = cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY)
    imgThresh = cv2.threshold(imgWarpGray, 170, 255, cv2.THRESH_BINARY_INV)[1]
    #cv2.imshow('Thresh Image', imgThresh)

    # Get the boxes from the biggest rect contour warped image 
    boxes = utils.splitBoxes(imgThresh, habits, 31)     # 6 rows and 31 columns
    #cv2.imshow('Boxes Image', boxes[2])   # Display the third box
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
    # print(myPixelVal)               # The pixel values of each box
    # print("The size of the pixel values array: ", myPixelVal.shape)         # (6,31)

    # Create a new array with 1 where the pixel value is greater than threshold, and 0 otherwise (Check if marked or not)
    binary_array = np.where(myPixelVal > threshold, 1, 0)
    print(binary_array)

    # Display the marked boxes
    # imgMarked = imgWarpColored.copy()
    # imgMarked = utils.draw_circles_on_image(imgMarked, binary_array)
    # cv2.imshow('Marked Image', imgMarked)

    # Create a black image of same shape of imgWarpColored to display circles
    imgRawCircles = np.zeros_like(imgWarpColored)
    imgRawCircles = utils.draw_circles_on_image(imgRawCircles, binary_array)
    #cv2.imshow('Raw Circles Image', imgRawCircles)

    # Inverse warp the raw circles image (This will be a black image with circles)
    invMatrix = cv2.getPerspectiveTransform(pt2, pt1)
    imgInvWarp = cv2.warpPerspective(imgRawCircles, invMatrix, (img.shape[1], img.shape[0])) # img.shape[1] = width, img.shape[0] = height
    #cv2.imshow('Inverse Warped Circle Image', imgInvWarp)

    # Add the inverse warped image to the original image
    # imgFinal = cv2.addWeighted(img, 1, imgInvWarp, 1.5, 10)
    # cv2.imshow('Final Image', imgFinal)

    # # Overlay using mask (Replace only the non-zero pixels of imgInvWarp with the original image pixels)
    imgFinal = img.copy()
    mask = np.any(imgInvWarp != 0, axis=-1)
    imgFinal[mask] = imgInvWarp[mask]

    ##################### Processing the month area #####################

    # Convert the warped image of the third biggest rect contour to grayscale and apply thresholding
    imgWarpGrayT = cv2.cvtColor(imgWarpColoredT, cv2.COLOR_BGR2GRAY)
    imgThreshT = cv2.threshold(imgWarpGrayT, 170, 255, cv2.THRESH_BINARY_INV)[1]

    # Get the boxes from the third biggest rect contour warped image
    month_boxes = utils.splitBoxes(imgThreshT, 3, 4)           # 3 rows and 4 columns
    # cv2.imshow('Month Boxes Image', month_boxes[0])          # Display the first month box
    # print(len(month_boxes))                                  # 12 boxes (3x4)
    # print(month_boxes[0].shape)                              # (50, 89)         i.e. 50 x 3 = 150 and 89 x 4 = 356

    # Get the non-zero pixel values of each box
    monthPixelVal = np.zeros((3, 4))  # 3x4
    countR = 0
    countC = 0
    for image in month_boxes:
        totalPixels = cv2.countNonZero(image)
        monthPixelVal[countR][countC] = totalPixels
        countC += 1
        if countC == 4:
            countR += 1
            countC = 0
    #print(monthPixelVal)

    # Determine the month with the highest value
    month, month_name = utils.detect_month(monthPixelVal)
    print("The month with the highest value is:", month, "i.e.", month_name)

    # Display the month on a black image
    imgRawMonth = np.zeros_like(imgWarpColoredT)
    imgRawMonth = utils.draw_month_on_image(imgRawMonth, month)
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
    imgRawStats = utils.apply_stats_to_image(imgRawStats, total_days, f"/{no_of_days}", 0.15) # 0.15 is the vertical adjustment factor
    longest_streak = utils.get_longest_streak(binary_array)
    imgStats = utils.apply_stats_to_image(imgRawStats, longest_streak, "day streak", -0.2) # -0.2 is the vertical adjustment factor
    #cv2.imshow('Stats Image', imgStats)

    # Inverse warp the stats image
    invMatrixS = cv2.getPerspectiveTransform(ptS2, ptS1)
    imgInvWarpStats = cv2.warpPerspective(imgRawStats, invMatrixS, (img.shape[1], img.shape[0]))
    #cv2.imshow('Inverse Warped Stats Image', imgInvWarpStats)

    # Overlay the stats image on the original image
    maskStats = np.any(imgInvWarpStats != 0, axis=-1)
    imgFinal[maskStats] = imgInvWarpStats[maskStats]

    ##################### Save the data to a csv file #####################
    total_days = total_days.tolist()
    longest_streak = longest_streak.tolist()
    streak_start = utils.calculate_streaks(binary_array, "start")
    streak_end = utils.calculate_streaks(binary_array, "end")
 
    # Save the data to a csv file (data.csv)
    result = utils.save_data(month, year, total_days, longest_streak, streak_start, streak_end, override=False)
    if result:
        print("Data saved successfully!")
    else:
        print("Data not saved. Data already exists.")
    
    cv2.imshow('Final Image', imgFinal)
    

cv2.imshow('Original Image', img)
# cv2.imshow('Gray Image', imgGray)
# cv2.imshow('Blur Image', imgBlur)
# cv2.imshow('Canny Image', imgCanny)
# cv2.imshow('Contours Image', imgContours)
cv2.waitKey(0)