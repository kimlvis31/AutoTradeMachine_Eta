from GUI import atmEta_gui_HitBoxes

import pyglet
#import win32clipboard #DEPRECATED
import pyperclip

CHARTABLE_LOWER = {48: '0', 49: '1', 50: '2', 51: '3', 52: '4', 53: '5', 54: '6', 55: '7', 56: '8', 57: '9',
                   97: 'a', 98: 'b', 99: 'c', 100: 'd', 101: 'e', 102: 'f', 103: 'g', 104: 'h', 105: 'i', 106: 'j', 107: 'k', 108: 'l', 109: 'm', 110: 'n', 111: 'o', 112: 'p', 113: 'q', 114: 'r', 115: 's', 116: 't', 117: 'u', 118: 'v', 119: 'w', 120: 'x', 121: 'y', 122: 'z',
                   96: '`', 45: '-', 61: '=', 91: '[', 93: ']', 92: '\\', 59: ';', 39: '\'', 44: ',', 46: '.', 47: '/',
                   32: ' ', 65289: '   '}

CHARTABLE_UPPER = {48: ')', 49: '!', 50: '@', 51: '#', 52: '$', 53: '%', 54: '^', 55: '&', 56: '*', 57: '(',
                   97: 'A', 98: 'B', 99: 'C', 100: 'D', 101: 'E', 102: 'F', 103: 'G', 104: 'H', 105: 'I', 106: 'J', 107: 'K', 108: 'L', 109: 'M', 110: 'N', 111: 'O', 112: 'P', 113: 'Q', 114: 'R', 115: 'S', 116: 'T', 117: 'U', 118: 'V', 119: 'W', 120: 'X', 121: 'Y', 122: 'Z',
                   96: '~', 45: '_', 61: '+', 91: '{', 93: '}', 92: '|', 59: ':', 39: '"', 44: '<', 46: '>', 47: '?',
                   32: ' ', 65289: '   '}

MODIFIER_SHIFT    = 0b00001
MODIFIER_CTRL     = 0b00010
MODIFIER_ALT      = 0b00100
MODIFIER_CAPSLOCK = 0b01000
MODIFIER_NUMLOCK  = 0b10000

