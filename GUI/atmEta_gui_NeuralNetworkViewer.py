#ATM Modules
from GUI import atmEta_gui_HitBoxes, atmEta_gui_TextControl, atmEta_gui_AdvancedPygletGroups, atmEta_gui_Generals
import atmEta_Auxillaries
import atmEta_Analyzers
import atmEta_IPC
import atmEta_NeuralNetworks

#Python Modules
import pyglet
import time
import math
import random
import numpy
from datetime import datetime, timezone, tzinfo
import pprint
import termcolor

#Constants
_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT
_IPC_PRD_INVALIDADDRESS    = atmEta_IPC._PRD_INVALIDADDRESS
_IPC_FAR_INVALIDFUNCTIONID = atmEta_IPC._FAR_INVALIDFUNCTIONID

_GD_DISPLAYBOX_GOFFSET    = 50
_GD_DISPLAYBOX_MINWIDTH   = 4600
_GD_DISPLAYBOX_MINHEIGHT  = 3000
_GD_DISPLAYBOX_SBF_WIDTH  = 800
_GD_DISPLAYBOX_SBF_HEIGHT = 350

_GD_OBJECT_MINWIDTH  = _GD_DISPLAYBOX_MINWIDTH                                                       #4600
_GD_OBJECT_MINHEIGHT = _GD_DISPLAYBOX_MINHEIGHT + _GD_DISPLAYBOX_SBF_HEIGHT + _GD_DISPLAYBOX_GOFFSET #3000 + 350 + 50 = 2500

_GD_SETTINGSSUBPAGE_WIDTH     = 4250
_GD_SETTINGSSUBPAGE_MAXHEIGHT = 8500

_GD_DISPLAYBOX_MINMAGNITUDE = 1
_GD_DISPLAYBOX_MAXMAGNITUDE = 100

_GD_DISPLAYBOX_NODEPIXELSIZE    = 10
_GD_DISPLAYBOX_WEIGHTPIXELWIDTH = 1000

_GD_DISPLAYBOX_GUIDE_HORIZONTALTEXTHEIGHT = 120

_TIMEINTERVAL_MOUSEINTERPRETATION_NS = 10e6
_TIMEINTERVAL_POSTDRAGWAITTIME       = 500e6
_TIMEINTERVAL_POSTSCROLLWAITTIME     = 500e6
_TIMEINTERVAL_POSHIGHLIGHTUPDATE     = 10e6

_TIMELIMIT_DRAWQUEUE_NS       = 10e6
_TIMELIMIT_RCLCGPROCESSING_NS = 10e6

_GD_LOADINGGAUGEBAR_HEIGHT = 150

_MAXDRAWABLEWEIGHTSPERLAYER = 1000

