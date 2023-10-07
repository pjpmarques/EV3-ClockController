#!/usr/bin/env pybricks-micropython

################################################################

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor
from pybricks.ev3devices import TouchSensor
from pybricks.parameters import Port
from pybricks.parameters import Button
from pybricks.parameters import Color
from pybricks.media.ev3dev import Font
import pybricks.tools

################################################################

def ev_print(msg):
    """Prints a message both into the serial port and the EV3 display"""
    print(msg)
    ev3.screen.print(msg)

class Clock:
    """Allows to perform time calculations and control a physical clock connected to the RV3 brick."""
    
    # Constants
    TIME_TURN = 8.02              # Number of degrees that the clock motor needs to advance to represent one minute in the physical clock
    MOTOR_SPEED = 300             # Target motor speed
    
    def __init__(self, motor, hour, min):
        """Create a new instance of our clock

        Args:
            motor (pybricks.ev3devices.Motor): The motor we'll be controlling
            hour (int): start hour
            min (int): start minute
        """
        
        self.current_hour = hour
        self.current_min  = min
        self.motor = motor


    def go_to_time(self, hour, min):
        """Advance the clock to a certain time, actually actuating the motor.

        Args:
            hour (int): The hour to advance to.
            min (int): The minute to advance to.
        """
        
        delta_hours = hour - self.current_hour
        delta_mins = min - self.current_min
        if (delta_mins < 0.0):
            delta_hours-= 1.0
            delta_mins+= 60.0
                
        angle = delta_hours*60.0*Clock.TIME_TURN + delta_mins*Clock.TIME_TURN
        self.motor.run_angle(Clock.MOTOR_SPEED, angle)
            
        self.current_hour = hour
        self.current_min = min
        
        
    def set_time(self, hour, min):
        """Set the clock to a certain time without actuating the motor.

        Args:
            hour (int): The hour.
            min (int): The minute.
        """
        
        self.current_hour = hour
        self.current_min = min
        
        
    def normalize_time(self):
        """Normalize the internal clock into hours that range [0, 24["""
        self.current_hour = self.current_hour % 24
                
                
    def run_until_pressed(self, should_stop):
        """Advance the clock in real-time by actuating the motor until a button is pressed.

        Args:
            should_stop (function): A function that returns True if the clock should stop running.
        """
        
        # Advance the clock in one minute increments checking if someone pressed a button
        self.motor.reset_angle(0)        
        done = False 
        while not done:                                    
            for i in range(600):
                pybricks.tools.wait(100)
                if should_stop():
                    done = True
                    break                
            ev_print("*** 1 min ***")                
            if not done:
                self.motor.run_angle(Clock.MOTOR_SPEED, 1 * Clock.TIME_TURN)
                        
        # Update the time with the realtime that actually passed, according to what the motor was able to do
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

HOURS = [ (16, 15), (19, 0), (24 + 4, 0), (24 + 6, 30)]                     # The hours that the clock should show during the play

ev3 = None
motor = None
clock = None
touch = []

################################################################

def init_brick():
    """Initialize the EV3 Brick."""
    
    global ev3
    global motor
    global touch
    global clock
    
    ev3 = EV3Brick()
    ev3.screen.set_font(Font(size=12))
    
    # Make sure that the sensors and motors are connected
    while True:            
        try:
            motor = Motor(Port.D)            
            for port in (Port.S1, Port.S2, Port.S3, Port.S4):
                try:
                    touch.append(TouchSensor(port))
                except:
                    pass                        
            break
        except:
            motor = None
            touch = []            
            ev_print("Something is wrong")
            ev_print("Disconnect/Reconnect motor")
            pybricks.tools.wait(5000)
            ev3.screen.clear()
                
    # Initialize the clock
    clock = Clock(motor, HOURS[0][0], HOURS[0][1])    

def calibrate():
    """Ask the user to calibrate the clock to the starting hour"""
    ev3.light.on(Color.RED)
    ev3.screen.clear()
    ev_print("READY TO CALIBRATE")    
    ev_print("LEFT / RIGHT Buttons to adjust")
    ev_print("Set clock to %02d:%2d" % (HOURS[0][0] % 24, HOURS[0][1]))
    ev_print("Press UP when done")
    
    while True:
        pressed = ev3.buttons.pressed()
        if Button.RIGHT in pressed:
            motor.run_angle(100, 5)
        elif Button.LEFT in pressed:
            motor.run_angle(100, -5)
        elif (Button.UP in pressed) or any(sensor.pressed() for sensor in touch):
            motor.reset_angle(0)
            break

    clock.set_time(HOURS[0][0], HOURS[0][1])
    ev_print("Calibration done")
    ev_print("Assuming it's %02d:%02d" % (HOURS[0][0] % 24, HOURS[0][1]))
    ev_print("Going live in 5 seconds...")
    for i in range(5, 0, -1):
        pybricks.tools.wait(1000)
        ev_print("   %d" % i)
    ev3.screen.clear()
    ev_print("LIVE -- REAL TIME!")

def check_pressed():
    """Function that checks if a button is pressed to advance the clock or calibrate the device.

    Returns:
        boolean: If a button is pressed.
    """
    return any(sensor.pressed() for sensor in touch) or (Button.DOWN in ev3.buttons.pressed())
    
def main():    
    """Main loop -- run the clock through all the hours"""
    
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

# Main routine for the script
if __name__ == "__main__":    
    init_brick() 
    
    while True:        
        calibrate()        
        main()    
