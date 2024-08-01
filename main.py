import tkinter as tk
from tkinter import simpledialog, messagebox
import sqlite3
from datetime import datetime

# Database setup
conn = sqlite3.connect('time_keeper.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS time_keeper (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        cn TEXT,
        time TEXT,
        date TEXT
    )
''')
conn.commit()


# Functions
def save_data():
    c.execute('DELETE FROM time_keeper WHERE date = ?', (current_date,))
    for entry in entries:
        name = entry['name'].get()
        cn = entry['cn'].cget('text')  # Assuming CN is entered through the popup
        time = entry['time'].get()
        c.execute('INSERT INTO time_keeper (name, cn, time, date) VALUES (?, ?, ?, ?)', (name, cn, time, current_date))
    conn.commit()


def toggle_edit_mode():
    global edit_mode
    edit_mode = not edit_mode
    edit_button.config(bg='green' if edit_mode else 'lightgray')
    for entry in entries:
        entry['name'].config(state='normal' if edit_mode else 'readonly')
    save_data()


def reset_fields():
    if custom_confirm_reset():
        for entry in entries:
            entry['name'].delete(0, tk.END)
            entry['time'].config(state='normal')
            entry['time'].delete(0, tk.END)
            entry['time'].insert(0, '00:00:00')
            entry['time'].config(state='readonly')
            entry['start_stop'].config(text="Start")
            entry['running'] = False
        # Reset to one row
        while len(entries) > 1:
            entry = entries.pop()
            entry['name'].grid_forget()
            entry['cn'].grid_forget()
            entry['time'].grid_forget()
            entry['start_stop'].grid_forget()
        save_data()


def custom_confirm_reset():
    result = tk.messagebox.askyesno("Confirm Reset", "Are you sure you want to reset all fields?", default=tk.NO)
    return result


def add_entry():
    new_row = {
        'name': tk.Entry(window),
        'cn': tk.Button(window, text="CN", command=open_cn_popup),
        'time': tk.Entry(window, state='readonly'),
        'start_stop': tk.Button(window, text="Start", command=lambda e=len(entries): toggle_timer(e)),
        'running': False
    }
    new_row['name'].grid(row=len(entries) + 2, column=0)
    new_row['cn'].grid(row=len(entries) + 2, column=1)
    new_row['time'].grid(row=len(entries) + 2, column=2)
    new_row['time'].insert(0, '00:00:00')
    new_row['start_stop'].grid(row=len(entries) + 2, column=3)
    entries.append(new_row)
    plus_button.grid(row=len(entries) + 2, column=4)
    save_data()


def open_cn_popup():
    cn_values = simpledialog.askstring("Input", "Enter CN values separated by commas:")
    if cn_values:
        cn_list = cn_values.split(',')
        messagebox.showinfo("CN Values", f"Entered CN values: {cn_list}")
    save_data()


def toggle_timer(index):
    for i, entry in enumerate(entries):
        if i != index and entry['running']:
            entry['start_stop'].config(text="Start")
            entry['running'] = False

    entry = entries[index]
    if entry['start_stop'].cget('text') == "Start":
        entry['start_stop'].config(text="Stop")
        entry['running'] = True
        increment_time(index)
    else:
        entry['start_stop'].config(text="Start")
        entry['running'] = False
    save_data()


def increment_time(index):
    if entries[index]['running']:
        current_time = entries[index]['time'].get()
        h, m, s = map(int, current_time.split(':'))
        s += 1
        if s == 60:
            s = 0
            m += 1
        if m == 60:
            m = 0
            h += 1
        new_time = f"{h:02}:{m:02}:{s:02}"
        entries[index]['time'].config(state='normal')
        entries[index]['time'].delete(0, tk.END)
        entries[index]['time'].insert(0, new_time)
        entries[index]['time'].config(state='readonly')
        window.after(1000, increment_time, index)


def update_title():
    current_time = datetime.now().strftime('%H:%M:%S')
    window.title(f"Time Keeper - {current_date} - {current_time}")


def on_close():
    save_data()
    conn.close()
    window.destroy()


def load_data():
    c.execute('SELECT name, cn, time FROM time_keeper WHERE date = ?', (current_date,))
    rows = c.fetchall()
    if rows:
        for row in rows:
            add_entry()
            entries[-1]['name'].insert(0, row[0])
            entries[-1]['cn'].config(text=row[1])
            entries[-1]['time'].config(state='normal')
            entries[-1]['time'].delete(0, tk.END)
            entries[-1]['time'].insert(0, row[2])
            entries[-1]['time'].config(state='readonly')
    else:
        add_entry()


# GUI setup
window = tk.Tk()
window.geometry("600x400")

window.protocol("WM_DELETE_WINDOW", on_close)

edit_mode = False

# Date and Time
current_date = datetime.now().strftime('%Y-%m-%d')
current_time = datetime.now().strftime('%H:%M:%S')
date_label = tk.Label(window, text=f"Time Keeper - {current_date} - {current_time}")
date_label.grid(row=0, column=1, columnspan=3)

# Buttons
edit_button = tk.Button(window, text="Edit", command=toggle_edit_mode, bg='lightgray')
edit_button.grid(row=0, column=0)

reset_button = tk.Button(window, text="Reset", command=reset_fields)
reset_button.grid(row=0, column=3)

# Entries
entries = []
initial_entry = {
    'name': tk.Entry(window),
    'cn': tk.Button(window, text="CN", command=open_cn_popup),
    'time': tk.Entry(window, state='readonly'),
    'start_stop': tk.Button(window, text="Start", command=lambda: toggle_timer(0)),
    'running': False
}
initial_entry['name'].grid(row=2, column=0)
initial_entry['cn'].grid(row=2, column=1)
initial_entry['time'].grid(row=2, column=2)
initial_entry['time'].insert(0, '00:00:00')
initial_entry['start_stop'].grid(row=2, column=3)
entries.append(initial_entry)

# Add Entry Button
plus_button = tk.Button(window, text="+", command=add_entry)
plus_button.grid(row=3, column=3)

# Load data from the database
load_data()

# Update window title with current time
update_title()

# Main loop
window.mainloop()

conn.close()
