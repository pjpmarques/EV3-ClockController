#!/usr/bin/env pybricks-micropython

################################################################

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.iodevices import AnalogSensor
from pybricks.ev3devices import TouchSensor
from pybricks.parameters import Port
from pybricks.parameters import Button
from pybricks.parameters import Color
from pybricks.media.ev3dev import Font
import pybricks.tools

################################################################

def ev_print(msg):
    print(msg)
    ev3.screen.print(msg)

class Clock:
    # Constants
    TIME_TURN = 8.2
    MOTOR_SPEED = 300
    
    def __init__(self, motor, hour, min):
        self.current_hour = hour
        self.current_min  = min
        self.motor = motor

    def go_to_time(self, hour, min):
        delta_hours = hour - self.current_hour
        delta_mins = min - self.current_min
        if (delta_mins < 0):
            delta_hours-= 1
            delta_mins+= 60
                
        angle = delta_hours*60*Clock.TIME_TURN + delta_mins*Clock.TIME_TURN
        self.motor.run_angle(Clock.MOTOR_SPEED, angle)
            
        self.current_hour = hour
        self.current_min = min
        
    def set_time(self, hour, min):
        self.current_hour = hour
        self.current_min = min
        
    def normalize_time(self):
        self.current_hour = self.current_hour % 24
                
    def run_until_pressed(self, should_advance):
        self.motor.reset_angle(0)
        
        done = False 
        while not done:
            
            for i in range(600):
                pybricks.tools.wait(100)
                if should_advance():
                    done = True
                    break
                
            ev_print("*** 1 min ***")
                
            if not done:
                self.motor.run_angle(Clock.MOTOR_SPEED, 1 * Clock.TIME_TURN)
                        
        time_elapsed_min = motor.angle() / Clock.TIME_TURN
        time_elapsed_hour = time_elapsed_min // 60
        time_elapsed_min = time_elapsed_min % 60
        
        self.current_hour+= time_elapsed_hour
        self.current_min+= time_elapsed_min
        if self.current_min >= 60:
            self.current_hour+= 1
            self.current_min-= 60
        
##################################################### 

# Main section and global variables

HOURS = [ (16, 15), (19, 0), (24 + 4, 0), (24 + 6, 30)]

ev3 = None
motor = None
clock = None
touch = None

################################################################

def init_brick():
    # Initialize the EV3 Brick.
    global ev3
    global motor
    global touch
    global clock
    
    ev3 = EV3Brick()
    
    ev3.screen.set_font(Font(size=12))
    
    while True:            
        try:
            motor = Motor(Port.D)
            touch = TouchSensor(Port.S1)
            break

        except:
            ev_print("Something is wrong")
            ev_print("Disconnect/Reconnect motor")
            pybricks.tools.wait(5000)
            ev3.screen.clear()
                
    clock = Clock(motor, HOURS[0][0], HOURS[0][1])
    

def calibrate():
    ev3.light.on(Color.RED)
    ev3.screen.clear()
    ev_print("Ready to calibrate")    
    ev_print("LEFT / RIGHT Buttons to adjust")
    ev_print("Set clock to %02d:%2d" % (HOURS[0][0] % 24, HOURS[0][1]))
    ev_print("Press UP when done")
    
    while True:
        pressed = ev3.buttons.pressed()
        if Button.RIGHT in pressed:
            motor.run_angle(300, 5)
        elif Button.LEFT in pressed:
            motor.run_angle(300, -5)
        elif (Button.UP in pressed) or (touch.pressed()):
            motor.reset_angle(0)
            break

    clock.set_time(HOURS[0][0], HOURS[0][1])
    ev_print("Calibration done")
    ev_print("Assuming it's %02d:%02d" % (HOURS[0][0] % 24, HOURS[0][1]))
    pybricks.tools.wait(5000)
    ev3.screen.clear()
    ev_print("LIVE -- REAL TIME!")

def check_pressed():
    if (touch.pressed()) or (Button.DOWN in ev3.buttons.pressed()):
        return True
    else:
        return False
    
def main():    
    ev3.light.on(Color.GREEN)
    for (hour, min) in HOURS:
        clock.go_to_time(hour, min)
        ev_print("Time is %02d:%02d" % (hour % 24, min))
        clock.run_until_pressed(check_pressed)
        
    ev_print("=========")    
    ev_print("Play Done")
    ev_print("Resetting to the beginning")
    clock.normalize_time()
    clock.go_to_time(HOURS[0][0], HOURS[0][1])
    ev3.screen.clear()

if __name__ == "__main__":    
    init_brick()    
    while True:        
        calibrate()        
        main()    

