import tkinter as tk
import os
import mysql.connector
from math import sqrt

def open_file(file):
    with open(file, "r") as file:
        measurements = []
        drawing = []
        building = []
        found_empty_line = False
        empty_line_count = 0
        for line in file:
            line = line.strip()
            if not line:
                if not found_empty_line:
                    found_empty_line = True
                else:
                    empty_line_count += 1
                continue
            if not found_empty_line:
                measurements.append(line)
            elif empty_line_count == 0:
                drawing.append(line)
            else:
                building.append(line)
    return measurements, drawing, building

def create_points(drawing, cursor):
    points = {"0": [10, 10]}
    for line in drawing:
        key, value_str = line.strip().split(" ", 1)
        value = value_str[value_str.index("(")+1:value_str.rindex(")")]
        first_coord = value.split("|")
        points[key] = [eval(first_coord[0]), eval(first_coord[1])]
    return points

def draw_points(points, canvas):
    for key, value in points.items():
        x, y = value
        canvas.create_oval(x-5, y-5, x+5, y+5, fill="black", tags="drawing") 
        canvas.create_text(x, y+12, text=key, fill="black", font=("Helvetica", 12), tags="drawing") 

def draw_lines(building, points, canvas):
    for line in building:
        eval(line)

def create_drawing(cursor, d, b, canvas):
    points = create_points(d, cursor)
    draw_points(points, canvas)
    draw_lines(b, points, canvas)

def check_measurements(m, d, b, root, canvas):
    conn = mysql.connector.connect(
        host="localhost",  
        user="darya",  
        password="1234",
        database="MyDefaultDatabase"  
    )
    cursor = conn.cursor()
    zero_measurements = []
    for each in m:
        cursor.execute("SELECT measurement_value FROM measurements WHERE measurement_name = %s", (each,))
        result = cursor.fetchone()

        if result and result[0] == 0:
            zero_measurements.append(each)
        else:
            pass
    if len(zero_measurements)!=0:
        write_m_window = tk.Toplevel(root)
        write_m_window.title("Введите недостающие данные")
        entries = []
        labels = []
        for i, line in enumerate(zero_measurements):
            label_text = line.strip()+":"
            label = tk.Label(write_m_window, text=label_text)
            label.grid(row=i, column=0, sticky="e")
            entry = tk.Entry(write_m_window)
            entry.grid(row=i, column=1, padx=5, pady=5)
            entries.append(entry)
            labels.append(line.strip())
        def on_ok():
            for label, entry in zip(labels, entries):
                value = entry.get()
                if value:
                    cursor.execute("UPDATE measurements SET measurement_value = %s WHERE measurement_name = %s",(value, label))
                
            conn.commit()
            write_m_window.destroy()
            create_drawing(cursor, d, b, canvas)
        ok_button = tk.Button(write_m_window, text="Ок", command=on_ok)
        ok_button.grid(row=len(entries), column=0, columnspan=2)
    else:
        create_drawing(cursor, d, b, canvas)


def on_clothes_selection(name, root, canvas):
    zero_measurements = []
    m, d, b = open_file(os.path.join("Database/", name.split(".")[0]+".txt"))
    check_measurements(m, d, b, root, canvas)