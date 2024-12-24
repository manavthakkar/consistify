import streamlit as st
import cv2
import numpy as np
import calendar
import utils  
import firebase_admin
from firebase_admin import credentials, firestore
from streamlit_google_auth import Authenticate

# Firebase Initialization
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase.json")
    firebase_admin.initialize_app(cred)

# Initialize Firestore
db = firestore.client()

def get_user_data(user_id, year, month_name):
    """
    Retrieve user data for a specific year and month from Firestore.
    """
    doc = db.collection("users").document(user_id).get()
    if doc.exists:
        user_data = doc.to_dict()
        if str(year) in user_data and month_name in user_data[str(year)]:
            return user_data[str(year)][month_name]
    return None

def store_user_data(user_id, user_data):
    """
    Store user data in Firestore.
    """
    db.collection("users").document(user_id).set(user_data, merge=True)

def process_image_and_generate_collage(img, year, percentage_threshold=50):
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


def get_days_in_month(year, month_name):
    """
    Get the number of days in a month, considering leap years.
    """
    month_number = list(calendar.month_name).index(month_name)  # Get the month number
    _, num_days = calendar.monthrange(year, month_number)
    return num_days

# Streamlit App
def store_data_main():
    st.title("Habit Tracker with Google Authentication")

    # Google Authentication
    authenticator = Authenticate(
        secret_credentials_path='google_credentials.json',
        cookie_name='auth_cookie',
        cookie_key='this_is_secret',
        redirect_uri='http://localhost:8501',
    )

    # Check authentication
    authenticator.check_authentification()

    # Show login button
    authenticator.login()

    if not st.session_state.get('connected', False):
        # Show information only if the user is not logged in
        st.write("### Welcome to the Habit Tracker App!")
        st.write("""
        This app allows you to process habit tracker images, extract data, and save it securely in the cloud.
        With this tool, you can:
        - Upload an image of your habit tracker.
        - Detect and analyze habits for a specific month.
        - Save your data to the cloud for future access.

        **Note**: You must log in with your Google account to save your data. Click the Google login button below to proceed.
        """)
        st.warning("Please log in with Google to access the app features.")
        st.stop()
    

    # Display user details after login
    st.image(st.session_state['user_info'].get('picture'), width=80)
    st.write(f"**Hello, {st.session_state['user_info'].get('name')}!**")
    st.write(f"Your email is **{st.session_state['user_info'].get('email')}**.")
    user_id = st.session_state['oauth_id']

    if st.button('Log out'):
        authenticator.logout()
        st.stop()

    # Input for year
    st.header("Image Processing")
    year = st.number_input("Enter the Year", min_value=1900, max_value=2100, value=2024, step=1)

    # File uploader for the image
    uploaded_file = st.file_uploader("Upload the habit tracker image", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        st.write("Processing your image...")
        
        # Slider for percentage threshold
        percentage_threshold = st.slider(
            "Set the percentage threshold for checkbox detection:",
            min_value=0,
            max_value=100,
            value=50,  # Default value
            step=1
        )
        
        # Convert the uploaded file to OpenCV format
        file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
        img = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        try:
            # Process the image with the user-defined threshold
            processed_image, month_name, binary_array = process_image_and_generate_collage(img, year, percentage_threshold)

            # Convert BGR to RGB for Streamlit display
            collage_image_rgb = cv2.cvtColor(processed_image, cv2.COLOR_BGR2RGB)

            # Get the number of days in the detected month
            num_days = get_days_in_month(year, month_name)

            # Trim the binary array to match the number of days in the month
            binary_array_trimmed = binary_array[:num_days, :]

            # Display the processed results
            st.subheader("Processed Results")
            st.image(collage_image_rgb, caption="Processed Image", use_column_width=True)
            st.write(f"**Detected Month:** {month_name}")
            st.write(f"**Number of Days in {month_name}:** {num_days}")
            st.write("**Binary Array of Checkbox Values (Trimmed):**")
            st.write(binary_array_trimmed)

            # Prompt user to enter habit names
            st.subheader("Enter Habit Names")
            habit_names = []
            for i in range(binary_array_trimmed.shape[1]):  # Assuming each column corresponds to a habit
                habit_name = st.text_input(f"Enter name for Habit {i + 1}", value=f"Habit {i + 1}")
                habit_names.append(habit_name)

            # Prepare the habit data
            habit_data = {habit_names[i]: binary_array_trimmed[:, i].tolist() for i in range(binary_array_trimmed.shape[1])}

            # Prepare the data to store in Firebase
            extracted_data = {
                str(year): {
                    month_name: habit_data
                }
            }

            # Check if data exists for the specific year and month
            st.subheader("Firebase Integration")
            existing_data = get_user_data(user_id, year, month_name)
            if existing_data:
                st.write("Data already exists for this user, year, and month.")
                overwrite = st.radio("Do you want to overwrite the existing data?", ("No", "Yes"))
                if overwrite == "Yes":
                    if st.button("Save Data"):
                        store_user_data(user_id, extracted_data)
                        st.success("Data overwritten successfully in Firebase!")
                else:
                    st.info("Data was not overwritten.")
            else:
                # Add Save Data Button
                if st.button("Save Data"):
                    store_user_data(user_id, extracted_data)
                    st.success("Data saved successfully in Firebase!")

        except Exception as e:
            st.error(f"An error occurred during processing: {e}")


if __name__ == "__main__":
    store_data_main()
