from GUI import atmEta_gui_TextControl, atmEta_gui_HitBoxes, atmEta_gui_AdvancedPygletGroups, atmEta_gui_ChartDrawer

import termcolor
import time
import pyglet
import pprint

#GUIO - 'guiPage' ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class guiPage:
    def __init__(self, windowInstance, systemFunctions, displaySpaceDefiner, guioConfig, imageManager, audioManager, visualManager, pageName, ipcA, path_project):
        #Page Management
        self.windowInstance = windowInstance
        self.displaySpaceDefiner = displaySpaceDefiner
        self.guioConfig = guioConfig
        self.pageName = pageName
        self.imageManager = imageManager
        self.audioManager = audioManager
        self.visualManager = visualManager
        self.ipcA = ipcA
        self.path_project = path_project

        #GUIO Control
        self.batch = pyglet.graphics.Batch()
        self.groups = dict()
        self.GUIOs = dict()
        self.selectedGUIO = None
        self.hoveredGUIO = None
        self.backgroundShape = None
        self.lastMouseInput = None
        self.lastKeyInput   = None

        #Process Control
        self.sysFunctions = systemFunctions
        self.pageAuxillaryFunctions = dict()
        self.pageObjectFunctinos    = dict()
        self.pageLoadFunction    = None
        self.pageEscapeFunction  = None
        self.pageProcessFunction = None
        self.puVar = dict()

    def process(self, t_elapsed_ns):
        for guioName in self.GUIOs.keys(): self.GUIOs[guioName].process(t_elapsed_ns)
        if (self.pageProcessFunction != None): self.pageProcessFunction(self, t_elapsed_ns, onLoad = False)

    def handleMouseEvent(self, event):
        """
        This are the messages that can be seen by GUIOs
        [0]: HOVERENTERED
        [1]: HOVERESCAPED
        [2]: DHOVERENTERED
        [3]: DHOVERESCAPED
        [4]: {'eType': MOVED,    'x': x, 'y': y, 'dx': dx, 'dy': dy}
        [5]: {'eType': PRESSED,  'x': x, 'y': y, 'button': button, 'modifiers': modifiers}
        [6]: {'eType': RELEASED, 'x': x, 'y': y, 'button': button, 'modifiers': modifiers}
        [7]: {'eType': DRAGGED,  'x': x, 'y': y, 'dx': dx, 'dy': dy, 'modifiers': modifiers}
        [8]: {'eType': SCROLLED, 'x': x, 'y': y, 'scroll_x': scroll_x, 'scroll_y': scroll_y}
        """
        if (event['eType'] == "MOVED"): #x, y, dx, dy
            newHovered = self.__findGUIOAtPosition(event['x'], event['y'])
            if (newHovered == self.hoveredGUIO): 
                if (self.hoveredGUIO != None): self.GUIOs[self.hoveredGUIO].handleMouseEvent(event)
            else:
                if (newHovered != None):       self.GUIOs[newHovered].handleMouseEvent({'eType': "HOVERENTERED", 'x': event['x'], 'y': event['y']})
                if (self.hoveredGUIO != None): self.GUIOs[self.hoveredGUIO].handleMouseEvent({'eType': "HOVERESCAPED", 'x': event['x'], 'y': event['y']}) 
                self.hoveredGUIO = newHovered
        elif (event['eType'] == "PRESSED"): #x, y, button, modifiers
            if (self.hoveredGUIO != self.selectedGUIO):
                if (self.selectedGUIO != None): self.GUIOs[self.selectedGUIO].handleMouseEvent({'eType': "SELECTIONESCAPED", 'x': event['x'], 'y': event['y'], 'button': event['button'], 'modifiers': event['modifiers']})
                self.selectedGUIO = self.hoveredGUIO
            if (self.hoveredGUIO != None): self.GUIOs[self.hoveredGUIO].handleMouseEvent(event)
        elif (event['eType'] == "RELEASED"): #x, y, button, modifiers
            if (self.selectedGUIO != None): self.GUIOs[self.selectedGUIO].handleMouseEvent(event)
            if (self.hoveredGUIO != self.selectedGUIO): #If mouse was released after a 'drag', find the object at the mouse release location and send 'HOVERENTERED' and 'HOVERESCAPED' signal to the corresponding objects
                if (self.hoveredGUIO != None):  self.GUIOs[self.hoveredGUIO].handleMouseEvent({'eType': "HOVERENTERED", 'x': event['x'], 'y': event['y']})
                if (self.selectedGUIO != None): self.GUIOs[self.selectedGUIO].handleMouseEvent({'eType': "HOVERESCAPED", 'x': event['x'], 'y': event['y']})
                
        elif (event['eType'] == "DRAGGED"): #x, y, dx, dy, button, modifiers
            newHovered = self.__findGUIOAtPosition(event['x'], event['y'])
            if (self.selectedGUIO != None): self.GUIOs[self.selectedGUIO].handleMouseEvent(event)
            if (newHovered != self.hoveredGUIO):
                if (newHovered != None):       self.GUIOs[newHovered].handleMouseEvent({'eType': "DHOVERENTERED", 'x': event['x'], 'y': event['y'], 'selectedGUIO': self.selectedGUIO})   #To newly hovered object
                if (self.hoveredGUIO != None): self.GUIOs[self.hoveredGUIO].handleMouseEvent({'eType': "DHOVERESCAPED", 'x': event['x'], 'y': event['y']})                                #To previously hovered object
                self.hoveredGUIO = newHovered
            
        elif (event['eType'] == "SCROLLED"): #x, y, scroll_x, scroll_y
            if (self.hoveredGUIO != None): self.GUIOs[self.hoveredGUIO].handleMouseEvent(event)
        self.lastMouseInput = event
        self.visualManager.setLastMouseEvent(event)

    def handleKeyEvent(self, event):
        if ((event['eType'] == 'PRESSED') and (event['symbol'] == 65307)): #ESC
            if (self.selectedGUIO != None): self.GUIOs[self.selectedGUIO].handleKeyEvent({'eType': "SELECTIONESCAPED", 'symbol': event['symbol'], 'modifiers': event['modifiers']}); self.selectedGUIO = None
        else:
            if (self.selectedGUIO != None): self.GUIOs[self.selectedGUIO].handleKeyEvent(event)
        self.lastKeyInput = event

    def draw(self): self.batch.draw()

    def on_PageLoad(self):
        self.lastMouseInput = {'eType': "MOVED", 'x': 0, 'y': 0}
        if (self.selectedGUIO != None): 
            self.GUIOs[self.selectedGUIO].handleMouseEvent({'eType': "HOVERESCAPED", 'x': self.lastMouseInput['x'], 'y': self.lastMouseInput['y']})
            self.GUIOs[self.selectedGUIO].handleMouseEvent({'eType': "SELECTIONESCAPED", 'x': self.lastMouseInput['x'], 'y': self.lastMouseInput['y']})
            self.selectedGUIO = None
        if (self.pageLoadFunction != None): self.pageLoadFunction(self)

    def on_PageEscape(self):
        if (self.pageEscapeFunction != None): self.pageEscapeFunction(self)

    def on_GUIThemeUpdate(self):
        self.backgroundShape.color = self.visualManager.getFromColorTable('PAGEBACKGROUND')
        for guioName in self.GUIOs:
            objectType = type(self.GUIOs[guioName])
            if ((objectType == atmEta_gui_TextControl.textObject_SL) or (objectType == atmEta_gui_TextControl.textObject_SL_I) or (objectType == atmEta_gui_TextControl.textObject_SL_IE)): self.GUIOs[guioName].on_GUIThemeUpdate(newDefaultTextStyle = self.visualManager.getTextStyle('textInputBox_default')['DEFAULT'])
            else:                                                                                                                                                                           self.GUIOs[guioName].on_GUIThemeUpdate()
        
    def on_LanguageUpdate(self):
        for guioName in self.GUIOs: self.GUIOs[guioName].on_LanguageUpdate(newLanguageFont = self.visualManager.getLanguageFont())

    def __findGUIOAtPosition(self, mouseX, mouseY):
        touchedObjects = [_objectName for _objectName in self.GUIOs if ((self.GUIOs[_objectName].isHidden() == False) and (self.GUIOs[_objectName].isTouched(mouseX, mouseY) == True))]
        lastTarget = None
        for objectName in touchedObjects:
            if (lastTarget == None):                                                      lastTarget = objectName
            elif (self.GUIOs[lastTarget].groupOrder < self.GUIOs[objectName].groupOrder): lastTarget = objectName
        return lastTarget
#GUIO - 'guiPage' END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




    
#GUIO - 'passiveGraphics_typeA' -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class passiveGraphics_typeA:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']

        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)

        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']

        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.style = kwargs.get('style', 'styleA')
        
        self.images = {'DEFAULT': self.imageManager.getImageByCode("passiveGraphics_typeA_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler)}

        self.graphicsSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT'][0], batch = self.batch, group = self.group_0)

        self.status = 'DEFAULT'
        self.hidden = False

    def process(self, t_elapsed_ns): pass
    def handleMouseEvent(self, event): pass
    def handleKeyEvent(self, event): pass

    def show(self):
        self.hidden = False
        self.graphicsSprite.visible = True

    def hide(self):
        self.hidden = True
        self.graphicsSprite.visible = False

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y;
        self.graphicsSprite.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.graphicsSprite.z)

    def resize(self, width, height):
        self.width = width; self.height = height
        self.images['DEFAULT'] = self.imageManager.getImageByCode("passiveGraphics_typeA_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler)
        self.graphicsSprite.image = self.images['DEFAULT'][0]
        self.graphicsSprite.width = self.width*self.scaler; self.graphicsSprite.height = self.height*self.scaler

    def setName(self, name): self.name = name
    def getName(self): return self.name
    def isTouched(self, mouseX, mouseY): return False
    def isHidden(self): return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        self.images['DEFAULT'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT'][1])
        self.graphicsSprite.image = self.images['DEFAULT'][0]
    def on_LanguageUpdate(self, newLanguageFont): pass

    def getGroupRequirement(): return 0
#GUIO - 'passiveGraphics_typeA' END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------




    
#GUIO - 'passiveGraphics_wrapperTypeA' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class passiveGraphics_wrapperTypeA:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)

        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.style = kwargs.get('style', 'styleA')
        self.text = kwargs.get('text', None); 
        self.fontSize = int(kwargs.get('fontSize', 100)*self.scaler)
        self.textStyle = kwargs.get('textStyle', 'default')
        self.effectiveTextStyle = self.visualManager.getTextStyle('wrapperBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
       
        #Wrapper Graphics
        self.outlineWidth = kwargs.get('outlineWidth', 3)
        self.cornerRadius = kwargs.get('cornerRadius', 20)
        
        self.textElement = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_1, 
                                                                  text = self.visualManager.extractText(self.text), defaultTextStyle = self.effectiveTextStyle['DEFAULT'],
                                                                  xPos = self.xPos, yPos = self.yPos, width = self.width, height = self.height, showElementBox = False, anchor = 'N')

        self.images = {'DEFAULT': self.imageManager.getImageByCode("passiveGraphics_wrapperTypeA_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler, 
                                                                   objectSpecificCode = "{:d}_{:d}_{:d}_{:d}".format(self.outlineWidth, self.cornerRadius, int(self.textElement.getContentWidth()+10), round(self.textElement.getContentHeight()/2)))}
        self.graphicsSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT'][0], batch = self.batch, group = self.group_0)

        self.hidden = False

    def process(self, t_elapsed_ns): pass
    def handleMouseEvent(self, event): pass
    def handleKeyEvent(self, event): pass

    def show(self):
        self.hidden = False
        self.textElement.show()
        self.graphicsSprite.visible = True

    def hide(self):
        self.hidden = True
        self.textElement.hide()
        self.graphicsSprite.visible = False

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y;
        self.textElement.moveTo(x = self.xPos, y = self.yPos)
        self.graphicsSprite.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.graphicsSprite.z)

    def resize(self, width, height):
        self.width = width; self.height = height
        self.textElement.changeSize(width = self.width, height = self.height)
        self.images['DEFAULT'] = self.imageManager.getImageByCode("passiveGraphics_wrapperTypeA_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler, 
                                                                   objectSpecificCode = "{:d}_{:d}_{:d}_{:d}".format(self.outlineWidth, self.cornerRadius, int(self.textElement.getContentWidth()+10), round(self.textElement.getContentHeight()/2)))
        self.graphicsSprite.image = self.images['DEFAULT'][0]
        
    def setName(self, name): self.name = name
    def getName(self): return self.name
    def isTouched(self, mouseX, mouseY): return False
    def isHidden(self): return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        #Get the updated image and textStyle from the managers
        self.images['DEFAULT'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT'][1])
        self.effectiveTextStyle = self.visualManager.getTextStyle('wrapperBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        #Apply the updated image and textStyle
        self.graphicsSprite.image = self.images['DEFAULT'][0]
        self.textElement.on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['DEFAULT'])
    def on_LanguageUpdate(self, **kwargs):
        self.effectiveTextStyle = self.visualManager.getTextStyle('wrapperBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        previousText = self.textElement.text; newText = self.visualManager.extractText(self.text)
        if (previousText == newText): self.textElement.on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'])
        else:                         self.textElement.on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'], newLanguageText = newText)
        self.images['DEFAULT'] = self.imageManager.getImageByCode("passiveGraphics_wrapperTypeA_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler, 
                                                                objectSpecificCode = "{:d}_{:d}_{:d}_{:d}".format(self.outlineWidth, self.cornerRadius, int(self.textElement.getContentWidth()+10), round(self.textElement.getContentHeight()/2)),
                                                                reloadIndex = self.images['DEFAULT'][1])
        self.graphicsSprite.image = self.images['DEFAULT'][0]
        
    def getGroupRequirement(): return 1
#GUIO - 'passiveGraphics_wrapperTypeA' END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'passiveGraphics_wrapperTypeB' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class passiveGraphics_wrapperTypeB:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)

        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.style = kwargs.get('style', 'styleA')
        self.text = kwargs.get('text', None); 
        self.fontSize = int(kwargs.get('fontSize', 100)*self.scaler)
        self.textStyle = kwargs.get('textStyle', 'default')
        self.effectiveTextStyle = self.visualManager.getTextStyle('wrapperBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize

        #Text Control
        self.textElement = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_1,
                                                                  text = self.visualManager.extractText(self.text), defaultTextStyle = self.effectiveTextStyle['DEFAULT'],
                                                                  xPos = self.xPos, yPos = self.yPos, width = self.width, height = self.height, showElementBox = False, anchor = 'CENTER')
        #Wrapper Graphics
        self.outlineWidth = kwargs.get('outlineWidth', 3)
        self.images = {'DEFAULT': self.imageManager.getImageByCode("passiveGraphics_wrapperTypeB_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}_{:d}".format(self.outlineWidth, int(self.textElement.getContentWidth()+10)))}
        self.graphicsSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT'][0], batch = self.batch, group = self.group_0)

        self.hidden = False

    def process(self, t_elapsed_ns): pass
    def handleMouseEvent(self, event): pass
    def handleKeyEvent(self, event): pass

    def show(self):
        self.hidden = False
        self.textElement.show()
        self.graphicsSprite.visible = True

    def hide(self):
        self.hidden = True
        self.textElement.hide()
        self.graphicsSprite.visible = False

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y;
        self.textElement.moveTo(x = self.xPos, y = self.yPos)
        self.graphicsSprite.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.graphicsSprite.z)

    def resize(self, width, height):
        self.width = width; self.height = height
        self.textElement.changeSize(width = self.width, height = self.height)
        self.images['DEFAULT'] = self.imageManager.getImageByCode("passiveGraphics_wrapperTypeB_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler, 
                                                                   objectSpecificCode = "{:d}_{:d}".format(self.outlineWidth, int(self.textElement.getContentWidth()+10)))
        self.graphicsSprite.image = self.images['DEFAULT'][0]
        
    def setName(self, name): self.name = name
    def getName(self): return self.name
    def isTouched(self, mouseX, mouseY): return False
    def isHidden(self): return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        #Get the updated image and textStyle from the managers
        self.images['DEFAULT'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT'][1])
        self.effectiveTextStyle = self.visualManager.getTextStyle('wrapperBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        #Apply the updated image and textStyle
        self.graphicsSprite.image = self.images['DEFAULT'][0]
        self.textElement.on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['DEFAULT'])
    def on_LanguageUpdate(self, **kwargs):
        self.effectiveTextStyle = self.visualManager.getTextStyle('wrapperBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        previousText = self.textElement.text; newText = self.visualManager.extractText(self.text)
        if (previousText == newText): self.textElement.on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'])
        else:                         self.textElement.on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'], newLanguageText = newText)
        self.images['DEFAULT'] = self.imageManager.getImageByCode("passiveGraphics_wrapperTypeB_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler, 
                                                                objectSpecificCode = "{:d}_{:d}".format(self.outlineWidth, int(self.textElement.getContentWidth()+10)),
                                                                reloadIndex = self.images['DEFAULT'][1])
        self.graphicsSprite.image = self.images['DEFAULT'][0]
        
    def getGroupRequirement(): return 1
#GUIO - 'passiveGraphics_wrapperTypeB' END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'passiveGraphics_wrapperTypeC' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class passiveGraphics_wrapperTypeC:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)

        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.style = kwargs.get('style', 'styleA')
        self.text = kwargs.get('text', None); 
        self.fontSize = int(kwargs.get('fontSize', 100)*self.scaler)
        self.textStyle = kwargs.get('textStyle', 'default')
        self.effectiveTextStyle = self.visualManager.getTextStyle('wrapperBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize

        #Text Control
        self.textElement = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_1,
                                                                  text = self.visualManager.extractText(self.text), defaultTextStyle = self.effectiveTextStyle['DEFAULT'],
                                                                  xPos = self.xPos, yPos = self.yPos, width = self.width, height = self.height, showElementBox = False, anchor = 'W')
        #Wrapper Graphics
        self.outlineWidth = kwargs.get('outlineWidth', 3)

        self.images = {'DEFAULT': self.imageManager.getImageByCode("passiveGraphics_wrapperTypeC_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler, 
                                                                   objectSpecificCode = "{:d}_{:d}".format(self.outlineWidth, int(self.textElement.getContentWidth()+10)))}
        self.graphicsSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT'][0], batch = self.batch, group = self.group_0)

        self.hidden = False

    def process(self, t_elapsed_ns): pass
    def handleMouseEvent(self, event): pass
    def handleKeyEvent(self, event): pass

    def show(self):
        self.hidden = False
        self.textElement.show()
        self.graphicsSprite.visible = True

    def hide(self):
        self.hidden = True
        self.textElement.hide()
        self.graphicsSprite.visible = False

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y;
        self.textElement.moveTo(x = self.xPos, y = self.yPos)
        self.graphicsSprite.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.graphicsSprite.z)

    def resize(self, width, height):
        self.width = width; self.height = height
        self.textElement.changeSize(width = self.width, height = self.height)
        self.images['DEFAULT'] = self.imageManager.getImageByCode("passiveGraphics_wrapperTypeC_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}_{:d}".format(self.outlineWidth, int(self.textElement.getContentWidth()+10)))
        self.graphicsSprite.image = self.images['DEFAULT'][0]
        
    def setName(self, name): self.name = name
    def getName(self): return self.name
    def isTouched(self, mouseX, mouseY): return False
    def isHidden(self): return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        #Get the updated image and textStyle from the managers
        self.images['DEFAULT'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT'][1])
        self.effectiveTextStyle = self.visualManager.getTextStyle('wrapperBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        #Apply the updated image and textStyle
        self.graphicsSprite.image = self.images['DEFAULT'][0]
        self.textElement.on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['DEFAULT'])
    def on_LanguageUpdate(self, **kwargs):
        self.effectiveTextStyle = self.visualManager.getTextStyle('wrapperBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        previousText = self.textElement.text; newText = self.visualManager.extractText(self.text)
        if (previousText == newText): self.textElement.on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'])
        else:                         self.textElement.on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'], newLanguageText = newText)
        self.images['DEFAULT'] = self.imageManager.getImageByCode("passiveGraphics_wrapperTypeC_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler, 
                                                                  objectSpecificCode = "{:d}_{:d}".format(self.outlineWidth, int(self.textElement.getContentWidth()+10)),
                                                                  reloadIndex = self.images['DEFAULT'][1])
        self.graphicsSprite.image = self.images['DEFAULT'][0]
        
    def getGroupRequirement(): return 1
#GUIO - 'passiveGraphics_wrapperTypeC' END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'textBox_typeA' ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class textBox_typeA:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)

        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.align = kwargs.get('horizontal', 0);
        self.style = kwargs.get('style', None)

        self.text = kwargs.get('text', None)
        self.fontSize = int(kwargs.get('fontSize', 100)*self.scaler)
        self.textStyle = kwargs.get('textStyle', 'default')
        self.effectiveTextStyle = self.visualManager.getTextStyle('textBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        self.textAnchor = kwargs.get('anchor', 'CENTER')

        #Functional Object Parameters
        if (self.style != None):
            self.images = {'DEFAULT': self.imageManager.getImageByCode("textBox_typeA_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler)}
            self.textBoxSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT'][0], batch = self.batch, group = self.group_0)
            
        #Text Control
        self.textElement = atmEta_gui_TextControl.textObject_SL_I(scaler = self.scaler, batch = self.batch, group = self.group_1, 
                                                                  text = self.visualManager.extractText(self.text), defaultTextStyle = self.effectiveTextStyle['DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                  xPos = self.xPos, yPos = self.yPos, width = self.width, height = self.height, showElementBox = False, anchor = self.textAnchor)
        
        self.textInteractable = kwargs.get('textInteractable', True)
        self.hidden = False

    def process(self, t_elapsed_ns): pass

    def handleMouseEvent(self, event):
        if (self.textInteractable == True): self.textElement.handleMouseEvent(event)

    def handleKeyEvent(self, event):
        if (self.textInteractable == True): self.textElement.handleKeyEvent(event)

    def show(self):
        self.hidden = False
        if (self.style != None): self.textBoxSprite.visible = True
        self.textElement.show()

    def hide(self):
        self.hidden = True
        if (self.style != None): self.textBoxSprite.visible = False
        self.textElement.hide()

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y;
        self.textElement.moveTo(x = self.xPos, y = self.yPos)
        if (self.style != None): self.textBoxSprite.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.textBoxSprite.z)

    def resize(self, width, height):
        self.width = width; self.height = height
        self.textElement.changeSize(width = self.width, height = self.height)
        if (self.style != None):
            self.images['DEFAULT'] = self.imageManager.getImageByCode("textBox_typeA_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler)
            self.textBoxSprite.image = self.images['DEFAULT'][0]
        
    def setName(self, name): self.name = name
    def getName(self): return self.name
    def isTouched(self, mouseX, mouseY): return self.textElement.isTouched(mouseX, mouseY)
    def isHidden(self): return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        #Get the updated image and textStyle from the managers
        if (self.style != None): self.images['DEFAULT'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT'][1])
        self.effectiveTextStyle = self.visualManager.getTextStyle('textBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        #Apply the updated image and textStyle
        if (self.style != None): self.textBoxSprite.image = self.images['DEFAULT'][0]
        self.textElement.on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle)
    def on_LanguageUpdate(self, **kwargs):
        self.effectiveTextStyle = self.visualManager.getTextStyle('textBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        previousText = self.textElement.getText(); newText = self.visualManager.extractText(self.text)
        if (previousText == newText): self.textElement.on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'])
        else:                         self.textElement.on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'], newLanguageText = newText)

    def updateText(self, text, textStyle = 'DEFAULT'):
        self.text = text
        self.textElement.setText(self.visualManager.extractText(self.text), textStyle)
        
    def getGroupRequirement(): return 1
#GUIO - 'textBox_typeA' END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'imageBox_typeA' --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class imageBox_typeA:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)

        self.imageManager  = kwargs['imageManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.style = kwargs.get('style', None); self.imageName = kwargs.get('image', None)
        
        self.images = {'#dti#': self.imageManager.getImage('#dti#.png')}
        if (self.style != None):
            self.images['DEFAULT'] = self.imageManager.getImageByCode("imageBox_typeA_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler)
            self.frameSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT'][0], batch = self.batch, group = self.group_0)

        if (self.imageName == None): 
            self.displayImage = None
            self.imageSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['#dti#'], batch = self.batch, group = self.group_1)
        else:                        
            if (self.style == None):
                self.displayImage = self.imageManager.getImage(self.imageName, (round(self.width*self.scaler), round(self.height*self.scaler)))
                self.imageSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.displayImage, batch = self.batch, group = self.group_1)
            else:
                self.displayImage = self.imageManager.getImage(self.imageName, (round(self.width*self.scaler-6), round(self.height*self.scaler-6)))
                self.imageSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler + 3, y = self.yPos * self.scaler + 3, img = self.displayImage, batch = self.batch, group = self.group_1)

        self.appliedImageRGBA = [self.imageSprite.color[0], self.imageSprite.color[1], self.imageSprite.color[2], self.imageSprite.opacity]

        self.hidden = False

    def process(self, t_elapsed_ns): pass
    def handleMouseEvent(self, event): pass
    def handleKeyEvent(self, event): pass

    def show(self):
        self.hidden = False
        self.imageSprite.visible = True
        if (self.style != None): self.frameSprite.visible = True

    def hide(self):
        self.hidden = True
        self.imageSprite.visible = False
        if (self.style != None): self.frameSprite.visible = False

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y;
        self.frameSprite.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.frameSprite.z)
        if (self.style == None): self.imageSprite.position = (self.xPos*self.scaler,   self.yPos*self.scaler,   self.imageSprite.z)
        else:                    self.imageSprite.position = (self.xPos*self.scaler+3, self.yPos*self.scaler+3, self.imageSprite.z)

    def resize(self, width, height):
        self.width = width; self.height = height
        if (self.style == None): self.displayImage = self.imageManager.getImage(self.imageName, (round(self.width*self.scaler),   round(self.height*self.scaler)))
        else:                    self.displayImage = self.imageManager.getImage(self.imageName, (round(self.width*self.scaler-6), round(self.height*self.scaler-6)))
        self.imageSprite.image = self.displayImage
        if (self.style != None):
            self.images['DEFAULT'] = self.imageManager.getImageByCode("imageBox_typeA_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler)
            self.frameSprite.image = self.images['DEFAULT'][0]

    def updateImage(self, image):
        self.imageName = image
        if (self.style == None): self.displayImage = self.imageManager.getImage(self.imageName, (round(self.width*self.scaler),   round(self.height*self.scaler)))
        else:                    self.displayImage = self.imageManager.getImage(self.imageName, (round(self.width*self.scaler-6), round(self.height*self.scaler-6)))
        self.imageSprite.image = self.displayImage
        self.imageSprite.color   = (self.appliedImageRGBA[0], self.appliedImageRGBA[1], self.appliedImageRGBA[2])
        self.imageSprite.opacity = self.appliedImageRGBA[3]

    def editImageRGBA(self, rgba):
        self.imageSprite.color = (rgba[0], rgba[1], rgba[2]); self.imageSprite.opacity = rgba[3]
        self.appliedImageRGBA = [self.imageSprite.color[0], self.imageSprite.color[1], self.imageSprite.color[2], self.imageSprite.opacity]
        
    def setName(self, name): self.name = name
    def getName(self): return self.name
    def isTouched(self, mouseX, mouseY): return False
    def isHidden(self): return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        if (self.style != None): 
            self.images['DEFAULT'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT'][1])
            self.frameSprite.image = self.images['DEFAULT'][0]
        self.imageSprite.color = (self.appliedImageRGBA[0], self.appliedImageRGBA[1], self.appliedImageRGBA[2]); self.imageSprite.opacity = self.appliedImageRGBA[3]
    def on_LanguageUpdate(self, **kwargs): pass
        
    def getGroupRequirement(): return 1
#GUIO - 'passiveGraphics_typeA' END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'button_typeA' ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class button_typeA:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.group_2 = kwargs['group_2']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)
            self.group_2 = pyglet.graphics.Group(order = self.groupOrder+2)

        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.style = kwargs.get('style', 'styleA')
        self.text = kwargs.get('text', "")
        self.fontSize = int(kwargs.get('fontSize', 100)*self.scaler)
        self.textStyle = kwargs.get('textStyle', 'default')
        self.effectiveTextStyle = self.visualManager.getTextStyle('button_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        self.hitBox = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos, self.width, self.height)

        #Functional Object Parameters
        self.hoverFunction       = kwargs.get('hoverFunction',       None)
        self.hoverEscapeFunction = kwargs.get('hoverEscapeFunction', None)
        self.pressFunction       = kwargs.get('pressFunction',       None)
        self.releaseFunction     = kwargs.get('releaseFunction',     None)
        
        self.images = {'DEFAULT':  self.imageManager.getImageByCode("button_typeA_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler),
                       'HOVERED':  self.imageManager.getImageByCode("button_typeA_"+self.style+"_HOVERED", self.width*self.scaler, self.height*self.scaler),
                       'PRESSED':  self.imageManager.getImageByCode("button_typeA_"+self.style+"_PRESSED", self.width*self.scaler, self.height*self.scaler),
                       'INACTIVEMASK': self.imageManager.getImageByCode("button_typeA_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler)}

        self.buttonSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT'][0], batch = self.batch, group = self.group_0)
        self.textElement = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_1,
                                                                  text = self.visualManager.extractText(self.text), defaultTextStyle = self.effectiveTextStyle['DEFAULT'],
                                                                  xPos = self.xPos, yPos = self.yPos, width = self.width, height = self.height, showElementBox = False, anchor = 'CENTER')
        self.textElement.addTextStyle('HOVERED',  self.effectiveTextStyle['HOVERED'])
        self.textElement.addTextStyle('PRESSED',  self.effectiveTextStyle['PRESSED'])
        self.textElement.addTextStyle('INACTIVE', self.effectiveTextStyle['INACTIVE'])
        self.inactiveMask = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['INACTIVEMASK'][0], batch = self.batch, group = self.group_2); self.inactiveMask.visible = False

        self.status = "DEFAULT"
        self.hidden = False; self.deactivated = False

    def process(self, t_elapsed_ns): pass

    def handleMouseEvent(self, event):
        if not((self.deactivated == True) or (self.hidden)):
            if (event['eType'] == "HOVERENTERED"):
                self.audioManager.playAudioByCode('button_typeA_HOVERED_A')
                self.status = "HOVERED"
                self.buttonSprite.image = self.images[self.status][0]
                self.textElement.editTextStyle('all', 'HOVERED')
                if (self.hoverFunction != None): self.hoverFunction(self)
            elif (event['eType'] == "HOVERESCAPED"):
                self.status = "DEFAULT"
                self.buttonSprite.image = self.images[self.status][0]
                self.textElement.editTextStyle('all', 'DEFAULT')
                if (self.hoverEscapeFunction != None): self.hoverEscapeFunction(self)
            elif (event['eType'] == "DHOVERESCAPED"):
                self.status = "DEFAULT"
                self.buttonSprite.image = self.images[self.status][0]
                self.textElement.editTextStyle('all', 'DEFAULT')
            elif (event['eType'] == "PRESSED"):
                self.audioManager.playAudioByCode('button_typeA_PRESSED_A')
                self.status = "PRESSED"
                self.buttonSprite.image = self.images[self.status][0]
                self.textElement.editTextStyle('all', 'PRESSED')
                if (self.pressFunction != None): self.pressFunction(self)
            elif (event['eType'] == "RELEASED"):
                if (self.status == "PRESSED"):
                    self.audioManager.playAudioByCode('button_typeA_RELEASED_A')
                    self.status = "HOVERED"
                    self.buttonSprite.image = self.images[self.status][0]
                    self.textElement.editTextStyle('all', 'HOVERED')
                    if (self.releaseFunction != None): self.releaseFunction(self)

    def handleKeyEvent(self, event): pass

    def show(self):
        self.hidden = False
        self.buttonSprite.visible = True
        if (self.deactivated == True): self.inactiveMask.visible = True
        self.textElement.show()

    def hide(self):
        self.hidden = True
        self.buttonSprite.visible = False
        self.inactiveMask.visible = False
        self.textElement.hide()

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y;
        self.buttonSprite.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.buttonSprite.z)
        self.textElement.moveTo(x = self.xPos, y = self.yPos)
        self.inactiveMask.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.inactiveMask.z)
        self.hitBox.reposition(xPos = self.xPos, yPos = self.yPos)

    def resize(self, width, height):
        self.width = width; self.height = height
        self.textElement.changeSize(width = self.width, height = self.height)
        self.images['DEFAULT'] = self.imageManager.getImageByCode("button_typeA_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler)
        self.images['HOVERED'] = self.imageManager.getImageByCode("button_typeA_"+self.style+"_HOVERED", self.width*self.scaler, self.height*self.scaler)
        self.images['PRESSED'] = self.imageManager.getImageByCode("button_typeA_"+self.style+"_PRESSED", self.width*self.scaler, self.height*self.scaler)
        self.images['INACTIVEMASK'] = self.imageManager.getImageByCode("button_typeA_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler)
        self.buttonSprite.image = self.images[self.status][0]
        self.inactiveMask.image = self.images['INACTIVEMASK'][0]
        self.hitBox.resize(width = self.width, height = self.height)

    def activate(self):
        if (self.hidden == False):
            self.inactiveMask.visible = False
            self.textElement.editTextStyle('all', self.status)
        self.deactivated = False

    def deactivate(self):
        if (self.hidden == False):
            self.inactiveMask.visible = True
            self.textElement.editTextStyle('all', 'INACTIVE')
        self.deactivated = True

    def updateText(self, text): 
        self.text = text
        self.textElement.setText(self.visualManager.extractText(self.text))
    
    def setName(self, name): self.name = name
    def getName(self): return self.name
    def isTouched(self, mouseX, mouseY): return self.hitBox.isTouched(mouseX, mouseY)
    def isHidden(self): return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        #Get the updated image and textStyle from the managers
        self.images['DEFAULT'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT'][1])
        self.images['HOVERED'] = self.imageManager.getImageByLoadIndex(self.images['HOVERED'][1])
        self.images['PRESSED'] = self.imageManager.getImageByLoadIndex(self.images['PRESSED'][1])
        self.effectiveTextStyle = self.visualManager.getTextStyle('button_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        #Apply the updated image and textStyle
        self.buttonSprite.image = self.images[self.status][0]
        self.textElement.addTextStyle('HOVERED',  self.effectiveTextStyle['HOVERED'])
        self.textElement.addTextStyle('PRESSED',  self.effectiveTextStyle['PRESSED'])
        self.textElement.addTextStyle('INACTIVE', self.effectiveTextStyle['INACTIVE'])
        self.textElement.on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['DEFAULT'])

    def on_LanguageUpdate(self, **kwargs):
        self.effectiveTextStyle = self.visualManager.getTextStyle('button_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        previousText = self.textElement.getText(); newText = self.visualManager.extractText(self.text)
        if (previousText == newText): self.textElement.on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'])
        else:                         self.textElement.on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'], newLanguageText = newText)
        
    def getGroupRequirement(): return 2
#GUIO - 'button_typeA' END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'button_typeB' ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class button_typeB:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.group_2 = kwargs['group_2']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)
            self.group_2 = pyglet.graphics.Group(order = self.groupOrder+2)

        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.style = kwargs.get('style', 'styleA')
        self.imageName = kwargs.get('image', None); self.imageSize = kwargs.get('imageSize', (0.5, 0.5)); self.imageRGBA = kwargs.get('imageRGBA', self.visualManager.getFromColorTable('ICON_COLORING'))
        self.hitBox = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos, self.width, self.height)

        #Functional Object Parameters
        self.hoverFunction       = kwargs.get('hoverFunction',       None)
        self.hoverEscapeFunction = kwargs.get('hoverEscapeFunction', None)
        self.pressFunction       = kwargs.get('pressFunction',       None)
        self.releaseFunction     = kwargs.get('releaseFunction',     None)
        
        self.images = {'DEFAULT':      self.imageManager.getImageByCode("button_typeB_"+self.style+"_DEFAULT",      self.width*self.scaler, self.height*self.scaler),
                       'HOVERED':      self.imageManager.getImageByCode("button_typeB_"+self.style+"_HOVERED",      self.width*self.scaler, self.height*self.scaler),
                       'PRESSED':      self.imageManager.getImageByCode("button_typeB_"+self.style+"_PRESSED",      self.width*self.scaler, self.height*self.scaler),
                       'INACTIVEMASK': self.imageManager.getImageByCode("button_typeB_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler)}

        self.buttonSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT'][0], batch = self.batch, group = self.group_0)
        if (self.imageName != None):
            self.displayImage = self.imageManager.getImage(self.imageName, (round(self.imageSize[0]*self.scaler), round(self.imageSize[1]*self.scaler)))
            self.imageSprite = pyglet.sprite.Sprite(x = (self.xPos+self.width/2)*self.scaler-self.displayImage.width/2, y = (self.yPos+self.height/2)*self.scaler-self.displayImage.height/2, img = self.displayImage, batch = self.batch, group = self.group_1)
            if (self.imageRGBA != None): self.imageSprite.color = (self.imageRGBA[0], self.imageRGBA[1], self.imageRGBA[2]); self.imageSprite.opacity = self.imageRGBA[3]
        self.inactiveMask = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['INACTIVEMASK'][0], batch = self.batch, group = self.group_2); self.inactiveMask.visible = False
        
        self.status = "DEFAULT"
        self.hidden = False; self.deactivated = False

    def process(self, t_elapsed_ns): pass

    def handleMouseEvent(self, event):
        if not((self.deactivated == True) or (self.hidden)):
            if (event['eType'] == "HOVERENTERED"):
                self.audioManager.playAudioByCode('button_typeB_HOVERED_A')
                self.status = "HOVERED"
                self.buttonSprite.image = self.images[self.status][0]
                if (self.hoverFunction != None): self.hoverFunction(self)
            elif (event['eType'] == "HOVERESCAPED"):
                self.status = "DEFAULT"
                self.buttonSprite.image = self.images[self.status][0]
                if (self.hoverEscapeFunction != None): self.hoverEscapeFunction(self)
            elif (event['eType'] == "DHOVERESCAPED"):
                self.status = "DEFAULT"
                self.buttonSprite.image = self.images[self.status][0]
            elif (event['eType'] == "PRESSED"):
                self.audioManager.playAudioByCode('button_typeB_PRESSED_A')
                self.status = "PRESSED"
                self.buttonSprite.image = self.images[self.status][0]
                if (self.pressFunction != None): self.pressFunction(self)
            elif (event['eType'] == "RELEASED"):
                if (self.status == "PRESSED"):
                    self.audioManager.playAudioByCode('button_typeB_RELEASED_A')
                    self.status = "HOVERED"
                    self.buttonSprite.image = self.images[self.status][0]
                    if (self.releaseFunction != None): self.releaseFunction(self)

    def handleKeyEvent(self, event): pass

    def show(self):
        self.hidden = False
        self.buttonSprite.visible = True
        self.imageSprite.visible  = True
        if (self.deactivated == True): self.inactiveMask.visible = True

    def hide(self):
        self.hidden = True
        self.buttonSprite.visible = False
        self.imageSprite.visible  = False
        self.inactiveMask.visible = False

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y;
        self.buttonSprite.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.buttonSprite.z)
        self.inactiveMask.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.inactiveMask.z)
        if (self.imageName != None): self.imageSprite.position = ((self.xPos+self.width/2)*self.scaler-self.displayImage.width/2, (self.yPos+self.height/2)*self.scaler-self.displayImage.height/2, self.imageSprite.z)
        self.hitBox.reposition(xPos = self.xPos, yPos = self.yPos)

    def resize(self, width, height, newImageSize = None):
        self.width = width; self.height = height
        if (self.imageName != None):
            if (newImageSize != None): self.imageSize = newImageSize
            self.displayImage = self.imageManager.getImage(self.imageName, (round(self.imageSize[0]*self.scaler), round(self.imageSize[1]*self.scaler)))
            self.imageSprite.image = self.displayImage
            if (self.imageRGBA != None): self.imageSprite.color = (self.imageRGBA[0], self.imageRGBA[1], self.imageRGBA[2]); self.imageSprite.opacity = self.imageRGBA[3]
            self.imageSprite.position = ((self.xPos+self.width/2)*self.scaler-self.displayImage.width/2, (self.yPos+self.height/2)*self.scaler-self.displayImage.height/2, self.imageSprite.z)
        self.images['DEFAULT'] = self.imageManager.getImageByCode("button_typeB_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler)
        self.images['HOVERED'] = self.imageManager.getImageByCode("button_typeB_"+self.style+"_HOVERED", self.width*self.scaler, self.height*self.scaler)
        self.images['PRESSED'] = self.imageManager.getImageByCode("button_typeB_"+self.style+"_PRESSED", self.width*self.scaler, self.height*self.scaler)
        self.images['INACTIVEMASK'] = self.imageManager.getImageByCode("button_typeB_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler)
        self.buttonSprite.image = self.images[self.status][0]
        self.inactiveMask.image = self.images['INACTIVEMASK'][0]
        self.hitBox.resize(width = self.width, height = self.height)

    def activate(self):
        if (self.hidden == False):
            self.inactiveMask.visible = False
        self.deactivated = False

    def deactivate(self):
        if (self.hidden == False):
            self.inactiveMask.visible = True
        self.deactivated = True
        
    def setName(self, name): self.name = name
    def getName(self): return self.name
    def isTouched(self, mouseX, mouseY): return self.hitBox.isTouched(mouseX, mouseY)
    def isHidden(self): return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        self.images['DEFAULT'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT'][1])
        self.images['HOVERED'] = self.imageManager.getImageByLoadIndex(self.images['HOVERED'][1])
        self.images['PRESSED'] = self.imageManager.getImageByLoadIndex(self.images['PRESSED'][1])
        self.imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING')
        self.buttonSprite.image = self.images[self.status][0]
        if (self.imageRGBA != None): self.imageSprite.color = (self.imageRGBA[0], self.imageRGBA[1], self.imageRGBA[2]); self.imageSprite.opacity = self.imageRGBA[3]
    def on_LanguageUpdate(self, **kwargs): pass
        
    def getGroupRequirement(): return 2
#GUIO - 'button_typeB' END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'switch_typeA' ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class switch_typeA:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.group_2 = kwargs['group_2']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)
            self.group_2 = pyglet.graphics.Group(order = self.groupOrder+2)

        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.style = kwargs.get('style', 'styleA')
        self.hitBox = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos, self.width, self.height)

        #Functional Object Parameters
        self.hoverFunction        = kwargs.get('hoverFunction',       None)
        self.hoverEscapeFunction  = kwargs.get('hoverEscapeFunction', None)
        self.pressFunction        = kwargs.get('pressFunction',       None)
        self.releaseFunction      = kwargs.get('releaseFunction',     None)
        self.statusUpdateFunction = kwargs.get('statusUpdateFunction', None)
        
        self.switchStatus = kwargs.get('switchStatus', False)

        self.images = {'DEFAULT_FRAME':  self.imageManager.getImageByCode("switch_typeA_"+self.style+"_F_DEFAULT", self.width*self.scaler, self.height*self.scaler),
                       'HOVERED_FRAME':  self.imageManager.getImageByCode("switch_typeA_"+self.style+"_F_HOVERED", self.width*self.scaler, self.height*self.scaler),
                       'PRESSED_FRAME':  self.imageManager.getImageByCode("switch_typeA_"+self.style+"_F_PRESSED", self.width*self.scaler, self.height*self.scaler),
                       'DEFAULT_BUTTON': self.imageManager.getImageByCode("switch_typeA_"+self.style+"_B_DEFAULT", self.width*self.scaler, self.height*self.scaler),
                       'HOVERED_BUTTON': self.imageManager.getImageByCode("switch_typeA_"+self.style+"_B_HOVERED", self.width*self.scaler, self.height*self.scaler),
                       'PRESSED_BUTTON': self.imageManager.getImageByCode("switch_typeA_"+self.style+"_B_PRESSED", self.width*self.scaler, self.height*self.scaler),
                       'INACTIVEMASK': self.imageManager.getImageByCode("switch_typeA_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler)}
        
        self.frameSprite  = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT_FRAME'][0], batch = self.batch, group = self.group_0)
        self.buttonSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT_BUTTON'][0], batch = self.batch, group = self.group_1)
        if (self.switchStatus == True): self.buttonSprite.visible = True
        else:                           self.buttonSprite.visible = False
        self.inactiveMask = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['INACTIVEMASK'][0], batch = self.batch, group = self.group_2); self.inactiveMask.visible = False
        
        self.status = 'DEFAULT'
        self.hidden = False; self.deactivated = False
        self.setStatus(self.switchStatus, callStatusUpdateFunction = False)

    def process(self, t_elapsed_ns): pass

    def handleMouseEvent(self, event):
        if not((self.deactivated == True) or (self.hidden)):
            if (event['eType'] == "HOVERENTERED"):
                self.audioManager.playAudioByCode('switch_typeA_HOVERED_A')
                self.status = "HOVERED"
                self.frameSprite.image = self.images['HOVERED_FRAME'][0]
                if (self.switchStatus == True): self.buttonSprite.image = self.images['HOVERED_BUTTON'][0]
                if (self.hoverFunction != None): self.hoverFunction(self)
            elif (event['eType'] == "HOVERESCAPED"):
                self.status = "DEFAULT"
                self.frameSprite.image = self.images['DEFAULT_FRAME'][0]
                if (self.switchStatus == True): self.buttonSprite.image = self.images['DEFAULT_BUTTON'][0]
            elif (event['eType'] == "DHOVERESCAPED"):
                self.status = "DEFAULT"
                self.frameSprite.image = self.images['DEFAULT_FRAME'][0]
                if (self.switchStatus == True): self.buttonSprite.image = self.images['DEFAULT_BUTTON'][0]
            elif (event['eType'] == "PRESSED"):
                self.audioManager.playAudioByCode('switch_typeA_PRESSED_A')
                self.status = "PRESSED"
                self.frameSprite.image = self.images['PRESSED_FRAME'][0]
                if (self.switchStatus == True): self.buttonSprite.image = self.images['PRESSED_BUTTON'][0]
                if (self.pressFunction != None): self.pressFunction(self)
            elif (event['eType'] == "RELEASED"):
                if (self.status == "PRESSED"):
                    self.switchStatus = not(self.switchStatus)
                    self.audioManager.playAudioByCode('switch_typeA_RELEASED_A')
                    self.status = "HOVERED"
                    self.frameSprite.image = self.images['HOVERED_FRAME'][0]
                    if (self.switchStatus == True): self.buttonSprite.visible = True; self.buttonSprite.image = self.images['HOVERED_BUTTON'][0]
                    else:                           self.buttonSprite.visible = False
                    if (self.releaseFunction      != None): self.releaseFunction(self)
                    if (self.statusUpdateFunction != None): self.statusUpdateFunction(self)

    def handleKeyEvent(self, event): pass

    def show(self):
        self.hidden = False
        self.frameSprite.visible = True
        if (self.switchStatus == True): self.buttonSprite.visible = True
        if (self.deactivated == True): self.inactiveMask.visible = True

    def hide(self):
        self.hidden = True
        self.frameSprite.visible = False
        self.buttonSprite.visible = False
        self.inactiveMask.visible = False

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y;
        self.frameSprite.position  = (self.xPos*self.scaler, self.yPos*self.scaler, self.frameSprite.z)
        self.buttonSprite.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.buttonSprite.z)
        self.inactiveMask.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.inactiveMask.z)
        self.hitBox.reposition(xPos = self.xPos, yPos = self.yPos)

    def resize(self, width, height):
        self.width = width; self.height = height
        self.images['DEFAULT_FRAME']  = self.imageManager.getImageByCode("switch_typeA_"+self.style+"_F_DEFAULT",    self.width*self.scaler, self.height*self.scaler)
        self.images['HOVERED_FRAME']  = self.imageManager.getImageByCode("switch_typeA_"+self.style+"_F_HOVERED",    self.width*self.scaler, self.height*self.scaler)
        self.images['PRESSED_FRAME']  = self.imageManager.getImageByCode("switch_typeA_"+self.style+"_F_PRESSED",    self.width*self.scaler, self.height*self.scaler)
        self.images['DEFAULT_BUTTON'] = self.imageManager.getImageByCode("switch_typeA_"+self.style+"_B_DEFAULT",    self.width*self.scaler, self.height*self.scaler)
        self.images['HOVERED_BUTTON'] = self.imageManager.getImageByCode("switch_typeA_"+self.style+"_B_HOVERED",    self.width*self.scaler, self.height*self.scaler)
        self.images['PRESSED_BUTTON'] = self.imageManager.getImageByCode("switch_typeA_"+self.style+"_B_PRESSED",    self.width*self.scaler, self.height*self.scaler)
        self.images['INACTIVEMASK']   = self.imageManager.getImageByCode("switch_typeA_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler)
        self.frameSprite.image  = self.images[self.status+'_FRAME'][0]
        self.buttonSprite.image = self.images[self.status+'_BUTTON'][0]
        self.inactiveMask.image = self.images['INACTIVEMASK'][0]
        self.hitBox.resize(width = self.width, height = self.height)
        
    def activate(self):
        self.deactivated = False
        self.inactiveMask.visible = False

    def deactivate(self):
        self.deactivated = True
        if (self.hidden == False): self.inactiveMask.visible = True
        
    def setName(self, name): self.name = name
    def getName(self): return self.name
    def isTouched(self, mouseX, mouseY): return self.hitBox.isTouched(mouseX, mouseY)
    def isHidden(self): return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        self.images['DEFAULT_FRAME'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT_FRAME'][1])
        self.images['HOVERED_FRAME'] = self.imageManager.getImageByLoadIndex(self.images['HOVERED_FRAME'][1])
        self.images['PRESSED_FRAME'] = self.imageManager.getImageByLoadIndex(self.images['PRESSED_FRAME'][1])
        self.images['DEFAULT_BUTTON'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT_BUTTON'][1])
        self.images['HOVERED_BUTTON'] = self.imageManager.getImageByLoadIndex(self.images['HOVERED_BUTTON'][1])
        self.images['PRESSED_BUTTON'] = self.imageManager.getImageByLoadIndex(self.images['PRESSED_BUTTON'][1])
        self.frameSprite.image  = self.images[self.status+"_FRAME"][0]
        self.buttonSprite.image = self.images[self.status+"_BUTTON"][0]
    def on_LanguageUpdate(self, **kwargs): pass

    def getStatus(self): return self.switchStatus

    def setStatus(self, status, callStatusUpdateFunction = True):
        if (status != self.switchStatus):
            self.switchStatus = status
            self.frameSprite.image = self.images[self.status+'_FRAME'][0]
            if (self.switchStatus == True): self.buttonSprite.visible = True; self.buttonSprite.image = self.images[self.status+'_BUTTON'][0]
            else:                           self.buttonSprite.visible = False
            if ((callStatusUpdateFunction == True) and (self.statusUpdateFunction != None)): self.statusUpdateFunction(self)
        
    def getGroupRequirement(): return 2
#GUIO - 'switch_typeA' END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'switch_typeB' ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class switch_typeB:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.group_2 = kwargs['group_2']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)
            self.group_2 = pyglet.graphics.Group(order = self.groupOrder+2)

        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        if (self.width < self.height * 2): self.width = int(self.height * 2)
        self.align = kwargs.get('align', 'horizontal')
        self.style = kwargs.get('style', 'styleA')
        if (self.align == 'horizontal'): self.hitBox = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos, self.width, self.height)
        elif (self.align == 'vertical'): self.hitBox = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos, self.height, self.width)

        #Functional Object Parameters
        self.hoverFunction        = kwargs.get('hoverFunction',       None)
        self.hoverEscapeFunction  = kwargs.get('hoverEscapeFunction', None)
        self.pressFunction        = kwargs.get('pressFunction',       None)
        self.releaseFunction      = kwargs.get('releaseFunction',     None)
        self.statusUpdateFunction = kwargs.get('statusUpdateFunction', None)
        
        self.switchStatus = kwargs.get('switchStatus', False)

        self.buttonSizeFactor = 0.7
        if (self.align == 'horizontal'):
            self.images = {'DEFAULT_FRAME_ON':  self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_DEFAULT@ON", self.width*self.scaler, self.height*self.scaler),
                           'HOVERED_FRAME_ON':  self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_HOVERED@ON", self.width*self.scaler, self.height*self.scaler),
                           'PRESSED_FRAME_ON':  self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_PRESSED@ON", self.width*self.scaler, self.height*self.scaler),
                           'DEFAULT_FRAME_OFF': self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_DEFAULT@OFF", self.width*self.scaler, self.height*self.scaler),
                           'HOVERED_FRAME_OFF': self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_HOVERED@OFF", self.width*self.scaler, self.height*self.scaler),
                           'PRESSED_FRAME_OFF': self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_PRESSED@OFF", self.width*self.scaler, self.height*self.scaler),
                           'DEFAULT_BUTTON': self.imageManager.getImageByCode("switch_typeB_"+self.style+"_B_DEFAULT", self.height*self.scaler*self.buttonSizeFactor, self.height*self.scaler*self.buttonSizeFactor),
                           'HOVERED_BUTTON': self.imageManager.getImageByCode("switch_typeB_"+self.style+"_B_HOVERED", self.height*self.scaler*self.buttonSizeFactor, self.height*self.scaler*self.buttonSizeFactor),
                           'PRESSED_BUTTON': self.imageManager.getImageByCode("switch_typeB_"+self.style+"_B_PRESSED", self.height*self.scaler*self.buttonSizeFactor, self.height*self.scaler*self.buttonSizeFactor),
                           'INACTIVEMASK': self.imageManager.getImageByCode("switch_typeB_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler)}
        elif (self.align == 'vertical'):
            self.images = {'DEFAULT_FRAME_ON':  self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_DEFAULT@ON", self.height*self.scaler, self.width*self.scaler),
                           'HOVERED_FRAME_ON':  self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_HOVERED@ON", self.height*self.scaler, self.width*self.scaler),
                           'PRESSED_FRAME_ON':  self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_PRESSED@ON", self.height*self.scaler, self.width*self.scaler),
                           'DEFAULT_FRAME_OFF': self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_DEFAULT@OFF", self.height*self.scaler, self.width*self.scaler),
                           'HOVERED_FRAME_OFF': self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_HOVERED@OFF", self.height*self.scaler, self.width*self.scaler),
                           'PRESSED_FRAME_OFF': self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_PRESSED@OFF", self.height*self.scaler, self.width*self.scaler),
                           'DEFAULT_BUTTON': self.imageManager.getImageByCode("switch_typeB_"+self.style+"_B_DEFAULT", self.height*self.scaler*self.buttonSizeFactor, self.height*self.scaler*self.buttonSizeFactor),
                           'HOVERED_BUTTON': self.imageManager.getImageByCode("switch_typeB_"+self.style+"_B_HOVERED", self.height*self.scaler*self.buttonSizeFactor, self.height*self.scaler*self.buttonSizeFactor),
                           'PRESSED_BUTTON': self.imageManager.getImageByCode("switch_typeB_"+self.style+"_B_PRESSED", self.height*self.scaler*self.buttonSizeFactor, self.height*self.scaler*self.buttonSizeFactor),
                           'INACTIVEMASK': self.imageManager.getImageByCode("switch_typeB_"+self.style+"_INACTIVEMASK", self.height*self.scaler, self.width*self.scaler)}
        if (self.switchStatus == True): self.frameSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT_FRAME_ON'][0],  batch = self.batch, group = self.group_0)
        else:                           self.frameSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT_FRAME_OFF'][0], batch = self.batch, group = self.group_0)
        if   (self.align == 'horizontal'): self.buttonSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = (self.yPos + self.height * (1-self.buttonSizeFactor)/2) * self.scaler, img = self.images['DEFAULT_BUTTON'][0], batch = self.batch, group = self.group_1)
        elif (self.align == 'vertical'):   self.buttonSprite = pyglet.sprite.Sprite(x = (self.xPos + self.height * (1-self.buttonSizeFactor)/2) * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT_BUTTON'][0], batch = self.batch, group = self.group_1)
        self.inactiveMask = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['INACTIVEMASK'][0], batch = self.batch, group = self.group_2); self.inactiveMask.visible = False
        
        self.status = "DEFAULT"
        self.hidden = False; self.deactivated = False
        self.setStatus(self.switchStatus, animate = False, callStatusUpdateFunction = False)

        #Object Animation Variables
        self.animating = False; self.animationTimer = 0; self.animationSpeed = kwargs.get('animationSpeed', 0.1)

    def process(self, t_elapsed_ns):
        if (self.animating == True):
            self.animationTimer += t_elapsed_ns / 1e9
            completion = self.animationTimer / self.animationSpeed
            if (1 <= completion): self.animating = False; completion = 1
            if (self.align == 'horizontal'):
                if (self.switchStatus == True): self.buttonSprite.x = (self.xPos+             self.height*(1-self.buttonSizeFactor)/2+(self.width-self.height)*completion) * self.scaler   #Moving from False -> True
                else:                           self.buttonSprite.x = (self.xPos+self.width - self.height*(1+self.buttonSizeFactor)/2-(self.width-self.height)*completion) * self.scaler   #Moving from True  -> False
            elif (self.align == 'vertical'):
                if (self.switchStatus == True): self.buttonSprite.y = (self.yPos+             self.height*(1-self.buttonSizeFactor)/2+(self.width-self.height)*completion) * self.scaler   #Moving from False -> True
                else:                           self.buttonSprite.y = (self.yPos+self.width - self.height*(1+self.buttonSizeFactor)/2-(self.width-self.height)*completion) * self.scaler   #Moving from True  -> False
            self.buttonSprite.image = self.images[self.status+'_BUTTON'][0]

    def handleMouseEvent(self, event):
        if not((self.deactivated == True) or (self.hidden)):
            if (event['eType'] == "HOVERENTERED"):
                self.audioManager.playAudioByCode('switch_typeB_HOVERED_A')
                self.status = "HOVERED"
                if (self.switchStatus == True): self.frameSprite.image = self.images['HOVERED_FRAME_ON'][0]
                else:                           self.frameSprite.image = self.images['HOVERED_FRAME_OFF'][0]
                self.buttonSprite.image = self.images['HOVERED_BUTTON'][0]
                if (self.hoverFunction != None): self.hoverFunction(self)
            elif (event['eType'] == "HOVERESCAPED"):
                self.status = "DEFAULT"
                if (self.switchStatus == True): self.frameSprite.image = self.images['DEFAULT_FRAME_ON'][0]
                else:                           self.frameSprite.image = self.images['DEFAULT_FRAME_OFF'][0]
                self.buttonSprite.image = self.images['DEFAULT_BUTTON'][0]
            elif (event['eType'] == "DHOVERESCAPED"):
                self.status = "DEFAULT"
                if (self.switchStatus == True): self.frameSprite.image = self.images['DEFAULT_FRAME_ON'][0]
                else:                           self.frameSprite.image = self.images['DEFAULT_FRAME_OFF'][0]
                self.buttonSprite.image = self.images['DEFAULT_BUTTON'][0]
            elif (event['eType'] == "PRESSED"):
                self.audioManager.playAudioByCode('switch_typeB_PRESSED_A')
                self.status = "PRESSED"
                if (self.switchStatus == True): self.frameSprite.image = self.images['PRESSED_FRAME_ON'][0]
                else:                           self.frameSprite.image = self.images['PRESSED_FRAME_OFF'][0]
                self.buttonSprite.image = self.images['PRESSED_BUTTON'][0]
                if (self.pressFunction != None): self.pressFunction(self)
            elif (event['eType'] == "RELEASED"):
                if (self.status == "PRESSED"):
                    self.audioManager.playAudioByCode('switch_typeB_RELEASED_A')
                    self.status = "HOVERED"
                    self.setStatus(not(self.switchStatus), animate = True, callStatusUpdateFunction = False)
                    if (self.releaseFunction      != None): self.releaseFunction(self)
                    if (self.statusUpdateFunction != None): self.statusUpdateFunction(self)

    def handleKeyEvent(self, event): pass

    def show(self):
        self.hidden = False
        self.frameSprite.visible = True
        self.buttonSprite.visible = True
        if (self.deactivated == True): self.inactiveMask.visible = True

    def hide(self):
        self.hidden = True
        self.frameSprite.visible = False
        self.buttonSprite.visible = False
        self.inactiveMask.visible = False

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y;
        self.frameSprite.position  = (self.xPos*self.scaler, self.yPos*self.scaler, self.frameSprite.z)
        if (self.align == 'horizontal'):
            if (self.switchStatus == True): self.buttonSprite.position = ((self.xPos + self.width - self.height * (1+self.buttonSizeFactor)/2) * self.scaler, (self.yPos + self.height * (1-self.buttonSizeFactor)/2) * self.scaler, self.buttonSprite.z)
            else:                           self.buttonSprite.position = ((self.xPos + self.height              * (1-self.buttonSizeFactor)/2) * self.scaler,              (self.yPos + self.height * (1-self.buttonSizeFactor)/2) * self.scaler, self.buttonSprite.z)
        elif (self.align == 'vertical'):
            if (self.switchStatus == True): self.buttonSprite.position = ((self.xPos + self.height * (1-self.buttonSizeFactor)/2) * self.scaler, (self.yPos + self.width - self.height * (1+self.buttonSizeFactor)/2) * self.scaler, self.buttonSprite.z)
            else:                           self.buttonSprite.position = ((self.xPos + self.height * (1-self.buttonSizeFactor)/2) * self.scaler, (self.yPos + self.height * (1-self.buttonSizeFactor)/2) * self.scaler,              self.buttonSprite.z)
        self.inactiveMask.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.inactiveMask.z)
        self.hitBox.reposition(xPos = self.xPos, yPos = self.yPos)

    def resize(self, width, height):
        self.width = width; self.height = height
        if (self.align == 'horizontal'):
            self.images['DEFAULT_FRAME_ON']  = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_DEFAULT@ON",  self.width*self.scaler, self.height*self.scaler)
            self.images['HOVERED_FRAME_ON']  = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_HOVERED@ON",  self.width*self.scaler, self.height*self.scaler)
            self.images['PRESSED_FRAME_ON']  = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_PRESSED@ON",  self.width*self.scaler, self.height*self.scaler)
            self.images['DEFAULT_FRAME_OFF'] = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_DEFAULT@OFF", self.width*self.scaler, self.height*self.scaler)
            self.images['HOVERED_FRAME_OFF'] = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_HOVERED@OFF", self.width*self.scaler, self.height*self.scaler)
            self.images['PRESSED_FRAME_OFF'] = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_PRESSED@OFF", self.width*self.scaler, self.height*self.scaler)
            self.images['DEFAULT_BUTTON']    = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_B_DEFAULT",     self.height*self.scaler*self.buttonSizeFactor, self.height*self.scaler*self.buttonSizeFactor)
            self.images['HOVERED_BUTTON']    = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_B_HOVERED",     self.height*self.scaler*self.buttonSizeFactor, self.height*self.scaler*self.buttonSizeFactor)
            self.images['PRESSED_BUTTON']    = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_B_PRESSED",     self.height*self.scaler*self.buttonSizeFactor, self.height*self.scaler*self.buttonSizeFactor)
            self.images['INACTIVEMASK']      = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_INACTIVEMASK",  self.width*self.scaler, self.height*self.scaler)
        elif (self.align == 'vertical'):
            self.images['DEFAULT_FRAME_ON']  = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_DEFAULT@ON",  self.height*self.scaler, self.width*self.scaler)
            self.images['HOVERED_FRAME_ON']  = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_HOVERED@ON",  self.height*self.scaler, self.width*self.scaler)
            self.images['PRESSED_FRAME_ON']  = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_PRESSED@ON",  self.height*self.scaler, self.width*self.scaler)
            self.images['DEFAULT_FRAME_OFF'] = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_DEFAULT@OFF", self.height*self.scaler, self.width*self.scaler)
            self.images['HOVERED_FRAME_OFF'] = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_HOVERED@OFF", self.height*self.scaler, self.width*self.scaler)
            self.images['PRESSED_FRAME_OFF'] = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_F_PRESSED@OFF", self.height*self.scaler, self.width*self.scaler)
            self.images['DEFAULT_BUTTON']    = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_B_DEFAULT",     self.height*self.scaler*self.buttonSizeFactor, self.height*self.scaler*self.buttonSizeFactor)
            self.images['HOVERED_BUTTON']    = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_B_HOVERED",     self.height*self.scaler*self.buttonSizeFactor, self.height*self.scaler*self.buttonSizeFactor)
            self.images['PRESSED_BUTTON']    = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_B_PRESSED",     self.height*self.scaler*self.buttonSizeFactor, self.height*self.scaler*self.buttonSizeFactor)
            self.images['INACTIVEMASK']      = self.imageManager.getImageByCode("switch_typeB_"+self.style+"_INACTIVEMASK",  self.height*self.scaler, self.width*self.scaler)

        if (self.switchStatus == True): self.frameSprite.image = self.images[self.status+'_FRAME_ON'][0]
        else:                           self.frameSprite.image = self.images[self.status+'_FRAME_OFF'][0]
        self.buttonSprite.image = self.images[self.status+'_BUTTON'][0]
        if (self.align == 'horizontal'):
            if (self.switchStatus == True): self.buttonSprite.position = ((self.xPos + self.width - self.height * (1+self.buttonSizeFactor)/2) * self.scaler, (self.yPos + self.height * (1-self.buttonSizeFactor)/2) * self.scaler, self.buttonSprite.z)
            else:                           self.buttonSprite.position = ((self.xPos + self.height              * (1-self.buttonSizeFactor)/2) * self.scaler,              (self.yPos + self.height * (1-self.buttonSizeFactor)/2) * self.scaler, self.buttonSprite.z)
        elif (self.align == 'vertical'):
            if (self.switchStatus == True): self.buttonSprite.position = ((self.xPos + self.height * (1-self.buttonSizeFactor)/2) * self.scaler, (self.yPos + self.width - self.height * (1+self.buttonSizeFactor)/2) * self.scaler, self.buttonSprite.z)
            else:                           self.buttonSprite.position = ((self.xPos + self.height * (1-self.buttonSizeFactor)/2) * self.scaler, (self.yPos + self.height * (1-self.buttonSizeFactor)/2) * self.scaler,              self.buttonSprite.z)
        self.inactiveMask.image = self.images['INACTIVEMASK'][0]
        if (self.align == 'horizontal'): self.hitBox.resize(width = self.width,  height = self.height)
        elif (self.align == 'vertical'): self.hitBox.resize(width = self.height, height = self.width)

    def activate(self):
        self.deactivated = False
        self.inactiveMask.visible = False

    def deactivate(self):
        self.deactivated = True
        if (self.hidden == False): self.inactiveMask.visible = True
        
    def setName(self, name): self.name = name
    def getName(self): return self.name
    def isTouched(self, mouseX, mouseY): return self.hitBox.isTouched(mouseX, mouseY)
    def isHidden(self): return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        self.images['DEFAULT_FRAME_ON']  = self.imageManager.getImageByLoadIndex(self.images['DEFAULT_FRAME_ON'][1])
        self.images['HOVERED_FRAME_ON']  = self.imageManager.getImageByLoadIndex(self.images['HOVERED_FRAME_ON'][1])
        self.images['PRESSED_FRAME_ON']  = self.imageManager.getImageByLoadIndex(self.images['PRESSED_FRAME_ON'][1])
        self.images['DEFAULT_FRAME_OFF'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT_FRAME_OFF'][1])
        self.images['HOVERED_FRAME_OFF'] = self.imageManager.getImageByLoadIndex(self.images['HOVERED_FRAME_OFF'][1])
        self.images['PRESSED_FRAME_OFF'] = self.imageManager.getImageByLoadIndex(self.images['PRESSED_FRAME_OFF'][1])
        self.images['DEFAULT_BUTTON']    = self.imageManager.getImageByLoadIndex(self.images['DEFAULT_BUTTON'][1])
        self.images['HOVERED_BUTTON']    = self.imageManager.getImageByLoadIndex(self.images['HOVERED_BUTTON'][1])
        self.images['PRESSED_BUTTON']    = self.imageManager.getImageByLoadIndex(self.images['PRESSED_BUTTON'][1])
        if (self.switchStatus == True): self.frameSprite.image = self.images[self.status+"_FRAME_ON"][0]
        else:                           self.frameSprite.image = self.images[self.status+"_FRAME_OFF"][0]
        self.buttonSprite.image = self.images[self.status+"_BUTTON"][0]

    def on_LanguageUpdate(self, **kwargs): pass

    def getStatus(self): return self.switchStatus

    def setStatus(self, status, animate = False, callStatusUpdateFunction = True):
        _switchStatus_prev = self.switchStatus
        self.switchStatus = status
        if (animate == True):
            if (status == True): self.frameSprite.image = self.images[self.status+'_FRAME_ON'][0]
            else:                self.frameSprite.image = self.images[self.status+'_FRAME_OFF'][0]
            self.animationTimer = 0; self.animating = True
        else:
            if (self.align == 'horizontal'):
                if (self.switchStatus == True): self.frameSprite.image = self.images[self.status+'_FRAME_ON'][0];  self.buttonSprite.x = (self.xPos            + self.height*(1-self.buttonSizeFactor)/2+(self.width-self.height)) * self.scaler
                else:                           self.frameSprite.image = self.images[self.status+'_FRAME_OFF'][0]; self.buttonSprite.x = (self.xPos+self.width - self.height*(1+self.buttonSizeFactor)/2-(self.width-self.height)) * self.scaler
            elif (self.align == 'vertical'):
                if (self.switchStatus == True): self.frameSprite.image = self.images[self.status+'_FRAME_ON'][0];  self.buttonSprite.y = (self.yPos            + self.height*(1-self.buttonSizeFactor)/2+(self.width-self.height)) * self.scaler
                else:                           self.frameSprite.image = self.images[self.status+'_FRAME_OFF'][0]; self.buttonSprite.y = (self.yPos+self.width - self.height*(1+self.buttonSizeFactor)/2-(self.width-self.height)) * self.scaler
            self.buttonSprite.image = self.images[self.status+'_BUTTON'][0]
        if ((_switchStatus_prev != self.switchStatus) and (callStatusUpdateFunction == True) and (self.statusUpdateFunction != None)): self.statusUpdateFunction(self)
        
    def getGroupRequirement(): return 2
#GUIO - 'switch_typeB' END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'switch_typeC' ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class switch_typeC:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.group_2 = kwargs['group_2']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)
            self.group_2 = pyglet.graphics.Group(order = self.groupOrder+2)

        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.style = kwargs.get('style', 'styleA')
        self.hitBox = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos, self.width, self.height)
        
        self.text = kwargs.get('text', None)
        self.fontSize = int(kwargs.get('fontSize', 100)*self.scaler)
        self.textStyle = kwargs.get('textStyle', 'default')
        self.effectiveTextStyle = self.visualManager.getTextStyle('switch_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        self.textAnchor = kwargs.get('anchor', 'CENTER')

        #Functional Object Parameters
        self.hoverFunction        = kwargs.get('hoverFunction',        None)
        self.hoverEscapeFunction  = kwargs.get('hoverEscapeFunction',  None)
        self.pressFunction        = kwargs.get('pressFunction',        None)
        self.releaseFunction      = kwargs.get('releaseFunction',      None)
        self.statusUpdateFunction = kwargs.get('statusUpdateFunction', None)
        
        self.switchStatus = kwargs.get('switchStatus', False)
        self.outlineWidth = kwargs.get('outlineWidth', 2)
        self.images = {'DEFAULT_OFF':  self.imageManager.getImageByCode("switch_typeC_"+self.style+"_DEFAULT@OFF",  self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.outlineWidth)),
                       'HOVERED_OFF':  self.imageManager.getImageByCode("switch_typeC_"+self.style+"_HOVERED@OFF",  self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.outlineWidth)),
                       'PRESSED_OFF':  self.imageManager.getImageByCode("switch_typeC_"+self.style+"_PRESSED@OFF",  self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.outlineWidth)),
                       'DEFAULT_ON':   self.imageManager.getImageByCode("switch_typeC_"+self.style+"_DEFAULT@ON",   self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.outlineWidth)),
                       'HOVERED_ON':   self.imageManager.getImageByCode("switch_typeC_"+self.style+"_HOVERED@ON",   self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.outlineWidth)),
                       'PRESSED_ON':   self.imageManager.getImageByCode("switch_typeC_"+self.style+"_PRESSED@ON",   self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.outlineWidth)),
                       'INACTIVEMASK': self.imageManager.getImageByCode("switch_typeC_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.outlineWidth))}
        
        if (self.switchStatus == True): self.buttonSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT_ON'][0],  batch = self.batch, group = self.group_0)
        else:                           self.buttonSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT_OFF'][0], batch = self.batch, group = self.group_0)
        self.textElement = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_1,
                                                                  text = self.visualManager.extractText(self.text), defaultTextStyle = self.effectiveTextStyle['DEFAULT'],
                                                                  xPos = self.xPos, yPos = self.yPos, width = self.width, height = self.height, showElementBox = False, anchor = 'CENTER')
        self.textElement.addTextStyle('HOVERED',  self.effectiveTextStyle['HOVERED'])
        self.textElement.addTextStyle('PRESSED',  self.effectiveTextStyle['PRESSED'])
        self.textElement.addTextStyle('INACTIVE', self.effectiveTextStyle['INACTIVE'])
        self.inactiveMask = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['INACTIVEMASK'][0], batch = self.batch, group = self.group_2); self.inactiveMask.visible = False


        self.status = 'DEFAULT'
        self.hidden = False; self.deactivated = False

        self.setStatus(self.switchStatus, callStatusUpdateFunction = False)

    def process(self, t_elapsed_ns): pass

    def handleMouseEvent(self, event):
        if not((self.deactivated == True) or (self.hidden)):
            if (event['eType'] == "HOVERENTERED"):
                self.audioManager.playAudioByCode('switch_typeA_HOVERED_A')
                self.status = "HOVERED"
                if (self.switchStatus == True): self.buttonSprite.image = self.images['HOVERED_ON'][0]
                else:                           self.buttonSprite.image = self.images['HOVERED_OFF'][0]
                if (self.hoverFunction != None): self.hoverFunction(self)
            elif (event['eType'] == "HOVERESCAPED"):
                self.status = "DEFAULT"
                if (self.switchStatus == True): self.buttonSprite.image = self.images['DEFAULT_ON'][0]
                else:                           self.buttonSprite.image = self.images['DEFAULT_OFF'][0]
            elif (event['eType'] == "DHOVERESCAPED"):
                self.status = "DEFAULT"
                if (self.switchStatus == True): self.buttonSprite.image = self.images['DEFAULT_ON'][0]
                else:                           self.buttonSprite.image = self.images['DEFAULT_OFF'][0]
            elif (event['eType'] == "PRESSED"):
                self.audioManager.playAudioByCode('switch_typeA_PRESSED_A')
                self.status = "PRESSED"
                if (self.switchStatus == True): self.buttonSprite.image = self.images['PRESSED_ON'][0]
                else:                           self.buttonSprite.image = self.images['PRESSED_OFF'][0]
                if (self.pressFunction != None): self.pressFunction(self)
            elif (event['eType'] == "RELEASED"):
                if (self.status == "PRESSED"):
                    self.switchStatus = not(self.switchStatus)
                    self.audioManager.playAudioByCode('switch_typeA_RELEASED_A')
                    self.status = "HOVERED"
                    if (self.switchStatus == True): self.buttonSprite.image = self.images['HOVERED_ON'][0]
                    else:                           self.buttonSprite.image = self.images['HOVERED_OFF'][0]
                    if (self.releaseFunction      != None): self.releaseFunction(self)
                    if (self.statusUpdateFunction != None): self.statusUpdateFunction(self)

    def handleKeyEvent(self, event): pass

    def show(self):
        self.hidden = False
        self.buttonSprite.visible = True
        if (self.deactivated == True): self.inactiveMask.visible = True
        self.textElement.show()

    def hide(self):
        self.hidden = True
        self.buttonSprite.visible = False
        self.inactiveMask.visible = False
        self.textElement.hide()

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y;
        self.buttonSprite.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.buttonSprite.z)
        self.textElement.moveTo(x = self.xPos, y = self.yPos)
        self.inactiveMask.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.inactiveMask.z)
        self.hitBox.reposition(xPos = self.xPos, yPos = self.yPos)

    def resize(self, width, height):
        self.width = width; self.height = height
        self.textElement.changeSize(width = self.width, height = self.height)
        self.images['DEFAULT_OFF']  = self.imageManager.getImageByCode("switch_typeC_"+self.style+"_DEFAULT@OFF",  self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.outlineWidth))
        self.images['HOVERED_OFF']  = self.imageManager.getImageByCode("switch_typeC_"+self.style+"_HOVERED@OFF",  self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.outlineWidth))
        self.images['PRESSED_OFF']  = self.imageManager.getImageByCode("switch_typeC_"+self.style+"_PRESSED@OFF",  self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.outlineWidth))
        self.images['DEFAULT_ON']   = self.imageManager.getImageByCode("switch_typeC_"+self.style+"_DEFAULT@ON",   self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.outlineWidth))
        self.images['HOVERED_ON']   = self.imageManager.getImageByCode("switch_typeC_"+self.style+"_HOVERED@ON",   self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.outlineWidth))
        self.images['PRESSED_ON']   = self.imageManager.getImageByCode("switch_typeC_"+self.style+"_PRESSED@ON",   self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.outlineWidth))
        self.images['INACTIVEMASK'] = self.imageManager.getImageByCode("switch_typeC_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.outlineWidth))
        if (self.switchStatus == True): self.buttonSprite.image = self.images[self.status+'_ON'][0]
        else:                           self.buttonSprite.image = self.images[self.status+'_OFF'][0]
        self.inactiveMask.image = self.images['INACTIVEMASK'][0]
        self.hitBox.resize(width = self.width, height = self.height)

    def activate(self):
        if (self.hidden == False):
            self.inactiveMask.visible = False
            self.textElement.editTextStyle('all', self.status)
        self.deactivated = False

    def deactivate(self):
        if (self.hidden == False): 
            self.inactiveMask.visible = True
            self.textElement.editTextStyle('all', 'INACTIVE')
        self.deactivated = True
        
    def setName(self, name): self.name = name
    def getName(self): return self.name
    def isTouched(self, mouseX, mouseY): return self.hitBox.isTouched(mouseX, mouseY)
    def isHidden(self): return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        self.images['DEFAULT_ON']  = self.imageManager.getImageByLoadIndex(self.images['DEFAULT_ON'][1])
        self.images['HOVERED_ON']  = self.imageManager.getImageByLoadIndex(self.images['HOVERED_ON'][1])
        self.images['PRESSED_ON']  = self.imageManager.getImageByLoadIndex(self.images['PRESSED_ON'][1])
        self.images['DEFAULT_OFF'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT_OFF'][1])
        self.images['HOVERED_OFF'] = self.imageManager.getImageByLoadIndex(self.images['HOVERED_OFF'][1])
        self.images['PRESSED_OFF'] = self.imageManager.getImageByLoadIndex(self.images['PRESSED_OFF'][1])
        self.effectiveTextStyle = self.visualManager.getTextStyle('switch_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize

        if (self.switchStatus == True): self.buttonSprite.image = self.images[self.status+'_ON'][0]
        else:                           self.buttonSprite.image = self.images[self.status+'_OFF'][0]
        self.textElement.addTextStyle('HOVERED',  self.effectiveTextStyle['HOVERED'])
        self.textElement.addTextStyle('PRESSED',  self.effectiveTextStyle['PRESSED'])
        self.textElement.addTextStyle('INACTIVE', self.effectiveTextStyle['INACTIVE'])
        self.textElement.on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['DEFAULT'])

    def on_LanguageUpdate(self, **kwargs):
        self.effectiveTextStyle = self.visualManager.getTextStyle('switch_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        previousText = self.textElement.getText(); newText = self.visualManager.extractText(self.text)
        if (previousText == newText): self.textElement.on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'])
        else:                         self.textElement.on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'], newLanguageText = newText)

    def getStatus(self): return self.switchStatus

    def setStatus(self, status, callStatusUpdateFunction = True):
        if (status != self.switchStatus):
            self.switchStatus = status
            if (self.switchStatus == True): self.buttonSprite.image = self.images[self.status+'_ON'][0]
            else:                           self.buttonSprite.image = self.images[self.status+'_OFF'][0]
            if ((callStatusUpdateFunction == True) and (self.statusUpdateFunction != None)): self.statusUpdateFunction(self)
        
    def getGroupRequirement(): return 2
#GUIO - 'switch_typeC' END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'slider_typeA' ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class slider_typeA:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.group_2 = kwargs['group_2']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)
            self.group_2 = pyglet.graphics.Group(order = self.groupOrder+2)

        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.align = kwargs.get('align', 'horizontal');
        self.style = kwargs.get('style', 'styleA')

        #Functional Object Parameters
        self.hoverFunction       = kwargs.get('hoverFunction',       None)
        self.hoverEscapeFunction = kwargs.get('hoverEscapeFunction', None)
        self.pressFunction       = kwargs.get('pressFunction',       None)
        self.releaseFunction     = kwargs.get('releaseFunction',     None)
        self.valueUpdateFunction = kwargs.get('valueUpdateFunction', None)
        
        #-----These values are resolution scaled
        self.sliderValue = kwargs.get('sliderValue', 50)
        self.railLength = self.width - self.height/2
        self.buttonSize = self.height
        
        if (self.align == 'horizontal'): self.buttonPos_0 = self.xPos+(self.width-self.railLength-self.buttonSize)/2
        elif (self.align == 'vertical'): self.buttonPos_0 = self.yPos+(self.width-self.railLength-self.buttonSize)/2

        if (self.align == 'horizontal'):
            self.images = {'DEFAULT_SLIDER':  self.imageManager.getImageByCode("slider_typeA_"+self.style+"_S_DEFAULT", self.width*self.scaler, self.height/2*self.scaler),
                           'HOVERED_SLIDER':  self.imageManager.getImageByCode("slider_typeA_"+self.style+"_S_HOVERED", self.width*self.scaler, self.height/2*self.scaler),
                           'PRESSED_SLIDER':  self.imageManager.getImageByCode("slider_typeA_"+self.style+"_S_PRESSED", self.width*self.scaler, self.height/2*self.scaler),
                           'DEFAULT_BUTTON':  self.imageManager.getImageByCode("slider_typeA_"+self.style+"_B_DEFAULT", self.buttonSize*self.scaler, self.buttonSize*self.scaler),
                           'HOVERED_BUTTON':  self.imageManager.getImageByCode("slider_typeA_"+self.style+"_B_HOVERED", self.buttonSize*self.scaler, self.buttonSize*self.scaler),
                           'PRESSED_BUTTON':  self.imageManager.getImageByCode("slider_typeA_"+self.style+"_B_PRESSED", self.buttonSize*self.scaler, self.buttonSize*self.scaler),
                           'INACTIVEMASK_SLIDER': self.imageManager.getImageByCode("slider_typeA_"+self.style+"_S_INACTIVEMASK", self.width*self.scaler, self.height/2*self.scaler),
                           'INACTIVEMASK_BUTTON': self.imageManager.getImageByCode("slider_typeA_"+self.style+"_B_INACTIVEMASK", self.buttonSize*self.scaler, self.buttonSize*self.scaler)}
        elif (self.align == 'vertical'):
            self.images = {'DEFAULT_SLIDER':  self.imageManager.getImageByCode("slider_typeA_"+self.style+"_S_DEFAULT", self.height/2*self.scaler, self.width*self.scaler),
                           'HOVERED_SLIDER':  self.imageManager.getImageByCode("slider_typeA_"+self.style+"_S_HOVERED", self.height/2*self.scaler, self.width*self.scaler),
                           'PRESSED_SLIDER':  self.imageManager.getImageByCode("slider_typeA_"+self.style+"_S_PRESSED", self.height/2*self.scaler, self.width*self.scaler),
                           'DEFAULT_BUTTON':  self.imageManager.getImageByCode("slider_typeA_"+self.style+"_B_DEFAULT", self.buttonSize*self.scaler, self.buttonSize*self.scaler),
                           'HOVERED_BUTTON':  self.imageManager.getImageByCode("slider_typeA_"+self.style+"_B_HOVERED", self.buttonSize*self.scaler, self.buttonSize*self.scaler),
                           'PRESSED_BUTTON':  self.imageManager.getImageByCode("slider_typeA_"+self.style+"_B_PRESSED", self.buttonSize*self.scaler, self.buttonSize*self.scaler),
                           'INACTIVEMASK_SLIDER': self.imageManager.getImageByCode("slider_typeA_"+self.style+"_S_INACTIVEMASK", self.height/2*self.scaler, self.width*self.scaler),
                           'INACTIVEMASK_BUTTON': self.imageManager.getImageByCode("slider_typeA_"+self.style+"_B_INACTIVEMASK", self.buttonSize*self.scaler, self.buttonSize*self.scaler)}

        #Graphics Sprites
        if (self.align == 'horizontal'): 
            self.sliderSprite = pyglet.sprite.Sprite(x = self.xPos*self.scaler, y = (self.yPos+self.height/4)*self.scaler,                   img = self.images['DEFAULT_SLIDER'][0], batch = self.batch, group = self.group_0)
            self.buttonSprite = pyglet.sprite.Sprite(x = self.xPos*self.scaler, y = (self.yPos+(self.height-self.buttonSize)/2)*self.scaler, img = self.images['DEFAULT_BUTTON'][0], batch = self.batch, group = self.group_1)
        elif (self.align == 'vertical'): 
            self.sliderSprite = pyglet.sprite.Sprite(x = (self.xPos+self.height/4)*self.scaler,                   y = self.yPos*self.scaler, img = self.images['DEFAULT_SLIDER'][0], batch = self.batch, group = self.group_0)
            self.buttonSprite = pyglet.sprite.Sprite(x = (self.xPos+(self.height-self.buttonSize)/2)*self.scaler, y = self.yPos*self.scaler, img = self.images['DEFAULT_BUTTON'][0], batch = self.batch, group = self.group_1)
        self.inactiveMask_slider = pyglet.sprite.Sprite(x = self.sliderSprite.x,     y = self.sliderSprite.y,     img = self.images['INACTIVEMASK_SLIDER'][0], batch = self.batch, group = self.group_2); self.inactiveMask_slider.visible = False
        self.inactiveMask_button = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['INACTIVEMASK_BUTTON'][0], batch = self.batch, group = self.group_2); self.inactiveMask_button.visible = False
        #Hitbox
        if (self.align == 'horizontal'): self.hitBox_slider = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos+self.height/4, self.width, self.height/2)
        elif (self.align == 'vertical'): self.hitBox_slider = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos+self.height/4, self.yPos, self.height/2, self.width)
        self.hitBox_button = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos, self.buttonSize, self.buttonSize)

        #Status Variables
        self.status = "DEFAULT"; self.status_slider = "DEFAULT"; self.status_button = "DEFAULT"
        self.hidden = False; self.deactivated = False

        #Initial Positioning
        self.__positionButton(self.sliderValue)

    def process(self, t_elapsed_ns): pass

    def handleMouseEvent(self, event):
        if not((self.deactivated == True) or (self.hidden)):
            if (event['eType'] == "HOVERENTERED"):
                self.status = "HOVERED"
                if (self.hitBox_slider.isTouched(event['x'], event['y']) == True):
                    self.audioManager.playAudioByCode('slider_typeA_HOVERED_A')
                    self.sliderSprite.image = self.images[self.status+"_SLIDER"][0]; self.status_slider = "HOVERED"
                if (self.hitBox_button.isTouched(event['x'], event['y']) == True):
                    self.audioManager.playAudioByCode('slider_typeA_HOVERED_A')
                    self.buttonSprite.image = self.images[self.status+"_BUTTON"][0]; self.status_button = "HOVERED"
                if (self.hoverFunction != None): self.hoverFunction(self)
                
            elif (event['eType'] == "HOVERESCAPED"):
                self.status = "DEFAULT"
                self.sliderSprite.image = self.images[self.status+"_SLIDER"][0]; self.status_slider = "DEFAULT"
                self.buttonSprite.image = self.images[self.status+"_BUTTON"][0]; self.status_button = "DEFAULT"

            elif (event['eType'] == "PRESSED"):
                self.audioManager.playAudioByCode('slider_typeA_PRESSED_A')
                self.status = "PRESSED"
                self.sliderSprite.image = self.images[self.status+"_SLIDER"][0]; self.status_slider = "PRESSED"
                self.buttonSprite.image = self.images[self.status+"_BUTTON"][0]; self.status_button = "PRESSED"
                if (self.align == 'horizontal'): self.__positionButton(self.__calculateSliderValue(event['x']))
                elif (self.align == 'vertical'): self.__positionButton(self.__calculateSliderValue(event['y']))
                if (self.pressFunction != None): self.pressFunction(self)
                
            elif (event['eType'] == "RELEASED"):
                self.audioManager.playAudioByCode('slider_typeA_RELEASED_A')
                self.status = "HOVERED"
                self.sliderSprite.image = self.images[self.status+"_SLIDER"][0]; self.status_slider = "HOVERED"
                self.buttonSprite.image = self.images[self.status+"_BUTTON"][0]; self.status_button = "HOVERED"
                if (self.releaseFunction != None): self.releaseFunction(self)
                
            elif (event['eType'] == "DRAGGED"):
                if (self.status == "PRESSED"):
                    if (self.align == 'horizontal'): self.__positionButton(self.__calculateSliderValue(event['x']))
                    elif (self.align == 'vertical'): self.__positionButton(self.__calculateSliderValue(event['y']))

            elif (event['eType'] == "MOVED"):
                sliderTouched = self.hitBox_slider.isTouched(event['x'], event['y'])
                if   ((sliderTouched == True)  and (self.status_slider == "DEFAULT")): self.sliderSprite.image = self.images["HOVERED_SLIDER"][0]; self.status_slider = "HOVERED"; self.audioManager.playAudioByCode('slider_typeA_HOVERED_A')
                elif ((sliderTouched == False) and (self.status_slider == "HOVERED")): self.sliderSprite.image = self.images["DEFAULT_SLIDER"][0]; self.status_slider = "DEFAULT"
                buttonTouched = self.hitBox_button.isTouched(event['x'], event['y'])
                if   ((buttonTouched == True)  and (self.status_button == "DEFAULT")): self.buttonSprite.image = self.images["HOVERED_BUTTON"][0]; self.status_button = "HOVERED"; self.audioManager.playAudioByCode('slider_typeA_HOVERED_A')
                elif ((buttonTouched == False) and (self.status_button == "HOVERED")): self.buttonSprite.image = self.images["DEFAULT_BUTTON"][0]; self.status_button = "DEFAULT"

    def handleKeyEvent(self, event): pass

    def show(self):
        self.hidden = False
        self.sliderSprite.visible = True
        self.buttonSprite.visible = True
        if (self.deactivated == True):
            self.inactiveMask_slider.visible = True
            self.inactiveMask_button.x = self.buttonSprite.x; self.inactiveMask_button.y = self.buttonSprite.y;
            self.inactiveMask_button.visible = True

    def hide(self):
        self.hidden = True
        self.sliderSprite.visible = False
        self.buttonSprite.visible = False
        self.inactiveMask_slider.visible = False
        self.inactiveMask_button.visible = False

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y
        if (self.align == 'horizontal'):
            self.buttonPos_0 = self.xPos+(self.width-self.railLength-self.buttonSize)/2
            self.sliderSprite.position = (self.xPos*self.scaler, (self.yPos+self.height/4)*self.scaler, self.sliderSprite.z)
            self.buttonSprite.position = ((self.buttonPos_0+(self.sliderValue*self.railLength/100))*self.scaler, (self.yPos+(self.height-self.buttonSize)/2)*self.scaler, self.buttonSprite.z)
        elif (self.align == 'vertical'):
            self.buttonPos_0 = self.yPos+(self.width-self.railLength-self.buttonSize)/2
            self.sliderSprite.position = ((self.xPos+self.height/4)*self.scaler, self.yPos*self.scaler, self.sliderSprite.z)
            self.buttonSprite.position = ((self.xPos+(self.height-self.buttonSize)/2)*self.scaler, (self.buttonPos_0+(self.sliderValue*self.railLength/100))*self.scaler, self.buttonSprite.z)

        self.inactiveMask_slider.position = (self.sliderSprite.x, self.sliderSprite.y, self.sliderSprite.z)
        self.inactiveMask_button.position = (self.buttonSprite.x, self.buttonSprite.y, self.buttonSprite.z)
        self.hitBox_slider.reposition(xPos = self.sliderSprite.x/self.scaler, yPos = self.sliderSprite.y/self.scaler)
        self.hitBox_button.reposition(xPos = self.buttonSprite.x/self.scaler, yPos = self.buttonSprite.y/self.scaler)
            

    def resize(self, width, height):
        self.width = width; self.height = height
        self.railLength = self.width - self.height/2
        self.buttonSize = self.height
        if (self.align == 'horizontal'):
            self.images['DEFAULT_SLIDER']      = self.imageManager.getImageByCode("slider_typeA_"+self.style+"_S_DEFAULT",      self.width*self.scaler,      self.height/2*self.scaler)
            self.images['HOVERED_SLIDER']      = self.imageManager.getImageByCode("slider_typeA_"+self.style+"_S_HOVERED",      self.width*self.scaler,      self.height/2*self.scaler)
            self.images['PRESSED_SLIDER']      = self.imageManager.getImageByCode("slider_typeA_"+self.style+"_S_PRESSED",      self.width*self.scaler,      self.height/2*self.scaler)
            self.images['DEFAULT_BUTTON']      = self.imageManager.getImageByCode("slider_typeA_"+self.style+"_B_DEFAULT",      self.buttonSize*self.scaler, self.buttonSize*self.scaler)
            self.images['HOVERED_BUTTON']      = self.imageManager.getImageByCode("slider_typeA_"+self.style+"_B_HOVERED",      self.buttonSize*self.scaler, self.buttonSize*self.scaler)
            self.images['PRESSED_BUTTON']      = self.imageManager.getImageByCode("slider_typeA_"+self.style+"_B_PRESSED",      self.buttonSize*self.scaler, self.buttonSize*self.scaler)
            self.images['INACTIVEMASK_SLIDER'] = self.imageManager.getImageByCode("slider_typeA_"+self.style+"_S_INACTIVEMASK", self.width*self.scaler,      self.height/2*self.scaler)
            self.images['INACTIVEMASK_BUTTON'] = self.imageManager.getImageByCode("slider_typeA_"+self.style+"_B_INACTIVEMASK", self.buttonSize*self.scaler, self.buttonSize*self.scaler)
        elif (self.align == 'vertical'): 
            self.images['DEFAULT_SLIDER']      = self.imageManager.getImageByCode("slider_typeA_"+self.style+"_S_DEFAULT",      self.height/2*self.scaler,   self.width*self.scaler)
            self.images['HOVERED_SLIDER']      = self.imageManager.getImageByCode("slider_typeA_"+self.style+"_S_HOVERED",      self.height/2*self.scaler,   self.width*self.scaler)
            self.images['PRESSED_SLIDER']      = self.imageManager.getImageByCode("slider_typeA_"+self.style+"_S_PRESSED",      self.height/2*self.scaler,   self.width*self.scaler)
            self.images['DEFAULT_BUTTON']      = self.imageManager.getImageByCode("slider_typeA_"+self.style+"_B_DEFAULT",      self.buttonSize*self.scaler, self.buttonSize*self.scaler)
            self.images['HOVERED_BUTTON']      = self.imageManager.getImageByCode("slider_typeA_"+self.style+"_B_HOVERED",      self.buttonSize*self.scaler, self.buttonSize*self.scaler)
            self.images['PRESSED_BUTTON']      = self.imageManager.getImageByCode("slider_typeA_"+self.style+"_B_PRESSED",      self.buttonSize*self.scaler, self.buttonSize*self.scaler)
            self.images['INACTIVEMASK_SLIDER'] = self.imageManager.getImageByCode("slider_typeA_"+self.style+"_S_INACTIVEMASK", self.height/2*self.scaler,   self.width*self.scaler)
            self.images['INACTIVEMASK_BUTTON'] = self.imageManager.getImageByCode("slider_typeA_"+self.style+"_B_INACTIVEMASK", self.buttonSize*self.scaler, self.buttonSize*self.scaler)
        self.sliderSprite.image = self.images[self.status+'_SLIDER'][0]
        self.buttonSprite.image = self.images[self.status+'_BUTTON'][0]
        self.inactiveMask_slider.image = self.images['INACTIVEMASK_SLIDER'][0]
        self.inactiveMask_button.image = self.images['INACTIVEMASK_BUTTON'][0]

        if (self.align == 'horizontal'): self.hitBox_slider.resize(width = self.width, height = self.height/2)
        elif (self.align == 'vertical'): self.hitBox_slider.resize(width = self.height/2, height = self.width)
        self.hitBox_button.resize(width = self.buttonSize, height = self.buttonSize)
        
        if (self.align == 'horizontal'):
            self.buttonPos_0 = self.xPos+(self.width-self.railLength-self.buttonSize)/2
            self.sliderSprite.y = (self.yPos+self.height/4)*self.scaler
            self.buttonSprite.position = ((self.buttonPos_0+(self.sliderValue*self.railLength/100))*self.scaler, (self.yPos+(self.height-self.buttonSize)/2)*self.scaler, self.buttonSprite.z)
            self.inactiveMask_slider.y = self.sliderSprite.y
            self.inactiveMask_button.position = (self.buttonSprite.x, self.buttonSprite.y, self.buttonSprite.z)
            self.hitBox_slider.reposition(xPos = self.sliderSprite.x/self.scaler)
            self.hitBox_button.reposition(xPos = self.buttonSprite.x/self.scaler, yPos = self.buttonSprite.y/self.scaler)
        elif (self.align == 'vertical'):
            self.sliderSprite.x = (self.xPos+self.height/4)*self.scaler
            self.buttonSprite.position = ((self.xPos+(self.height-self.buttonSize)/2)*self.scaler, (self.buttonPos_0+(self.sliderValue*self.railLength/100))*self.scaler, self.buttonSprite.z)
            self.inactiveMask_slider.x = self.sliderSprite.x
            self.inactiveMask_button.position = (self.buttonSprite.x, self.buttonSprite.y, self.buttonSprite.z)
            self.hitBox_slider.reposition(yPos = self.sliderSprite.y/self.scaler)
            self.hitBox_button.reposition(xPos = self.buttonSprite.x/self.scaler, yPos = self.buttonSprite.y/self.scaler)

    def activate(self):
        self.deactivated = False
        self.inactiveMask_slider.visible = False
        self.inactiveMask_button.visible = False

    def deactivate(self):
        self.deactivated = True
        if (self.hidden == False):
            self.inactiveMask_slider.visible = True
            self.inactiveMask_button.x = self.buttonSprite.x; self.inactiveMask_button.y = self.buttonSprite.y;
            self.inactiveMask_button.visible = True
            
    def setName(self, name): 
        self.name = name
    def getName(self): 
        return self.name
    def isTouched(self, mouseX, mouseY): 
        return (self.hitBox_slider.isTouched(mouseX, mouseY) or self.hitBox_button.isTouched(mouseX, mouseY))
    def isHidden(self): 
        return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        self.images['DEFAULT_SLIDER'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT_SLIDER'][1])
        self.images['HOVERED_SLIDER'] = self.imageManager.getImageByLoadIndex(self.images['HOVERED_SLIDER'][1])
        self.images['PRESSED_SLIDER'] = self.imageManager.getImageByLoadIndex(self.images['PRESSED_SLIDER'][1])
        self.images['DEFAULT_BUTTON'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT_BUTTON'][1])
        self.images['HOVERED_BUTTON'] = self.imageManager.getImageByLoadIndex(self.images['HOVERED_BUTTON'][1])
        self.images['PRESSED_BUTTON'] = self.imageManager.getImageByLoadIndex(self.images['PRESSED_BUTTON'][1])
        self.sliderSprite.image = self.images[self.status_slider+'_SLIDER'][0]
        self.buttonSprite.image = self.images[self.status_button+'_BUTTON'][0]
    def on_LanguageUpdate(self, **kwargs): 
        pass

    def getSliderValue(self): 
        return self.sliderValue

    def setSliderValue(self, newValue, callValueUpdateFunction = True):
        if ((0 <= newValue) and (newValue <= 100)):
            self.sliderValue = newValue
            self.__positionButton(newValue)
            if ((callValueUpdateFunction == True) and (self.valueUpdateFunction != None)): self.valueUpdateFunction(self)

    def __positionButton(self, posValue):
        if (self.align == 'horizontal'):
            x = self.buttonPos_0 + (posValue*self.railLength/100)
            self.buttonSprite.x        = x * self.scaler
            self.inactiveMask_button.x = x * self.scaler
            self.hitBox_button.reposition(xPos = x)
        elif (self.align == 'vertical'):
            y = self.buttonPos_0 + (posValue*self.railLength/100)
            self.buttonSprite.y        = y * self.scaler
            self.inactiveMask_button.y = y * self.scaler
            self.hitBox_button.reposition(yPos = y)

    def __calculateSliderValue(self, coordinate):
        sliderValue = (coordinate - self.buttonPos_0 - self.buttonSize/2) / self.railLength * 100
        if   (sliderValue < 0):   sliderValue = 0
        elif (100 < sliderValue): sliderValue = 100
        if (self.sliderValue != sliderValue): valueChanged = True
        else:                                 valueChanged = False
        self.sliderValue = round(sliderValue, 10)
        if ((self.valueUpdateFunction != None) and (valueChanged == True)): self.valueUpdateFunction(self)
        return self.sliderValue
        
    def getGroupRequirement(): 
        return 2
#GUIO - 'slider_typeA' END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'scrollBar_typeA' -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class scrollBar_typeA:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.group_2 = kwargs['group_2']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)
            self.group_2 = pyglet.graphics.Group(order = self.groupOrder+2)

        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.align = kwargs.get('align', 'horizontal');
        self.style = kwargs.get('style', 'styleA')
        self.text = kwargs.get('text', None); self.textStyle = kwargs.get('textStyle', None)

        if (self.align == 'horizontal'): self.hitBox_slider = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos, self.width, self.height)
        elif (self.align == 'vertical'): self.hitBox_slider = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos, self.height, self.width)
        self.hitBox_button = atmEta_gui_HitBoxes.hitBox_Rectangular(0, 0, 0, 0)

        #Functional Object Parameters
        self.hoverFunction       = kwargs.get('hoverFunction',       None)
        self.hoverEscapeFunction = kwargs.get('hoverEscapeFunction', None)
        self.pressFunction       = kwargs.get('pressFunction',       None)
        self.releaseFunction     = kwargs.get('releaseFunction',     None)
        self.viewRangeUpdateFunction = kwargs.get('viewRangeUpdateFunction', None)
        
        self.viewRange = kwargs.get('viewRange', [40, 60])
        
        self.buttonEdgeWidth      = int(self.height/2);                  self.buttonEdgeWidth_scaled      = int(self.buttonEdgeWidth*self.scaler)
        self.buttonBodyFullLength = self.width - self.buttonEdgeWidth*2; self.buttonBodyFullLength_scaled = int(self.buttonBodyFullLength*self.scaler)
        self.pressedPos_relToButtonCenter = None

        if (self.align == 'horizontal'):
            self.images = {'DEFAULT_FRAME':  self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_F_DEFAULT", self.width*self.scaler, self.height*self.scaler),
                           'HOVERED_FRAME':  self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_F_HOVERED", self.width*self.scaler, self.height*self.scaler),
                           'PRESSED_FRAME':  self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_F_PRESSED", self.width*self.scaler, self.height*self.scaler),
                           'DEFAULT_BUTTON': self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_B_DEFAULT", self.width*self.scaler, self.height*self.scaler),
                           'HOVERED_BUTTON': self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_B_HOVERED", self.width*self.scaler, self.height*self.scaler),
                           'PRESSED_BUTTON': self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_B_PRESSED", self.width*self.scaler, self.height*self.scaler),
                           'INACTIVEMASK': self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler)}
            self.buttonImages = {'DEFAULT_EDGE_EL': pyglet.image.ImageDataRegion(0,                                                                    0, self.buttonEdgeWidth_scaled,      self.images['DEFAULT_BUTTON'][0].height, self.images['DEFAULT_BUTTON'][0]),
                                 'DEFAULT_EDGE_EH': pyglet.image.ImageDataRegion(self.images['DEFAULT_BUTTON'][0].width - self.buttonEdgeWidth_scaled, 0, self.buttonEdgeWidth_scaled,      self.images['DEFAULT_BUTTON'][0].height, self.images['DEFAULT_BUTTON'][0]),
                                 'DEFAULT_EDGE_B':  pyglet.image.ImageDataRegion(self.buttonEdgeWidth_scaled,                                          0, self.buttonBodyFullLength_scaled, self.images['DEFAULT_BUTTON'][0].height, self.images['DEFAULT_BUTTON'][0]),
                                 'HOVERED_EDGE_EL': pyglet.image.ImageDataRegion(0,                                                                    0, self.buttonEdgeWidth_scaled,      self.images['HOVERED_BUTTON'][0].height, self.images['HOVERED_BUTTON'][0]),
                                 'HOVERED_EDGE_EH': pyglet.image.ImageDataRegion(self.images['DEFAULT_BUTTON'][0].width - self.buttonEdgeWidth_scaled, 0, self.buttonEdgeWidth_scaled,      self.images['HOVERED_BUTTON'][0].height, self.images['HOVERED_BUTTON'][0]),
                                 'HOVERED_EDGE_B':  pyglet.image.ImageDataRegion(self.buttonEdgeWidth_scaled,                                          0, self.buttonBodyFullLength_scaled, self.images['HOVERED_BUTTON'][0].height, self.images['HOVERED_BUTTON'][0]),
                                 'PRESSED_EDGE_EL': pyglet.image.ImageDataRegion(0,                                                                    0, self.buttonEdgeWidth_scaled,      self.images['PRESSED_BUTTON'][0].height, self.images['PRESSED_BUTTON'][0]),
                                 'PRESSED_EDGE_EH': pyglet.image.ImageDataRegion(self.images['DEFAULT_BUTTON'][0].width - self.buttonEdgeWidth_scaled, 0, self.buttonEdgeWidth_scaled,      self.images['PRESSED_BUTTON'][0].height, self.images['PRESSED_BUTTON'][0]),
                                 'PRESSED_EDGE_B':  pyglet.image.ImageDataRegion(self.buttonEdgeWidth_scaled,                                          0, self.buttonBodyFullLength_scaled, self.images['PRESSED_BUTTON'][0].height, self.images['PRESSED_BUTTON'][0]),
                                 'DEFAULT_COMBINED': None, 'HOVERED_COMBINED': None, 'PRESSED_COMBINED': None}

        elif (self.align == 'vertical'):
            self.images = {'DEFAULT_FRAME':  self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_F_DEFAULT", self.height*self.scaler, self.width*self.scaler),
                           'HOVERED_FRAME':  self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_F_HOVERED", self.height*self.scaler, self.width*self.scaler),
                           'PRESSED_FRAME':  self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_F_PRESSED", self.height*self.scaler, self.width*self.scaler),
                           'DEFAULT_BUTTON': self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_B_DEFAULT", self.height*self.scaler, self.width*self.scaler),
                           'HOVERED_BUTTON': self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_B_HOVERED", self.height*self.scaler, self.width*self.scaler),
                           'PRESSED_BUTTON': self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_B_PRESSED", self.height*self.scaler, self.width*self.scaler),
                           'INACTIVEMASK': self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_INACTIVEMASK", self.height*self.scaler, self.width*self.scaler)}
            self.buttonImages = {'DEFAULT_EDGE_EL': pyglet.image.ImageDataRegion(0, 0,                                                                     self.images['DEFAULT_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['DEFAULT_BUTTON'][0]),
                                 'DEFAULT_EDGE_EH': pyglet.image.ImageDataRegion(0, self.images['DEFAULT_BUTTON'][0].height - self.buttonEdgeWidth_scaled, self.images['DEFAULT_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['DEFAULT_BUTTON'][0]),
                                 'DEFAULT_EDGE_B':  pyglet.image.ImageDataRegion(0, self.buttonEdgeWidth_scaled,                                           self.images['DEFAULT_BUTTON'][0].width, self.buttonBodyFullLength_scaled, self.images['DEFAULT_BUTTON'][0]),
                                 'HOVERED_EDGE_EL': pyglet.image.ImageDataRegion(0, 0,                                                                     self.images['HOVERED_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['HOVERED_BUTTON'][0]),
                                 'HOVERED_EDGE_EH': pyglet.image.ImageDataRegion(0, self.images['HOVERED_BUTTON'][0].height - self.buttonEdgeWidth_scaled, self.images['HOVERED_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['HOVERED_BUTTON'][0]),
                                 'HOVERED_EDGE_B':  pyglet.image.ImageDataRegion(0, self.buttonEdgeWidth_scaled,                                           self.images['HOVERED_BUTTON'][0].width, self.buttonBodyFullLength_scaled, self.images['HOVERED_BUTTON'][0]),
                                 'PRESSED_EDGE_EL': pyglet.image.ImageDataRegion(0, 0,                                                                     self.images['PRESSED_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['PRESSED_BUTTON'][0]),
                                 'PRESSED_EDGE_EH': pyglet.image.ImageDataRegion(0, self.images['PRESSED_BUTTON'][0].height - self.buttonEdgeWidth_scaled, self.images['PRESSED_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['PRESSED_BUTTON'][0]),
                                 'PRESSED_EDGE_B':  pyglet.image.ImageDataRegion(0, self.buttonEdgeWidth_scaled,                                           self.images['PRESSED_BUTTON'][0].width, self.buttonBodyFullLength_scaled, self.images['PRESSED_BUTTON'][0]),
                                 'DEFAULT_COMBINED': None, 'HOVERED_COMBINED': None, 'PRESSED_COMBINED': None}
        
        self.frameSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler,  img = self.images['DEFAULT_FRAME'][0],  batch = self.batch, group = self.group_0)
        if (self.align == 'horizontal'): self.buttonSprite = pyglet.sprite.Sprite(x = self.xPos*self.scaler, y = self.yPos*self.scaler, img = self.images['DEFAULT_BUTTON'][0], batch = self.batch, group = self.group_1)
        elif (self.align == 'vertical'): self.buttonSprite = pyglet.sprite.Sprite(x = self.xPos*self.scaler, y = self.yPos*self.scaler, img = self.images['DEFAULT_BUTTON'][0], batch = self.batch, group = self.group_1)
        self.inactiveMask = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['INACTIVEMASK'][0], batch = self.batch, group = self.group_2); self.inactiveMask.visible = False

        self.status = "DEFAULT"; self.status_frame = "DEFAULT"; self.status_button = "DEFAULT"
        self.hidden = False; self.deactivated = False

        self.__positionButton()

    def process(self, t_elapsed_ns): pass

    def handleMouseEvent(self, event):
        if not((self.deactivated == True) or (self.hidden)):
            if (event['eType'] == "HOVERENTERED"):
                self.status = "HOVERED"
                if (self.hitBox_slider.isTouched(event['x'], event['y']) == True):
                    self.audioManager.playAudioByCode('scrollBar_typeA_HOVERED_A')
                    self.frameSprite.image = self.images[self.status+"_FRAME"][0]; self.status_frame = "HOVERED"
                if (self.hoverFunction != None): self.hoverFunction(self)
                
            elif (event['eType'] == "HOVERESCAPED"):
                self.status = "DEFAULT"
                self.frameSprite.image = self.images[self.status+"_FRAME"][0]; self.status_frame = "DEFAULT"
                self.buttonSprite.image = self.buttonImages[self.status+"_COMBINED"]
                self.status_button = "DEFAULT"

            elif (event['eType'] == "PRESSED"):
                self.audioManager.playAudioByCode('scrollBar_typeA_PRESSED_A')
                self.status = "PRESSED"
                self.frameSprite.image = self.images[self.status+"_FRAME"][0]; self.status_frame = "PRESSED"
                self.buttonSprite.image = self.buttonImages[self.status+"_COMBINED"]
                self.status_button = "PRESSED"
                previousViewRange = (self.viewRange[0], self.viewRange[1])
                self.__calculateViewRange(event['x'], event['y'])
                if ((previousViewRange[0] != self.viewRange[0]) or (previousViewRange[1] != self.viewRange[1])):
                    self.__positionButton()
                    if (self.viewRangeUpdateFunction != None): self.viewRangeUpdateFunction(self)
                    if (self.pressFunction != None): self.pressFunction(self)
                
            elif (event['eType'] == "RELEASED"):
                if (self.status == 'PRESSED'):
                    sliderTouched = self.hitBox_slider.isTouched(event['x'], event['y'])
                    buttonTouched = self.hitBox_button.isTouched(event['x'], event['y'])
                    self.audioManager.playAudioByCode('scrollBar_typeA_RELEASED_A')
                    if (sliderTouched == True):
                        self.status       = "HOVERED"
                        self.status_frame = 'HOVERED'
                        if (buttonTouched == True): self.status_button = 'HOVERED'
                        else:                       self.status_button = 'DEFAULT'
                    else:
                        self.status        = 'DEFAULT'
                        self.status_frame  = 'DEFAULT'
                        self.status_button = 'DEFAULT'
                    self.frameSprite.image  = self.images[self.status_frame+"_FRAME"][0]
                    self.buttonSprite.image = self.buttonImages[self.status_button+"_COMBINED"]
                    if (self.releaseFunction != None): self.releaseFunction(self)
                
            elif (event['eType'] == "DRAGGED"):
                if (self.status == "PRESSED"):
                    previousViewRange = (self.viewRange[0], self.viewRange[1])
                    self.__calculateViewRange(event['x'], event['y'], dragged = True)
                    if ((previousViewRange[0] != self.viewRange[0]) or (previousViewRange[1] != self.viewRange[1])):
                        self.__positionButton()
                        if (self.viewRangeUpdateFunction != None): self.viewRangeUpdateFunction(self)

            elif (event['eType'] == "MOVED"):
                buttonTouched = self.hitBox_button.isTouched(event['x'], event['y'])
                if ((buttonTouched == True)  and (self.status_button == "DEFAULT")): 
                    self.buttonSprite.image = self.buttonImages["HOVERED_COMBINED"]
                    self.status_button = "HOVERED"
                elif ((buttonTouched == False) and (self.status_button == "HOVERED")): 
                    self.buttonSprite.image = self.buttonImages["DEFAULT_COMBINED"]
                    self.status_button = "DEFAULT"

    def handleKeyEvent(self, event): pass

    def show(self):
        self.hidden = False
        self.frameSprite.visible = True
        self.buttonSprite.visible = True
        if (self.deactivated == True): self.inactiveMask.visible = True

    def hide(self):
        self.hidden = True
        self.frameSprite.visible = False
        self.buttonSprite.visible = False
        self.inactiveMask.visible = False

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y
        self.frameSprite.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.frameSprite.z)
        if (self.align == 'horizontal'): 
            self.buttonSprite.position = ((self.xPos+self.buttonBodyFullLength*self.viewRange[0]/100)*self.scaler, self.yPos*self.scaler, self.buttonSprite.z)
            self.hitBox_button.reposition(xPos = self.buttonSprite.x/self.scaler, yPos = self.yPos)
        elif (self.align == 'vertical'): 
            self.buttonSprite.position = (self.xPos*self.scaler, (self.yPos+self.buttonBodyFullLength*self.viewRange[0]/100)*self.scaler, self.buttonSprite.z)
            self.hitBox_button.reposition(xPos = self.xPos, yPos = self.buttonSprite.y/self.scaler)
        self.inactiveMask.position = (self.frameSprite.x, self.frameSprite.y, self.frameSprite.z)
        self.hitBox_slider.reposition(xPos = self.xPos, yPos = self.yPos)

    def resize(self, width, height):
        self.width = width; self.height = height
        self.buttonEdgeWidth      = int(self.height/2);                  self.buttonEdgeWidth_scaled      = int(self.buttonEdgeWidth*self.scaler)
        self.buttonBodyFullLength = self.width - self.buttonEdgeWidth*2; self.buttonBodyFullLength_scaled = int(self.buttonBodyFullLength*self.scaler)
        if (self.align == 'horizontal'):
            self.images['DEFAULT_FRAME']  = self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_F_DEFAULT",    self.width*self.scaler, self.height*self.scaler)
            self.images['HOVERED_FRAME']  = self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_F_HOVERED",    self.width*self.scaler, self.height*self.scaler)
            self.images['PRESSED_FRAME']  = self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_F_PRESSED",    self.width*self.scaler, self.height*self.scaler)
            self.images['DEFAULT_BUTTON'] = self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_B_DEFAULT",    self.width*self.scaler, self.height*self.scaler)
            self.images['HOVERED_BUTTON'] = self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_B_HOVERED",    self.width*self.scaler, self.height*self.scaler)
            self.images['PRESSED_BUTTON'] = self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_B_PRESSED",    self.width*self.scaler, self.height*self.scaler)
            self.images['INACTIVEMASK']   = self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler)
            self.buttonImages['DEFAULT_EDGE_EL']  = pyglet.image.ImageDataRegion(0,                                                                    0, self.buttonEdgeWidth_scaled,      self.images['DEFAULT_BUTTON'][0].height, self.images['DEFAULT_BUTTON'][0])
            self.buttonImages['DEFAULT_EDGE_EH']  = pyglet.image.ImageDataRegion(self.images['DEFAULT_BUTTON'][0].width - self.buttonEdgeWidth_scaled, 0, self.buttonEdgeWidth_scaled,      self.images['DEFAULT_BUTTON'][0].height, self.images['DEFAULT_BUTTON'][0])
            self.buttonImages['DEFAULT_EDGE_B']   = pyglet.image.ImageDataRegion(self.buttonEdgeWidth_scaled,                                          0, self.buttonBodyFullLength_scaled, self.images['DEFAULT_BUTTON'][0].height, self.images['DEFAULT_BUTTON'][0])
            self.buttonImages['HOVERED_EDGE_EL']  = pyglet.image.ImageDataRegion(0,                                                                    0, self.buttonEdgeWidth_scaled,      self.images['HOVERED_BUTTON'][0].height, self.images['HOVERED_BUTTON'][0])
            self.buttonImages['HOVERED_EDGE_EH']  = pyglet.image.ImageDataRegion(self.images['DEFAULT_BUTTON'][0].width - self.buttonEdgeWidth_scaled, 0, self.buttonEdgeWidth_scaled,      self.images['HOVERED_BUTTON'][0].height, self.images['HOVERED_BUTTON'][0])
            self.buttonImages['HOVERED_EDGE_B']   = pyglet.image.ImageDataRegion(self.buttonEdgeWidth_scaled,                                          0, self.buttonBodyFullLength_scaled, self.images['HOVERED_BUTTON'][0].height, self.images['HOVERED_BUTTON'][0])
            self.buttonImages['PRESSED_EDGE_EL']  = pyglet.image.ImageDataRegion(0,                                                                    0, self.buttonEdgeWidth_scaled,      self.images['PRESSED_BUTTON'][0].height, self.images['PRESSED_BUTTON'][0])
            self.buttonImages['PRESSED_EDGE_EH']  = pyglet.image.ImageDataRegion(self.images['DEFAULT_BUTTON'][0].width - self.buttonEdgeWidth_scaled, 0, self.buttonEdgeWidth_scaled,      self.images['PRESSED_BUTTON'][0].height, self.images['PRESSED_BUTTON'][0])
            self.buttonImages['PRESSED_EDGE_B']   = pyglet.image.ImageDataRegion(self.buttonEdgeWidth_scaled,                                          0, self.buttonBodyFullLength_scaled, self.images['PRESSED_BUTTON'][0].height, self.images['PRESSED_BUTTON'][0])
            self.buttonImages['DEFAULT_COMBINED'] = None; self.buttonImages['HOVERED_COMBINED'] = None; self.buttonImages['PRESSED_COMBINED'] = None
        elif (self.align == 'vertical'):
            self.images['DEFAULT_FRAME']  = self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_F_DEFAULT",    self.height*self.scaler, self.width*self.scaler)
            self.images['HOVERED_FRAME']  = self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_F_HOVERED",    self.height*self.scaler, self.width*self.scaler)
            self.images['PRESSED_FRAME']  = self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_F_PRESSED",    self.height*self.scaler, self.width*self.scaler)
            self.images['DEFAULT_BUTTON'] = self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_B_DEFAULT",    self.height*self.scaler, self.width*self.scaler)
            self.images['HOVERED_BUTTON'] = self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_B_HOVERED",    self.height*self.scaler, self.width*self.scaler)
            self.images['PRESSED_BUTTON'] = self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_B_PRESSED",    self.height*self.scaler, self.width*self.scaler)
            self.images['INACTIVEMASK']   = self.imageManager.getImageByCode("scrollBar_typeA_"+self.style+"_INACTIVEMASK", self.height*self.scaler, self.width*self.scaler)
            self.buttonImages['DEFAULT_EDGE_EL']  = pyglet.image.ImageDataRegion(0, 0,                                                                     self.images['DEFAULT_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['DEFAULT_BUTTON'][0])
            self.buttonImages['DEFAULT_EDGE_EH']  = pyglet.image.ImageDataRegion(0, self.images['DEFAULT_BUTTON'][0].height - self.buttonEdgeWidth_scaled, self.images['DEFAULT_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['DEFAULT_BUTTON'][0])
            self.buttonImages['DEFAULT_EDGE_B']   = pyglet.image.ImageDataRegion(0, self.buttonEdgeWidth_scaled,                                           self.images['DEFAULT_BUTTON'][0].width, self.buttonBodyFullLength_scaled, self.images['DEFAULT_BUTTON'][0])
            self.buttonImages['HOVERED_EDGE_EL']  = pyglet.image.ImageDataRegion(0, 0,                                                                     self.images['HOVERED_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['HOVERED_BUTTON'][0])
            self.buttonImages['HOVERED_EDGE_EH']  = pyglet.image.ImageDataRegion(0, self.images['HOVERED_BUTTON'][0].height - self.buttonEdgeWidth_scaled, self.images['HOVERED_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['HOVERED_BUTTON'][0])
            self.buttonImages['HOVERED_EDGE_B']   = pyglet.image.ImageDataRegion(0, self.buttonEdgeWidth_scaled,                                           self.images['HOVERED_BUTTON'][0].width, self.buttonBodyFullLength_scaled, self.images['HOVERED_BUTTON'][0])
            self.buttonImages['PRESSED_EDGE_EL']  = pyglet.image.ImageDataRegion(0, 0,                                                                     self.images['PRESSED_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['PRESSED_BUTTON'][0])
            self.buttonImages['PRESSED_EDGE_EH']  = pyglet.image.ImageDataRegion(0, self.images['PRESSED_BUTTON'][0].height - self.buttonEdgeWidth_scaled, self.images['PRESSED_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['PRESSED_BUTTON'][0])
            self.buttonImages['PRESSED_EDGE_B']   = pyglet.image.ImageDataRegion(0, self.buttonEdgeWidth_scaled,                                           self.images['PRESSED_BUTTON'][0].width, self.buttonBodyFullLength_scaled, self.images['PRESSED_BUTTON'][0])
            self.buttonImages['DEFAULT_COMBINED'] = None; self.buttonImages['HOVERED_COMBINED'] = None; self.buttonImages['PRESSED_COMBINED'] = None
        self.frameSprite.image  = self.images[self.status+'_FRAME'][0]
        self.inactiveMask.image = self.images['INACTIVEMASK'][0]
        if (self.align == 'horizontal'): self.hitBox_slider.resize(width = self.width,  height = self.height)
        elif (self.align == 'vertical'): self.hitBox_slider.resize(width = self.height, height = self.width)
        self.__positionButton()

    def activate(self):
        self.deactivated = False
        self.inactiveMask.visible = False

    def deactivate(self):
        self.deactivated = True
        if (self.hidden == False): self.inactiveMask.visible = True

    def getViewRange(self, asInverse = False): 
        if (asInverse == True): return (100-self.viewRange[1], 100-self.viewRange[0])
        else:                   return (self.viewRange[0],     self.viewRange[1])

    def editViewRange(self, viewRange, asInverse = False):
        if (((0 <= viewRange[0]) and (viewRange[0] <= 100)) and ((0 <= viewRange[1]) and (viewRange[1] <= 100)) and (viewRange[0] <= viewRange[1])):
            if (asInverse == True): newViewRange = [round(100 - viewRange[1], 3), round(100 - viewRange[0], 3)]
            else:                   newViewRange = [round(viewRange[0], 3),       round(viewRange[1], 3)]
            if ((newViewRange[0] != self.viewRange[0]) or (newViewRange[1] != self.viewRange[1])):
                self.viewRange = [newViewRange[0], newViewRange[1]]
                self.__positionButton()
                
    def setName(self, name): self.name = name
    def getName(self): return self.name
    def isTouched(self, mouseX, mouseY): return (self.hitBox_slider.isTouched(mouseX, mouseY) or self.hitBox_button.isTouched(mouseX, mouseY))
    def isHidden(self): return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        self.images['DEFAULT_FRAME']  = self.imageManager.getImageByLoadIndex(self.images['DEFAULT_FRAME'][1])
        self.images['HOVERED_FRAME']  = self.imageManager.getImageByLoadIndex(self.images['HOVERED_FRAME'][1])
        self.images['PRESSED_FRAME']  = self.imageManager.getImageByLoadIndex(self.images['PRESSED_FRAME'][1])
        self.images['DEFAULT_BUTTON'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT_BUTTON'][1])
        self.images['HOVERED_BUTTON'] = self.imageManager.getImageByLoadIndex(self.images['HOVERED_BUTTON'][1])
        self.images['PRESSED_BUTTON'] = self.imageManager.getImageByLoadIndex(self.images['PRESSED_BUTTON'][1])
        self.frameSprite.image  = self.images[self.status_frame+'_FRAME'][0]
        self.buttonSprite.image = self.images[self.status_button+'_BUTTON'][0]
        if (self.align == 'horizontal'):
            self.buttonImages = {'DEFAULT_EDGE_EL': pyglet.image.ImageDataRegion(0,                                                                    0, self.buttonEdgeWidth_scaled,      self.images['DEFAULT_BUTTON'][0].height, self.images['DEFAULT_BUTTON'][0]),
                                 'DEFAULT_EDGE_EH': pyglet.image.ImageDataRegion(self.images['DEFAULT_BUTTON'][0].width - self.buttonEdgeWidth_scaled, 0, self.buttonEdgeWidth_scaled,      self.images['DEFAULT_BUTTON'][0].height, self.images['DEFAULT_BUTTON'][0]),
                                 'DEFAULT_EDGE_B':  pyglet.image.ImageDataRegion(self.buttonEdgeWidth_scaled,                                          0, self.buttonBodyFullLength_scaled, self.images['DEFAULT_BUTTON'][0].height, self.images['DEFAULT_BUTTON'][0]),
                                 'HOVERED_EDGE_EL': pyglet.image.ImageDataRegion(0,                                                                    0, self.buttonEdgeWidth_scaled,      self.images['HOVERED_BUTTON'][0].height, self.images['HOVERED_BUTTON'][0]),
                                 'HOVERED_EDGE_EH': pyglet.image.ImageDataRegion(self.images['DEFAULT_BUTTON'][0].width - self.buttonEdgeWidth_scaled, 0, self.buttonEdgeWidth_scaled,      self.images['HOVERED_BUTTON'][0].height, self.images['HOVERED_BUTTON'][0]),
                                 'HOVERED_EDGE_B':  pyglet.image.ImageDataRegion(self.buttonEdgeWidth_scaled,                                          0, self.buttonBodyFullLength_scaled, self.images['HOVERED_BUTTON'][0].height, self.images['HOVERED_BUTTON'][0]),
                                 'PRESSED_EDGE_EL': pyglet.image.ImageDataRegion(0,                                                                    0, self.buttonEdgeWidth_scaled,      self.images['PRESSED_BUTTON'][0].height, self.images['PRESSED_BUTTON'][0]),
                                 'PRESSED_EDGE_EH': pyglet.image.ImageDataRegion(self.images['DEFAULT_BUTTON'][0].width - self.buttonEdgeWidth_scaled, 0, self.buttonEdgeWidth_scaled,      self.images['PRESSED_BUTTON'][0].height, self.images['PRESSED_BUTTON'][0]),
                                 'PRESSED_EDGE_B':  pyglet.image.ImageDataRegion(self.buttonEdgeWidth_scaled,                                          0, self.buttonBodyFullLength_scaled, self.images['PRESSED_BUTTON'][0].height, self.images['PRESSED_BUTTON'][0]),
                                 'DEFAULT_COMBINED': None, 'HOVERED_COMBINED': None, 'PRESSED_COMBINED': None}
        elif (self.align == 'vertical'):
            self.buttonImages = {'DEFAULT_EDGE_EL': pyglet.image.ImageDataRegion(0, 0,                                                                     self.images['DEFAULT_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['DEFAULT_BUTTON'][0]),
                                 'DEFAULT_EDGE_EH': pyglet.image.ImageDataRegion(0, self.images['DEFAULT_BUTTON'][0].height - self.buttonEdgeWidth_scaled, self.images['DEFAULT_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['DEFAULT_BUTTON'][0]),
                                 'DEFAULT_EDGE_B':  pyglet.image.ImageDataRegion(0, self.buttonEdgeWidth_scaled,                                           self.images['DEFAULT_BUTTON'][0].width, self.buttonBodyFullLength_scaled, self.images['DEFAULT_BUTTON'][0]),
                                 'HOVERED_EDGE_EL': pyglet.image.ImageDataRegion(0, 0,                                                                     self.images['HOVERED_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['HOVERED_BUTTON'][0]),
                                 'HOVERED_EDGE_EH': pyglet.image.ImageDataRegion(0, self.images['HOVERED_BUTTON'][0].height - self.buttonEdgeWidth_scaled, self.images['HOVERED_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['HOVERED_BUTTON'][0]),
                                 'HOVERED_EDGE_B':  pyglet.image.ImageDataRegion(0, self.buttonEdgeWidth_scaled,                                           self.images['HOVERED_BUTTON'][0].width, self.buttonBodyFullLength_scaled, self.images['HOVERED_BUTTON'][0]),
                                 'PRESSED_EDGE_EL': pyglet.image.ImageDataRegion(0, 0,                                                                     self.images['PRESSED_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['PRESSED_BUTTON'][0]),
                                 'PRESSED_EDGE_EH': pyglet.image.ImageDataRegion(0, self.images['PRESSED_BUTTON'][0].height - self.buttonEdgeWidth_scaled, self.images['PRESSED_BUTTON'][0].width, self.buttonEdgeWidth_scaled,      self.images['PRESSED_BUTTON'][0]),
                                 'PRESSED_EDGE_B':  pyglet.image.ImageDataRegion(0, self.buttonEdgeWidth_scaled,                                           self.images['PRESSED_BUTTON'][0].width, self.buttonBodyFullLength_scaled, self.images['PRESSED_BUTTON'][0]),
                                 'DEFAULT_COMBINED': None, 'HOVERED_COMBINED': None, 'PRESSED_COMBINED': None}
        self.__positionButton()

    def on_LanguageUpdate(self, **kwargs): pass

    def __positionButton(self):
        if (self.align == 'horizontal'):
            bodyWidth = round(self.buttonBodyFullLength * (self.viewRange[1] - self.viewRange[0]) / 100); bodyWidth_scaled = round(self.buttonBodyFullLength_scaled * (self.viewRange[1] - self.viewRange[0]) / 100)
            self.currentButtonBodyWidth = bodyWidth
            for mode in ('DEFAULT', 'HOVERED', 'PRESSED'):
                self.buttonImages[mode+'_COMBINED'] = pyglet.image.Texture.create(bodyWidth_scaled+self.buttonEdgeWidth_scaled*2, self.images[mode+'_BUTTON'][0].height)
                self.buttonImages[mode+'_EDGE_B'] = pyglet.image.ImageDataRegion(self.buttonEdgeWidth_scaled, 0, bodyWidth_scaled, self.images[mode+'_BUTTON'][0].height, self.images[mode+'_BUTTON'][0])
                self.buttonImages[mode+'_COMBINED'].blit_into(source = self.buttonImages[mode+'_EDGE_EL'], x = 0,                                              y = 0, z = 0)
                self.buttonImages[mode+'_COMBINED'].blit_into(source = self.buttonImages[mode+'_EDGE_B'],  x = self.buttonEdgeWidth_scaled,                    y = 0, z = 0)
                self.buttonImages[mode+'_COMBINED'].blit_into(source = self.buttonImages[mode+'_EDGE_EH'], x = self.buttonEdgeWidth_scaled + bodyWidth_scaled, y = 0, z = 0)
            self.buttonSprite.image = self.buttonImages[self.status+'_COMBINED']
            xPosition = self.xPos+self.buttonBodyFullLength*self.viewRange[0]/100
            self.buttonSprite.x = xPosition*self.scaler
            self.hitBox_button.reposition(xPos = xPosition, yPos = self.yPos)
            self.hitBox_button.resize(width = bodyWidth+self.buttonEdgeWidth*2, height = self.height)

        elif (self.align == 'vertical'):
            bodyWidth = round(self.buttonBodyFullLength * (self.viewRange[1] - self.viewRange[0]) / 100); bodyWidth_scaled = round(self.buttonBodyFullLength_scaled * (self.viewRange[1] - self.viewRange[0]) / 100)
            self.currentButtonBodyWidth = bodyWidth
            for mode in ('DEFAULT', 'HOVERED', 'PRESSED'):
                self.buttonImages[mode+'_COMBINED'] = pyglet.image.Texture.create(self.images[mode+'_BUTTON'][0].width, bodyWidth_scaled+self.buttonEdgeWidth_scaled*2)
                self.buttonImages[mode+'_EDGE_B'] = pyglet.image.ImageDataRegion(0, self.buttonEdgeWidth_scaled, self.images[mode+'_BUTTON'][0].width, bodyWidth_scaled, self.images[mode+'_BUTTON'][0])
                self.buttonImages[mode+'_COMBINED'].blit_into(source = self.buttonImages[mode+'_EDGE_EL'], x = 0, y = 0,                                              z = 0)
                self.buttonImages[mode+'_COMBINED'].blit_into(source = self.buttonImages[mode+'_EDGE_B'],  x = 0, y = self.buttonEdgeWidth_scaled,                    z = 0)
                self.buttonImages[mode+'_COMBINED'].blit_into(source = self.buttonImages[mode+'_EDGE_EH'], x = 0, y = self.buttonEdgeWidth_scaled + bodyWidth_scaled, z = 0)
            self.buttonSprite.image = self.buttonImages[self.status+'_COMBINED']
            yPosition = self.yPos+self.buttonBodyFullLength*(self.viewRange[0])/100
            self.buttonSprite.y = yPosition*self.scaler
            self.hitBox_button.reposition(xPos = self.xPos, yPos = yPosition)
            self.hitBox_button.resize(width = self.height, height = bodyWidth+self.buttonEdgeWidth*2)

    def __calculateViewRange(self, mouseX, mouseY, dragged = False):
        if (dragged == True):
            if (self.align == 'horizontal'):
                viewRange0 = ((mouseX-self.currentButtonBodyWidth/2-self.buttonEdgeWidth-self.pressedPos_relToButtonCenter) - (self.xPos))                        / (self.buttonBodyFullLength) * 100
                viewRange1 = ((mouseX+self.currentButtonBodyWidth/2+self.buttonEdgeWidth-self.pressedPos_relToButtonCenter) - (self.xPos+self.buttonEdgeWidth*2)) / (self.buttonBodyFullLength) * 100
            elif (self.align == 'vertical'):
                viewRange0 = ((mouseY-self.currentButtonBodyWidth/2-self.buttonEdgeWidth-self.pressedPos_relToButtonCenter) - (self.yPos))                        / (self.buttonBodyFullLength) * 100
                viewRange1 = ((mouseY+self.currentButtonBodyWidth/2+self.buttonEdgeWidth-self.pressedPos_relToButtonCenter) - (self.yPos+self.buttonEdgeWidth*2)) / (self.buttonBodyFullLength) * 100
        else:
            if (self.align == 'horizontal'):
                if (self.hitBox_button.isTouched(mouseX, mouseY) == True):
                    viewRange0, viewRange1 = self.viewRange[0], self.viewRange[1]
                    self.pressedPos_relToButtonCenter = mouseX - (self.buttonSprite.x/self.scaler + self.currentButtonBodyWidth/2 + self.buttonEdgeWidth)
                else:
                    viewRange0 = ((mouseX-self.currentButtonBodyWidth/2-self.buttonEdgeWidth) - (self.xPos))                        / (self.buttonBodyFullLength) * 100
                    viewRange1 = ((mouseX+self.currentButtonBodyWidth/2+self.buttonEdgeWidth) - (self.xPos+self.buttonEdgeWidth*2)) / (self.buttonBodyFullLength) * 100
                    self.pressedPos_relToButtonCenter = 0
            elif (self.align == 'vertical'):
                if (self.hitBox_button.isTouched(mouseX, mouseY) == True):
                    viewRange0, viewRange1 = self.viewRange[0], self.viewRange[1]
                    self.pressedPos_relToButtonCenter = mouseY - (self.buttonSprite.y/self.scaler + self.currentButtonBodyWidth/2 + self.buttonEdgeWidth)
                else:
                    viewRange0 = ((mouseY-self.currentButtonBodyWidth/2-self.buttonEdgeWidth) - (self.yPos))                        / (self.buttonBodyFullLength) * 100
                    viewRange1 = ((mouseY+self.currentButtonBodyWidth/2+self.buttonEdgeWidth) - (self.yPos+self.buttonEdgeWidth*2)) / (self.buttonBodyFullLength) * 100
                    self.pressedPos_relToButtonCenter = 0
            
        if (viewRange0 < 0):   viewRange1 += 0 - viewRange0;   viewRange0 = 0
        if (100 < viewRange1): viewRange0 -= viewRange1 - 100; viewRange1 = 100
        self.viewRange = [round(viewRange0, 3), round(viewRange1, 3)]
        
    def getGroupRequirement(): return 2
#GUIO - 'scrollBar_typeA' END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'textInputBox_typeA' ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class textInputBox_typeA:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.group_2 = kwargs['group_2']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)
            self.group_2 = pyglet.graphics.Group(order = self.groupOrder+2)

        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.align = kwargs.get('horizontal', 0);
        self.style = kwargs.get('style', None)
        self.text = kwargs.get('text', "")
        self.fontSize = int(kwargs.get('fontSize', 100)*self.scaler)
        self.textStyle = kwargs.get('textStyle', 'default')
        self.effectiveTextStyle = self.visualManager.getTextStyle('textInputBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize

        self.hitBox = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos, self.width, self.height)

        #Functional Object Parameters
        self.hoverFunction       = kwargs.get('hoverFunction',       None)
        self.hoverEscapeFunction = kwargs.get('hoverEscapeFunction', None)
        self.pressFunction       = kwargs.get('pressFunction',       None)
        self.releaseFunction     = kwargs.get('releaseFunction',     None)
        self.textUpdateFunction = kwargs.get('textUpdateFunction', None)

        if (self.style == None):
            self.images = {'INACTIVEMASK': self.imageManager.getImageByCode("textInputBox_typeA_RAW_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler)}
            self.textElement = atmEta_gui_TextControl.textObject_SL_IE(scaler = self.scaler, batch = self.batch, group = self.group_1, 
                                                                         text = self.visualManager.extractText(self.text), defaultTextStyle = self.effectiveTextStyle['DEFAULT'],
                                                                         xPos = self.xPos, yPos = self.yPos, width = self.width, height = self.height, showElementBox = False, anchor = 'W',
                                                                         textUpdateFunction = self.__onTextUpdate)
            self.inactiveMask = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['INACTIVEMASK'][0], batch = self.batch, group = self.group_2); self.inactiveMask.visible = False
        else:
            self.images = {'DEFAULT': self.imageManager.getImageByCode("textInputBox_typeA_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler),
                           'HOVERED': self.imageManager.getImageByCode("textInputBox_typeA_"+self.style+"_HOVERED", self.width*self.scaler, self.height*self.scaler),
                           'PRESSED': self.imageManager.getImageByCode("textInputBox_typeA_"+self.style+"_PRESSED", self.width*self.scaler, self.height*self.scaler),
                           'INACTIVEMASK': self.imageManager.getImageByCode("textInputBox_typeA_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler)}
            self.frameSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT'][0], batch = self.batch, group = self.group_0)
            if (self.style == 'styleA'): self.gOffsetX = self.height/4; self.gOffsetY = self.height/10
            self.textElement = atmEta_gui_TextControl.textObject_SL_IE(scaler = self.scaler, batch = self.batch, group = self.group_1, 
                                                                         text = self.visualManager.extractText(self.text), defaultTextStyle = self.effectiveTextStyle['DEFAULT'],
                                                                         xPos = self.xPos+self.gOffsetX, yPos = self.yPos+self.gOffsetY, width = self.width-self.gOffsetX*2, height = self.height-self.gOffsetY*2, showElementBox = False, anchor = 'W',
                                                                         textUpdateFunction = self.__onTextUpdate)
            self.inactiveMask = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['INACTIVEMASK'][0], batch = self.batch, group = self.group_2); self.inactiveMask.visible = False

        #Object Graphics Control Variables
        self.status = "DEFAULT"; self.focused = False
        self.deactivated = False; self.hidden = False

    def process(self, t_elapsed_ns):
        processResult = self.textElement.process(t_elapsed_ns)
        if   (processResult == 'textUpdated'):      self.audioManager.playAudioByCode('textInputBox_typeA_TEXTEDITED_A')
        elif (processResult == 'selectionUpdated'): self.audioManager.playAudioByCode('textInputBox_typeA_POSMOVED_A')

    def handleMouseEvent(self, event):
        if not((self.deactivated == True) or (self.hidden)):
            handlerResult = self.textElement.handleMouseEvent(event)
            if (event['eType'] == "HOVERENTERED"):
                if (self.focused == False):
                    self.audioManager.playAudioByCode('textInputBox_typeA_HOVERED_A')
                    self.status = "HOVERED"
                    if (self.style != None): self.frameSprite.image = self.images[self.status][0]
                    if (self.hoverFunction != None): self.hoverFunction(self)
            elif (event['eType'] == "HOVERESCAPED"):
                if (self.focused == False):
                    self.status = "DEFAULT"
                    if (self.style != None): self.frameSprite.image = self.images[self.status][0]
            elif (event['eType'] == "PRESSED"):
                self.audioManager.playAudioByCode('textInputBox_typeA_PRESSED_A')
                self.status = "PRESSED"
                if (self.style != None): self.frameSprite.image = self.images[self.status][0]
                if (self.pressFunction != None): self.pressFunction(self)
            elif (event['eType'] == "RELEASED"):
                if (self.status == "PRESSED"):
                    self.audioManager.playAudioByCode('textInputBox_typeA_RELEASED_A')
                    if (self.releaseFunction != None): self.releaseFunction(self)
                    self.focused = True
            elif (event['eType'] == "DRAGGED"):
                if (handlerResult == 'selectionUpdated'):
                    self.audioManager.playAudioByCode('textInputBox_typeA_POSMOVED_A')
            elif (event['eType'] == "SELECTIONESCAPED"):
                self.status = "DEFAULT"
                if (self.style != None): self.frameSprite.image = self.images[self.status][0]
                self.focused = False

    def handleKeyEvent(self, event):
        if not((self.deactivated == True) or (self.hidden == True)):
            if (event['eType'] == "SELECTIONESCAPED"):
                self.status = "DEFAULT"
                if (self.style != None): self.frameSprite.image = self.images[self.status][0]
                self.focused = False
            handlerResult = self.textElement.handleKeyEvent(event)
            if   (handlerResult == 'textUpdated'):      self.audioManager.playAudioByCode('textInputBox_typeA_TEXTEDITED_A')
            elif (handlerResult == 'selectionUpdated'): self.audioManager.playAudioByCode('textInputBox_typeA_POSMOVED_A')

    def show(self):
        self.hidden = False
        self.frameSprite.visible = True
        self.textElement.show()
        if (self.deactivated == True): self.inactiveMask.visible = True

    def hide(self):
        self.hidden = True
        self.frameSprite.visible = False
        self.textElement.hide()
        self.inactiveMask.visible = False

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y
        if (self.style == None): self.textElement.moveTo(x = self.xPos, y = self.yPos)
        else: 
            self.frameSprite.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.frameSprite.z)
            self.textElement.moveTo(x = self.xPos+self.gOffsetX, y = self.yPos+self.gOffsetY)
        self.inactiveMask.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.inactiveMask.z)
        self.hitBox.reposition(xPos = self.xPos, yPos = self.yPos)

    def resize(self, width, height):
        self.width = width; self.height = height
        if (self.style == None): self.textElement.changeSize(width = self.width, height = self.height)
        else:
            self.images['DEFAULT'] = self.imageManager.getImageByCode("textInputBox_typeA_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler)
            self.images['HOVERED'] = self.imageManager.getImageByCode("textInputBox_typeA_"+self.style+"_HOVERED", self.width*self.scaler, self.height*self.scaler)
            self.images['PRESSED'] = self.imageManager.getImageByCode("textInputBox_typeA_"+self.style+"_PRESSED", self.width*self.scaler, self.height*self.scaler)
            self.frameSprite.image = self.images[self.status][0]
            if (self.style == 'styleA'): self.gOffsetX = self.height/4; self.gOffsetY = self.height/10
            self.textElement.changeSize(width = self.width-self.gOffsetX*2, height = self.height-self.gOffsetY*2)
            self.textElement.moveTo(x = self.xPos+self.gOffsetX, y = self.yPos+self.gOffsetY)
        self.images['INACTIVEMASK'] = self.imageManager.getImageByCode("textInputBox_typeA_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler)
        self.inactiveMask.image = self.images['INACTIVEMASK'][0]
        self.hitBox.resize(width = self.width, height = self.height)

    def activate(self):
        self.deactivated = False
        self.inactiveMask.visible = False

    def deactivate(self):
        self.deactivated = True
        if (self.hidden == False): self.inactiveMask.visible = True
        
    def setName(self, name): self.name = name
    def getName(self): return self.name
    def isTouched(self, mouseX, mouseY): return self.hitBox.isTouched(mouseX, mouseY)
    def isHidden(self): return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        #Get the updated image and textStyle from the managers
        if (self.style != None):
            self.images['DEFAULT'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT'][1])
            self.images['HOVERED'] = self.imageManager.getImageByLoadIndex(self.images['HOVERED'][1])
            self.images['PRESSED'] = self.imageManager.getImageByLoadIndex(self.images['PRESSED'][1])
        self.effectiveTextStyle = self.visualManager.getTextStyle('textInputBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        #Apply the updated image and textStyle
        if (self.style != None): self.frameSprite.image = self.images[self.status][0]
        self.textElement.on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle[self.status])
    def on_LanguageUpdate(self, **kwargs):
        self.effectiveTextStyle = self.visualManager.getTextStyle('textInputBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        self.textElement.on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'])

    def updateText(self, text):
        self.textElement.setText(text)

    def getText(self):
        return self.textElement.getText()

    def __onTextUpdate(self, textElementInstance):
        if (self.textUpdateFunction != None): self.textUpdateFunction(self)
        
    def getGroupRequirement(): return 2
#GUIO - 'textInputBox_typeA' END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'LED_typeA' -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class LED_typeA:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)

        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.style = kwargs.get('style', 'styleA')

        #Functional Object Parameters
        self.images = {'DEFAULT': self.imageManager.getImageByCode("LED_typeA_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler),
                       'LED':     self.imageManager.getImageByCode("LED_typeA_"+self.style+"_LED",     self.width*self.scaler, self.height*self.scaler)}
        self.frameSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT'][0], batch = self.batch, group = self.group_0)
        self.LEDSprite   = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['LED'][0],     batch = self.batch, group = self.group_1)
        self.LEDColor = [0, 0, 0, 0]; self.LEDSprite.color = (self.LEDColor[0], self.LEDColor[1], self.LEDColor[2]); self.LEDSprite.opacity = self.LEDColor[3]

        self.mode = kwargs.get('mode', False)
        self.hidden = False

        self.setMode(self.mode)

    def process(self, t_elapsed_ns): pass

    def handleMouseEvent(self, event): pass
    def handleKeyEvent(self, event): pass

    def show(self):
        self.hidden = False
        self.frameSprite.visible = True
        if (self.mode == True): self.LEDSprite.visible = True

    def hide(self):
        self.hidden = True
        self.frameSprite.visible = False
        self.LEDSprite.visible = False

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y
        self.frameSprite.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.frameSprite.z)
        self.LEDSprite.position   = (self.xPos*self.scaler, self.yPos*self.scaler, self.LEDSprite.z)

    def resize(self, width, height):
        self.width = width; self.height = height
        self.images['DEFAULT'] = self.imageManager.getImageByCode("LED_typeA_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler)
        self.images['LED']     = self.imageManager.getImageByCode("LED_typeA_"+self.style+"_LED",     self.width*self.scaler, self.height*self.scaler)
        self.frameSprite.image = self.images['DEFAULT'][0]
        self.LEDSprite.image   = self.images['LED'][0]

    def setMode(self, mode = 'toggle'):
        if (mode == True):
            self.mode = True
            if (self.hidden == False): self.LEDSprite.visible = True
        elif (mode == False):
            self.mode = False
            if (self.hidden == False): self.LEDSprite.visible = False
        elif (mode == 'toggle'):
            self.mode = not(self.mode)
            if (self.hidden == False): 
                if   (self.mode == True):  self.LEDSprite.visible = True
                elif (self.mode == False): self.LEDSprite.visible = False
                
    def setName(self, name): self.name = name
    def getName(self): return self.name
    def isTouched(self, mouseX, mouseY): return False
    def isHidden(self): return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        self.images['DEFAULT'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT'][1])
        self.images['LED']     = self.imageManager.getImageByLoadIndex(self.images['LED'][1])
        self.frameSprite.image = self.images['DEFAULT'][0]
        self.LEDSprite.image   = self.images['LED'][0]
        self.LEDSprite.color = (self.LEDColor[0], self.LEDColor[1], self.LEDColor[2]); self.LEDSprite.opacity = self.LEDColor[3]
    def on_LanguageUpdate(self, **kwargs): pass

    def updateColor(self, rValue = None, gValue = None, bValue = None, aValue = None):
        if ((rValue != None) and (0 <= rValue) and (rValue <= 255)): self.LEDColor[0] = rValue
        if ((gValue != None) and (0 <= gValue) and (gValue <= 255)): self.LEDColor[1] = gValue
        if ((bValue != None) and (0 <= bValue) and (bValue <= 255)): self.LEDColor[2] = bValue
        if ((aValue != None) and (0 <= aValue) and (aValue <= 255)): self.LEDColor[3] = aValue
        self.LEDSprite.color = (self.LEDColor[0], self.LEDColor[1], self.LEDColor[2]); self.LEDSprite.opacity = self.LEDColor[3]

    def getColor(self): return self.LEDColor
        
    def getGroupRequirement(): return 1
#GUIO - 'LED_typeA' END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'gaugeBar_typeA' --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class gaugeBar_typeA:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)

        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.align = kwargs.get('align', 'horizontal')
        self.style = kwargs.get('style', None)

        #Functional Object Parameters
        if (self.align == 'horizontal'):
            self.images = {'DEFAULT': self.imageManager.getImageByCode("gaugeBar_typeA_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler),
                           'GAUGE':   self.imageManager.getImageByCode("gaugeBar_typeA_"+self.style+"_GAUGE",   self.width*self.scaler, self.height*self.scaler)}
        elif (self.align == 'vertical'):
            self.images = {'DEFAULT': self.imageManager.getImageByCode("gaugeBar_typeA_"+self.style+"_DEFAULT", self.height*self.scaler, self.width*self.scaler),
                           'GAUGE':   self.imageManager.getImageByCode("gaugeBar_typeA_"+self.style+"_GAUGE",   self.height*self.scaler, self.width*self.scaler)}

        self.images['GAUGE_REGIONAL'] = pyglet.image.ImageDataRegion(0, 0, 1, 1, image_data = self.images['GAUGE'][0])
        self.frameSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT'][0], batch = self.batch, group = self.group_0)
        self.gaugeSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['GAUGE'][0],   batch = self.batch, group = self.group_1)
        self.gaugeColor = list(kwargs.get('gaugeColor', (70, 150, 255, 255))); self.gaugeSprite.color = (self.gaugeColor[0], self.gaugeColor[1], self.gaugeColor[2]); self.gaugeSprite.opacity = self.gaugeColor[3]

        self.gaugeValue = kwargs.get('value', 50)
        self.updateGaugeValue(self.gaugeValue)

        self.hidden = False

    def process(self, t_elapsed_ns): pass
    def handleMouseEvent(self, event): pass
    def handleKeyEvent(self, event): pass

    def show(self):
        self.hidden = False
        self.frameSprite.visible = True
        if (0 < self.gaugeValue): self.gaugeSprite.visible = True

    def hide(self):
        self.hidden = True
        self.frameSprite.visible = False
        self.gaugeSprite.visible = False

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y
        self.frameSprite.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.frameSprite.z)
        self.gaugeSprite.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.gaugeSprite.z)

    def resize(self, width, height):
        self.width = width; self.height = height
        if (self.align == 'horizontal'):
            self.images['DEFAULT'] = self.imageManager.getImageByCode("gaugeBar_typeA_"+self.style+"_DEFAULT", self.width*self.scaler, self.height*self.scaler)
            self.images['GAUGE']   = self.imageManager.getImageByCode("gaugeBar_typeA_"+self.style+"_GAUGE",   self.width*self.scaler, self.height*self.scaler)
        elif (self.align == 'vertical'):
            self.images['DEFAULT'] = self.imageManager.getImageByCode("gaugeBar_typeA_"+self.style+"_DEFAULT", self.height*self.scaler, self.width*self.scaler)
            self.images['GAUGE']   = self.imageManager.getImageByCode("gaugeBar_typeA_"+self.style+"_GAUGE",   self.height*self.scaler, self.width*self.scaler)
        self.frameSprite.image = self.images['DEFAULT'][0]
        self.updateGaugeValue(self.gaugeValue)
        
    def setName(self, name): self.name = name
    def getName(self): return self.name
    def isTouched(self, mouseX, mouseY): return False
    def isHidden(self): return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        self.images['DEFAULT'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT'][1])
        self.images['GAUGE']   = self.imageManager.getImageByLoadIndex(self.images['GAUGE'][1])
        self.images['GAUGE_REGIONAL'] = pyglet.image.ImageDataRegion(0, 0, 1, 1, image_data = self.images['GAUGE'][0])
        self.frameSprite.image = self.images['DEFAULT'][0]
        self.gaugeSprite.color = (self.gaugeColor[0], self.gaugeColor[1], self.gaugeColor[2]); self.gaugeSprite.opacity = self.gaugeColor[3]
        self.updateGaugeValue(self.gaugeValue)
    def on_LanguageUpdate(self, **kwargs): pass

    def updateGaugeColor(self, rValue = None, gValue = None, bValue = None, aValue = None):
        if ((rValue != None) and (0 <= rValue) and (rValue <= 255)): self.gaugeColor[0] = rValue
        if ((gValue != None) and (0 <= gValue) and (gValue <= 255)): self.gaugeColor[1] = gValue
        if ((bValue != None) and (0 <= bValue) and (bValue <= 255)): self.gaugeColor[2] = bValue
        if ((aValue != None) and (0 <= aValue) and (aValue <= 255)): self.gaugeColor[3] = aValue
        self.gaugeSprite.color = (self.gaugeColor[0], self.gaugeColor[1], self.gaugeColor[2]); self.gaugeSprite.opacity = self.gaugeColor[3]

    def updateGaugeValue(self, gaugeValue):
        if ((0 <= gaugeValue) and (gaugeValue <= 100)):
            self.gaugeValue = gaugeValue
            if (self.align == 'horizontal'):
                clipLength = round(self.images['GAUGE'][0].width*self.gaugeValue/100)
                if (clipLength == 0): self.gaugeSprite.visible = False
                else:                 
                    self.images['GAUGE_REGIONAL'] = pyglet.image.ImageDataRegion(0, 0, clipLength, self.images['GAUGE'][0].height, self.images['GAUGE'][0])
                    if ((self.gaugeSprite.visible == False) and (self.hidden == False)): self.gaugeSprite.visible = True
            elif (self.align == 'vertical'):
                clipLength = round(self.images['GAUGE'][0].height*self.gaugeValue/100)
                if (clipLength == 0): self.gaugeSprite.visible = False
                else:                 
                    self.images['GAUGE_REGIONAL'] = pyglet.image.ImageDataRegion(0, 0, self.images['GAUGE'][0].width, clipLength, self.images['GAUGE'][0])
                    if ((self.gaugeSprite.visible == False) and (self.hidden == False)): self.gaugeSprite.visible = True
            self.gaugeSprite.image = self.images['GAUGE_REGIONAL']
        
    def getGroupRequirement(): return 1
#GUIO - 'gaugeBar_typeA' END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'selectionBox_typeA' ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class selectionBox_typeA:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.group_2 = kwargs['group_2']
            self.group_3 = kwargs['group_3']
            self.group_4 = kwargs['group_4']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)
            self.group_2 = pyglet.graphics.Group(order = self.groupOrder+2)
            self.group_3 = pyglet.graphics.Group(order = self.groupOrder+3)
            self.group_4 = pyglet.graphics.Group(order = self.groupOrder+4)
        
        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.style = kwargs.get('style', 'styleA')

        self.fontSize = int(kwargs.get('fontSize', 100)*self.scaler)
        self.textStyle = kwargs.get('textStyle', 'default')
        self.effectiveTextStyle = self.visualManager.getTextStyle('selectionBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize

        self.scrollBarWidth = 100
        self.internalGOffset = 50
        self.elementWidth  = self.width - self.scrollBarWidth - self.internalGOffset*3
        self.elementHeight = kwargs.get("elementHeight", 250)
        
        self.objectHitBox = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos, self.width, self.height)

        self.displayBox = (self.xPos+self.internalGOffset, self.yPos+self.internalGOffset, self.elementWidth, self.height-self.internalGOffset*2)
        self.displayBox_hitBox = atmEta_gui_HitBoxes.hitBox_Rectangular(self.displayBox[0], self.displayBox[1], self.displayBox[2], self.displayBox[3])
        
        
        #Functional Object Parameters
        self.hoverFunction       = kwargs.get('hoverFunction',       None)
        self.hoverEscapeFunction = kwargs.get('hoverEscapeFunction', None)
        self.pressFunction       = kwargs.get('pressFunction',       None)
        self.releaseFunction     = kwargs.get('releaseFunction',     None)
        self.selectionUpdateFunction = kwargs.get('selectionUpdateFunction', None)
        
        self.frameRadius = kwargs.get('frameRadius', 10)
        self.images = {'DEFAULT':      self.imageManager.getImageByCode("selectionBox_typeA_"+self.style+"_DEFAULT",      self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.frameRadius)),
                       'HOVERED':      self.imageManager.getImageByCode("selectionBox_typeA_"+self.style+"_HOVERED",      self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.frameRadius)),
                       'INACTIVEMASK': self.imageManager.getImageByCode("selectionBox_typeA_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.frameRadius))}

        self.frameSprite  = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULT'][0],      batch = self.batch, group = self.group_0)
        self.inactiveMask = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['INACTIVEMASK'][0], batch = self.batch, group = self.group_4); self.inactiveMask.visible = False
        
        #The scrollbar will use groupOrder (group_1 ~~~ group_4)
        if (groupOrder == None):
            self.scrollBar = scrollBar_typeA(scaler = self.scaler, batch = self.batch, imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager, 
                                             xPos=self.xPos+self.width-self.internalGOffset-self.scrollBarWidth, yPos=self.yPos+self.internalGOffset, width=self.height-self.internalGOffset*2, height=self.scrollBarWidth, 
                                             align = 'vertical', style="styleA", group_0 = self.group_1, group_1 = self.group_2, group_2 = self.group_3, viewRangeUpdateFunction = self.__onViewRangeUpdate_ScrollBar)
        else:
            self.scrollBar = scrollBar_typeA(scaler = self.scaler, batch = self.batch, imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager, 
                                             xPos=self.xPos+self.width-self.internalGOffset-self.scrollBarWidth, yPos=self.yPos+self.internalGOffset, width=self.height-self.internalGOffset*2, height=self.scrollBarWidth, 
                                             align = 'vertical', style="styleA", groupOrder=self.groupOrder+1, viewRangeUpdateFunction = self.__onViewRangeUpdate_ScrollBar)

        self.highlightColor_HOVERED    = self.visualManager.getFromColorTable('SELECTIONBOX_HOVERED')
        self.highlightColor_PRESSED    = self.visualManager.getFromColorTable('SELECTIONBOX_PRESSED')
        self.highlightColor_HOVEREDSEL = self.visualManager.getFromColorTable('SELECTIONBOX_HOVEREDSEL')
        self.highlightColor_SELECTED   = self.visualManager.getFromColorTable('SELECTIONBOX_SELECTED')
        
        self.displayProjectionHeight_Max = (self.height-self.internalGOffset*2)*self.scaler
        self.displayTargetHeight_Max = 0
        self.displayProjection = [0, self.displayTargetHeight_Max]

        if (groupOrder == None):
            self.display_camGroup = atmEta_gui_AdvancedPygletGroups.cameraGroup(window = kwargs['windowInstance'], order = self.groupOrder+1, parentCameraGroup = self.group_0,
                                                                                  viewport_x = (self.xPos+self.internalGOffset)*self.scaler, viewport_y = (self.yPos+self.internalGOffset)*self.scaler, viewport_width = self.elementWidth*self.scaler, viewport_height = (self.height-self.internalGOffset*2)*self.scaler,
                                                                                  projection_x0 = 0, projection_x1 = self.elementWidth*self.scaler, projection_y0 = 0, projection_y1 = 1)
        else:
            self.display_camGroup = atmEta_gui_AdvancedPygletGroups.cameraGroup(window = kwargs['windowInstance'], order = self.groupOrder+1,
                                                                                  viewport_x = (self.xPos+self.internalGOffset)*self.scaler, viewport_y = (self.yPos+self.internalGOffset)*self.scaler, viewport_width = self.elementWidth*self.scaler, viewport_height = (self.height-self.internalGOffset*2)*self.scaler,
                                                                                  projection_x0 = 0, projection_x1 = self.elementWidth*self.scaler, projection_y0 = 0, projection_y1 = 1)


        #Selection Dict
        #[Key]: Item ID
        #[Value][0]: Display Text
        #[Value][1]: Text Style (List of tuples [0]: targetRange, [1]: styleCode)
        #[Value][2]: Text Element SL
        #[Value][3]: Highlight Shape
        self.selectionList = dict()
        self.selectedKeys     = dict()
        self.selectedKeysList = list()
        self.displayTargets     = dict()
        self.displayTargetsList = list()
        self.displayTargets_visibleIndexRange = None
        self.displayTargets_coordinateUpdateQueue = list()
        self.displayTargets_coordinateUpdateProcessTimeLimit_ns = 10e6
        self.showIndex                   = kwargs.get("showIndex",                   False)
        self.multiSelect                 = kwargs.get("multiSelect",                 False)
        self.singularSelect_allowRelease = kwargs.get("singularSelect_allowRelease", True)

        #User Interaction Control
        self.interactionHandler_lastProcessed_ns   = 0
        self.interactionHandler_processInterval_ns = 10*1e6 #10ms
        
        self.mouseScrollDY = 0
        self.mouseScroll_lastRelY = None
        self.previousHoveredItemKey = None
        
        self.scrollBarUpdated = False

        #Object Status Control
        self.status = "DEFAULT"
        self.hidden = False; self.deactivated = False

        #Post-Initialization Action
        self.__updateDisplayElements()

    def process(self, t_elapsed_ns):
        interactionProcessed = False
        if ((self.interactionHandler_processInterval_ns <= time.perf_counter_ns() - self.interactionHandler_lastProcessed_ns)):
            #Mouse Scroll Interpreation
            if (self.mouseScrollDY != 0):
                #ViewRange Update
                projectionDelta = round(self.mouseScrollDY*self.elementHeight/4*self.scaler, 1)
                newDisplayProjection = [self.displayProjection[0]+projectionDelta, self.displayProjection[1]+projectionDelta]
                belowZeroDelta = -newDisplayProjection[0]
                aboveMaxDelta  = newDisplayProjection[1] - self.displayTargetHeight_Max
                if (0 < belowZeroDelta): newDisplayProjection = [0,                                     newDisplayProjection[1]+belowZeroDelta]
                if (0 < aboveMaxDelta):  newDisplayProjection = [newDisplayProjection[0]-aboveMaxDelta, self.displayTargetHeight_Max]
                if (self.displayProjection != newDisplayProjection):
                    self.displayProjection = newDisplayProjection
                    self.__onViewRangeUpdate(byScrollBar=False)

                #Item Hover Target Computation
                self.__findHoveredItem(self.mouseScroll_lastRelY)
                self.mouseScrollDY = 0
                interactionProcessed = True

            #Scrollbar Update Interpreation
            if (self.scrollBarUpdated == True):
                #Update the viewRange accordingly with the scrollbar
                viewRange_sb = self.scrollBar.getViewRange(asInverse = False)
                self.displayProjection[0] = viewRange_sb[0]/100*self.displayTargetHeight_Max
                self.displayProjection[1] = viewRange_sb[1]/100*self.displayTargetHeight_Max
                self.__onViewRangeUpdate(byScrollBar=True)
                self.scrollBarUpdated = False
                interactionProcessed = True

            #Update Timer
            self.interactionHandler_lastProcessed_ns = time.perf_counter_ns()

        if ((interactionProcessed == False) and (0 <len(self.displayTargets_coordinateUpdateQueue))):
            timer_beg = time.perf_counter_ns()
            while (0 <len(self.displayTargets_coordinateUpdateQueue)):
                oldestQueue = self.displayTargets_coordinateUpdateQueue.pop(0)
                self.selectionList[oldestQueue[0]]['textElement'].moveTo(y = oldestQueue[1])
                self.selectionList[oldestQueue[0]]['highlightShape'].y = oldestQueue[1]*self.scaler
                #Check elapsed time and escape if needed
                if (self.displayTargets_coordinateUpdateProcessTimeLimit_ns <= time.perf_counter_ns() - timer_beg): break

    def handleMouseEvent(self, event):
        if not((self.deactivated == True) or (self.hidden == True)):
            #HOVER ENTERED Handler
            if (event['eType'] == "HOVERENTERED"):
                #Object Interaction
                self.audioManager.playAudioByCode('selectionBox_typeA_HOVERED_A')
                self.status = "HOVERED"
                self.frameSprite.image = self.images[self.status][0]
                if (self.hoverFunction != None): self.hoverFunction(self)

            #HOVERESCAPED Handler
            elif (event['eType'] == "HOVERESCAPED"):
                #Object Interaction
                self.status = "DEFAULT"
                self.frameSprite.image = self.images[self.status][0]
                self.__releaseHoveredItem() #Release hovered item
                if (self.scrollBar.status == 'HOVERED'): self.scrollBar.handleMouseEvent({'eType': "HOVERESCAPED", 'x': event['x'], 'y': event['y']})

            #PRESSED Handler
            elif (event['eType'] == "PRESSED"):
                #Pressing on the scrollBar
                if (self.scrollBar.isTouched(event['x'], event['y']) == True): self.scrollBar.handleMouseEvent(event)
                #Pressing on the object
                else:
                    #Object Interaction
                    self.audioManager.playAudioByCode('selectionBox_typeA_PRESSED_A')
                    self.status = "PRESSED"
                    if (self.pressFunction != None): self.pressFunction(self)
                    self.__pressHoveredItem() #Press hovered item

            #RELEASED Handler
            elif (event['eType'] == "RELEASED"):
                #ScrollBar was pressed
                if (self.scrollBar.status == 'PRESSED'): self.scrollBar.handleMouseEvent(event)
                #Object was pressed
                elif (self.status == "PRESSED"):
                    self.audioManager.playAudioByCode('selectionBox_typeA_RELEASED_A')
                    self.status = "HOVERED"
                    self.frameSprite.image = self.images[self.status][0]
                    if (self.displayBox_hitBox.isTouched(event['x'], event['y']) == True): self.__selectHoveredItem(relativeY = (event['y']-self.displayBox[1])*self.scaler) #Select hovered item
                    else:                                                                  self.__releaseHoveredItem() #Release hovered item

            #MOVED Handler
            elif (event['eType'] == "MOVED"):
                #Scrollbar Control
                if (self.scrollBar.status == 'HOVERED'):
                    if (self.scrollBar.isTouched(event['x'], event['y']) == False): self.scrollBar.handleMouseEvent({'eType': "HOVERESCAPED", 'x': event['x'], 'y': event['y']}) #Scrollbar Touched -> NotTouched
                else:
                    if (self.scrollBar.isTouched(event['x'], event['y']) == True): self.scrollBar.handleMouseEvent({'eType': "HOVERENTERED", 'x': event['x'], 'y': event['y']}) #Scrollbar NotTouched -> Touched

                #DisplayBox Control
                if (self.displayBox_hitBox.isTouched(event['x'], event['y']) == True): self.__findHoveredItem(relativeY = (event['y']-self.displayBox[1])*self.scaler) #Find new hovered item
                else:                                                                  self.__releaseHoveredItem()                                                     #Release hovered item

            #DRAGGED Handler
            elif (event['eType'] == "DRAGGED"):
                #Scroll Bar Update
                if (self.scrollBar.status == 'PRESSED'): self.scrollBar.handleMouseEvent(event)

            #SCROLLED Handler
            elif (event['eType'] == "SCROLLED"):
                #Scroll Delta Update
                if (self.displayBox_hitBox.isTouched(event['x'], event['y']) == True):
                    self.mouseScrollDY += event['scroll_y']
                    self.mouseScroll_lastRelY = (event['y']-self.displayBox[1])*self.scaler

    def handleKeyEvent(self, event): 
        pass

    def show(self):
        self.hidden = False
        self.frameSprite.visible = True
        self.display_camGroup.show()
        self.scrollBar.show()
        if (self.deactivated == True): self.inactiveMask.visible = True

    def hide(self):
        self.hidden = True
        self.frameSprite.visible = False
        self.display_camGroup.hide()
        self.scrollBar.hide()
        self.inactiveMask.visible = False
        self.__releaseHoveredItem()

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y
        self.frameSprite.position  = (self.xPos*self.scaler, self.yPos*self.scaler, self.frameSprite.z)
        self.inactiveMask.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.inactiveMask.z)
        self.objectHitBox.reposition(xPos = self.xPos, yPos = self.yPos)
        self.scrollBar.moveTo(x = self.xPos+self.width-self.internalGOffset-self.scrollBarWidth, y = self.yPos+self.internalGOffset)
        self.displayBox = (self.xPos+self.internalGOffset, self.yPos+self.internalGOffset, self.elementWidth, self.height-self.internalGOffset*2)
        self.displayBox_hitBox.reposition(xPos = self.displayBox[0], yPos = self.displayBox[1])
        self.display_camGroup.updateViewport(viewport_x=(self.xPos+self.internalGOffset)*self.scaler, viewport_y=(self.yPos+self.internalGOffset)*self.scaler)

    def resize(self, width, height):
        self.width = width; self.height = height
        self.elementWidth  = self.width - self.scrollBarWidth - self.internalGOffset*3
        self.displayProjectionHeight_Max = (self.height-self.internalGOffset*2)*self.scaler

        self.objectHitBox.resize(width = self.width, height = self.height)
        self.displayBox = (self.xPos+self.internalGOffset, self.yPos+self.internalGOffset, self.elementWidth, self.height-self.internalGOffset*2)
        self.displayBox_hitBox.resize(width = self.displayBox[2], height = self.displayBox[3])

        self.images['DEFAULT']      = self.imageManager.getImageByCode("selectionBox_typeA_"+self.style+"_DEFAULT",      self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.frameRadius))
        self.images['HOVERED']      = self.imageManager.getImageByCode("selectionBox_typeA_"+self.style+"_HOVERED",      self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.frameRadius))
        self.images['INACTIVEMASK'] = self.imageManager.getImageByCode("selectionBox_typeA_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.frameRadius))
        self.frameSprite.image  = self.images[self.status][0]
        self.inactiveMask.image = self.images['INACTIVEMASK'][0]

        self.scrollBar.resize(self.height-self.internalGOffset*2, self.scrollBar.height)
        self.scrollBar.moveTo(x = self.xPos+self.width-self.internalGOffset-self.scrollBarWidth, y = self.scrollBar.yPos)
        
        for itemKey in self.selectionList: 
            self.selectionList[itemKey]['textElement'].changeSize(width = self.elementWidth)
            self.selectionList[itemKey]['highlightShape'].width = self.elementWidth*self.scaler
            
        self.display_camGroup.updateViewport(viewport_width = self.elementWidth*self.scaler, viewport_height = (self.height-self.internalGOffset*2)*self.scaler)
        self.display_camGroup.updateProjection(projection_x1 = self.elementWidth*self.scaler)
        self.__updateDisplayElements()

    def activate(self):
        self.deactivated = False
        self.inactiveMask.visible = False

    def deactivate(self):
        self.deactivated = True
        if (self.hidden == False): self.inactiveMask.visible = True

    def addTextStyle(self, textStyleCode, textStyle):
        self.effectiveTextStyle[textStyleCode] = textStyle.copy()
        self.effectiveTextStyle[textStyleCode]['font_size'] = self.fontSize
        for itemKey in self.selectionList: self.selectionList[itemKey]['textElement'].addTextStyle(textStyleCode, self.effectiveTextStyle[textStyleCode])
            


    #<Selection List Control>
    def setSelectionList(self, selectionList, displayTargets = None, keepSelected = False, callSelectionUpdateFunction = True):
        #If Selected Keys are to be conserved, save a copy of the previsouly selected keys list
        if (keepSelected == True): previouslySelectedKeysList = self.selectedKeysList.copy()

        #Initialize SelectionList and Display Control Variables
        self.clearSelectionList(callSelectionUpdateFunction = False)
        self.previousHoveredItemKey = None

        #Add Selection List
        if (0 < len(selectionList)):
            listType = type(selectionList)
            if (listType == list):
                for index, item in enumerate(selectionList):
                    self.selectionList[index] = {'text': item,
                                                 'textStyles': None,
                                                 'textAnchor': 'CENTER',
                                                 'textElement': atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.display_camGroup, text = "", defaultTextStyle = self.effectiveTextStyle['DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                                                       xPos = 0, yPos = 0, width = self.elementWidth, height = self.elementHeight, showElementBox = False, anchor = 'CENTER'),
                                                 'highlightShape': pyglet.shapes.Rectangle(x = 0, y = 0, width = self.elementWidth*self.scaler, height = self.elementHeight*self.scaler, batch = self.batch, group = self.display_camGroup, color = self.highlightColor_HOVERED),
                                                 'index': index}
                    self.selectionList[index]['textElement'].hide()
                    self.selectionList[index]['highlightShape'].visible = False

            elif (listType == dict):
                for index, itemKey in enumerate(selectionList):
                    self.selectionList[itemKey] = {'text': selectionList[itemKey]['text'],
                                                   'textStyles': selectionList[itemKey].get('textStyles', None),
                                                   'textAnchor': selectionList[itemKey].get('textAnchor', 'CENTER'),
                                                   'textElement': atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.display_camGroup, text = "", defaultTextStyle = self.effectiveTextStyle['DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                                                         xPos = 0, yPos = 0, width = self.elementWidth, height = self.elementHeight, showElementBox = False, anchor = selectionList[itemKey].get('textAnchor', 'CENTER')),
                                                   'highlightShape': pyglet.shapes.Rectangle(x = 0, y = 0, width = self.elementWidth*self.scaler, height = self.elementHeight*self.scaler, batch = self.batch, group = self.display_camGroup, color = self.highlightColor_HOVERED),
                                                   'index': index}
                    self.selectionList[itemKey]['textElement'].hide()
                    self.selectionList[itemKey]['highlightShape'].visible = False
                    
        #Add back selected items that are still existing
        if (keepSelected == True):
            previouslySelectedKeysList_stillExisting = [itemKey for itemKey in previouslySelectedKeysList if itemKey in self.selectionList]
            for index, itemKey in enumerate(previouslySelectedKeysList_stillExisting): 
                self.selectedKeys[itemKey] = index
                self.selectedKeysList.append(itemKey)
                self.selectionList[itemKey]['highlightShape'].color = self.highlightColor_SELECTED

        #Post SelectionList Update Actions
        if (displayTargets == None): self.__updateDisplayElements()
        else:                        self.setDisplayTargets(displayTargets)
        self.__updateTextElementTexts()


        #Call Selection Update Function if needed
        if ((callSelectionUpdateFunction == True) and (self.selectionUpdateFunction != None)): self.selectionUpdateFunction(self)

    def clearSelectionList(self, callSelectionUpdateFunction = True):
        #Initialize SelectionList and Display Control Variables
        self.displayTargetHeight_Max = 0
        self.displayProjection = [0, self.displayTargetHeight_Max]

        for itemKey in self.selectionList: self.selectionList[itemKey]['textElement'].delete()
        self.selectionList.clear()
        self.selectedKeys.clear()
        self.selectedKeysList.clear()
        self.displayTargets.clear()
        self.displayTargetsList.clear()
        self.displayTargets_visibleIndexRange = None
        self.displayTargets_coordinateUpdateQueue.clear()

        self.__onViewRangeUpdate()

        #Call Selection Update Function if needed
        if ((callSelectionUpdateFunction == True) and (self.selectionUpdateFunction != None)): self.selectionUpdateFunction(self)

    def editSelectionListItem(self, itemKey, item):
        if (itemKey in self.selectionList):
            updateText       = False
            updateTextStyles = False
            updateTextAnchor = False
            if (('text' in item)       and (item['text']       != self.selectionList[itemKey]['text'])):       self.selectionList[itemKey]['text'] = item['text'];             updateText = True; updateTextStyles = True
            if (('textStyles' in item) and (item['textStyles'] != self.selectionList[itemKey]['textStyles'])): self.selectionList[itemKey]['textStyles'] = item['textStyles']; updateTextStyles = True
            if (('textAnchor' in item) and (item['textAnchor'] != self.selectionList[itemKey]['textAnchor'])): self.selectionList[itemKey]['text'] = item['textAnchor'];       updateTextAnchor = True

            if (updateTextAnchor == True): self.selectionList[itemKey]['textElement'].setAnchor(item['textAnchor'])
            
            if (self.showIndex == True):
                nSelectionList = len(self.selectionList)
                indexStr = "[{:d} / {:d}] ".format(self.selectionList[itemKey]['index']+1, nSelectionList)
                effectiveText = indexStr + self.visualManager.extractText(self.selectionList[itemKey]['text'])
                if (updateText == True): self.selectionList[itemKey]['textElement'].setText(effectiveText)
                if (updateTextStyles == True):
                    if (self.selectionList[itemKey]['textStyles'] == None): self.selectionList[itemKey]['textElement'].editTextStyle((0, len(effectiveText)), 'DEFAULT')
                    else:
                        self.selectionList[itemKey]['textElement'].editTextStyle((0, len(indexStr)-1), 'DEFAULT')
                        for textStyle in self.selectionList[itemKey]['textStyles']:
                            targetRange = (textStyle[0][0]+len(indexStr), textStyle[0][1]+len(indexStr))
                            targetCode  = textStyle[1]
                            if (targetCode in self.effectiveTextStyle): self.selectionList[itemKey]['textElement'].editTextStyle(targetRange, targetCode)
                            else:                                       self.selectionList[itemKey]['textElement'].editTextStyle(targetRange, 'DEFAULT')
            else:
                effectiveText = self.visualManager.extractText(self.selectionList[itemKey]['text'])
                if (updateText == True): self.selectionList[itemKey]['textElement'].setText(effectiveText)
                if (updateTextStyles == True):
                    if (self.selectionList[itemKey]['textStyles'] == None): self.selectionList[itemKey]['textElement'].editTextStyle((0, len(effectiveText)), 'DEFAULT')
                    else:
                        for textStyle in self.selectionList[itemKey]['textStyles']:
                            targetRange = textStyle[0]
                            targetCode  = textStyle[1]
                            if (targetCode in self.effectiveTextStyle): self.selectionList[itemKey]['textElement'].editTextStyle(targetRange, targetCode)
                            else:                                       self.selectionList[itemKey]['textElement'].editTextStyle(targetRange, 'DEFAULT')
                
        
                
    def getSelectionListItemInfo(self, itemKey):
        if (itemKey in self.selectionList): 
            return {'text':          self.selectionList[itemKey]['text'],
                    'effectiveText': self.selectionList[itemKey]['textElement'].getText(),
                    'textStyles':    self.selectionList[itemKey]['textStyles'], 
                    'textAnchor':    self.selectionList[itemKey]['textAnchor'], 
                    'isSelected':    itemKey in self.selectedKeys}
        else: return None

    def getSelectionList(self):
        returnDict = dict()
        for itemKey in self.selectionList:
            returnDict[itemKey] = {'text':          self.selectionList[itemKey]['text'],
                                   'effectiveText': self.selectionList[itemKey]['textElement'].getText(),
                                   'textStyles':    self.selectionList[itemKey]['textStyles'], 
                                   'textAnchor':    self.selectionList[itemKey]['textAnchor'],
                                   'index':         self.selectionList[itemKey]['index'], 
                                   'isSelected':    itemKey in self.selectedKeys}
        return returnDict

    def getSelectionListKeys(self):
        return list(self.selectionList.keys())


    #<Display Target Control>
    def setDisplayTargets(self, displayTargets):
        #Hide all items
        for itemKey in self.displayTargets:
            if (self.selectionList[itemKey]['textElement'].isHidden() == False): self.selectionList[itemKey]['textElement'].hide()
            if (self.selectionList[itemKey]['highlightShape'].visible == True): self.selectionList[itemKey]['highlightShape'].visible = False
        self.displayTargets_visibleIndexRange = None

        #Set display targets
        self.displayTargets.clear()
        self.displayTargetsList.clear()
        if (displayTargets == 'all'):
            for index, selectionListKey in enumerate(self.selectionList):
                self.displayTargets[selectionListKey] = index
                self.displayTargetsList.append(selectionListKey)
        else:
            for index, targetKey in enumerate(displayTargets): 
                self.displayTargets[targetKey] = index
                self.displayTargetsList.append(targetKey)

        #Update Display Elements
        self.__updateDisplayElements()





    #<Selected Items Control>
    def addSelected(self, itemKey, additionType = 0, callSelectionUpdateFunction = True):
        if (itemKey in self.selectionList):
            if (self.multiSelect == False): self.clearSelected()
            self.selectedKeys[itemKey] = len(self.selectedKeys)
            self.selectedKeysList.append(itemKey)
            if (itemKey in self.displayTargets): self.selectionList[itemKey]['highlightShape'].visible = True
            if   (additionType == 0): self.selectionList[itemKey]['highlightShape'].color = self.highlightColor_SELECTED
            elif (additionType == 1): self.selectionList[itemKey]['highlightShape'].color = self.highlightColor_HOVEREDSEL
            if ((callSelectionUpdateFunction == True) and (self.selectionUpdateFunction != None)): self.selectionUpdateFunction(self)
            return True
        return False


    def removeSelected(self, itemKey, removalType = 0, callSelectionUpdateFunction = True):
        if ((itemKey in self.selectionList) and (itemKey in self.selectedKeys)):
            if not((self.multiSelect == False) and (self.singularSelect_allowRelease == False)):
                selectionIndex = self.selectedKeys[itemKey]
                for selectedkey in self.selectedKeys:
                    if (selectionIndex < self.selectedKeys[selectedkey]): self.selectedKeys[selectedkey] -= 1
                if   (removalType == 0): self.selectionList[itemKey]['highlightShape'].visible = False
                elif (removalType == 1): self.selectionList[itemKey]['highlightShape'].color = self.highlightColor_HOVERED
                del self.selectedKeys[itemKey]
                self.selectedKeysList.pop(selectionIndex)
                if ((callSelectionUpdateFunction == True) and (self.selectionUpdateFunction != None)): self.selectionUpdateFunction(self)
                return True
            elif (removalType == 1): self.selectionList[itemKey]['highlightShape'].color = self.highlightColor_HOVEREDSEL
        return False


    def clearSelected(self):
        for selectedkey in self.selectedKeys:
            if (self.previousHoveredItemKey == selectedkey): self.selectionList[selectedkey]['highlightShape'].color = self.highlightColor_HOVERED
            else:                                            self.selectionList[selectedkey]['highlightShape'].visible = False
        self.selectedKeys.clear()
        self.selectedKeysList.clear()



    def getSelected(self):
        return self.selectedKeysList.copy()





    #<Internal Functions>
    def __updateTextElementTexts(self):
        if (self.showIndex == True):
            nSelectionList = len(self.selectionList)
            for index, itemKey in enumerate(self.selectionList):
                indexStr = "[{:d} / {:d}] ".format(index+1, nSelectionList)
                effectiveText = indexStr + self.visualManager.extractText(self.selectionList[itemKey]['text'])
                self.selectionList[itemKey]['textElement'].setText(effectiveText)
                if (self.selectionList[itemKey]['textStyles'] == None): self.selectionList[itemKey]['textElement'].editTextStyle((0, len(effectiveText)), 'DEFAULT')
                else:
                    self.selectionList[itemKey]['textElement'].editTextStyle((0, len(indexStr)), 'DEFAULT')
                    for textStyle in self.selectionList[itemKey]['textStyles']:
                        targetRange = (textStyle[0][0]+len(indexStr), textStyle[0][1]+len(indexStr))
                        targetCode  = textStyle[1]
                        if (targetCode in self.effectiveTextStyle): self.selectionList[itemKey]['textElement'].editTextStyle(targetRange, targetCode)
                        else:                                       self.selectionList[itemKey]['textElement'].editTextStyle(targetRange, 'DEFAULT')
        else:
            for itemKey in self.selectionList:
                effectiveText = self.visualManager.extractText(self.selectionList[itemKey]['text'])
                self.selectionList[itemKey]['textElement'].setText(effectiveText)
                if (self.selectionList[itemKey]['textStyles'] == None): self.selectionList[itemKey]['textElement'].editTextStyle((0, len(effectiveText)), 'DEFAULT')
                else:
                    for textStyle in self.selectionList[itemKey]['textStyles']:
                        targetRange = textStyle[0]
                        targetCode  = textStyle[1]
                        if (targetCode in self.effectiveTextStyle): self.selectionList[itemKey]['textElement'].editTextStyle(targetRange, targetCode)
                        else:                                       self.selectionList[itemKey]['textElement'].editTextStyle(targetRange, 'DEFAULT')



    def __updateDisplayElements(self):
        self.displayTargets_coordinateUpdateQueue.clear()
        nDisplayTargetsLen = len(self.displayTargets)
        if (0 < nDisplayTargetsLen):
            #Display Projection Update
            self.displayTargetHeight_Max = len(self.displayTargets)*self.elementHeight*self.scaler
            if (self.displayProjectionHeight_Max < self.displayTargetHeight_Max): self.displayProjection = [self.displayTargetHeight_Max-self.displayProjectionHeight_Max, self.displayTargetHeight_Max]
            else:                                                                 self.displayProjection = [0,                                                             self.displayTargetHeight_Max]
            if ((self.display_camGroup.visible == False) and (self.hidden == False)): self.display_camGroup.visible = True
            self.__onViewRangeUpdate()
            
            #Item Coordinate Update
            for selectionItemKey in self.selectionList:
                if (selectionItemKey in self.displayTargets):
                    displayTargetIndex = self.displayTargets[selectionItemKey]
                    if ((self.displayTargets_visibleIndexRange[0] <= displayTargetIndex) and (displayTargetIndex <= self.displayTargets_visibleIndexRange[1])):
                        newYCoord = (nDisplayTargetsLen-displayTargetIndex-1)*self.elementHeight
                        self.selectionList[selectionItemKey]['textElement'].moveTo(y = newYCoord)
                        self.selectionList[selectionItemKey]['highlightShape'].y = newYCoord*self.scaler
                    else:
                        newYCoord = (nDisplayTargetsLen-displayTargetIndex-1)*self.elementHeight
                        self.displayTargets_coordinateUpdateQueue.append((selectionItemKey, newYCoord))
        else:
            self.displayTargetHeight_Max = 0
            self.scrollBar.editViewRange((0, 100), asInverse = False)
            if (self.display_camGroup.visible == True): self.display_camGroup.visible = False



    def __releaseHoveredItem(self):
        if (self.previousHoveredItemKey != None):
            if (self.previousHoveredItemKey in self.selectedKeys): self.selectionList[self.previousHoveredItemKey]['highlightShape'].color = self.highlightColor_SELECTED
            else:                                                  self.selectionList[self.previousHoveredItemKey]['highlightShape'].visible = False
            self.previousHoveredItemKey = None



    def __pressHoveredItem(self):
        if (self.previousHoveredItemKey != None):
            if (self.selectionList[self.previousHoveredItemKey]['highlightShape'].visible == False):                     self.selectionList[self.previousHoveredItemKey]['highlightShape'].visible = True
            if (self.selectionList[self.previousHoveredItemKey]['highlightShape'].color != self.highlightColor_PRESSED): self.selectionList[self.previousHoveredItemKey]['highlightShape'].color = self.highlightColor_PRESSED



    def __findHoveredItem(self, relativeY):
        #Find the new hovered index
        maxDelta = self.displayProjectionHeight_Max - self.displayTargetHeight_Max
        if (0 < maxDelta): yWithinDisplaySpace = relativeY+self.displayProjection[0]-maxDelta
        else:              yWithinDisplaySpace = relativeY+self.displayProjection[0]
        if ((0 <= yWithinDisplaySpace) and (yWithinDisplaySpace < self.displayTargetHeight_Max)): indexPosition = len(self.displayTargets)-int(yWithinDisplaySpace/(self.elementHeight*self.scaler))-1
        else:                                                                                     indexPosition = None

        #Find the new hovered key
        if (indexPosition == None): newHoveredKey = None
        else:                       newHoveredKey = self.displayTargetsList[indexPosition]

        #Compare the previous and the new hovered item, and update the highlighters
        if (newHoveredKey != self.previousHoveredItemKey):
            #Release previously hovered item
            if (self.previousHoveredItemKey != None):
                if (self.previousHoveredItemKey in self.selectedKeys): self.selectionList[self.previousHoveredItemKey]['highlightShape'].color = self.highlightColor_SELECTED
                else:                                                  self.selectionList[self.previousHoveredItemKey]['highlightShape'].visible = False

            #Highlight newly hovered item
            if (newHoveredKey != None):
                if (newHoveredKey in self.selectedKeys): 
                    if (self.selectionList[newHoveredKey]['highlightShape'].color != self.highlightColor_HOVEREDSEL): self.selectionList[newHoveredKey]['highlightShape'].color = self.highlightColor_HOVEREDSEL
                    self.selectionList[newHoveredKey]['highlightShape'].visible = True
                else:
                    if (self.selectionList[newHoveredKey]['highlightShape'].color != self.highlightColor_HOVERED): self.selectionList[newHoveredKey]['highlightShape'].color = self.highlightColor_HOVERED
                    self.selectionList[newHoveredKey]['highlightShape'].visible = True

            self.previousHoveredItemKey = newHoveredKey



    def __selectHoveredItem(self, relativeY):
        #Find the new hovered index
        maxDelta = self.displayProjectionHeight_Max - self.displayTargetHeight_Max
        if (0 < maxDelta): yWithinDisplaySpace = relativeY+self.displayProjection[0]-maxDelta
        else:              yWithinDisplaySpace = relativeY+self.displayProjection[0]
        if ((0 <= yWithinDisplaySpace) and (yWithinDisplaySpace < self.displayTargetHeight_Max)): indexPosition = len(self.displayTargets)-int(yWithinDisplaySpace/(self.elementHeight*self.scaler))-1
        else:                                                                                     indexPosition = None

        #Find the new hovered key
        if (indexPosition == None): itemKeyOnRelease = None
        else:                       itemKeyOnRelease = self.displayTargetsList[indexPosition]

        #Compare the previous and the new hovered item, and add selection if needed
        if (self.previousHoveredItemKey == itemKeyOnRelease): 
            if (itemKeyOnRelease in self.selectedKeys): self.removeSelected(itemKey = itemKeyOnRelease, removalType= 1, callSelectionUpdateFunction = True)
            else:                                       self.addSelected(itemKey = itemKeyOnRelease, additionType = 1, callSelectionUpdateFunction = True)
        else:
            #Release previously hovered item
            if (self.previousHoveredItemKey != None):
                if (self.previousHoveredItemKey in self.selectedKeys): self.selectionList[self.previousHoveredItemKey]['highlightShape'].color = self.highlightColor_SELECTED
                else:                                                  self.selectionList[self.previousHoveredItemKey]['highlightShape'].visible = False
            #Highlight newly hovered item
            if (itemKeyOnRelease != None):
                if (itemKeyOnRelease in self.selectedKeys): 
                    if (self.selectionList[itemKeyOnRelease]['highlightShape'].color != self.highlightColor_HOVEREDSEL): self.selectionList[itemKeyOnRelease]['highlightShape'].color = self.highlightColor_HOVEREDSEL
                    self.selectionList[itemKeyOnRelease]['highlightShape'].visible = True
                else:
                    if (self.selectionList[itemKeyOnRelease]['highlightShape'].color != self.highlightColor_HOVERED): self.selectionList[itemKeyOnRelease]['highlightShape'].color = self.highlightColor_HOVERED
                    self.selectionList[itemKeyOnRelease]['highlightShape'].visible = True
            self.previousHoveredItemKey = itemKeyOnRelease



    def __onViewRangeUpdate(self, byScrollBar = False):
        #Edit the camera group projection and viewport
        if (self.displayTargetHeight_Max == 0):
            self.scrollBar.editViewRange((0, 100), asInverse = False)
            self.display_camGroup.visible = False
        else:
            if (byScrollBar == False): self.scrollBar.editViewRange((self.displayProjection[0]/self.displayTargetHeight_Max*100, self.displayProjection[1]/self.displayTargetHeight_Max*100), asInverse = False)
            self.display_camGroup.updateProjection(projection_y0=self.displayProjection[0], projection_y1=self.displayProjection[1])
            maxDelta = self.displayProjectionHeight_Max - self.displayTargetHeight_Max
            if (0 < maxDelta): self.display_camGroup.updateViewport(viewport_y = (self.yPos+self.internalGOffset)*self.scaler+maxDelta, viewport_height = self.displayTargetHeight_Max)
            else:              self.display_camGroup.updateViewport(viewport_y = (self.yPos+self.internalGOffset)*self.scaler, viewport_height = self.displayProjectionHeight_Max)

        #Set visibilities of items
        nDisplayTargetsLen = len(self.displayTargets)
        visibleDisplayTargetIndex_0 = nDisplayTargetsLen-int(self.displayProjection[1]/(self.elementHeight*self.scaler))-1
        visibleDisplayTargetIndex_1 = nDisplayTargetsLen-int(self.displayProjection[0]/(self.elementHeight*self.scaler))-1
        if (visibleDisplayTargetIndex_0 < 0):                   visibleDisplayTargetIndex_0 = 0
        if (nDisplayTargetsLen <= visibleDisplayTargetIndex_1): visibleDisplayTargetIndex_1 = nDisplayTargetsLen-1

        #---Find indexes to show and hide
        if (self.displayTargets_visibleIndexRange == None):
            toShow = list(range(visibleDisplayTargetIndex_0, visibleDisplayTargetIndex_1+1))
            toHide = []
        else:
            toShow = [newVisibleIndex        for newVisibleIndex        in range(visibleDisplayTargetIndex_0, visibleDisplayTargetIndex_1+1)                           if not((self.displayTargets_visibleIndexRange[0] <= newVisibleIndex) and (newVisibleIndex <= self.displayTargets_visibleIndexRange[1]))]
            toHide = [previouslyVisibleIndex for previouslyVisibleIndex in range(self.displayTargets_visibleIndexRange[0], self.displayTargets_visibleIndexRange[1]+1) if not((visibleDisplayTargetIndex_0 <= previouslyVisibleIndex)       and (previouslyVisibleIndex <= visibleDisplayTargetIndex_1))]

        #---Show items that are newly visible
        for itemIndex in toShow:
            itemKey = self.displayTargetsList[itemIndex]
            if (self.selectionList[itemKey]['textElement'].isHidden() == True): self.selectionList[itemKey]['textElement'].show()
            if (itemKey in self.selectedKeys) and (self.selectionList[itemKey]['highlightShape'].visible == False): self.selectionList[itemKey]['highlightShape'].visible = True

        #---Hide items that are no longer visible
        for itemIndex in toHide:
            itemKey = self.displayTargetsList[itemIndex]
            if (self.selectionList[itemKey]['textElement'].isHidden() == False): self.selectionList[itemKey]['textElement'].hide()
            if (self.selectionList[itemKey]['highlightShape'].visible == True): self.selectionList[itemKey]['highlightShape'].visible = False

        #Update the tracker
        self.displayTargets_visibleIndexRange = (visibleDisplayTargetIndex_0, visibleDisplayTargetIndex_1)

    def __onViewRangeUpdate_ScrollBar(self, objectInstance): 
        self.scrollBarUpdated = True

    def setName(self, name): 
        self.name = name
    
    def getName(self): 
        return self.name
    
    def isTouched(self, mouseX, mouseY): 
        return ((self.hidden == False) and (self.objectHitBox.isTouched(mouseX, mouseY) == True))
    
    def isHidden(self): 
        return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        #Get the updated image and textStyle from the managers
        self.images['DEFAULT'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT'][1])
        self.images['HOVERED'] = self.imageManager.getImageByLoadIndex(self.images['HOVERED'][1])
        if (self.status == 'PRESSED'): self.frameSprite.image = self.images['HOVERED'][0]
        else:                          self.frameSprite.image = self.images[self.status][0]
        self.effectiveTextStyle = self.visualManager.getTextStyle('selectionBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        
        self.highlightColor_HOVERED    = self.visualManager.getFromColorTable('SELECTIONBOX_HOVERED')
        self.highlightColor_PRESSED    = self.visualManager.getFromColorTable('SELECTIONBOX_PRESSED')
        self.highlightColor_HOVEREDSEL = self.visualManager.getFromColorTable('SELECTIONBOX_HOVEREDSEL')
        self.highlightColor_SELECTED   = self.visualManager.getFromColorTable('SELECTIONBOX_SELECTED')

        #Apply the updated image and textStyle
        self.frameSprite.image = self.images[self.status][0]
        for selectionItemKey in self.selectionList:
            for textStyleCode in self.effectiveTextStyle: self.selectionList[selectionItemKey]['textElement'].addTextStyle(textStyleCode, self.effectiveTextStyle[textStyleCode])
            self.selectionList[selectionItemKey]['textElement'].on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['DEFAULT'])
            if (selectionItemKey in self.selectedKeys):
                if (selectionItemKey == self.previousHoveredItemKey): self.selectionList[selectionItemKey]['highlightShape'].color = self.highlightColor_HOVEREDSEL
                else:                                                 self.selectionList[selectionItemKey]['highlightShape'].color = self.highlightColor_SELECTED
            else:
                if (selectionItemKey == self.previousHoveredItemKey): self.selectionList[selectionItemKey]['highlightShape'].color = self.highlightColor_HOVERED

        #ScrollBar GUI Theme Update
        self.scrollBar.on_GUIThemeUpdate()

    def on_LanguageUpdate(self, **kwargs):
        #Get the updated image and textStyle from the managers
        self.effectiveTextStyle = self.visualManager.getTextStyle('selectionBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize

        #Apply updated language font and text
        if (self.showIndex == True):
            nSelectionList = len(self.selectionList)
            indexStr_maxLen = len("[{:d} / {:d}] ".format(nSelectionList, nSelectionList))
            for index, selectionItemKey in enumerate(self.selectionList):
                indexStr = "[{:d} / {:d}]".format(index+1, nSelectionList)
                indexStr += " "*(indexStr_maxLen-len(indexStr))
                newEffectiveText = indexStr + self.visualManager.extractText(self.selectionList[selectionItemKey]['text'])
                self.selectionList[selectionItemKey]['textElement'].on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'], newLanguageText = newEffectiveText)
        else:
            for selectionItemKey in self.selectionList:
                newEffectiveText = self.visualManager.extractText(self.selectionList[selectionItemKey]['text'])
                self.selectionList[selectionItemKey]['textElement'].on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'], newLanguageText = newEffectiveText)
        
    def getGroupRequirement(): return 4
#GUIO - 'selectionBox_typeA' END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'selectionBox_typeB' ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class selectionBox_typeB:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1'] 
            self.group_2 = kwargs['group_2']
            self.group_10 = kwargs['group_10'] #group_2 for selectionBox_typeA
            self.group_11 = kwargs['group_11'] #group_3 for selectionBox_typeA
            self.group_12 = kwargs['group_12'] #group_3 for selectionBox_typeA
            self.group_13 = kwargs['group_13'] #group_3 for selectionBox_typeA
            self.group_14 = kwargs['group_14'] #group_3 for selectionBox_typeA
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)
            self.group_2 = pyglet.graphics.Group(order = self.groupOrder+2)
            self.group_10 = pyglet.graphics.Group(order = self.groupOrder+10)
            self.group_11 = pyglet.graphics.Group(order = self.groupOrder+11)
            self.group_12 = pyglet.graphics.Group(order = self.groupOrder+12)
            self.group_13 = pyglet.graphics.Group(order = self.groupOrder+13)
            self.group_14 = pyglet.graphics.Group(order = self.groupOrder+14)

        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.style = kwargs.get('style', 'styleA')

        fontSize_unscaled = kwargs.get('fontSize', 100)
        self.fontSize = int(fontSize_unscaled*self.scaler)
        self.textStyle = kwargs.get('textStyle', 'default')
        self.effectiveTextStyle = self.visualManager.getTextStyle('selectionBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize

        self.hitBox = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos, self.width, self.height)

        #Functional Object Parameters
        self.hoverFunction       = kwargs.get('hoverFunction',       None)
        self.hoverEscapeFunction = kwargs.get('hoverEscapeFunction', None)
        self.pressFunction       = kwargs.get('pressFunction',       None)
        self.releaseFunction     = kwargs.get('releaseFunction',     None)
        self.selectionUpdateFunction = kwargs.get('selectionUpdateFunction', None)
        
        self.nDisplay_max = kwargs.get('nDisplay', 10)
        self.nDisplay_effective = 0
        self.expansionDir = kwargs.get('expansionDir', 0)
        if (groupOrder == None):
            if   (self.expansionDir == 0): sb_yPos = self.yPos-(self.nDisplay_effective*self.height+50*2)
            elif (self.expansionDir == 1): sb_yPos = self.yPos+self.height
            self.selectionBoxTypeA = selectionBox_typeA(windowInstance = kwargs['windowInstance'], scaler = self.scaler, batch = self.batch, imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager, 
                                                        group_0 = self.group_10, group_1 = self.group_11, group_2 = self.group_12, group_3 = self.group_13, group_4 = self.group_14,
                                                        xPos=self.xPos, yPos=sb_yPos, width=self.width, height=self.nDisplay_max*self.height+50*2, style=self.style, radius = int(self.height/3*self.scaler), fontSize = fontSize_unscaled,
                                                        multiSelect = False, singularSelect_allowRelease = False, showIndex = kwargs.get('showIndex', False))
        else:
            if   (self.expansionDir == 0): sb_yPos = self.yPos-(self.nDisplay_effective*self.height+50*2)
            elif (self.expansionDir == 1): sb_yPos = self.yPos+self.height
            self.selectionBoxTypeA = selectionBox_typeA(windowInstance = kwargs['windowInstance'], scaler = self.scaler, batch = self.batch, imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager, groupOrder = self.groupOrder+10,
                                                        xPos=self.xPos, yPos=sb_yPos, width=self.width, height=self.nDisplay_max*self.height+50*2, style=self.style, radius = int(self.height/3*self.scaler), fontSize = fontSize_unscaled,
                                                        multiSelect = False, singularSelect_allowRelease = False, showIndex = kwargs.get('showIndex', False))

        self.selectionBoxTypeA.process(1e9)
        self.selectionBoxTypeA.hide()
        self.selectedKey = None

        textBoxWidth = self.width-self.selectionBoxTypeA.scrollBarWidth-self.selectionBoxTypeA.internalGOffset*2
        self.images = {'DEFAULTC':     self.imageManager.getImageByCode("selectionBox_typeB_"+self.style+"_DEFAULTC",     self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}_{:d}".format(round(self.height/2*self.scaler), round(textBoxWidth*self.scaler))),
                       'HOVEREDC':     self.imageManager.getImageByCode("selectionBox_typeB_"+self.style+"_HOVEREDC",     self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}_{:d}".format(round(self.height/2*self.scaler), round(textBoxWidth*self.scaler))),
                       'PRESSEDC':     self.imageManager.getImageByCode("selectionBox_typeB_"+self.style+"_PRESSEDC",     self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}_{:d}".format(round(self.height/2*self.scaler), round(textBoxWidth*self.scaler))),
                       'DEFAULTO':     self.imageManager.getImageByCode("selectionBox_typeB_"+self.style+"_DEFAULTO",     self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}_{:d}".format(round(self.height/2*self.scaler), round(textBoxWidth*self.scaler))),
                       'HOVEREDO':     self.imageManager.getImageByCode("selectionBox_typeB_"+self.style+"_HOVEREDO",     self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}_{:d}".format(round(self.height/2*self.scaler), round(textBoxWidth*self.scaler))),
                       'PRESSEDO':     self.imageManager.getImageByCode("selectionBox_typeB_"+self.style+"_PRESSEDO",     self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}_{:d}".format(round(self.height/2*self.scaler), round(textBoxWidth*self.scaler))),
                       'INACTIVEMASK': self.imageManager.getImageByCode("selectionBox_typeB_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}_{:d}".format(round(self.height/2*self.scaler), round(textBoxWidth*self.scaler)))}
        
        self.mainBoxSprite = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['DEFAULTC'][0], batch = self.batch, group = self.group_0)
        self.textElement = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_1,
                                                                  text = "", defaultTextStyle = self.effectiveTextStyle['DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                  xPos = self.xPos, yPos = self.yPos, width = textBoxWidth, height = self.height, showElementBox = False, anchor = 'CENTER')
        self.inactiveMask = pyglet.sprite.Sprite(x = self.xPos * self.scaler, y = self.yPos * self.scaler, img = self.images['INACTIVEMASK'][0], batch = self.batch, group = self.group_2); self.inactiveMask.visible = False
        

        self.status = "DEFAULT"; self.statusDir = 'C'; self.lastFocusedBox = None
        self.hidden = False; self.deactivated = False

    def process(self, t_elapsed_ns):
        self.selectionBoxTypeA.process(t_elapsed_ns)

    def handleMouseEvent(self, event):
        if not((self.deactivated == True) or (self.hidden == True)):
            if   (self.hitBox.isTouched(event['x'], event['y']) == True):            focusedBox = 'MAINBOX'
            elif (self.selectionBoxTypeA.isTouched(event['x'], event['y']) == True): focusedBox = 'SELECTIONBOX'
            else:                                                                    focusedBox = None
            
            if (event['eType'] == "HOVERENTERED"):
                if (focusedBox == 'MAINBOX'):
                    if (self.status == 'DEFAULT'):
                        self.audioManager.playAudioByCode('button_typeA_HOVERED_A')
                        self.status = "HOVERED"
                        self.mainBoxSprite.image = self.images["HOVERED"+self.statusDir][0]
                elif (focusedBox == 'SELECTIONBOX'): self.selectionBoxTypeA.handleMouseEvent(event)
                if (self.hoverFunction != None): self.hoverFunction(self)
                self.lastFocusedBox = focusedBox

            elif (event['eType'] == "HOVERESCAPED"):
                if (self.lastFocusedBox == 'MAINBOX'):
                    if (self.status == 'HOVERED'):
                        self.status = "DEFAULT"
                        self.mainBoxSprite.image = self.images["DEFAULT"+self.statusDir][0]
                        if (self.hoverEscapeFunction != None): self.hoverEscapeFunction(self)
                elif (self.lastFocusedBox == 'SELECTIONBOX'): self.selectionBoxTypeA.handleMouseEvent(event)

            elif (event['eType'] == "DHOVERESCAPED"):
                if (self.lastFocusedBox == 'MAINBOX'):
                    if (self.selectionBoxTypeA.isHidden() == False):
                        self.status = "DEFAULT"
                        self.mainBoxSprite.image = self.images["DEFAULT"+self.statusDir][0]
                elif (self.lastFocusedBox == 'SELECTIONBOX'): self.selectionBoxTypeA.handleMouseEvent(event)

            elif (event['eType'] == "PRESSED"):
                if (focusedBox == 'MAINBOX'):
                    self.audioManager.playAudioByCode('button_typeA_PRESSED_A')
                    self.status = "PRESSED"
                    self.mainBoxSprite.image = self.images["PRESSED"+self.statusDir][0]
                    if (self.pressFunction != None): self.pressFunction(self)
                elif (focusedBox == 'SELECTIONBOX'): self.selectionBoxTypeA.handleMouseEvent(event)

            elif (event['eType'] == "RELEASED"):
                if (focusedBox == 'MAINBOX'):
                    if (self.status == "PRESSED"):
                        self.audioManager.playAudioByCode('button_typeA_RELEASED_A')
                        if (self.statusDir == 'C'):
                            if (0 < self.nDisplay_effective): self.selectionBoxTypeA.show()
                            self.status = "PRESSED"; self.statusDir = 'O'
                            self.mainBoxSprite.image = self.images['PRESSEDO'][0]
                        elif (self.statusDir == 'O'):
                            if (0 < self.nDisplay_effective): self.selectionBoxTypeA.hide()
                            self.status = "HOVERED"; self.statusDir = 'C'
                            self.mainBoxSprite.image = self.images['HOVEREDC'][0]
                        if (self.releaseFunction != None): self.releaseFunction(self)
                elif (focusedBox == 'SELECTIONBOX'): 
                    self.selectionBoxTypeA.handleMouseEvent(event)
                    #Check and handle new selection
                    newSelectedKeys = self.selectionBoxTypeA.getSelected()
                    nNewSelectedKeys = len(newSelectedKeys)
                    #If there exists a single new selected key
                    if ((nNewSelectedKeys == 1) and (newSelectedKeys[0] != self.selectedKey)):
                        self.selectedKey = newSelectedKeys[0]
                        selectedItemInfo = self.selectionBoxTypeA.getSelectionListItemInfo(self.selectedKey)
                        selectedItemText = self.visualManager.extractText(selectedItemInfo['text'])
                        self.textElement.setText(selectedItemText)
                        if (selectedItemInfo['textStyles'] == None): self.textElement.editTextStyle((0, len(selectedItemText)), 'DEFAULT')
                        else:
                            for textStyle in selectedItemInfo['textStyles']: self.textElement.editTextStyle(textStyle[0], textStyle[1])
                        if (self.selectionUpdateFunction != None): self.selectionUpdateFunction(self)
                        #Close the selectionBox
                        self.selectionBoxTypeA.hide()
                        self.status = "DEFAULT"; self.statusDir = 'C'
                        self.mainBoxSprite.image = self.images['DEFAULTC'][0]
                    #NOT SUPPOSED TO HAPPEN, placed only for possible debugging
                    elif (1 < nNewSelectedKeys): print(termcolor.colored("Abnormal Case Detected For 'selectionBox_typeB': nNewSelectedKeys == {:d}".format(nNewSelectedKeys), 'light_red'))
                elif (focusedBox == None):
                    if (self.statusDir == 'O'): self.selectionBoxTypeA.hide()
                    self.status = "DEFAULT"; self.statusDir = 'C'
                    self.mainBoxSprite.image = self.images['DEFAULTC'][0]


            elif (event['eType'] == "MOVED"):
                if   (focusedBox == 'MAINBOX') and (self.lastFocusedBox == 'SELECTIONBOX'): self.selectionBoxTypeA.handleMouseEvent({'eType': 'HOVERESCAPED', 'x': event['x'], 'y': event['y']})
                elif (focusedBox == 'SELECTIONBOX'):                                        
                    if (self.lastFocusedBox == 'MAINBOX'): self.selectionBoxTypeA.handleMouseEvent({'eType': 'HOVERENTERED', 'x': event['x'], 'y': event['y']})
                    else:                                  self.selectionBoxTypeA.handleMouseEvent(event)

            elif (event['eType'] == "DRAGGED"):
                self.selectionBoxTypeA.handleMouseEvent(event)

            elif (event['eType'] == "SCROLLED"):
                if (focusedBox == 'SELECTIONBOX'): self.selectionBoxTypeA.handleMouseEvent(event)

            elif (event['eType'] == "SELECTIONESCAPED"):
                self.selectionBoxTypeA.hide()
                self.status = "DEFAULT"; self.statusDir = 'C'
                self.mainBoxSprite.image = self.images["DEFAULT"+self.statusDir][0]

            self.lastFocusedBox = focusedBox

    def handleKeyEvent(self, event): pass

    def show(self):
        self.hidden = False
        self.mainBoxSprite.visible = True
        if (self.deactivated == True): self.inactiveMask.visible = True
        self.textElement.show()

    def hide(self):
        self.hidden = True
        self.mainBoxSprite.visible = False
        self.inactiveMask.visible = False
        self.textElement.hide()

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y
        if   (self.expansionDir == 0): self.selectionBoxTypeA.moveTo(x = self.xPos, y = self.yPos-(self.nDisplay_effective*self.height+50*2))
        elif (self.expansionDir == 1): self.selectionBoxTypeA.moveTo(x = self.xPos, y = self.yPos+self.height)
        self.mainBoxSprite.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.mainBoxSprite.z)
        self.inactiveMask.position  = (self.xPos*self.scaler, self.yPos*self.scaler, self.inactiveMask.z)
        self.textElement.moveTo(x = self.xPos, y = self.yPos)
        self.hitBox.reposition(xPos = self.xPos, yPos = self.yPos)

    def resize(self, width, height):
        self.width = width; self.height = height

        textBoxWidth = self.width-self.selectionBoxTypeA.scrollBarWidth-self.selectionBoxTypeA.internalGOffset*2
        self.images['DEFAULTC']     = self.imageManager.getImageByCode("selectionBox_typeB_"+self.style+"_DEFAULTC",     self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}_{:d}".format(round(self.height/2*self.scaler), round(textBoxWidth*self.scaler)))
        self.images['HOVEREDC']     = self.imageManager.getImageByCode("selectionBox_typeB_"+self.style+"_HOVEREDC",     self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}_{:d}".format(round(self.height/2*self.scaler), round(textBoxWidth*self.scaler)))
        self.images['PRESSEDC']     = self.imageManager.getImageByCode("selectionBox_typeB_"+self.style+"_PRESSEDC",     self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}_{:d}".format(round(self.height/2*self.scaler), round(textBoxWidth*self.scaler)))
        self.images['DEFAULTO']     = self.imageManager.getImageByCode("selectionBox_typeB_"+self.style+"_DEFAULTO",     self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}_{:d}".format(round(self.height/2*self.scaler), round(textBoxWidth*self.scaler)))
        self.images['HOVEREDO']     = self.imageManager.getImageByCode("selectionBox_typeB_"+self.style+"_HOVEREDO",     self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}_{:d}".format(round(self.height/2*self.scaler), round(textBoxWidth*self.scaler)))
        self.images['PRESSEDO']     = self.imageManager.getImageByCode("selectionBox_typeB_"+self.style+"_PRESSEDO",     self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}_{:d}".format(round(self.height/2*self.scaler), round(textBoxWidth*self.scaler)))
        self.images['INACTIVEMASK'] = self.imageManager.getImageByCode("selectionBox_typeB_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}_{:d}".format(round(self.height/2*self.scaler), round(textBoxWidth*self.scaler)))
        self.mainBoxSprite.image = self.images[self.status+self.statusDir][0]
        self.inactiveMask.image  = self.images['INACTIVEMASK'][0]
        self.textElement.changeSize(width = textBoxWidth, height = self.height)
        self.hitBox.resize(width = self.width, height = self.height)

        if (0 < self.nDisplay_effective):
            self.selectionBoxTypeA.resize(width = self.width, height = self.nDisplay_effective*self.height+50*2)
            if   (self.expansionDir == 0): self.selectionBoxTypeA.moveTo(x = self.xPos, y = self.yPos-(self.nDisplay_effective*self.height+50*2))
            elif (self.expansionDir == 1): self.selectionBoxTypeA.moveTo(x = self.xPos, y = self.yPos+self.height)

    def activate(self):
        if (self.hidden == False): self.inactiveMask.visible = False
        self.deactivated = False

    def deactivate(self):
        if (self.hidden == False): self.inactiveMask.visible = True
        self.deactivated = True

    def addTextStyle(self, textStyleCode, textStyle):
        self.effectiveTextStyle[textStyleCode] = textStyle.copy()
        self.effectiveTextStyle[textStyleCode]['font_size'] = self.fontSize
        self.textElement.addTextStyle(textStyleCode, self.effectiveTextStyle[textStyleCode])
        self.selectionBoxTypeA.addTextStyle(textStyleCode, textStyle)

    def setSelectionList(self, selectionList, displayTargets = None, keepSelected = False, callSelectionUpdateFunction = False):
        self.selectionBoxTypeA.setSelectionList(selectionList, displayTargets, keepSelected, callSelectionUpdateFunction)
        if   (displayTargets == 'all'): nDisplayTargets = len(selectionList)
        elif (displayTargets == None):  nDisplayTargets = 0
        else:                           nDisplayTargets = len(displayTargets)
        self.nDisplay_effective = min([nDisplayTargets, self.nDisplay_max])
        if (0 < self.nDisplay_effective):
            self.selectionBoxTypeA.resize(width = self.width, height = self.nDisplay_effective*self.height+50*2)
            if   (self.expansionDir == 0): self.selectionBoxTypeA.moveTo(x = self.xPos, y = self.yPos-(self.nDisplay_effective*self.height+50*2))
            elif (self.expansionDir == 1): self.selectionBoxTypeA.moveTo(x = self.xPos, y = self.yPos+self.height)
        if (len(self.selectionBoxTypeA.selectedKeysList) == 0):
            self.selectedKey = None
            self.textElement.deleteText('all')

    def clearSelectionList(self):
        self.selectionBoxTypeA.clearSelectionList()

    def editSelectionListItem(self, itemKey, item):
        self.selectionBoxTypeA.editSelectionListItem(itemKey, item)
        
    def setDisplayTargets(self, displayTargets):
        self.selectionBoxTypeA.setDisplayTargets(displayTargets)
        if   (displayTargets == 'all'): nDisplayTargets = len(self.selectionBoxTypeA.getSelectionList())
        elif (displayTargets == None):  nDisplayTargets = 0
        else:                           nDisplayTargets = len(displayTargets)
        self.nDisplay_effective = min([nDisplayTargets, self.nDisplay_max])
        if (0 < self.nDisplay_effective):
            self.selectionBoxTypeA.resize(width = self.width, height = self.nDisplay_effective*self.height+50*2)
            if   (self.expansionDir == 0): self.selectionBoxTypeA.moveTo(x = self.xPos, y = self.yPos-(self.nDisplay_effective*self.height+50*2))
            elif (self.expansionDir == 1): self.selectionBoxTypeA.moveTo(x = self.xPos, y = self.yPos+self.height)

    def setSelected(self, itemKey, callSelectionUpdateFunction = True):
        if (itemKey == None): self.selectionBoxTypeA.clearSelected()
        else:                 self.selectionBoxTypeA.addSelected(itemKey = itemKey, additionType = 1, callSelectionUpdateFunction = False)
        try:    newSelectedKey = self.selectionBoxTypeA.getSelected()[0]
        except: newSelectedKey = None
        if (self.selectedKey != newSelectedKey):
            self.selectedKey = newSelectedKey
            if (self.selectedKey == None): self.textElement.deleteText('all')
            else:                          self.textElement.setText(self.visualManager.extractText(self.selectionBoxTypeA.getSelectionListItemInfo(self.selectedKey)['text']))
            if ((callSelectionUpdateFunction == True) and (self.selectionUpdateFunction != None)): self.selectionUpdateFunction(self)
        
    def getSelected(self):
        return self.selectedKey

    def setName(self, name): self.name = name
    def getName(self): return self.name
    def isTouched(self, mouseX, mouseY):
        return ((self.hidden == False) and (self.hitBox.isTouched(mouseX, mouseY) or self.selectionBoxTypeA.isTouched(mouseX, mouseY)))
    def isHidden(self): return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        #Get the updated image and textStyle from the managers
        self.images['DEFAULTC'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULTC'][1])
        self.images['HOVEREDC'] = self.imageManager.getImageByLoadIndex(self.images['HOVEREDC'][1])
        self.images['PRESSEDC'] = self.imageManager.getImageByLoadIndex(self.images['PRESSEDC'][1])
        self.images['DEFAULTO'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULTO'][1])
        self.images['HOVEREDO'] = self.imageManager.getImageByLoadIndex(self.images['HOVEREDO'][1])
        self.images['PRESSEDO'] = self.imageManager.getImageByLoadIndex(self.images['PRESSEDO'][1])
        self.effectiveTextStyle = self.visualManager.getTextStyle('selectionBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        #Apply the updated image and textStyle
        self.mainBoxSprite.image = self.images[self.status+self.statusDir][0]
        self.textElement.on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['DEFAULT'])
        self.selectionBoxTypeA.on_GUIThemeUpdate()

    def on_LanguageUpdate(self, **kwargs):
        #Get the updated image and textStyle from the managers
        self.effectiveTextStyle = self.visualManager.getTextStyle('selectionBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        
        #Apply updated language font and text
        if (self.selectedKey != None):
            newText = self.visualManager.extractText(self.selectionBoxTypeA.getSelectionListItemInfo(self.selectedKey)['text'])
            self.textElement.on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'], newLanguageText = newText)

        self.selectionBoxTypeA.on_LanguageUpdate(**kwargs)
        if (self.statusDir == "C"): self.selectionBoxTypeA.hide()
        
    def getGroupRequirement(): return 14
#GUIO - 'selectionBox_typeB' END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'selectionBox_typeC' ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
GOBJECTSBUFFER_MAXLENGTH = 50
class selectionBox_typeC:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.group_2 = kwargs['group_2']
            self.group_3 = kwargs['group_3']
            self.group_4 = kwargs['group_4']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)
            self.group_2 = pyglet.graphics.Group(order = self.groupOrder+2)
            self.group_3 = pyglet.graphics.Group(order = self.groupOrder+3)
            self.group_4 = pyglet.graphics.Group(order = self.groupOrder+4)
        
        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.name = kwargs.get('name', None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.style = kwargs.get('style', 'styleA')

        self.fontSize = int(kwargs.get('fontSize', 100)*self.scaler)
        self.textStyle = kwargs.get('textStyle', 'default')
        self.effectiveTextStyle = self.visualManager.getTextStyle('selectionBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle: self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize

        self.scrollBarThickness = 100
        self.internalGOffset    = 50
        self.elementWidths = kwargs.get("elementWidths", (self.width-self.scrollBarThickness-self.internalGOffset*3,))
        self.nColumns = len(self.elementWidths)
        self.elementHeight = kwargs.get("elementHeight", 250)
        
        self.objectHitBox = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos, self.width, self.height)

        self.displayBox = (self.xPos+self.internalGOffset, self.yPos+self.scrollBarThickness+self.internalGOffset*2, self.width-self.scrollBarThickness-self.internalGOffset*3, self.height-self.scrollBarThickness-self.internalGOffset*3-self.elementHeight)
        self.displayBox_hitBox = atmEta_gui_HitBoxes.hitBox_Rectangular(self.displayBox[0], self.displayBox[1], self.displayBox[2], self.displayBox[3])
        
        #Functional Object Parameters
        self.hoverFunction       = kwargs.get('hoverFunction',       None)
        self.hoverEscapeFunction = kwargs.get('hoverEscapeFunction', None)
        self.pressFunction       = kwargs.get('pressFunction',       None)
        self.releaseFunction     = kwargs.get('releaseFunction',     None)
        self.selectionUpdateFunction = kwargs.get('selectionUpdateFunction', None)

        self.frameRadius = kwargs.get('frameRadius', 10)
        self.images = {'DEFAULT':      self.imageManager.getImageByCode("selectionBox_typeC_"+self.style+"_DEFAULT",      self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.frameRadius)),
                       'HOVERED':      self.imageManager.getImageByCode("selectionBox_typeC_"+self.style+"_HOVERED",      self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.frameRadius)),
                       'INACTIVEMASK': self.imageManager.getImageByCode("selectionBox_typeA_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.frameRadius))}

        self.frameSprite  = pyglet.sprite.Sprite(x = self.xPos*self.scaler, y = self.yPos*self.scaler, img = self.images['DEFAULT'][0],      batch = self.batch, group = self.group_0)
        self.inactiveMask = pyglet.sprite.Sprite(x = self.xPos*self.scaler, y = self.yPos*self.scaler, img = self.images['INACTIVEMASK'][0], batch = self.batch, group = self.group_4); self.inactiveMask.visible = False
        self.display_shapes_titleDivider = pyglet.shapes.Line(x = self.displayBox[0]*self.scaler,                      x2 = (self.displayBox[0]+self.displayBox[2])*self.scaler, 
                                                              y = (self.displayBox[1]+self.displayBox[3])*self.scaler, y2 = (self.displayBox[1]+self.displayBox[3])*self.scaler, 
                                                              width = 1, color = self.visualManager.getFromColorTable('SELECTIONBOX_TITLEDIVIDER'), 
                                                              batch = self.batch, group = self.group_1)
        
        #The scrollbar will use groupOrder (group_1 ~~~ group_4)
        if (groupOrder == None):
            self.scrollBar_H = scrollBar_typeA(scaler = self.scaler, batch = self.batch, imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager,
                                               xPos=self.xPos+self.internalGOffset, yPos=self.yPos+self.internalGOffset, width=self.width-self.internalGOffset*3-self.scrollBarThickness, height=self.scrollBarThickness,
                                               align = 'horizontal', style="styleA", group_0 = self.group_1, group_1 = self.group_2, group_2 = self.group_3, viewRangeUpdateFunction = self.__onViewRangeUpdate_ScrollBar)
            self.scrollBar_V = scrollBar_typeA(scaler = self.scaler, batch = self.batch, imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager,
                                               xPos=self.xPos+self.width-self.internalGOffset-self.scrollBarThickness, yPos=self.yPos+self.internalGOffset*2+self.scrollBarThickness, width=self.height-self.internalGOffset*3-self.scrollBarThickness, height=self.scrollBarThickness,
                                               align = 'vertical', style="styleA", group_0 = self.group_1, group_1 = self.group_2, group_2 = self.group_3, viewRangeUpdateFunction = self.__onViewRangeUpdate_ScrollBar)
        else:
            self.scrollBar_H = scrollBar_typeA(scaler = self.scaler, batch = self.batch, imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager,
                                               xPos=self.xPos+self.internalGOffset, yPos=self.yPos+self.internalGOffset, width=self.width-self.internalGOffset*3-self.scrollBarThickness, height=self.scrollBarThickness,
                                               align = 'horizontal', style="styleA", groupOrder=self.groupOrder+1, viewRangeUpdateFunction = self.__onViewRangeUpdate_ScrollBar)
            self.scrollBar_V = scrollBar_typeA(scaler = self.scaler, batch = self.batch, imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager,
                                               xPos=self.xPos+self.width-self.internalGOffset-self.scrollBarThickness, yPos=self.yPos+self.internalGOffset*2+self.scrollBarThickness, width=self.height-self.internalGOffset*3-self.scrollBarThickness, height=self.scrollBarThickness,
                                               align = 'vertical', style="styleA", groupOrder=self.groupOrder+1, viewRangeUpdateFunction = self.__onViewRangeUpdate_ScrollBar)


        self.highlightColor_HOVERED    = self.visualManager.getFromColorTable('SELECTIONBOX_HOVERED')
        self.highlightColor_PRESSED    = self.visualManager.getFromColorTable('SELECTIONBOX_PRESSED')
        self.highlightColor_HOVEREDSEL = self.visualManager.getFromColorTable('SELECTIONBOX_HOVEREDSEL')
        self.highlightColor_SELECTED   = self.visualManager.getFromColorTable('SELECTIONBOX_SELECTED')
        
        self.displayProjectionWidth_Max  = self.displayBox[2]*self.scaler
        self.displayProjectionHeight_Max = self.displayBox[3]*self.scaler
        self.displayTargetWidth_Max  = sum(self.elementWidths)*self.scaler
        self.displayTargetHeight_Max = 0
        self.displayProjection = [0, 0, self.displayProjectionWidth_Max, self.displayProjectionHeight_Max]

        if (groupOrder == None):
            self.display_camGroup_titles = atmEta_gui_AdvancedPygletGroups.cameraGroup(window = kwargs['windowInstance'], order = self.groupOrder+1, parentCameraGroup = self.group_0,
                                                                                       viewport_x      = self.displayBox[0]*self.scaler, 
                                                                                       viewport_y      = (self.displayBox[1]+self.displayBox[3])*self.scaler,
                                                                                       viewport_width  = self.displayBox[2]*self.scaler, 
                                                                                       viewport_height = self.elementHeight*self.scaler,
                                                                                       projection_x0 = 0, projection_x1 = self.displayBox[2]*self.scaler, projection_y0 = 0, projection_y1 = self.elementHeight*self.scaler)
            self.display_camGroup_elements = atmEta_gui_AdvancedPygletGroups.cameraGroup(window = kwargs['windowInstance'], order = self.groupOrder+1, parentCameraGroup = self.group_0,
                                                                                         viewport_x      = self.displayBox[0]*self.scaler,
                                                                                         viewport_y      = self.displayBox[1]*self.scaler,
                                                                                         viewport_width  = self.displayBox[2]*self.scaler,
                                                                                         viewport_height = self.displayBox[3]*self.scaler,
                                                                                         projection_x0 = 0, projection_x1 = self.displayBox[2]*self.scaler, projection_y0 = 0, projection_y1 = 1)
        else:
            self.display_camGroup_titles = atmEta_gui_AdvancedPygletGroups.cameraGroup(window = kwargs['windowInstance'], order = self.groupOrder+1,
                                                                                       viewport_x      = self.displayBox[0]*self.scaler, 
                                                                                       viewport_y      = (self.displayBox[1]+self.displayBox[3])*self.scaler, 
                                                                                       viewport_width  = self.displayBox[2]*self.scaler,
                                                                                       viewport_height = self.elementHeight*self.scaler,
                                                                                       projection_x0 = 0, projection_x1 = self.displayBox[2]*self.scaler, projection_y0 = 0, projection_y1 = self.elementHeight*self.scaler)
            self.display_camGroup_elements = atmEta_gui_AdvancedPygletGroups.cameraGroup(window = kwargs['windowInstance'], order = self.groupOrder+1,
                                                                                         viewport_x      = self.displayBox[0]*self.scaler, 
                                                                                         viewport_y      = self.displayBox[1]*self.scaler, 
                                                                                         viewport_width  = self.displayBox[2]*self.scaler, 
                                                                                         viewport_height = self.displayBox[3]*self.scaler,
                                                                                         projection_x0 = 0, projection_x1 = self.displayBox[2]*self.scaler, projection_y0 = 0, projection_y1 = 1)

        #Column Titles
        self.columnTitles = list()
        _ct_currentX = 0
        for _eWidth in self.elementWidths:
            self.columnTitles.append({'text':       "",
                                      'textAnchor': 'CENTER',
                                      'textStyles': None,
                                      'textElement': atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.display_camGroup_titles, text = "-", defaultTextStyle = self.effectiveTextStyle['DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                                          xPos = _ct_currentX, yPos = 0, width = _eWidth, height = self.elementHeight, showElementBox = False, anchor = 'CENTER')})
            _ct_currentX += _eWidth

        #Selection Dict
        #[Key]: Item ID
        #[Value][0]: Display Text
        #[Value][1]: Text Style (List of tuples [0]: targetRange, [1]: styleCode)
        #[Value][2]: Text Element SL
        #[Value][3]: Highlight Shape
        self.selectionList    = dict()
        self.selectedKeys     = dict()
        self.selectedKeysList = list()
        self.displayTargets     = dict()
        self.displayTargetsList = list()
        self.displayTargets_visibleIndexRange = None
        self.displayTargets_textUpdateProcessTimeLimit_ns = 100e6
        self.multiSelect                 = kwargs.get("multiSelect",                 False)
        self.singularSelect_allowRelease = kwargs.get("singularSelect_allowRelease", True)

        self.textElementsBuffer      = dict()
        self.textElementsBuffer_keys = list()
        self.hlShapeBuffer           = list()
        self.updateQueue             = set()

        #User Interaction Control
        self.interactionHandler_lastProcessed_ns   = 0
        self.interactionHandler_processInterval_ns = 10*1e6 #10ms
        
        self.mouseScrollDY = 0
        self.mouseScrollDX = 0
        self.mouseScroll_lastRelY = None
        self.mouseScroll_lastRelX = None
        self.previousHoveredItemKey = None
        
        self.scrollBarUpdated = False

        #Object Status Control
        self.status = "DEFAULT"
        self.hidden = False; self.deactivated = False

        #Internal Hashed Functions
        self.__mouseEventHandlers = {'HOVERENTERED': self.__hme_HOVERENTERED,
                                     'HOVERESCAPED': self.__hme_HOVERESCAPED,
                                     'PRESSED':      self.__hme_PRESSED,
                                     'RELEASED':     self.__hme_RELEASED,
                                     'MOVED':        self.__hme_MOVED,
                                     'DRAGGED':      self.__hme_DRAGGED,
                                     'SCROLLED':     self.__hme_SCROLLED}

        #Post-Initialization Action
        self.__updateDisplayElements()

    def process(self, t_elapsed_ns):
        #[1]: Interaction Control
        if ((self.interactionHandler_processInterval_ns <= time.perf_counter_ns() - self.interactionHandler_lastProcessed_ns)):
            #Mouse Scroll Interpreation
            if (self.mouseScrollDY != 0):
                #ViewRange Update
                projectionDelta = round(self.mouseScrollDY*self.elementHeight/4*self.scaler, 1)
                _newDisplayProjection_y0 = self.displayProjection[1]+projectionDelta
                _newDisplayProjection_y1 = self.displayProjection[3]+projectionDelta
                belowZeroDelta = -_newDisplayProjection_y0
                aboveMaxDelta  = _newDisplayProjection_y1-self.displayTargetHeight_Max
                if (0 < belowZeroDelta): _newDisplayProjection_y0 = 0;                                      _newDisplayProjection_y1 = _newDisplayProjection_y1+belowZeroDelta
                if (0 < aboveMaxDelta):  _newDisplayProjection_y0 = _newDisplayProjection_y0-aboveMaxDelta; _newDisplayProjection_y1 = self.displayTargetHeight_Max
                if ((_newDisplayProjection_y0 != self.displayProjection[1]) or (_newDisplayProjection_y1 != self.displayProjection[3])):
                    self.displayProjection[1] = _newDisplayProjection_y0
                    self.displayProjection[3] = _newDisplayProjection_y1
                    self.__onViewRangeUpdate(byScrollBar=False)
                #Item Hover Target Computation
                self.__findHoveredItem(self.mouseScroll_lastRelY)
                self.mouseScrollDY = 0
            #Scrollbar Update Interpreation
            if (self.scrollBarUpdated == True):
                #Update the viewRange accordingly with the scrollbar
                viewRange_x_sb = self.scrollBar_H.getViewRange(asInverse = False)
                viewRange_y_sb = self.scrollBar_V.getViewRange(asInverse = False)
                self.displayProjection = [viewRange_x_sb[0]/100*self.displayTargetWidth_Max,
                                          viewRange_y_sb[0]/100*self.displayTargetHeight_Max,
                                          viewRange_x_sb[1]/100*self.displayTargetWidth_Max,
                                          viewRange_y_sb[1]/100*self.displayTargetHeight_Max]
                self.__onViewRangeUpdate(byScrollBar=True)
                self.scrollBarUpdated = False
            #Update Timer
            self.interactionHandler_lastProcessed_ns = time.perf_counter_ns()
        #[2]: Update Queue
        t_beg_ns = time.perf_counter_ns()
        teb      = self.textElementsBuffer
        teb_keys = self.textElementsBuffer_keys
        hsb      = self.hlShapeBuffer
        selList  = self.selectionList
        uQueue   = self.updateQueue
        while ((uQueue) and (time.perf_counter_ns()-t_beg_ns < self.displayTargets_textUpdateProcessTimeLimit_ns)):
            itemKey = uQueue.pop()
            item = selList[itemKey]
            item_text       = item['text']
            item_textAnchor = item['textAnchor']
            item_textStyles = item['textStyles']
            item_tes        = item['textElement']
            item_hls        = item['highlightShape']
            item_display    = not(item['_rowHide'])
            item_hls_status = item['_hlsStatus']
            item_yCoord     = item['_yCoord']
            #[1]: Text Element & HighlightShape Initialization
            if ((item_tes is None) and (item_display == True)):
                #[1-1]: Text Elements Initialization
                #---[1-1-1]: Load from buffer
                if (teb):
                    bufferKey = itemKey if (itemKey in teb) else teb_keys[0]
                    tes = teb.pop(bufferKey)
                    teb_keys.remove(bufferKey)
                    xCoord = 0
                    for cIndex, eWidth in enumerate(self.elementWidths):
                        te = tes[cIndex]
                        if (te.getWidth() != eWidth):                         te.changeSize(width = eWidth)
                        if ((te.xPos != xCoord) or (te.yPos != item_yCoord)): te.moveTo(x = xCoord, y = item_yCoord)
                        te.show()
                        xCoord += eWidth
                #---[1-1-2]: Generate new text element instance
                else:
                    tes    = []
                    xCoord = 0
                    for cIndex, eWidth in enumerate(self.elementWidths):
                        te = atmEta_gui_TextControl.textObject_SL(scaler              = self.scaler, 
                                                                  batch               = self.batch, 
                                                                  group               = self.display_camGroup_elements, 
                                                                  text                = "", 
                                                                  defaultTextStyle    = self.effectiveTextStyle['DEFAULT'], 
                                                                  auxillaryTextStyles = self.effectiveTextStyle,
                                                                  xPos                = xCoord, 
                                                                  yPos                = item_yCoord, 
                                                                  width               = eWidth, 
                                                                  height              = self.elementHeight, 
                                                                  showElementBox      = False, 
                                                                  anchor              = item_textAnchor[cIndex])
                        tes.append(te)
                        xCoord += eWidth
                #---[1-1-3]: Text Updates
                for cIndex, te in enumerate(tes):
                    text_eff    = self.visualManager.extractText(item_text[cIndex])
                    text_styles = item_textStyles[cIndex]
                    if (te.getText() != text_eff): te.setText(text_eff)
                    if (text_styles is None): te.editTextStyle('all', 'DEFAULT')
                    else:
                        for tRange, tCode in text_styles:
                            if (tCode in self.effectiveTextStyle): te.editTextStyle(tRange, tCode)
                            else:                                  te.editTextStyle(tRange, 'DEFAULT')
                #[1-2]: Highlight Shape
                #---[1-2-1]: Load from buffer
                if (hsb):
                    hlShape = hsb.pop(-1)
                    hls_new_y     = item_yCoord*self.scaler
                    hls_new_color = item_hls_status[1]
                    if (hlShape.y     != hls_new_y):     hlShape.y     = hls_new_y
                    if (hlShape.color != hls_new_color): hlShape.color = hls_new_color
                #---[1-2-2]: Generate new shape instance
                else:
                    hlShape = pyglet.shapes.Rectangle(x      = 0, 
                                                      y      = item_yCoord*self.scaler, 
                                                      width  = self.displayTargetWidth_Max, 
                                                      height = self.elementHeight*self.scaler, 
                                                      batch  = self.batch, 
                                                      group  = self.display_camGroup_elements, 
                                                      color  = item_hls_status[1])
                hlShape.visible = item_hls_status[0]
                #[1-3]: Finally
                item['textElement']    = tes
                item['highlightShape'] = hlShape
            #[2]: Visibility & Coordinates Update
            else:
                #[2-1]: Is Visible
                if (item_display == True):
                    #[2-1-1]: Coordinates
                    if (item_tes is not None):
                        y_te_new  = item_yCoord
                        y_hls_new = item_yCoord*self.scaler
                        for te in item_tes:
                            if (te.yPos != y_te_new): te.moveTo(y = y_te_new)
                        if (item_hls.y != y_hls_new): item_hls.y = y_hls_new
                    #[2-1-2]: Highlight Shape Update
                    hls_new_visible = item_hls_status[0]
                    hls_new_color   = item_hls_status[1]
                    if (item_hls.visible != hls_new_visible): item_hls.visible = hls_new_visible
                    if (item_hls.color   != hls_new_color):   item_hls.color   = hls_new_color
                #[2-2]: Is Not Visible
                else:
                    if (item_tes is None): continue
                    #[2-2-1]: Add to buffer
                    for te in item_tes: te.hide()
                    item_hls.visible = False
                    teb[itemKey] = item_tes
                    teb_keys.append(itemKey)
                    hsb.append(item_hls)
                    #[2-2-2]: Remove oldest items in the buffer if overflowed
                    while (GOBJECTSBUFFER_MAXLENGTH <= len(teb)):
                        itemKey_oldest = teb_keys.pop(0)
                        for te in teb[itemKey_oldest]: te.delete()
                        teb.pop(itemKey_oldest)
                        hsb.pop(0).delete()
                    #[2-2-3]: Finally
                    item['textElement']    = None
                    item['highlightShape'] = None

    def handleMouseEvent(self, event):
        if ((self.deactivated == True) or (self.hidden == True)): return
        if (event['eType'] in self.__mouseEventHandlers): self.__mouseEventHandlers[event['eType']](event = event)
    def __hme_HOVERENTERED(self, event):
        self.audioManager.playAudioByCode('selectionBox_typeC_HOVERED_A')
        self.status = "HOVERED"
        self.frameSprite.image = self.images[self.status][0]
        if (self.hoverFunction != None): self.hoverFunction(self)
    def __hme_HOVERESCAPED(self, event):
        self.status = "DEFAULT"
        self.frameSprite.image = self.images[self.status][0]
        self.__releaseHoveredItem() #Release hovered item
        if (self.scrollBar_H.status == 'HOVERED'): self.scrollBar_H.handleMouseEvent({'eType': "HOVERESCAPED", 'x': event['x'], 'y': event['y']})
        if (self.scrollBar_V.status == 'HOVERED'): self.scrollBar_V.handleMouseEvent({'eType': "HOVERESCAPED", 'x': event['x'], 'y': event['y']})
    def __hme_PRESSED(self, event):
        if   (self.scrollBar_H.isTouched(event['x'], event['y']) == True): self.scrollBar_H.handleMouseEvent(event)
        elif (self.scrollBar_V.isTouched(event['x'], event['y']) == True): self.scrollBar_V.handleMouseEvent(event)
        #Pressing on the object
        else:
            #Object Interaction
            self.audioManager.playAudioByCode('selectionBox_typeC_PRESSED_A')
            self.status = "PRESSED"
            if (self.pressFunction is not None): self.pressFunction(self)
            self.__pressHoveredItem() #Press hovered item
    def __hme_RELEASED(self, event):
        #ScrollBar was pressed
        if   (self.scrollBar_H.status == 'PRESSED'): self.scrollBar_H.handleMouseEvent(event)
        elif (self.scrollBar_V.status == 'PRESSED'): self.scrollBar_V.handleMouseEvent(event)
        #Object was pressed
        elif (self.status == "PRESSED"):
            self.audioManager.playAudioByCode('selectionBox_typeC_RELEASED_A')
            self.status = "HOVERED"
            self.frameSprite.image = self.images[self.status][0]
            if (self.displayBox_hitBox.isTouched(event['x'], event['y']) == True): self.__selectHoveredItem(relativeY = (event['y']-self.displayBox[1])*self.scaler) #Select hovered item
            else:                                                                  self.__releaseHoveredItem() #Release hovered item
    def __hme_MOVED(self, event):
        #Scrollbar Control
        if (self.scrollBar_H.status == 'HOVERED'):
            if (self.scrollBar_H.isTouched(event['x'], event['y']) == False): self.scrollBar_H.handleMouseEvent({'eType': "HOVERESCAPED", 'x': event['x'], 'y': event['y']}) #Scrollbar Touched -> NotTouched
        else:
            if (self.scrollBar_H.isTouched(event['x'], event['y']) == True): self.scrollBar_H.handleMouseEvent({'eType': "HOVERENTERED", 'x': event['x'], 'y': event['y']}) #Scrollbar NotTouched -> Touched
        if (self.scrollBar_V.status == 'HOVERED'):
            if (self.scrollBar_V.isTouched(event['x'], event['y']) == False): self.scrollBar_V.handleMouseEvent({'eType': "HOVERESCAPED", 'x': event['x'], 'y': event['y']}) #Scrollbar Touched -> NotTouched
        else:
            if (self.scrollBar_V.isTouched(event['x'], event['y']) == True): self.scrollBar_V.handleMouseEvent({'eType': "HOVERENTERED", 'x': event['x'], 'y': event['y']}) #Scrollbar NotTouched -> Touched
        #DisplayBox Control
        if (self.displayBox_hitBox.isTouched(event['x'], event['y']) == True): self.__findHoveredItem(relativeY = (event['y']-self.displayBox[1])*self.scaler) #Find new hovered item
        else:                                                                  self.__releaseHoveredItem()                                                     #Release hovered item
    def __hme_DRAGGED(self, event):
        #Scroll Bar Update
        if   (self.scrollBar_H.status == 'PRESSED'): self.scrollBar_H.handleMouseEvent(event)
        elif (self.scrollBar_V.status == 'PRESSED'): self.scrollBar_V.handleMouseEvent(event)
    def __hme_SCROLLED(self, event):
        #Scroll Delta Update
        if (self.displayBox_hitBox.isTouched(event['x'], event['y']) == True):
            self.mouseScrollDX += event['scroll_x']
            self.mouseScrollDY += event['scroll_y']
            self.mouseScroll_lastRelX = (event['x']-self.displayBox[0])*self.scaler
            self.mouseScroll_lastRelY = (event['y']-self.displayBox[1])*self.scaler

    def handleKeyEvent(self, event): 
        pass

    def show(self):
        self.hidden = False
        self.frameSprite.visible = True
        self.display_camGroup_titles.show()
        self.display_camGroup_elements.show()
        self.scrollBar_H.show()
        self.scrollBar_V.show()
        self.display_shapes_titleDivider.visible = True
        if (self.deactivated == True): self.inactiveMask.visible = True

    def hide(self):
        self.hidden = True
        self.frameSprite.visible = False
        self.display_camGroup_titles.hide()
        self.display_camGroup_elements.hide()
        self.scrollBar_H.hide()
        self.scrollBar_V.hide()
        self.inactiveMask.visible = False
        self.display_shapes_titleDivider.visible = False
        self.__releaseHoveredItem()

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y
        self.frameSprite.position  = (self.xPos*self.scaler, self.yPos*self.scaler, self.frameSprite.z)
        self.inactiveMask.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.inactiveMask.z)
        self.objectHitBox.reposition(xPos = self.xPos, yPos = self.yPos)
        self.scrollBar_H.moveTo(x = self.xPos+self.internalGOffset, y = self.yPos+self.internalGOffset)
        self.scrollBar_V.moveTo(x = self.xPos+self.width-self.internalGOffset-self.scrollBarThickness, y = self.yPos+self.internalGOffset*2+self.scrollBarThickness)
        self.displayBox = (self.xPos+self.internalGOffset, self.yPos+self.scrollBarThickness+self.internalGOffset*2, self.width-self.scrollBarThickness-self.internalGOffset*3, self.height-self.scrollBarThickness-self.internalGOffset*3)
        self.displayBox_hitBox.reposition(xPos = self.displayBox[0], yPos = self.displayBox[1])
        self.display_camGroup_titles.updateViewport(viewport_x=self.displayBox[0]*self.scaler, viewport_y=(self.displayBox[1]+self.displayBox[3])*self.scaler)
        self.display_camGroup_elements.updateViewport(viewport_x=self.displayBox[0]*self.scaler, viewport_y=self.displayBox[1]*self.scaler)

    def resize(self, width, height):
        self.width  = width
        self.height = height

        self.objectHitBox.resize(width = self.width, height = self.height)
        self.displayBox = (self.xPos+self.internalGOffset, self.yPos+self.scrollBarThickness+self.internalGOffset*2, self.width-self.scrollBarThickness-self.internalGOffset*3, self.height-self.scrollBarThickness-self.internalGOffset*3-self.elementHeight)
        self.displayBox_hitBox.resize(width = self.displayBox[2], height = self.displayBox[3])

        self.images['DEFAULT']      = self.imageManager.getImageByCode("selectionBox_typeC_"+self.style+"_DEFAULT",      self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.frameRadius))
        self.images['HOVERED']      = self.imageManager.getImageByCode("selectionBox_typeC_"+self.style+"_HOVERED",      self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.frameRadius))
        self.images['INACTIVEMASK'] = self.imageManager.getImageByCode("selectionBox_typeC_"+self.style+"_INACTIVEMASK", self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(self.frameRadius))
        self.frameSprite.image  = self.images[self.status][0]
        self.inactiveMask.image = self.images['INACTIVEMASK'][0]

        self.scrollBar_H.resize(self.width-self.internalGOffset*3-self.scrollBarThickness, self.scrollBar.height)
        self.scrollBar_H.moveTo(x = self.xPos+self.internalGOffset, y = self.yPos+self.internalGOffset)
        self.scrollBar_V.resize(self.height-self.internalGOffset*3-self.scrollBarThickness, self.scrollBar.height)
        self.scrollBar_V.moveTo(x = self.xPos+self.width-self.internalGOffset-self.scrollBarThickness, y = self.yPos+self.internalGOffset*2+self.scrollBarThickness)
            
        self.display_camGroup_titles.updateViewport(viewport_width = self.displayBox[2]*self.scaler)
        self.display_camGroup_elements.updateViewport(viewport_width = self.displayBox[2]*self.scaler, viewport_height = self.displayBox[3]*self.scaler)

        self.__updateDisplayElements()

    def activate(self):
        self.deactivated = False
        self.inactiveMask.visible = False

    def deactivate(self):
        self.deactivated = True
        if (self.hidden == False): self.inactiveMask.visible = True

    def addTextStyle(self, textStyleCode, textStyle):
        self.effectiveTextStyle[textStyleCode] = textStyle.copy()
        self.effectiveTextStyle[textStyleCode]['font_size'] = self.fontSize
        etStyle_toApply = self.effectiveTextStyle[textStyleCode]
        for item in self.selectionList.values():
            item_te = item['textElement']
            if (item_te is not None):
                for te_col in item_te: te_col.addTextStyle(textStyleCode, etStyle_toApply)

    #<Column Titles Control>
    def editColumnTitles(self, columnTitles):
        cts_current = self.columnTitles
        for _cIndex, _ct in enumerate(columnTitles):
            ct_current = cts_current[_cIndex]
            if ('textAnchor' in _ct): 
                ct_current['textAnchor'] = _ct['textAnchor']
                ct_current['textElement'].setAnchor(_ct['textAnchor'])
            if ('text' in _ct): 
                ct_current['text'] = _ct['text']
                ct_current['textElement'].setText(self.visualManager.extractText(_ct['text']))
            if ('textStyles' in _ct):
                ct_current['textStyles'] = _ct['textStyles']
                for textStyle in _ct['textStyles']:
                    targetRange, targetCode = textStyle
                    if (targetCode in self.effectiveTextStyle): ct_current['textElement'].editTextStyle(targetRange, targetCode)
                    else:                                       ct_current['textElement'].editTextStyle(targetRange, 'DEFAULT')

    #<Selection List Control>
    def setSelectionList(self, selectionList, displayTargets = None, keepSelected = False, callSelectionUpdateFunction = True):
        selList = self.selectionList

        #[1]: If Selected Keys are to be conserved, save a copy of the previsouly selected keys list
        if (keepSelected == True): 
            selectedKeysList_prev = self.selectedKeysList
            self.selectedKeysList = []

        #[2]: Initialize SelectionList and Display Control Variables
        self.clearSelectionList(callSelectionUpdateFunction = False)
        self.previousHoveredItemKey = None

        #[3]: Update Selection List
        _cRange = range (0, self.nColumns)
        for rIndex, itemKey in enumerate(selectionList):
            item = selectionList[itemKey]
            selList[itemKey] = {'text':           [item[_cIndex]['text']                     for _cIndex in _cRange],
                                'textStyles':     [item[_cIndex].get('textStyles', None)     for _cIndex in _cRange],
                                'textAnchor':     [item[_cIndex].get('textAnchor', 'CENTER') for _cIndex in _cRange],
                                'textElement':    None,
                                'highlightShape': None,
                                'index':          rIndex,
                                '_rowHide':       False,
                                '_yCoord':        0,
                                '_hlsStatus':     [False, self.highlightColor_HOVERED]}
        self.updateQueue.update(selectionList)

        #[4]: Add back selected items that are still existing
        if (keepSelected == True):
            selKeys = self.selectedKeys
            selectedKeysList_stillExisting = (_itemKey for _itemKey in selectedKeysList_prev if (_itemKey in self.selectionList))
            for index, itemKey in enumerate(selectedKeysList_stillExisting):
                selKeys[itemKey] = index
                selList[itemKey]['_hlsStatus'] = [True, self.highlightColor_SELECTED]
                self.selectedKeysList.append(itemKey)

        #[5]: Post SelectionList Update Actions
        if (displayTargets is None): self.__updateDisplayElements()
        else:                        self.setDisplayTargets(displayTargets)
        
        #[6]: Call Selection Update Function if needed
        if ((callSelectionUpdateFunction == True) and (self.selectionUpdateFunction is not None)): self.selectionUpdateFunction(self)

    def clearSelectionList(self, callSelectionUpdateFunction = True):
        #[1]: Initialize SelectionList and Display Control Variables
        self.displayTargetHeight_Max = 0
        self.displayProjection = [0, 0, self.displayProjectionWidth_Max, self.displayProjectionHeight_Max]

        #[2]: Text Elements Delete
        for item in self.selectionList.values():
            item_tes = item['textElement']
            if (item_tes is None): continue
            for te in item_tes: te.delete()
        for tes in self.textElementsBuffer.values():
            for te in tes: te.delete()
        for hls in self.hlShapeBuffer: hls.delete()
        
        #[3]: Data Clearing
        self.textElementsBuffer.clear()
        self.textElementsBuffer_keys.clear()
        self.hlShapeBuffer.clear()
        self.selectionList.clear()
        self.selectedKeys.clear()
        self.selectedKeysList.clear()
        self.displayTargets.clear()
        self.displayTargetsList.clear()
        self.displayTargets_visibleIndexRange = None
        self.updateQueue.clear()

        #[4]: Reset ViewRange
        self.__onViewRangeUpdate()

        #[5]: Call Selection Update Function if needed
        if ((callSelectionUpdateFunction == True) and (self.selectionUpdateFunction != None)): self.selectionUpdateFunction(self)

    def editSelectionListItem(self, itemKey, item, columnIndex):
        selList = self.selectionList
        if (itemKey not in selList):       return
        if (self.nColumns <= columnIndex): return

        item_current = selList[itemKey]
        item_current_t  = item_current['text']
        item_current_te = item_current['textElement']
        item_current_ts = item_current['textStyles']
        item_current_ta = item_current['textAnchor']
        item_current_t_this  = item_current_t[columnIndex]
        item_current_ts_this = item_current_ts[columnIndex]
        item_current_ta_this = item_current_ta[columnIndex]

        #Update need check
        _updated_text       = False
        _updated_textStyles = False
        _updated_textAnchor = False
        if (('text'       in item) and (item['text']       != item_current_t_this)):  item_current_t[columnIndex]  = item['text'];       _updated_text = True; _updated_textStyles = True
        if (('textStyles' in item) and (item['textStyles'] != item_current_ts_this)): item_current_ts[columnIndex] = item['textStyles']; _updated_textStyles = True
        if (('textAnchor' in item) and (item['textAnchor'] != item_current_ta_this)): item_current_ta[columnIndex] = item['textAnchor']; _updated_textAnchor = True

        #Contents Update (Only needs to be handled here if textElement is already initialized)
        if (item_current_te is None): return
        item_current_t_this  = item_current_t[columnIndex]
        item_current_te_this = item_current_te[columnIndex]
        item_current_ts_this = item_current_ts[columnIndex]
        item_current_ta_this = item_current_ta[columnIndex]
        effectiveText = self.visualManager.extractText(item_current_t_this)
        #---[1]: Text Anchor
        if (_updated_textAnchor == True): 
            item_current_te_this.setAnchor(item_current_ta_this)
        #---[2]: Text
        if (_updated_text == True): 
            item_current_te_this.setText(effectiveText)
        #---[3]: Text Styles
        if (_updated_textStyles == True):
            if (item_current_ts_this is None): item_current_te_this.editTextStyle((0, len(effectiveText)), 'DEFAULT')
            else:
                for _targetRange, _targetCode in item_current_ts_this:
                    if (_targetCode in self.effectiveTextStyle): item_current_te_this.editTextStyle(_targetRange, _targetCode)
                    else:                                        item_current_te_this.editTextStyle(_targetRange, 'DEFAULT')
                
    def getSelectionListItemInfo(self, itemKey, columnIndex = None):
        selList = self.selectionList
        nCols   = self.nColumns

        if (itemKey not in selList):                             return None
        if (columnIndex is not None) and (nCols <= columnIndex): return None

        item  = selList[itemKey]
        if (columnIndex is None):
            item_return = {'text':          item['text'].copy(),
                           'effectiveText': [None]*nCols,
                           'textStyles':    item['textStyles'].copy(), 
                           'textAnchor':    item['textAnchor'].copy(), 
                           'index':         item['index'], 
                           'isSelected':    itemKey in self.selectedKeys}
            item_tes = item['textElement']
            if (item_tes is not None): item_return['effectiveText'] = [item_te.getText() for item_te in item_tes]
        else:
            item_return = {'text':          item['text'][columnIndex],
                           'effectiveText': None,
                           'textStyles':    item['textStyles'][columnIndex], 
                           'textAnchor':    item['textAnchor'][columnIndex], 
                           'index':         item['index'],
                           'isSelected':    itemKey in self.selectedKeys}
            item_tes = item['textElement']
            if (item_tes is not None): item_return['effectiveText'] = item_tes[columnIndex].getText()

        return item_return

    def getSelectionList(self):
        returnDict = dict()
        nCols = self.nColumns
        for itemKey, item in self.selectionList.items():
            returnDict_item = {'text':          item['text'].copy(),
                               'effectiveText': [None]*nCols,
                               'textStyles':    item['textStyles'].copy(), 
                               'textAnchor':    item['textAnchor'].copy(),
                               'index':         item['index'], 
                               'isSelected':    itemKey in self.selectedKeys}
            item_tes = item['textElement']
            if (item_tes is not None): returnDict_item['effectiveText'] = [item_te.getText() for item_te in item_tes]
            returnDict[itemKey] = returnDict_item
        return returnDict

    def getSelectionListKeys(self):
        return list(self.selectionList.keys())



    #<Display Target Control>
    def setDisplayTargets(self, displayTargets, resetViewPosition = True):
        #[1]: Hide all items
        selList = self.selectionList
        for _itemKey in self.displayTargets: selList[_itemKey]['_rowHide'] = True
        self.updateQueue.update(self.displayTargets)
        self.displayTargets_visibleIndexRange = None
        #[2]: Update display targets
        dispTargets    = self.displayTargets
        dispTargetList = self.displayTargetsList
        dispTargets.clear()
        dispTargetList.clear()
        if (displayTargets == 'all'):
            for _index, _key in enumerate(self.selectionList): dispTargets[_key] = _index
            dispTargetList.extend(self.selectionList)
        else:
            for _index, _key in enumerate(displayTargets): dispTargets[_key] = _index
            dispTargetList.extend(displayTargets)
        #[3]: Update Display Elements
        self.__updateDisplayElements(resetViewPosition = resetViewPosition)



    #<Selected Items Control>
    def addSelected(self, itemKey, additionType = 0, callSelectionUpdateFunction = True):
        selKeys     = self.selectedKeys
        selKeysList = self.selectedKeysList
        selList     = self.selectionList

        if (itemKey not in selList): return False
        if (itemKey in     selKeys): return False

        if (self.multiSelect == False): self.clearSelected(callSelectionUpdateFunction = callSelectionUpdateFunction)

        selKeys[itemKey] = len(selKeys)
        selKeysList.append(itemKey)

        item = selList[itemKey]
        item['_hlsStatus'][0] = True
        if   (additionType == 0): item['_hlsStatus'][1] = self.highlightColor_SELECTED
        elif (additionType == 1): item['_hlsStatus'][1] = self.highlightColor_HOVEREDSEL

        self.updateQueue.add(itemKey)

        if ((callSelectionUpdateFunction == True) and (self.selectionUpdateFunction is not None)): 
            self.selectionUpdateFunction(self)

        return True

    def removeSelected(self, itemKey, removalType = 0, callSelectionUpdateFunction = True):
        selKeys     = self.selectedKeys
        selKeysList = self.selectedKeysList
        selList     = self.selectionList

        if not((itemKey in selList) and (itemKey in selKeys)): return False

        if not((self.multiSelect == False) and (self.singularSelect_allowRelease == False)):
            selectionIndex = selKeys[itemKey]
            for selectedkey in selKeys:
                if (selectionIndex < selKeys[selectedkey]): selKeys[selectedkey] -= 1
            if   (removalType == 0): selList[itemKey]['_hlsStatus'][0] = False
            elif (removalType == 1): selList[itemKey]['_hlsStatus'][1] = self.highlightColor_HOVERED
            self.updateQueue.add(itemKey)
            del selKeys[itemKey]
            selKeysList.pop(selectionIndex)
            if ((callSelectionUpdateFunction == True) and (self.selectionUpdateFunction is not None)): self.selectionUpdateFunction(self)
            return True
        
        elif (removalType == 1): 
            selList[itemKey]['_hlsStatus'][1] = self.highlightColor_HOVEREDSEL
            self.updateQueue.add(itemKey)
            return True
        
        return False

    def clearSelected(self, callSelectionUpdateFunction = True):
        selList = self.selectionList
        for selectedkey in self.selectedKeys:
            item = selList[selectedkey]
            if (self.previousHoveredItemKey == selectedkey): item['_hlsStatus'][1] = self.highlightColor_HOVERED
            else:                                            item['_hlsStatus'][0] = False
            self.updateQueue.add(selectedkey)
        self.selectedKeys.clear()
        self.selectedKeysList.clear()
        if ((callSelectionUpdateFunction == True) and (self.selectionUpdateFunction is not None)): self.selectionUpdateFunction(self)

    def getSelected(self):
        return self.selectedKeysList.copy()



    #<Internal Functions>
    def __updateDisplayElements(self, resetViewPosition = True):
        #[1]: X Coordinate Display Projection Update
        if resetViewPosition:
            dProj_x0 = 0
            dProj_x1 = min(self.displayProjectionWidth_Max, self.displayTargetWidth_Max)
            self.displayProjection[0] = dProj_x0
            self.displayProjection[2] = dProj_x1

        #[2]: Y Coordinate Display Projection Update
        self.displayTargetHeight_Max = len(self.displayTargets)*self.elementHeight*self.scaler
        dpHeight_prev = self.displayProjection[3]-self.displayProjection[1]
        dpHeight_new  = min(self.displayProjectionHeight_Max, self.displayTargetHeight_Max)
        if resetViewPosition or self.displayTargetHeight_Max < self.displayProjection[3] or (dpHeight_prev != dpHeight_new): dProj_y1 = self.displayTargetHeight_Max
        else:                                                                                                                dProj_y1 = self.displayProjection[3]
        dProj_y0 = dProj_y1-dpHeight_new
        self.displayProjection[1] = dProj_y0
        self.displayProjection[3] = dProj_y1

        #[3]: Elements Camera Group Visiblity
        if self.displayTargetHeight_Max == 0:
            self.display_camGroup_elements.visible = False
        elif not self.display_camGroup_elements.visible and not self.hidden: 
            self.display_camGroup_elements.visible = True

        #[4]: View Range Update
        self.__onViewRangeUpdate()

        #[5]: Item Coordinates Update Queue
        selList  = self.selectionList
        dTargets = self.displayTargets
        eHeight  = self.elementHeight
        for itemKey, dTargetIndex in dTargets.items(): selList[itemKey]['_yCoord'] = (len(self.displayTargets)-dTargetIndex-1) * eHeight
        self.updateQueue.update(dTargets)

    def __releaseHoveredItem(self):
        if (self.previousHoveredItemKey is None):                   return
        if (self.previousHoveredItemKey not in self.selectionList): return
        _item = self.selectionList[self.previousHoveredItemKey]
        if (self.previousHoveredItemKey in self.selectedKeys):
            _item['_hlsStatus'][1] = self.highlightColor_SELECTED
            if (_item['highlightShape'] is None): self.updateQueue.add(self.previousHoveredItemKey)
            else:                                 _item['highlightShape'].color = _item['_hlsStatus'][1]
        else:
            _item['_hlsStatus'][0] = False
            if (_item['highlightShape'] is None): self.updateQueue.add(self.previousHoveredItemKey)
            else:                                 _item['highlightShape'].visible = _item['_hlsStatus'][0]
        self.previousHoveredItemKey = None

    def __pressHoveredItem(self):
        if (self.previousHoveredItemKey is None): return
        _item = self.selectionList[self.previousHoveredItemKey]
        _item['_hlsStatus'][0] = True
        _item['_hlsStatus'][1] = self.highlightColor_PRESSED
        if (_item['highlightShape'] is None): self.updateQueue.add(self.previousHoveredItemKey)
        else:
            _item['highlightShape'].visible = _item['_hlsStatus'][0]
            _item['highlightShape'].color   = _item['_hlsStatus'][1]

    def __findHoveredItem(self, relativeY):
        #Find the new hovered index and key
        yWithinDisplaySpace = relativeY+self.displayProjection[1]
        maxDelta = self.displayProjectionHeight_Max - self.displayTargetHeight_Max
        if (0 < maxDelta): yWithinDisplaySpace -= maxDelta
        if ((0 <= yWithinDisplaySpace) and (yWithinDisplaySpace < self.displayTargetHeight_Max)): 
            indexPosition = len(self.displayTargets)-int(yWithinDisplaySpace/(self.elementHeight*self.scaler))-1
            newHoveredKey = self.displayTargetsList[indexPosition]
        else: 
            newHoveredKey = None

        #If hovered item key has not changed, return
        if (newHoveredKey == self.previousHoveredItemKey): return

        #Release previously hovered item
        if (self.previousHoveredItemKey is not None):
            _item = self.selectionList[self.previousHoveredItemKey]
            if (self.previousHoveredItemKey in self.selectedKeys): _item['_hlsStatus'][1] = self.highlightColor_SELECTED
            else:                                                  _item['_hlsStatus'][0] = False
            if (_item['highlightShape'] is None): self.updateQueue.add(self.previousHoveredItemKey)
            else:
                if (self.previousHoveredItemKey in self.selectedKeys): _item['highlightShape'].color   = _item['_hlsStatus'][1]
                else:                                                  _item['highlightShape'].visible = _item['_hlsStatus'][0]

        #Highlight newly hovered item
        if (newHoveredKey is not None):
            _item = self.selectionList[newHoveredKey]
            _item['_hlsStatus'][0] = True
            if (newHoveredKey in self.selectedKeys): _item['_hlsStatus'][1] = self.highlightColor_HOVEREDSEL
            else:                                    _item['_hlsStatus'][1] = self.highlightColor_HOVERED
            if (_item['highlightShape'] is None): self.updateQueue.add(newHoveredKey)
            else:
                _item['highlightShape'].visible = _item['_hlsStatus'][0]
                _item['highlightShape'].color   = _item['_hlsStatus'][1]
        self.previousHoveredItemKey = newHoveredKey

    def __selectHoveredItem(self, relativeY):
        #Find the new hovered index
        yWithinDisplaySpace = relativeY+self.displayProjection[1]
        maxDelta = self.displayProjectionHeight_Max - self.displayTargetHeight_Max
        if (0 < maxDelta): yWithinDisplaySpace -= maxDelta
        if ((0 <= yWithinDisplaySpace) and (yWithinDisplaySpace < self.displayTargetHeight_Max)): 
            indexPosition = len(self.displayTargets)-int(yWithinDisplaySpace/(self.elementHeight*self.scaler))-1
            itemKeyOnRelease = self.displayTargetsList[indexPosition]
        else:
            itemKeyOnRelease = None

        #Compare the previous and the new hovered item, and add selection if needed
        if (self.previousHoveredItemKey == itemKeyOnRelease): 
            if (itemKeyOnRelease in self.selectedKeys): self.removeSelected(itemKey = itemKeyOnRelease, removalType  = 1, callSelectionUpdateFunction = True)
            else:                                       self.addSelected(itemKey    = itemKeyOnRelease, additionType = 1, callSelectionUpdateFunction = True)
            return
        
        #Release previously hovered item
        if (self.previousHoveredItemKey is not None):
            _item = self.selectionList[self.previousHoveredItemKey]
            if (self.previousHoveredItemKey in self.selectedKeys): 
                _item['_hlsStatus'][1] = self.highlightColor_SELECTED
                if (_item['highlightShape'] is None): self.updateQueue.add(self.previousHoveredItemKey)
                else:                                 _item['highlightShape'].color = _item['_hlsStatus'][1]
            else:                                                  
                _item['_hlsStatus'][0] = False
                if (_item['highlightShape'] is None): self.updateQueue.add(self.previousHoveredItemKey)
                else:                                 _item['highlightShape'].visible = _item['_hlsStatus'][0]

        #Highlight newly hovered item
        if (itemKeyOnRelease is not None):
            _item = self.selectionList[itemKeyOnRelease]
            _item['_hlsStatus'][0] = True
            if (itemKeyOnRelease in self.selectedKeys): _item['_hlsStatus'][1] = self.highlightColor_HOVEREDSEL
            else:                                       _item['_hlsStatus'][1] = self.highlightColor_HOVERED
            if (_item['highlightShape'] is None): self.updateQueue.add(itemKeyOnRelease)
            else:
                _item['highlightShape'].visible = _item['_hlsStatus'][0]
                _item['highlightShape'].color   = _item['_hlsStatus'][1]
        self.previousHoveredItemKey = itemKeyOnRelease

    def __onViewRangeUpdate(self, byScrollBar = False):
        #[1]: Display Projection X
        #---[1-1]: Scroll Bar
        if (byScrollBar == False): self.scrollBar_H.editViewRange((self.displayProjection[0]/self.displayTargetWidth_Max*100, self.displayProjection[2]/self.displayTargetWidth_Max*100), asInverse = False)
        #---[1-2]: Cam Group
        cg_proj_x0, cg_proj_x1 = self.displayProjection[0], self.displayProjection[2]
        maxDelta = self.displayProjectionWidth_Max-self.displayTargetWidth_Max
        if (0 < maxDelta): cg_vp_width = self.displayTargetWidth_Max
        else:              cg_vp_width = self.displayProjectionWidth_Max
        self.display_camGroup_titles.updateProjection(projection_x0  =cg_proj_x0, projection_x1=cg_proj_x1)
        self.display_camGroup_elements.updateProjection(projection_x0=cg_proj_x0, projection_x1=cg_proj_x1)
        self.display_camGroup_titles.updateViewport(viewport_width   = cg_vp_width)
        self.display_camGroup_elements.updateViewport(viewport_width = cg_vp_width)

        #[2]: Display Projection Y
        #---[2-1]: Scroll Bar
        if (self.displayTargetHeight_Max == 0):
            self.scrollBar_V.editViewRange(viewRange = (0, 100), asInverse = False)
        elif (byScrollBar == False):
            self.scrollBar_V.editViewRange(viewRange = (self.displayProjection[1]/self.displayTargetHeight_Max*100, 
                                                        self.displayProjection[3]/self.displayTargetHeight_Max*100), 
                                           asInverse = False)
        #---[2-2]: Cam Group
        if (self.displayTargetHeight_Max == 0):
            self.display_camGroup_elements.visible = False
        else:
            cg_proj_y0, cg_proj_y1 = self.displayProjection[1], self.displayProjection[3]
            maxDelta = self.displayProjectionHeight_Max-self.displayTargetHeight_Max
            if (0 < maxDelta): 
                cg_vp_y      = self.displayBox[1]*self.scaler+maxDelta
                cg_vp_height = self.displayTargetHeight_Max
            else:              
                cg_vp_y      = self.displayBox[1]*self.scaler
                cg_vp_height = self.displayProjectionHeight_Max
            self.display_camGroup_elements.updateProjection(projection_y0=cg_proj_y0, projection_y1=cg_proj_y1)
            self.display_camGroup_elements.updateViewport(viewport_y = cg_vp_y, viewport_height = cg_vp_height)
            if (self.hidden == False): self.display_camGroup_elements.visible = True

        #Set visibilities of items
        _nDisplayTargets = len(self.displayTargetsList)
        vdtIdx_new_beg = _nDisplayTargets-int(self.displayProjection[3]/(self.elementHeight*self.scaler))-1
        vdtIdx_new_end = _nDisplayTargets-int(self.displayProjection[1]/(self.elementHeight*self.scaler))-1
        _nEffectiveVisibleRows = (vdtIdx_new_end-vdtIdx_new_beg+1)*1
        vdtIdx_new_beg -= _nEffectiveVisibleRows
        vdtIdx_new_end += _nEffectiveVisibleRows
        if (vdtIdx_new_beg < 0):                 vdtIdx_new_beg = 0
        if (_nDisplayTargets <= vdtIdx_new_end): vdtIdx_new_end = _nDisplayTargets-1
        #---Find extended indexes to show and hide
        keysToShow = []
        keysToHide = []
        if (self.displayTargets_visibleIndexRange is None):
            keysToShow.extend(self.displayTargetsList[vdtIdx_new_beg:vdtIdx_new_end+1])
        else:
            vdtIdx_prev_beg, vdtIdx_prev_end = self.displayTargets_visibleIndexRange
            if (vdtIdx_new_end < vdtIdx_prev_beg) or (vdtIdx_prev_end < vdtIdx_new_beg):
                keysToHide.extend(self.displayTargetsList[vdtIdx_prev_beg : vdtIdx_prev_end+1])
                keysToShow.extend(self.displayTargetsList[vdtIdx_new_beg : vdtIdx_new_end+1])
            else:
                if (vdtIdx_prev_beg < vdtIdx_new_beg):  keysToHide.extend(self.displayTargetsList[vdtIdx_prev_beg  : vdtIdx_new_beg])
                if (vdtIdx_new_end  < vdtIdx_prev_end): keysToHide.extend(self.displayTargetsList[vdtIdx_new_end+1 : vdtIdx_prev_end+1])
                if (vdtIdx_new_beg  < vdtIdx_prev_beg): keysToShow.extend(self.displayTargetsList[vdtIdx_new_beg   : vdtIdx_prev_beg])
                if (vdtIdx_prev_end < vdtIdx_new_end):  keysToShow.extend(self.displayTargetsList[vdtIdx_prev_end+1: vdtIdx_new_end +1])
        #---Show items that are newly visible and hide items that are no longer visible
        selList = self.selectionList
        for _itemKey in keysToShow: selList[_itemKey]['_rowHide'] = False
        for _itemKey in keysToHide: selList[_itemKey]['_rowHide'] = True
        if (keysToShow or keysToHide): self.updateQueue.update(keysToShow, keysToHide)

        #Update the tracker
        self.displayTargets_visibleIndexRange = (vdtIdx_new_beg, vdtIdx_new_end)
        
    def __onViewRangeUpdate_ScrollBar(self, objectInstance): 
        self.scrollBarUpdated = True


    
    #<GUIO Basics>
    def setName(self, name): 
        self.name = name

    def getName(self): 
        return self.name
    
    def isTouched(self, mouseX, mouseY): 
        return ((self.hidden == False) and (self.objectHitBox.isTouched(mouseX, mouseY) == True))
    
    def isHidden(self): 
        return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        #Get the updated image and textStyle from the managers
        self.images['DEFAULT'] = self.imageManager.getImageByLoadIndex(self.images['DEFAULT'][1])
        self.images['HOVERED'] = self.imageManager.getImageByLoadIndex(self.images['HOVERED'][1])
        if (self.status == 'PRESSED'): self.frameSprite.image = self.images['HOVERED'][0]
        else:                          self.frameSprite.image = self.images[self.status][0]
        self.effectiveTextStyle = self.visualManager.getTextStyle('selectionBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle.keys(): self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        self.highlightColor_HOVERED    = self.visualManager.getFromColorTable('SELECTIONBOX_HOVERED')
        self.highlightColor_PRESSED    = self.visualManager.getFromColorTable('SELECTIONBOX_PRESSED')
        self.highlightColor_HOVEREDSEL = self.visualManager.getFromColorTable('SELECTIONBOX_HOVEREDSEL')
        self.highlightColor_SELECTED   = self.visualManager.getFromColorTable('SELECTIONBOX_SELECTED')
        #Apply the updated image and textStyle
        #---Frame
        self.frameSprite.image = self.images[self.status][0]
        #---Titles
        for _cTitle in self.columnTitles:
            for textStyleCode in self.effectiveTextStyle: _cTitle['textElement'].addTextStyle(textStyleCode, self.effectiveTextStyle[textStyleCode])
            _cTitle['textElement'].on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['DEFAULT'])
        self.display_shapes_titleDivider.color = self.visualManager.getFromColorTable('SELECTIONBOX_TITLEDIVIDER')
        #---Selection List
        for _itemKey in self.selectionList:
            _item = self.selectionList[_itemKey]
            #Text Element
            if (_item['textElement'] is not None):
                for _cIndex in range (0, self.nColumns):
                    for textStyleCode in self.effectiveTextStyle: _item['textElement'][_cIndex].addTextStyle(textStyleCode, self.effectiveTextStyle[textStyleCode])
                    _item['textElement'][_cIndex].on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['DEFAULT'])
            #Highlight Shape
            if (_itemKey in self.selectedKeys):
                if (_itemKey == self.previousHoveredItemKey): 
                    if (_item['highlightShape'] is not None): _item['highlightShape'].color = self.highlightColor_HOVEREDSEL
                    _item['_hlsStatus'][1] = self.highlightColor_HOVEREDSEL
                else:                                         
                    if (_item['highlightShape'] is not None): _item['highlightShape'].color = self.highlightColor_SELECTED
                    _item['_hlsStatus'][1] = self.highlightColor_SELECTED
            else:
                if (_itemKey == self.previousHoveredItemKey): 
                    if (_item['highlightShape'] is not None): _item['highlightShape'].color = self.highlightColor_HOVERED
                    _item['_hlsStatus'][1] = self.highlightColor_HOVERED
        #ScrollBar GUI Theme Update
        self.scrollBar_H.on_GUIThemeUpdate()
        self.scrollBar_V.on_GUIThemeUpdate()

    def on_LanguageUpdate(self, **kwargs):
        #Get the updated image and textStyle from the managers
        self.effectiveTextStyle = self.visualManager.getTextStyle('selectionBox_'+self.textStyle)
        for styleMode in self.effectiveTextStyle: self.effectiveTextStyle[styleMode]['font_size'] = self.fontSize
        #Apply updated language font and text
        _cRange = range(0, self.nColumns)
        #---Titles
        for _cIndex in _cRange:
            _newEffectiveText = self.visualManager.extractText(self.columnTitles[_cIndex]['text'])
            self.columnTitles[_cIndex]['textElement'].on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'], newLanguageText = _newEffectiveText)
        #---Selection List
        for _itemKey in self.selectionList:
            _item = self.selectionList[_itemKey]
            if (_item['textElement'] is not None):
                for _cIndex in _cRange:
                    _newEffectiveText     = self.visualManager.extractText(_item['text'][_cIndex])
                    _newEffectiveText_len = len(_newEffectiveText)
                    _item['textElement'][_cIndex].on_LanguageUpdate(newLanguageFont = kwargs['newLanguageFont'], newLanguageText = _newEffectiveText)
                    if (_item['textStyles'][_cIndex] is None): _item['textElement'][_cIndex].editTextStyle((0, _newEffectiveText_len), 'DEFAULT')
                    else:
                        for _textStyle in _item['textStyles'][_cIndex]:
                            _targetRange = _textStyle[0]
                            _targetCode  = _textStyle[1]
                            if (_targetCode in self.effectiveTextStyle): _item['textElement'][_cIndex].editTextStyle(_targetRange, _targetCode)
                            else:                                        _item['textElement'][_cIndex].editTextStyle(_targetRange, 'DEFAULT')
        
    def getGroupRequirement(): return 4
#GUIO - 'selectionBox_typeC' END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#GUIO - 'subPageBox_typeA' ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class subPageBox_typeA:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.window = kwargs['windowInstance']
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']

        self.guioConfig = kwargs['guioConfig']

        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        
        self.ipcA = kwargs['ipcA']
        
        self.baseInitParams = {'windowInstance': self.window, 'batch': self.batch, 'scaler': self.scaler, 'guioConfig': self.guioConfig, 'sysFunctions': kwargs['sysFunctions'], 'imageManager': self.imageManager, 'audioManager': self.audioManager, 'visualManager': self.visualManager,
                               'ipcA': self.ipcA}

        groupOrder = kwargs.get('groupOrder', None)
        if (groupOrder == None):
            self.group_0 = kwargs['group_0']
            self.group_1 = kwargs['group_1']
            self.group_2 = kwargs['group_2']
            self.group_3 = kwargs['group_3']
            self.groupOrder = self.group_0.order
        else:
            self.groupOrder = groupOrder
            self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
            self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)
            self.group_2 = pyglet.graphics.Group(order = self.groupOrder+2)
            self.group_3 = pyglet.graphics.Group(order = self.groupOrder+3)
        
        #Object Properties
        self.name = kwargs.get('name', None)
        self.xPos  = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.style = kwargs.get('style', 'styleA')
        self.hitBox = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos, self.width, self.height)
        
        #Internal Object Positioning
        self.projectionScrollBar_H = None
        self.projectionScrollBar_V = None
        useScrollBar_H = kwargs.get('useScrollBar_H', False)
        useScrollBar_V = kwargs.get('useScrollBar_V', False)
        self.scrollBarHeight = kwargs.get('scrollBarHeight', 100)
        self.style_scrollBar = kwargs.get('style_scrollBar', 'styleA')
        self.gOffset = 50

        if (self.style == None):
            if (useScrollBar_H == True):
                #Use H & V
                if (useScrollBar_V == True):
                    scrollBar_H_x      = self.xPos
                    scrollBar_H_y      = self.yPos
                    scrollBar_H_width  = self.width-self.scrollBarHeight-self.gOffset
                    scrollBar_V_x      = self.xPos+self.width-self.scrollBarHeight
                    scrollBar_V_y      = self.yPos+self.scrollBarHeight+self.gOffset
                    scrollBar_V_width  = self.height-self.scrollBarHeight-self.gOffset
                    spe_viewport_x      = (self.xPos)*self.scaler
                    spe_viewport_y      = (self.yPos+self.scrollBarHeight+self.gOffset)*self.scaler
                    spe_viewport_width  = (self.width-self.scrollBarHeight-self.gOffset)*self.scaler
                    spe_viewport_height = (self.height-self.scrollBarHeight-self.gOffset)*self.scaler
                #Use H Only
                else:
                    scrollBar_H_x      = self.xPos
                    scrollBar_H_y      = self.yPos
                    scrollBar_H_width  = self.width
                    spe_viewport_x      = (self.xPos)*self.scaler
                    spe_viewport_y      = (self.yPos+self.scrollBarHeight+self.gOffset)*self.scaler
                    spe_viewport_width  = (self.width)*self.scaler
                    spe_viewport_height = (self.height-self.scrollBarHeight-self.gOffset)*self.scaler
            else:
                #Use V Only
                if (useScrollBar_V == True):
                    scrollBar_V_x      = self.xPos+self.width-self.scrollBarHeight
                    scrollBar_V_y      = self.yPos
                    scrollBar_V_width  = self.height
                    spe_viewport_x      = (self.xPos)*self.scaler
                    spe_viewport_y      = (self.yPos)*self.scaler
                    spe_viewport_width  = (self.width-self.scrollBarHeight-self.gOffset)*self.scaler
                    spe_viewport_height = (self.height)*self.scaler
                #No ScrollBar
                else:
                    spe_viewport_x      = (self.xPos)*self.scaler
                    spe_viewport_y      = (self.yPos)*self.scaler
                    spe_viewport_width  = (self.width)*self.scaler
                    spe_viewport_height = (self.height)*self.scaler
        else:
            if (useScrollBar_H == True):
                #Use H & V
                if (useScrollBar_V == True):
                    scrollBar_H_x      = self.xPos+self.gOffset
                    scrollBar_H_y      = self.yPos+self.gOffset
                    scrollBar_H_width  = self.width-self.gOffset*3-self.scrollBarHeight
                    scrollBar_V_x      = self.xPos+self.width-self.gOffset-self.scrollBarHeight
                    scrollBar_V_y      = self.yPos+self.gOffset*2+self.scrollBarHeight
                    scrollBar_V_width  = self.height-self.gOffset*3-self.scrollBarHeight
                    spe_viewport_x      = (self.xPos+self.gOffset)*self.scaler
                    spe_viewport_y      = (self.yPos+self.gOffset*2+self.scrollBarHeight)*self.scaler
                    spe_viewport_width  = (self.width -self.gOffset*3-self.scrollBarHeight)*self.scaler
                    spe_viewport_height = (self.height-self.gOffset*3-self.scrollBarHeight)*self.scaler
                #Use H Only
                else:
                    scrollBar_H_x      = self.xPos+self.gOffset
                    scrollBar_H_y      = self.yPos+self.gOffset
                    scrollBar_H_width  = self.width-self.gOffset*2
                    spe_viewport_x      = (self.xPos+self.gOffset)*self.scaler
                    spe_viewport_y      = (self.yPos+self.gOffset*2+self.scrollBarHeight)*self.scaler
                    spe_viewport_width  = (self.width -self.gOffset*2)*self.scaler
                    spe_viewport_height = (self.height-self.gOffset*3-self.scrollBarHeight)*self.scaler
            else:
                #Use V Only
                if (useScrollBar_V == True):
                    scrollBar_V_x      = self.xPos+self.width-self.gOffset-self.scrollBarHeight
                    scrollBar_V_y      = self.yPos+self.gOffset
                    scrollBar_V_width  = self.height-self.gOffset*2
                    spe_viewport_x      = (self.xPos+self.gOffset)*self.scaler
                    spe_viewport_y      = (self.yPos+self.gOffset)*self.scaler
                    spe_viewport_width  = (self.width -self.gOffset*3-self.scrollBarHeight)*self.scaler
                    spe_viewport_height = (self.height-self.gOffset*2)*self.scaler
                #No ScrollBar
                else:
                    spe_viewport_x      = (self.xPos+self.gOffset)*self.scaler
                    spe_viewport_y      = (self.yPos+self.gOffset)*self.scaler
                    spe_viewport_width  = (self.width-self.gOffset*2)*self.scaler
                    spe_viewport_height = (self.height-self.gOffset*2)*self.scaler

            self.frameRadius = kwargs.get('frameRadius', 50)
            self.images = {'FRAME': self.imageManager.getImageByCode("subPageBox_typeA_"+self.style, self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(int(self.frameRadius*self.scaler)))}
            self.frameSprite = pyglet.sprite.Sprite(x = self.xPos*self.scaler, y = self.yPos*self.scaler, img = self.images['FRAME'][0], batch = self.batch, group = self.group_0)
        self.spe_viewport_full = (spe_viewport_x, spe_viewport_y, spe_viewport_width, spe_viewport_height)

        #The scrollbar will use groupOrder (group_1 ~~~ group_3)
        if (groupOrder == None):
            #print(self.name, self.group_0.projection_x0_effective, self.group_0.projection_x1_effective, self.group_0.projection_y0_effective, self.group_0.projection_y1_effective)
            self.layeredCamGroup = atmEta_gui_AdvancedPygletGroups.layeredCameraGroup(window = self.window, parentCameraGroup = self.group_0, viewport_x = spe_viewport_x, viewport_y = spe_viewport_y, viewport_width = spe_viewport_width, viewport_height = spe_viewport_height)
            if (useScrollBar_H == True): self.projectionScrollBar_H = scrollBar_typeA(**self.baseInitParams, name = 'psb_H', xPos=scrollBar_H_x, yPos=scrollBar_H_y, width=scrollBar_H_width, height=self.scrollBarHeight, align = 'horizontal', style=self.style_scrollBar, group_0 = self.group_1, group_1 = self.group_2, group_2 = self.group_3, viewRangeUpdateFunction = self.__onProjectionScrollBarUpdate, viewRange = (0, 100))
            if (useScrollBar_V == True): self.projectionScrollBar_V = scrollBar_typeA(**self.baseInitParams, name = 'psb_V', xPos=scrollBar_V_x, yPos=scrollBar_V_y, width=scrollBar_V_width, height=self.scrollBarHeight, align = 'vertical',   style=self.style_scrollBar, group_0 = self.group_1, group_1 = self.group_2, group_2 = self.group_3, viewRangeUpdateFunction = self.__onProjectionScrollBarUpdate, viewRange = (0, 100))
        else:
            self.layeredCamGroup = atmEta_gui_AdvancedPygletGroups.layeredCameraGroup(window = self.window, order = self.groupOrder, viewport_x = spe_viewport_x, viewport_y = spe_viewport_y, viewport_width = spe_viewport_width, viewport_height = spe_viewport_height)
            if (useScrollBar_H == True): self.projectionScrollBar_H = scrollBar_typeA(**self.baseInitParams, name = 'psb_H', xPos=scrollBar_H_x, yPos=scrollBar_H_y, width=scrollBar_H_width, height=self.scrollBarHeight, align = 'horizontal', style=self.style_scrollBar, groupOrder=self.groupOrder+1, viewRangeUpdateFunction = self.__onProjectionScrollBarUpdate, viewRange = (0, 100))
            if (useScrollBar_V == True): self.projectionScrollBar_V = scrollBar_typeA(**self.baseInitParams, name = 'psb_V', xPos=scrollBar_V_x, yPos=scrollBar_V_y, width=scrollBar_V_width, height=self.scrollBarHeight, align = 'vertical',   style=self.style_scrollBar, groupOrder=self.groupOrder+1, viewRangeUpdateFunction = self.__onProjectionScrollBarUpdate, viewRange = (0, 100))
        
        #Subpage GUIO Control
        self.GUIOs = dict()
        self.GUIOs_displayStatus = dict()
        self.hoveredGUIO  = None
        self.selectedGUIO = None
        self.projectionSpaceBoundary_x0 = None; self.projectionSpaceBoundary_x1 = None
        self.projectionSpaceBoundary_y0 = None; self.projectionSpaceBoundary_y1 = None
        self.projectionViewRange = [None, None, None, None]
        self.hoveredGUIO_object  = None
        self.selectedGUIO_object = None
        
        #Projection Scroll Buffer
        self.projectionScroll_interpretationInterval = 10e6
        self.projectionScroll_lastInterpreted = 0
        self.projectionScroll_dx = 0
        self.projectionScroll_dy = 0
        self.projectionScroll_accelerationFactor = 5

        #Object Status
        self.hidden = False

    def process(self, t_elapsed_ns):
        currentTime_ns = time.perf_counter_ns()
        if (self.projectionScroll_interpretationInterval <= currentTime_ns - self.projectionScroll_lastInterpreted):
            if (self.projectionScroll_dx != 0): self.__updateProjection(updateType = 3)
            if (self.projectionScroll_dy != 0): self.__updateProjection(updateType = 4)
            self.projectionScroll_lastInterpreted = currentTime_ns

        for guioInstance in self.GUIOs.values(): guioInstance.process(t_elapsed_ns)
             
    def handleMouseEvent(self, event):
        projectionSpaceCoordinate = self.layeredCamGroup.getProjectionSpaceCoordinate(event['x']*self.scaler, event['y']*self.scaler)
        event_projectionSpace = event.copy()
        event_projectionSpace['x'] = projectionSpaceCoordinate[0]/self.scaler
        event_projectionSpace['y'] = projectionSpaceCoordinate[1]/self.scaler

        hoveredWithinObject = None
        eventXScaled = event['x']*self.scaler; eventYScaled = event['y']*self.scaler
        if   ((self.projectionScrollBar_H != None) and (self.projectionScrollBar_H.isTouched(event['x'], event['y']) == True)): hoveredWithinObject = 'psb_H'
        elif ((self.projectionScrollBar_V != None) and (self.projectionScrollBar_V.isTouched(event['x'], event['y']) == True)): hoveredWithinObject = 'psb_V'
        elif ((self.spe_viewport_full[0] <= eventXScaled)                           and
              (eventXScaled <= self.spe_viewport_full[0]+self.spe_viewport_full[2]) and
              (self.spe_viewport_full[1] <= eventYScaled)                           and
              (eventYScaled <= self.spe_viewport_full[1]+self.spe_viewport_full[3])): hoveredWithinObject = 'lcg'

        if (event['eType'] == "MOVED"): #x, y, dx, dy
            if (hoveredWithinObject == self.hoveredGUIO_object):
                if (hoveredWithinObject == 'lcg'):
                    newHovered = self.__findGUIOAtPosition(event_projectionSpace['x'], event_projectionSpace['y'])
                    if (newHovered == self.hoveredGUIO): 
                        if (self.hoveredGUIO != None): self.GUIOs[self.hoveredGUIO].handleMouseEvent(event_projectionSpace)
                    else:
                        if (newHovered != None):       self.GUIOs[newHovered].handleMouseEvent({'eType': "HOVERENTERED", 'x': event_projectionSpace['x'], 'y': event_projectionSpace['y']})
                        if (self.hoveredGUIO != None): self.GUIOs[self.hoveredGUIO].handleMouseEvent({'eType': "HOVERESCAPED", 'x': event_projectionSpace['x'], 'y': event_projectionSpace['y']}) 
                    self.hoveredGUIO = newHovered
            else:
                if   (hoveredWithinObject == 'psb_H'):     self.projectionScrollBar_H.handleMouseEvent({'eType': "HOVERENTERED", 'x': event['x'], 'y': event['y']})
                elif (hoveredWithinObject == 'psb_V'):     self.projectionScrollBar_V.handleMouseEvent({'eType': "HOVERENTERED", 'x': event['x'], 'y': event['y']})
                elif (hoveredWithinObject == 'lcg'):
                    newHovered = self.__findGUIOAtPosition(event_projectionSpace['x'], event_projectionSpace['y'])
                    if (newHovered != None): self.GUIOs[newHovered].handleMouseEvent({'eType': "HOVERENTERED", 'x': event_projectionSpace['x'], 'y': event_projectionSpace['y']})
                if   (self.hoveredGUIO_object == 'psb_H'): self.projectionScrollBar_H.handleMouseEvent({'eType': "HOVERESCAPED", 'x': event['x'], 'y': event['y']})
                elif (self.hoveredGUIO_object == 'psb_V'): self.projectionScrollBar_V.handleMouseEvent({'eType': "HOVERESCAPED", 'x': event['x'], 'y': event['y']})
                elif (self.hoveredGUIO_object == 'lcg'):
                    if (self.hoveredGUIO != None): self.GUIOs[self.hoveredGUIO].handleMouseEvent({'eType': "HOVERESCAPED", 'x': event_projectionSpace['x'], 'y': event_projectionSpace['y']})
                
        elif (event['eType'] == "PRESSED"): #x, y, button, modifiers
            if   (self.hoveredGUIO_object == 'psb_H'): self.projectionScrollBar_H.handleMouseEvent(event)
            elif (self.hoveredGUIO_object == 'psb_V'): self.projectionScrollBar_V.handleMouseEvent(event)
            elif (self.hoveredGUIO_object == 'lcg'):
                if (self.hoveredGUIO != self.selectedGUIO):
                    if (self.selectedGUIO != None): self.GUIOs[self.selectedGUIO].handleMouseEvent({'eType': "SELECTIONESCAPED", 'x': event_projectionSpace['x'], 'y': event_projectionSpace['y'], 'button': event_projectionSpace['button'], 'modifiers': event_projectionSpace['modifiers']})
                    self.selectedGUIO = self.hoveredGUIO
                if (self.hoveredGUIO != None): self.GUIOs[self.hoveredGUIO].handleMouseEvent(event_projectionSpace)
            self.selectedGUIO_object = self.hoveredGUIO_object

        elif (event['eType'] == "RELEASED"): #x, y, button, modifiers
            if (self.selectedGUIO_object != None):
                if   (self.selectedGUIO_object == 'psb_H'): self.projectionScrollBar_H.handleMouseEvent(event)
                elif (self.selectedGUIO_object == 'psb_V'): self.projectionScrollBar_V.handleMouseEvent(event)
                elif (self.selectedGUIO_object == 'lcg'):
                    if (self.selectedGUIO != None): self.GUIOs[self.selectedGUIO].handleMouseEvent(event_projectionSpace)
                    if (self.hoveredGUIO != self.selectedGUIO): #If mouse was released after a 'drag', find the object at the mouse release location and send 'HOVERENTERED' and 'HOVERESCAPED' signal to the corresponding objects
                        if (self.hoveredGUIO != None):  self.GUIOs[self.hoveredGUIO].handleMouseEvent({'eType': "HOVERENTERED", 'x': event_projectionSpace['x'], 'y': event_projectionSpace['y']})
                        if (self.selectedGUIO != None): self.GUIOs[self.selectedGUIO].handleMouseEvent({'eType': "HOVERESCAPED", 'x': event_projectionSpace['x'], 'y': event_projectionSpace['y']})
                
        elif (event['eType'] == "DRAGGED"): #x, y, dx, dy, button, modifiers
            if (self.selectedGUIO_object != None):
                if   (self.selectedGUIO_object == 'psb_H'): self.projectionScrollBar_H.handleMouseEvent(event)
                elif (self.selectedGUIO_object == 'psb_V'): self.projectionScrollBar_V.handleMouseEvent(event)
                elif (self.selectedGUIO_object == 'lcg'):
                    newHovered = self.__findGUIOAtPosition(event_projectionSpace['x'], event_projectionSpace['y'])
                    if (self.selectedGUIO != None): self.GUIOs[self.selectedGUIO].handleMouseEvent(event_projectionSpace)
                    if (newHovered != self.hoveredGUIO):
                        if (newHovered != None):       self.GUIOs[newHovered].handleMouseEvent({'eType': "DHOVERENTERED", 'x': event_projectionSpace['x'], 'y': event_projectionSpace['y'], 'selectedGUIO': self.selectedGUIO})   #To newly hovered object
                        if (self.hoveredGUIO != None): self.GUIOs[self.hoveredGUIO].handleMouseEvent({'eType': "DHOVERESCAPED", 'x': event_projectionSpace['x'], 'y': event_projectionSpace['y']})                                #To previously hovered object
                        self.hoveredGUIO = newHovered
            
        elif (event['eType'] == "SCROLLED"): #x, y, scroll_x, scroll_y
            if (self.selectedGUIO == None):
                self.projectionScroll_dx += event['scroll_x']
                self.projectionScroll_dy += event['scroll_y']
            else:
                selectedGUIOType = type(self.GUIOs[self.selectedGUIO])
                if ((selectedGUIOType == selectionBox_typeA) or (selectedGUIOType == selectionBox_typeB) or (selectedGUIOType == selectionBox_typeC) or (selectedGUIOType == subPageBox_typeA) or (selectedGUIOType == atmEta_gui_ChartDrawer.chartDrawer)): 
                    self.GUIOs[self.selectedGUIO].handleMouseEvent(event_projectionSpace)
                else:
                    self.projectionScroll_dx += event['scroll_x']
                    self.projectionScroll_dy += event['scroll_y']

        elif (event['eType'] == "SELECTIONESCAPED"):
            if (self.selectedGUIO != None): self.GUIOs[self.selectedGUIO].handleMouseEvent({'eType': "SELECTIONESCAPED", 'x': event_projectionSpace['x'], 'y': event_projectionSpace['y'], 'button': event_projectionSpace['button'], 'modifiers': event_projectionSpace['modifiers']})

        elif (event['eType'] == "HOVERESCAPED"):
            if (self.hoveredGUIO != None): self.GUIOs[self.hoveredGUIO].handleMouseEvent(event)

        self.hoveredGUIO_object = hoveredWithinObject

    def __findGUIOAtPosition(self, mouseX, mouseY):
        touchedObjects = list()
        for objectName in self.GUIOs.keys():
            if ((self.GUIOs[objectName].isTouched(mouseX, mouseY) == True) and (self.GUIOs[objectName].isHidden() == False)): touchedObjects.append(objectName)
        lastTarget = None
        for objectName in touchedObjects:
            if (lastTarget == None):                                                      lastTarget = objectName
            elif (self.GUIOs[lastTarget].groupOrder < self.GUIOs[objectName].groupOrder): lastTarget = objectName
        return lastTarget

    def handleKeyEvent(self, event):
        if (self.selectedGUIO != None): self.GUIOs[self.selectedGUIO].handleKeyEvent(event)

    def __onProjectionScrollBarUpdate(self, objectInstance):
        if   (objectInstance.name == 'psb_H'): self.__updateProjection(updateType = 1)
        elif (objectInstance.name == 'psb_V'): self.__updateProjection(updateType = 2)

    def __updateProjection(self, updateType):
        """
        [updateType == 0]: Projection Boundary Updated
        [updateType == 1]: Projection ScrollBar H Updated
        [updateType == 2]: Projection ScrollBar V Updated
        [updateType == 3]: Mouse Scrolled H
        [updateType == 4]: Mouse Scrolled V
        """
        if (updateType == 0):
            projectionBoundaryWidth_onViewportSpace  = (self.projectionSpaceBoundary_x1-self.projectionSpaceBoundary_x0)*self.scaler
            projectionBoundaryHeight_onViewportSpace = (self.projectionSpaceBoundary_y1-self.projectionSpaceBoundary_y0)*self.scaler
            #<X>
            appliedViewport_x = self.spe_viewport_full[0]
            if (projectionBoundaryWidth_onViewportSpace < self.spe_viewport_full[2]):
                appliedViewport_width = projectionBoundaryWidth_onViewportSpace
                appliedProjection_x0 = self.projectionSpaceBoundary_x0*self.scaler
                appliedProjection_x1 = self.projectionSpaceBoundary_x1*self.scaler
            else:
                appliedViewport_width = self.spe_viewport_full[2]
                if (self.projectionViewRange[0] == None):
                    appliedProjection_x0 = self.projectionSpaceBoundary_x0*self.scaler
                    appliedProjection_x1 = appliedProjection_x0 + appliedViewport_width
                else:
                    #If 'overBoundaryDelta' is positive, the previous view range exceeds the new projectionSpaceBoundary
                    overBoundaryDelta_left  = self.projectionSpaceBoundary_x0*self.scaler       - self.projectionViewRange[0]
                    overBoundaryDelta_right = self.projectionViewRange[0]+appliedViewport_width - self.projectionSpaceBoundary_x1*self.scaler
                    if (0 < overBoundaryDelta_left):
                        appliedProjection_x0 = self.projectionSpaceBoundary_x0*self.scaler
                        appliedProjection_x1 = appliedProjection_x0+appliedViewport_width
                    elif (0 < overBoundaryDelta_right):
                        appliedProjection_x1 = self.projectionSpaceBoundary_x1*self.scaler
                        appliedProjection_x0 = appliedProjection_x1-appliedViewport_width
                    else:
                        appliedProjection_x0 = self.projectionViewRange[0]
                        appliedProjection_x1 = self.projectionViewRange[0]+appliedViewport_width
            #<Y>
            if (projectionBoundaryHeight_onViewportSpace < self.spe_viewport_full[3]): 
                appliedViewport_height = projectionBoundaryHeight_onViewportSpace
                appliedViewport_y = self.spe_viewport_full[1] + self.spe_viewport_full[3] - projectionBoundaryHeight_onViewportSpace
                appliedProjection_y0 = self.projectionSpaceBoundary_y0*self.scaler
                appliedProjection_y1 = self.projectionSpaceBoundary_y1*self.scaler
            else:
                appliedViewport_height = self.spe_viewport_full[3]
                appliedViewport_y = self.spe_viewport_full[1]
                if (self.projectionViewRange[2] == None):
                    appliedProjection_y0 = self.projectionSpaceBoundary_y0*self.scaler
                    appliedProjection_y1 = appliedProjection_y0 + appliedViewport_height
                else:
                    #If 'overBoundaryDelta' is positive, the previous view range exceeds the new projectionSpaceBoundary
                    overBoundaryDelta_bottom = self.projectionSpaceBoundary_y0*self.scaler        - self.projectionViewRange[2]
                    overBoundaryDelta_top    = self.projectionViewRange[2]+appliedViewport_height - self.projectionSpaceBoundary_y1*self.scaler
                    if (0 < overBoundaryDelta_bottom):
                        appliedProjection_y0 = self.projectionSpaceBoundary_y0*self.scaler
                        appliedProjection_y1 = appliedProjection_y0+appliedViewport_height
                    elif (0 < overBoundaryDelta_top):
                        appliedProjection_y1 = self.projectionSpaceBoundary_y1*self.scaler
                        appliedProjection_y0 = appliedProjection_y1-appliedViewport_height
                    else:
                        appliedProjection_y0 = self.projectionViewRange[2]
                        appliedProjection_y1 = self.projectionViewRange[2]+appliedViewport_height

            self.projectionViewRange = [appliedProjection_x0, appliedProjection_x1, appliedProjection_y0, appliedProjection_y1]
            self.layeredCamGroup.updateViewport(viewport_x = appliedViewport_x, viewport_y = appliedViewport_y, viewport_width = appliedViewport_width, viewport_height = appliedViewport_height)
            self.layeredCamGroup.updateProjection(projection_x0 = round(appliedProjection_x0), projection_x1 = round(appliedProjection_x1), projection_y0 = round(appliedProjection_y0), projection_y1 = round(appliedProjection_y1))

            #Update ScrollBars
            if (self.projectionScrollBar_H != None): self.projectionScrollBar_H.editViewRange(((self.projectionViewRange[0]-self.projectionSpaceBoundary_x0*self.scaler)/(projectionBoundaryWidth_onViewportSpace)*100,  (self.projectionViewRange[1]-self.projectionSpaceBoundary_x0*self.scaler)/(projectionBoundaryWidth_onViewportSpace) *100))
            if (self.projectionScrollBar_V != None): self.projectionScrollBar_V.editViewRange(((self.projectionViewRange[2]-self.projectionSpaceBoundary_y0*self.scaler)/(projectionBoundaryHeight_onViewportSpace)*100, (self.projectionViewRange[3]-self.projectionSpaceBoundary_y0*self.scaler)/(projectionBoundaryHeight_onViewportSpace)*100))

        elif (updateType == 1):
            psb_viewRange = self.projectionScrollBar_H.getViewRange()
            projectionBoundaryWidth_onViewportSpace = (self.projectionSpaceBoundary_x1-self.projectionSpaceBoundary_x0)*self.scaler
            newProjectionViewRange_x0 = psb_viewRange[0]/100*projectionBoundaryWidth_onViewportSpace+self.projectionSpaceBoundary_x0*self.scaler
            newProjectionViewRange_x1 = psb_viewRange[1]/100*projectionBoundaryWidth_onViewportSpace+self.projectionSpaceBoundary_x0*self.scaler
            self.projectionViewRange[0] = newProjectionViewRange_x0
            self.projectionViewRange[1] = newProjectionViewRange_x1
            self.layeredCamGroup.updateProjection(projection_x0 = round(self.projectionViewRange[0]), projection_x1 = round(self.projectionViewRange[1]))

        elif (updateType == 2): 
            psb_viewRange = self.projectionScrollBar_V.getViewRange()
            projectionBoundaryHeight_onViewportSpace = (self.projectionSpaceBoundary_y1-self.projectionSpaceBoundary_y0)*self.scaler
            newProjectionViewRange_y0 = psb_viewRange[0]/100*projectionBoundaryHeight_onViewportSpace+self.projectionSpaceBoundary_y0*self.scaler
            newProjectionViewRange_y1 = psb_viewRange[1]/100*projectionBoundaryHeight_onViewportSpace+self.projectionSpaceBoundary_y0*self.scaler
            self.projectionViewRange[2] = newProjectionViewRange_y0
            self.projectionViewRange[3] = newProjectionViewRange_y1
            self.layeredCamGroup.updateProjection(projection_y0 = round(self.projectionViewRange[2]), projection_y1 = round(self.projectionViewRange[3]))

        elif (updateType == 3):
            if ((self.projectionViewRange[0] != None) and (self.projectionViewRange[1] != None)):
                projectionDelta = self.projectionScroll_dx*self.projectionScroll_accelerationFactor
                newProjectionViewRange_x0 = self.projectionViewRange[0] + projectionDelta
                newProjectionViewRange_x1 = self.projectionViewRange[1] + projectionDelta
                #Positive
                if (0 < self.projectionScroll_dx):         
                    projectionBoundary_x1_scaled = self.projectionSpaceBoundary_x1*self.scaler
                    overBoundaryDelta = newProjectionViewRange_x1 - projectionBoundary_x1_scaled
                    if (0 < overBoundaryDelta):
                        newProjectionViewRange_x0 -= overBoundaryDelta
                        newProjectionViewRange_x1 -= overBoundaryDelta
                #Negative
                elif (self.projectionScroll_dx < 0):
                    projectionBoundary_x0_scaled = self.projectionSpaceBoundary_x0*self.scaler
                    overBoundaryDelta = projectionBoundary_x0_scaled - newProjectionViewRange_x0
                    if (0 < overBoundaryDelta):
                        newProjectionViewRange_x0 += overBoundaryDelta
                        newProjectionViewRange_x1 += overBoundaryDelta

                self.projectionViewRange[0] = newProjectionViewRange_x0
                self.projectionViewRange[1] = newProjectionViewRange_x1
                self.layeredCamGroup.updateProjection(projection_x0 = round(self.projectionViewRange[0]), projection_x1 = round(self.projectionViewRange[1]))
                if (self.projectionScrollBar_H != None):
                    self.projectionScrollBar_H.editViewRange(((self.projectionViewRange[0]-self.projectionSpaceBoundary_x0*self.scaler)/((self.projectionSpaceBoundary_x1-self.projectionSpaceBoundary_x0)*self.scaler)*100, 
                                                              (self.projectionViewRange[1]-self.projectionSpaceBoundary_x0*self.scaler)/((self.projectionSpaceBoundary_x1-self.projectionSpaceBoundary_x0)*self.scaler)*100))
            self.projectionScroll_dx = 0 

        elif (updateType == 4):
            if ((self.projectionViewRange[2] != None) and (self.projectionViewRange[3] != None)):
                projectionDelta = self.projectionScroll_dy*self.projectionScroll_accelerationFactor
                newProjectionViewRange_y0 = self.projectionViewRange[2] + projectionDelta
                newProjectionViewRange_y1 = self.projectionViewRange[3] + projectionDelta
                #Positive
                if (0 < self.projectionScroll_dy):         
                    projectionBoundary_y1_scaled = self.projectionSpaceBoundary_y1*self.scaler
                    overBoundaryDelta = newProjectionViewRange_y1 - projectionBoundary_y1_scaled
                    if (0 < overBoundaryDelta):
                        newProjectionViewRange_y0 -= overBoundaryDelta
                        newProjectionViewRange_y1 -= overBoundaryDelta
                #Negative
                elif (self.projectionScroll_dy < 0):
                    projectionBoundary_y0_scaled = self.projectionSpaceBoundary_y0*self.scaler
                    overBoundaryDelta = projectionBoundary_y0_scaled - newProjectionViewRange_y0
                    if (0 < overBoundaryDelta):
                        newProjectionViewRange_y0 += overBoundaryDelta
                        newProjectionViewRange_y1 += overBoundaryDelta

                self.projectionViewRange[2] = newProjectionViewRange_y0
                self.projectionViewRange[3] = newProjectionViewRange_y1
                self.layeredCamGroup.updateProjection(projection_y0 = round(self.projectionViewRange[2]), projection_y1 = round(self.projectionViewRange[3]))
                if (self.projectionScrollBar_V != None):
                    self.projectionScrollBar_V.editViewRange(((self.projectionViewRange[2]-self.projectionSpaceBoundary_y0*self.scaler)/((self.projectionSpaceBoundary_y1-self.projectionSpaceBoundary_y0)*self.scaler)*100, 
                                                              (self.projectionViewRange[3]-self.projectionSpaceBoundary_y0*self.scaler)/((self.projectionSpaceBoundary_y1-self.projectionSpaceBoundary_y0)*self.scaler)*100))
            self.projectionScroll_dy = 0

    def show(self):
        if (self.style != None): self.frameSprite.visible = True
        self.layeredCamGroup.show()
        if (self.projectionScrollBar_H != None): self.projectionScrollBar_H.show()
        if (self.projectionScrollBar_V != None): self.projectionScrollBar_V.show()
        for guioName in self.GUIOs: 
            if (self.GUIOs_displayStatus[guioName] == True): self.GUIOs[guioName].show()
        self.hidden = False

    def hide(self):
        if (self.style != None): self.frameSprite.visible = False
        self.layeredCamGroup.hide()
        if (self.projectionScrollBar_H != None): self.projectionScrollBar_H.hide()
        if (self.projectionScrollBar_V != None): self.projectionScrollBar_V.hide()
        for guioInstance in self.GUIOs.values(): guioInstance.hide()
        self.hidden = True

    def moveTo(self, x, y):
        self.xPos = x; self.yPos = y
        if (self.style == None):
            if (self.projectionScrollBar_H != None):
                #Use H & V
                if (self.projectionScrollBar_V != None):
                    scrollBar_H_x = self.xPos
                    scrollBar_H_y = self.yPos
                    scrollBar_V_x = self.xPos+self.width-self.scrollBarHeight
                    scrollBar_V_y = self.yPos+self.scrollBarHeight+self.gOffset
                    spe_viewport_x = (self.xPos)*self.scaler
                    spe_viewport_y = (self.yPos+self.scrollBarHeight+self.gOffset)*self.scaler
                #Use H Only
                else:
                    scrollBar_H_x = self.xPos
                    scrollBar_H_y = self.yPos
                    spe_viewport_x = (self.xPos)*self.scaler
                    spe_viewport_y = (self.yPos+self.scrollBarHeight+self.gOffset)*self.scaler
            else:
                #Use V Only
                if (self.projectionScrollBar_V != None):
                    scrollBar_V_x = self.xPos+self.width-self.scrollBarHeight
                    scrollBar_V_y = self.yPos
                    spe_viewport_x = (self.xPos)*self.scaler
                    spe_viewport_y = (self.yPos)*self.scaler
                #No ScrollBar
                else:
                    spe_viewport_x = (self.xPos)*self.scaler
                    spe_viewport_y = (self.yPos)*self.scaler
        else:
            if (self.projectionScrollBar_H != None):
                #Use H & V
                if (self.projectionScrollBar_V != None):
                    scrollBar_H_x = self.xPos+self.gOffset
                    scrollBar_H_y = self.yPos+self.gOffset
                    scrollBar_V_x = self.xPos+self.width-self.gOffset-self.scrollBarHeight
                    scrollBar_V_y = self.yPos+self.gOffset*2+self.scrollBarHeight
                    spe_viewport_x = (self.xPos+self.gOffset)*self.scaler
                    spe_viewport_y = (self.yPos+self.gOffset*2+self.scrollBarHeight)*self.scaler
                #Use H Only
                else:
                    scrollBar_H_x = self.xPos+self.gOffset
                    scrollBar_H_y = self.yPos+self.gOffset
                    spe_viewport_x = (self.xPos+self.gOffset)*self.scaler
                    spe_viewport_y = (self.yPos+self.gOffset*2+self.scrollBarHeight)*self.scaler
            else:
                #Use V Only
                if (self.projectionScrollBar_V != None):
                    scrollBar_V_x = self.xPos+self.width-self.gOffset-self.scrollBarHeight
                    scrollBar_V_y = self.yPos+self.gOffset
                    spe_viewport_x = (self.xPos+self.gOffset)*self.scaler
                    spe_viewport_y = (self.yPos+self.gOffset)*self.scaler
                #No ScrollBar
                else:
                    spe_viewport_x = (self.xPos+self.gOffset)*self.scaler
                    spe_viewport_y = (self.yPos+self.gOffset)*self.scaler
        self.spe_viewport_full = (spe_viewport_x, spe_viewport_y, self.spe_viewport_full[2], self.spe_viewport_full[3])

        self.frameSprite.position = (self.xPos*self.scaler, self.yPos*self.scaler, self.frameSprite.z)
        if (self.projectionScrollBar_H != None): self.projectionScrollBar_H.moveTo(scrollBar_H_x, scrollBar_H_y)
        if (self.projectionScrollBar_V != None): self.projectionScrollBar_V.moveTo(scrollBar_V_x, scrollBar_V_y)
        self.hitBox.reposition(xPos = self.xPos, yPos = self.yPos)
        if (0 < len(self.GUIOs)): self.__updateProjection(0)

    def resize(self, width, height):
        self.width = width; self.height = height
        if (self.style == None):
            if (self.projectionScrollBar_H != None):
                #Use H & V
                if (self.projectionScrollBar_V != None):
                    scrollBar_H_width  = self.width-self.scrollBarHeight-self.gOffset
                    scrollBar_V_x      = self.xPos+self.width-self.scrollBarHeight
                    scrollBar_V_width  = self.height-self.scrollBarHeight-self.gOffset
                    spe_viewport_width  = (self.width-self.scrollBarHeight-self.gOffset)*self.scaler
                    spe_viewport_height = (self.height-self.scrollBarHeight-self.gOffset)*self.scaler
                #Use H Only
                else:
                    scrollBar_H_width  = self.width
                    spe_viewport_width  = (self.width)*self.scaler
                    spe_viewport_height = (self.height-self.scrollBarHeight-self.gOffset)*self.scaler
            else:
                #Use V Only
                if (self.projectionScrollBar_V != None):
                    scrollBar_V_x      = self.xPos+self.width-self.scrollBarHeight
                    scrollBar_V_width  = self.height
                    spe_viewport_width  = (self.width-self.scrollBarHeight-self.gOffset)*self.scaler
                    spe_viewport_height = (self.height)*self.scaler
                #No ScrollBar
                else:
                    spe_viewport_width  = (self.width)*self.scaler
                    spe_viewport_height = (self.height)*self.scaler
        else:
            if (self.projectionScrollBar_H != None):
                #Use H & V
                if (self.projectionScrollBar_V != None):
                    scrollBar_H_width  = self.width-self.gOffset*3-self.scrollBarHeight
                    scrollBar_V_x      = self.xPos+self.width-self.gOffset-self.scrollBarHeight
                    scrollBar_V_width  = self.height-self.gOffset*3-self.scrollBarHeight
                    spe_viewport_width  = (self.width -self.gOffset*3-self.scrollBarHeight)*self.scaler
                    spe_viewport_height = (self.height-self.gOffset*3-self.scrollBarHeight)*self.scaler
                #Use H Only
                else:
                    scrollBar_H_width  = self.width-self.gOffset*2
                    spe_viewport_width  = (self.width -self.gOffset*2)*self.scaler
                    spe_viewport_height = (self.height-self.gOffset*3-self.scrollBarHeight)*self.scaler
            else:
                #Use V Only
                if (self.projectionScrollBar_V != None):
                    scrollBar_V_x      = self.xPos+self.width-self.gOffset-self.scrollBarHeight
                    scrollBar_V_width  = self.height-self.gOffset*2
                    spe_viewport_width  = (self.width -self.gOffset*3-self.scrollBarHeight)*self.scaler
                    spe_viewport_height = (self.height-self.gOffset*2)*self.scaler
                #No ScrollBar
                else:
                    spe_viewport_width  = (self.width-self.gOffset*2)*self.scaler
                    spe_viewport_height = (self.height-self.gOffset*2)*self.scaler
            self.images['FRAME'] = self.imageManager.getImageByCode("subPageBox_typeA_"+self.style, self.width*self.scaler, self.height*self.scaler, objectSpecificCode = "{:d}".format(int(self.frameRadius*self.scaler)))
            self.frameSprite.image = self.images['FRAME'][0]
        self.spe_viewport_full = (self.spe_viewport_full[0], self.spe_viewport_full[1], spe_viewport_width, spe_viewport_height)

        
        if (self.projectionScrollBar_H != None): self.projectionScrollBar_H.resize(scrollBar_H_width, self.projectionScrollBar_H.height)
        if (self.projectionScrollBar_V != None):
            self.projectionScrollBar_V.moveTo(scrollBar_V_x, self.projectionScrollBar_V.yPos)
            self.projectionScrollBar_V.resize(scrollBar_V_width, self.projectionScrollBar_V.height)

        
        self.hitBox.resize(width = self.width, height = self.height)
        if (0 < len(self.GUIOs)): self.__updateProjection(0)

    def setName(self, name): self.name = name

    def getName(self): return self.name

    def isTouched(self, mouseX, mouseY): 
        if (self.hidden == True): return False
        return self.hitBox.isTouched(mouseX, mouseY)

    def isHidden(self): return self.hidden

    def on_GUIThemeUpdate(self, **kwargs):
        if (self.style != None):
            self.images['FRAME'] = self.imageManager.getImageByLoadIndex(self.images['FRAME'][1])
            self.frameSprite.image = self.images['FRAME'][0]
        if (self.projectionScrollBar_H != None): self.projectionScrollBar_H.on_GUIThemeUpdate(**kwargs)
        if (self.projectionScrollBar_V != None): self.projectionScrollBar_V.on_GUIThemeUpdate(**kwargs)
        for guioInstance in self.GUIOs.values(): guioInstance.on_GUIThemeUpdate(**kwargs)

    def on_LanguageUpdate(self, **kwargs):
        for guioInstance in self.GUIOs.values(): guioInstance.on_LanguageUpdate(**kwargs)
    
    def addGUIO(self, name, guioType, guioInitParams):
        groupInstances = self.layeredCamGroup.getGroups(guioInitParams['groupOrder'], guioInitParams['groupOrder']+guioType.getGroupRequirement()); del guioInitParams['groupOrder']
        self.GUIOs[name] = guioType(**self.baseInitParams, **guioInitParams, **groupInstances)
        if (self.hidden == True): self.GUIOs[name].hide()
        else:                     self.GUIOs[name].show()
        self.GUIOs_displayStatus[name] = True

        projectionBoundaryUpdated = False
        if ((self.projectionSpaceBoundary_x0 == None) or (guioInitParams['xPos']          < self.projectionSpaceBoundary_x0)):                 self.projectionSpaceBoundary_x0 = guioInitParams['xPos'];                          projectionBoundaryUpdated = True
        if ((self.projectionSpaceBoundary_x1 == None) or (self.projectionSpaceBoundary_x1 < guioInitParams['xPos']+guioInitParams['width'])):  self.projectionSpaceBoundary_x1 = guioInitParams['xPos']+guioInitParams['width'];  projectionBoundaryUpdated = True
        if ((self.projectionSpaceBoundary_y0 == None) or (guioInitParams['yPos']          < self.projectionSpaceBoundary_y0)):                 self.projectionSpaceBoundary_y0 = guioInitParams['yPos'];                          projectionBoundaryUpdated = True
        if ((self.projectionSpaceBoundary_y1 == None) or (self.projectionSpaceBoundary_y1 < guioInitParams['yPos']+guioInitParams['height'])): self.projectionSpaceBoundary_y1 = guioInitParams['yPos']+guioInitParams['height']; projectionBoundaryUpdated = True
        if (projectionBoundaryUpdated == True): self.__updateProjection(updateType = 0)

    def hideGUIO(self, guioName):
        self.GUIOs_displayStatus[guioName] = False
        if (self.GUIOs[guioName].isHidden() == False): self.GUIOs[guioName].hide()

    def showGUIO(self, guioName):
        self.GUIOs_displayStatus[guioName] = True
        if ((self.GUIOs[guioName].isHidden() == True) and (self.hidden == False)): self.GUIOs[guioName].show()

    def moveGUIO(self, guioName, x, y):
        if (guioName in self.GUIOs):
            self.GUIOs[guioName].moveTo(x, y)
            if (self.__updateProjectionSpaceBoundary() == True): self.__updateProjection(updateType = 0)

    def resizeGUIO(self, guioName, width, height):
        if (guioName in self.GUIOs):
            self.GUIOs[guioName].resize(width, height)
            if (self.__updateProjectionSpaceBoundary() == True): self.__updateProjection(updateType = 0)

    def moveProjectionView(self, newProjection_x0 = None, newProjection_y0 = None):
        if (newProjection_x0 != None):
            newProjectionViewRange_x0 = newProjection_x0*self.scaler
            newProjectionViewRange_x1 = newProjection_x0*self.scaler + (self.projectionViewRange[1]-self.projectionViewRange[0])
            #Positive
            if (0 < self.projectionScroll_dx):         
                projectionBoundary_x1_scaled = self.projectionSpaceBoundary_x1*self.scaler
                overBoundaryDelta = newProjectionViewRange_x1 - projectionBoundary_x1_scaled
                if (0 < overBoundaryDelta):
                    newProjectionViewRange_x0 -= overBoundaryDelta
                    newProjectionViewRange_x1 -= overBoundaryDelta
            #Negative
            elif (self.projectionScroll_dx < 0):
                projectionBoundary_x0_scaled = self.projectionSpaceBoundary_x0*self.scaler
                overBoundaryDelta = projectionBoundary_x0_scaled - newProjectionViewRange_x0
                if (0 < overBoundaryDelta):
                    newProjectionViewRange_x0 += overBoundaryDelta
                    newProjectionViewRange_x1 += overBoundaryDelta

            self.projectionViewRange[0] = newProjectionViewRange_x0
            self.projectionViewRange[1] = newProjectionViewRange_x1
            self.layeredCamGroup.updateProjection(projection_x0 = self.projectionViewRange[0], projection_x1 = self.projectionViewRange[1])
            if (self.projectionScrollBar_H != None):
                self.projectionScrollBar_H.editViewRange(((self.projectionViewRange[0]-self.projectionSpaceBoundary_x0*self.scaler)/((self.projectionSpaceBoundary_x1-self.projectionSpaceBoundary_x0)*self.scaler)*100, 
                                                            (self.projectionViewRange[1]-self.projectionSpaceBoundary_x0*self.scaler)/((self.projectionSpaceBoundary_x1-self.projectionSpaceBoundary_x0)*self.scaler)*100))

        if (newProjection_y0 != None):
            newProjectionViewRange_y0 = newProjection_y0*self.scaler
            newProjectionViewRange_y1 = newProjection_y0*self.scaler + (self.projectionViewRange[3]-self.projectionViewRange[2])
            #Positive
            if (0 < self.projectionScroll_dy):
                projectionBoundary_y1_scaled = self.projectionSpaceBoundary_y1*self.scaler
                overBoundaryDelta = newProjectionViewRange_y1 - projectionBoundary_y1_scaled
                if (0 < overBoundaryDelta):
                    newProjectionViewRange_y0 -= overBoundaryDelta
                    newProjectionViewRange_y1 -= overBoundaryDelta
            #Negative
            elif (self.projectionScroll_dy < 0):
                projectionBoundary_y0_scaled = self.projectionSpaceBoundary_y0*self.scaler
                overBoundaryDelta = projectionBoundary_y0_scaled - newProjectionViewRange_y0
                if (0 < overBoundaryDelta):
                    newProjectionViewRange_y0 += overBoundaryDelta
                    newProjectionViewRange_y1 += overBoundaryDelta

            self.projectionViewRange[2] = newProjectionViewRange_y0
            self.projectionViewRange[3] = newProjectionViewRange_y1
            self.layeredCamGroup.updateProjection(projection_y0 = self.projectionViewRange[2], projection_y1 = self.projectionViewRange[3])
            if (self.projectionScrollBar_V != None):
                self.projectionScrollBar_V.editViewRange(((self.projectionViewRange[2]-self.projectionSpaceBoundary_y0*self.scaler)/((self.projectionSpaceBoundary_y1-self.projectionSpaceBoundary_y0)*self.scaler)*100, 
                                                          (self.projectionViewRange[3]-self.projectionSpaceBoundary_y0*self.scaler)/((self.projectionSpaceBoundary_y1-self.projectionSpaceBoundary_y0)*self.scaler)*100))

    def __updateProjectionSpaceBoundary(self):
        projectionSpaceBoundary_x0 = None; projectionSpaceBoundary_x1 = None
        projectionSpaceBoundary_y0 = None; projectionSpaceBoundary_y1 = None
        for guioInstance in self.GUIOs.values():
            if ((projectionSpaceBoundary_x0 == None) or (guioInstance.xPos          < projectionSpaceBoundary_x0)):            projectionSpaceBoundary_x0 = guioInstance.xPos
            if ((projectionSpaceBoundary_x1 == None) or (projectionSpaceBoundary_x1 < guioInstance.xPos+guioInstance.width)):  projectionSpaceBoundary_x1 = guioInstance.xPos+guioInstance.width
            if ((projectionSpaceBoundary_y0 == None) or (guioInstance.yPos          < projectionSpaceBoundary_y0)):            projectionSpaceBoundary_y0 = guioInstance.yPos
            if ((projectionSpaceBoundary_y1 == None) or (projectionSpaceBoundary_y1 < guioInstance.yPos+guioInstance.height)): projectionSpaceBoundary_y1 = guioInstance.yPos+guioInstance.height
        if ((projectionSpaceBoundary_x0 != self.projectionSpaceBoundary_x0) or (projectionSpaceBoundary_x1 != self.projectionSpaceBoundary_x1) or (projectionSpaceBoundary_y0 != self.projectionSpaceBoundary_y0) or (projectionSpaceBoundary_y1 != self.projectionSpaceBoundary_y1)):
            self.projectionSpaceBoundary_x0 = projectionSpaceBoundary_x0
            self.projectionSpaceBoundary_x1 = projectionSpaceBoundary_x1
            self.projectionSpaceBoundary_y0 = projectionSpaceBoundary_y0
            self.projectionSpaceBoundary_y1 = projectionSpaceBoundary_y1
            return True
        else: return False

    def getGUIOInstance(self, name):
        if (name in self.GUIOs): return self.GUIOs[name]
        else:                    return None

    def getGroupRequirement():
        return 3
#GUIO - 'subPageBox_typeA' END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------