#'neuralNetworkViewer' -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class neuralNetworkViewer:
    #Initialization -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __init__(self, **kwargs):
        #Default Graphics Parameters
        self.window = kwargs['windowInstance']
        self.scaler = kwargs['scaler']; self.batch = kwargs['batch']
        
        #Group Order
        if (True):
            groupOrder = kwargs.get('groupOrder', None)
            if (groupOrder == None):
                self.group_0 = kwargs['group_0']
                self.group_1 = kwargs['group_1']
                self.group_2 = kwargs['group_2']
                self.group_3 = kwargs['group_3']
                self.group_4 = kwargs['group_4']
                self.group_5 = kwargs['group_5']
                #Hovered Descriptor
                self.group_hd0 = kwargs['group_20']
                #For Settings Subpage
                self.group_ss0 = kwargs['group_21']
                self.group_ss1 = kwargs['group_22']
                self.group_ss2 = kwargs['group_23']
                self.group_ss3 = kwargs['group_24']
                self.groupOrder = self.group_0.order
                self.parentCameraGroup = self.group_0
            else:
                self.groupOrder = groupOrder
                self.group_0 = pyglet.graphics.Group(order = self.groupOrder)
                self.group_1 = pyglet.graphics.Group(order = self.groupOrder+1)
                self.group_2 = pyglet.graphics.Group(order = self.groupOrder+2)
                self.group_3 = pyglet.graphics.Group(order = self.groupOrder+3)
                self.group_4 = pyglet.graphics.Group(order = self.groupOrder+4)
                self.group_5 = pyglet.graphics.Group(order = self.groupOrder+5)
                #Hovered Descriptor
                self.group_hd0 = pyglet.graphics.Group(order = self.groupOrder+20)
                #For Settings Subpage
                self.group_ss_order = self.groupOrder+21
                self.parentCameraGroup = None

        #External Connections
        self.imageManager  = kwargs['imageManager']
        self.audioManager  = kwargs['audioManager']
        self.visualManager = kwargs['visualManager']
        self.currentGUITheme = self.visualManager.getGUITheme()
        self.ipcA = kwargs['ipcA']
        
        #Interal Basic Configurations
        self.name = kwargs.get('name', None)
        if (self.name == None): self.objectConfig_preset = None
        else:                   self.objectConfig_preset = kwargs['guioConfig'].get(self.name, None)
        self.xPos = kwargs.get('xPos', 0); self.yPos = kwargs.get('yPos', 0)
        self.width = kwargs.get('width', 0); self.height = kwargs.get('height', 0)
        self.style = kwargs.get('style', 'styleA')
        
        self.textStyle = kwargs.get('textStyle', 'default')
        self.effectiveTextStyle = self.visualManager.getTextStyle('neuralNetworkViewer_'+self.textStyle)
        for textStyleCode in self.effectiveTextStyle: self.effectiveTextStyle[textStyleCode]['font_size'] = 80*self.scaler

        #DisplayBox Dimension Standards & Interaction Control Variables
        self.hitBox = dict()
        self.hitBox_Object = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos, self.width, self.height)
        self.images = dict()
        self.frameSprites = dict()
        if (self.width  < _GD_OBJECT_MINWIDTH):  self.width  = _GD_OBJECT_MINWIDTH  
        if (self.height < _GD_OBJECT_MINHEIGHT): self.height = _GD_OBJECT_MINHEIGHT
        self.displayBox = {'MAIN': None, 'AUX': None, 'SBF': None}
        self.displayBox_graphics = dict()
        for displayBoxName in self.displayBox: self.displayBox_graphics[displayBoxName] = dict()
        self.__RCLCGReferences = list()

        #Kline Loading Display Elements
        if (True):
            self.images['DATALOADINGCOVER'] = self.imageManager.getImageByCode("neuralNetworkViewer_typeA_"+self.style+"_dataLoadingCover", self.width*self.scaler, self.height*self.scaler)
            self.frameSprites['DATALOADINGCOVER'] = pyglet.sprite.Sprite(x = self.xPos*self.scaler, y = self.yPos*self.scaler, img = self.images['DATALOADINGCOVER'][0], batch = self.batch, group = self.group_1)
            self.frameSprites['DATALOADINGCOVER'].visible = False
            self.dataLoadingGaugeBar = atmEta_gui_Generals.gaugeBar_typeA(windowInstance = self.window, batch = self.batch, scaler = self.scaler, imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager,
                                                                          xPos = self.xPos, yPos = self.yPos, width = 100, height = _GD_LOADINGGAUGEBAR_HEIGHT,
                                                                          style = 'styleA', align = 'horizontal', group_0 = self.group_2, group_1 = self.group_3, value = 0)
            self.dataLoadingTextBox_perc = atmEta_gui_Generals.textBox_typeA(windowInstance = self.window, batch = self.batch, scaler = self.scaler, imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager,
                                                                             xPos = self.xPos, yPos = self.yPos, width = 100, height = _GD_LOADINGGAUGEBAR_HEIGHT,
                                                                             style = None, group_0 = self.group_4, group_1 = self.group_5, text = '', fontSize = 60)
            self.dataLoadingTextBox = atmEta_gui_Generals.textBox_typeA(windowInstance = self.window, batch = self.batch, scaler = self.scaler, imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager,
                                                                        xPos = self.xPos, yPos = self.yPos, width = 100, height = 200,
                                                                        style = None, group_0 = self.group_2, group_1 = self.group_3, text = "", fontSize = 80)
            self.dataLoadingGaugeBar.hide()
            self.dataLoadingTextBox_perc.hide()
            self.dataLoadingTextBox.hide()

        #Mouse Control Variables
        self.mouse_lastHoveredSection  = None; self.mouse_lastSelectedSection = None
        self.mouse_Dragged  = False; self.mouse_DragDX   = dict(); self.mouse_DragDY   = dict(); self.mouse_lastDragged_ns  = 0
        self.mouse_Scrolled = False; self.mouse_ScrollDX = dict(); self.mouse_ScrollDY = dict(); self.mouse_lastScrolled_ns = 0
        self.mouse_Event_lastRead    = None
        self.mouse_Event_lastPressed = None
        self.mouse_Event_lastInterpreted_ns = 0
        
        #Kline & Analysis Control Variables
        self.neuralNetworkCode             = None
        self.neuralNetwork                 = None
        self.connectionsData               = None
        self.connectionsData_drawing       = None
        self.connectionsDataFetchRequestID = None
        self.connections_absMax_bias   = None
        self.connections_absMax_weight = None
        self.data_DrawQueue       = list()
        self.data_DrawableWeights = dict()
        #Settings Sub Page Setup
        if (True):
            self.settingsSubPage = dict()
            self.settingsSubPage_Current = 'MAIN'
            self.settingsSubPage_Opened = False
            self.settingsButtonStatus = 'DEFAULT'
            settingsSubPage_effectiveHeight = self.height-100
            if (_GD_SETTINGSSUBPAGE_MAXHEIGHT < settingsSubPage_effectiveHeight): settingsSubPage_effectiveHeight = _GD_SETTINGSSUBPAGE_MAXHEIGHT
            if (groupOrder == None):
                self.settingsSubPage = atmEta_gui_Generals.subPageBox_typeA(windowInstance = self.window, batch = self.batch, scaler = self.scaler, guioConfig = kwargs['guioConfig'], sysFunctions = kwargs['sysFunctions'], imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager, ipcA = self.ipcA,
                                                                            xPos = self.xPos+50, yPos = self.yPos+self.height-50-settingsSubPage_effectiveHeight, width = _GD_SETTINGSSUBPAGE_WIDTH, height = settingsSubPage_effectiveHeight, 
                                                                            useScrollBar_V = True, useScrollBar_H = False,
                                                                            group_0 = self.group_ss0, group_1 = self.group_ss1, group_2 = self.group_ss2, group_3 = self.group_ss3)
                self.settingsSubPage.hide()
            else:
                self.settingsSubPage = atmEta_gui_Generals.subPageBox_typeA(windowInstance = self.window, batch = self.batch, scaler = self.scaler, guioConfig = kwargs['guioConfig'], sysFunctions = kwargs['sysFunctions'], imageManager = self.imageManager, audioManager = self.audioManager, visualManager = self.visualManager, ipcA = self.ipcA,
                                                                            xPos = self.xPos+50, yPos = self.yPos+self.height-50-settingsSubPage_effectiveHeight, width = _GD_SETTINGSSUBPAGE_WIDTH, height = settingsSubPage_effectiveHeight, 
                                                                            useScrollBar_V = True, useScrollBar_H = False,
                                                                            groupOrder = self.group_ss_order)
                self.settingsSubPage.hide()
            self.__configureSettingsSubPageObjects()

        #<ViewRange>
        self.viewRangeWidth_H_max   = None
        self.viewRangeWidth_V_max   = None
        self.viewRangeComp          = None
        self.viewRange_H            = [None, None]
        self.viewRange_V            = [None, None]
        self.viewRangeMagnification = None

        self.posHighlight_hoveredPos       = (None, None, None, None)
        self.posHighlight_updatedPositions = None
        self.posHighlight_selectedPos      = None
        self.posHighlight_lastUpdated_ns   = 0

        #Object Configuration
        self.sysFunc_editGUIOConfig = kwargs['sysFunctions']['EDITGUIOCONFIG']
        self.objectConfig = dict()
        self.__initializeObjectConfig()
        if (self.name in kwargs['guioConfig']): self.objectConfig = kwargs['guioConfig'][self.name]
        else:                                   self.__initializeObjectConfig()
        self.__matchGUIOsToConfig()
        self.__configureDisplayBoxes(onInit = True)
        
        #Object Status
        self.status = "DEFAULT"
        self.hidden = False

        #Post-Initialization
        self.__setVRParams()
        self.frameSprites['DATALOADINGCOVER'].visible = False
        self.dataLoadingGaugeBar.hide()
        self.dataLoadingTextBox.hide()
        self.dataLoadingTextBox_perc.hide()
    #Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Object Configuration & GUIO Initialization ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __configureSettingsSubPageObjects(self):
        subPageViewSpaceWidth = 4000
        #<MAIN>
        if (True):
            yPos_beg = 20000
            #Title
            self.settingsSubPage.addGUIO("TITLE_MAIN", atmEta_gui_Generals.passiveGraphics_wrapperTypeB, {'groupOrder': 0, 'xPos': 0, 'yPos': yPos_beg, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:TITLE_VIEWERSETTINGS')})
            yPosPoint0 = yPos_beg-350
            self.settingsSubPage.addGUIO("LINECOLOR_TITLE",           atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:LINE'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPage.addGUIO("LINECOLOR_TEXT",            atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-350, 'width':  600, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:LINETARGET'), 'fontSize': 80})
            self.settingsSubPage.addGUIO("LINECOLOR_TARGETSELECTION", atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 2, 'xPos':  700, 'yPos': yPosPoint0-350, 'width': 1500, 'height': 250, 'style': 'styleA', 'name': 'LineSelectionBox', 'nDisplay': 5, 'fontSize': 80, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPage.addGUIO("LINECOLOR_LED",             atmEta_gui_Generals.LED_typeA,          {'groupOrder': 0, 'xPos': 2300, 'yPos': yPosPoint0-350, 'width':  950, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPage.addGUIO("LINECOLOR_APPLYCOLOR",      atmEta_gui_Generals.button_typeA,       {'groupOrder': 0, 'xPos': 3350, 'yPos': yPosPoint0-350, 'width':  650, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_CHARTDRAWER:APPLYCOLOR'), 'fontSize': 80, 'name': 'ApplyColor', 'releaseFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B')):
                self.settingsSubPage.addGUIO("LINECOLOR_{:s}_TEXT".format(componentType),   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-700-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                self.settingsSubPage.addGUIO("LINECOLOR_{:s}_SLIDER".format(componentType), atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': yPosPoint0-650-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': 'Color_{:s}'.format(componentType), 'valueUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPage.addGUIO("LINECOLOR_{:s}_VALUE".format(componentType),  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': yPosPoint0-700-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            yPosPoint1 = yPosPoint0-1400
            self.settingsSubPage.addGUIO("LINECOLOR_POSITIVE_TEXT",    atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350, 'width': 1100, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_NEURALNETWORKVIEWER:LINEPOSITIVE'), 'fontSize': 80})
            self.settingsSubPage.addGUIO("LINECOLOR_POSITIVE_COLOR",   atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 1200, 'yPos': yPosPoint1-350, 'width':  750, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPage.addGUIO("LINECOLOR_NEGATIVE_TEXT",    atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 2050, 'yPos': yPosPoint1-350, 'width': 1100, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_NEURALNETWORKVIEWER:LINENEGATIVE'), 'fontSize': 80})
            self.settingsSubPage.addGUIO("LINECOLOR_NEGATIVE_COLOR",   atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3250, 'yPos': yPosPoint1-350, 'width':  750, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPage.addGUIO("LINECOLOR_NEUTRAL_TEXT",     atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-700, 'width': 1100, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_NEURALNETWORKVIEWER:LINENEUTRAL'),  'fontSize': 80})
            self.settingsSubPage.addGUIO("LINECOLOR_NEUTRAL_COLOR",    atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 1200, 'yPos': yPosPoint1-700, 'width':  750, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPage.addGUIO("LINECOLOR_INPUTLAYER_TEXT",  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 2050, 'yPos': yPosPoint1-700, 'width': 1100, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_NEURALNETWORKVIEWER:INPUTLAYER'),   'fontSize': 80})
            self.settingsSubPage.addGUIO("LINECOLOR_INPUTLAYER_COLOR", atmEta_gui_Generals.LED_typeA,     {'groupOrder': 0, 'xPos': 3250, 'yPos': yPosPoint1-700, 'width':  750, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPage.addGUIO("LINEWIDTH_TEXT",      atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-1050, 'width': 2900, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_NEURALNETWORKVIEWER:LINEWIDTH'), 'fontSize': 80})
            self.settingsSubPage.addGUIO("LINEWIDTH_TEXTINPUT", atmEta_gui_Generals.textInputBox_typeA, {'groupOrder': 0, 'xPos': 3000, 'yPos': yPosPoint1-1050, 'width': 1000, 'height': 250, 'style': 'styleA', 'name': 'WidthTextInputBox', 'text': "", 'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPage.addGUIO("APPLYNEWSETTINGS",  atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1-1400, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'ApplySettings',   'releaseFunction': self.__onSettingsContentUpdate})
            self.settingsSubPage.addGUIO("SAVECONFIGURATION", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1-1750, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:SAVECONFIG'),    'fontSize': 80, 'name': 'SAVECONFIG', 'releaseFunction': self.__onSettingsContentUpdate})
            #GUIO Setup
            _targetList = dict()
            _targetList['POSITIVE']   = {'text': self.visualManager.getTextPack('GUIO_NEURALNETWORKVIEWER:LINEPOSITIVE')}
            _targetList['NEGATIVE']   = {'text': self.visualManager.getTextPack('GUIO_NEURALNETWORKVIEWER:LINENEGATIVE')}
            _targetList['NEUTRAL']    = {'text': self.visualManager.getTextPack('GUIO_NEURALNETWORKVIEWER:LINENEUTRAL')}
            _targetList['INPUTLAYER'] = {'text': self.visualManager.getTextPack('GUIO_NEURALNETWORKVIEWER:INPUTLAYER')}
            self.settingsSubPage.GUIOs["LINECOLOR_TARGETSELECTION"].setSelectionList(selectionList = _targetList, displayTargets = 'all')

    def __initializeObjectConfig(self):
        self.objectConfig = dict()
        self.objectConfig['LINE_Width'] = 1
        self.objectConfig['LINE_POSITIVE_ColorR%DARK']    =random.randint(64,255); self.objectConfig['LINE_POSITIVE_ColorG%DARK']    =random.randint(64,255); self.objectConfig['LINE_POSITIVE_ColorB%DARK']    =random.randint(64, 255)
        self.objectConfig['LINE_POSITIVE_ColorR%LIGHT']   =random.randint(64,255); self.objectConfig['LINE_POSITIVE_ColorG%LIGHT']   =random.randint(64,255); self.objectConfig['LINE_POSITIVE_ColorB%LIGHT']   =random.randint(64, 255)
        self.objectConfig['LINE_NEGATIVE_ColorR%DARK']    =random.randint(64,255); self.objectConfig['LINE_NEGATIVE_ColorG%DARK']    =random.randint(64,255); self.objectConfig['LINE_NEGATIVE_ColorB%DARK']    =random.randint(64, 255)
        self.objectConfig['LINE_NEGATIVE_ColorR%LIGHT']   =random.randint(64,255); self.objectConfig['LINE_NEGATIVE_ColorG%LIGHT']   =random.randint(64,255); self.objectConfig['LINE_NEGATIVE_ColorB%LIGHT']   =random.randint(64, 255)
        self.objectConfig['LINE_NEUTRAL_ColorR%DARK']     =random.randint(64,255); self.objectConfig['LINE_NEUTRAL_ColorG%DARK']     =random.randint(64,255); self.objectConfig['LINE_NEUTRAL_ColorB%DARK']     =random.randint(64, 255)
        self.objectConfig['LINE_NEUTRAL_ColorR%LIGHT']    =random.randint(64,255); self.objectConfig['LINE_NEUTRAL_ColorG%LIGHT']    =random.randint(64,255); self.objectConfig['LINE_NEUTRAL_ColorB%LIGHT']    =random.randint(64, 255)
        self.objectConfig['LINE_INPUTLAYER_ColorR%DARK']  =random.randint(64,255); self.objectConfig['LINE_INPUTLAYER_ColorG%DARK']  =random.randint(64,255); self.objectConfig['LINE_INPUTLAYER_ColorB%DARK']  =random.randint(64, 255)
        self.objectConfig['LINE_INPUTLAYER_ColorR%LIGHT'] =random.randint(64,255); self.objectConfig['LINE_INPUTLAYER_ColorG%LIGHT'] =random.randint(64,255); self.objectConfig['LINE_INPUTLAYER_ColorB%LIGHT'] =random.randint(64, 255)

    def __matchGUIOsToConfig(self):
        self.settingsSubPage.GUIOs["LINEWIDTH_TEXTINPUT"].updateText(str(self.objectConfig['LINE_Width']))
        self.settingsSubPage.GUIOs["LINECOLOR_POSITIVE_COLOR"].updateColor(self.objectConfig['LINE_POSITIVE_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                           self.objectConfig['LINE_POSITIVE_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                           self.objectConfig['LINE_POSITIVE_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                           255)
        self.settingsSubPage.GUIOs["LINECOLOR_NEGATIVE_COLOR"].updateColor(self.objectConfig['LINE_NEGATIVE_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                           self.objectConfig['LINE_NEGATIVE_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                           self.objectConfig['LINE_NEGATIVE_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                           255)
        self.settingsSubPage.GUIOs["LINECOLOR_NEUTRAL_COLOR"].updateColor(self.objectConfig['LINE_NEUTRAL_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                          self.objectConfig['LINE_NEUTRAL_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                          self.objectConfig['LINE_NEUTRAL_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                          255)
        self.settingsSubPage.GUIOs["LINECOLOR_INPUTLAYER_COLOR"].updateColor(self.objectConfig['LINE_INPUTLAYER_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                             self.objectConfig['LINE_INPUTLAYER_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                             self.objectConfig['LINE_INPUTLAYER_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                             255)
        self.settingsSubPage.GUIOs["LINECOLOR_TARGETSELECTION"].setSelected('POSITIVE')
        self.settingsSubPage.GUIOs["APPLYNEWSETTINGS"].deactivate()
        self.settingsSubPage.GUIOs["SAVECONFIGURATION"].deactivate()
    #Object Configuration & GUIO Initialization END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #DisplayBox Control ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __configureDisplayBoxes(self, onInit = False):
        #[1]: Determine DisplayBox Dimensions
        if (True):
            displayBox_MAIN = (self.xPos, 
                               self.yPos, 
                               self.width, 
                               self.height-_GD_DISPLAYBOX_GOFFSET-_GD_DISPLAYBOX_SBF_HEIGHT)
            displayBox_AUX = (self.xPos,
                              self.yPos+self.height-_GD_DISPLAYBOX_SBF_HEIGHT,
                              self.width-_GD_DISPLAYBOX_SBF_WIDTH-_GD_DISPLAYBOX_GOFFSET,
                              _GD_DISPLAYBOX_SBF_HEIGHT)
            displayBox_SBF = (self.xPos+self.width-_GD_DISPLAYBOX_SBF_WIDTH,
                              self.yPos+self.height-_GD_DISPLAYBOX_SBF_HEIGHT,
                              _GD_DISPLAYBOX_SBF_WIDTH,
                              _GD_DISPLAYBOX_SBF_HEIGHT)
            drawBox_MAIN = (displayBox_MAIN[0]+_GD_DISPLAYBOX_GOFFSET, displayBox_MAIN[1]+_GD_DISPLAYBOX_GOFFSET, displayBox_MAIN[2]-_GD_DISPLAYBOX_GOFFSET*2, displayBox_MAIN[3]-_GD_DISPLAYBOX_GOFFSET*2)
            self.displayBox['MAIN'] = displayBox_MAIN
            self.displayBox['AUX']  = displayBox_AUX
            self.displayBox['SBF']  = displayBox_SBF
            self.displayBox_graphics['MAIN']['DRAWBOX'] = drawBox_MAIN
        #[2]: Set DisplayBox Objects (HitBox, Images, FrameSprites, CamGroups, RCLCGs, etc.)
        if (True):
            if (onInit == True):
                #<MAIN>
                if (True):
                    displayBox = self.displayBox['MAIN']
                    drawBox    = self.displayBox_graphics['MAIN']['DRAWBOX']
                    #Generate Graphic Sprites and Hitboxes
                    self.hitBox['MAIN'] = atmEta_gui_HitBoxes.hitBox_Rectangular(drawBox[0], drawBox[1], drawBox[2], drawBox[3])
                    self.images['MAIN'] = self.imageManager.getImageByCode("neuralNetworkViewer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                    self.frameSprites['MAIN'] = pyglet.sprite.Sprite(x = displayBox[0]*self.scaler, y = displayBox[1]*self.scaler, img = self.images['MAIN'][0], batch = self.batch, group = self.group_0)
                    #Setup CamGroup and DisplaySpaceManager
                    self.displayBox_graphics['MAIN']['RCLCG'] = atmEta_gui_AdvancedPygletGroups.resolutionControlledLayeredCameraGroup(window = self.window, batch = self.batch, viewport_x = drawBox[0]*self.scaler, viewport_y = drawBox[1]*self.scaler, viewport_width = drawBox[2]*self.scaler, viewport_height = drawBox[3]*self.scaler, order = self.groupOrder+2, parentCameraGroup = self.parentCameraGroup, fsdResolution_x = 5, fsdResolution_y = 5)
                    #Add RCLCGs to the reference list
                    self.__RCLCGReferences.append(self.displayBox_graphics['MAIN']['RCLCG'])
                    #Description Texts
                    self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'] = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_hd0, text = "", 
                                                                                                                defaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                                                                xPos = drawBox[0], yPos = drawBox[1]+drawBox[3]-200, width = drawBox[2], height = 200, showElementBox = False, anchor = 'W')
                    self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'] = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_hd0, text = "", 
                                                                                                                defaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                                                                xPos = drawBox[0], yPos = drawBox[1]+drawBox[3]-400, width = drawBox[2], height = 200, showElementBox = False, anchor = 'W')
                    self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT3'] = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_hd0, text = "", 
                                                                                                                defaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                                                                xPos = drawBox[0], yPos = drawBox[1]+drawBox[3]-200, width = drawBox[2], height = 200, showElementBox = False, anchor = 'E')
                #<AUX>
                if (True):
                    displayBox = self.displayBox['AUX']
                    #Generate Graphic Sprites and Hitboxes
                    self.images['AUX'] = self.imageManager.getImageByCode("neuralNetworkViewer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                    self.frameSprites['AUX'] = pyglet.sprite.Sprite(x = displayBox[0]*self.scaler, y = displayBox[1]*self.scaler, img = self.images['AUX'][0], batch = self.batch, group = self.group_0)
                #<SBF>
                if (True):
                    _displayBox = self.displayBox['SBF']
                    self.hitBox['SBF'] = atmEta_gui_HitBoxes.hitBox_Rectangular(_displayBox[0], _displayBox[1], _displayBox[2], _displayBox[3])
                    self.images['SBF_DEFAULT'] = self.imageManager.getImageByCode("neuralNetworkViewer_typeA_"+self.style+"_displayBoxFrameInteractable_DEFAULT", _displayBox[2]*self.scaler, _displayBox[3]*self.scaler)
                    self.images['SBF_HOVERED'] = self.imageManager.getImageByCode("neuralNetworkViewer_typeA_"+self.style+"_displayBoxFrameInteractable_HOVERED", _displayBox[2]*self.scaler, _displayBox[3]*self.scaler)
                    self.images['SBF_PRESSED'] = self.imageManager.getImageByCode("neuralNetworkViewer_typeA_"+self.style+"_displayBoxFrameInteractable_PRESSED", _displayBox[2]*self.scaler, _displayBox[3]*self.scaler)
                    self.images['SBF_ICON'] = self.imageManager.getImage('settingsIcon_512x512.png', (round(_displayBox[3]*0.65*self.scaler), round(_displayBox[3]*0.65*self.scaler)))
                    self.frameSprites['SBF'] = pyglet.sprite.Sprite(x = _displayBox[0]*self.scaler, y = _displayBox[1]*self.scaler, img = self.images['SBF_DEFAULT'][0], batch = self.batch, group = self.group_0)
                    self.frameSprites['SBF_ICON'] = pyglet.sprite.Sprite(x = (_displayBox[0]+_displayBox[2]/2)*self.scaler-self.images['SBF_ICON'].width/2, 
                                                                                         y = (_displayBox[1]+_displayBox[3]/2)*self.scaler-self.images['SBF_ICON'].height/2, 
                                                                                         img = self.images['SBF'+'_ICON'], batch = self.batch, group = self.group_1)
                    iconColoring = self.visualManager.getFromColorTable('ICON_COLORING')
                    self.frameSprites['SBF_ICON'].color = (iconColoring[0], iconColoring[1], iconColoring[2]); self.frameSprites['SBF'+'_ICON'].opacity = iconColoring[3]
            else:
                #<MAIN>
                if (True):
                    displayBox = self.displayBox['MAIN']
                    drawBox    = self.displayBox_graphics['MAIN']['DRAWBOX']
                    #Reposition & Resize Graphics and Hitboxes
                    self.hitBox['MAIN'].reposition(xPos = drawBox[0], yPos = drawBox[1])
                    self.hitBox['MAIN'].resize(width = drawBox[2], height = drawBox[3])
                    self.images['MAIN'] = self.imageManager.getImageByCode("neuralNetworkViewer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                    self.frameSprites['MAIN'].position = (displayBox[0]*self.scaler, displayBox[1]*self.scaler, self.frameSprites['MAIN'].z)
                    self.frameSprites['MAIN'].image = self.images['MAIN'][0]
                    #Reposition & Resize CamGroups and RCLCGs
                    self.displayBox_graphics['MAIN']['RCLCG'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                    #Reposition & Resize Auxillary Objects
                    self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'].moveTo(x = drawBox[0], y = drawBox[1]+drawBox[3]-200)
                    self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'].changeSize(width = drawBox[2])
                    self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'].moveTo(x = drawBox[0], y = drawBox[1]+drawBox[3]-400)
                    self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'].changeSize(width = drawBox[2])
                    self.displayBox_graphics['MAIN']['POSHIGHLIGHT_HOVERED'].height  = drawBox[3]*self.scaler
                    self.displayBox_graphics['MAIN']['POSHIGHLIGHT_SELECTED'].height = drawBox[3]*self.scaler
                #<AUX>
                if (True):
                    displayBox = self.displayBox['AUX']
                    #Reposition & Resize Graphics
                    self.images['AUX'] = self.imageManager.getImageByCode("neuralNetworkViewer_typeA_"+self.style+"_displayBoxFrame", self.displayBox['AUX'][2]*self.scaler, self.displayBox['AUX'][3]*self.scaler)
                    self.frameSprites['AUX'].position = (self.displayBox['AUX'][0]*self.scaler, self.displayBox['AUX'][1]*self.scaler, self.frameSprites['AUX'].z)
                    self.frameSprites['AUX'].image = self.images['AUX'][0]
                    self.frameSprites['AUX'].visible = True
                #<SBF>
                if (True):
                    displayBox = self.displayBox['SBF']
                    self.hitBox['SBF'].reposition(xPos = displayBox[0], yPos = displayBox[1])
                    self.frameSprites['SBF'].position = (displayBox[0]*self.scaler, displayBox[1]*self.scaler, self.frameSprites['SBF'].z)
                    self.frameSprites['SBF_ICON'].position = ((displayBox[0]+displayBox[2]/2)*self.scaler-self.images['SBF_ICON'].width/2,
                                                              (displayBox[1]+displayBox[3]/2)*self.scaler-self.images['SBF_ICON'].height/2,
                                                              self.frameSprites['SBF'].z)
            self.mouse_DragDX['MAIN'] = 0; self.mouse_DragDY['MAIN'] = 0; self.mouse_ScrollDX['MAIN'] = 0; self.mouse_ScrollDY['MAIN'] = 0
            self.mouse_DragDX['AUX']  = 0; self.mouse_DragDY['AUX']  = 0; self.mouse_ScrollDX['AUX']  = 0; self.mouse_ScrollDY['AUX']  = 0
            self.mouse_DragDX['SBF']  = 0; self.mouse_DragDY['SBF']  = 0; self.mouse_ScrollDX['SBF']  = 0; self.mouse_ScrollDY['SBF']  = 0
        #[3]: Size and Position Data Loading Gauge Bar and Text
        if (True):
            self.dataLoadingGaugeBar.resize(width     = round(self.width*0.9), height = _GD_LOADINGGAUGEBAR_HEIGHT)
            self.dataLoadingTextBox_perc.resize(width = round(self.width*0.9), height = _GD_LOADINGGAUGEBAR_HEIGHT)
            self.dataLoadingTextBox.resize(width      = round(self.width*0.9), height = 200)
            self.dataLoadingGaugeBar.moveTo(x     = round(self.xPos+self.width*0.05), y = round(self.yPos+self.height/2-_GD_LOADINGGAUGEBAR_HEIGHT))
            self.dataLoadingTextBox_perc.moveTo(x = round(self.xPos+self.width*0.05), y = round(self.yPos+self.height/2-_GD_LOADINGGAUGEBAR_HEIGHT))
            self.dataLoadingTextBox.moveTo(x      = round(self.xPos+self.width*0.05), y = round(self.yPos+self.height/2))
    #DisplayBox Control END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Processings -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def process(self, t_elapsed_ns):
        mei_beg = time.perf_counter_ns()
        self.settingsSubPage.process(t_elapsed_ns)                                                                            #[1]: Subpage Processing
        self.__process_MouseEventInterpretation()                                                                             #[2]: Mouse Event Interpretation
        #self.__process_PosHighlightUpdate(mei_beg)                                                                            #[3]: PosHighlight Update
        if (self.connectionsDataFetchRequestID == None):
            waitPostDrag   = (mei_beg-self.mouse_lastDragged_ns  <= _TIMEINTERVAL_POSTDRAGWAITTIME)
            waitPostScroll = (mei_beg-self.mouse_lastScrolled_ns <= _TIMEINTERVAL_POSTSCROLLWAITTIME)
            if ((waitPostDrag == False) and (waitPostScroll == False)): processNext = not(self.__process_drawQueues(mei_beg)) #[5]: Draw Queues Processing
            else:                                                       processNext = True
            if (processNext == True): processNext = not(self.__process_RCLCGs(mei_beg))                                       #[6]: RCLCGs Processing
        return
        
    def __process_MouseEventInterpretation(self):
        if (_TIMEINTERVAL_MOUSEINTERPRETATION_NS <= time.perf_counter_ns() - self.mouse_Event_lastInterpreted_ns):
            #[1-1]: Mouse Drag Handling
            if (self.mouse_Dragged == True):
                for section in self.mouse_DragDX: #Iterating over 'self.mouseDragDX' or 'self.mouseDragDY' does not matter
                    #Drag Delta
                    drag_dx = self.mouse_DragDX[section]; drag_dy = self.mouse_DragDY[section]
                    #Drag Responses
                    if ((drag_dx != 0) or (drag_dy != 0)):
                        if (section == 'MAIN'): self.__editVRPosition(delta_drag_x = drag_dx, delta_drag_y = drag_dy)
                        #Delta Reset
                        self.mouse_DragDX[section] = 0; self.mouse_DragDY[section] = 0
                #Post-Interpretation
                self.mouseDragged = False
            #[1-2]: Mouse Scroll Handling
            if (self.mouse_Scrolled == True):
                for section in self.mouse_ScrollDX: #Iterating over 'self.mouseScrollDX' or 'self.mouseScrollDY' does not matter
                    #Scroll Delta
                    scroll_dx = self.mouse_ScrollDX[section]; scroll_dy = self.mouse_ScrollDY[section]
                    #Scroll Responses
                    if ((scroll_dx != 0) or (scroll_dy != 0)):
                        if (section == 'SETTINGSFRAME'):
                            self.internalGUIOs_SETTINGS_viewRange[0] += scroll_dy*5
                            self.internalGUIOs_SETTINGS_viewRange[1] += scroll_dy*5
                            self.__onSettingsViewRangeUpdate(byScrollBar=False)
                        elif (section == 'MAIN'): 
                            self.__editVRMagFactor(delta_scroll = scroll_dy)
                            #self.__updatePosHighlight(self.mouse_Event_lastRead['x'], self.mouse_Event_lastRead['y'], self.mouse_lastHoveredSection, updateType = 0)
                        #Delta Reset
                        self.mouse_ScrollDX[section] = 0; self.mouse_ScrollDY[section] = 0
                self.mouse_Scrolled = False
            #[1-3]: Period Counter Reset
            self.mouse_Event_lastInterpreted_ns = time.perf_counter_ns()

    def __process_PosHighlightUpdate(self, mei_beg):
        if (self.posHighlight_updatedPositions != None) and (_TIMEINTERVAL_POSHIGHLIGHTUPDATE <= mei_beg - self.posHighlight_lastUpdated_ns): self.__onPosHighlightUpdate()

    def __process_drawQueues(self, mei_beg):
        while ((time.perf_counter_ns()-mei_beg < _TIMELIMIT_DRAWQUEUE_NS) and (0 < len(self.data_DrawQueue))): self.__dataDrawer_draw(targetAddress = self.data_DrawQueue.pop())
        return (0 < len(self.data_DrawQueue))

    def __process_RCLCGs(self, mei_beg):
        remainingProcTime = _TIMELIMIT_RCLCGPROCESSING_NS-(time.perf_counter_ns()-mei_beg)
        nRefedRCLCGs = len(self.__RCLCGReferences)
        #If there is no more shapes to draw in the current focus, draw shapes outside the focus
        RCLCGRefIndex = 0
        while ((RCLCGRefIndex < nRefedRCLCGs) and (0 < remainingProcTime)):
            if (self.__RCLCGReferences[RCLCGRefIndex].processShapeGenerationQueue(remainingProcTime, currentFocusOnly = False) == True): return True #Will return True if timeout has occurred and there still exist more shapes to draw
            else:
                remainingProcTime = _TIMELIMIT_RCLCGPROCESSING_NS-(time.perf_counter_ns()-mei_beg)
                RCLCGRefIndex += 1
        #Return if there exist any more shapes to draw
        return False
    #Processings END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #User Interaction Control ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def handleMouseEvent(self, event):
        if ((self.connectionsDataFetchRequestID == None) and (self.hidden == False)):
            if (event['eType'] == "MOVED"):
                #Find hovering section
                hoveredSection = None
                if (self.settingsSubPage_Opened == True) and (self.settingsSubPage.isTouched(event['x'], event['y']) == True): hoveredSection = 'SETTINGSSUBPAGE'
                else:
                    for displayBoxName in self.hitBox:
                        if (self.hitBox[displayBoxName].isTouched(event['x'], event['y']) == True): hoveredSection = displayBoxName; break
                #Hovering Section Has Not Changed
                if (hoveredSection == self.mouse_lastHoveredSection):
                    if (hoveredSection == 'SETTINGSSUBPAGE'): self.settingsSubPage.handleMouseEvent(event)
                #Hovering Section Changed
                else:
                    #[1]: New Hovered Section is 'SBF'
                    if (hoveredSection == 'SBF'):
                        self.frameSprites['SBF'].image = self.images['SBF_HOVERED'][0]
                        self.settingsButtonStatus = 'HOVERED'
                    #  or New Hovered Section is 'SETTINGSSUBPAGE'
                    elif (hoveredSection == 'SETTINGSSUBPAGE'):
                        self.settingsSubPage.handleMouseEvent({'eType': "HOVERENTERED", 'x': event['x'], 'y': event['y']})
                    #  or New Hovered Section is None
                    elif (hoveredSection == None):
                        self.__updatePosHighlight(event['x'], event['y'], hoveredSection, updateType = 1)
                    #[2]: Last Hovered Section was 'SBF'
                    if (self.mouse_lastHoveredSection == 'SBF'):
                        self.frameSprites['SBF'].image = self.images['SBF_DEFAULT'][0]
                        self.settingsButtonStatus = 'DEFAULT'
                    #  or Last Hovered Section was 'SETTINGSSUBPAGE'
                    elif (self.mouse_lastHoveredSection == 'SETTINGSSUBPAGE'):
                        self.settingsSubPage.handleMouseEvent({'eType': "HOVERESCAPED", 'x': event['x'], 'y': event['y']})
                #POSHIGHLIGHT Control
                if ((hoveredSection != None) and (hoveredSection == 'MAIN')): self.__updatePosHighlight(event['x'], event['y'], hoveredSection, updateType = 0)
                #Recording
                self.mouse_lastHoveredSection = hoveredSection
        
            elif (event['eType'] == "PRESSED"):
                if (self.mouse_lastHoveredSection != self.mouse_lastSelectedSection):
                    if (self.mouse_lastSelectedSection == 'SETTINGSSUBPAGE'): self.settingsSubPage.handleMouseEvent({'eType': "SELECTIONESCAPED", 'x': event['x'], 'y': event['y'], 'button': event['button'], 'modifiers': event['modifiers']})
                if (self.mouse_lastHoveredSection == 'SBF'):
                    self.frameSprites['SBF'].image = self.images['SBF_PRESSED'][0]
                    self.settingsButtonStatus = 'PRESSED'
                elif (self.mouse_lastHoveredSection == 'SETTINGSSUBPAGE'): self.settingsSubPage.handleMouseEvent(event)
                #POSHIGHLIGHT Control
                if ((self.mouse_lastHoveredSection != None) and (self.mouse_lastHoveredSection == 'MAIN')): self.__updatePosHighlight(event['x'], event['y'], self.mouse_lastHoveredSection, updateType = 1)
                #Recording
                self.mouse_lastSelectedSection = self.mouse_lastHoveredSection
                self.mouse_Event_lastPressed = event
        
            elif (event['eType'] == "RELEASED"):
                if (self.mouse_lastSelectedSection == self.mouse_lastHoveredSection):
                    if (self.mouse_lastHoveredSection == 'SBF'):
                        self.frameSprites['SBF'].image = self.images['SBF_HOVERED'][0]
                        self.settingsButtonStatus = 'HOVERED'
                        self.__onSettingsButtonClick()
                    elif (self.mouse_lastHoveredSection == 'SETTINGSSUBPAGE'): self.settingsSubPage.handleMouseEvent(event)
                else:
                    if (self.mouse_lastSelectedSection == 'SBF'):
                        self.frameSprites['SBF'].image = self.images['SBF_DEFAULT'][0]
                        self.settingsButtonStatus = 'DEFAULT'
                    elif (self.mouse_lastSelectedSection == 'SETTINGSSUBPAGE'): self.settingsSubPage.handleMouseEvent({'eType': "HOVERESCAPED", 'x': event['x'], 'y': event['y']})
                    if (self.mouse_lastHoveredSection == 'SBF'):
                        self.frameSprites['SBF'].image = self.images['SBF_HOVERED'][0]
                        self.settingsButtonStatus = 'HOVERED'
                    elif (self.mouse_lastHoveredSection == 'SETTINGSSUBPAGE'): self.settingsSubPage.handleMouseEvent({'eType': "HOVEREENTERED", 'x': event['x'], 'y': event['y']})
                #POSHIGHLIGHT Control
                if ((self.mouse_lastHoveredSection != None) and (self.mouse_lastHoveredSection == 'MAIN')): 
                    self.__updatePosHighlight(event['x'], event['y'], self.mouse_lastHoveredSection, updateType = 0)
                    if ((self.mouse_Event_lastPressed != None) and (self.mouse_Event_lastPressed['x'] == event['x']) and (self.mouse_Event_lastPressed['y'] == event['y'])):
                        #LEFT MOUSE BUTTON -> POSSELECTION Update
                        if (event['button'] == 1): self.__updatePosSelection(updateType = 0)   
                        #RIGHT MOUSE BUTTON -> None
                        elif (event['button'] == 4): pass

            elif (event['eType'] == "DRAGGED"):
                #Find hovering section
                hoveredSection = None
                if (self.settingsSubPage_Opened == True) and (self.settingsSubPage.isTouched(event['x'], event['y']) == True): hoveredSection = 'SETTINGSSUBPAGE'
                else:
                    for displayBoxName in self.hitBox:
                        if (self.hitBox[displayBoxName].isTouched(event['x'], event['y']) == True): hoveredSection = displayBoxName; break
                #Drag Source
                if (self.mouse_lastSelectedSection == 'SETTINGSSUBPAGE'): self.settingsSubPage.handleMouseEvent(event)
                elif (self.mouse_lastSelectedSection != None) and (self.mouse_lastSelectedSection != 'SBF'): 
                    self.mouse_DragDX[self.mouse_lastSelectedSection] += event['dx']
                    self.mouse_DragDY[self.mouse_lastSelectedSection] += event['dy']
                    self.mouse_Dragged = True
                    self.mouse_lastDragged_ns = time.perf_counter_ns()
                self.mouse_lastHoveredSection = hoveredSection
        
            elif (event['eType'] == "SCROLLED"):
                if (self.mouse_lastSelectedSection == 'SETTINGSSUBPAGE'): self.settingsSubPage.handleMouseEvent(event)
                elif (self.mouse_lastSelectedSection != None):
                    self.mouse_ScrollDX[self.mouse_lastSelectedSection] += event['scroll_x']
                    self.mouse_ScrollDY[self.mouse_lastSelectedSection] += event['scroll_y']
                    self.mouse_Scrolled = True
                    self.mouse_lastScrolled_ns = time.perf_counter_ns()
        
            elif (event['eType'] == "SELECTIONESCAPED"):
                if (self.mouse_lastSelectedSection == 'SETTINGSSUBPAGE'): self.settingsSubPage.handleMouseEvent(event)
                self.mouse_lastSelectedSection = None
        
            elif (event['eType'] == "HOVERESCAPED"):
                self.__updatePosHighlight(event['x'], event['y'], None, updateType = 1)
                self.mouse_lastSelectedSection = None

        self.mouse_Event_lastRead = event

    def __updatePosHighlight(self, mouseX, mouseY, hoveredSection, updateType):
        if (updateType == 0):
            try:
                #Get Position Within the DrawBox
                xWithinDrawBox = mouseX-self.displayBox_graphics['MAINGRID_X']['DRAWBOX'][0]
                yWithinDrawBox = mouseY-self.displayBox_graphics['MAIN']['DRAWBOX'][1]
                #Compute Abstract Space Position
                xValHovered = xWithinDrawBox/self.displayBox_graphics['MAINGRID_X']['DRAWBOX'][2]*(self.horizontalViewRange[1]-self.horizontalViewRange[0])+self.horizontalViewRange[0]
                yValHovered = yWithinDrawBox/self.displayBox_graphics['MAIN']['DRAWBOX'][3]*(self.verticalViewRange[1]-self.verticalViewRange[0])+self.verticalViewRange[0]
                #Get Timestamp Interval Position
                tsIntervalHovered_0 = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = xValHovered, mrktReg = None, nTicks = 0)

                #If there exist no previous hoveredPosition
                if (self.posHighlight_hoveredPos[2] == None): 
                    self.posHighlight_updatedPositions = [True, True]
                    self.posHighlight_hoveredPos = (tsIntervalHovered_0, yValHovered, hoveredSection, None)
                #If there exist a previous hoveredPoisiton
                else:
                    self.posHighlight_updatedPositions = [False, False]
                    if (self.posHighlight_hoveredPos[0] != tsIntervalHovered_0): self.posHighlight_updatedPositions[0] = True
                    if (self.posHighlight_hoveredPos[1] != yValHovered):         self.posHighlight_updatedPositions[1] = True
                    if (self.posHighlight_hoveredPos[2] != hoveredSection): self.posHighlight_hoveredPos = (tsIntervalHovered_0, yValHovered, hoveredSection, self.posHighlight_hoveredPos[2])
                    else:                                                   self.posHighlight_hoveredPos = (tsIntervalHovered_0, yValHovered, hoveredSection, hoveredSection)
            except:
                self.posHighlight_hoveredPos = (None, None, None, self.posHighlight_hoveredPos[2])
                self.posHighlight_updatedPositions = [True, True]

        elif (updateType == 1):
            if (self.posHighlight_hoveredPos[2] != None):
                self.posHighlight_hoveredPos = (None, None, None, self.posHighlight_hoveredPos[2])
                self.posHighlight_updatedPositions = [True, True]

    def __onPosHighlightUpdate(self):
        #Horizontal Elements Update
        if (self.posHighlight_updatedPositions[0] == True):
            if (self.posHighlight_hoveredPos[2] == None): 
                self.displayBox_graphics['MAIN']['POSHIGHLIGHT_HOVERED'].visible = False
                self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'].hide()
            else:
                #Visibility Control
                if (self.displayBox_graphics['MAIN']['POSHIGHLIGHT_HOVERED'].visible == False): self.displayBox_graphics['MAIN']['POSHIGHLIGHT_HOVERED'].visible = True
                if (self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'].isHidden() == True): self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'].show()
                for displayBoxName in self.displayBox_graphics_visibleSIViewers:
                    if (self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_HOVERED'].visible == False): self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_HOVERED'].visible = True
                    if (self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].isHidden() == True): self.displayBox_graphics[displayBoxName]['DESCRIPTIONTEXT1'].show()
                #Update Highligter Graphics
                ts_rightEnd = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = self.posHighlight_hoveredPos[0], mrktReg = None, nTicks = 1)
                pixelPerTS = self.displayBox_graphics['MAINGRID_X']['DRAWBOX'][2]*self.scaler / (self.horizontalViewRange[1]-self.horizontalViewRange[0])
                highlightShape_x     = round((self.posHighlight_hoveredPos[0]-self.verticalGrid_intervals[0])*pixelPerTS, 1)
                highlightShape_width = round((ts_rightEnd-self.posHighlight_hoveredPos[0])*pixelPerTS,                    1)
                self.displayBox_graphics['MAIN']['POSHIGHLIGHT_HOVERED'].x     = highlightShape_x
                self.displayBox_graphics['MAIN']['POSHIGHLIGHT_HOVERED'].width = highlightShape_width
                if (self.displayBox_graphics['MAIN']['POSHIGHLIGHT_HOVERED'].visible == False): self.displayBox_graphics['MAIN']['POSHIGHLIGHT_HOVERED'].visible = True
                for displayBoxName in self.displayBox_graphics_visibleSIViewers:
                    self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_HOVERED'].x     = highlightShape_x
                    self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_HOVERED'].width = highlightShape_width
                    if (self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_HOVERED'].visible == False): self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_HOVERED'].visible = True
                #Update Data Descriptor
                displayText_time = datetime.fromtimestamp(self.posHighlight_hoveredPos[0]+self.timezoneDelta, tz = timezone.utc).strftime(" %Y/%m/%d")
                self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'].setText(displayText_time, [((0, len(displayText_time)), 'DEFAULT')])

        #Vertcial Elements Update
        if (self.posHighlight_updatedPositions[1] == True):
            if (self.posHighlight_hoveredPos[2] == None):
                self.displayBox_graphics['MAIN']['HORIZONTALGUIDELINE'].visible = False
                self.displayBox_graphics['MAIN']['HORIZONTALGUIDETEXT'].hide()
            else:
                dBox_current  = self.posHighlight_hoveredPos[2]
                dBox_previous = self.posHighlight_hoveredPos[3]
                #Visibility Control
                if ((dBox_previous != None) and (dBox_previous != dBox_current)):
                    self.displayBox_graphics[dBox_previous]['HORIZONTALGUIDELINE'].visible = False
                    self.displayBox_graphics[dBox_previous]['HORIZONTALGUIDETEXT'].hide()
                else:
                    if (self.displayBox_graphics[dBox_current]['HORIZONTALGUIDELINE'].visible == False): self.displayBox_graphics[dBox_current]['HORIZONTALGUIDELINE'].visible = True
                    if (self.displayBox_graphics[dBox_current]['HORIZONTALGUIDETEXT'].isHidden() == True): self.displayBox_graphics[dBox_current]['HORIZONTALGUIDETEXT'].show()
                #Update Highligter Graphics
                pixelPerVal = self.displayBox_graphics[dBox_current]['DRAWBOX'][3]*self.scaler / (self.verticalViewRange[1]-self.verticalViewRange[0])
                try:    verticalHoverLine_y = round((self.posHighlight_hoveredPos[1]-self.horizontalGridIntervals[0])*pixelPerVal, 1)
                except: verticalHoverLine_y = round(self.posHighlight_hoveredPos[1]*pixelPerVal,                                   1)
                self.displayBox_graphics[dBox_current]['HORIZONTALGUIDELINE'].y  = verticalHoverLine_y
                self.displayBox_graphics[dBox_current]['HORIZONTALGUIDELINE'].y2 = verticalHoverLine_y
                #Update Vertical Value Text
                dFromCeiling = self.displayBox_graphics[dBox_current]['HORIZONTALGRID_CAMGROUP'].projection_y1-verticalHoverLine_y
                if (dFromCeiling < _GD_DISPLAYBOX_GUIDE_HORIZONTALTEXTHEIGHT*self.scaler): self.displayBox_graphics[dBox_current]['HORIZONTALGUIDETEXT'].moveTo(y = verticalHoverLine_y/self.scaler-_GD_DISPLAYBOX_GUIDE_HORIZONTALTEXTHEIGHT)
                else:                                                            self.displayBox_graphics[dBox_current]['HORIZONTALGUIDETEXT'].moveTo(y = verticalHoverLine_y/self.scaler)
                self.displayBox_graphics[dBox_current]['HORIZONTALGUIDETEXT'].setText(atmEta_Auxillaries.floatToString(number = self.posHighlight_hoveredPos[1], precision = self.verticalViewRange_precision))
        self.posHighlight_updatedPositions = None

    def __updatePosSelection(self, updateType):
        #By button press->release
        if (updateType == 0):
            if (self.posHighlight_hoveredPos[2] != None):
                if (self.posHighlight_hoveredPos[0] == self.posHighlight_selectedPos):
                    self.posHighlight_selectedPos = None
                    self.displayBox_graphics['MAIN']['POSHIGHLIGHT_SELECTED'].visible = False
                    for displayBoxName in self.displayBox_graphics_visibleSIViewers: self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_SELECTED'].visible = False
                else:
                    self.posHighlight_selectedPos = self.posHighlight_hoveredPos[0]
                    shape_xPos  = self.displayBox_graphics['MAIN']['POSHIGHLIGHT_HOVERED'].x
                    shape_width = self.displayBox_graphics['MAIN']['POSHIGHLIGHT_HOVERED'].width
                    self.displayBox_graphics['MAIN']['POSHIGHLIGHT_SELECTED'].x     = shape_xPos
                    self.displayBox_graphics['MAIN']['POSHIGHLIGHT_SELECTED'].width = shape_width
                    self.displayBox_graphics['MAIN']['POSHIGHLIGHT_SELECTED'].visible = True
                    for displayBoxName in self.displayBox_graphics_visibleSIViewers: 
                        self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_SELECTED'].x     = shape_xPos
                        self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_SELECTED'].width = shape_width
                        self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_SELECTED'].visible = True
                self.__onPosSelectionUpdate()
        #By HorizontalViewRange Update
        elif (updateType == 1):
            if (self.posHighlight_selectedPos != None):
                tsPosEnd = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = self.posHighlight_selectedPos, mrktReg = None, nTicks = 1)
                pixelPerTS = self.displayBox_graphics['MAINGRID_X']['DRAWBOX'][2]*self.scaler / (self.horizontalViewRange[1]-self.horizontalViewRange[0])
                shape_xPos  = round((self.posHighlight_selectedPos-self.verticalGrid_intervals[0])*pixelPerTS, 1)
                shape_width = round((tsPosEnd-self.posHighlight_selectedPos)*pixelPerTS,                       1)
                self.displayBox_graphics['MAIN']['POSHIGHLIGHT_SELECTED'].x     = shape_xPos
                self.displayBox_graphics['MAIN']['POSHIGHLIGHT_SELECTED'].width = shape_width
                for displayBoxName in self.displayBox_graphics_visibleSIViewers: 
                    self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_SELECTED'].x     = shape_xPos
                    self.displayBox_graphics[displayBoxName]['POSHIGHLIGHT_SELECTED'].width = shape_width

    def __onPosSelectionUpdate(self):
        pass

    def handleKeyEvent(self, event):
        if ((self.connectionsDataFetchRequestID == None) and (self.hidden == False)):
            if (self.mouse_lastSelectedSection == 'SETTINGSSUBPAGE'): self.settingsSubPage.handleKeyEvent(event)
    #User Interaction Control END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Basic Object Control -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def show(self):
        self.hidden = False
        for displayBoxName in self.frameSprites: self.frameSprites[displayBoxName].visible = True
        self.displayBox_graphics['MAIN']['RCLCG'].show()
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'].show()
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'].show()
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT3'].show()
        if (self.settingsSubPage_Opened == True): self.settingsSubPage.show()
        if (self.connectionsDataFetchRequestID != None):
            self.frameSprites['DATALOADINGCOVER'].visible = True
            self.dataLoadingGaugeBar.show()
            self.dataLoadingTextBox.show()
            self.dataLoadingTextBox_perc.show()
        else:
            self.frameSprites['DATALOADINGCOVER'].visible = False
            self.dataLoadingGaugeBar.hide()
            self.dataLoadingTextBox.hide()
            self.dataLoadingTextBox_perc.hide()

    def hide(self):
        self.hidden = True
        for displayBoxName in self.frameSprites: self.frameSprites[displayBoxName].visible = False
        self.displayBox_graphics['MAIN']['RCLCG'].hide()
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'].hide()
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'].hide()
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT3'].hide()
        self.settingsSubPage.hide()
        self.frameSprites['DATALOADINGCOVER'].visible = False
        self.dataLoadingGaugeBar.hide()
        self.dataLoadingTextBox.hide()
        self.dataLoadingTextBox_perc.hide()

    def isHidden(self): 
        return self.hidden
        
    def moveTo(self, x, y):
        dx = x - self.xPos; dy = y - self.yPos
        self.xPos = x; self.yPos = y
        for displayBoxName in self.displayBox:
            if (self.displayBox[displayBoxName] != None):
                self.displayBox[displayBoxName] = (self.displayBox[displayBoxName][0]+dx, self.displayBox[displayBoxName][1]+dy, self.displayBox[displayBoxName][2], self.displayBox[displayBoxName][3])
                if (displayBoxName == 'SBF'):
                    self.hitBox['SBF'].reposition(xPos = self.displayBox['SBF'][0], yPos = self.displayBox['SBF'][1])
                    self.frameSprites['SBF'].position = (self.displayBox['SBF'][0]*self.scaler, self.displayBox['SBF'][1]*self.scaler, self.frameSprites['SBF'].z)
                    self.frameSprites['SBF_ICON'].position = ((self.displayBox['SBF'][0]+self.displayBox['SBF'][2]/2)*self.scaler-self.images['SBF_ICON'].width/2,
                                                              (self.displayBox['SBF'][1]+self.displayBox['SBF'][3]/2)*self.scaler-self.images['SBF_ICON'].height/2,
                                                              self.frameSprites['SBF_ICON'].z)
                else:
                    self.hitBox[displayBoxName].reposition(xPos = self.displayBox[displayBoxName][0]+_GD_DISPLAYBOX_GOFFSET, yPos = self.displayBox[displayBoxName][1]+_GD_DISPLAYBOX_GOFFSET)
                    self.frameSprites[displayBoxName].position = (self.displayBox[displayBoxName][0]*self.scaler, self.displayBox[displayBoxName][1]*self.scaler, self.frameSprites[displayBoxName].z)
        for settingsSubPageName in self.settingsSubPages: self.settingsSubPages[settingsSubPageName].moveTo(x = self.xPos+50, y = self.yPos+50)
        self.hitBox_Object.reposition(xPos = self.xPos, yPos = self.yPos)

    def resize(self, width, height):
        self.width = width; self.height = height
        self.__setDisplayBoxDimensions()
        self.settingsSubPage.resize(width = _GD_SETTINGSSUBPAGE_WIDTH, height = self.height-100)
        self.hitBox_Object.resize(width = self.width, height = self.height)

    def isTouched(self, mouseX, mouseY):
        if (self.hidden == False): return self.hitBox_Object.isTouched(mouseX, mouseY)
        else: return False

    def setName(self, name): 
        self.name = name

    def getName(self): 
        return self.name

    def on_GUIThemeUpdate(self, **kwargs):
        #Bring in updated textStyle and colors
        self.currentGUITheme = self.visualManager.getGUITheme()

        newEffectiveTextStyle = self.visualManager.getTextStyle('neuralNetworkViewer_'+self.textStyle)
        for styleTarget in newEffectiveTextStyle: newEffectiveTextStyle[styleTarget]['font_size'] = self.effectiveTextStyle[styleTarget]['font_size']
        self.effectiveTextStyle = newEffectiveTextStyle

        #Object Image Update
        for displayBoxName in self.displayBox:
            if (self.displayBox[displayBoxName] != None):
                if (displayBoxName == 'SBF'):
                    self.images['SBF_DEFAULT'] = self.imageManager.getImageByLoadIndex(self.images['SBF_DEFAULT'][1])
                    self.images['SBF_HOVERED'] = self.imageManager.getImageByLoadIndex(self.images['SBF_HOVERED'][1])
                    self.images['SBF_PRESSED'] = self.imageManager.getImageByLoadIndex(self.images['SBF_PRESSED'][1])
                    iconColoring = self.visualManager.getFromColorTable('ICON_COLORING')
                    self.frameSprites[displayBoxName].image = self.images['SBF_'+self.settingsButtonStatus][0]
                    self.frameSprites['SBF_ICON'].color = (iconColoring[0], iconColoring[1], iconColoring[2]); self.frameSprites['SBF'+'_ICON'].opacity = iconColoring[3]
                else:
                    self.images[displayBoxName] = self.imageManager.getImageByLoadIndex(self.images[displayBoxName][1])
                    self.frameSprites[displayBoxName].image = self.images[displayBoxName][0]
                    
        #Grid and Guide Lines & Text Update
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'].on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle)
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'].on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle)
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT3'].on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle)
        #Data Loading GaugeBar Related
        self.images['DATALOADINGCOVER'] = self.imageManager.getImageByLoadIndex(self.images['DATALOADINGCOVER'][1])
        self.frameSprites['DATALOADINGCOVER'].image = self.images['DATALOADINGCOVER'][0]
        self.dataLoadingGaugeBar.on_GUIThemeUpdate(**kwargs)
        self.dataLoadingTextBox_perc.on_GUIThemeUpdate(**kwargs)
        self.dataLoadingTextBox.on_GUIThemeUpdate(**kwargs)

        #Update Settings Subpage
        self.settingsSubPage.on_GUIThemeUpdate(**kwargs)
        
        #Update Configuration Objects Color
        for _lType in ('POSITIVE', 'NEGATIVE', 'NEUTRAL', 'INPUTLAYER'):
            self.settingsSubPage.GUIOs["LINECOLOR_{:s}_COLOR".format(_lType)].updateColor(self.objectConfig['LINE_{:s}_ColorR%{:s}'.format(_lType, self.currentGUITheme)], 
                                                                                          self.objectConfig['LINE_{:s}_ColorG%{:s}'.format(_lType, self.currentGUITheme)], 
                                                                                          self.objectConfig['LINE_{:s}_ColorB%{:s}'.format(_lType, self.currentGUITheme)], 
                                                                                          255)

        #Draw Queue
        if (self.connectionsData_drawing != None):
            self.data_DrawQueue = list()
            for _layerAddress in self.connectionsData_drawing['Nodes']: 
                for _nodeIndex in self.connectionsData_drawing['Nodes'][_layerAddress]: self.data_DrawQueue.append(('Nodes', _layerAddress, _nodeIndex))
            for _layerConnectivity in self.connectionsData_drawing['Weights']:
                for _weightAddress in self.data_DrawableWeights[_layerConnectivity]: self.data_DrawQueue.append(('Weights', _layerConnectivity, _weightAddress))

    def on_LanguageUpdate(self, **kwargs):
        #Bring in updated textStyle
        newEffectiveTextStyle = self.visualManager.getTextStyle('neuralNetworkViewer_'+self.textStyle)
        for styleTarget in newEffectiveTextStyle: newEffectiveTextStyle[styleTarget]['font_size'] = self.effectiveTextStyle[styleTarget]['font_size']
        self.effectiveTextStyle = newEffectiveTextStyle
        
        #Grid and Guide Lines & Text Update
        for displayBoxName in self.displayBox:
            if (displayBoxName == 'MAIN'):
                self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'].on_LanguageUpdate(**kwargs)
                self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'].on_LanguageUpdate(**kwargs)
                self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT3'].on_LanguageUpdate(**kwargs)

        #Data Loading GaugeBar Related
        self.dataLoadingTextBox_perc.on_LanguageUpdate(**kwargs)
        self.dataLoadingTextBox.on_LanguageUpdate(**kwargs)

        #Update Settings Subpage
        self.settingsSubPage.on_LanguageUpdate(**kwargs)
    #Basic Object Control END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Configuration Update Control -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __onSettingsButtonClick(self):
        if (self.settingsSubPage_Opened == True): self.settingsSubPage.hide()
        else:                                     self.settingsSubPage.show()
        self.settingsSubPage_Opened = not(self.settingsSubPage_Opened)

    def __onSettingsContentUpdate(self, objectInstnace):
        guioName = objectInstnace.getName()
        guioName_split = guioName.split("_")
        activateSaveConfigButton = False
        setterType = guioName_split[0]
        if (setterType == 'SAVECONFIG'):
            self.sysFunc_editGUIOConfig(configName = self.name, targetContent = self.objectConfig.copy()); self.settingsSubPage.GUIOs["SAVECONFIGURATION"].deactivate()
        elif (setterType == 'LineSelectionBox'):
            lineSelected = self.settingsSubPage.GUIOs["LINECOLOR_TARGETSELECTION"].getSelected()
            color_r, color_g, color_b, color_a = self.settingsSubPage.GUIOs["LINECOLOR_{:s}_COLOR".format(lineSelected)].getColor()
            self.settingsSubPage.GUIOs['LINECOLOR_LED'].updateColor(color_r, color_g, color_b, 255)
            self.settingsSubPage.GUIOs["LINECOLOR_R_VALUE"].updateText(str(color_r))
            self.settingsSubPage.GUIOs["LINECOLOR_G_VALUE"].updateText(str(color_g))
            self.settingsSubPage.GUIOs["LINECOLOR_B_VALUE"].updateText(str(color_b))
            self.settingsSubPage.GUIOs['LINECOLOR_R_SLIDER'].setSliderValue(color_r/255*100)
            self.settingsSubPage.GUIOs['LINECOLOR_G_SLIDER'].setSliderValue(color_g/255*100)
            self.settingsSubPage.GUIOs['LINECOLOR_B_SLIDER'].setSliderValue(color_b/255*100)
            self.settingsSubPage.GUIOs['LINECOLOR_APPLYCOLOR'].deactivate()
        elif (setterType == 'Color'):
            contentType = guioName_split[1]
            self.settingsSubPage.GUIOs['LINECOLOR_LED'].updateColor(rValue = int(self.settingsSubPage.GUIOs['LINECOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                    gValue = int(self.settingsSubPage.GUIOs['LINECOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                    bValue = int(self.settingsSubPage.GUIOs['LINECOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                    aValue = 255)
            self.settingsSubPage.GUIOs["LINECOLOR_{:s}_VALUE".format(contentType)].updateText(str(int(self.settingsSubPage.GUIOs['LINECOLOR_{:s}_SLIDER'.format(contentType)].getSliderValue()*255/100)))
            self.settingsSubPage.GUIOs['LINECOLOR_APPLYCOLOR'].activate()
        elif (setterType == 'ApplyColor'):
            lineSelected = self.settingsSubPage.GUIOs["LINECOLOR_TARGETSELECTION"].getSelected()
            color_r = int(self.settingsSubPage.GUIOs['LINECOLOR_R_SLIDER'].getSliderValue()*255/100)
            color_g = int(self.settingsSubPage.GUIOs['LINECOLOR_G_SLIDER'].getSliderValue()*255/100)
            color_b = int(self.settingsSubPage.GUIOs['LINECOLOR_B_SLIDER'].getSliderValue()*255/100)
            self.settingsSubPage.GUIOs["LINECOLOR_{:s}_COLOR".format(lineSelected)].updateColor(color_r, color_g, color_b, 255)
            self.settingsSubPage.GUIOs['LINECOLOR_APPLYCOLOR'].deactivate()
            self.settingsSubPage.GUIOs['APPLYNEWSETTINGS'].activate()
        elif (setterType == 'WidthTextInputBox'):
            self.settingsSubPage.GUIOs['APPLYNEWSETTINGS'].activate()
        elif (setterType == 'ApplySettings'):
            updateTracker = False
            #Width
            width_previous = self.objectConfig['LINE_Width']
            reset = False
            try:
                width = int(self.settingsSubPage.GUIOs["LINEWIDTH_TEXTINPUT"].getText())
                if (0 < width): self.objectConfig['LINE_Width'] = width
                else: reset = False
            except: reset = True
            if (reset == True):
                self.objectConfig['LINE_Width'] = 1
                self.settingsSubPage.GUIOs["LINEWIDTH_TEXTINPUT"].updateText(str(self.objectConfig['LINE_Width']))
            if (width_previous != self.objectConfig['LINE_Width']): updateTracker = True
            #Color
            for _line in ('POSITIVE', 'NEGATIVE', 'NEUTRAL', 'INPUTLAYER'):
                color_previous = (self.objectConfig['LINE_{:s}_ColorR%{:s}'.format(_line, self.currentGUITheme)],
                                  self.objectConfig['LINE_{:s}_ColorG%{:s}'.format(_line, self.currentGUITheme)],
                                  self.objectConfig['LINE_{:s}_ColorB%{:s}'.format(_line, self.currentGUITheme)])
                color_r, color_g, color_b, color_a = self.settingsSubPage.GUIOs["LINECOLOR_{:s}_COLOR".format(_line)].getColor()
                self.objectConfig['LINE_{:s}_ColorR%{:s}'.format(_line, self.currentGUITheme)] = color_r
                self.objectConfig['LINE_{:s}_ColorG%{:s}'.format(_line, self.currentGUITheme)] = color_g
                self.objectConfig['LINE_{:s}_ColorB%{:s}'.format(_line, self.currentGUITheme)] = color_b
                if (color_previous != (color_r, color_g, color_b)): updateTracker = True
            #Queue Update
            if (updateTracker == True):
                #Remove previous graphics
                self.__dataDrawer_RemoveDrawings()
                #Update Draw Queue
                self.data_DrawQueue = list()
                if (self.connectionsData_drawing != None):
                    for _layerAddress in self.connectionsData_drawing['Nodes']: 
                        for _nodeIndex in self.connectionsData_drawing['Nodes'][_layerAddress]: self.data_DrawQueue.append(('Nodes', _layerAddress, _nodeIndex))
                    for _layerConnectivity in self.connectionsData_drawing['Weights']:
                            for _weightAddress in self.data_DrawableWeights[_layerConnectivity]: self.data_DrawQueue.append(('Weights', _layerConnectivity, _weightAddress))
            #Control Buttons Handling
            self.settingsSubPage.GUIOs['APPLYNEWSETTINGS'].deactivate()
            activateSaveConfigButton = True
        if ((activateSaveConfigButton == True) and (self.settingsSubPage.GUIOs["SAVECONFIGURATION"].deactivated == True)): self.settingsSubPage.GUIOs["SAVECONFIGURATION"].activate()
    #Configuration Update Control END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Data Drawing --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __dataDrawer_draw(self, targetAddress):
        try: self.__dataDrawer(targetAddress = targetAddress)
        except Exception as e: print(termcolor.colored("An unexpected error occured while attempting to draw {:s}\n *".format(str(targetAddress)), 'light_yellow'), termcolor.colored(e, 'light_yellow'))

    def __dataDrawer(self, targetAddress):
        _target = self.connectionsData_drawing[targetAddress[0]][targetAddress[1]][targetAddress[2]]
        if (targetAddress[0] == 'Nodes'):
            if (targetAddress[1] == 'i'): 
                _color = (self.objectConfig['LINE_INPUTLAYER_ColorR%{:s}'.format(self.currentGUITheme)], 
                          self.objectConfig['LINE_INPUTLAYER_ColorG%{:s}'.format(self.currentGUITheme)], 
                          self.objectConfig['LINE_INPUTLAYER_ColorB%{:s}'.format(self.currentGUITheme)], 
                          255)
            else:
                _color_neutral = (self.objectConfig['LINE_NEUTRAL_ColorR%{:s}'.format(self.currentGUITheme)], 
                                  self.objectConfig['LINE_NEUTRAL_ColorG%{:s}'.format(self.currentGUITheme)], 
                                  self.objectConfig['LINE_NEUTRAL_ColorB%{:s}'.format(self.currentGUITheme)], 
                                  255)
                if ((self.connections_absMax_bias == 0) or (_target[2] == 0)): _color = _color_neutral
                else:
                    _value_rel = _target[2]/self.connections_absMax_bias
                    _value_relAbs = abs(_value_rel)
                    if (_value_rel < 0): _color_base = (self.objectConfig['LINE_NEGATIVE_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                        self.objectConfig['LINE_NEGATIVE_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                        self.objectConfig['LINE_NEGATIVE_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                        255)
                    elif (0 < _value_rel): _color_base = (self.objectConfig['LINE_POSITIVE_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                          self.objectConfig['LINE_POSITIVE_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                          self.objectConfig['LINE_POSITIVE_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                          255)
                    _color_r_delta = _color_base[0]-_color_neutral[0]
                    _color_g_delta = _color_base[1]-_color_neutral[1]
                    _color_b_delta = _color_base[2]-_color_neutral[2]
                    _color = (int(_color_base[0]-_color_r_delta*_value_relAbs), 
                              int(_color_base[1]-_color_g_delta*_value_relAbs),
                              int(_color_base[2]-_color_b_delta*_value_relAbs), 
                              255)
            self.displayBox_graphics['MAIN']['RCLCG'].addShape_Rectangle(x = _target[0], y = _target[1], width = _GD_DISPLAYBOX_NODEPIXELSIZE, height = _GD_DISPLAYBOX_NODEPIXELSIZE, 
                                                                         color = _color, 
                                                                         shapeName = targetAddress[1]+"_"+targetAddress[2], shapeGroupName = 'NODES', layerNumber = 1)

        elif (targetAddress[0] == 'Weights'):
            _color_neutral = (self.objectConfig['LINE_NEUTRAL_ColorR%{:s}'.format(self.currentGUITheme)], 
                              self.objectConfig['LINE_NEUTRAL_ColorG%{:s}'.format(self.currentGUITheme)], 
                              self.objectConfig['LINE_NEUTRAL_ColorB%{:s}'.format(self.currentGUITheme)], 
                              255)
            if ((self.connections_absMax_weight == 0) or (_target[4] == 0)): _color = _color_neutral
            else:
                _value_rel = _target[4]/self.connections_absMax_weight
                _value_relAbs = abs(_value_rel)
                if (_value_rel < 0): _color_base = (self.objectConfig['LINE_NEGATIVE_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                    self.objectConfig['LINE_NEGATIVE_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                    self.objectConfig['LINE_NEGATIVE_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                    255)
                elif (0 < _value_rel): _color_base = (self.objectConfig['LINE_POSITIVE_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                      self.objectConfig['LINE_POSITIVE_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                      self.objectConfig['LINE_POSITIVE_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                      255)
                _color_r_delta = _color_base[0]-_color_neutral[0]
                _color_g_delta = _color_base[1]-_color_neutral[1]
                _color_b_delta = _color_base[2]-_color_neutral[2]
                _color = (int(_color_base[0]-_color_r_delta*_value_relAbs), 
                          int(_color_base[1]-_color_g_delta*_value_relAbs),
                          int(_color_base[2]-_color_b_delta*_value_relAbs), 
                          255)
            self.displayBox_graphics['MAIN']['RCLCG'].addShape_Line(x = _target[0], x2 = _target[1], y = _target[2], y2 = _target[3], 
                                                                    color = _color, width = self.objectConfig['LINE_Width']/4, 
                                                                    shapeName = targetAddress[1]+"_"+targetAddress[2], shapeGroupName = 'WEIGHTS', layerNumber = 0)

    def __dataDrawer_RemoveDrawings(self):
        self.displayBox_graphics['MAIN']['RCLCG'].clearAll()
    #Data Drawing End ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #View Control ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __setVRParams(self):
        _displayBox_MAIN = self.displayBox['MAIN']
        _hvRatio = (_displayBox_MAIN[2]/_displayBox_MAIN[3])
        if (self.neuralNetwork == None):
            self.viewRangeWidth_H_max   = 100
            self.viewRangeWidth_V_max   = round(self.viewRangeWidth_H_max/_hvRatio, 2)
            self.viewRange_H            = [0, self.viewRangeWidth_H_max]
            self.viewRange_V            = [0, self.viewRangeWidth_V_max]
            self.viewRangeMagnification = 100
        else:
            _nLayersTotal = len(self.neuralNetwork['hiddenLayers'])+2
            _NNodesMax    = max([self.neuralNetwork_nInputNodes, 1])
            for _hl in self.neuralNetwork['hiddenLayers']:
                if (_NNodesMax < _hl['size']): _NNodesMax = _hl['size']
            _vr_elements_maxH = _nLayersTotal*_GD_DISPLAYBOX_NODEPIXELSIZE+(_nLayersTotal+1)*_GD_DISPLAYBOX_WEIGHTPIXELWIDTH
            _vr_elements_maxV = (_NNodesMax*2+1)*_GD_DISPLAYBOX_NODEPIXELSIZE
            _hvRatio_elements = _vr_elements_maxH/_vr_elements_maxV
            if   (_hvRatio_elements < _hvRatio): self.viewRangeComp = ('H', round(_vr_elements_maxH*(_hvRatio/_hvRatio_elements-1), 2)); _vr_elements_maxH += self.viewRangeComp[1] #Horizontal element VR is relatively shorter
            elif (_hvRatio < _hvRatio_elements): self.viewRangeComp = ('V', round(_vr_elements_maxV*(_hvRatio_elements/_hvRatio-1), 2)); _vr_elements_maxV += self.viewRangeComp[1] #Vertical   element VR is relatively shorter
            self.viewRangeWidth_H_max   = round(_vr_elements_maxH, 2)
            self.viewRangeWidth_V_max   = round(_vr_elements_maxV, 2)
            self.viewRange_H            = [0, self.viewRangeWidth_H_max]
            self.viewRange_V            = [0, self.viewRangeWidth_V_max]
            self.viewRangeMagnification = 100
        self.__onVRUpdate()
    
    def __editVRPosition(self, delta_drag_x, delta_drag_y):
        _drawBox_MAIN = self.displayBox_graphics['MAIN']['DRAWBOX']
        _effectiveDelta_H = -delta_drag_x*(self.viewRange_H[1]-self.viewRange_H[0])/_drawBox_MAIN[2]
        _effectiveDelta_V = -delta_drag_y*(self.viewRange_V[1]-self.viewRange_V[0])/_drawBox_MAIN[3]
        _vr_H_new = [self.viewRange_H[0]+_effectiveDelta_H, self.viewRange_H[1]+_effectiveDelta_H]
        _vr_V_new = [self.viewRange_V[0]+_effectiveDelta_V, self.viewRange_V[1]+_effectiveDelta_V]
        _vrWidth  = _vr_H_new[1]-_vr_H_new[0]
        _vrHeight = _vr_V_new[1]-_vr_V_new[0]
        if (_vr_H_new[0] < 0):                         _vr_H_new = [0,                                  _vrWidth]
        if (self.viewRangeWidth_H_max < _vr_H_new[1]): _vr_H_new = [self.viewRangeWidth_H_max-_vrWidth, self.viewRangeWidth_H_max]
        if (_vr_V_new[0] < 0):                         _vr_V_new = [0,                                   _vrHeight]
        if (self.viewRangeWidth_V_max < _vr_V_new[1]): _vr_V_new = [self.viewRangeWidth_V_max-_vrHeight, self.viewRangeWidth_V_max]
        self.viewRange_H = [round(_vr_H_new[0], 2), round(_vr_H_new[1], 2)]
        self.viewRange_V = [round(_vr_V_new[0], 2), round(_vr_V_new[1], 2)]
        self.__onVRUpdate()

    def __editVRMagFactor(self, delta_scroll):
        _newMagFactor = self.viewRangeMagnification + delta_scroll
        #Rounding
        _newMagFactor = round(_newMagFactor, 1)
        if   (_newMagFactor < _GD_DISPLAYBOX_MINMAGNITUDE): _newMagFactor = _GD_DISPLAYBOX_MINMAGNITUDE
        elif (_GD_DISPLAYBOX_MAXMAGNITUDE < _newMagFactor): _newMagFactor = _GD_DISPLAYBOX_MAXMAGNITUDE
        #Variation Check and response
        if (_newMagFactor != self.viewRangeMagnification):
            self.viewRangeMagnification = _newMagFactor
            _vrCenter_H = (self.viewRange_H[1]-self.viewRange_H[0])/2+self.viewRange_H[0]
            _vrCenter_V = (self.viewRange_V[1]-self.viewRange_V[0])/2+self.viewRange_V[0]
            _vrWidth_H_new  = self.viewRangeWidth_H_max*self.viewRangeMagnification/100
            _vrHeight_V_new = self.viewRangeWidth_V_max*self.viewRangeMagnification/100
            _vr_H_new = [_vrCenter_H-_vrWidth_H_new /2, _vrCenter_H+_vrWidth_H_new /2]
            _vr_V_new = [_vrCenter_V-_vrHeight_V_new/2, _vrCenter_V+_vrHeight_V_new/2]
            if (_vr_H_new[0] < 0):                         _vr_H_new = [0,                                        _vrWidth_H_new]
            if (self.viewRangeWidth_H_max < _vr_H_new[1]): _vr_H_new = [self.viewRangeWidth_H_max-_vrWidth_H_new, self.viewRangeWidth_H_max]
            if (_vr_V_new[0] < 0):                         _vr_V_new = [0,                                         _vrHeight_V_new]
            if (self.viewRangeWidth_V_max < _vr_V_new[1]): _vr_V_new = [self.viewRangeWidth_V_max-_vrHeight_V_new, self.viewRangeWidth_V_max]
            self.viewRange_H = [round(_vr_H_new[0], 2), round(_vr_H_new[1], 2)]
            self.viewRange_V = [round(_vr_V_new[0], 2), round(_vr_V_new[1], 2)]
            self.__onVRUpdate()

    def __onVRUpdate(self):
        self.displayBox_graphics['MAIN']['RCLCG'].updateProjection(projection_x0 = self.viewRange_H[0], projection_x1 = self.viewRange_H[1], projection_y0 = self.viewRange_V[0], projection_y1 = self.viewRange_V[1])
    #View Control END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    


    #Targe Data -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def setTarget(self, neuralNetworkCode):
        if (neuralNetworkCode == None):
            self.neuralNetworkCode             = None
            self.neuralNetwork                 = None
            self.neuralNetwork_nInputNodes     = None
            self.connectionsData               = None
            self.connectionsData_drawing       = None
            self.connectionsDataFetchRequestID = None
            self.connections_absMax_bias   = None
            self.connections_absMax_weight = None
            self.frameSprites['DATALOADINGCOVER'].visible = False
            self.dataLoadingGaugeBar.hide()
            self.dataLoadingTextBox.hide()
            self.dataLoadingTextBox_perc.hide()
            self.data_DrawQueue       = list()
            self.data_DrawableWeights = dict()
        else:
            self.neuralNetworkCode             = neuralNetworkCode
            self.neuralNetwork                 = self.ipcA.getPRD(processName = 'NEURALNETWORKMANAGER', prdAddress = ('NEURALNETWORKS', self.neuralNetworkCode))
            self.neuralNetwork_nInputNodes     = self.neuralNetwork['nKlines']*6
            self.connectionsData               = None
            self.connectionsData_drawing       = None
            self.connectionsDataFetchRequestID = self.ipcA.sendFAR(targetProcess  = "NEURALNETWORKMANAGER",
                                                                   functionID     = 'getNeuralNetworkConnections',
                                                                   functionParams = {'neuralNetworkCode': self.neuralNetworkCode},
                                                                   farrHandler    = self.__onNeuralNetworkConnectionsDataRequestResponse_FARR)
            self.connections_absMax_bias   = None
            self.connections_absMax_weight = None
            self.frameSprites['DATALOADINGCOVER'].visible = True
            self.dataLoadingGaugeBar.show()
            self.dataLoadingTextBox.show()
            self.dataLoadingTextBox_perc.show()
            self.dataLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_NEURALNETWORKVIEWER:REQUESTINGCONNECTIONSDATA'))
            self.dataLoadingTextBox_perc.updateText("-")
            self.data_DrawQueue       = list()
            self.data_DrawableWeights = dict()
        self.__dataDrawer_RemoveDrawings()

    def __onNeuralNetworkConnectionsDataRequestResponse_FARR(self, responder, requestID, functionResult):
        if (responder == 'NEURALNETWORKMANAGER'):
            if (requestID == self.connectionsDataFetchRequestID):
                if (functionResult != None):
                    #Get results
                    _neuralNetworkCode = functionResult['neuralNetworkCode']
                    _nKlines           = functionResult['nKlines']
                    _hiddenLayers      = functionResult['hiddenLayers']
                    _outputLayer       = functionResult['outputLayer']
                    _connections       = functionResult['connections']
                    if (_neuralNetworkCode == self.neuralNetworkCode):
                        self.connectionsDataFetchRequestID = None
                        #Connections data localization & projection coordinate computations
                        self.connectionsData = _connections
                        self.__computeParameterExtremas()
                        #Data loading GUIOs
                        self.frameSprites['DATALOADINGCOVER'].visible = False
                        self.dataLoadingGaugeBar.hide()
                        self.dataLoadingTextBox.hide()
                        self.dataLoadingTextBox_perc.hide()
                        #VR Params Setup & Draw queue add
                        self.__setVRParams()
                        self.__computeConnectionsProjectionCoordinates()
                        self.__determineDrawableWeights()
                        self.data_DrawQueue = list()
                        for _layerAddress in self.connectionsData_drawing['Nodes']: 
                            for _nodeIndex in self.connectionsData_drawing['Nodes'][_layerAddress]: self.data_DrawQueue.append(('Nodes', _layerAddress, _nodeIndex))
                        for _layerConnectivity in self.connectionsData_drawing['Weights']:
                            for _weightAddress in self.data_DrawableWeights[_layerConnectivity]: self.data_DrawQueue.append(('Weights', _layerConnectivity, _weightAddress))
                    else: self.dataLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_NEURALNETWORKVIEWER:NEURALNETWORKCONNECTIONSDATAREQUESTFAILED'))
                else: self.dataLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_NEURALNETWORKVIEWER:NEURALNETWORKCONNECTIONSDATAREQUESTFAILED'))

    def __computeParameterExtremas(self):
        _absMax_bias   = 0
        _absMax_weight = 0
        for _connection in self.connectionsData:
            _type   = _connection[0]
            _absVal = abs(float(_connection[3]))
            if   ((_type == 'bias')   and (_absMax_bias  < _absVal)):  _absMax_bias   = _absVal
            elif ((_type == 'weight') and (_absMax_weight < _absVal)): _absMax_weight = _absVal
        self.connections_absMax_bias   = _absMax_bias
        self.connections_absMax_weight = _absMax_weight

    def __computeConnectionsProjectionCoordinates(self):
        #Find maximum number of nodes per layer and maximum elemental layer-wise view range
        _NNodesMax = max([self.neuralNetwork_nInputNodes, 1])
        for _hl in self.neuralNetwork['hiddenLayers']:
            if (_NNodesMax < _hl['size']): _NNodesMax = _hl['size']
        _vr_elements_maxV = (_NNodesMax*2+1)*_GD_DISPLAYBOX_NODEPIXELSIZE
        #Pre-compute layer projection height offsets
        _nNodes = {'i': self.neuralNetwork_nInputNodes, 'o': 1}
        for _lIndex, _hl in enumerate(self.neuralNetwork['hiddenLayers']): _nNodes[str(_lIndex)] = _hl['size']
        _layerProjectionHeightOffsets = dict()
        for _lAddress in _nNodes: _layerProjectionHeightOffsets[_lAddress] = round((_vr_elements_maxV-(_nNodes[_lAddress]*2+1)*_GD_DISPLAYBOX_NODEPIXELSIZE)/2, 2)
        #Number of hidden layers for reference
        _nHiddenLayers = len(self.neuralNetwork['hiddenLayers'])
        #Drawing data computations
        self.connectionsData_drawing = {'Nodes': {'i': dict(),
                                                  'o': dict()}, 
                                        'Weights': dict()}
        for _hlIndex in range (_nHiddenLayers):
            self.connectionsData_drawing['Nodes'][str(_hlIndex)] = dict()
            if (_hlIndex == 0): self.connectionsData_drawing['Weights']["i-{:d}".format(_hlIndex)]                = dict()
            else:               self.connectionsData_drawing['Weights']["{:d}-{:d}".format(_hlIndex-1, _hlIndex)] = dict()
        self.connectionsData_drawing['Weights']["{:d}-o".format(_nHiddenLayers-1)] = dict()
        #---Bias and weights
        for _connection in self.connectionsData:
            if (_connection[0] == 'bias'):
                _lAddress  = _connection[1]
                _biasIndex = _connection[2]
                #X Coord
                if (_lAddress == 'o'): _effectiveLayerIndex = _nHiddenLayers+1
                else:                  _effectiveLayerIndex = int(_lAddress)+1
                _xCoord = _effectiveLayerIndex*_GD_DISPLAYBOX_NODEPIXELSIZE+(_effectiveLayerIndex+1)*_GD_DISPLAYBOX_WEIGHTPIXELWIDTH
                if (self.viewRangeComp[0] == 'H'): _xCoord += self.viewRangeComp[1]/2
                #Y Coord
                _yCoord = (2*(_nNodes[_lAddress]-_biasIndex)-1)*_GD_DISPLAYBOX_NODEPIXELSIZE+_layerProjectionHeightOffsets[_lAddress]
                if (self.viewRangeComp[0] == 'V'): _yCoord += self.viewRangeComp[1]/2
                #Finally
                self.connectionsData_drawing['Nodes'][_lAddress][str(_biasIndex)] = (round(_xCoord, 2), round(_yCoord, 2), float(_connection[3]))
            elif (_connection[0] == 'weight'):
                _layerConnectivity = _connection[1]
                _weightAddress     = _connection[2]
                _layerIn, _layerOut = _layerConnectivity.split("-")
                #X Coord
                if (_layerIn == 'i'): _effectiveInputLayerIndex = 0
                else:                 _effectiveInputLayerIndex = int(_layerIn)+1
                _xCoord1 = (_effectiveInputLayerIndex+1)*(_GD_DISPLAYBOX_NODEPIXELSIZE+_GD_DISPLAYBOX_WEIGHTPIXELWIDTH)
                _xCoord2 = _xCoord1+_GD_DISPLAYBOX_WEIGHTPIXELWIDTH
                if (self.viewRangeComp[0] == 'H'): 
                    _xCoord1 += self.viewRangeComp[1]/2
                    _xCoord2 += self.viewRangeComp[1]/2
                #Y Coord
                _yCoord1 = (2*(_nNodes[_layerIn] -_weightAddress[1])-0.5)*_GD_DISPLAYBOX_NODEPIXELSIZE+_layerProjectionHeightOffsets[_layerIn]
                _yCoord2 = (2*(_nNodes[_layerOut]-_weightAddress[0])-0.5)*_GD_DISPLAYBOX_NODEPIXELSIZE+_layerProjectionHeightOffsets[_layerOut]
                if (self.viewRangeComp[0] == 'V'):
                    _yCoord1 += self.viewRangeComp[1]/2
                    _yCoord2 += self.viewRangeComp[1]/2
                #Finally
                self.connectionsData_drawing['Weights'][_layerConnectivity]["{:d},{:d}".format(_weightAddress[0], _weightAddress[1])] = (round(_xCoord1, 2), round(_xCoord2, 2), round(_yCoord1, 2), round(_yCoord2, 2), float(_connection[3]))
        #---Input nodes
        _xCoord_inputNodes = _GD_DISPLAYBOX_WEIGHTPIXELWIDTH
        if (self.viewRangeComp[0] == 'H'): _xCoord_inputNodes += self.viewRangeComp[1]/2
        for _nIndex in range (0, self.neuralNetwork_nInputNodes):
            _yCoord = (2*(_nNodes['i']-_nIndex)-1)*_GD_DISPLAYBOX_NODEPIXELSIZE+_layerProjectionHeightOffsets['i']
            if (self.viewRangeComp[0] == 'V'): _yCoord += self.viewRangeComp[1]/2
            self.connectionsData_drawing['Nodes']['i'][str(_nIndex)] = (round(_xCoord_inputNodes, 2), round(_yCoord, 2), None)

    def __determineDrawableWeights(self):
        self.data_DrawableWeights = dict()
        for _layerConnectivity in self.connectionsData_drawing['Weights']:
            _weights_thisLayer = self.connectionsData_drawing['Weights'][_layerConnectivity]
            _weights_forSort = [(_weightAddress, abs(_weights_thisLayer[_weightAddress][4])) for _weightAddress in _weights_thisLayer]
            _weights_forSort.sort(key = lambda x: x[1], reverse = True)
            self.data_DrawableWeights[_layerConnectivity] = [_weight[0] for _weight in _weights_forSort][:_MAXDRAWABLEWEIGHTSPERLAYER]
    #Kline Data END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def getGroupRequirement(): return 30
#'tradeLogViewer' END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