#Text Object - Singular Line ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class textObject_SL:
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        self.group = kwargs['group']
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.text = kwargs.get('text', None)

        self.textStyles = dict()
        self.textStyles['DEFAULT'] = kwargs['defaultTextStyle']
        if ('auxillaryTextStyles' in kwargs.keys()): self.textStyles.update(kwargs['auxillaryTextStyles'])
        self.activeTextStyle = 'DEFAULT'
        
        #Element Box - Activated for reference
        self.showElementBox = kwargs.get('showElementBox', False)
        self.elementBox = pyglet.shapes.Rectangle(self.xPos*self.scaler, self.yPos*self.scaler, self.width*self.scaler, self.height*self.scaler, batch = self.batch, group = self.group, color = (255, 0, 0, 50))
        self.elementBox.visible = self.showElementBox

        #Text Control
        #---Document Initialization
        self.document       = pyglet.text.document.FormattedDocument()
        self.document_empty = pyglet.text.document.UnformattedDocument()
        self.document.insert_text(0, '#', attributes = self.textStyles[self.activeTextStyle]); self.document.delete_text(0, len(self.document.text))
        self.document.insert_text(0, self.text, attributes = self.textStyles[self.activeTextStyle])
        self.textStyleAtIndex = list()
        for i in range (len(self.text)): self.textStyleAtIndex.append(self.activeTextStyle)

        #---Layout Initialization
        self.layout = pyglet.text.layout.IncrementalTextLayout(self.document, 0, 0, batch = self.batch, group = self.group, multiline = False)
        self.textAnchor = None; self.textAnchor_x = None; self.textAnchor_y = None; 
        self.xOverSizeDelta = None; self.yOverSizeDelta = None

        #Object Control
        self.hidden = False

        #Post Initialization
        self.setAnchor(kwargs.get('anchor', 'CENTER'))
        self.locateLayout()

    def process(self, t_elapsed_ns): pass
    def handleMouseEvent(self, event): pass
    def handleKeyEvent(self, event): pass

    def show(self):
        self.hidden = False
        self.layout.document = self.document
        self.elementBox.visible = self.showElementBox
        self.locateLayout()

    def hide(self):
        self.hidden = True
        self.layout.document = self.document_empty
        self.elementBox.visible = False

    def isHidden(self): return self.hidden

    def moveTo(self, x = None, y = None):
        if (x != None):
            self.xPos = x
            if (self.showElementBox == True): self.elementBox.x = self.xPos*self.scaler
        if (y != None):
            self.yPos = y
            if (self.showElementBox == True): self.elementBox.y = self.yPos*self.scaler
        if (self.hidden == False): self.locateLayout()

    def changeSize(self, width = None, height = None):
        if (width != None):
            self.width = width
            if (self.showElementBox == True): self.elementBox.width = self.width*self.scaler
            self.layout.width = self.width*self.scaler
        if (height != None):
            self.height = height
            if (self.showElementBox == True): self.elementBox.height = self.height*self.scaler
            self.layout.height = self.height*self.scaler
        if (self.hidden == False): self.locateLayout()

    def setAnchor(self, newAnchor):
        if   (newAnchor == 'CENTER'): self.textAnchor_x = 'center'; self.textAnchor_y = 'center'
        elif (newAnchor == 'W'):      self.textAnchor_x = 'left';   self.textAnchor_y = 'center'
        elif (newAnchor == 'NW'):     self.textAnchor_x = 'left';   self.textAnchor_y = 'top'
        elif (newAnchor == 'N'):      self.textAnchor_x = 'center'; self.textAnchor_y = 'top'
        elif (newAnchor == 'NE'):     self.textAnchor_x = 'right';  self.textAnchor_y = 'top'
        elif (newAnchor == 'E'):      self.textAnchor_x = 'right';  self.textAnchor_y = 'center'
        elif (newAnchor == 'SE'):     self.textAnchor_x = 'right';  self.textAnchor_y = 'bottom'
        elif (newAnchor == 'S'):      self.textAnchor_x = 'center'; self.textAnchor_y = 'bottom'
        elif (newAnchor == 'SW'):     self.textAnchor_x = 'left';   self.textAnchor_y = 'bottom'
        else: return False
        self.textAnchor = newAnchor
        self.document.set_paragraph_style(0, len(self.text), {'align': self.textAnchor_x})
        if (self.hidden == False): self.locateLayout()

    def changePosSizeAnchor(self, x = None, y = None, width = None, height = None, anchor = None):
        if (x != None):
            self.xPos = x
            if (self.showElementBox == True): self.elementBox.x = self.xPos*self.scaler
        if (y != None):
            self.yPos = y
            if (self.showElementBox == True): self.elementBox.y = self.yPos*self.scaler
        if (width != None):
            self.width = width
            if (self.showElementBox == True): self.elementBox.width = self.width*self.scaler
        if (height != None):
            self.height = height
            if (self.showElementBox == True): self.elementBox.height = self.height*self.scaler
        if (anchor != None):
            acceptableAnchor = True
            if   (anchor == 'CENTER'): self.textAnchor_x = 'center'; self.textAnchor_y = 'center'
            elif (anchor == 'W'):      self.textAnchor_x = 'left';   self.textAnchor_y = 'center'
            elif (anchor == 'NW'):     self.textAnchor_x = 'left';   self.textAnchor_y = 'top'
            elif (anchor == 'N'):      self.textAnchor_x = 'center'; self.textAnchor_y = 'top'
            elif (anchor == 'NE'):     self.textAnchor_x = 'right';  self.textAnchor_y = 'top'
            elif (anchor == 'E'):      self.textAnchor_x = 'right';  self.textAnchor_y = 'center'
            elif (anchor == 'SE'):     self.textAnchor_x = 'right';  self.textAnchor_y = 'bottom'
            elif (anchor == 'S'):      self.textAnchor_x = 'center'; self.textAnchor_y = 'bottom'
            elif (anchor == 'SW'):     self.textAnchor_x = 'left';   self.textAnchor_y = 'bottom'
            else: acceptableAnchor = False
            if (acceptableAnchor == True): self.textAnchor = anchor; self.document.set_paragraph_style(0, len(self.text), {'align': self.textAnchor_x})
        if (self.hidden == False): self.locateLayout()

    def setText(self, text, textStyle = None):
        self.document.delete_text(0, len(self.document.text))
        self.text = text
        nText = len(self.text)
        if (0 < nText):
            if (type(textStyle) == list):
                #Edit TextStylesAtIndex
                self.textStyleAtIndex = [self.activeTextStyle] * nText
                for textStyleBlock in textStyle:
                    styleRange = self.__reformIndexRange(textStyleBlock[0], nText)
                    for textIndex in range (styleRange[0], styleRange[1]+1): self.textStyleAtIndex[textIndex] = textStyleBlock[1]
                #Construct UpdateBlocks
                updateBlocks = list()
                _updateBlock = None
                for index in range (0, nText):
                    if (_updateBlock == None): _updateBlock = [index, index, self.textStyleAtIndex[index]]
                    else:
                        if (_updateBlock[2] == self.textStyleAtIndex[index]): _updateBlock[1] = index
                        else:
                            updateBlocks.append(((_updateBlock[0], _updateBlock[1]), _updateBlock[2]))
                            _updateBlock = [index, index, self.textStyleAtIndex[index]]
                if (_updateBlock != None): updateBlocks.append(((_updateBlock[0], _updateBlock[1]), _updateBlock[2]))
                #Update the document using the constructed UpdateBlocks
                for updateBlock in updateBlocks: 
                    blockTextStyle = updateBlock[1]
                    if (blockTextStyle in self.textStyles): blockTextStyle_effective = blockTextStyle
                    else:                                   blockTextStyle_effective = self.activeTextStyle; print("{:s} not found".format(str(blockTextStyle)))
                    self.document.insert_text(start = len(self.document.text), text = self.text[updateBlock[0][0]:updateBlock[0][1]+1], attributes = self.textStyles[blockTextStyle_effective])
            else:
                if (textStyle == None): self.textStyleAtIndex = [self.activeTextStyle] * nText
                else:                   self.textStyleAtIndex = [textStyle] * nText
                self.document.insert_text(start = 0, text = self.text, attributes = self.textStyles[self.textStyleAtIndex[0]])
            self.document.set_paragraph_style(0, nText, {'align': self.textAnchor_x})
        if (self.hidden == False): self.locateLayout()

    def insertText(self, text, position = None, textStyle = None):
        #Positional Text and TextStyle Computation
        if (textStyle == None): textStyleToUse = self.activeTextStyle
        else:                   textStyleToUse = textStyle
        if (position == None):
            initialPosition = len(self.text)
            self.text += text
            self.textStyleAtIndex += [textStyleToUse] * len(text)
        else:
            if (position < 0):
                if (position < -len(self.text)): position = 0
                else:                            position = len(self.text) + position + 1
            elif (len(self.text) < position):    position = len(self.text)
            initialPosition = position
            self.text             = self.text[:position]             + text                       + self.text[position:]
            self.textStyleAtIndex = self.textStyleAtIndex[:position] + [textStyleToUse]*len(text) + self.textStyleAtIndex[position:]
            
        #Document Edit
        self.document.text = self.text
        for i in range (len(self.text)): self.document.set_style(i, i+1, self.textStyles[self.textStyleAtIndex[i]])
        self.document.set_paragraph_style(initialPosition, len(self.text), {'align': self.textAnchor_x})

        #If not hidden, update the layout position
        if (self.hidden == False): self.locateLayout()

    def deleteText(self, indexRange):
        if (indexRange == 'all'):
            self.text = ""
            self.textStyleAtIndex.clear()
        else:
            charIndexRange = self.__reformIndexRange(indexRange, len(self.document.text))
            self.text             = self.text[:charIndexRange[0]]             + self.text[charIndexRange[1]+1:]
            self.textStyleAtIndex = self.textStyleAtIndex[:charIndexRange[0]] + self.textStyleAtIndex[charIndexRange[1]+1:]
            
        #Document Edit
        self.document.text = self.text
        for i in range (len(self.text)): self.document.set_style(i, i+1, self.textStyles[self.textStyleAtIndex[i]])

        #If not hidden, update the layout position
        if (self.hidden == False): self.locateLayout()

    def getText(self): return self.text

    def editTextStyle(self, indexRange, style):
        if (indexRange == 'all'):
            self.document.set_style(start = 0, end = len(self.document.text), attributes = self.textStyles[style])
            self.textStyleAtIndex = [style]*len(self.textStyleAtIndex)
        else:
            charIndexRange = self.__reformIndexRange(indexRange, len(self.document.text))
            textStylesToApply = [(self.textStyleAtIndex[i] != style) for i in range (charIndexRange[0], charIndexRange[1]+1)]
            updateBlocks = list()
            lastChecked = False
            anchorIndex = None
            nToApply = len(textStylesToApply)
            for relIndex in range (nToApply):
                if (lastChecked == False) and (textStylesToApply[relIndex] == True):
                    lastChecked = True
                    anchorIndex = relIndex
                elif (lastChecked == True):
                    if (textStylesToApply[relIndex] == False):
                        lastChecked = False
                        updateBlocks.append((anchorIndex+charIndexRange[0], relIndex-1+charIndexRange[0]))
                    elif (relIndex == nToApply-1):
                        updateBlocks.append((anchorIndex+charIndexRange[0], relIndex+charIndexRange[0]))
            if (0 < len(updateBlocks)):
                for updateBlock in updateBlocks: self.document.set_style(start = updateBlock[0], end = updateBlock[1]+1, attributes = self.textStyles[style])
                for i in range (charIndexRange[0], charIndexRange[1]+1): self.textStyleAtIndex[i] = style
            
        #If not hidden, update the layout position
        if (self.hidden == False): self.locateLayout()

    def addTextStyle(self, textStyleName, textStyle):
        self.textStyles[textStyleName] = textStyle

    def existsTextStyle(self, textStyleName):
        return (textStyleName in self.textStyles)

    def getTextStyle(self, textStyleName):
        return self.textStyles.get(textStyleName, None)

    def changeActiveTextStyle(self, textStyle):
        self.activeTextStyle = textStyle

    def on_GUIThemeUpdate(self, **kwargs):
        self.textStyles['DEFAULT'] = kwargs.get('newDefaultTextStyle')
        for textStyleName, textStyle in kwargs.get('auxillaryTextStyles', dict()).items(): self.textStyles[textStyleName] = textStyle
        for i in range (len(self.text)):
            textStyleNameAtPosition = self.textStyleAtIndex[i]
            if (textStyleNameAtPosition in self.textStyles): self.document.set_style(i, i+1, self.textStyles[textStyleNameAtPosition])
            else:                                            self.document.set_style(i, i+1, self.textStyles['DEFAULT'])

    def on_LanguageUpdate(self, **kwargs):
        #Update the language font
        for textStyleCode in self.textStyles.keys(): self.textStyles[textStyleCode]['font_name'] = kwargs['newLanguageFont']

        #If the text has been updated, set to the new text
        newLanguageText = kwargs.get('newLanguageText', None)
        if (newLanguageText != None) and (newLanguageText != self.text): self.setText(newLanguageText, textStyle = 'DEFAULT')
        else:
            for i in range (len(self.text)): self.document.set_style(start = i, end = i+1, attributes = self.textStyles[self.textStyleAtIndex[i]])

        #If not hidden, update the layout position
        if (self.hidden == False): self.locateLayout()

    def getWidth(self):         return self.width
    def getHeight(self):        return self.height
    def getTextLength(self):    return len(self.text)
    def getContentWidth(self):
        if (self.hidden == True):
            self.layout.document = self.document
            contentWidth = self.layout.content_width
            self.layout.document = self.document_empty
            return contentWidth
        else: return self.layout.content_width
    def getContentHeight(self):
        if (self.hidden == True):
            self.layout.document = self.document
            contentHeight = self.layout.content_height
            self.layout.document = self.document_empty
            return contentHeight
        else: return self.layout.content_height

    def getTextAnchor(self): return self.textAnchor

    def isTouched(self, mouseX, mouseY): return False

    def delete(self): self.layout.delete()

    #Locate Layout
    def locateLayout(self):
        self.xOverSizeDelta = round(self.layout.content_width - self.width*self.scaler, 1)
        newWidth      = round(self.width*self.scaler, 1)
        newLayoutXPos = round(self.xPos*self.scaler,  1)
        
        newLayoutYPos = None; newHeight = None
        self.yOverSizeDelta = round(self.layout.content_height - self.height*self.scaler, 1)
        if (0 < self.yOverSizeDelta): newHeight = round(self.height*self.scaler, 1)
        else:                         newHeight = self.layout.content_height
        if   (self.textAnchor_y == 'bottom'): newLayoutYPos = round(self.yPos*self.scaler,                                           1)
        elif (self.textAnchor_y == 'center'): newLayoutYPos = round(self.yPos*self.scaler + self.height*self.scaler/2 - newHeight/2, 1)
        elif (self.textAnchor_y == 'top'):    newLayoutYPos = round(self.yPos*self.scaler + self.height*self.scaler   - newHeight,   1)

        #Apply new positions
        if (newWidth  != self.layout.width):  self.layout.width  = newWidth; updateXPos = True
        if (newHeight != self.layout.height): self.layout.height = newHeight
        if ((newLayoutXPos != None) or (newLayoutXPos != self.layout.x)):  updateXPos = True
        else:                                                              updateXPos = False
        if ((newLayoutYPos != None) and (newLayoutYPos != self.layout.y)): updateYPos = True
        else:                                                              updateYPos = False
        if (updateXPos == True):
            if (updateYPos == True): self.layout.position = (newLayoutXPos, newLayoutYPos, 0)
            else:                    self.layout.x        = newLayoutXPos
        elif (updateYPos == True):   self.layout.y        = newLayoutYPos

        #Set Layout View
        self.setLayoutView()

    #Set Layout View
    def setLayoutView(self):
        if (0 < self.xOverSizeDelta):
            if   (self.textAnchor_x == 'left'):   newViewX = 0
            elif (self.textAnchor_x == 'center'): newViewX = round(self.xOverSizeDelta/2, 1)
            elif (self.textAnchor_x == 'right'):  newViewX = round(self.xOverSizeDelta,   1)
        else:                                     newViewX = 0
        
        if (0 < self.yOverSizeDelta):
            if   (self.textAnchor_y == 'bottom'): newViewY = 0
            elif (self.textAnchor_y == 'center'): newViewY = -round(self.yOverSizeDelta/2, 1)
            elif (self.textAnchor_y == 'top'):    newViewY = -round(self.yOverSizeDelta,   1)
        else:                                     newViewY = 0
        
        if (self.layout.view_x != newViewX): self.layout.view_x = newViewX
        if (self.layout.view_y != newViewY): self.layout.view_y = newViewY
    #Reform the passed index range
    def __reformIndexRange(self, indexRange, nElements):
        #Analysis Variables Initialization
        charIndexRange = [indexRange[0], indexRange[1]]
        #Non-specified Boundary Read
        if   (indexRange[0] == None): charIndexRange[0] = 0
        elif (indexRange[1] == None): charIndexRange[1] = nElements
        #Index Reverse Read
        if (charIndexRange[0] < 0):
            if (charIndexRange[0] < -nElements): charIndexRange[0] = 0
            else:                                charIndexRange[0] = nElements + charIndexRange[0]
        else: 
            if (nElements <= charIndexRange[0]): charIndexRange[0] = nElements - 1
        if (charIndexRange[1] < 0):
            if (charIndexRange[1] < -nElements): charIndexRange[1] = 0
            else:                                charIndexRange[1] = nElements + charIndexRange[1]
        else: 
            if (nElements <= charIndexRange[1]): charIndexRange[1] = nElements - 1
        #Index Flip Read
        if (charIndexRange[1] < charIndexRange[0]): charIndexRange = [charIndexRange[1], charIndexRange[0]]
        return charIndexRange
