import tkinter as tk
from pelvi.background import load_image_to_canvas

class CanvasArea:
    def __init__(self, parent, pelvi, axis1, axis2, width, height, background_image, click_callback):
        self.canvas = tk.Canvas(parent, width=width, height=height)
        load_image_to_canvas(self.canvas, background_image, width, height)
        self.canvas.bind("<Button-1>", click_callback)
        self.canvas.bind("<Configure>", self.on_resize)
        self.pelvi = pelvi
        self.point = None
        self.axis1 = axis1
        self.axis2 = axis2

    def on_resize(self, event):
        self.update_point()

    def update_point(self):
        if self.axis1 == self.axis2:
            x_pixel = self.canvas.winfo_width() // 2
            y_pixel = self.pelvi.get_axis_value(self.axis1)
        else:
            x_pixel = self.pelvi.get_axis_value(self.axis1)
            y_pixel = self.pelvi.get_axis_value(self.axis2)

        if self.point:
            self.canvas.delete(self.point)
        self.point = self.canvas.create_oval(x_pixel - 5, y_pixel - 5, x_pixel + 5, y_pixel + 5, fill='blue')

    def create_axes_lines(self, axis1_pos, axis2_pos):
        self.canvas.create_line(axis1_pos, 0, axis1_pos, self.canvas.winfo_height(), fill="black")
        self.canvas.create_line(0, axis2_pos, self.canvas.winfo_width(), axis2_pos, fill="black")

    def delete_point(self):
        if self.point:
            self.canvas.delete(self.point)
            self.point = None

    def update_red_rectangle(self):
        # Get current rectangle coordinates from pelvi
        rectangle_left, rectangle_right = self.pelvi.get_blocked_area("X")
        rectangle_top, rectangle_bottom = self.pelvi.get_blocked_area("Y")

        self.canvas.delete('red_rectangle')

        self.canvas.create_rectangle(
            rectangle_left,
            rectangle_top,
            rectangle_right,
            rectangle_bottom,
            fill='red',
            outline='',
            tags='red_rectangle'
        )