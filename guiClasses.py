from cmu_graphics import *

class Fader:

    def __init__(self, name, cx, cy, width, height, minVal, maxVal, startPos,
                 target):
        self.cx = cx
        self.cy = cy
        self.name = name
        self.width = width
        self.height = height
        self.minVal = minVal
        self.maxVal = maxVal
        self.currPos = startPos
        self.actualVal = self.currPos * maxVal
        self.target = target

    def __repr__(self):
        return f'{self.name} Fader [{self.minVal} {self.maxVal}]'
    
    def moveFader(self, mouseY):
        self.beingMoved = True
        top = self.cy - self.height//2
        bot = self.cy + self.height//2
        distanceFromBot = bot - mouseY
        self.currPos = distanceFromBot / self.height            
        print(self.currPos)

    def updateValue(self, value):
        self.actualVal = self.currPos * self.maxVal
        self.target = self.actualVal

    def checkPressInFader(self, mouseX, mouseY):
        if (self.cx-self.width//2 <= mouseX <= self.cx + self.width//2 and
            self.cy-self.height//2 <= mouseY <= self.cy+self.height//2):
            return True
    
    def drawFader(self):
        percentOfFader = self.height * (self.currPos)
        bottom = self.cy + self.height//2
        top = self.cy - self.height//2
        left = self.cx - self.width//2
        drawLabel(self.name, self.cx, bottom+10)
        if self.currPos != 0:
            drawRect(left, bottom-percentOfFader, self.width, percentOfFader,
                    fill='green')

        drawRect(left, top, self.width, self.height, fill=None, border='black')

def onAppStart(app):
    app.faders = [Fader('Fader', app.width//2, app.height//2, 40, 80, 0, 100, .5)]

def redrawAll(app):
    for fader in app.faders:
        fader.drawFader()

def onMouseDrag(app, mouseX, mouseY):
    for fader in app.faders:
        if fader.checkPressInFader(mouseX, mouseY):
            fader.moveFader(mouseY)





# def main():
#     runApp()

# main()

class Button:

    buttons = []

    def __init__(self, cx, cy, width, height, onColor='limeGreen', 
                 offColor='red'):
        self.cx = cx
        self.cy = cy
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