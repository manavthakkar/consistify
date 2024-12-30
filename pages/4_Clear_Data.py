import calendar

import streamlit as st

import firebase_utils as fb_utils
import utils

st.set_page_config(page_title="Clear Data", page_icon="🗑️")

db = fb_utils.initialize_firestore()

def clear_data_main()->None:

    utils.add_side_logo()

    if "user_info" not in st.session_state:
        st.warning("Please log in from the Home page to access this feature.")
        st.stop()

    st.title("Clear Data")
    st.write(f"**Logged in as :** {st.session_state['user_info'].get('email')}")

    user_email = st.session_state["user_info"].get("email")

    user_data = fb_utils.get_all_user_data(db, user_email)

    if user_data:
        st.write("You can delete all your data or data for a specific year or month.")

        clear_data_options = ["All Data", "Data for a Specific Year", "Data for a Specific Month"]
        clear_data_choice = st.radio("Select an option:", clear_data_options)

        if clear_data_choice == "All Data":
            st.warning("You are about to delete all your data. This action cannot be undone.")
            if st.button("Delete All Data"):
                try:
                    fb_utils.delete_all_user_data(db, user_email)
                    st.success("All data has been successfully deleted.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

        elif clear_data_choice == "Data for a Specific Year":
            # Dropdown to select year
            available_years = sorted(user_data.keys())
            selected_year = st.selectbox("Select Year to Delete", available_years)

            if st.button(f"Delete Data for {selected_year}"):
                try:
                    fb_utils.delete_data_for_year(db, user_email, selected_year)
                    st.success(f"Data for {selected_year} has been successfully deleted.")
                except Exception as e:
                    st.error(f"An error occurred: {e}")

        elif clear_data_choice == "Data for a Specific Month":
            # Dropdowns to select year and month
            available_years = sorted(user_data.keys())
            selected_year = st.selectbox("Select Year", available_years)

            if selected_year:
                available_months = sorted(user_data[selected_year].keys(), key=lambda x: list(calendar.month_name).index(x))
                selected_month = st.selectbox("Select Month to Delete", available_months)

                if st.button(f"Delete Data for {selected_month} {selected_year}"):
                    try:
                        fb_utils.delete_data_for_year_month(db, user_email, selected_year, selected_month)
                        st.success(f"Data for {selected_month} {selected_year} has been successfully deleted.")
                    except Exception as e:
                        st.error(f"An error occurred: {e}")
    else:
        st.error("No data found.")

if __name__ == "__main__":
    clear_data_main()
