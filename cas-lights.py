from flask import Flask
from flask import render_template
import time
import RPi.GPIO as GPIO
import json

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
        self.redPin = GPIO.PWM( self.redPin, 120 )
        self.grnPin = GPIO.PWM( self.grnPin, 120 )
        self.bluPin = GPIO.PWM( self.bluPin, 120 )
        self.redPin.start(0)
        self.grnPin.start(0)
        self.bluPin.start(0)

        self.redVal = 0
        self.grnVal = 0
        self.bluVal = 0

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

        l = lights[lightID]

        l.redVal = calculateVal( stepR, l.redVal, i )
        l.grnVal = calculateVal( stepG, l.grnVal, i )
        l.bluVal = calculateVal( stepB, l.bluVal, i )

        if ( prevR != l.redVal ):
            lights[lightID].redPin.ChangeDutyCycle( l.redVal )
        if ( prevG != l.grnVal ):
            lights[lightID].grnPin.ChangeDutyCycle( l.grnVal )
        if ( prevB != l.bluVal ):
            lights[lightID].bluPin.ChangeDutyCycle( l.bluVal )

        time.sleep( wait )

        if ( DEBUG ):
            print( "Loop/RGB: #" )
            print( l.redVal, l.grnVal, l.bluVal )
            print( i )
            print()


    prevR = l.redVal
    prevG = l.grnVal
    prevB = l.bluVal

    time.sleep( hold )

def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

app = Flask(__name__)

@app.route('/')
def home():
    lights_page = []
    for light in lights:
        try:
            color = rgb_to_hex((light.redVal * 255 / 100, light.grnVal * 255 / 100, light.bluVal * 255 / 100))
            lights_page.append(color)
        except Exception as e:
            print (e)
    return render_template('content.html', lights=lights_page)

@app.route('/light/color/<id>/<red>/<green>/<blue>')
def changeColor(id=0, red=0, green=0, blue=0):
    lightID = int(id)
    color = [int(red), int(green), int(blue)]
    crossFade(lightID, color)

@app.route('/light/status/<id>')
def lightStatus(id=0):
    lightID = int(id)
    l = lights[lightID]

    try:
        return json.dumps({'id' : lightID, 'red' : l.redVal, 'blue' : l.bluVal, 'green' : l.grnVal}, separators=(',',':'))
    except Exception as e:
        return e

if __name__ == '__main__':
    app.run(host='0.0.0.0')