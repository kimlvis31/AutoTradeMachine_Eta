#Rectangular Shape Hitbox
class hitBox_Rectangular:
    def __init__(self, xPos, yPos, width, height):
        self.xPos = xPos
        self.yPos = yPos
        self.width = width
        self.height = height

        self.deactivated = False

    def getRelPos(self, mouseX, mouseY):
        return (mouseX-self.xPos, mouseY-self.yPos)

    def isTouched(self, mouseX, mouseY):
        if ((self.deactivated == False) and (self.xPos <= mouseX) and (mouseX <= self.xPos + self.width) and (self.yPos <= mouseY) and (mouseY <= self.yPos + self.height)): return True
        else:                                                                                                                                                                return False

    def reposition(self, xPos = None, yPos = None):
        if (xPos != None): self.xPos = xPos
        if (yPos != None): self.yPos = yPos

    def resize(self, width = None, height = None):
        if (width  != None): self.width = width
        if (height != None): self.height = height

    def activate(self):   self.deactivated = False
    def deactivate(self): self.deactivated = True