#Text Object - Singular Line END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Text Object - Singular Line, Interactable --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class textObject_SL_I:
    def __init__(self, **kwargs):
        self.textElement_SL = textObject_SL(scaler = kwargs['scaler'], batch = kwargs['batch'], group = kwargs['group'], 
                                            text = kwargs.get('text', ""), defaultTextStyle = kwargs['defaultTextStyle'], auxillaryTextStyles = kwargs.get('auxillaryTextStyles', dict()),
                                            xPos = kwargs.get('xPos', 0), yPos = kwargs.get('yPos', 0), width = kwargs.get('width', 0), height = kwargs.get('height', 0), showElementBox = kwargs.get('showElementBox', False), anchor = kwargs.get('anchor', 'CENTER'))
        self.textElement_SL.elementBox.color = (0, 255, 0, 50)

        self.textElement_SL.layout.selection_color            = self.textElement_SL.textStyles['DEFAULT']['selectionColor']
        self.textElement_SL.layout.selection_background_color = self.textElement_SL.textStyles['DEFAULT']['selectionBackgroundColor']
        
        self.caret = textObjectCaret(layout = self.textElement_SL.layout, color = self.textElement_SL.textStyles['DEFAULT']['selectionColor'])
        self.caret.hide()

        self.hitBox = atmEta_gui_HitBoxes.hitBox_Rectangular(self.textElement_SL.xPos, self.textElement_SL.yPos, self.textElement_SL.width, self.textElement_SL.height)

        self.status = "DEFAULT"

    def process(self, t_elapsed_ns):
        self.caret.process(t_elapsed_ns)

    def handleMouseEvent(self, event):
        selectionPrevious = (self.textElement_SL.layout.selection_start, self.textElement_SL.layout.selection_end)
        if (self.textElement_SL.hidden == False):
            if (event['eType'] == "PRESSED"):
                self.status = "PRESSED"
                self.caret.onMousePress(event['x']*self.textElement_SL.scaler, event['y']*self.textElement_SL.scaler)
            elif (event['eType'] == "DRAGGED"):
                if (self.status == "PRESSED"):
                    self.caret.onMouseDrag(event['x']*self.textElement_SL.scaler, event['y']*self.textElement_SL.scaler)
            elif (event['eType'] == "SELECTIONESCAPED"):
                self.status = "DEFAULT"
                self.caret.resetCaret()
                self.textElement_SL.setLayoutView()
        if (selectionPrevious != (self.textElement_SL.layout.selection_start, self.textElement_SL.layout.selection_end)): return 'selectionUpdated'
        else: return None

    def handleKeyEvent(self, event):
        if (self.textElement_SL.hidden == False):
            if (event['eType'] == "PRESSED"):
                if ((event['symbol'] == 99) and (event['modifiers'] & MODIFIER_CTRL)): #CTRL + C
                    self.__writeToClipBoard(self.textElement_SL.text[self.textElement_SL.layout.selection_start:self.textElement_SL.layout.selection_end])
            elif (event['eType'] == "SELECTIONESCAPED"):
                self.status = "DEFAULT"
                self.caret.resetCaret()

    def show(self): self.textElement_SL.show()
    def hide(self): self.textElement_SL.hide()

    def moveTo(self, x = None, y = None):
        self.textElement_SL.moveTo(x = x, y = y)
        self.hitBox.reposition(xPos = x, yPos = y)

    def changeSize(self, width = None, height = None):
        self.textElement_SL.changeSize(width = width, height = height)
        self.hitBox.resize(width = width, height = height)

    def setText(self, text, textStyle = None):                     self.textElement_SL.setText(text = text, textStyle = textStyle)
    def insertText(self, text, position = None, textStyle = None): self.textElement_SL.insertText(text = text, position = position, textStlye = textStyle)
    def deleteText(self, indexRange):                              self.textElement_SL.deleteText(indexRange = indexRange)
    def getText(self):                                             return self.textElement_SL.text

    def editTextStyle(self, indexRange, style): self.textElement_SL.editTextStyle(indexRange = indexRange, style = style)
    def addTextStyle(self, textStyleName, textStyle): self.textElement_SL.addTextStyle(textStyleName = textStyleName, textStyle = textStyle)
    def changeActiveTextStyle(self, textStyle): self.textElement_SL.changeActiveTextStyle(textStyle = textStyle)

    def on_GUIThemeUpdate(self, **kwargs):
        self.textElement_SL.on_GUIThemeUpdate(**kwargs)
        self.textElement_SL.layout.selection_color = self.textElement_SL.textStyles['DEFAULT']['selectionColor']; self.textElement_SL.layout.selection_background_color = self.textElement_SL.textStyles['DEFAULT']['selectionBackgroundColor']
        if ('caretColor' in self.textElement_SL.textStyles['DEFAULT'].keys()): self.caret.editCaretColor(self.textElement_SL.textStyles['DEFAULT']['caretColor'])

    def on_LanguageUpdate(self, **kwargs):
        self.textElement_SL.on_LanguageUpdate(**kwargs)

    def getTextLength(self): return self.textElement_SL.getTextLength()
    def getContentWidth(self): return self.textElement_SL.getContentWidth()
    def getContentHeight(self): return self.textElement_SL.getContentHeight()

    def isTouched(self, mouseX, mouseY): return ((self.hitBox.isTouched(mouseX, mouseY)) and (self.textElement_SL.hidden == False))

    def delete(self): self.textElement_SL.delete()
        
    def __getFromClipBoard(self):
        return pyperclip.paste()
    
    def __writeToClipBoard(self, text):
        pyperclip.copy(text)

