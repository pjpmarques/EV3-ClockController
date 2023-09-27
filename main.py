#!/usr/bin/env pybricks-micropython

################################################################

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.iodevices import AnalogSensor
from pybricks.parameters import Port
from pybricks.parameters import Button
import pybricks.tools

################################################################

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
        
    def run_until_pressed(self, should_advance):
        self.motor.reset_angle(0)
        
        done = False 
        while not done:
            
            for i in range(600):
                pybricks.tools.wait(100)
                if should_advance():
                    done = True
                    break
                
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

INIT_HOUR = 14
INIT_MIN = 45

# Initialize the EV3 Brick.
ev3 = EV3Brick()
motor = Motor(Port.A)
clock = Clock(motor, INIT_HOUR, INIT_MIN)
esp32 = AnalogSensor(Port.S1)

################################################################

def calibrate():
    print("Ready to calibrate")
    print("LEFT / RIGHT Buttons for adjusting the clock to 02:45")
    print("UP when you have finished the calibration")
    
    while True:
        pressed = ev3.buttons.pressed()
        if Button.RIGHT in pressed:
            motor.run_angle(180, 1)
            print("Motor at %d" % motor.angle())
        elif Button.LEFT in pressed:
            motor.run_angle(180, -1)
            print("Motor at %d" % motor.angle())
        elif Button.UP in pressed:
            motor.reset_angle(0)
            break

    print("Calibration done")
    print("Assuming clock is set at 02:45")
    clock.go_to_time(14, 45)

def check_pressed():
    V_THRESHOLD = 2.0
    
    if (esp32.voltage() < V_THRESHOLD) or (Button.DOWN in ev3.buttons.pressed()):
        return True
    else:
        return False
    
def main():
    clock.go_to_time(14, 45)
    print("Set at 14:45")
    clock.run_until_pressed(check_pressed)
    
    clock.go_to_time(17, 27)
    print("Set at 17:27")    
    clock.run_until_pressed(check_pressed)
    
    clock.go_to_time(24 + 2, 26)
    print("Set at 2:26")    
    clock.run_until_pressed(check_pressed)
        
    clock.go_to_time(24 + 3, 58)
    print("Set at 3:58")    
    clock.run_until_pressed(check_pressed)
    
    print("=========")    
    print("Play Done")
    print("Resetting to 2:45")
    clock.go_to_time(24 + 12 + 2, 45)
    
    print("Finished")

if __name__ == "__main__":
    calibrate()
    main()    

