import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os
from functions import *

import mysql.connector


def connect_to_database():
    conn = mysql.connector.connect(
    host="localhost",
    user="darya",
    password="1234"
    )

    cursor = conn.cursor()

    cursor.execute("SHOW DATABASES")
    databases = cursor.fetchall()
    default_exists = False

    for db in databases:
        if db[0] == "MyDefaultDatabase":
            default_exists = True
            break

    if not default_exists:
        cursor.execute("CREATE DATABASE MyDefaultDatabase")

    conn.database = "MyDefaultDatabase"

    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    measurements_table_exists = False

    for table in tables:
        if table[0] == "Measurements":
            measurements_table_exists = True
            break

    if not measurements_table_exists:
        create_table_query = """
        CREATE TABLE Measurements (
            id INT AUTO_INCREMENT PRIMARY KEY,
            measurement_name VARCHAR(255),
            measurement_value FLOAT
        )
        """
        cursor.execute(create_table_query)

        file_path = "Measurements.txt"

        with open(file_path, "r") as file:
            measurements = file.readlines()

        for measurement in measurements:
            measurement_name = measurement.strip()
            insert_query = "INSERT INTO Measurements (measurement_name, measurement_value) VALUES (%s, %s)"
            cursor.execute(insert_query, (measurement_name, 0))

        conn.commit()

    cursor.close()
    conn.close()

def on_tool_click(tool_name):
    if (root["cursor"] == 'hand') and (tool_name != "4Move.png"):
        root.config(cursor="")
    if tool_name == "1Plus.png":
        new(tk, buttons, drawing_label, root, canvas)
    if tool_name == "1Image.png":
        open_image()
    if tool_name == "2Line.png":
        open_image()
    if tool_name == "4Move.png":
        if root["cursor"] == 'hand':
            root.config(cursor="")
        else:
            root.config(cursor="hand")
    if tool_name == "2Save.png":
        export_canvas(root, canvas)
    if tool_name == "3Length.png":
        show_measurments(root)
    


root = tk.Tk()
root.title("Мой редактор")
root.geometry("1060x689")
root.configure(bg='#292929')

top_tools_frame = tk.Frame(root, bg='#323131', highlightbackground="#818181", highlightthickness=2)
top_tools_frame.pack(side=tk.TOP, fill=tk.X)

top_tools_icons = [file for file in os.listdir("icons/Top") if not file.startswith('.')]
top_tools_icons.sort()
buttons = []
for icon in top_tools_icons:
    tool_icon = tk.PhotoImage(file=os.path.join("icons/Top/", icon))
    tool_button = tk.Button(top_tools_frame, image=tool_icon, bd=0, highlightthickness=0, command=lambda icon=icon: on_tool_click(icon))
    tool_button.image = tool_icon
    tool_button.pack(side=tk.LEFT, padx=20, pady=10)
    buttons.append(tool_button)

tools_frame = tk.Frame(root, width=210, height=root.winfo_height(), bg='#323131', highlightbackground="#818181", highlightthickness=2)
tools_frame.pack(side=tk.LEFT, fill=tk.Y)

tools_label = tk.Label(tools_frame, text="Tools", bg='#323131', fg='white', font=("Inter", 20, "bold"))
tools_label.pack(side=tk.TOP, pady=(10, 0))

left_tools_icons = [file for file in os.listdir("icons/Left") if not file.startswith('.')]
left_tools_icons.sort()
for i in range(3):
    row_frame = tk.Frame(tools_frame, width=210)
    row_frame.pack(side=tk.TOP, fill=tk.X, padx=20, pady=10)
    for j in range(2):
        index = i * 2 + j
        if i==2 and j==1:
            break
        if index < len(left_tools_icons):
            tool_icon = tk.PhotoImage(file=os.path.join("icons/Left/", left_tools_icons[index]))
            tool_button = tk.Button(row_frame, image=tool_icon, command=lambda idx=index: on_tool_click(left_tools_icons[idx]))
            tool_button.image = tool_icon  
            tool_button.pack(side=tk.LEFT, padx=25, pady=5)
            buttons.append(tool_button)
    
layer_label_frame = tk.Frame(tools_frame, width=210, bg='#323131', highlightbackground="#818181", highlightthickness=2)
layer_label_frame.pack(side=tk.TOP, fill=tk.X, pady=(25, 0))

layer_label = tk.Label(layer_label_frame, text="Layers", bg='#323131', fg='white', font=("Inter", 14, "bold"), compound=tk.LEFT)
layer_icon = tk.PhotoImage(file="icons/Layer.png")  
layer_label.config(image=layer_icon)
layer_label.pack(side=tk.TOP, pady=10)

layer_frame = tk.Frame(tools_frame, width=210, bg='#323131')
layer_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)  

drawing_label = tk.Label(layer_frame, text="Чертеж 1", bg='#323131', fg='white', font=("Inter", 14), compound=tk.LEFT)
drawing_icon = tk.PhotoImage(file="icons/Drawing.png")  
drawing_label.config(image=drawing_icon)

canvas = tk.Canvas(root, bg="white", width=623, height=496)
canvas.pack(side=tk.TOP, pady=69)

for button in buttons:
    if str(button) == ".!frame.!button":
        continue
    button.config(state=tk.DISABLED)

connect_to_database()



def open_image():
    global img, img_id, photo_img, img_width, img_height
    file_path = filedialog.askopenfilename()
    if file_path:
        img = Image.open(file_path)
        img.thumbnail((250, 250))
        photo_img = ImageTk.PhotoImage(img)
        img_width, img_height = img.size
        display_image()

def display_image():
    global img_id
    if img_id:
        canvas.delete(img_id)
    img_id = canvas.create_image(250, 250, anchor=tk.CENTER, image=photo_img, tags="image")


def move_items(event):
    global start_x, start_y, selected, img_id, img_width, img_height
    current_cursor = root["cursor"]
    if current_cursor == "hand":
        if 'start_x' in globals():
            if selected != 'image':
                dx = event.x - start_x
                dy = event.y - start_y
                canvas.move("drawing", dx, dy)
                start_x, start_y = event.x, event.y
            else:
                canvas.coords(img_id, event.x, event.y)

def start_move(event):
    global start_x, start_y, selected
    start_x, start_y = event.x, event.y
    clicked_item = event.widget.find_closest(event.x, event.y)
    tags = event.widget.gettags(clicked_item)
    if clicked_item:
        selected = tags[0]


def handle_keypress(event):
    global img_id, selected
    if event.char == 'x' and selected:
        if selected == 1:
            canvas.delete("drawing")
        else:
            canvas.delete(selected)
        if selected == img_id:
            img_id = None



canvas.bind("<B1-Motion>", move_items)
canvas.bind("<Button-1>", start_move)
root.bind("<Key>", handle_keypress)

img = None
photo_img = None
img_id = None
img_width = 0
img_height = 0
selected_image = None

root.mainloop()







