import cv2
import numpy as np
import utils
import calendar

##################### Constants #####################
YEAR = 2024
IMG_PATH = 'assets/testimg2.jpeg'
THRESHOLD_ADJUSTMENT = 0          # ± value to adjust the threshold

# Configurable grid dimensions
CHECKBOX_ROWS = 31
CHECKBOX_COLS = 6
MONTH_ROWS = 4
MONTH_COLS = 4

# Biggest rectangle dimensions
GRID_RECT_WIDTH = 534
GRID_RECT_HEIGHT = 558

BOX_WIDTH = GRID_RECT_WIDTH // CHECKBOX_COLS
BOX_HEIGHT = GRID_RECT_HEIGHT // CHECKBOX_ROWS

# Stats rectangle dimensions
STAT_RECT_WIDTH = 564
STAT_RECT_HEIGHT = 92

##################### Helper Functions #####################
def resize_image(img, scale_percent):
    """Resize image by a scale percentage."""
    width = int(img.shape[1] * scale_percent / 100)
    height = int(img.shape[0] * scale_percent / 100)
    return cv2.resize(img, (width, height), interpolation=cv2.INTER_AREA)

def warp_image(img, src_points, width, height):
    """Warp the image to a rectangle defined by the src_points."""
    dst_points = np.float32([[0, 0], [width, 0], [0, height], [width, height]])
    matrix = cv2.getPerspectiveTransform(src_points, dst_points)
    return cv2.warpPerspective(img, matrix, (width, height)), matrix

def threshold_image(img_gray):
    """Apply Otsu's thresholding to a grayscale image."""
    _, img_thresh = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    return img_thresh

##################### Main Code #####################
# Load and preprocess the image
img = resize_image(cv2.imread(IMG_PATH), scale_percent=100)
imgContours = img.copy()
imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
imgBlur = cv2.GaussianBlur(imgGray, (5, 5), 1)
imgCanny = cv2.Canny(imgBlur, 10, 50)

# Find and process contours
contours, _ = cv2.findContours(imgCanny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
cv2.drawContours(imgContours, contours, -1, (0, 255, 0), 3)

# Detect rectangle contours
rectCon = utils.rectContour(contours)
biggest_rectCon = utils.getCornerPoints(rectCon[0])
second_biggest_rectCon = utils.getCornerPoints(rectCon[1])
third_biggest_rectCon = utils.getCornerPoints(rectCon[2])

# Validate detected rectangles
if any(rect is None or rect.size != 8 for rect in [biggest_rectCon, second_biggest_rectCon, third_biggest_rectCon]):
    print("Error: One or more required rectangles could not be detected.")
    exit()

# Ensure proper formatting of rectangle points
biggest_rectCon = np.array(utils.reorder(biggest_rectCon), dtype=np.float32)
second_biggest_rectCon = np.array(utils.reorder(second_biggest_rectCon), dtype=np.float32)
third_biggest_rectCon = np.array(utils.reorder(third_biggest_rectCon), dtype=np.float32)

# Warp main regions
markerImgWidth, markerImgHeight = (CHECKBOX_COLS * BOX_WIDTH), (CHECKBOX_ROWS * BOX_HEIGHT)
imgWarpColored, matrix = warp_image(img, biggest_rectCon, markerImgWidth, markerImgHeight)

imgWarpColoredS, matrixS = warp_image(img, second_biggest_rectCon, STAT_RECT_WIDTH, STAT_RECT_HEIGHT)

monthImgWidth, monthImgHeight = MONTH_COLS * 60, MONTH_ROWS * 26
imgWarpColoredT, matrixT = warp_image(img, third_biggest_rectCon, monthImgWidth, monthImgHeight)

##################### Checkbox Area Processing #####################
# Process checkbox grid
imgThresh = threshold_image(cv2.cvtColor(imgWarpColored, cv2.COLOR_BGR2GRAY))
boxes = utils.splitBoxes(imgThresh, CHECKBOX_ROWS, CHECKBOX_COLS)
myPixelVal = np.array([cv2.countNonZero(box) for box in boxes]).reshape(CHECKBOX_ROWS, CHECKBOX_COLS)
threshold = np.max(myPixelVal) * 0.7 + THRESHOLD_ADJUSTMENT # 70% of the max pixel value
binary_array = (myPixelVal > threshold).astype(int)

# Mark detected checkboxes
imgMarked = utils.draw_circles_on_image(imgWarpColored.copy(), binary_array)
imgRawCircles = np.zeros_like(imgWarpColored)
imgRawCircles = utils.draw_circles_on_image(imgRawCircles, binary_array)

# Overlay detected checkboxes on the original image
imgInvWarp = cv2.warpPerspective(imgRawCircles, np.linalg.inv(matrix), (img.shape[1], img.shape[0]))
imgFinal = img.copy()
imgFinal[np.any(imgInvWarp != 0, axis=-1)] = imgInvWarp[np.any(imgInvWarp != 0, axis=-1)]

##################### Month Area Processing #####################
# Process month selector
imgThreshT = threshold_image(cv2.cvtColor(imgWarpColoredT, cv2.COLOR_BGR2GRAY))
month_boxes = utils.splitBoxes(imgThreshT, MONTH_ROWS, MONTH_COLS)
monthPixelVal = np.array([cv2.countNonZero(box) for box in month_boxes]).reshape(MONTH_ROWS, MONTH_COLS)[1:]
month, month_name = utils.detect_month(monthPixelVal)

# Highlight detected month
imgRawMonth = utils.draw_month_on_image_with_top_row(np.zeros_like(imgWarpColoredT), month)
imgInvWarpMonth = cv2.warpPerspective(imgRawMonth, np.linalg.inv(matrixT), (img.shape[1], img.shape[0]))
imgFinal[np.any(imgInvWarpMonth != 0, axis=-1)] = imgInvWarpMonth[np.any(imgInvWarpMonth != 0, axis=-1)]

##################### Stats Area Processing #####################
# Calculate stats
total_days = utils.count_total_days(binary_array)
no_of_days = calendar.monthrange(YEAR, month)[1]
longest_streak = utils.get_longest_streak(binary_array)

# Display stats
imgRawStats = np.zeros_like(imgWarpColoredS)
imgRawStats = utils.apply_stats_to_image(imgRawStats, total_days, f"/{no_of_days}", 0.15)
imgRawStats = utils.apply_stats_to_image(imgRawStats, longest_streak, "day streak", -0.2)
imgInvWarpStats = cv2.warpPerspective(imgRawStats, np.linalg.inv(matrixS), (img.shape[1], img.shape[0]))
imgFinal[np.any(imgInvWarpStats != 0, axis=-1)] = imgInvWarpStats[np.any(imgInvWarpStats != 0, axis=-1)]

##################### Final Visualization #####################
collage = utils.create_collage(img, imgFinal, scale=0.3)
cv2.imshow('Collage', collage)
cv2.waitKey(0)
