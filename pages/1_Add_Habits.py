import streamlit as st
import cv2
import numpy as np
import calendar
import utils
import firebase_utils as fb_utils
import auth_functions

st.set_page_config(page_title="Add Habits", page_icon="📂")

# Initialize Firebase
db = fb_utils.initialize_firestore()

def process_image_and_extract_data(img, year, percentage_threshold=50):
    ##################### Constants #####################
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
    img = resize_image(img, scale_percent=100)
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
    threshold = np.max(myPixelVal) * (percentage_threshold / 100) + THRESHOLD_ADJUSTMENT # 65% of the max pixel value
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
    no_of_days = calendar.monthrange(year, month)[1]
    longest_streak = utils.get_longest_streak(binary_array)

    # Display stats
    imgRawStats = np.zeros_like(imgWarpColoredS)
    imgRawStats = utils.apply_stats_to_image(imgRawStats, total_days, f"/{no_of_days}", 0.15)
    imgRawStats = utils.apply_stats_to_image(imgRawStats, longest_streak, "day streak", -0.2)
    imgInvWarpStats = cv2.warpPerspective(imgRawStats, np.linalg.inv(matrixS), (img.shape[1], img.shape[0]))
    imgFinal[np.any(imgInvWarpStats != 0, axis=-1)] = imgInvWarpStats[np.any(imgInvWarpStats != 0, axis=-1)]

    ##################### Final Visualization #####################
    #collage = utils.create_collage(img, imgFinal, scale=0.3)
    
    return imgFinal, month_name, binary_array

def add_habits_main():

    utils.add_side_logo()
    
    # Check if the user is authenticated
    if 'user_info' not in st.session_state:
        st.warning("Please log in from the Home page to access this feature.")
        st.stop()

    if st.sidebar.button("Log out"):
        auth_functions.sign_out()
        st.rerun()

    st.title("Upload Your Habit Tracker Image")
    st.write(f"**Logged in as :** {st.session_state['user_info'].get('email')}")

    user_email = st.session_state['user_info']['email']

    year = st.number_input("Enter the year : ", min_value=2020, max_value=2100, value=2024, step=1)

    uploaded_file = st.file_uploader("Upload your habit tracker image :", type=["jpg", "jpeg", "png"])

    if uploaded_file:

        percentage_threshold = st.slider(
            "Change the slider value in case of incorrect detection:",
            min_value=0,
            max_value=100,
            value=50,
            step=1,
            help="Increasing the value will reduce the number of detected checkboxes and vice versa."
        )


        # Convert uploaded file to OpenCV format
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        try:
            processed_image, month_name, binary_array = process_image_and_extract_data(img, year, percentage_threshold)

            # Convert BGR to RGB for Streamlit display
            collage_image_rgb = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)

            # Get the number of days in the detected month
            num_days = utils.get_days_in_month(year, month_name)

            # Trim the binary array to match the number of days in the month
            binary_array_trimmed = binary_array[:num_days, :]

            # Display the processed results
            st.image(collage_image_rgb, caption="Processed Image", use_container_width=True)
            st.write(f"**Detected Month:** {month_name}")

            # Enter habit names
            st.subheader(f"Enter Habit Names for {month_name}, {year}")
            habit_names = []
            for i in range(binary_array_trimmed.shape[1]):  # Assuming each column corresponds to a habit
                habit_name = st.text_input(f"Enter name for Habit {i + 1}", value=f"Habit {i + 1}")
                habit_names.append(habit_name.capitalize())

            st.info("Enter habit names consistently, as in previous months, to ensure accurate yearly insights.")

            habit_data = {habit_names[i]: binary_array_trimmed[:, i].tolist() for i in range(binary_array_trimmed.shape[1])}

            # Prepare data to store in Firebase
            extracted_data = {
                str(year): {
                    month_name: habit_data
                }
            }

            # Firebase integration
            st.subheader("Save data to get insights")
            existing_data = fb_utils.get_user_data(db, user_email, year, month_name)
            if existing_data:
                st.write("Data already exists for this user, year, and month.")
                overwrite = st.radio("Do you want to overwrite the existing data?", ("No", "Yes"))
                if overwrite == "Yes" and st.button("Save Data"):
                    fb_utils.delete_data_for_year_month(db, user_email, year, month_name)
                    fb_utils.store_user_data(db, user_email, extracted_data)
                    st.success("Data overwritten successfully!")
            else:
                if st.button("Save Data"):
                    fb_utils.store_user_data(db, user_email, extracted_data)
                    st.success("Data saved successfully!")

        except Exception as e:
            st.error(f"An error occurred during processing: {e}")

if __name__ == "__main__":
    add_habits_main()
