from flask import Flask
from flask import render_template
import time
import RPi.GPIO as GPIO

# Global crossfading variables
black     = ( 0, 0, 0 )
white     = ( 100, 100, 100 )
red       = ( 100, 0, 0 )
green     = ( 0, 100, 0 )
blue      = ( 0, 0, 100 )
yellow    = ( 40, 95, 0 )
dimWhite  = ( 30, 30, 30 )
redVal    = black[0]
grnVal    = black[1]
bluVal    = black[2]
prevR     = redVal
prevG     = grnVal
prevB     = bluVal
wait      = 0.0001
hold      = 2
DEBUG     = 0
loopCount = 60
repeat    = 3
j         = 0

# Setup GPIO pins
GPIO.setmode(GPIO.BOARD)

class Lights:
    def __init__(self, redPin, grnPin, bluPin):
        self.redPin = redPin
        self.grnPin = grnPin
        self.bluPin = bluPin

        GPIO.setup(self.redPin, GPIO.OUT)
        GPIO.setup(self.grnPin, GPIO.OUT)
        GPIO.setup(self.bluPin, GPIO.OUT)
        self.redPin = GPIO.PWM( self.redPin, 50 )
        self.grnPin = GPIO.PWM( self.grnPin, 50 )
        self.bluPin = GPIO.PWM( self.bluPin, 50 )
        self.redPin.start(0)
        self.grnPin.start(0)
        self.bluPin.start(0)        

lights = [ Lights(3,5,7), Lights(11,13,15), Lights(19,21,23) ]

def calculateStep( prevValue, endValue ):
    step = endValue - prevValue
    if (step):
        step = 1020/step
    return int(step)

def calculateVal( step, val, i ):
    if ((step) and (i % step) == 0):
        if (step > 0):
            val += 1

        elif (step < 0):
            val -= 1

    if (val > 100):
        val = 100

    elif (val < 0):
        val = 0

    return val

def crossFade( lightID, color ):
    global prevR, prevG, prevB, redVal, grnVal, bluVal

    R = color[0]
    G = color[1]
    B = color[2]

    stepR = calculateStep( prevR, R )
    stepG = calculateStep( prevG, G )
    stepB = calculateStep( prevB, B )

    for i in range( 0, 1020 ):

        redVal = calculateVal( stepR, redVal, i )
        grnVal = calculateVal( stepG, grnVal, i )
        bluVal = calculateVal( stepB, bluVal, i )

        if ( prevR != redVal ):
            lights[lightID].redPin.ChangeDutyCycle( redVal )
        if ( prevG != grnVal ):
            lights[lightID].grnPin.ChangeDutyCycle( grnVal )
        if ( prevB != bluVal ):
            lights[lightID].bluPin.ChangeDutyCycle( bluVal )

        time.sleep( wait )

        if ( DEBUG ):
            print( "Loop/RGB: #" )
            print( redVal, grnVal, bluVal )
            print( i )
            print()


    prevR = redVal
    prevG = grnVal
    prevB = bluVal
    time.sleep( hold )

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('content.html')

@app.route('/light/color/<id>/<red>/<green>/<blue>')
def changeColor(id=0, red=0, green=0, blue=0):
    lightID = int(id)
    color = [int(red), int(green), int(blue)]
    crossFade(lightID, color)

if __name__ == '__main__':
    app.run(host='0.0.0.0')