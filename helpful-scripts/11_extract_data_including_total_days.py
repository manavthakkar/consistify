def get_habit_data_with_cumulative_sum(data, year, month, habit):
    """
    Retrieves the binary array for a specific habit in a given year and month,
    along with the cumulative number of days the habit was performed from January
    to the specified month.

    Parameters:
    - data (dict): The dictionary containing habit data.
    - year (str): The year as a string (e.g., '2024').
    - month (str): The month as a string (e.g., 'Mar').
    - habit (str): The habit as a string (e.g., 'Workout').

    Returns:
    - tuple: (binary_array, cumulative_sum)
      - binary_array: The binary array corresponding to the habit for the specified month.
      - cumulative_sum: The cumulative sum of days the habit was performed from January to the specified month.
    - tuple of (None, None): If the year, month, or habit is not found.
    """
    try:
        # List of months in order to calculate cumulative sum
        months_in_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                           'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
        
        if year not in data:
            raise KeyError(f"Year '{year}' not found in the data.")
        
        if month not in months_in_order:
            raise ValueError(f"Invalid month '{month}'. Please use three-letter format (e.g., 'Jan').")
        
        if month not in data[year]:
            raise KeyError(f"Month '{month}' not found in the data for year '{year}'.")
        
        if habit not in data[year][month]:
            raise KeyError(f"Habit '{habit}' not found in the data for year '{year}', month '{month}'.")
        
        # Binary array for the specified month
        binary_array = data[year][month][habit]

        # Cumulative sum calculation
        cumulative_sum = 0
        for m in months_in_order:
            if m in data[year]:
                if habit in data[year][m]:
                    cumulative_sum += sum(data[year][m][habit])
            if m == month:
                break

        return binary_array, cumulative_sum
    
    except KeyError as e:
        print(f"KeyError: {e}")
        return None, None
    except ValueError as e:
        print(f"ValueError: {e}")
        return None, None

# Example usage
data = {
    '2024': {
        'Feb': {
            'Workout': [0, 0, 0, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            'Meditation': [1, 0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
        },
        'Jan': {
            'Workout': [1, 0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
            'Meditation': [0, 1, 1, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
        },
        'Mar': {
            'Workout': [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            'Meditation': [0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
        },
        'Apr': {
            'Workout': [1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0],
            'Meditation': [0, 1, 0, 0, 0, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1],
        }
    }
}

# Test
binary_array, cumulative_sum = get_habit_data_with_cumulative_sum(data, '2024', 'Mar', 'Workout')
print("Binary Array:", binary_array)
print("Cumulative Sum:", cumulative_sum)

# Output:
# Binary Array: [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0]
# Cumulative Sum: 76

