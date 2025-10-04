from tkinter import ttk

def create_canvas_back(_canvas_back, _canvas_frame):
    frame_back = ttk.Frame(_canvas_frame)
    frame_back.grid(row=0, column=1, padx=4, pady=5)
    button_frame_back = ttk.Frame(frame_back)
    button_frame_back.grid(pady=5)

    btn_x1_negative = ttk.Button(button_frame_back, text='←', command=lambda: _canvas_back.move_by("X1", -10), width=3)
    btn_x1_negative.grid(row=0, column=0, padx=2, pady=2)
    btn_x1_positive = ttk.Button(button_frame_back, text='→', command=lambda: _canvas_back.move_by("X1", 10), width=3)
    btn_x1_positive.grid(row=0, column=1, padx=2, pady=2)
    btn_y1_positive = ttk.Button(button_frame_back, text='↓', command=lambda: _canvas_back.move_by("Y1", 10), width=3)
    btn_y1_positive.grid(row=1, column=0, padx=2, pady=2)
    btn_y1_negative = ttk.Button(button_frame_back, text='↑', command=lambda: _canvas_back.move_by("Y1", -10), width=3)
    btn_y1_negative.grid(row=1, column=1, padx=2, pady=2)

    _canvas_back.update_red_rectangle()

    frame_rectangle = ttk.Frame(frame_back)
    frame_rectangle.grid(pady=30)
    label_rectangle = ttk.Label(frame_rectangle, text="Move Red Rectangle")
    label_rectangle.grid(row=0, column=0, columnspan=2)

    button_frame_rectangle = ttk.Frame(frame_rectangle)
    button_frame_rectangle.grid(row=1, column=0, columnspan=2)

    btn_rectangle_x1_negative = ttk.Button(button_frame_rectangle, text='←', command=lambda: _canvas_back.adjust_blocked_position(-10, 0), width=3)
    btn_rectangle_x1_negative.grid(row=0, column=0, padx=2, pady=2)
    btn_rectangle_x1_positive = ttk.Button(button_frame_rectangle, text='→', command=lambda: _canvas_back.adjust_blocked_position(10, 0), width=3)
    btn_rectangle_x1_positive.grid(row=0, column=1, padx=2, pady=2)
    btn_rectangle_y1_positive = ttk.Button(button_frame_rectangle, text='↓', command=lambda: _canvas_back.adjust_blocked_position(0, 10), width=3)
    btn_rectangle_y1_positive.grid(row=1, column=0, padx=2, pady=2)
    btn_rectangle_y1_negative = ttk.Button(button_frame_rectangle, text='↑', command=lambda: _canvas_back.adjust_blocked_position(0, -10), width=3)
    btn_rectangle_y1_negative.grid(row=1, column=1, padx=2, pady=2)

    return _canvas_back

def create_canvas_seat(_canvas_seat, _canvas_frame):
    frame_seat = ttk.Frame(_canvas_frame)
    frame_seat.grid(row=1, column=1, padx=10, pady=10)
    button_frame_seat = ttk.Frame(frame_seat)
    button_frame_seat.grid(pady=5)

    btn_x2_negative = ttk.Button(button_frame_seat, text='←', command=lambda: _canvas_seat.move_by("X2", -10), width=3)
    btn_x2_negative.grid(row=0, column=0, padx=2, pady=2)
    btn_x2_positive = ttk.Button(button_frame_seat, text='→', command=lambda: _canvas_seat.move_by("X2", 10), width=3)
    btn_x2_positive.grid(row=0, column=1, padx=2, pady=2)
    btn_y2_negative = ttk.Button(button_frame_seat, text='↓', command=lambda: _canvas_seat.move_by("Y2", 10), width=3)
    btn_y2_negative.grid(row=1, column=0, padx=2, pady=2)
    btn_y2_positive = ttk.Button(button_frame_seat, text='↑', command=lambda: _canvas_seat.move_by("Y2", -10), width=3)
    btn_y2_positive.grid(row=1, column=1, padx=2, pady=2)

    return _canvas_seat

def create_canvas_leg(_canvas_leg, _canvas_frame):
    frame_leg = ttk.Frame(_canvas_frame)
    frame_leg.grid(row=2, column=1, padx=10, pady=10)
    button_frame_leg = ttk.Frame(frame_leg)
    button_frame_leg.grid(pady=5)

    btn_y3_negative = ttk.Button(button_frame_leg, text='↓', command=lambda: _canvas_leg.move_by("Y3", 10), width=3)
    btn_y3_negative.grid(row=0, column=0, padx=2, pady=2)
    btn_y3_positive = ttk.Button(button_frame_leg, text='↑', command=lambda: _canvas_leg.move_by("Y3", -10), width=3)
    btn_y3_positive.grid(row=1, column=0, padx=2, pady=2)

    return _canvas_leg

def create_canvas_dc_motor_buttons(canvas_frame, arduino):
    frame_motor = ttk.Frame(canvas_frame)
    frame_motor.grid(row=3, column=0, pady=10)
    label_motor = ttk.Label(frame_motor, text="DC-Motor-Steuerung")
    label_motor.grid(row=3, column=0, columnspan=3)
    btn_motor_reverse = ttk.Button(frame_motor, text="Motor Vorwärts", command=lambda: motor_command(arduino, 'FORWARD'))
    btn_motor_reverse.grid(row=4, column=0, padx=3)
    btn_motor_stop = ttk.Button(frame_motor, text="Motor Stop", command=lambda: motor_command(arduino, 'STOP'))
    btn_motor_stop.grid(row=5, column=0, columnspan=2, pady=4, padx=3)
    btn_motor_forward = ttk.Button(frame_motor, text="Motor Rückwärts", command=lambda: motor_command(arduino, 'REVERSE'))
    btn_motor_forward.grid(row=4, column=1, padx=3)

def create_canvas_save_button(canvas_frame, pelvi):
    btn_save = ttk.Button(canvas_frame, text="Save", command=lambda: save_data(pelvi))
    btn_save.grid(row=3, column=2, padx=3, pady=5)

def create_canvas_home_button(canvas_frame, arduino, canvas_back, canvas_seat, canvas_leg):
    btn_home = ttk.Button(canvas_frame, text="Home", command=lambda: home_motors(arduino, [canvas_back, canvas_seat, canvas_leg]))
    btn_home.grid(row=3, column=1, padx=3, pady=5)

def home_motors(arduino, canvas_areas):
    arduino.send_command('HOMING')
    print("Befehl: HOMING")
    for canvas_area in canvas_areas:
        canvas_area.homing_position()

def motor_command(arduino, motor_cmd):
    command = 'MOTOR ' + motor_cmd
    arduino.send_command(command)
    print(f"DC Motor-Befehl: {command}")

def save_data(pelvi):
    pelvi.save_user_data()
    print("Data saved")
