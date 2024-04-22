from cmu_graphics import *

class Knob:
    
    def __init__(self, cx, cy, minVal, maxVal, startVal, name):
        self.cx = cx
        self.cy = cy
        self.min = minVal
        self.max = maxVal
        self.currPos = startVal
        self.name = name
        self.beingTurned = False

    def __repr__(self):
        return f'{self.name} Knob at ({self.cx},{self.cy})'

    def 



def onAppStart(app):
    app.testKnob = Knob(cx=app.width//2, cy=app.height//2)

def redrawAll(app):
    pass




class Button:

    buttons = []

    def __init__(self, cx, cy, width, height, onColor='limeGreen', 
                 offColor='red'):
        self.leftX = cx - width//2
        self.topY = cy - height//2
        self.width = width
        self.height = height
        self.onColor = onColor
        self.offColor = offColor
        self.pressed = False

    def __repr__(self):
        return f'Button({self.leftX},{self.topY}), pressed:{self.pressed}'

    def drawButton(self, borderFill=None):
        if self.pressed:
            color = self.onColor
        elif not(self.pressed):
            color = self.offColor
        # color = self.onColor if self.pressed else self.offColor
        drawRect(self.leftX, self.topY, self.width, self.height,
                 fill=color, border=borderFill, borderWidth=2)

    def checkPressInButton(self, mouseX, mouseY):
        if (self.leftX <= mouseX <= self.leftX + self.width and
            self.topY <= mouseY <= self.topY + self.height):
            self.pressed = not(self.pressed)