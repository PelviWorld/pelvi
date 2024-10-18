from tkinter import ttk

def create_canvas_xy(_canvas_xy, _canvas_frame):
    frame_xy = ttk.Frame(_canvas_frame)
    frame_xy.grid(row=1, column=0, padx=4, pady=5)
    button_frame_xy = ttk.Frame(frame_xy)
    button_frame_xy.grid(pady=5)

    btn_x_negative = ttk.Button(button_frame_xy, text='←', command=lambda: _canvas_xy.move_by("X", -10), width=3)
    btn_x_negative.grid(row=0, column=0, padx=2, pady=2)
    btn_x_positive = ttk.Button(button_frame_xy, text='→', command=lambda: _canvas_xy.move_by("X", 10), width=3)
    btn_x_positive.grid(row=0, column=1, padx=2, pady=2)
    btn_y_positive = ttk.Button(button_frame_xy, text='↓', command=lambda: _canvas_xy.move_by("Y", 10), width=3)
    btn_y_positive.grid(row=1, column=0, padx=2, pady=2)
    btn_y_negative = ttk.Button(button_frame_xy, text='↑', command=lambda: _canvas_xy.move_by("Y", -10), width=3)
    btn_y_negative.grid(row=1, column=1, padx=2, pady=2)

    _canvas_xy.update_red_rectangle()

    frame_rectangle = ttk.Frame(frame_xy)
    frame_rectangle.grid(pady=3)
    label_rectangle = ttk.Label(frame_rectangle, text="Move Red Rectangle")
    label_rectangle.grid(row=0, column=0, columnspan=2)

    button_frame_rectangle = ttk.Frame(frame_rectangle)
    button_frame_rectangle.grid(row=1, column=0, columnspan=2)

    btn_rectangle_x_negative = ttk.Button(button_frame_rectangle, text='←', command=lambda: _canvas_xy.adjust_blocked_position(-10, 0), width=3)
    btn_rectangle_x_negative.grid(row=0, column=0, padx=2, pady=2)
    btn_rectangle_x_positive = ttk.Button(button_frame_rectangle, text='→', command=lambda: _canvas_xy.adjust_blocked_position(10, 0), width=3)
    btn_rectangle_x_positive.grid(row=0, column=1, padx=2, pady=2)
    btn_rectangle_y_positive = ttk.Button(button_frame_rectangle, text='↓', command=lambda: _canvas_xy.adjust_blocked_position(0, 10), width=3)
    btn_rectangle_y_positive.grid(row=1, column=0, padx=2, pady=2)
    btn_rectangle_y_negative = ttk.Button(button_frame_rectangle, text='↑', command=lambda: _canvas_xy.adjust_blocked_position(0, -10), width=3)
    btn_rectangle_y_negative.grid(row=1, column=1, padx=2, pady=2)

    return _canvas_xy

def create_canvas_ze0_buttons(_canvas_ze0, _canvas_frame):
    frame_ze0 = ttk.Frame(_canvas_frame)
    frame_ze0.grid(row=1, column=1, padx=10, pady=10)
    button_frame_ze0 = ttk.Frame(frame_ze0)
    button_frame_ze0.grid(pady=5)

    btn_z_negative = ttk.Button(button_frame_ze0, text='←', command=lambda: _canvas_ze0.move_by("Z", -10), width=3)
    btn_z_negative.grid(row=0, column=0, padx=2, pady=2)
    btn_z_positive = ttk.Button(button_frame_ze0, text='→', command=lambda: _canvas_ze0.move_by("Z", 10), width=3)
    btn_z_positive.grid(row=0, column=1, padx=2, pady=2)
    btn_e0_negative = ttk.Button(button_frame_ze0, text='↓', command=lambda: _canvas_ze0.move_by("E0", 10), width=3)
    btn_e0_negative.grid(row=1, column=0, padx=2, pady=2)
    btn_e0_positive = ttk.Button(button_frame_ze0, text='↑', command=lambda: _canvas_ze0.move_by("E0", -10), width=3)
    btn_e0_positive.grid(row=1, column=1, padx=2, pady=2)

    return _canvas_ze0

def create_canvas_e1_buttons(_canvas_e1, _canvas_frame):
    frame_e1 = ttk.Frame(_canvas_frame)
    frame_e1.grid(row=1, column=2, padx=10, pady=10)
    button_frame_e1 = ttk.Frame(frame_e1)
    button_frame_e1.grid(pady=5)

    btn_e1_negative = ttk.Button(button_frame_e1, text='↓', command=lambda: _canvas_e1.move_by("E1", 10), width=3)
    btn_e1_negative.grid(row=0, column=0, padx=2, pady=2)
    btn_e1_positive = ttk.Button(button_frame_e1, text='↑', command=lambda: _canvas_e1.move_by("E1", -10), width=3)
    btn_e1_positive.grid(row=1, column=0, padx=2, pady=2)

    return _canvas_e1

def create_canvas_dc_motor_buttons(canvas_frame, arduino):
    frame_motor = ttk.Frame(canvas_frame)
    frame_motor.grid(row=3, column=0, pady=10)
    label_motor = ttk.Label(frame_motor, text="DC-Motor-Steuerung")
    label_motor.grid(row=3, column=0, columnspan=3)
    btn_motor_reverse = ttk.Button(frame_motor, text="Motor Vorwärts", command=lambda: motor_command(arduino, 'MOTOR FORWARD'))
    btn_motor_reverse.grid(row=4, column=0, padx=3)
    btn_motor_stop = ttk.Button(frame_motor, text="Motor Stop", command=lambda: motor_command(arduino, 'MOTOR STOP'))
    btn_motor_stop.grid(row=5, column=0, columnspan=2, pady=4, padx=3)
    btn_motor_forward = ttk.Button(frame_motor, text="Motor Rückwärts", command=lambda: motor_command(arduino, 'MOTOR REVERSE'))
    btn_motor_forward.grid(row=4, column=1, padx=3)

def create_canvas_save_button(canvas_frame, pelvi):
    btn_save = ttk.Button(canvas_frame, text="Save", command=lambda: save_data(pelvi))
    btn_save.grid(row=3, column=2, padx=3, pady=5)

def motor_command(arduino, command):
    arduino.send_coordinates('MOTOR', command)
    print(f"DC Motor-Befehl: {command}")

def save_data(pelvi):
    pelvi.save_user_data()
    print("Data saved")