#Text Object - Singular Line, Interactable END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Text Object - Singular Line, Interactable & Editable ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class textObject_SL_IE:
    def __init__(self, **kwargs):
        self.textElement_SL_I = textObject_SL_I(scaler = kwargs['scaler'], batch = kwargs['batch'], group = kwargs['group'],
                                                text = kwargs.get('text', ""), defaultTextStyle = kwargs['defaultTextStyle'], auxillaryTextStyles = kwargs.get('auxillaryTextStyles', dict()),
                                                xPos = kwargs.get('xPos', 0), yPos = kwargs.get('yPos', 0), width = kwargs.get('width', 0), height = kwargs.get('height', 0), showElementBox = kwargs.get('showElementBox', False), anchor = kwargs.get('anchor', 'CENTER'))
        self.textElement_SL_I.caret.show()
        self.textElement_SL = self.textElement_SL_I.textElement_SL
        
        self.textElement_SL.elementBox.color = (0, 0, 255, 50)
        self.textElement_SL.elementBox.visible = kwargs.get('showElementBox', False)
        
        #Functional Object Parameters
        self.hoverFunction      = kwargs.get('hoverFunction',      None)
        self.pressFunction      = kwargs.get('pressFunction',      None)
        self.releaseFunction    = kwargs.get('releaseFunction',    None)
        self.textUpdateFunction = kwargs.get('textUpdateFunction', None)

        #Keyboard Interaction Control Variables
        self.pressedKey = None; self.insertMode = False
        self.keyPressReadInterval = 100; self.keyPressReadTimer_ms = 0
        
        #Object Status Variables
        self.deactivated = False; self.hidden = False

    def process(self, t_elapsed_ns):
        self.textElement_SL_I.caret.process(t_elapsed_ns)
        if (self.pressedKey != None):
            self.keyPressReadTimer_ms += t_elapsed_ns / 1e6
            if (self.keyPressReadInterval <= self.keyPressReadTimer_ms):
                self.keyPressReadTimer_ms = self.keyPressReadTimer_ms % self.keyPressReadInterval
                selectionPrevious = (self.textElement_SL.layout.selection_start, self.textElement_SL.layout.selection_end); textPrevious = self.textElement_SL.text
                self.__readPressedKey()
                if   (textPrevious != self.textElement_SL.text):                                                                    return 'textUpdated'
                elif (selectionPrevious != (self.textElement_SL.layout.selection_start, self.textElement_SL.layout.selection_end)): return 'selectionUpdated'
                else:                                                                                                               return None

    def handleMouseEvent(self, event):
        selectionPrevious = (self.textElement_SL.layout.selection_start, self.textElement_SL.layout.selection_end)
        if not((self.deactivated == True) or (self.textElement_SL.hidden == True)):
            if (event['eType'] == "PRESSED"):
                self.textElement_SL_I.status = "PRESSED"
                self.textElement_SL_I.caret.onMousePress(event['x']*self.textElement_SL.scaler, event['y']*self.textElement_SL.scaler)
            elif (event['eType'] == "DRAGGED"):
                if (self.textElement_SL_I.status == "PRESSED"):
                    self.textElement_SL_I.caret.onMouseDrag(event['x']*self.textElement_SL.scaler, event['y']*self.textElement_SL.scaler)
            elif (event['eType'] == "SELECTIONESCAPED"):
                self.textElement_SL_I.status = "DEFAULT"
                self.textElement_SL_I.caret.resetCaret()
                self.textElement_SL.setLayoutView()
        if (selectionPrevious != (self.textElement_SL.layout.selection_start, self.textElement_SL.layout.selection_end)): return 'selectionUpdated'
        else: return None

    def handleKeyEvent(self, event):
        selectionPrevious = (self.textElement_SL.layout.selection_start, self.textElement_SL.layout.selection_end); textPrevious = self.textElement_SL.text
        if not((self.deactivated == True) or (self.textElement_SL.hidden == True)):
            if   (event['eType'] == "PRESSED"):  self.pressedKey = {'symbol': event['symbol'], 'modifiers': event['modifiers']}; self.__readPressedKey(); self.keyPressReadTimer_ms = -(self.keyPressReadInterval*5)
            elif (event['eType'] == "RELEASED"): self.pressedKey = None
            elif (event['eType'] == "SELECTIONESCAPED"):
                self.pressedKey = None
                self.textElement_SL_I.status = "DEFAULT"
                self.textElement_SL_I.caret.resetCaret()
        if (textPrevious != self.textElement_SL.text): return 'textUpdated'
        elif (selectionPrevious != (self.textElement_SL.layout.selection_start, self.textElement_SL.layout.selection_end)): return 'selectionUpdated'
        else: return None

    def show(self): self.textElement_SL.show()
    def hide(self): self.textElement_SL.hide()

    def moveTo(self, x = None, y = None):
        self.textElement_SL_I.moveTo(x = x, y = y)

    def changeSize(self, width = None, height = None):
        self.textElement_SL_I.changeSize(width = width, height = height)

    def setText(self, text, textStyle = None):                     self.textElement_SL.setText(text = text, textStyle = textStyle)
    def insertText(self, text, position = None, textStyle = None): self.textElement_SL.insertText(text = text, position = position, textStyle = textStyle)
    def deleteText(self, indexRange):                              self.textElement_SL.deleteText(indexRange = indexRange)
    def getText(self):                                             return self.textElement_SL.text

    def editTextStyle(self, indexRange, style):       self.textElement_SL.editTextStyle(indexRange = indexRange, style = style)
    def addTextStyle(self, textStyleName, textStyle): self.textElement_SL.addTextStyle(textStyleName = textStyleName, textStyle = textStyle)
    def changeActiveTextStyle(self, textStyle):       self.textElement_SL.changeActiveTextStyle(textStyle = textStyle)

    def on_GUIThemeUpdate(self, **kwargs): self.textElement_SL_I.on_GUIThemeUpdate(**kwargs)
    def on_LanguageUpdate(self, **kwargs): self.textElement_SL_I.on_LanguageUpdate(**kwargs)

    def getTextLength(self): return self.textElement_SL.getTextLength()
    def getContentWidth(self): return self.textElement_SL.getContentWidth()
    def getContentHeight(self): return self.textElement_SL.getContentHeight()

    def isTouched(self, mouseX, mouseY): return self.textElement_SL_I.isTouched(mouseX, mouseY)

    def delete(self): self.textElement_SL_I.delete()

    def __readPressedKey(self):
        if (self.pressedKey['symbol'] in CHARTABLE_LOWER.keys()):
            #Character-Combined AUX ShortKeys
            #---SELECT ALL
            if ((self.pressedKey['symbol'] == 97) and (self.pressedKey['modifiers'] == MODIFIER_CTRL)): #CTRL + A
                self.textElement_SL_I.caret.move(len(self.textElement_SL.text), basePos = 0)
            #---COPY TO CLIPBOARD
            elif ((self.pressedKey['symbol'] == 99) and (self.pressedKey['modifiers'] & MODIFIER_CTRL) and not(self.pressedKey['modifiers'] & MODIFIER_SHIFT)): #CTRL + C (Shift Except)
                self.__writeToClipBoard(self.textElement_SL.text[self.textElement_SL.layout.selection_start:self.textElement_SL.layout.selection_end])
            #---PASTE FROM CLIPBOARD
            elif ((self.pressedKey['symbol'] == 118) and (self.pressedKey['modifiers'] & MODIFIER_CTRL) and not(self.pressedKey['modifiers'] & MODIFIER_SHIFT)): #CTRL + C (Shift Except)
                clipboardText = self.__getFromClipBoard()
                if (clipboardText != None): self.__insertCharacter(clipboardText)

            #Else
            else:
                useUpper = (((self.pressedKey['modifiers'] & MODIFIER_CAPSLOCK) and not (self.pressedKey['modifiers'] & MODIFIER_SHIFT)) or (self.pressedKey['modifiers'] & MODIFIER_SHIFT) and not (self.pressedKey['modifiers'] & MODIFIER_CAPSLOCK))
                #Identify the character type
                if (97 <= self.pressedKey['symbol']) and (self.pressedKey['symbol'] <= 122):                            
                    if (useUpper == True):                                                                              charType = "normalChar_upper"
                    else:                                                                                               charType = "normalChar_lower"
                elif ((49 <= self.pressedKey['symbol']) and (self.pressedKey['symbol'] <= 58) and (useUpper == False)): charType = "number"
                elif (self.pressedKey['symbol'] == 32):                                                                 charType = "SPACE"
                elif (self.pressedKey['symbol'] == 65289):                                                              charType = "TAB"
                else:                                                                                                   charType = "specialCharacter"
                if (useUpper == True): character = CHARTABLE_UPPER[self.pressedKey['symbol']]
                else:                  character = CHARTABLE_LOWER[self.pressedKey['symbol']]
                self.__insertCharacter(character)

        #Navigation
        elif (self.pressedKey['symbol'] == 65361): self.__moveWithinText('L')
        elif (self.pressedKey['symbol'] == 65363): self.__moveWithinText('R')

        #Text Edit
        elif (self.pressedKey['symbol'] == 65288): #BACKSPACE
            self.__removeText()
        elif (self.pressedKey['symbol'] == 65535): #DELETE
            self.__removeText()
        elif (self.pressedKey['symbol'] == 65379): #INSERT
            pass
        elif (self.pressedKey['symbol'] == 65360): #HOME
            self.textElement_SL_I.caret.move(0, basePos = 0)
        elif (self.pressedKey['symbol'] == 65367): #END
            self.textElement_SL_I.caret.move(len(self.textElement_SL.text), basePos = len(self.textElement_SL.text))
        #Command Key

    def __insertCharacter(self, text):
        if (self.textElement_SL.layout.selection_start != self.textElement_SL.layout.selection_end): self.__removeText(alone = False)
        self.textElement_SL.insertText(text, self.textElement_SL.layout.selection_start)
        if (self.textElement_SL_I.caret.position_mobile == None): newCaretPos = len(text)
        else:                                                     newCaretPos = self.textElement_SL_I.caret.position_mobile+len(text)
        self.textElement_SL_I.caret.move(newCaretPos, basePos = newCaretPos)
        if (self.textUpdateFunction != None): self.textUpdateFunction(self)

    def __removeText(self, alone = True):
        if (self.textElement_SL_I.caret.position_mobile == self.textElement_SL_I.caret.position_base): #Delete a single character from the current position
            if (0 < self.textElement_SL_I.caret.position_mobile):
                self.deleteText((self.textElement_SL_I.caret.position_mobile-1, self.textElement_SL_I.caret.position_mobile-1))
                self.textElement_SL_I.caret.move(self.textElement_SL_I.caret.position_mobile-1, basePos = self.textElement_SL_I.caret.position_mobile-1)
                if (alone == True):
                    if (self.textUpdateFunction != None): self.textUpdateFunction(self)
        else:                                                                                
            self.deleteText((self.textElement_SL.layout.selection_start, self.textElement_SL.layout.selection_end-1))
            self.textElement_SL_I.caret.move(self.textElement_SL.layout.selection_start, basePos = self.textElement_SL.layout.selection_start)
            if (alone == True):
                if (self.textUpdateFunction != None): self.textUpdateFunction(self)

    def __moveWithinText(self, movDir):
        if (self.pressedKey['modifiers'] & MODIFIER_SHIFT): #MOVE+SHIFT
            if (movDir == 'L'):
                if (0 < self.textElement_SL_I.caret.position_mobile):
                    self.textElement_SL_I.caret.move(self.textElement_SL_I.caret.position_mobile-1)
            elif (movDir == 'R'):
                if (self.textElement_SL_I.caret.position_mobile < len(self.textElement_SL.text)):
                    self.textElement_SL_I.caret.move(self.textElement_SL_I.caret.position_mobile+1)
        else: #MOVE
            if (movDir == 'L'):
                if (self.textElement_SL.layout.selection_start == self.textElement_SL.layout.selection_end):
                    if (0 < self.textElement_SL_I.caret.position_mobile): self.textElement_SL_I.caret.move(self.textElement_SL_I.caret.position_mobile-1, basePos = self.textElement_SL_I.caret.position_mobile-1)
                else:                                                     self.textElement_SL_I.caret.move(self.textElement_SL.layout.selection_start,    basePos = self.textElement_SL.layout.selection_start)
            elif (movDir == 'R'):
                if (self.textElement_SL.layout.selection_start == self.textElement_SL.layout.selection_end):
                    if (self.textElement_SL_I.caret.position_mobile < len(self.textElement_SL.text)): self.textElement_SL_I.caret.move(self.textElement_SL_I.caret.position_mobile+1, basePos = self.textElement_SL_I.caret.position_mobile+1)
                else:                                                                                 self.textElement_SL_I.caret.move(self.textElement_SL.layout.selection_end,      basePos = self.textElement_SL.layout.selection_end)

    #if   (self.pressedKey['modifiers'] == 0b00000): #DEFAULT
    #elif (self.pressedKey['modifiers'] == 0b00001): #SHIFT
    #elif (self.pressedKey['modifiers'] == 0b00010): #CTRL
    #elif (self.pressedKey['modifiers'] == 0b00100): #ALT
    #elif (self.pressedKey['modifiers'] == 0b01000): #CAPS LOCK
    #elif (self.pressedKey['modifiers'] == 0b10000): #NUM LOCK
        
    def __getFromClipBoard(self):
        return pyperclip.paste()
    
    def __writeToClipBoard(self, text):
        pyperclip.copy(text)
