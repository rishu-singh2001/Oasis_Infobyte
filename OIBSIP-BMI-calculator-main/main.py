
import tkinter as tk
from tkinter import ttk, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3

# Function to calculate BMI
def calculate_bmi(weight, height):
    try:
        height_m = height / 100  # Convert height from cm to meters
        bmi = weight / (height_m ** 2)
        return bmi
    except ZeroDivisionError:
        return None

# Function to create the SQLite database and table if they don't exist
def create_database():
    try:
        conn = sqlite3.connect('my_database.db')  # Replace with your desired path
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS bmi_records
                     (name TEXT, weight REAL, height REAL, bmi REAL)''')
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error creating database: {e}")





# Function to save BMI data to SQLite database
def save_bmi_data(name, weight, height, bmi):
    try:
        conn = sqlite3.connect('my_database.db')  # Replace with your desired path
        c = conn.cursor()
        c.execute('''INSERT INTO bmi_records (name, weight, height, bmi)
                     VALUES (?, ?, ?, ?)''', (name, weight, height, bmi))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error saving BMI data: {e}")

# Function to retrieve BMI data from SQLite database
def retrieve_bmi_data(name):
    try:
        conn = sqlite3.connect('my_database.db')  # Replace with yourC:\Users\HP\PycharmProjects\bmi cal\bmi_data.db desired path
        c = conn.cursor()
        c.execute('''SELECT weight, height, bmi FROM bmi_records WHERE name=?''', (name,))
        data = c.fetchall()
        conn.close()
        return data
    except Exception as e:
        print(f"Error retrieving BMI data: {e}")
        return []

# Function to retrieve all user names from SQLite database
def retrieve_all_users():
    try:
        conn = sqlite3.connect('my_database.db')  # Replace with your desired path
        c = conn.cursor()
        c.execute('''SELECT DISTINCT name FROM bmi_records''')
        users = [row[0] for row in c.fetchall()]
        conn.close()
        return users
    except Exception as e:
        print(f"Error retrieving user names: {e}")
        return []

# Function to plot BMI trend graph
def plot_bmi_trend(name):
    try:
        data = retrieve_bmi_data(name)
        if data:
            weights = [row[0] for row in data]
            heights = [row[1] for row in data]
            bmis = [row[2] for row in data]

            fig, ax = plt.subplots(figsize=(8, 6))
            ax.plot(bmis, marker='o', linestyle='-', color='b', label='BMI')
            ax.set_xlabel('Measurements')
            ax.set_ylabel('BMI')
            ax.set_title(f'BMI Trend for {name}')
            ax.legend()

            canvas = FigureCanvasTkAgg(fig, master=plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack()
        else:
            messagebox.showwarning('Warning', 'No data available for this user.')
    except Exception as e:
        print(f"Error plotting BMI trend: {e}")

# Function to handle BMI calculation and data storage
def calculate_and_store_bmi():
    try:
        name = name_entry.get()
        weight = float(weight_entry.get())
        height = float(height_entry.get())

        bmi = calculate_bmi(weight, height)
        if bmi is not None:
            result_label.config(text=f'BMI: {bmi:.2f}')

            save_bmi_data(name, weight, height, bmi)
            users_combo['values'] = retrieve_all_users()

            plot_bmi_trend(name)
        else:
            messagebox.showerror('Error', 'Height cannot be zero. Please check your input.')
    except Exception as e:
        print(f"Error calculating and storing BMI: {e}")

# GUI setup
root = tk.Tk()
root.title('BMI Calculator and Tracker')

input_frame = tk.Frame(root, padx=10, pady=10)
input_frame.pack()

name_label = tk.Label(input_frame, text='Name:')
name_label.grid(row=0, column=0, sticky=tk.W)

name_entry = tk.Entry(input_frame, width=30)
name_entry.grid(row=0, column=1)

weight_label = tk.Label(input_frame, text='Weight (kg):')
weight_label.grid(row=1, column=0, sticky=tk.W)

weight_entry = tk.Entry(input_frame, width=10)
weight_entry.grid(row=1, column=1)

height_label = tk.Label(input_frame, text='Height (cm):')
height_label.grid(row=2, column=0, sticky=tk.W)

height_entry = tk.Entry(input_frame, width=10)
height_entry.grid(row=2, column=1)

calculate_button = tk.Button(input_frame, text='Calculate BMI', command=calculate_and_store_bmi)
calculate_button.grid(row=3, columnspan=2, pady=10)

result_label = tk.Label(input_frame, text='', font=('Helvetica', 14, 'bold'))
result_label.grid(row=4, columnspan=2, pady=10)

# Historical Data Frame
history_frame = tk.LabelFrame(root, text='Historical Data', padx=10, pady=10)
history_frame.pack(padx=10, pady=10, fill='both', expand=True)

users_label = tk.Label(history_frame, text='Select User:')
users_label.grid(row=0, column=0, sticky=tk.W)

users_combo = ttk.Combobox(history_frame, width=27)
users_combo['values'] = retrieve_all_users()
users_combo.grid(row=0, column=1, padx=10)

def show_history():
    try:
        selected_user = users_combo.get()
        if selected_user:
            data = retrieve_bmi_data(selected_user)
            if data:
                history_text = "\n".join(f"Weight: {row[0]} kg, Height: {row[1]} cm, BMI: {row[2]:.2f}" for row in data)
                history_text += "\n\nBMI Trend Analysis:"
                history_label.config(text=history_text)
                plot_bmi_trend(selected_user)
            else:
                history_label.config(text='No data available for this user.')
        else:
            history_label.config(text='Please select a user.')
    except Exception as e:
        print(f"Error showing history: {e}")

show_history_button = tk.Button(history_frame, text='Show History', command=show_history)
show_history_button.grid(row=0, column=2, padx=10)

history_label = tk.Label(history_frame, text='', justify=tk.LEFT)
history_label.grid(row=1, column=0, columnspan=3, pady=10)

# Plot Frame for BMI Trend Graph
plot_frame = tk.Frame(root)
plot_frame.pack(padx=10, pady=10, fill='both', expand=True)

# Create database and table if they don't exist
create_database()

def connect_to_database(db_file="my_database.db"):
    """Connects to the specified SQLite database file.

    Args:
        db_file (str, optional): The path to the database file. Defaults to "my_database.db".

    Returns:
        sqlite3.Connection: A connection object to the database, or None on error.
    """
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        print(f"Error connecting to database: {e}")
        return None




# Example usage:
db_file = "my_database.db"
conn = connect_to_database("my_database.db")

if conn:
    # Perform database operations
    conn.close()

root.mainloop()
