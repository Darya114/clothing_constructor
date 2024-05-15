from PIL import ImageGrab, Image, ImageTk
from tkinter import filedialog
import tkinter as tk
from tkinter import ttk
import os
import mysql.connector
from textwork import *

def export_canvas(root, canvas):
    x = root.winfo_rootx() + canvas.winfo_x()
    y = root.winfo_rooty() + canvas.winfo_y()
    x1 = x + canvas.winfo_width()
    y1 = y + canvas.winfo_height()
    
    screenshot = ImageGrab.grab(bbox=(x, y, x1, y1))
    
    file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png"), ("JPEG files", "*.jpg")])
    if file_path:
        file_extension = file_path.split(".")[-1].upper()
        if file_extension not in ["PNG", "JPEG"]:
            file_extension = "PNG"
        screenshot.save(file_path)


def center_window(root, window):
    root.update_idletasks()
    width = window.winfo_reqwidth()
    height = window.winfo_reqheight()
    x = (root.winfo_width() // 2) + root.winfo_x() - (width // 2)
    y = (root.winfo_height() // 2) + root.winfo_y() - (height // 2)
    window.geometry(f'{width}x{height}+{x}+{y}')


def show_measurments(root):
    conn = mysql.connector.connect(
        host="localhost",  
        user="darya",  
        password="1234", 
        database="MyDefaultDatabase"  
    )
    cursor = conn.cursor()

    cursor.execute("SELECT id, measurement_name, measurement_value FROM measurements")
    measurements = cursor.fetchall()
    measurements = [(id, f"{name}:", value) for id, name, value in measurements]
    measurements_window = tk.Toplevel(root)
    measurements_window.title("Список измерений")
    style = ttk.Style()
    style.configure("Treeview", background="#292929", foreground="white", fieldbackground="#292929")
    tree = ttk.Treeview(measurements_window, columns=('ID', 'Измерение', 'Значение'), show='headings')
    tree.heading('ID', text='№')
    tree.heading('Измерение', text='Измерение')
    tree.heading('Значение', text='Значение')
    tree.pack(fill=tk.BOTH, expand=True)

    for measurement in measurements:
        tree.insert('', tk.END, values=measurement)
    

    def on_double_click(event):
        item = tree.selection()[0]
        values = tree.item(item, "values")
        measurement_id = values[0]
        measurement_name = values[1]
        measurement_value = values[2]

        edit_window = tk.Toplevel(measurements_window)
        edit_window.title(f"Изменение")

        tk.Label(edit_window, text=f"{measurement_name}").pack(pady=10)
        new_value_var = tk.StringVar(value=measurement_value)
        tk.Entry(edit_window, textvariable=new_value_var, bg='#292929').pack(pady=10)
        tk.Button(edit_window, text="OK", command=lambda: update_value(edit_window, item, new_value_var.get())).pack(pady=10)
        center_window(root, edit_window)

    def update_value(edit_window, item, new_value):
        tree.item(item, values=(tree.item(item, "values")[0], tree.item(item, "values")[1], new_value))
        edit_window.destroy()

    tree.bind("<Double-1>", on_double_click)

    def save_changes():
        updated_measurements = []
        for item in tree.get_children():
            measurement_id = tree.item(item, "values")[0]
            measurement_name = tree.item(item, "values")[1]
            measurement_value = tree.item(item, "values")[2]
            updated_measurements.append((measurement_id, measurement_name, measurement_value))
        for measurement in updated_measurements:
            cursor.execute(
                "UPDATE measurements SET measurement_value = %s WHERE id = %s",
                (measurement[2], measurement[0])
            )

        conn.commit()
        measurements_window.destroy()
        conn.close()

    tk.Button(measurements_window, text="Сохранить изменения", command=save_changes).pack(pady=10)

    center_window(root, measurements_window)

def open_pattern_database(root, canvas):
    clothes_icons = [file for file in os.listdir("icons/PatternDatabase") if not file.startswith('.')]
    clothes_icons.sort()
    tool_selection_window = tk.Toplevel(root)
    tool_selection_window.title("Выберите изделие")
    for i, icon_path in enumerate(clothes_icons):
        row = i // 2
        col = i % 2
        tool_icon = tk.PhotoImage(file=os.path.join("icons/PatternDatabase/", icon_path))
        tool_icon = tool_icon.subsample(4, 4)
        tool_button = tk.Button(tool_selection_window, image=tool_icon, command=lambda clothes_name=icon_path: on_clothes_selection(clothes_name, root, canvas))
        tool_button.image = tool_icon
        tool_button.grid(row=row, column=col, padx=5, pady=5)
    center_window(root, tool_selection_window)

def open_modal(root, buttons, drawing_label, canvas):
    def choice():
        if option_var.get() == 'Индивидуальный чертеж':
            points = {}
            canvas.create_oval(5, 5, 10, 10, fill="black", tags="drawing") 
            canvas.create_text(10, 20, text=0, fill="black", tags="drawing")
            points['0'] = (5, 5)
        else:
            open_pattern_database(root, canvas)
        modal.destroy()
        for button in buttons:
            button.config(state=tk.NORMAL)
            drawing_label.pack(side=tk.LEFT, padx=10)

    modal = tk.Toplevel(root)
    modal.title("Выбор опции")

    label = tk.Label(modal, text="Выберите опцию:")
    label.pack()
    option_var = tk.StringVar(value="База выкроек")
    
    for option in ["База выкроек", "Индивидуальный чертеж"]:
        radio_button = tk.Radiobutton(modal, text=option, variable=option_var, value=option)
        radio_button.pack(anchor=tk.W)

    ok_button = tk.Button(modal, text="OK", command=choice)
    ok_button.pack(pady=10)
    center_window(root, modal)

def new(tk, buttons, drawing_label, root, canvas):
    open_modal(root, buttons, drawing_label, canvas)