#Text Object - Singular Line, Interactable & Editable END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#Text Object Caret --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class textObjectCaret:
    def __init__(self, layout, color = (0, 0, 0, 255), width = 1):
        self.layout = layout
        self.caretShape = pyglet.shapes.Line(0, 0, 0, 0, width = width, color = color, batch = layout.batch, group = layout.group)
        self.caretShape.visible = True

        self.position_base   = None
        self.position_mobile = None

        self.hidden = False
        
        #Blinker Variables
        self.blinkInterval_ms = 500; self.blinkTimer_ms = 0

    def process(self, t_elapsed_ns):
        if ((self.hidden == False) and (self.position_base != None)):
            self.blinkTimer_ms += t_elapsed_ns / 1e6
            if (self.blinkInterval_ms <= self.blinkTimer_ms):
                self.blinkTimer_ms = self.blinkTimer_ms % self.blinkInterval_ms
                if (self.caretShape.visible == True): self.caretShape.visible = False
                else:                                 self.caretShape.visible = True

    def hide(self):
        self.hidden = True
        self.caretShape.visible = False

    def show(self):
        self.hidden = False

    def editCaretColor(self, newColor):
        self.caretShape.color = newColor

    def move(self, position, basePos = None):
        previousPosition = self.position_mobile; previousBase = self.position_base
        mouseXCompensator, mouseYCompensator = self.__getMouseCompensators()
        self.position_mobile = position
        if (basePos != None): self.position_base = basePos
        caretX_rel = self.layout.get_point_from_position(self.position_mobile)[0]
        if (caretX_rel < self.layout.view_x):                       caretX = 0;                               viewMove = 'left'
        elif (self.layout.width < caretX_rel - self.layout.view_x): caretX = self.layout.width;               viewMove = 'right'
        else:                                                       caretX = caretX_rel - self.layout.view_x; viewMove = None
        self.caretShape.x  = caretX + self.layout.x - mouseXCompensator; self.caretShape.x2 = self.caretShape.x
        if   (self.layout.anchor_y == 'bottom'): self.caretShape.y  = self.layout.y - mouseYCompensator;               
        elif (self.layout.anchor_y == 'center'): self.caretShape.y  = self.layout.y - mouseYCompensator + self.layout.height/2 - self.layout.content_height/2
        elif (self.layout.anchor_y == 'top'):    self.caretShape.y  = self.layout.y - mouseYCompensator + self.layout.height - self.layout.content_height
        self.caretShape.y2 = self.caretShape.y + self.layout.content_height
        if (self.hidden == False): self.caretShape.visible = True; self.blinkTimer_ms = 0
        
        if ((previousPosition == self.position_mobile) and (previousBase == self.position_base)): return False
        else: self.__applyLayoutSelection(viewMove); return True

    def resetCaret(self):
        self.position_base   = None
        self.position_mobile = None
        self.caretShape.visible = False
        self.layout.selection_start = 0; self.layout.selection_end = 0

    def onMousePress(self, mouseX, mouseY):
        mouseXCompensator, mouseYCompensator = self.__getMouseCompensators()
        self.position_base = self.layout.get_position_from_point(mouseX+mouseXCompensator, mouseY+mouseYCompensator)
        self.position_mobile = self.position_base
        self.caretShape.x  = self.layout.get_point_from_position(self.position_base)[0] + self.layout.x - mouseXCompensator - self.layout.view_x; self.caretShape.x2 = self.caretShape.x
        if   (self.layout.anchor_y == 'bottom'): self.caretShape.y  = self.layout.y - mouseYCompensator;               
        elif (self.layout.anchor_y == 'center'): self.caretShape.y  = self.layout.y - mouseYCompensator + self.layout.height/2 - self.layout.content_height/2
        elif (self.layout.anchor_y == 'top'):    self.caretShape.y  = self.layout.y - mouseYCompensator + self.layout.height - self.layout.content_height
        self.caretShape.y2 = self.caretShape.y + self.layout.content_height
        if (self.hidden == False): self.caretShape.visible = True; self.blinkTimer_ms = 0
        self.initialViewX = self.layout.view_x
        self.__applyLayoutSelection()

    def onMouseDrag(self, mouseX, mouseY):
        previousPosition = self.position_mobile
        mouseXCompensator, mouseYCompensator = self.__getMouseCompensators()
        self.position_mobile = self.layout.get_position_from_point(mouseX+mouseXCompensator, mouseY+mouseYCompensator)
        caretX_rel = self.layout.get_point_from_position(self.position_mobile)[0]
        if (caretX_rel < self.layout.view_x):                       caretX = 0;                               viewMove = 'left'
        elif (self.layout.width < caretX_rel - self.layout.view_x): caretX = self.layout.width;               viewMove = 'right'
        else:                                                       caretX = caretX_rel - self.layout.view_x; viewMove = None
        self.caretShape.x  = caretX + self.layout.x - mouseXCompensator; self.caretShape.x2 = self.caretShape.x
        if   (self.layout.anchor_y == 'bottom'): self.caretShape.y  = self.layout.y - mouseYCompensator;               
        elif (self.layout.anchor_y == 'center'): self.caretShape.y  = self.layout.y - mouseYCompensator + self.layout.height/2 - self.layout.content_height/2
        elif (self.layout.anchor_y == 'top'):    self.caretShape.y  = self.layout.y - mouseYCompensator + self.layout.height - self.layout.content_height
        self.caretShape.y2 = self.caretShape.y + self.layout.content_height
        if (self.hidden == False): self.caretShape.visible = True; self.blinkTimer_ms = 0

        if (previousPosition == self.position_mobile): return False
        else: self.__applyLayoutSelection(viewMove); return True

    def __getMouseCompensators(self):
        if   (self.layout.anchor_x == 'left'):   mouseXCompensator = 0
        elif (self.layout.anchor_x == 'center'): mouseXCompensator = self.layout.content_width/2
        elif (self.layout.anchor_x == 'right'):  mouseXCompensator = self.layout.content_width
        
        if   (self.layout.anchor_y == 'bottom'): mouseYCompensator = 0                 
        elif (self.layout.anchor_y == 'center'): mouseYCompensator = self.layout.height/2
        elif (self.layout.anchor_y == 'top'):    mouseYCompensator = self.layout.height
        return (mouseXCompensator, mouseYCompensator)

    def __applyLayoutSelection(self, viewMove = None):
        if (self.position_base <= self.position_mobile): self.layout.selection_start = self.position_base;   self.layout.selection_end = self.position_mobile
        else:                                            self.layout.selection_start = self.position_mobile; self.layout.selection_end = self.position_base
        if   (viewMove == 'left'):  self.layout.view_x = self.layout.get_point_from_position(self.position_mobile)[0]
        elif (viewMove == 'right'): self.layout.view_x = self.layout.get_point_from_position(self.position_mobile)[0] - self.layout.width
#Text Object Caret End ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------       