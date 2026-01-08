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

TEXTANCHOR = {'CENTER': ('center', 'center'),
              'W':      ('left',   'center'),
              'NW':     ('left',   'top'),
              'N':      ('center', 'top'),
              'NE':     ('right',  'top'),
              'E':      ('right',  'center'),
              'SE':     ('right',  'center'),
              'S':      ('center', 'center'),
              'SW':     ('left',   'bottom')}

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
        for _ in range (len(self.text)): self.textStyleAtIndex.append(self.activeTextStyle)

        #---Layout Initialization
        self.layout = pyglet.text.layout.IncrementalTextLayout(self.document, 0, 0, batch = self.batch, group = self.group, multiline = False)
        self.textAnchor = None; self.textAnchor_x = None; self.textAnchor_y = None; 
        self.xOverSizeDelta = None; self.yOverSizeDelta = None

        #Object Control
        self.hidden = False

        #Post Initialization
        self.setAnchor(kwargs.get('anchor', 'CENTER'))
        self.locateLayout()

    def process(self, t_elapsed_ns): 
        pass
    
    def handleMouseEvent(self, event): 
        pass
    
    def handleKeyEvent(self, event): 
        pass

    def show(self):
        self.hidden = False
        self.layout.document = self.document
        self.elementBox.visible = self.showElementBox
        self.locateLayout()

    def hide(self):
        self.hidden = True
        self.layout.document = self.document_empty
        self.elementBox.visible = False

    def isHidden(self): 
        return self.hidden

    def moveTo(self, x = None, y = None):
        if (x is not None):
            self.xPos = x
            if (self.showElementBox == True): self.elementBox.x = self.xPos*self.scaler
        if (y is not None):
            self.yPos = y
            if (self.showElementBox == True): self.elementBox.y = self.yPos*self.scaler
        if (self.hidden == False): self.locateLayout()

    def changeSize(self, width = None, height = None):
        if (width is not None):
            self.width = width
            if (self.showElementBox == True): self.elementBox.width = self.width*self.scaler
            self.layout.width = self.width*self.scaler
        if (height is not None):
            self.height = height
            if (self.showElementBox == True): self.elementBox.height = self.height*self.scaler
            self.layout.height = self.height*self.scaler
        if (self.hidden == False): self.locateLayout()

    def setAnchor(self, newAnchor):
        self.textAnchor_x, self.textAnchor_y = TEXTANCHOR[newAnchor]
        self.textAnchor = newAnchor
        self.document.set_paragraph_style(0, len(self.text), {'align': self.textAnchor_x})
        if (self.hidden == False): self.locateLayout()

    def changePosSizeAnchor(self, x = None, y = None, width = None, height = None, anchor = None):
        if (x is not None):
            self.xPos = x
            if (self.showElementBox == True): self.elementBox.x = self.xPos*self.scaler
        if (y is not None):
            self.yPos = y
            if (self.showElementBox == True): self.elementBox.y = self.yPos*self.scaler
        if (width is not None):
            self.width = width
            if (self.showElementBox == True): self.elementBox.width = self.width*self.scaler
        if (height is not None):
            self.height = height
            if (self.showElementBox == True): self.elementBox.height = self.height*self.scaler
        if (anchor is not None):
            self.textAnchor_x, self.textAnchor_y = TEXTANCHOR[anchor]
            self.textAnchor = anchor
            self.document.set_paragraph_style(0, len(self.text), {'align': self.textAnchor_x})
        if (self.hidden == False): self.locateLayout()

    def setText(self, text, textStyle = None):
        #Initialize
        self.document.delete_text(0, len(self.document.text))
        self.text = text
        nText = len(self.text)

        if (0 < nText):
            #Text Style Update
            tStyle_default = self.activeTextStyle
            if (textStyle is not None) and (not isinstance(textStyle, list)): tStyle_default = textStyle
            self.textStyleAtIndex = [tStyle_default]*nText
            if isinstance(textStyle, list):
                for tStyleBlock in textStyle:
                    idx_beg, idx_end = self.__reformIndexRange(tStyleBlock[0], nText)
                    self.textStyleAtIndex[idx_beg:idx_end+1] = [tStyleBlock[1]]*(idx_end-idx_beg+1)

            #Document Text Update
            self.document.text = self.text

            #Document Style Update
            tStyles         = self.textStyles
            tStyles_current = self.textStyleAtIndex
            idx_anchor = 0
            tStyle_current = tStyles_current[0]
            if tStyle_current not in tStyles: tStyle_current = self.activeTextStyle
            for idx_rel in range(1, nText):
                if (tStyles_current[idx_rel] != tStyle_current):
                    self.document.set_style(start=idx_anchor, end=idx_rel, attributes=tStyles[tStyle_current])
                    idx_anchor     = idx_rel
                    tStyle_current = tStyles_current[idx_rel]
                    if tStyle_current not in tStyles: tStyle_current = self.activeTextStyle
            self.document.set_style(start=idx_anchor, end=nText, attributes=tStyles[tStyle_current])
        else: self.textStyleAtIndex = []

        #Document Paragraph Style Update
        self.document.set_paragraph_style(0, nText, {'align': self.textAnchor_x})

        #If not hidden, update the layout position
        if (self.hidden == False): self.locateLayout()

    def insertText(self, text, position = None, textStyle = None):
        #Positional Text and TextStyle Computation
        tLen_current   = len(self.text)
        textStyleToUse = self.activeTextStyle if (textStyle is None) else textStyle
        if (position is None):
            initialPosition = tLen_current
            self.text             += text
            self.textStyleAtIndex += [textStyleToUse]*len(text)
        else:
            if (position < 0):
                if (position < -tLen_current): position = 0
                else:                          position = tLen_current + position + 1
            elif (tLen_current < position):    position = tLen_current
            initialPosition = position
            self.text             = self.text[:position]             + text                       + self.text[position:]
            self.textStyleAtIndex = self.textStyleAtIndex[:position] + [textStyleToUse]*len(text) + self.textStyleAtIndex[position:]
            
        #Document Text Update
        self.document.text = self.text

        #Document Style Update
        tStyles         = self.textStyles
        tStyles_current = self.textStyleAtIndex
        tLen            = len(self.text)
        if 0 < tLen:
            idx_anchor     = 0
            tStyle_current = tStyles_current[0]
            for idx_rel in range (1, tLen):
                if (tStyles_current[idx_rel] != tStyle_current):
                    self.document.set_style(start = idx_anchor, end = idx_rel, attributes = tStyles[tStyle_current])
                    idx_anchor = idx_rel
                    tStyle_current = tStyles_current[idx_rel]
            self.document.set_style(start = idx_anchor, end = tLen, attributes = tStyles[tStyle_current])
        self.document.set_paragraph_style(initialPosition, tLen, {'align': self.textAnchor_x})

        #If not hidden, update the layout position
        if (self.hidden == False): self.locateLayout()

    def deleteText(self, indexRange):
        if (indexRange == 'all'):
            self.text = ""
            self.textStyleAtIndex.clear()
            self.document.text = ""
        else:
            cir_beg, cir_end = self.__reformIndexRange(indexRange, len(self.document.text))
            self.text             = self.text[:cir_beg]             + self.text[cir_end+1:]
            self.textStyleAtIndex = self.textStyleAtIndex[:cir_beg] + self.textStyleAtIndex[cir_end+1:]
            self.document.text    = self.text
            tStyles         = self.textStyles
            tStyles_current = self.textStyleAtIndex
            tLen = len(tStyles_current)
            if 0 < tLen:
                idx_anchor     = 0
                tStyle_current = tStyles_current[0]
                for idx_rel in range (1, tLen):
                    if (tStyles_current[idx_rel] != tStyle_current):
                        self.document.set_style(start = idx_anchor, end = idx_rel, attributes = tStyles[tStyle_current])
                        idx_anchor = idx_rel
                        tStyle_current = tStyles_current[idx_rel]
                self.document.set_style(start = idx_anchor, end = tLen, attributes = tStyles[tStyle_current])
        #If not hidden, update the layout position
        if (self.hidden == False): self.locateLayout()

    def getText(self): 
        return self.text

    def editTextStyle(self, indexRange, style):
        tStyle = self.textStyles[style]
        if (indexRange == 'all'):
            self.document.set_style(start = 0, end = len(self.document.text), attributes = tStyle)
            self.textStyleAtIndex = [style]*len(self.textStyleAtIndex)
        else:
            cir_beg, cir_end = self.__reformIndexRange(indexRange, len(self.document.text))
            idx_anchor = None
            tStyles_current = self.textStyleAtIndex
            for idx_rel in range (cir_beg, cir_end+1):
                update = (tStyles_current[idx_rel] != style)
                if   (idx_anchor is     None and     update): idx_anchor = idx_rel
                elif (idx_anchor is not None and not update):
                    self.document.set_style(start = idx_anchor, end = idx_rel, attributes = tStyle)
                    idx_anchor = None
            if (idx_anchor is not None): self.document.set_style(start = idx_anchor, end = idx_rel+1, attributes = tStyle)
            tStyles_current[cir_beg:cir_end+1] = [style]*(cir_end-cir_beg+1)
            
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
        if (newLanguageText is not None) and (newLanguageText != self.text): self.setText(newLanguageText, textStyle = 'DEFAULT')
        else:
            for i in range (len(self.text)): self.document.set_style(start = i, end = i+1, attributes = self.textStyles[self.textStyleAtIndex[i]])

        #If not hidden, update the layout position
        if (self.hidden == False): self.locateLayout()

    def getWidth(self):
        return self.width
    
    def getHeight(self):
        return self.height
    
    def getTextLength(self):
        return len(self.text)
    
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

    def getTextAnchor(self): 
        return self.textAnchor

    def isTouched(self, mouseX, mouseY): 
        return False

    def delete(self): 
        self.layout.delete()

    #Locate Layout
    def locateLayout(self):
        self.xOverSizeDelta = round(self.layout.content_width - self.width*self.scaler, 1)
        newLayoutXPos = round(self.xPos *self.scaler, 1)
        newLayoutYPos = None
        newWidth      = round(self.width*self.scaler, 1)
        newHeight     = None
        self.yOverSizeDelta = round(self.layout.content_height - self.height*self.scaler, 1)
        if (0 < self.yOverSizeDelta): newHeight = round(self.height*self.scaler, 1)
        else:                         newHeight = self.layout.content_height
        if   (self.textAnchor_y == 'bottom'): newLayoutYPos = round(self.yPos*self.scaler,                                           1)
        elif (self.textAnchor_y == 'center'): newLayoutYPos = round(self.yPos*self.scaler + self.height*self.scaler/2 - newHeight/2, 1)
        elif (self.textAnchor_y == 'top'):    newLayoutYPos = round(self.yPos*self.scaler + self.height*self.scaler   - newHeight,   1)
        updated_xPos   = (newLayoutXPos != self.layout.x)
        updated_yPos   = (newLayoutYPos != self.layout.y)
        updated_width  = (newWidth      != self.layout.width)
        updated_height = (newHeight     != self.layout.height)

        #Apply new positions
        update_xPos = updated_xPos or updated_width
        update_yPos = updated_yPos
        if updated_width: self.layout.width  = newWidth
        if updated_height: self.layout.height = newHeight
        if update_xPos and update_yPos: self.layout.position = (newLayoutXPos, newLayoutYPos, 0)
        elif update_xPos: self.layout.x = newLayoutXPos
        elif update_yPos: self.layout.y = newLayoutYPos

        #Set Layout View
        self.setLayoutView()

    #Set Layout View
    def setLayoutView(self):
        osd_x = self.xOverSizeDelta
        ods_y = self.yOverSizeDelta
        ta_x = self.textAnchor_x
        ta_y = self.textAnchor_y
        if (0 < osd_x):
            if   (ta_x == 'left'):   newViewX = 0
            elif (ta_x == 'center'): newViewX = round(osd_x/2, 1)
            elif (ta_x == 'right'):  newViewX = round(osd_x,   1)
        else:                        newViewX = 0
        if (0 < ods_y):
            if   (ta_y == 'bottom'): newViewY = 0
            elif (ta_y == 'center'): newViewY = -round(ods_y/2, 1)
            elif (ta_y == 'top'):    newViewY = -round(ods_y,   1)
        else:                        newViewY = 0
        if (self.layout.view_x != newViewX): self.layout.view_x = newViewX
        if (self.layout.view_y != newViewY): self.layout.view_y = newViewY

    #Reform the passed index range
    def __reformIndexRange(self, indexRange, nElements):
        ir_beg, ir_end = indexRange
        cir_beg = 0         if (ir_beg is None) else ir_beg
        cir_end = nElements if (ir_end is None) else ir_end
        if (cir_beg < 0):
            if (cir_beg < -nElements): cir_beg = 0
            else:                      cir_beg = nElements + cir_beg
        elif (nElements <= cir_beg):   cir_beg = nElements - 1
        if (cir_end < 0):
            if (cir_end < -nElements): cir_end = 0
            else:                      cir_end = nElements + cir_end
        elif (nElements <= cir_end):   cir_end = nElements - 1
        if (cir_beg <= cir_end): return cir_beg, cir_end
        else:                    return cir_end, cir_beg
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

        #Internal Functions Dict
        self.__mouseEventHandlers = {'PRESSED':          self.__hme_PRESSED,
                                     'DRAGGED':          self.__hme_DRAGGED,
                                     'SELECTIONESCAPED': self.__hme_SELECTIONESCAPED}
        self.__keyEventHandlers = {'PRESSED':          self.__hke_PRESSED,
                                   'SELECTIONESCAPED': self.__hke_SELECTIONESCAPED}

    def process(self, t_elapsed_ns):
        self.caret.process(t_elapsed_ns)

    def handleMouseEvent(self, event):
        if (self.textElement_SL.hidden == True): return
        selectionPrevious = (self.textElement_SL.layout.selection_start, self.textElement_SL.layout.selection_end)
        if (event['eType'] in self.__mouseEventHandlers): self.__mouseEventHandlers[event['eType']](event = event)
        if (selectionPrevious != (self.textElement_SL.layout.selection_start, self.textElement_SL.layout.selection_end)): return 'selectionUpdated'
        return None
    def __hme_PRESSED(self, event):
        self.status = "PRESSED"
        self.caret.onMousePress(event['x']*self.textElement_SL.scaler, event['y']*self.textElement_SL.scaler)
    def __hme_DRAGGED(self, event):
        if (self.status == "PRESSED"):
            self.caret.onMouseDrag(event['x']*self.textElement_SL.scaler, event['y']*self.textElement_SL.scaler)
    def __hme_SELECTIONESCAPED(self, event):
        self.status = "DEFAULT"
        self.caret.resetCaret()
        self.textElement_SL.setLayoutView()

    def handleKeyEvent(self, event):
        if (self.textElement_SL.hidden == True): return
        if (event['eType'] in self.__keyEventHandlers): self.__keyEventHandlers[event['eType']](event = event)
    def __hke_PRESSED(self, event):
        if ((event['symbol'] == 99) and (event['modifiers'] & MODIFIER_CTRL)): #CTRL + C
            self.__writeToClipBoard(self.textElement_SL.text[self.textElement_SL.layout.selection_start:self.textElement_SL.layout.selection_end])
    def __hke_SELECTIONESCAPED(self, event):
        self.status = "DEFAULT"
        self.caret.resetCaret()

    def show(self): 
        self.textElement_SL.show()

    def hide(self): 
        self.textElement_SL.hide()

    def moveTo(self, x = None, y = None):
        self.textElement_SL.moveTo(x = x, y = y)
        self.hitBox.reposition(xPos = x, yPos = y)

    def changeSize(self, width = None, height = None):
        self.textElement_SL.changeSize(width = width, height = height)
        self.hitBox.resize(width = width, height = height)

    def setText(self, text, textStyle = None):
        self.textElement_SL.setText(text = text, textStyle = textStyle)
    
    def insertText(self, text, position = None, textStyle = None):
        self.textElement_SL.insertText(text = text, position = position, textStlye = textStyle)
    
    def deleteText(self, indexRange):
        self.textElement_SL.deleteText(indexRange = indexRange)
    
    def getText(self):
        return self.textElement_SL.text

    def editTextStyle(self, indexRange, style): 
        self.textElement_SL.editTextStyle(indexRange = indexRange, style = style)
        
    def addTextStyle(self, textStyleName, textStyle): 
        self.textElement_SL.addTextStyle(textStyleName = textStyleName, textStyle = textStyle)
        
    def changeActiveTextStyle(self, textStyle): 
        self.textElement_SL.changeActiveTextStyle(textStyle = textStyle)

    def on_GUIThemeUpdate(self, **kwargs):
        self.textElement_SL.on_GUIThemeUpdate(**kwargs)
        self.textElement_SL.layout.selection_color = self.textElement_SL.textStyles['DEFAULT']['selectionColor']; self.textElement_SL.layout.selection_background_color = self.textElement_SL.textStyles['DEFAULT']['selectionBackgroundColor']
        if ('caretColor' in self.textElement_SL.textStyles['DEFAULT'].keys()): self.caret.editCaretColor(self.textElement_SL.textStyles['DEFAULT']['caretColor'])

    def on_LanguageUpdate(self, **kwargs):
        self.textElement_SL.on_LanguageUpdate(**kwargs)

    def getTextLength(self): 
        return self.textElement_SL.getTextLength()
    
    def getContentWidth(self): 
        return self.textElement_SL.getContentWidth()
    
    def getContentHeight(self): 
        return self.textElement_SL.getContentHeight()

    def isTouched(self, mouseX, mouseY): 
        return ((self.hitBox.isTouched(mouseX, mouseY)) and (self.textElement_SL.hidden == False))

    def delete(self): 
        self.textElement_SL.delete()
        
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
        self.pressedKey = None
        self.keyPressReadInterval_ns = 25e6
        self.keyPressReadTimer_ns    = 0
        
        #Object Status Variables
        self.deactivated = False; self.hidden = False

        #Internal Functions Dict
        self.__mouseEventHandlers = {'PRESSED':          self.__hme_PRESSED,
                                     'DRAGGED':          self.__hme_DRAGGED,
                                     'SELECTIONESCAPED': self.__hme_SELECTIONESCAPED}
        self.__keyEventHandlers = {'PRESSED':          self.__hke_PRESSED,
                                   'RELEASED':         self.__hke_RELEASED,
                                   'SELECTIONESCAPED': self.__hke_SELECTIONESCAPED}

    def process(self, t_elapsed_ns):
        #Process Caret
        self.textElement_SL_I.caret.process(t_elapsed_ns)
        #If no key is pressed, return
        if (self.pressedKey is None): return
        #Update the key press read timer
        self.keyPressReadTimer_ns += t_elapsed_ns
        #If the key press read timer is less than the interval, return
        if (self.keyPressReadTimer_ns < self.keyPressReadInterval_ns): return
        #Update key press read timer
        self.keyPressReadTimer_ns = self.keyPressReadTimer_ns%self.keyPressReadInterval_ns
        #Record previous data
        selectionPrevious = (self.textElement_SL.layout.selection_start, self.textElement_SL.layout.selection_end)
        textPrevious      = self.textElement_SL.text
        #Read pressed key
        self.__readPressedKey()
        #Compare new text and selection, and return
        if (textPrevious      != self.textElement_SL.text):                                                               return 'textUpdated'
        if (selectionPrevious != (self.textElement_SL.layout.selection_start, self.textElement_SL.layout.selection_end)): return 'selectionUpdated'

    def handleMouseEvent(self, event):
        if ((self.deactivated == True) or (self.textElement_SL.hidden == True)): return
        selectionPrevious = (self.textElement_SL.layout.selection_start, self.textElement_SL.layout.selection_end)
        if (event['eType'] in self.__mouseEventHandlers): self.__mouseEventHandlers[event['eType']](event = event)
        if (selectionPrevious != (self.textElement_SL.layout.selection_start, self.textElement_SL.layout.selection_end)): return 'selectionUpdated'
    def __hme_PRESSED(self, event):
        self.textElement_SL_I.status = "PRESSED"
        self.textElement_SL_I.caret.onMousePress(event['x']*self.textElement_SL.scaler, event['y']*self.textElement_SL.scaler)
    def __hme_DRAGGED(self, event):
        if (self.textElement_SL_I.status == "PRESSED"):
            self.textElement_SL_I.caret.onMouseDrag(event['x']*self.textElement_SL.scaler, event['y']*self.textElement_SL.scaler)
    def __hme_SELECTIONESCAPED(self, event):
        self.textElement_SL_I.status = "DEFAULT"
        self.textElement_SL_I.caret.resetCaret()
        self.textElement_SL.setLayoutView()

    def handleKeyEvent(self, event):
        if ((self.deactivated == True) or (self.textElement_SL.hidden == True)): return
        selectionPrevious = (self.textElement_SL.layout.selection_start, self.textElement_SL.layout.selection_end); textPrevious = self.textElement_SL.text
        if (event['eType'] in self.__keyEventHandlers): self.__keyEventHandlers[event['eType']](event = event)
        if (textPrevious      != self.textElement_SL.text):                                                               return 'textUpdated'
        if (selectionPrevious != (self.textElement_SL.layout.selection_start, self.textElement_SL.layout.selection_end)): return 'selectionUpdated'
        else: return None
    def __hke_PRESSED(self, event):
        self.pressedKey = {'symbol': event['symbol'], 'modifiers': event['modifiers']}
        self.__readPressedKey()
        self.keyPressReadTimer_ns = -500e6
    def __hke_RELEASED(self, event):
        self.pressedKey = None
    def __hke_SELECTIONESCAPED(self, event):
        self.pressedKey = None
        self.textElement_SL_I.status = "DEFAULT"
        self.textElement_SL_I.caret.resetCaret()

    def show(self):
        self.textElement_SL.show()
    
    def hide(self):
        self.textElement_SL.hide()

    def moveTo(self, x = None, y = None):
        self.textElement_SL_I.moveTo(x = x, y = y)

    def changeSize(self, width = None, height = None):
        self.textElement_SL_I.changeSize(width = width, height = height)

    def setText(self, text, textStyle = None):
        self.textElement_SL.setText(text = text, textStyle = textStyle)
    
    def insertText(self, text, position = None, textStyle = None):
        self.textElement_SL.insertText(text = text, position = position, textStyle = textStyle)
    
    def deleteText(self, indexRange):
        self.textElement_SL.deleteText(indexRange = indexRange)
    
    def getText(self):
        return self.textElement_SL.text

    def editTextStyle(self, indexRange, style):
        self.textElement_SL.editTextStyle(indexRange = indexRange, style = style)
    
    def addTextStyle(self, textStyleName, textStyle):
        self.textElement_SL.addTextStyle(textStyleName = textStyleName, textStyle = textStyle)
    
    def changeActiveTextStyle(self, textStyle):
        self.textElement_SL.changeActiveTextStyle(textStyle = textStyle)

    def on_GUIThemeUpdate(self, **kwargs):
        self.textElement_SL_I.on_GUIThemeUpdate(**kwargs)
    
    def on_LanguageUpdate(self, **kwargs):
        self.textElement_SL_I.on_LanguageUpdate(**kwargs)

    def getTextLength(self):
        return self.textElement_SL.getTextLength()
    
    def getContentWidth(self):
        return self.textElement_SL.getContentWidth()
    
    def getContentHeight(self):
        return self.textElement_SL.getContentHeight()

    def isTouched(self, mouseX, mouseY):
        return self.textElement_SL_I.isTouched(mouseX, mouseY)

    def delete(self):
        self.textElement_SL_I.delete()

    def __readPressedKey(self):
        pk_symbol    = self.pressedKey['symbol']
        pk_modifiers = self.pressedKey['modifiers']

        if (pk_symbol in CHARTABLE_LOWER):
            #Character-Combined AUX ShortKeys
            #---SELECT ALL
            if ((pk_symbol == 97) and (pk_modifiers == MODIFIER_CTRL)): #CTRL + A
                self.textElement_SL_I.caret.move(len(self.textElement_SL.text), basePos = 0)
            #---COPY TO CLIPBOARD
            elif ((pk_symbol == 99) and (pk_modifiers & MODIFIER_CTRL) and not(pk_modifiers & MODIFIER_SHIFT)): #CTRL + C (Shift Except)
                self.__writeToClipBoard(self.textElement_SL.text[self.textElement_SL.layout.selection_start:self.textElement_SL.layout.selection_end])
            #---PASTE FROM CLIPBOARD
            elif ((pk_symbol == 118) and (pk_modifiers & MODIFIER_CTRL) and not(pk_modifiers & MODIFIER_SHIFT)): #CTRL + C (Shift Except)
                clipboardText = self.__getFromClipBoard()
                if (clipboardText is not None): self.__insertCharacter(clipboardText)

            #Else
            else:
                useUpper = (((pk_modifiers & MODIFIER_CAPSLOCK) and not(pk_modifiers & MODIFIER_SHIFT)) or (pk_modifiers & MODIFIER_SHIFT) and not(pk_modifiers & MODIFIER_CAPSLOCK))
                if (useUpper == True): character = CHARTABLE_UPPER.get(pk_symbol, None)
                else:                  character = CHARTABLE_LOWER.get(pk_symbol, None)
                if (character is not None): self.__insertCharacter(character)

        #Navigation
        elif (pk_symbol == 65361): self.__moveWithinText('L')
        elif (pk_symbol == 65363): self.__moveWithinText('R')

        #Text Edit
        #---[1]: BACKSPACE
        elif (pk_symbol == 65288): 
            self.__removeText()
        #---[2]: DELETE
        elif (pk_symbol == 65535):
            self.__removeText()
        #---[3]: INSERT
        elif (pk_symbol == 65379):
            pass
        #---[4]: HOME
        elif (pk_symbol == 65360): 
            self.textElement_SL_I.caret.move(0, basePos = 0)
        #---[5]: END
        elif (pk_symbol == 65367):
            self.textElement_SL_I.caret.move(len(self.textElement_SL.text), basePos = len(self.textElement_SL.text))

        #Command Key

    def __insertCharacter(self, text):
        if (self.textElement_SL.layout.selection_start != self.textElement_SL.layout.selection_end): self.__removeText(alone = False)
        self.textElement_SL.insertText(text, self.textElement_SL.layout.selection_start)
        newCaretPos = len(text)
        if (self.textElement_SL_I.caret.position_mobile is not None): newCaretPos += self.textElement_SL_I.caret.position_mobile
        self.textElement_SL_I.caret.move(newCaretPos, basePos = newCaretPos)
        if (self.textUpdateFunction is not None): self.textUpdateFunction(self)

    def __removeText(self, alone = True):
        caret  = self.textElement_SL_I.caret
        layout = self.textElement_SL.layout
        #Delete a single character from the current position
        if (caret.position_mobile == caret.position_base):
            if (caret.position_mobile <= 0): return
            idx = caret.position_mobile-1
            self.deleteText((idx, idx))
            caret.move(idx, basePos = idx)
        #Delete characters within the range
        else:
            r_beg, r_end = layout.selection_start, layout.selection_end-1
            self.deleteText((r_beg, r_end))
            caret.move(r_beg, basePos = r_beg)
        if ((alone == True) and (self.textUpdateFunction is not None)): self.textUpdateFunction(self)

    """
    self.pressedKey['modifiers'] == 0b00000: DEFAULT
    self.pressedKey['modifiers'] == 0b00001: SHIFT
    self.pressedKey['modifiers'] == 0b00010: CTRL
    self.pressedKey['modifiers'] == 0b00100: ALT
    self.pressedKey['modifiers'] == 0b01000: CAPS LOCK
    self.pressedKey['modifiers'] == 0b10000: NUM LOCK
    """
    def __moveWithinText(self, movDir):
        caret  = self.textElement_SL_I.caret
        layout = self.textElement_SL.layout
        tLen   = len(self.textElement_SL.text)
        #MOVE+SHIFT
        if (self.pressedKey['modifiers'] & MODIFIER_SHIFT):
            if (movDir == 'L'):
                if (0 < caret.position_mobile): caret.move(caret.position_mobile-1)
            elif (movDir == 'R'):
                if (caret.position_mobile < tLen): caret.move(caret.position_mobile+1)
        #MOVE
        else: 
            if (movDir == 'L'):
                if (layout.selection_start == layout.selection_end):
                    if (0 < caret.position_mobile): caret.move(caret.position_mobile-1, basePos = caret.position_mobile-1)
                else:                               caret.move(layout.selection_start,  basePos = layout.selection_start)
            elif (movDir == 'R'):
                if (layout.selection_start == layout.selection_end):
                    if (caret.position_mobile < tLen): caret.move(caret.position_mobile+1, basePos = caret.position_mobile+1)
                else:                                  caret.move(layout.selection_end,    basePos = layout.selection_end)
        
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
        if ((self.hidden == True) or (self.position_base is None)): return

        self.blinkTimer_ms += t_elapsed_ns / 1e6
        if (self.blinkTimer_ms < self.blinkInterval_ms): return

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
        previousPosition = self.position_mobile
        previousBase     = self.position_base
        mouseXCompensator, mouseYCompensator = self.__getMouseCompensators()

        self.position_mobile = position
        if (basePos is not None): self.position_base = basePos

        caretX_rel = self.layout.get_point_from_position(self.position_mobile)[0]
        if   (caretX_rel < self.layout.view_x):                     caretX = 0;                               viewMove = 'left'
        elif (self.layout.width < caretX_rel - self.layout.view_x): caretX = self.layout.width;               viewMove = 'right'
        else:                                                       caretX = caretX_rel - self.layout.view_x; viewMove = None
        self.caretShape.x  = caretX + self.layout.x - mouseXCompensator
        self.caretShape.x2 = self.caretShape.x

        if   (self.layout.anchor_y == 'bottom'): self.caretShape.y = self.layout.y - mouseYCompensator
        elif (self.layout.anchor_y == 'center'): self.caretShape.y = self.layout.y - mouseYCompensator + self.layout.height*0.5 - self.layout.content_height*0.5
        elif (self.layout.anchor_y == 'top'):    self.caretShape.y = self.layout.y - mouseYCompensator + self.layout.height     - self.layout.content_height
        self.caretShape.y2 = self.caretShape.y + self.layout.content_height

        if (self.hidden == False): self.caretShape.visible = True
        self.blinkTimer_ms = 0
        
        if ((previousPosition == self.position_mobile) and (previousBase == self.position_base)): return False

        self.__applyLayoutSelection(viewMove)

        return True

    def resetCaret(self):
        self.position_base   = None
        self.position_mobile = None
        self.caretShape.visible = False
        self.layout.selection_start = 0; self.layout.selection_end = 0

    def onMousePress(self, mouseX, mouseY):
        mouseXCompensator, mouseYCompensator = self.__getMouseCompensators()
        self.position_base   = self.layout.get_position_from_point(mouseX+mouseXCompensator, mouseY+mouseYCompensator)
        self.position_mobile = self.position_base

        self.caretShape.x  = self.layout.get_point_from_position(self.position_base)[0] + self.layout.x - mouseXCompensator - self.layout.view_x
        self.caretShape.x2 = self.caretShape.x

        if   (self.layout.anchor_y == 'bottom'): self.caretShape.y = self.layout.y - mouseYCompensator;               
        elif (self.layout.anchor_y == 'center'): self.caretShape.y = self.layout.y - mouseYCompensator + self.layout.height/2 - self.layout.content_height/2
        elif (self.layout.anchor_y == 'top'):    self.caretShape.y = self.layout.y - mouseYCompensator + self.layout.height - self.layout.content_height
        self.caretShape.y2 = self.caretShape.y + self.layout.content_height
        
        if (self.hidden == False): 
            self.caretShape.visible = True
            self.blinkTimer_ms      = 0

        self.initialViewX = self.layout.view_x

        self.__applyLayoutSelection()

    def onMouseDrag(self, mouseX, mouseY):
        previousPosition = self.position_mobile
        mouseXCompensator, mouseYCompensator = self.__getMouseCompensators()
        self.position_mobile = self.layout.get_position_from_point(mouseX+mouseXCompensator, mouseY+mouseYCompensator)

        caretX_rel = self.layout.get_point_from_position(self.position_mobile)[0]
        if   (caretX_rel < self.layout.view_x):                     caretX = 0;                               viewMove = 'left'
        elif (self.layout.width < caretX_rel - self.layout.view_x): caretX = self.layout.width;               viewMove = 'right'
        else:                                                       caretX = caretX_rel - self.layout.view_x; viewMove = None
        self.caretShape.x  = caretX + self.layout.x - mouseXCompensator
        self.caretShape.x2 = self.caretShape.x

        if   (self.layout.anchor_y == 'bottom'): self.caretShape.y = self.layout.y - mouseYCompensator;               
        elif (self.layout.anchor_y == 'center'): self.caretShape.y = self.layout.y - mouseYCompensator + self.layout.height/2 - self.layout.content_height/2
        elif (self.layout.anchor_y == 'top'):    self.caretShape.y = self.layout.y - mouseYCompensator + self.layout.height - self.layout.content_height
        self.caretShape.y2 = self.caretShape.y + self.layout.content_height
        
        if (self.hidden == False): 
            self.caretShape.visible = True
            self.blinkTimer_ms      = 0

        if (previousPosition == self.position_mobile): return False

        self.__applyLayoutSelection(viewMove)

        return True

    def __getMouseCompensators(self):
        if   (self.layout.anchor_x == 'left'):   mouseXCompensator = 0
        elif (self.layout.anchor_x == 'center'): mouseXCompensator = self.layout.content_width*0.5
        elif (self.layout.anchor_x == 'right'):  mouseXCompensator = self.layout.content_width
        if   (self.layout.anchor_y == 'bottom'): mouseYCompensator = 0                 
        elif (self.layout.anchor_y == 'center'): mouseYCompensator = self.layout.height*0.5
        elif (self.layout.anchor_y == 'top'):    mouseYCompensator = self.layout.height
        return (mouseXCompensator, mouseYCompensator)

    def __applyLayoutSelection(self, viewMove = None):
        if (self.position_base <= self.position_mobile): self.layout.selection_start = self.position_base;   self.layout.selection_end = self.position_mobile
        else:                                            self.layout.selection_start = self.position_mobile; self.layout.selection_end = self.position_base
        if   (viewMove == 'left'):  self.layout.view_x = self.layout.get_point_from_position(self.position_mobile)[0]
        elif (viewMove == 'right'): self.layout.view_x = self.layout.get_point_from_position(self.position_mobile)[0] - self.layout.width
#Text Object Caret End ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------       