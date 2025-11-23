#ATM Modules
from GUI import atmEta_gui_HitBoxes, atmEta_gui_TextControl, atmEta_gui_AdvancedPygletGroups, atmEta_gui_Generals
import atmEta_Auxillaries
import atmEta_Analyzers
import atmEta_IPC

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

KLINDEX_OPENTIME         =  0
KLINDEX_CLOSETIME        =  1
KLINDEX_OPENPRICE        =  2
KLINDEX_HIGHPRICE        =  3
KLINDEX_LOWPRICE         =  4
KLINDEX_CLOSEPRICE       =  5
KLINDEX_NTRADES          =  6
KLINDEX_VOLBASE          =  7
KLINDEX_VOLQUOTE         =  8
KLINDEX_VOLBASETAKERBUY  =  9
KLINDEX_VOLQUOTETAKERBUY = 10

_EXPECTEDTEMPORALWIDTHS = {0:       60, #  1m
                           1:      180, #  3m
                           2:      300, #  5m
                           3:      900, # 15m
                           4:     1800, # 30m
                           5:     3600, #  1h
                           6:     7200, #  2h
                           7:    14400, #  4h
                           8:    21600, #  6h
                           9:    28800, #  8h
                           10:   43200, # 12h
                           11:   86400, #  1d
                           12:  259200, #  3d
                           13:  604800, #  7d
                           14: 2592000} # 30d

_GD_DISPLAYBOX_GOFFSET              = 50
_GD_DISPLAYBOX_LEFTSECTION_MINWIDTH = 4600
_GD_DISPLAYBOX_RIGHTSECTION_WIDTH   = 800
_GD_DISPLAYBOX_AUXILLARYBAR_HEIGHT  = 350
_GD_DISPLAYBOX_SIVIEWER_HEIGHT      = 1200
_GD_DISPLAYBOX_MAIN_MINHEIGHT   = 3000
_GD_DISPLAYBOX_MAINGRIDX_HEIGHT = 350

_GD_OBJECT_MINWIDTH  = _GD_DISPLAYBOX_LEFTSECTION_MINWIDTH + _GD_DISPLAYBOX_RIGHTSECTION_WIDTH + _GD_DISPLAYBOX_GOFFSET #3000 + 800 + 50*3 = 3950
_GD_OBJECT_MINHEIGHT = _GD_DISPLAYBOX_MAIN_MINHEIGHT       + _GD_DISPLAYBOX_MAINGRIDX_HEIGHT   + _GD_DISPLAYBOX_GOFFSET #2000 + 350 + 50*3 = 2500

_GD_SETTINGSSUBPAGE_WIDTH     = 4250
_GD_SETTINGSSUBPAGE_MAXHEIGHT = 8500

_GD_DISPLAYBOX_MAIN_MINPIXELWIDTH    = 2
_GD_DISPLAYBOX_MAIN_MAXPIXELWIDTH    = 100
_GD_DISPLAYBOX_MAIN_HVR_MINMAGNITUDE = 1
_GD_DISPLAYBOX_MAIN_HVR_MAXMAGNITUDE = 100

_GD_DISPLAYBOX_HVR_BACKWARDBUFFERFACTOR = 1
_GD_DISPLAYBOX_HVR_FORWARDBUFFERFACTOR  = 1

_GD_DISPLAYBOX_VVR_MAGNITUDE_MIN = 10
_GD_DISPLAYBOX_VVR_MAGNITUDE_MAX = 100

_GD_DISPLAYBOX_GRID_VERTICALLINEPIXELINTERVAL = 150
_GD_DISPLAYBOX_GRID_VERTICALTEXTWIDTH         = 500
_GD_DISPLAYBOX_GRID_VERTICALTEXTHEIGHT        = 120

_GD_DISPLAYBOX_GRID_HORIZONTALLINEPIXELINTERVAL          = 75
_GD_DISPLAYBOX_GRID_HORIZONTALLINEPIXELINTERVAL_SIVIEWER = 25
_GD_DISPLAYBOX_GRID_HORIZONTALTEXTWIDTH                  = 500
_GD_DISPLAYBOX_GRID_HORIZONTALTEXTHEIGHT                 = 120
_GD_DISPLAYBOX_GUIDE_HORIZONTALTEXTHEIGHT                = 120

_TIMEINTERVAL_MOUSEINTERPRETATION_NS = 10e6
_TIMEINTERVAL_POSTDRAGWAITTIME       = 500e6
_TIMEINTERVAL_POSTSCROLLWAITTIME     = 500e6
_TIMEINTERVAL_POSHIGHLIGHTUPDATE     = 10e6

_TIMELIMIT_DRAWQUEUE_NS       = 10e6
_TIMELIMIT_RCLCGPROCESSING_NS = 10e6
_TIMELIMIT_DRAWREMOVAL_NS     = 10e6

_GD_LOADINGGAUGEBAR_HEIGHT = 150

_DATADRAWER_DISPLAYMODE_DATADRAWMETHOD = {'BALANCE':        (0, ('marginBalance_open', 'marginBalance_min', 'marginBalance_max', 'marginBalance_close', 'walletBalance_open', 'walletBalance_min', 'walletBalance_max', 'walletBalance_close')),
                                          'COMMITMENTRATE': (1, ('commitmentRate_open', 'commitmentRate_min', 'commitmentRate_max', 'commitmentRate_close')),
                                          'RISKLEVEL':      (1, ('riskLevel_open', 'riskLevel_min', 'riskLevel_max', 'riskLevel_close')),
                                          'NTRADES_TOTAL':  (2, 'nTrades'),
                                          'NTRADES_BUY':    (2, 'nTrades_buy'),
                                          'NTRADES_SELL':   (2, 'nTrades_sell'),
                                          'NTRADES_PSL':    (2, 'nTrades_psl'),
                                          'NLIQUIDATIONS':  (2, 'nLiquidations')}

#'dailyReportViewer' -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class dailyReportViewer:
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
        self.effectiveTextStyle = self.visualManager.getTextStyle('dailyReportViewer_'+self.textStyle)
        for textStyleCode in self.effectiveTextStyle: self.effectiveTextStyle[textStyleCode]['font_size'] = 80*self.scaler

        #DisplayBox Dimension Standards & Interaction Control Variables
        self.hitBox = dict()
        self.hitBox_Object = atmEta_gui_HitBoxes.hitBox_Rectangular(self.xPos, self.yPos, self.width, self.height)
        self.images = dict()
        self.frameSprites = dict()
        if (self.width  < _GD_OBJECT_MINWIDTH):  self.width  = _GD_OBJECT_MINWIDTH  
        if (self.height < _GD_OBJECT_MINHEIGHT): self.height = _GD_OBJECT_MINHEIGHT 
        self.displayBox = {'MAIN': None,  'MAINGRID_X': None, 'MAINGRID_Y': None, 'SETTINGSBUTTONFRAME': None}
        self.displayBox_graphics = dict()
        for displayBoxName in self.displayBox: self.displayBox_graphics[displayBoxName] = dict()
        self.displayBox_graphics_visibleSIViewers = set()
        self.displayBox_VerticalSection_Order = list()
        self.displayBox_VisibleBoxes = list()
        self.__RCLCGReferences = list()

        #Kline Loading Display Elements
        if (True):
            self.images['DATALOADINGCOVER'] = self.imageManager.getImageByCode("dailyReportViewer_typeA_"+self.style+"_dataLoadingCover", self.width*self.scaler, self.height*self.scaler)
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
        self.simulationCode   = None
        self.simulation       = None
        self.assetName        = None
        self.targetPrecisions = None
        self.data_ForDisplay         = dict()
        self.data_ForDisplay_Maximas = dict()
        self.data_DisplayMode = 'WalletBalance'
        self.data_FetchComplete = True
        self.data_Fetching      = False
        self.data_Fetching_RID  = None
        self.data_DrawQueue        = set()
        self.data_Drawn            = set()
        self.data_DrawRemovalQueue = set()
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

        #ViewRange & Grid Control
        self.gridColor       = self.visualManager.getFromColorTable('DAILYREPORTVIEWER_GRID')
        self.gridColor_Heavy = self.visualManager.getFromColorTable('DAILYREPORTVIEWER_GRIDHEAVY')
        self.guideColor      = self.visualManager.getFromColorTable('DAILYREPORTVIEWER_GUIDECONTENT')
        self.posHighlightColor_hovered  = self.visualManager.getFromColorTable('DAILYREPORTVIEWER_POSHOVERED')
        self.posHighlightColor_selected = self.visualManager.getFromColorTable('DAILYREPORTVIEWER_POSSELECTED')

        #<Horizontal ViewRange & Vertical Grid>
        #---Horizontal ViewRange
        self.intervalID = 11
        self.expectedKlineTemporalWidth = _EXPECTEDTEMPORALWIDTHS[self.intervalID]
        self.horizontalViewRangeWidth_min = None; self.horizontalViewRangeWidth_max = None
        self.horizontalViewRangeWidth_m = None;   self.horizontalViewRangeWidth_b = None
        self.horizontalViewRange = [None, None]
        self.horizontalViewRange_timestampsInViewRange  = set()
        self.horizontalViewRange_timestampsInBufferZone = set()
        #---Horizontal Position Highlighter
        self.posHighlight_hoveredPos       = (None, None, None, None)
        self.posHighlight_updatedPositions = None
        self.posHighlight_selectedPos      = None
        self.posHighlight_lastUpdated_ns   = 0
        #---Vertical Grid
        self.verticalGrid_intervalID = 0
        self.verticalGrid_intervals = list()
        self.nMaxVerticalGridLines = None
        #<Vertical ViewRange & Horizontal Grid>
        #---Vertical ViewRange
        self.verticalViewRange_magnification = 100
        self.verticalValue_min    = 0
        self.verticalValue_max    = 1000
        self.verticalValue_loaded = False
        self.verticalViewRange    = [self.verticalValue_min, self.verticalValue_max]
        self.verticalViewRange_precision = 4
        #---Horizontal Grid
        self.horizontalGridIntervals      = list()
        self.horizontalGridIntervalHeight = None
        self.nMaxHorizontalGridLines      = None

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
        self.__setHVRParams()
        self.__initializeRCLCG()
        self.horizontalViewRange_magnification = 100
        self.horizontalViewRange = [None, round(time.time()+self.expectedKlineTemporalWidth*5)]
        self.horizontalViewRange[0] = round(self.horizontalViewRange[1]-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
        self.__onHViewRangeUpdate(1)
        self.__editVVR_toExtremaCenter()
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
            self.settingsSubPage.addGUIO("DISPLAYMODE_TEXT",         atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos':  yPosPoint0,     'width': 1750, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:DISPLAYMODE'), 'fontSize': 80})
            self.settingsSubPage.addGUIO("DISPLAYMODE_SELECTIONBOX", atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 2, 'xPos': 1850, 'yPos':  yPosPoint0,     'width': 2150, 'height': 250, 'style': 'styleA', 'name': 'DISPLAYMODE_SELECTION', 'nDisplay': 10, 'fontSize': 80, 'expansionDir': 0, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            self.settingsSubPage.addGUIO("TIMEZONE_TEXT",            atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos':  yPosPoint0-350, 'width': 1750, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:TIMEZONE'), 'fontSize': 80})
            self.settingsSubPage.addGUIO("TIMEZONE_SELECTIONBOX",    atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 2, 'xPos': 1850, 'yPos':  yPosPoint0-350, 'width': 2150, 'height': 250, 'style': 'styleA', 'name': 'TIMEZONE_SELECTION', 'nDisplay': 10, 'fontSize': 80, 'expansionDir': 0, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
            yPosPoint1 = yPosPoint0-650
            self.settingsSubPage.addGUIO("LINECOLOR_TITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:LINE'), 'fontSize': 90, 'anchor': 'SW'})
            self.settingsSubPage.addGUIO("LINECOLOR_TEXT",      atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350, 'width': 900, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:COLOR'), 'fontSize': 80})
            self.settingsSubPage.addGUIO("LINECOLOR_LED",       atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 1000, 'yPos': yPosPoint1-350, 'width': 950, 'height': 250, 'style': 'styleA', 'mode': True})
            self.settingsSubPage.addGUIO("LINEWIDTH_TEXT",      atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos': 2050, 'yPos': yPosPoint1-350, 'width': 900, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:WIDTH'), 'fontSize': 80})
            self.settingsSubPage.addGUIO("LINEWIDTH_TEXTINPUT", atmEta_gui_Generals.textInputBox_typeA,           {'groupOrder': 0, 'xPos': 3050, 'yPos': yPosPoint1-350, 'width': 950, 'height': 250, 'style': 'styleA', 'name': 'WidthTextInputBox', 'text': "", 'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
            for index, componentType in enumerate(('R', 'G', 'B', 'A')):
                self.settingsSubPage.addGUIO("LINECOLOR_{:s}_TEXT".format(componentType),   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-700-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': componentType, 'fontSize': 80})
                self.settingsSubPage.addGUIO("LINECOLOR_{:s}_SLIDER".format(componentType), atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': yPosPoint1-650-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': 'Color_{:s}'.format(componentType), 'valueUpdateFunction': self.__onSettingsContentUpdate})
                self.settingsSubPage.addGUIO("LINECOLOR_{:s}_VALUE".format(componentType),  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': yPosPoint1-700-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
            yPosPoint2 = yPosPoint1-1750
            self.settingsSubPage.addGUIO("APPLYNEWSETTINGS",  atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'ApplySettings',   'releaseFunction': self.__onSettingsContentUpdate})
            self.settingsSubPage.addGUIO("SAVECONFIGURATION", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2-700, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:SAVECONFIG'),    'fontSize': 80, 'name': 'SAVECONFIG', 'releaseFunction': self.__onSettingsContentUpdate})
            #GUIO Setup
            displayModeSelections = {'BALANCE':        {'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:BALANCE')},
                                     'COMMITMENTRATE': {'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:COMMITMENTRATE')},
                                     'RISKLEVEL':      {'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:RISKLEVEL')},
                                     'NTRADES_TOTAL':  {'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:NTRADES_TOTAL')},
                                     'NTRADES_BUY':    {'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:NTRADES_BUY')},
                                     'NTRADES_SELL':   {'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:NTRADES_SELL')},
                                     'NTRADES_PSL':    {'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:NTRADES_PSL')},
                                     'NLIQUIDATIONS':  {'text': self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:NLIQUIDATIONS')}}
            self.settingsSubPage.GUIOs["DISPLAYMODE_SELECTIONBOX"].setSelectionList(displayModeSelections, displayTargets = 'all')
            timeZoneSelections = {'LOCAL': {'text': 'LOCAL'}}
            for hour in range (24): timeZoneSelections['UTC+{:d}'.format(hour)] = {'text': 'UTC+{:d}'.format(hour)}
            self.settingsSubPage.GUIOs["TIMEZONE_SELECTIONBOX"].setSelectionList(timeZoneSelections, displayTargets = 'all')

    def __initializeObjectConfig(self):
        self.objectConfig = dict()
        self.objectConfig['DisplayMode'] = 'BALANCE'
        self.objectConfig['TimeZone']    = 'LOCAL'
        self.objectConfig['LINE_Display'] = True
        self.objectConfig['LINE_Width'] = 1
        self.objectConfig['LINE_ColorR%DARK'] =random.randint(64,255); self.objectConfig['LINE_ColorG%DARK'] =random.randint(64,255); self.objectConfig['LINE_ColorB%DARK'] =random.randint(64, 255); self.objectConfig['LINE_ColorA%DARK'] =255
        self.objectConfig['LINE_ColorR%LIGHT']=random.randint(64,255); self.objectConfig['LINE_ColorG%LIGHT']=random.randint(64,255); self.objectConfig['LINE_ColorB%LIGHT']=random.randint(64, 255); self.objectConfig['LINE_ColorA%LIGHT']=255

    def __matchGUIOsToConfig(self):
        self.settingsSubPage.GUIOs["DISPLAYMODE_SELECTIONBOX"].setSelected(self.objectConfig['DisplayMode'], callSelectionUpdateFunction = True)
        self.settingsSubPage.GUIOs["TIMEZONE_SELECTIONBOX"].setSelected(self.objectConfig['TimeZone'],       callSelectionUpdateFunction = True)
        self.settingsSubPage.GUIOs["LINEWIDTH_TEXTINPUT"].updateText(str(self.objectConfig['LINE_Width']))
        _lineColor_r = self.objectConfig['LINE_ColorR%{:s}'.format(self.currentGUITheme)]
        _lineColor_g = self.objectConfig['LINE_ColorG%{:s}'.format(self.currentGUITheme)]
        _lineColor_b = self.objectConfig['LINE_ColorB%{:s}'.format(self.currentGUITheme)]
        _lineColor_a = self.objectConfig['LINE_ColorA%{:s}'.format(self.currentGUITheme)]
        self.settingsSubPage.GUIOs["LINECOLOR_LED"].updateColor(_lineColor_r, _lineColor_g, _lineColor_b, _lineColor_a)
        self.settingsSubPage.GUIOs["LINECOLOR_R_VALUE"].updateText(str(_lineColor_r))
        self.settingsSubPage.GUIOs["LINECOLOR_G_VALUE"].updateText(str(_lineColor_g))
        self.settingsSubPage.GUIOs["LINECOLOR_B_VALUE"].updateText(str(_lineColor_b))
        self.settingsSubPage.GUIOs["LINECOLOR_A_VALUE"].updateText(str(_lineColor_a))
        self.settingsSubPage.GUIOs["LINECOLOR_R_SLIDER"].setSliderValue(newValue = round(_lineColor_r/255*100), callValueUpdateFunction = False)
        self.settingsSubPage.GUIOs["LINECOLOR_G_SLIDER"].setSliderValue(newValue = round(_lineColor_g/255*100), callValueUpdateFunction = False)
        self.settingsSubPage.GUIOs["LINECOLOR_B_SLIDER"].setSliderValue(newValue = round(_lineColor_b/255*100), callValueUpdateFunction = False)
        self.settingsSubPage.GUIOs["LINECOLOR_A_SLIDER"].setSliderValue(newValue = round(_lineColor_a/255*100), callValueUpdateFunction = False)
        self.settingsSubPage.GUIOs["APPLYNEWSETTINGS"].deactivate()
        self.settingsSubPage.GUIOs["SAVECONFIGURATION"].deactivate()
    #Object Configuration & GUIO Initialization END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #DisplayBox Control ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __configureDisplayBoxes(self, onInit = False):
        #[1]: Determine Vertical DisplayBox Order
        if (True):
            self.displayBox_VerticalSection_Order = ['MAINGRID_X', 'MAIN']
            self.displayBox_VisibleBoxes = ['MAINGRID_TEMPORAL', 'SETTINGSBUTTONFRAME', 'KLINESPRICE']
            
        #[2]: Determine DisplayBox Dimensions
        if (True):
            #---Determin General Section Width
            displayBoxWidth_leftSection  = self.width - _GD_DISPLAYBOX_RIGHTSECTION_WIDTH - _GD_DISPLAYBOX_GOFFSET
            displayBoxWidth_rightSection = _GD_DISPLAYBOX_RIGHTSECTION_WIDTH

            #---Determine Vertical Section Height
            displayBoxHeight_MAIN = self.height - _GD_DISPLAYBOX_GOFFSET - _GD_DISPLAYBOX_MAINGRIDX_HEIGHT
        
            #---Set DisplayBox Coordinates and Dimensions
            verticalSectionYPos = self.yPos
            for verticalSectionName in self.displayBox_VerticalSection_Order:
                if (verticalSectionName == 'MAINGRID_X'):
                    #Define DisplayBox and DrawBox Dimensions for 'MAINGRID_TEMPORAL'
                    displayBox_MAINGRID_X = (self.xPos, verticalSectionYPos, displayBoxWidth_leftSection , _GD_DISPLAYBOX_MAINGRIDX_HEIGHT)
                    drawBox_MAINGRID_X    = (displayBox_MAINGRID_X[0]+_GD_DISPLAYBOX_GOFFSET, displayBox_MAINGRID_X[1]+_GD_DISPLAYBOX_GOFFSET, displayBox_MAINGRID_X[2]-_GD_DISPLAYBOX_GOFFSET*2, displayBox_MAINGRID_X[3]-_GD_DISPLAYBOX_GOFFSET*2)
                    self.displayBox['MAINGRID_X']                     = displayBox_MAINGRID_X
                    self.displayBox_graphics['MAINGRID_X']['DRAWBOX'] = drawBox_MAINGRID_X
                
                    #Define DisplayBox Dimensions for 'SETTINGSBUTTONFRAME'
                    displayBox_SETTINGSBUTTONFRAME = (self.xPos+displayBoxWidth_leftSection+_GD_DISPLAYBOX_GOFFSET, verticalSectionYPos, displayBoxWidth_rightSection, _GD_DISPLAYBOX_MAINGRIDX_HEIGHT)
                    self.displayBox['SETTINGSBUTTONFRAME'] = displayBox_SETTINGSBUTTONFRAME

                    verticalSectionYPos += _GD_DISPLAYBOX_MAINGRIDX_HEIGHT+_GD_DISPLAYBOX_GOFFSET

                elif (verticalSectionName == 'MAIN'):
                    #Define DisplayBox and DrawBox Dimensions for 'MAIN'
                    displayBox_MAIN = (self.xPos, verticalSectionYPos, displayBoxWidth_leftSection, displayBoxHeight_MAIN)
                    drawBox_MAIN    = (displayBox_MAIN[0]+_GD_DISPLAYBOX_GOFFSET, displayBox_MAIN[1]+_GD_DISPLAYBOX_GOFFSET, displayBox_MAIN[2]-_GD_DISPLAYBOX_GOFFSET*2, displayBox_MAIN[3]-_GD_DISPLAYBOX_GOFFSET*2)
                    self.displayBox['MAIN']                     = displayBox_MAIN
                    self.displayBox_graphics['MAIN']['DRAWBOX'] = drawBox_MAIN

                    #Define DisplayBox and DrawBox Dimensions for 'MAINGRID_Y'
                    displayBox_MAINGRID_Y = (self.xPos+displayBoxWidth_leftSection+_GD_DISPLAYBOX_GOFFSET, verticalSectionYPos, displayBoxWidth_rightSection, displayBoxHeight_MAIN)
                    drawBox_MAINGRID_Y    = (displayBox_MAINGRID_Y[0]+_GD_DISPLAYBOX_GOFFSET, displayBox_MAINGRID_Y[1]+_GD_DISPLAYBOX_GOFFSET, displayBox_MAINGRID_Y[2]-_GD_DISPLAYBOX_GOFFSET*2, displayBox_MAINGRID_Y[3]-_GD_DISPLAYBOX_GOFFSET*2)
                    self.displayBox['MAINGRID_Y']                     = displayBox_MAINGRID_Y
                    self.displayBox_graphics['MAINGRID_Y']['DRAWBOX'] = drawBox_MAINGRID_Y
                
        #[3]: Set DisplayBox Objects (HitBox, Images, FrameSprites, CamGroups, RCLCGs, etc.)
        if (True):
            self.nMaxVerticalGridLines   = int((self.displayBox['MAINGRID_X'][2]-_GD_DISPLAYBOX_GOFFSET*2)*self.scaler/_GD_DISPLAYBOX_GRID_VERTICALLINEPIXELINTERVAL)
            self.nMaxHorizontalGridLines = int((self.displayBox['MAIN'][3]      -_GD_DISPLAYBOX_GOFFSET*2)*self.scaler/_GD_DISPLAYBOX_GRID_HORIZONTALLINEPIXELINTERVAL)
            if (onInit == True):
                for displayBoxName in self.displayBox:
                    self.mouse_DragDX[displayBoxName] = 0; self.mouse_DragDY[displayBoxName] = 0; self.mouse_ScrollDX[displayBoxName] = 0; self.mouse_ScrollDY[displayBoxName] = 0
                    #---MAINGRID_X
                    if (displayBoxName == 'MAINGRID_X'):
                        displayBox = self.displayBox['MAINGRID_X']
                        drawBox    = self.displayBox_graphics['MAINGRID_X']['DRAWBOX']
                        #Generate Graphic Sprites and Hitboxes
                        self.hitBox['MAINGRID_X'] = atmEta_gui_HitBoxes.hitBox_Rectangular(drawBox[0], drawBox[1], drawBox[2], drawBox[3])
                        self.images['MAINGRID_X'] = self.imageManager.getImageByCode("dailyReportViewer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                        self.frameSprites['MAINGRID_X'] = pyglet.sprite.Sprite(x = displayBox[0]*self.scaler, y = displayBox[1]*self.scaler, img = self.images['MAINGRID_X'][0], batch = self.batch, group = self.group_0)
                        #Setup CamGroup
                        self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_CAMGROUP'] = atmEta_gui_AdvancedPygletGroups.cameraGroup(window = self.window, order = self.groupOrder+1, viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_y0 = 0, projection_y1 = drawBox[3]*self.scaler)
                        #Setup Grids
                        self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_LINES'] = list()
                        self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_TEXTS'] = list()
                        for i in range (self.nMaxVerticalGridLines):
                            self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_LINES'].append(pyglet.shapes.Line(0, (_GD_DISPLAYBOX_GRID_VERTICALTEXTHEIGHT+_GD_DISPLAYBOX_GOFFSET)*self.scaler, 0, drawBox[3]*self.scaler, width = 3, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_CAMGROUP']))
                            self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_TEXTS'].append(atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_CAMGROUP'], text = "-", defaultTextStyle = self.effectiveTextStyle['GRID'],
                                                                                                                                              xPos = 0, yPos = 0, width = _GD_DISPLAYBOX_GRID_VERTICALTEXTWIDTH, height = _GD_DISPLAYBOX_GRID_VERTICALTEXTHEIGHT, showElementBox = False, anchor = 'CENTER'))
                            self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_LINES'][-1].visible = False
                            self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_TEXTS'][-1].hide()
                    #---SETTINGSBUTTONFRAME
                    elif (displayBoxName == 'SETTINGSBUTTONFRAME'):
                        self.hitBox['SETTINGSBUTTONFRAME'] = atmEta_gui_HitBoxes.hitBox_Rectangular(self.displayBox['SETTINGSBUTTONFRAME'][0], self.displayBox['SETTINGSBUTTONFRAME'][1], self.displayBox['SETTINGSBUTTONFRAME'][2], self.displayBox['SETTINGSBUTTONFRAME'][3])
                        self.images['SETTINGSBUTTONFRAME_DEFAULT'] = self.imageManager.getImageByCode("dailyReportViewer_typeA_"+self.style+"_displayBoxFrameInteractable_DEFAULT", self.displayBox['SETTINGSBUTTONFRAME'][2]*self.scaler, self.displayBox['SETTINGSBUTTONFRAME'][3]*self.scaler)
                        self.images['SETTINGSBUTTONFRAME_HOVERED'] = self.imageManager.getImageByCode("dailyReportViewer_typeA_"+self.style+"_displayBoxFrameInteractable_HOVERED", self.displayBox['SETTINGSBUTTONFRAME'][2]*self.scaler, self.displayBox['SETTINGSBUTTONFRAME'][3]*self.scaler)
                        self.images['SETTINGSBUTTONFRAME_PRESSED'] = self.imageManager.getImageByCode("dailyReportViewer_typeA_"+self.style+"_displayBoxFrameInteractable_PRESSED", self.displayBox['SETTINGSBUTTONFRAME'][2]*self.scaler, self.displayBox['SETTINGSBUTTONFRAME'][3]*self.scaler)
                        self.images['SETTINGSBUTTONFRAME_ICON'] = self.imageManager.getImage('settingsIcon_512x512.png', (round(self.displayBox['SETTINGSBUTTONFRAME'][3]*0.65*self.scaler), round(self.displayBox['SETTINGSBUTTONFRAME'][3]*0.65*self.scaler)))
                        self.frameSprites['SETTINGSBUTTONFRAME'] = pyglet.sprite.Sprite(x = self.displayBox['SETTINGSBUTTONFRAME'][0]*self.scaler, y = self.displayBox['SETTINGSBUTTONFRAME'][1]*self.scaler, img = self.images['SETTINGSBUTTONFRAME_DEFAULT'][0], batch = self.batch, group = self.group_0)
                        self.frameSprites['SETTINGSBUTTONFRAME_ICON'] = pyglet.sprite.Sprite(x = (self.displayBox['SETTINGSBUTTONFRAME'][0]+self.displayBox['SETTINGSBUTTONFRAME'][2]/2)*self.scaler-self.images['SETTINGSBUTTONFRAME_ICON'].width/2, 
                                                                                             y = (self.displayBox['SETTINGSBUTTONFRAME'][1]+self.displayBox['SETTINGSBUTTONFRAME'][3]/2)*self.scaler-self.images['SETTINGSBUTTONFRAME_ICON'].height/2, 
                                                                                             img = self.images['SETTINGSBUTTONFRAME'+'_ICON'], batch = self.batch, group = self.group_1)
                        iconColoring = self.visualManager.getFromColorTable('ICON_COLORING')
                        self.frameSprites['SETTINGSBUTTONFRAME_ICON'].color = (iconColoring[0], iconColoring[1], iconColoring[2]); self.frameSprites['SETTINGSBUTTONFRAME'+'_ICON'].opacity = iconColoring[3]
                    #---MAIN
                    elif (displayBoxName == 'MAIN'):
                        displayBox            = self.displayBox['MAIN']
                        displayBox_MAINGRID_Y = self.displayBox['MAINGRID_Y']
                        drawBox               = self.displayBox_graphics['MAIN']['DRAWBOX']
                        drawBox_MAINGRID_Y    = self.displayBox_graphics['MAINGRID_Y']['DRAWBOX']
                        #Generate Graphic Sprites and Hitboxes
                        self.hitBox['MAIN'] = atmEta_gui_HitBoxes.hitBox_Rectangular(drawBox[0], drawBox[1], drawBox[2], drawBox[3])
                        self.images['MAIN'] = self.imageManager.getImageByCode("dailyReportViewer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                        self.frameSprites['MAIN'] = pyglet.sprite.Sprite(x = displayBox[0]*self.scaler, y = displayBox[1]*self.scaler, img = self.images['MAIN'][0], batch = self.batch, group = self.group_0)
                        self.hitBox['MAINGRID_Y'] = atmEta_gui_HitBoxes.hitBox_Rectangular(drawBox_MAINGRID_Y[0], drawBox_MAINGRID_Y[1], drawBox_MAINGRID_Y[2], drawBox_MAINGRID_Y[3])
                        self.images['MAINGRID_Y'] = self.imageManager.getImageByCode("dailyReportViewer_typeA_"+self.style+"_displayBoxFrame", displayBox_MAINGRID_Y[2]*self.scaler, displayBox_MAINGRID_Y[3]*self.scaler)
                        self.frameSprites['MAINGRID_Y'] = pyglet.sprite.Sprite(x = displayBox_MAINGRID_Y[0]*self.scaler, y = displayBox_MAINGRID_Y[1]*self.scaler, img = self.images['MAINGRID_Y'][0], batch = self.batch, group = self.group_0)
                        #Setup CamGroup and DisplaySpaceManager
                        self.displayBox_graphics['MAIN']['HORIZONTALGRID_CAMGROUP']  = atmEta_gui_AdvancedPygletGroups.cameraGroup(window=self.window, order = self.groupOrder+1, viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_x0 = 0, projection_x1 = drawBox[2]*self.scaler)
                        self.displayBox_graphics['MAIN']['VERTICALGRID_CAMGROUP']    = atmEta_gui_AdvancedPygletGroups.cameraGroup(window=self.window, order = self.groupOrder+1, viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_y0 = 0, projection_y1 = drawBox[3]*self.scaler)
                        self.displayBox_graphics['MAIN']['ANALYSISDISPLAY_CAMGROUP'] = atmEta_gui_AdvancedPygletGroups.cameraGroup(window=self.window, order = self.groupOrder+1, viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_y0 = 0, projection_y1 = drawBox[3]*self.scaler)
                        self.displayBox_graphics['MAIN']['RCLCG']        = atmEta_gui_AdvancedPygletGroups.resolutionControlledLayeredCameraGroup(window = self.window, batch = self.batch, viewport_x = drawBox[0]*self.scaler, viewport_y = drawBox[1]*self.scaler, viewport_width = drawBox[2]*self.scaler, viewport_height = drawBox[3]*self.scaler, order = self.groupOrder+2, parentCameraGroup = self.parentCameraGroup, fsdResolution_y = 2)
                        self.displayBox_graphics['MAIN']['RCLCG_XFIXED'] = atmEta_gui_AdvancedPygletGroups.resolutionControlledLayeredCameraGroup(window = self.window, batch = self.batch, viewport_x = drawBox[0]*self.scaler, viewport_y = drawBox[1]*self.scaler, viewport_width = drawBox[2]*self.scaler, viewport_height = drawBox[3]*self.scaler, order = self.groupOrder+2, parentCameraGroup = self.parentCameraGroup, projection_x0 = 0, projection_x1 = 100, fsdResolution_y = 5)
                        self.displayBox_graphics['MAIN']['RCLCG_YFIXED'] = atmEta_gui_AdvancedPygletGroups.resolutionControlledLayeredCameraGroup(window = self.window, batch = self.batch, viewport_x = drawBox[0]*self.scaler, viewport_y = drawBox[1]*self.scaler, viewport_width = drawBox[2]*self.scaler, viewport_height = drawBox[3]*self.scaler, order = self.groupOrder+2, parentCameraGroup = self.parentCameraGroup, projection_y0 = 0, projection_y1 = 100)
                        self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_CAMGROUP'] = atmEta_gui_AdvancedPygletGroups.cameraGroup(window = self.window, order = self.groupOrder+1, viewport_x=drawBox_MAINGRID_Y[0]*self.scaler, viewport_y=drawBox_MAINGRID_Y[1]*self.scaler, viewport_width=drawBox_MAINGRID_Y[2]*self.scaler, viewport_height=drawBox_MAINGRID_Y[3]*self.scaler, parentCameraGroup = self.parentCameraGroup, projection_x0 = 0, projection_x1 = drawBox_MAINGRID_Y[2]*self.scaler)
                        #Add RCLCGs to the reference list
                        self.__RCLCGReferences.append(self.displayBox_graphics['MAIN']['RCLCG'])
                        self.__RCLCGReferences.append(self.displayBox_graphics['MAIN']['RCLCG_XFIXED'])
                        self.__RCLCGReferences.append(self.displayBox_graphics['MAIN']['RCLCG_YFIXED'])
                        #Description Texts
                        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'] = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_hd0, text = "", 
                                                                                                                    defaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                                                                    xPos = drawBox[0], yPos = drawBox[1]+drawBox[3]-200, width = drawBox[2], height = 200, showElementBox = False, anchor = 'W')
                        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'] = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_hd0, text = "", 
                                                                                                                    defaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                                                                    xPos = drawBox[0], yPos = drawBox[1]+drawBox[3]-400, width = drawBox[2], height = 200, showElementBox = False, anchor = 'W')
                        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT3'] = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_hd0, text = self.visualManager.extractText(self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:{:s}'.format(self.data_DisplayMode))), 
                                                                                                                    defaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle,
                                                                                                                    xPos = drawBox[0], yPos = drawBox[1]+drawBox[3]-200, width = drawBox[2], height = 200, showElementBox = False, anchor = 'E')
                        #Setup Positional Highlight
                        self.displayBox_graphics['MAIN']['POSHIGHLIGHT_HOVERED']  = pyglet.shapes.Rectangle(x = 0, y = 0, width = 0, height = drawBox[3]*self.scaler, color = self.posHighlightColor_hovered,  batch = self.batch, group = self.displayBox_graphics['MAIN']['VERTICALGRID_CAMGROUP'])
                        self.displayBox_graphics['MAIN']['POSHIGHLIGHT_SELECTED'] = pyglet.shapes.Rectangle(x = 0, y = 0, width = 0, height = drawBox[3]*self.scaler, color = self.posHighlightColor_selected, batch = self.batch, group = self.displayBox_graphics['MAIN']['VERTICALGRID_CAMGROUP'])
                        self.displayBox_graphics['MAIN']['POSHIGHLIGHT_HOVERED'].visible  = False
                        self.displayBox_graphics['MAIN']['POSHIGHLIGHT_SELECTED'].visible = False
                        self.displayBox_graphics['MAIN']['HORIZONTALGUIDELINE'] = pyglet.shapes.Line(0, 0, drawBox[2]*self.scaler, 0, width = 3, color = self.guideColor, batch = self.batch, group = self.displayBox_graphics['MAIN']['HORIZONTALGRID_CAMGROUP'])
                        self.displayBox_graphics['MAIN']['HORIZONTALGUIDETEXT'] = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics['MAIN']['HORIZONTALGRID_CAMGROUP'], text = "", defaultTextStyle = self.effectiveTextStyle['GUIDECONTENT'],
                                                                                                                       xPos = 0, yPos = 0, width = drawBox[2], height = _GD_DISPLAYBOX_GUIDE_HORIZONTALTEXTHEIGHT, showElementBox = False, anchor = 'E')
                        self.displayBox_graphics['MAIN']['HORIZONTALGUIDELINE'].visible = False
                        self.displayBox_graphics['MAIN']['HORIZONTALGUIDETEXT'].hide()
                        #Setup Grids
                        self.displayBox_graphics['MAIN']['HORIZONTALGRID_LINES'] = list()
                        self.displayBox_graphics['MAIN']['VERTICALGRID_LINES'] = list()
                        self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_LINES'] = list()
                        self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_TEXTS'] = list()
                        for i in range (self.nMaxHorizontalGridLines):
                            self.displayBox_graphics['MAIN']['HORIZONTALGRID_LINES'].append(pyglet.shapes.Line(0, 0, drawBox[2]*self.scaler, 0, width = 1, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['MAIN']['HORIZONTALGRID_CAMGROUP']))
                            self.displayBox_graphics['MAIN']['HORIZONTALGRID_LINES'][-1].visible = False
                            self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_LINES'].append(pyglet.shapes.Line(0, 0, _GD_DISPLAYBOX_GOFFSET*self.scaler, 0, width = 3, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_CAMGROUP']))
                            self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_TEXTS'].append(atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_CAMGROUP'], text = "-", defaultTextStyle = self.effectiveTextStyle['GRID'],
                                                                                                                                       xPos = _GD_DISPLAYBOX_GOFFSET*2, yPos = 0, width = _GD_DISPLAYBOX_GRID_HORIZONTALTEXTWIDTH, height = _GD_DISPLAYBOX_GRID_HORIZONTALTEXTHEIGHT, showElementBox = False, anchor = 'W'))
                            self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_LINES'][-1].visible = False
                            self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_TEXTS'][-1].hide()
                        for i in range (self.nMaxVerticalGridLines):
                            self.displayBox_graphics['MAIN']['VERTICALGRID_LINES'].append(pyglet.shapes.Line(0, 0, 0, drawBox[3]*self.scaler, width = 1, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['MAIN']['VERTICALGRID_CAMGROUP']))
                            self.displayBox_graphics['MAIN']['VERTICALGRID_LINES'][-1].visible = False
            else:
                for displayBoxName in self.displayBox:
                    if (displayBoxName in self.displayBox_VisibleBoxes):
                        self.mouse_DragDX[displayBoxName] = 0; self.mouse_DragDY[displayBoxName] = 0; self.mouse_ScrollDX[displayBoxName] = 0; self.mouse_ScrollDY[displayBoxName] = 0
                        #SETTINGSBUTTONFRAME
                        if (displayBoxName == 'SETTINGSBUTTONFRAME'):
                            displayBox = self.displayBox['SETTINGSBUTTONFRAME']
                            self.hitBox['SETTINGSBUTTONFRAME'].reposition(xPos = displayBox[0], yPos = displayBox[1])
                            self.frameSprites['SETTINGSBUTTONFRAME'].position = (displayBox[0]*self.scaler, displayBox[1]*self.scaler, self.frameSprites['SETTINGSBUTTONFRAME'].z)
                            self.frameSprites['SETTINGSBUTTONFRAME_ICON'].position = ((displayBox[0]+displayBox[2]/2)*self.scaler-self.images['SETTINGSBUTTONFRAME_ICON'].width/2,
                                                                                      (displayBox[1]+displayBox[3]/2)*self.scaler-self.images['SETTINGSBUTTONFRAME_ICON'].height/2,
                                                                                      self.frameSprites['SETTINGSBUTTONFRAME'].z)
                        #MAIN
                        elif (displayBoxName == 'MAIN'):
                            displayBox            = self.displayBox['MAIN']
                            displayBox_MAINGRID_Y = self.displayBox['MAINGRID_Y']
                            drawBox               = self.displayBox_graphics['MAIN']['DRAWBOX']
                            drawBox_MAINGRID_Y    = self.displayBox_graphics['MAINGRID_Y']['DRAWBOX']
                            #Reposition & Resize Graphics and Hitboxes
                            self.hitBox['MAIN'].reposition(xPos = drawBox[0], yPos = drawBox[1])
                            self.hitBox['MAIN'].resize(width = drawBox[2], height = drawBox[3])
                            self.images['MAIN'] = self.imageManager.getImageByCode("dailyReportViewer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                            self.frameSprites['MAIN'].position = (displayBox[0]*self.scaler, displayBox[1]*self.scaler, self.frameSprites['MAIN'].z)
                            self.frameSprites['MAIN'].image = self.images['MAIN'][0]
                            self.hitBox['MAINGRID_Y'].reposition(xPos = drawBox_MAINGRID_Y[0], yPos = drawBox_MAINGRID_Y[1])
                            self.hitBox['MAINGRID_Y'].resize(width = drawBox_MAINGRID_Y[2], height = drawBox_MAINGRID_Y[3])
                            self.images['MAINGRID_Y'] = self.imageManager.getImageByCode("dailyReportViewer_typeA_"+self.style+"_displayBoxFrame", drawBox_MAINGRID_Y[2]*self.scaler, drawBox_MAINGRID_Y[3]*self.scaler)
                            self.frameSprites['MAINGRID_Y'].position = (drawBox_MAINGRID_Y[0]*self.scaler, drawBox_MAINGRID_Y[1]*self.scaler, self.frameSprites['MAINGRID_Y'].z)
                            self.frameSprites['MAINGRID_Y'].image = self.images['MAINGRID_Y'][0]
                            #Reposition & Resize CamGroups and RCLCGs
                            self.displayBox_graphics['MAIN']['HORIZONTALGRID_CAMGROUP'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics['MAIN']['VERTICALGRID_CAMGROUP'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics['MAIN']['ANALYSISDISPLAY_CAMGROUP'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics['MAIN']['HORIZONTALGRID_CAMGROUP'].updateProjection(projection_x0 = 0, projection_x1 = drawBox[2]*self.scaler)
                            self.displayBox_graphics['MAIN']['VERTICALGRID_CAMGROUP'].updateProjection(projection_y0 = 0, projection_y1 = drawBox[3]*self.scaler)
                            self.displayBox_graphics['MAIN']['ANALYSISDISPLAY_CAMGROUP'].updateProjection(projection_x0 = 1, projection_x1 = drawBox[2]*self.scaler, projection_y0 = 0, projection_y1 = drawBox[3]*self.scaler)
                            self.displayBox_graphics['MAIN']['RCLCG'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics['MAIN']['RCLCG_XFIXED'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics['MAIN']['RCLCG_YFIXED'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_CAMGROUP'].updateViewport(viewport_x=drawBox_MAINGRID_Y[0]*self.scaler, viewport_y=drawBox_MAINGRID_Y[1]*self.scaler, viewport_width=drawBox_MAINGRID_Y[2]*self.scaler, viewport_height=drawBox_MAINGRID_Y[3]*self.scaler)
                            self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_CAMGROUP'].updateProjection(projection_x0 = 0, projection_x1 = drawBox_MAINGRID_Y[2]*self.scaler)
                            #Reposition & Resize Auxillary Objects
                            self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'].moveTo(x = drawBox[0], y = drawBox[1]+drawBox[3]-200)
                            self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'].changeSize(width = drawBox[2])
                            self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'].moveTo(x = drawBox[0], y = drawBox[1]+drawBox[3]-400)
                            self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'].changeSize(width = drawBox[2])
                            self.displayBox_graphics['MAIN']['POSHIGHLIGHT_HOVERED'].height  = drawBox[3]*self.scaler
                            self.displayBox_graphics['MAIN']['POSHIGHLIGHT_SELECTED'].height = drawBox[3]*self.scaler
                            self.displayBox_graphics['MAIN']['HORIZONTALGUIDELINE'].x2 = drawBox[2]*self.scaler
                            self.displayBox_graphics['MAIN']['HORIZONTALGUIDETEXT'].changeSize(width = drawBox[2])
                            #Setup Grids
                            for horizontalGridText in self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_TEXTS']: horizontalGridText.delete()
                            self.displayBox_graphics['MAIN']['HORIZONTALGRID_LINES'] = list()
                            self.displayBox_graphics['MAIN']['VERTICALGRID_LINES'] = list()
                            self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_LINES'] = list()
                            self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_TEXTS'] = list()
                            for i in range (self.nMaxHorizontalGridLines):
                                self.displayBox_graphics['MAIN']['HORIZONTALGRID_LINES'].append(pyglet.shapes.Line(0, 0, drawBox[2]*self.scaler, 0, width = 1, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['MAIN']['HORIZONTALGRID_CAMGROUP']))
                                self.displayBox_graphics['MAIN']['HORIZONTALGRID_LINES'][-1].visible = False
                                self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_LINES'].append(pyglet.shapes.Line(0, 0, _GD_DISPLAYBOX_GOFFSET*self.scaler, 0, width = 3, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_CAMGROUP']))
                                self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_TEXTS'].append(atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_CAMGROUP'], text = "-", defaultTextStyle = self.effectiveTextStyle['GRID'],
                                                                                                                                           xPos = _GD_DISPLAYBOX_GOFFSET*2, yPos = 0, width = _GD_DISPLAYBOX_GRID_HORIZONTALTEXTWIDTH, height = _GD_DISPLAYBOX_GRID_HORIZONTALTEXTHEIGHT, showElementBox = False, anchor = 'W'))
                                self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_LINES'][-1].visible = False
                                self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_TEXTS'][-1].hide()
                            for i in range (self.nMaxVerticalGridLines):
                                self.displayBox_graphics['MAIN']['VERTICALGRID_LINES'].append(pyglet.shapes.Line(0, 0, 0, drawBox[3]*self.scaler, width = 1, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['MAIN']['VERTICALGRID_CAMGROUP']))
                                self.displayBox_graphics['MAIN']['VERTICALGRID_LINES'][-1].visible = False
                        #MAINGRID_X
                        elif (displayBoxName == 'MAINGRID_X'):
                            displayBox = self.displayBox['MAINGRID_X']
                            drawBox    = self.displayBox_graphics['MAINGRID_X']['DRAWBOX']
                            #Reposition & Resize Graphics and Hitboxes
                            self.hitBox['MAINGRID_X'].reposition(xPos = drawBox[0], yPos = drawBox[1])
                            self.hitBox['MAINGRID_X'].resize(width = drawBox[2], height = drawBox[3])
                            self.images['MAINGRID_X'] = self.imageManager.getImageByCode("dailyReportViewer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                            self.frameSprites['MAINGRID_X'].position = (displayBox[0]*self.scaler, displayBox[1]*self.scaler, self.frameSprites['MAINGRID_X'].z)
                            self.frameSprites['MAINGRID_X'].image = self.images['MAINGRID_X'][0]
                            #Reposition & Resize CamGroups and RCLCGs
                            self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_CAMGROUP'].updateViewport(viewport_x=drawBox[0]*self.scaler, viewport_y=drawBox[1]*self.scaler, viewport_width=drawBox[2]*self.scaler, viewport_height=drawBox[3]*self.scaler)
                            #Setup Grids
                            for verticalGridText in self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_TEXTS']: verticalGridText.delete()
                            self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_LINES'] = list()
                            self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_TEXTS'] = list()
                            for i in range (self.nMaxVerticalGridLines):
                                self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_LINES'].append(pyglet.shapes.Line(0, (_GD_DISPLAYBOX_GRID_VERTICALTEXTHEIGHT+_GD_DISPLAYBOX_GOFFSET)*self.scaler, 0, drawBox[3]*self.scaler, width = 3, color = self.gridColor, batch = self.batch, group = self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_CAMGROUP']))
                                self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_TEXTS'].append(atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_CAMGROUP'], text = "-", defaultTextStyle = self.effectiveTextStyle['GRID'],
                                                                                                                                         xPos = 0, yPos = 0, width = _GD_DISPLAYBOX_GRID_VERTICALTEXTWIDTH, height = _GD_DISPLAYBOX_GRID_VERTICALTEXTHEIGHT, showElementBox = False, anchor = 'CENTER'))
                                self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_LINES'][-1].visible = False
                                self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_TEXTS'][-1].hide()

        #[4]: Size and Position Data Loading Gauge Bar and Text
        if (True):
            self.dataLoadingGaugeBar.resize(width      = round(self.width*0.9), height = _GD_LOADINGGAUGEBAR_HEIGHT)
            self.dataLoadingTextBox_perc.resize(width  = round(self.width*0.9), height = _GD_LOADINGGAUGEBAR_HEIGHT)
            self.dataLoadingTextBox.resize(width       = round(self.width*0.9), height = 200)
            self.dataLoadingGaugeBar.moveTo(x     = round(self.xPos+self.width*0.05), y = round(self.yPos+self.height/2-_GD_LOADINGGAUGEBAR_HEIGHT))
            self.dataLoadingTextBox_perc.moveTo(x = round(self.xPos+self.width*0.05), y = round(self.yPos+self.height/2-_GD_LOADINGGAUGEBAR_HEIGHT))
            self.dataLoadingTextBox.moveTo(x      = round(self.xPos+self.width*0.05), y = round(self.yPos+self.height/2))

    def __initializeRCLCG(self, verticalPrecision = None):
        if (verticalPrecision == None): self.verticalViewRange_precision = 0
        else:                           self.verticalViewRange_precision = verticalPrecision
        precision_x = math.floor(math.log(self.expectedKlineTemporalWidth, 10))
        precision_y = -self.verticalViewRange_precision
        self.displayBox_graphics['MAIN']['RCLCG'].setPrecision(precision_x = precision_x, precision_y = precision_y, transferObjects = False)
        self.displayBox_graphics['MAIN']['RCLCG_XFIXED'].setPrecision(precision_y = precision_y, precision_x = 0, transferObjects = False)
        self.displayBox_graphics['MAIN']['RCLCG_YFIXED'].setPrecision(precision_x = precision_x, precision_y = 0, transferObjects = False)
    #DisplayBox Control END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Processings -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def process(self, t_elapsed_ns):
        mei_beg = time.perf_counter_ns()
        self.settingsSubPage.process(t_elapsed_ns)                                                                            #[1]: Subpage Processing
        self.__process_MouseEventInterpretation()                                                                             #[2]: Mouse Event Interpretation
        self.__process_PosHighlightUpdate(mei_beg)                                                                            #[3]: PosHighlight Update
        if (self.data_FetchComplete == True):
            waitPostDrag   = (mei_beg-self.mouse_lastDragged_ns  <= _TIMEINTERVAL_POSTDRAGWAITTIME)
            waitPostScroll = (mei_beg-self.mouse_lastScrolled_ns <= _TIMEINTERVAL_POSTSCROLLWAITTIME)
            if ((waitPostDrag == False) and (waitPostScroll == False)): processNext = not(self.__process_drawQueues(mei_beg)) #[5]: Draw Queues Processing
            else:                                                       processNext = True
            if (processNext == True): processNext = not(self.__process_RCLCGs(mei_beg))                                       #[6]: RCLCGs Processing
            if (processNext == True): self.__process_drawRemovalQueues(mei_beg)                                               #[7]: Draw Removal Queues Processing
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
                        if   (section == 'MAIN'):       self.__editVPosition(delta_drag = drag_dy); self.__editHPosition(delta_drag = drag_dx)
                        elif (section == 'MAINGRID_Y'): self.__editVMagFactor(delta_drag = drag_dy)
                        elif (section == 'MAINGRID_X'): self.__editHMagFactor(delta_drag = drag_dx)
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
                        elif (section == 'MAIN'):       self.__editHMagFactor(delta_scroll = scroll_dy); self.__updatePosHighlight(self.mouse_Event_lastRead['x'], self.mouse_Event_lastRead['y'], self.mouse_lastHoveredSection, updateType = 0)
                        elif (section == 'MAINGRID_Y'): pass
                        elif (section == 'MAINGRID_X'): pass
                        #Delta Reset
                        self.mouse_ScrollDX[section] = 0; self.mouse_ScrollDY[section] = 0
                self.mouse_Scrolled = False
            #[1-3]: Period Counter Reset
            self.mouse_Event_lastInterpreted_ns = time.perf_counter_ns()

    def __process_PosHighlightUpdate(self, mei_beg):
        if (self.posHighlight_updatedPositions != None) and (_TIMEINTERVAL_POSHIGHLIGHTUPDATE <= mei_beg - self.posHighlight_lastUpdated_ns): self.__onPosHighlightUpdate()

    def __process_drawQueues(self, mei_beg):
        while ((time.perf_counter_ns()-mei_beg < _TIMELIMIT_DRAWQUEUE_NS) and (0 < len(self.data_DrawQueue))): self.__dataDrawer_draw(timestamp = self.data_DrawQueue.pop())
        return (0 < len(self.data_DrawQueue))

    def __process_RCLCGs(self, mei_beg):
        remainingProcTime = _TIMELIMIT_RCLCGPROCESSING_NS-(time.perf_counter_ns()-mei_beg)
        nRefedRCLCGs = len(self.__RCLCGReferences)
        #If there exist any shapes within the focus do draw, process them first
        RCLCGRefIndex = 0
        while ((RCLCGRefIndex < nRefedRCLCGs) and (0 < remainingProcTime)):
            if (self.__RCLCGReferences[RCLCGRefIndex].processShapeGenerationQueue(remainingProcTime, currentFocusOnly = True) == True): return True #Will return True if timeout has occurred and there still exist more shapes to draw
            else:
                remainingProcTime = _TIMELIMIT_RCLCGPROCESSING_NS-(time.perf_counter_ns()-mei_beg)
                RCLCGRefIndex += 1
        #If there is no more shapes to draw in the current focus, draw shapes outside the focus
        RCLCGRefIndex = 0
        while ((RCLCGRefIndex < nRefedRCLCGs) and (0 < remainingProcTime)):
            if (self.__RCLCGReferences[RCLCGRefIndex].processShapeGenerationQueue(remainingProcTime, currentFocusOnly = False) == True): return True #Will return True if timeout has occurred and there still exist more shapes to draw
            else:
                remainingProcTime = _TIMELIMIT_RCLCGPROCESSING_NS-(time.perf_counter_ns()-mei_beg)
                RCLCGRefIndex += 1
        #Return if there exist any more shapes to draw
        return False

    def __process_drawRemovalQueues(self, mei_beg):
        while ((0 < len(self.data_DrawRemovalQueue)) and (time.perf_counter_ns()-mei_beg < _TIMELIMIT_DRAWREMOVAL_NS)):
            self.__dataDrawer_RemoveExpiredDrawings(self.data_DrawRemovalQueue.pop())
    #Processings END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #User Interaction Control ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def handleMouseEvent(self, event):
        if ((self.data_Fetching == False) and (self.hidden == False)):
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
                    #[1]: New Hovered Section is 'SETTINGSBUTTONFRAME'
                    if (hoveredSection == 'SETTINGSBUTTONFRAME'):
                        self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_HOVERED'][0]
                        self.settingsButtonStatus = 'HOVERED'
                    #  or New Hovered Section is 'SETTINGSSUBPAGE'
                    elif (hoveredSection == 'SETTINGSSUBPAGE'):
                        self.settingsSubPage.handleMouseEvent({'eType': "HOVERENTERED", 'x': event['x'], 'y': event['y']})
                    #  or New Hovered Section is None
                    elif (hoveredSection == None):
                        self.__updatePosHighlight(event['x'], event['y'], hoveredSection, updateType = 1)
                    #[2]: Last Hovered Section was 'SETTINGSBUTTONFRAME'
                    if (self.mouse_lastHoveredSection == 'SETTINGSBUTTONFRAME'):
                        self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_DEFAULT'][0]
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
                if (self.mouse_lastHoveredSection == 'SETTINGSBUTTONFRAME'):
                    self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_PRESSED'][0]
                    self.settingsButtonStatus = 'PRESSED'
                elif (self.mouse_lastHoveredSection == 'SETTINGSSUBPAGE'): self.settingsSubPage.handleMouseEvent(event)
                #POSHIGHLIGHT Control
                if ((self.mouse_lastHoveredSection != None) and (self.mouse_lastHoveredSection == 'MAIN')): self.__updatePosHighlight(event['x'], event['y'], self.mouse_lastHoveredSection, updateType = 1)
                #Recording
                self.mouse_lastSelectedSection = self.mouse_lastHoveredSection
                self.mouse_Event_lastPressed = event
        
            elif (event['eType'] == "RELEASED"):
                if (self.mouse_lastSelectedSection == self.mouse_lastHoveredSection):
                    if (self.mouse_lastHoveredSection == 'SETTINGSBUTTONFRAME'):
                        self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_HOVERED'][0]
                        self.settingsButtonStatus = 'HOVERED'
                        self.__onSettingsButtonClick()
                    elif (self.mouse_lastHoveredSection == 'SETTINGSSUBPAGE'): self.settingsSubPage.handleMouseEvent(event)
                else:
                    if (self.mouse_lastSelectedSection == 'SETTINGSBUTTONFRAME'):
                        self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_DEFAULT'][0]
                        self.settingsButtonStatus = 'DEFAULT'
                    elif (self.mouse_lastSelectedSection == 'SETTINGSSUBPAGE'): self.settingsSubPage.handleMouseEvent({'eType': "HOVERESCAPED", 'x': event['x'], 'y': event['y']})
                    if (self.mouse_lastHoveredSection == 'SETTINGSBUTTONFRAME'):
                        self.frameSprites['SETTINGSBUTTONFRAME'].image = self.images['SETTINGSBUTTONFRAME_HOVERED'][0]
                        self.settingsButtonStatus = 'HOVERED'
                    elif (self.mouse_lastHoveredSection == 'SETTINGSSUBPAGE'): self.settingsSubPage.handleMouseEvent({'eType': "HOVEREENTERED", 'x': event['x'], 'y': event['y']})
                #POSHIGHLIGHT Control
                if ((self.mouse_lastHoveredSection != None) and (self.mouse_lastHoveredSection == 'MAIN')): 
                    self.__updatePosHighlight(event['x'], event['y'], self.mouse_lastHoveredSection, updateType = 0)
                    if ((self.mouse_Event_lastPressed != None) and (self.mouse_Event_lastPressed['x'] == event['x']) and (self.mouse_Event_lastPressed['y'] == event['y'])):
                        #LEFT MOUSE BUTTON -> POSSELECTION Update
                        if (event['button'] == 1): self.__updatePosSelection(updateType = 0)   
                        #RIGHT MOUSE BUTTON -> moveToExtremaCenter
                        elif (event['button'] == 4): self.__editVVR_toExtremaCenter()

            elif (event['eType'] == "DRAGGED"):
                #Find hovering section
                hoveredSection = None
                if (self.settingsSubPage_Opened == True) and (self.settingsSubPage.isTouched(event['x'], event['y']) == True): hoveredSection = 'SETTINGSSUBPAGE'
                else:
                    for displayBoxName in self.hitBox:
                        if (self.hitBox[displayBoxName].isTouched(event['x'], event['y']) == True): hoveredSection = displayBoxName; break
                #Drag Source
                if (self.mouse_lastSelectedSection == 'SETTINGSSUBPAGE'): self.settingsSubPage.handleMouseEvent(event)
                elif (self.mouse_lastSelectedSection != None) and (self.mouse_lastSelectedSection != 'SETTINGSBUTTONFRAME'): 
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


                """
                if ((self.descriptorTarget != None) and (self.posHighlight_hoveredPos[0] in self.data_ForDisplay[self.data_DisplayMode][self.descriptorTarget])):
                    dataValue = self.data_ForDisplay[self.data_DisplayMode][self.descriptorTarget][self.posHighlight_hoveredPos[0]]
                    #Time
                    _displayText      = datetime.fromtimestamp(self.posHighlight_hoveredPos[0]+self.timezoneDelta, tz = timezone.utc).strftime(" %Y/%m/%d %H:%M")
                    _displayTextStyle = [((0, len(_displayText)), 'DEFAULT')]
                    #Descriptor Target
                    displayLineNumber = self.data_DisplayLineAllocations[self.descriptorTarget]
                    currentLineStyle = self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'].getTextStyle(displayLineNumber)
                    currentLineColor = (self.objectConfig['LINE_{:d}_ColorR%{:s}'.format(displayLineNumber, self.currentGUITheme)],
                                        self.objectConfig['LINE_{:d}_ColorG%{:s}'.format(displayLineNumber, self.currentGUITheme)],
                                        self.objectConfig['LINE_{:d}_ColorB%{:s}'.format(displayLineNumber, self.currentGUITheme)],
                                        self.objectConfig['LINE_{:d}_ColorA%{:s}'.format(displayLineNumber, self.currentGUITheme)])
                    if (currentLineStyle == None) or (currentLineStyle['color'] != currentLineColor):
                        newTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'].copy()
                        newTextStyle['color'] = currentLineColor
                        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'].addTextStyle(displayLineNumber, newTextStyle)
                    _dt_descriptorTarget = " <{:s}>".format(self.descriptorTarget)
                    _displayTextStyle.append(((len(_displayText), len(_displayText)+len(_dt_descriptorTarget)), displayLineNumber))
                    _displayText += _dt_descriptorTarget
                    #Values
                    if (self.data_DisplayMode == 'WalletBalance'):
                        quoteUnit = self.data_SimulationResults[self.descriptorTarget]['quoteUnit']
                        positionAllocationBalance = self.data_SimulationResults[self.descriptorTarget]['positionAllocationBalance']
                        if (dataValue['min'] < positionAllocationBalance):      _dtPair_color_min   = 'RED_LIGHT'
                        elif (positionAllocationBalance < dataValue['min']):    _dtPair_color_min   = 'GREEN_LIGHT'
                        elif (dataValue['min'] == positionAllocationBalance):   _dtPair_color_min   = 'DEFAULT'
                        if (dataValue['max'] < positionAllocationBalance):      _dtPair_color_max   = 'RED_LIGHT'
                        elif (positionAllocationBalance < dataValue['max']):    _dtPair_color_max   = 'GREEN_LIGHT'
                        elif (dataValue['max'] == positionAllocationBalance):   _dtPair_color_max   = 'DEFAULT'
                        if (dataValue['final'] < positionAllocationBalance):    _dtPair_color_final = 'RED_LIGHT'
                        elif (positionAllocationBalance < dataValue['final']):  _dtPair_color_final = 'GREEN_LIGHT'
                        elif (dataValue['final'] == positionAllocationBalance): _dtPair_color_final = 'DEFAULT'
                        _dtPair = ((" Min: ",                                          'DEFAULT'), 
                                   (str(dataValue['min'])+" {:s}".format(quoteUnit),   _dtPair_color_min), 
                                   (", Max: ",                                         'DEFAULT'), 
                                   (str(dataValue['max'])+" {:s}".format(quoteUnit),   _dtPair_color_max), 
                                   (", Final: ",                                       'DEFAULT'), 
                                   (str(dataValue['final'])+" {:s}".format(quoteUnit), _dtPair_color_final))
                    elif (self.data_DisplayMode == 'DailyNumberOfTrades'):
                        _dtPair = ((" Daily Number of Trades: ", 'DEFAULT'), 
                                   (str(dataValue),              'DEFAULT'))
                    elif (self.data_DisplayMode == 'DailyNetProfit'):
                        quoteUnit = self.data_SimulationResults[self.descriptorTarget]['quoteUnit']
                        if   (dataValue < 0):  _dtPair_color_value = 'RED_LIGHT'
                        elif (0 < dataValue):  _dtPair_color_value = 'GREEN_LIGHT'
                        elif (dataValue == 0): _dtPair_color_value = 'DEFAULT'
                        _dtPair = ((" Daily Net Profit: ",                    'DEFAULT'), 
                                   (str(dataValue)+"{:s}".format(quoteUnit), _dtPair_color_value))
                    elif (self.data_DisplayMode == 'DailySuccessRate'):
                        if   ( 0 <= dataValue <   20): _dtPair_color_value = 'RED'
                        elif (20 <= dataValue <   40): _dtPair_color_value = 'GREEN_LIGHT'
                        elif (40 <= dataValue <   50): _dtPair_color_value = 'ORANGE_LIGHT'
                        elif (50 <= dataValue <   80): _dtPair_color_value = 'GREEN_LIGHT'
                        elif (80 <= dataValue <= 100): _dtPair_color_value = 'GREEN'
                        _dtPair = ((" Daily Success Rate: ",       'DEFAULT'), 
                                   ("{:.2f} %".format(dataValue), _dtPair_color_value))
                    elif (self.data_DisplayMode == 'DailyGLRatio'):
                        if   ( 0 <= dataValue <   20): _dtPair_color_value = 'RED'
                        elif (20 <= dataValue <   40): _dtPair_color_value = 'GREEN_LIGHT'
                        elif (40 <= dataValue <   50): _dtPair_color_value = 'ORANGE_LIGHT'
                        elif (50 <= dataValue <   80): _dtPair_color_value = 'GREEN_LIGHT'
                        elif (80 <= dataValue <= 100): _dtPair_color_value = 'GREEN'
                        _dtPair = ((" Daily G/L Ratio: ",          'DEFAULT'), 
                                   ("{:.2f} %".format(dataValue), _dtPair_color_value))
                    elif (self.data_DisplayMode == 'DailyGFRatio'):
                        if   ( 0 <= dataValue <   20): _dtPair_color_value = 'RED'
                        elif (20 <= dataValue <   40): _dtPair_color_value = 'GREEN_LIGHT'
                        elif (40 <= dataValue <   50): _dtPair_color_value = 'ORANGE_LIGHT'
                        elif (50 <= dataValue <   80): _dtPair_color_value = 'GREEN_LIGHT'
                        elif (80 <= dataValue <= 100): _dtPair_color_value = 'GREEN'
                        _dtPair = ((" Daily G/F Ratio: ",          'DEFAULT'), 
                                   ("{:.2f} %".format(dataValue), _dtPair_color_value))
                    elif (self.data_DisplayMode == 'DailyGLFRatio'):
                        if   ( 0 <= dataValue <   20): _dtPair_color_value = 'RED'
                        elif (20 <= dataValue <   40): _dtPair_color_value = 'GREEN_LIGHT'
                        elif (40 <= dataValue <   50): _dtPair_color_value = 'ORANGE_LIGHT'
                        elif (50 <= dataValue <   80): _dtPair_color_value = 'GREEN_LIGHT'
                        elif (80 <= dataValue <= 100): _dtPair_color_value = 'GREEN'
                        _dtPair = ((" Daily G/LF Ratio: ",         'DEFAULT'), 
                                   ("{:.2f} %".format(dataValue), _dtPair_color_value))
                    for _dt, _dts in _dtPair: _displayTextStyle.append(((len(_displayText), len(_displayText)+len(_dt)), _dts)); _displayText += _dt
                    self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'].setText(_displayText, _displayTextStyle)
                else:
                    displayText_time = datetime.fromtimestamp(self.posHighlight_hoveredPos[0]+self.timezoneDelta, tz = timezone.utc).strftime(" %Y/%m/%d %H:%M")
                    self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'].setText(displayText_time, [((0, len(displayText_time)), 'DEFAULT')])
                """
                
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
        if ((self.data_Fetching == False) and (self.hidden == False)):
            if (self.mouse_lastSelectedSection == 'SETTINGSSUBPAGE'): self.settingsSubPage.handleKeyEvent(event)
    #User Interaction Control END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Basic Object Control -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def show(self):
        self.hidden = False
        for displayBoxName in self.frameSprites: self.frameSprites[displayBoxName].visible = True
        self.displayBox_graphics['MAIN']['HORIZONTALGRID_CAMGROUP'].show()
        self.displayBox_graphics['MAIN']['VERTICALGRID_CAMGROUP'].show()
        self.displayBox_graphics['MAIN']['ANALYSISDISPLAY_CAMGROUP'].show()
        self.displayBox_graphics['MAIN']['RCLCG'].show()
        self.displayBox_graphics['MAIN']['RCLCG_XFIXED'].show()
        self.displayBox_graphics['MAIN']['RCLCG_YFIXED'].show()
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'].show()
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'].show()
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT3'].show()
        self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_CAMGROUP'].visible = True
        self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_CAMGROUP'].visible = True
        if (self.settingsSubPage_Opened == True): self.settingsSubPage.show()
        if ((self.data_FetchComplete == False) and (self.data_Fetching == True)):
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
        self.displayBox_graphics['MAIN']['HORIZONTALGRID_CAMGROUP'].hide()
        self.displayBox_graphics['MAIN']['VERTICALGRID_CAMGROUP'].hide()
        self.displayBox_graphics['MAIN']['ANALYSISDISPLAY_CAMGROUP'].hide()
        self.displayBox_graphics['MAIN']['RCLCG'].hide()
        self.displayBox_graphics['MAIN']['RCLCG_XFIXED'].hide()
        self.displayBox_graphics['MAIN']['RCLCG_YFIXED'].hide()
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'].hide()
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'].hide()
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT3'].hide()
        self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_CAMGROUP'].visible = False
        self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_CAMGROUP'].visible = False
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
                if (displayBoxName == 'SETTINGSBUTTONFRAME'):
                    self.hitBox['SETTINGSBUTTONFRAME'].reposition(xPos = self.displayBox['SETTINGSBUTTONFRAME'][0], yPos = self.displayBox['SETTINGSBUTTONFRAME'][1])
                    self.frameSprites['SETTINGSBUTTONFRAME'].position = (self.displayBox['SETTINGSBUTTONFRAME'][0]*self.scaler, self.displayBox['SETTINGSBUTTONFRAME'][1]*self.scaler, self.frameSprites['SETTINGSBUTTONFRAME'].z)
                    self.frameSprites['SETTINGSBUTTONFRAME_ICON'].position = ((self.displayBox['SETTINGSBUTTONFRAME'][0]+self.displayBox['SETTINGSBUTTONFRAME'][2]/2)*self.scaler-self.images['SETTINGSBUTTONFRAME_ICON'].width/2,
                                                                              (self.displayBox['SETTINGSBUTTONFRAME'][1]+self.displayBox['SETTINGSBUTTONFRAME'][3]/2)*self.scaler-self.images['SETTINGSBUTTONFRAME_ICON'].height/2,
                                                                              self.frameSprites['SETTINGSBUTTONFRAME_ICON'].z)
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

        newEffectiveTextStyle = self.visualManager.getTextStyle('dailyReportViewer_'+self.textStyle)
        for styleTarget in newEffectiveTextStyle: newEffectiveTextStyle[styleTarget]['font_size'] = self.effectiveTextStyle[styleTarget]['font_size']
        self.effectiveTextStyle = newEffectiveTextStyle
        
        self.gridColor       = self.visualManager.getFromColorTable('DAILYREPORTVIEWER_GRID')
        self.gridColor_Heavy = self.visualManager.getFromColorTable('DAILYREPORTVIEWER_GRIDHEAVY')
        self.guideColor      = self.visualManager.getFromColorTable('DAILYREPORTVIEWER_GUIDECONTENT')
        self.posHighlightColor_hovered  = self.visualManager.getFromColorTable('DAILYREPORTVIEWER_POSHOVERED')
        self.posHighlightColor_selected = self.visualManager.getFromColorTable('DAILYREPORTVIEWER_POSSELECTED')

        #Object Image Update
        for displayBoxName in self.displayBox:
            if (self.displayBox[displayBoxName] != None):
                if (displayBoxName == 'SETTINGSBUTTONFRAME'):
                    self.images['SETTINGSBUTTONFRAME_DEFAULT'] = self.imageManager.getImageByLoadIndex(self.images['SETTINGSBUTTONFRAME_DEFAULT'][1])
                    self.images['SETTINGSBUTTONFRAME_HOVERED'] = self.imageManager.getImageByLoadIndex(self.images['SETTINGSBUTTONFRAME_HOVERED'][1])
                    self.images['SETTINGSBUTTONFRAME_PRESSED'] = self.imageManager.getImageByLoadIndex(self.images['SETTINGSBUTTONFRAME_PRESSED'][1])
                    iconColoring = self.visualManager.getFromColorTable('ICON_COLORING')
                    self.frameSprites[displayBoxName].image = self.images['SETTINGSBUTTONFRAME_'+self.settingsButtonStatus][0]
                    self.frameSprites['SETTINGSBUTTONFRAME_ICON'].color = (iconColoring[0], iconColoring[1], iconColoring[2]); self.frameSprites['SETTINGSBUTTONFRAME'+'_ICON'].opacity = iconColoring[3]
                else:
                    self.images[displayBoxName] = self.imageManager.getImageByLoadIndex(self.images[displayBoxName][1])
                    self.frameSprites[displayBoxName].image = self.images[displayBoxName][0]
                    
        #Grid and Guide Lines & Text Update
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'].on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle)
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'].on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle)
        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT3'].on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['CONTENT_DEFAULT'], auxillaryTextStyles = self.effectiveTextStyle)
        self.displayBox_graphics['MAIN']['POSHIGHLIGHT_HOVERED'].color  = self.posHighlightColor_hovered
        self.displayBox_graphics['MAIN']['POSHIGHLIGHT_SELECTED'].color = self.posHighlightColor_selected
        self.displayBox_graphics['MAIN']['HORIZONTALGUIDELINE'].color   = self.guideColor
        self.displayBox_graphics['MAIN']['HORIZONTALGUIDETEXT'].on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['GUIDECONTENT'])
        for gridLineShape in self.displayBox_graphics['MAIN']['HORIZONTALGRID_LINES']:       gridLineShape.color = self.gridColor
        for gridLineShape in self.displayBox_graphics['MAIN']['VERTICALGRID_LINES']:         gridLineShape.color = self.gridColor
        for gridLineShape in self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_LINES']: gridLineShape.color = self.gridColor
        for gridLineText  in self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_TEXTS']: gridLineText.on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['GRID'])
        for gridLineShape in self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_LINES']:   gridLineShape.color = self.gridColor
        for gridLineText  in self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_TEXTS']:   gridLineText.on_GUIThemeUpdate(newDefaultTextStyle = self.effectiveTextStyle['GRID'])
        #Data Loading GaugeBar Related
        self.images['DATALOADINGCOVER'] = self.imageManager.getImageByLoadIndex(self.images['DATALOADINGCOVER'][1])
        self.frameSprites['DATALOADINGCOVER'].image = self.images['DATALOADINGCOVER'][0]
        self.dataLoadingGaugeBar.on_GUIThemeUpdate(**kwargs)
        self.dataLoadingTextBox_perc.on_GUIThemeUpdate(**kwargs)
        self.dataLoadingTextBox.on_GUIThemeUpdate(**kwargs)

        #Update Settings Subpage
        self.settingsSubPage.on_GUIThemeUpdate(**kwargs)
        
        #Update Configuration Objects Color
        self.settingsSubPage.GUIOs["LINECOLOR_LED"].updateColor(self.objectConfig['LINE_ColorR%{:s}'.format(self.currentGUITheme)], 
                                                                self.objectConfig['LINE_ColorG%{:s}'.format(self.currentGUITheme)], 
                                                                self.objectConfig['LINE_ColorB%{:s}'.format(self.currentGUITheme)], 
                                                                self.objectConfig['LINE_ColorA%{:s}'.format(self.currentGUITheme)])

        #Register redraw queues
        for _ts in self.data_Drawn: self.__dataDrawer_draw(timestamp = _ts)

    def on_LanguageUpdate(self, **kwargs):
        #Bring in updated textStyle
        newEffectiveTextStyle = self.visualManager.getTextStyle('dailyReportViewer_'+self.textStyle)
        for styleTarget in newEffectiveTextStyle: newEffectiveTextStyle[styleTarget]['font_size'] = self.effectiveTextStyle[styleTarget]['font_size']
        self.effectiveTextStyle = newEffectiveTextStyle
        
        #Grid and Guide Lines & Text Update
        for displayBoxName in self.displayBox:
            if (displayBoxName == 'MAIN'):
                self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT1'].on_LanguageUpdate(**kwargs)
                self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT2'].on_LanguageUpdate(**kwargs)
                self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT3'].on_LanguageUpdate(**kwargs)
                self.displayBox_graphics['MAIN']['HORIZONTALGUIDETEXT'].on_LanguageUpdate(**kwargs)
                for gridLineText  in self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_TEXTS']: gridLineText.on_LanguageUpdate(**kwargs)

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
        if (setterType == 'DISPLAYMODE'):
            selectedDisplayMode = self.settingsSubPage.GUIOs['DISPLAYMODE_SELECTIONBOX'].getSelected()
            self.data_DisplayMode = selectedDisplayMode
            if (self.simulationCode != None):
                self.__dataDrawer_RemoveDrawings() #Remove previous graphics
                self.__addBufferZone_toDrawQueue() #Update draw queue
            if ('DESCRIPTIONTEXT3' in self.displayBox_graphics['MAIN']): self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT3'].setText(self.visualManager.extractText(self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:{:s}'.format(selectedDisplayMode))))
            try:
                if (self.__checkVerticalExtremas() == True): self.__onVerticalExtremaUpdate()
                self.__editVVR_toExtremaCenter()
                self.__updatePosSelection(updateType = 1)
            except: pass
        elif (setterType == 'TIMEZONE'):
            selectedTimeZone = self.settingsSubPage.GUIOs['TIMEZONE_SELECTIONBOX'].getSelected()
            self.updateTimeZone(newTimeZone = selectedTimeZone)
            activateSaveConfigButton = True
        elif (setterType == 'SAVECONFIG'):
            self.sysFunc_editGUIOConfig(configName = self.name, targetContent = self.objectConfig.copy()); self.settingsSubPage.GUIOs["SAVECONFIGURATION"].deactivate()
        elif (setterType == 'Color'):
            contentType = guioName_split[1]
            self.settingsSubPage.GUIOs['LINECOLOR_LED'].updateColor(rValue = int(self.settingsSubPage.GUIOs['LINECOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                                    gValue = int(self.settingsSubPage.GUIOs['LINECOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                                    bValue = int(self.settingsSubPage.GUIOs['LINECOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                                    aValue = int(self.settingsSubPage.GUIOs['LINECOLOR_A_SLIDER'].getSliderValue()*255/100))
            self.settingsSubPage.GUIOs["LINECOLOR_{:s}_VALUE".format(contentType)].updateText(str(int(self.settingsSubPage.GUIOs['LINECOLOR_{:s}_SLIDER'.format(contentType)].getSliderValue()*255/100)))
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
            color_previous = (self.objectConfig['LINE_ColorR%{:s}'.format(self.currentGUITheme)],
                              self.objectConfig['LINE_ColorG%{:s}'.format(self.currentGUITheme)],
                              self.objectConfig['LINE_ColorB%{:s}'.format(self.currentGUITheme)],
                              self.objectConfig['LINE_ColorA%{:s}'.format(self.currentGUITheme)])
            color_r, color_g, color_b, color_a = self.settingsSubPage.GUIOs["LINECOLOR_LED"].getColor()
            self.objectConfig['LINE_ColorR%{:s}'.format(self.currentGUITheme)] = color_r
            self.objectConfig['LINE_ColorG%{:s}'.format(self.currentGUITheme)] = color_g
            self.objectConfig['LINE_ColorB%{:s}'.format(self.currentGUITheme)] = color_b
            self.objectConfig['LINE_ColorA%{:s}'.format(self.currentGUITheme)] = color_a
            if (color_previous != (color_r, color_g, color_b, color_a)): updateTracker = True
            #Queue Update
            if (updateTracker == True):
                self.__dataDrawer_RemoveDrawings() #Remove previous graphics
                self.__addBufferZone_toDrawQueue() #Update draw queue
            #Control Buttons Handling
            self.settingsSubPage.GUIOs['APPLYNEWSETTINGS'].deactivate()
            activateSaveConfigButton = True
        if ((activateSaveConfigButton == True) and (self.settingsSubPage.GUIOs["SAVECONFIGURATION"].deactivated == True)): self.settingsSubPage.GUIOs["SAVECONFIGURATION"].activate()

    def __addBufferZone_toDrawQueue(self):
        for timestamp in self.horizontalViewRange_timestampsInViewRange.union(self.horizontalViewRange_timestampsInBufferZone):
            if (timestamp in self.data_ForDisplay): self.data_DrawQueue.add(timestamp)
        
    def updateTimeZone(self, newTimeZone):
        self.objectConfig['TimeZone'] = newTimeZone
        if   (newTimeZone     == 'LOCAL'): self.timezoneDelta = -time.timezone
        elif (newTimeZone[:3] == 'UTC'):   self.timezoneDelta = int(newTimeZone.split("+")[1])*3600
        #Update vertical grid texts (Temporal Texts)
        for index in range (len(self.verticalGrid_intervals)):
            timestamp_display = self.verticalGrid_intervals[index] + self.timezoneDelta
            #Grid Text
            if (self.verticalGrid_intervalID <= 10):
                if (timestamp_display % 86400 != 0): dateStrFormat = "%H:%M"
                else:                                dateStrFormat = "%m/%d"
            else:
                if (atmEta_Auxillaries.isNewMonth(timestamp_display) == True): dateStrFormat = "%Y/%m"
                else:                                                          dateStrFormat = "%m/%d"
            self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_TEXTS'][index].setText(datetime.fromtimestamp(timestamp_display, tz = timezone.utc).strftime(dateStrFormat))
            self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_TEXTS'][index].moveTo(x = self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_TEXTS'][index].xPos)
    #Configuration Update Control END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Data Drawing --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __dataDrawer_draw(self, timestamp):
        try:
            if (self.__dataDrawer(timestamp = timestamp) == True): self.data_Drawn.add(timestamp)
        except Exception as e: print(termcolor.colored("An unexpected error occured while attempting to draw at {:d}\n *".format(timestamp), 'light_yellow'), termcolor.colored(e, 'light_yellow'))

    def __dataDrawer(self, timestamp):
        _dailyReport = self.data_ForDisplay[timestamp]
        _tsWidth = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = timestamp, mrktReg = None, nTicks = 1)-timestamp
        #Previous (if exists) drawing clearing
        self.displayBox_graphics['MAIN']['RCLCG'].removeShape(shapeName = timestamp, groupName = '1')
        self.displayBox_graphics['MAIN']['RCLCG'].removeShape(shapeName = timestamp, groupName = '2')
        #Color and Width
        color = (self.objectConfig['LINE_ColorR%{:s}'.format(self.currentGUITheme)],
                 self.objectConfig['LINE_ColorG%{:s}'.format(self.currentGUITheme)],
                 self.objectConfig['LINE_ColorB%{:s}'.format(self.currentGUITheme)],
                 self.objectConfig['LINE_ColorA%{:s}'.format(self.currentGUITheme)])
        lineWidth = self.objectConfig['LINE_Width']
        #Drawing
        _drawMethod = _DATADRAWER_DISPLAYMODE_DATADRAWMETHOD[self.data_DisplayMode]
        _drawType = _drawMethod[0]
        _dataCall = _drawMethod[1]
        #---DrawType 0
        if (_drawType == 0):
            #Color
            color1 = (int(color[0]/2), int(color[1]/2), int(color[2]/2), int(color[3]/2))
            color2 = color
            #X
            _tail_width = round(_tsWidth/5, 1)
            _tail_xPos  = round(timestamp+(_tsWidth-_tail_width)/2, 1)
            #Y1
            _d0 = _dailyReport[_dataCall[0]]
            _d1 = _dailyReport[_dataCall[1]]
            _d2 = _dailyReport[_dataCall[2]]
            _d3 = _dailyReport[_dataCall[3]]
            if (_d0 < _d3): _body_y1 = _d0; _body_height1 = _d3-_d0
            else:           _body_y1 = _d3; _body_height1 = _d0-_d3
            _tail_y1      = _d1
            _tail_height1 = _d2-_d1
            #Y2
            _d4 = _dailyReport[_dataCall[4]]
            _d5 = _dailyReport[_dataCall[5]]
            _d6 = _dailyReport[_dataCall[6]]
            _d7 = _dailyReport[_dataCall[7]]
            if (_d4 < _d7): _body_y2 = _d4; _body_height2 = _d7-_d4
            else:           _body_y2 = _d7; _body_height2 = _d4-_d7
            _tail_y2      = _d5
            _tail_height2 = _d6-_d5
            #Drawing
            if (0 < _body_height1): self.displayBox_graphics['MAIN']['RCLCG'].addShape_Rectangle(x = timestamp, y = _body_y1, width = _tsWidth, height = _body_height1, color = color1, shapeName = timestamp, shapeGroupName = '0', layerNumber = 1)
            else:                   self.displayBox_graphics['MAIN']['RCLCG'].addShape_Line(x = timestamp, y = _body_y1, x2 = timestamp+_tsWidth, y2 = _body_y1, color = color1, width_y = lineWidth/2, shapeName = timestamp, shapeGroupName = '0', layerNumber = 1)
            self.displayBox_graphics['MAIN']['RCLCG'].addShape_Rectangle(x = _tail_xPos, y = _tail_y1, width = _tail_width, height = _tail_height1, color = color1, shapeName = timestamp, shapeGroupName = '1', layerNumber = 2)
            if (0 < _body_height2): self.displayBox_graphics['MAIN']['RCLCG'].addShape_Rectangle(x = timestamp, y = _body_y2, width = _tsWidth, height = _body_height2, color = color2, shapeName = timestamp, shapeGroupName = '2', layerNumber = 1)
            else:                   self.displayBox_graphics['MAIN']['RCLCG'].addShape_Line(x = timestamp, y = _body_y2, x2 = timestamp+_tsWidth, y2 = _body_y2, color = color2, width_y = lineWidth/2, shapeName = timestamp, shapeGroupName = '2', layerNumber = 1)
            self.displayBox_graphics['MAIN']['RCLCG'].addShape_Rectangle(x = _tail_xPos, y = _tail_y2, width = _tail_width, height = _tail_height2, color = color2, shapeName = timestamp, shapeGroupName = '3', layerNumber = 2)
        #---DrawType 1
        elif (_drawType == 1):
            #X
            _tail_width = round(_tsWidth/5, 1)
            _tail_xPos  = round(timestamp+(_tsWidth-_tail_width)/2, 1)
            #Y
            _d0 = _dailyReport[_dataCall[0]]*100
            _d1 = _dailyReport[_dataCall[1]]*100
            _d2 = _dailyReport[_dataCall[2]]*100
            _d3 = _dailyReport[_dataCall[3]]*100
            if (_d0 < _d3): _body_y = _d0; _body_height = _d3-_d0
            else:           _body_y = _d3; _body_height = _d0-_d3
            _tail_y      = _d1
            _tail_height = _d2-_d1
            #Drawing
            if (0 < _body_height): self.displayBox_graphics['MAIN']['RCLCG'].addShape_Rectangle(x = timestamp, y = _body_y, width = _tsWidth, height = _body_height, color = color, shapeName = timestamp, shapeGroupName = '0', layerNumber = 1)
            else:                  self.displayBox_graphics['MAIN']['RCLCG'].addShape_Line(x = timestamp, y = _body_y, x2 = timestamp+_tsWidth, y2 = _body_y, color = color, width_y = lineWidth/2, shapeName = timestamp, shapeGroupName = '0', layerNumber = 1)
            self.displayBox_graphics['MAIN']['RCLCG'].addShape_Rectangle(x = _tail_xPos, y = _tail_y, width = _tail_width, height = _tail_height, color = color, shapeName = timestamp, shapeGroupName = '1', layerNumber = 2)
        #---DrawType 2
        elif (_drawType == 2):
            #Drawing
            self.displayBox_graphics['MAIN']['RCLCG'].addShape_Rectangle(x = timestamp, width = _tsWidth, y = 0, height = _dailyReport[_dataCall], color = color, shapeName = timestamp, shapeGroupName = '0', layerNumber = 1)
        return True
    
    def __dataDrawer_RemoveExpiredDrawings(self, timestamp):
        if (timestamp in self.data_Drawn):
            self.displayBox_graphics['MAIN']['RCLCG'].removeShape(shapeName = timestamp, groupName = '0')
            self.displayBox_graphics['MAIN']['RCLCG'].removeShape(shapeName = timestamp, groupName = '1')
            self.displayBox_graphics['MAIN']['RCLCG'].removeShape(shapeName = timestamp, groupName = '2')
            self.displayBox_graphics['MAIN']['RCLCG'].removeShape(shapeName = timestamp, groupName = '3')
            self.data_Drawn.remove(timestamp)
        
    def __dataDrawer_RemoveDrawings(self):
        self.displayBox_graphics['MAIN']['RCLCG'].removeGroup(groupName = '0')
        self.displayBox_graphics['MAIN']['RCLCG'].removeGroup(groupName = '1')
        self.displayBox_graphics['MAIN']['RCLCG'].removeGroup(groupName = '2')
        self.displayBox_graphics['MAIN']['RCLCG'].removeGroup(groupName = '3')
        self.data_Drawn.clear()
    #Data Drawing End ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #View Control ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    #[1]: Horizontal Position and Magnification
    #---ViewRange Control Params
    def __setHVRParams(self):
        nDataDisplayable_min = self.displayBox['MAIN'][2]*self.scaler / _GD_DISPLAYBOX_MAIN_MAXPIXELWIDTH
        nDataDisplayable_max = self.displayBox['MAIN'][2]*self.scaler / _GD_DISPLAYBOX_MAIN_MINPIXELWIDTH
        self.horizontalViewRangeWidth_min = nDataDisplayable_min * self.expectedKlineTemporalWidth
        self.horizontalViewRangeWidth_max = nDataDisplayable_max * self.expectedKlineTemporalWidth
        self.horizontalViewRangeWidth_m = (self.horizontalViewRangeWidth_min-self.horizontalViewRangeWidth_max)/(_GD_DISPLAYBOX_MAIN_HVR_MAXMAGNITUDE-_GD_DISPLAYBOX_MAIN_HVR_MINMAGNITUDE)
        self.horizontalViewRangeWidth_b = (self.horizontalViewRangeWidth_min*_GD_DISPLAYBOX_MAIN_HVR_MINMAGNITUDE-self.horizontalViewRangeWidth_max*_GD_DISPLAYBOX_MAIN_HVR_MAXMAGNITUDE)/(_GD_DISPLAYBOX_MAIN_HVR_MINMAGNITUDE-_GD_DISPLAYBOX_MAIN_HVR_MAXMAGNITUDE)

    #---Horizontal Position
    def __editHPosition(self, delta_drag = None, delta_scroll = None):
        if   (delta_drag   != None): effectiveDelta = -delta_drag*(self.horizontalViewRange[1]-self.horizontalViewRange[0])/self.displayBox_graphics['MAIN']['DRAWBOX'][2]
        elif (delta_scroll != None): effectiveDelta = -delta_scroll*self.expectedKlineTemporalWidth
        hVR_new = [round(self.horizontalViewRange[0]+effectiveDelta), round(self.horizontalViewRange[1]+effectiveDelta)]
        #Above-Zero Container
        if (hVR_new[0] < 0): hVR_new = [0, hVR_new[1]-hVR_new[0]]
        self.horizontalViewRange = hVR_new
        self.__onHViewRangeUpdate(0)
        
    #---Horizontal Magnification
    def __editHMagFactor(self, delta_drag = None, delta_scroll = None):
        if   (delta_drag   != None): newMagnitudeFactor = self.horizontalViewRange_magnification - delta_drag*200/self.displayBox_graphics['MAIN']['DRAWBOX'][2]
        elif (delta_scroll != None): newMagnitudeFactor = self.horizontalViewRange_magnification + delta_scroll
        #Rounding
        newMagnitudeFactor = round(newMagnitudeFactor, 1)
        if   (newMagnitudeFactor < _GD_DISPLAYBOX_MAIN_HVR_MINMAGNITUDE): newMagnitudeFactor = _GD_DISPLAYBOX_MAIN_HVR_MINMAGNITUDE
        elif (_GD_DISPLAYBOX_MAIN_HVR_MAXMAGNITUDE < newMagnitudeFactor): newMagnitudeFactor = _GD_DISPLAYBOX_MAIN_HVR_MAXMAGNITUDE
        #Variation Check and response
        if (newMagnitudeFactor != self.horizontalViewRange_magnification):
            self.horizontalViewRange_magnification = newMagnitudeFactor
            hVR_new = (round(self.horizontalViewRange[1]-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b)), self.horizontalViewRange[1])
            if (hVR_new[0] < 0): hVR_new = [0, hVR_new[1]-hVR_new[0]]
            self.horizontalViewRange = hVR_new
            self.__onHViewRangeUpdate(1)
            
    #---Post Horizontal View-Range Update
    def __onHViewRangeUpdate(self, updateType):
        #[1]: Update Process Queue
        self._onHViewRangeUpdate_UpdateProcessQueue()
        #[2]: Update RCLCGs
        self.__onHViewRangeUpdate_UpdateRCLCGs()
        #[3]: Update Grids
        self.__onHViewRangeUpdate_UpdateGrids(updateType)
        #[4}: Find new vertical extrema within the new horizontalViewRange
        if (self.__checkVerticalExtremas() == True): self.__onVerticalExtremaUpdate()
        #[5]: Update PosSelection
        self.__updatePosSelection(updateType = 1)
        
    def _onHViewRangeUpdate_UpdateProcessQueue(self):
        #[1]: Update Target Timestamps (Within ViewRange & BufferZone)
        self.horizontalViewRange_timestampsInViewRange = set(atmEta_Auxillaries.getTimestampList_byRange(self.intervalID, self.horizontalViewRange[0], self.horizontalViewRange[1], lastTickInclusive = True))
        nTSsInViewRange = len(self.horizontalViewRange_timestampsInViewRange)
        timestampsInBufferZone1 = set(atmEta_Auxillaries.getTimestampList_byNTicks(self.intervalID, self.horizontalViewRange[0], nTicks = int(nTSsInViewRange*_GD_DISPLAYBOX_HVR_BACKWARDBUFFERFACTOR)+1, direction = False, mrktReg = None)[1:])
        timestampsInBufferZone2 = set(atmEta_Auxillaries.getTimestampList_byNTicks(self.intervalID, self.horizontalViewRange[1], nTicks = int(nTSsInViewRange*_GD_DISPLAYBOX_HVR_FORWARDBUFFERFACTOR) +1, direction = True,  mrktReg = None)[1:])
        self.horizontalViewRange_timestampsInBufferZone = timestampsInBufferZone1.union(timestampsInBufferZone2)
        #[2]: Determine which targets to draw and update the drawQueue
        for timestamp in self.horizontalViewRange_timestampsInViewRange.union(self.horizontalViewRange_timestampsInBufferZone):
            if ((timestamp in self.data_ForDisplay) and (timestamp not in self.data_Drawn)): self.data_DrawQueue.add(timestamp)
        #[3]: Update Draw Removal Queue
        self.data_DrawRemovalQueue = [ts for ts in self.data_Drawn if ((ts not in self.horizontalViewRange_timestampsInViewRange) and (ts not in self.horizontalViewRange_timestampsInBufferZone))]

    def __onHViewRangeUpdate_UpdateRCLCGs(self):
        self.displayBox_graphics['MAIN']['RCLCG'].updateProjection(projection_x0 = self.horizontalViewRange[0], projection_x1 = self.horizontalViewRange[1])
        self.displayBox_graphics['MAIN']['RCLCG_YFIXED'].updateProjection(projection_x0 = self.horizontalViewRange[0], projection_x1 = self.horizontalViewRange[1])
            
    def __onHViewRangeUpdate_UpdateGrids(self, updateType):
        #[1]: Determine Vertical Grid Intervals
        gridContentsUpdateFlag = False
        if (updateType == 1):
            for gridIntervalID in atmEta_Auxillaries.GRID_INTERVAL_IDs[self.intervalID:]:
                rightEnd = atmEta_Auxillaries.getNextIntervalTickTimestamp_GRID(gridIntervalID, self.horizontalViewRange[1], mrktReg = None, nTicks = 1)
                verticalGrid_intervals = atmEta_Auxillaries.getTimestampList_byRange_GRID(gridIntervalID, self.horizontalViewRange[0], rightEnd, mrktReg = None, lastTickInclusive = True)
                if (len(verticalGrid_intervals)+1 < self.nMaxVerticalGridLines): break
            self.verticalGrid_intervalID = gridIntervalID
            gridContentsUpdateFlag = True
        elif (updateType == 0):
            rightEnd = atmEta_Auxillaries.getNextIntervalTickTimestamp_GRID(self.verticalGrid_intervalID, self.horizontalViewRange[1], mrktReg = None, nTicks = 1)
            verticalGrid_intervals = atmEta_Auxillaries.getTimestampList_byRange_GRID(self.verticalGrid_intervalID, self.horizontalViewRange[0], rightEnd, mrktReg = None, lastTickInclusive = True)
            if ((self.verticalGrid_intervals[0] != verticalGrid_intervals[0]) or (self.verticalGrid_intervals[-1] != verticalGrid_intervals[-1])): gridContentsUpdateFlag = True

        #[2]: Update Grid Position & Text
        pixelPerTS = self.displayBox_graphics['MAINGRID_X']['DRAWBOX'][2]*self.scaler / (self.horizontalViewRange[1]-self.horizontalViewRange[0])
        if (gridContentsUpdateFlag == True):
            self.verticalGrid_intervals = verticalGrid_intervals
            for index in range (self.nMaxVerticalGridLines):
                if (index < len(self.verticalGrid_intervals)):
                    timestamp = self.verticalGrid_intervals[index]
                    timestamp_display = timestamp + self.timezoneDelta
                    xPos_Line = round((timestamp-self.verticalGrid_intervals[0])*pixelPerTS, 1)
                    #[1]: MAIN
                    self.displayBox_graphics['MAIN']['VERTICALGRID_LINES'][index].x = xPos_Line; self.displayBox_graphics['MAIN']['VERTICALGRID_LINES'][index].x2 = xPos_Line
                    if (self.displayBox_graphics['MAIN']['VERTICALGRID_LINES'][index].visible == False): self.displayBox_graphics['MAIN']['VERTICALGRID_LINES'][index].visible = True
                    #[2]: MAINGRID_X
                    #---GridLines
                    self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_LINES'][index].x = xPos_Line; self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_LINES'][index].x2 = xPos_Line
                    if (self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_LINES'][index].visible == False): self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_LINES'][index].visible = True
                    #---Grid Texts
                    if (self.verticalGrid_intervalID <= 10):
                        if (timestamp_display % 86400 != 0): dateStrFormat = "%H:%M"
                        else:                                dateStrFormat = "%m/%d"
                    else:
                        if (atmEta_Auxillaries.isNewMonth(timestamp_display) == True): dateStrFormat = "%Y/%m"
                        else:                                                          dateStrFormat = "%m/%d"
                    self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_TEXTS'][index].setText(datetime.fromtimestamp(timestamp_display, tz = timezone.utc).strftime(dateStrFormat))
                    self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_TEXTS'][index].moveTo(x = round((xPos_Line)/self.scaler-_GD_DISPLAYBOX_GRID_VERTICALTEXTWIDTH/2))
                    if (self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_TEXTS'][index].hidden == True): self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_TEXTS'][index].show()
                else:
                    #[1]: MAIN
                    if (self.displayBox_graphics['MAIN']['VERTICALGRID_LINES'][index].visible       == True): self.displayBox_graphics['MAIN']['VERTICALGRID_LINES'][index].visible       = False
                    #[2]: MAINGRID_X
                    if (self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_LINES'][index].visible == True): self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_LINES'][index].visible = False
                    if (self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_TEXTS'][index].hidden == False): self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_TEXTS'][index].hide()

        #Update Grid CamGroup Projections
        projectionX0 = (self.horizontalViewRange[0]-self.verticalGrid_intervals[0])*pixelPerTS
        projectionX1 = projectionX0+self.displayBox_graphics['MAINGRID_X']['DRAWBOX'][2]*self.scaler
        self.displayBox_graphics['MAIN']['VERTICALGRID_CAMGROUP'].updateProjection(projection_x0=projectionX0, projection_x1=projectionX1)       #MAIN
        self.displayBox_graphics['MAINGRID_X']['VERTICALGRID_CAMGROUP'].updateProjection(projection_x0=projectionX0, projection_x1=projectionX1) #MAINGRID_X
        return

    def __checkVerticalExtremas(self):
        valMin = float('inf')
        valMax = float('-inf')
        for _ts in self.horizontalViewRange_timestampsInViewRange:
            if (_ts in self.data_ForDisplay):
                #Values Collection
                _dailyReport = self.data_ForDisplay[_ts]
                if   (self.data_DisplayMode == 'BALANCE'):        values = [_dailyReport['marginBalance_min'], _dailyReport['marginBalance_max'], _dailyReport['walletBalance_min'], _dailyReport['walletBalance_max']]
                elif (self.data_DisplayMode == 'COMMITMENTRATE'): values = [_dailyReport['commitmentRate_min']*100, _dailyReport['commitmentRate_max']*100]
                elif (self.data_DisplayMode == 'RISKLEVEL'):      values = [_dailyReport['riskLevel_min']*100, _dailyReport['riskLevel_max']*100]
                elif (self.data_DisplayMode == 'NTRADES_TOTAL'):  values = [_dailyReport['nTrades'],]
                elif (self.data_DisplayMode == 'NTRADES_BUY'):    values = [_dailyReport['nTrades_buy'],]
                elif (self.data_DisplayMode == 'NTRADES_SELL'):   values = [_dailyReport['nTrades_sell'],]
                elif (self.data_DisplayMode == 'NTRADES_PSL'):    values = [_dailyReport['nTrades_psl'],]
                elif (self.data_DisplayMode == 'NLIQUIDATIONS'):  values = [_dailyReport['nLiquidations'],]
                #Extrema Finding
                if (0 < len(values)):
                    values_min = min(values)
                    values_max = max(values)
                    if (values_min < valMin): valMin = values_min
                    if (valMax < values_max): valMax = values_max
        #New Vertical Extremas Handling
        if (((valMin != float('inf')) and (valMax != float('-inf'))) and ((self.verticalValue_min != valMin) or (self.verticalValue_max != valMax))): #The found extremas are different
            if (valMin == valMax):
                self.verticalValue_min = valMin-1
                self.verticalValue_max = valMax+1
            else:
                self.verticalValue_min = valMin
                self.verticalValue_max = valMax
            return True
        else: return False

    def __onVerticalExtremaUpdate(self, updateType = 0):
        verticalExtremaDelta = self.verticalValue_max-self.verticalValue_min
        newViewRangeHeight_min = verticalExtremaDelta*100/_GD_DISPLAYBOX_VVR_MAGNITUDE_MAX
        newViewRangeHeight_max = verticalExtremaDelta*100/_GD_DISPLAYBOX_VVR_MAGNITUDE_MIN
        if (updateType == 0):
            previousViewRangeCenter = (self.verticalViewRange[0]+self.verticalViewRange[1])/2
            previousViewRangeHeight = self.verticalViewRange[1]-self.verticalViewRange[0]
            if   (previousViewRangeHeight < newViewRangeHeight_min): vVR_effective = [previousViewRangeCenter-newViewRangeHeight_min*0.5, previousViewRangeCenter+newViewRangeHeight_min*0.5]; self.verticalViewRange_magnification = _GD_DISPLAYBOX_VVR_MAGNITUDE_MAX
            elif (newViewRangeHeight_max < previousViewRangeHeight): vVR_effective = [previousViewRangeCenter-newViewRangeHeight_max*0.5, previousViewRangeCenter+newViewRangeHeight_max*0.5]; self.verticalViewRange_magnification = _GD_DISPLAYBOX_VVR_MAGNITUDE_MIN
            else:                                                    vVR_effective = self.verticalViewRange;                                                                                   self.verticalViewRange_magnification = round(verticalExtremaDelta/previousViewRangeHeight*100, 1)
            self.verticalViewRange = [round(vVR_effective[0], self.verticalViewRange_precision), round(vVR_effective[1], self.verticalViewRange_precision)]
            if (previousViewRangeHeight == self.verticalViewRange[1]-self.verticalViewRange[0]): self.__onVViewRangeUpdate(0)
            else:                                                                                self.__onVViewRangeUpdate(1)
        elif (updateType == 1):
            extremaCenter = (self.verticalValue_min+self.verticalValue_max)/2
            self.verticalViewRange_magnification = _GD_DISPLAYBOX_VVR_MAGNITUDE_MAX
            self.verticalViewRange = [round(extremaCenter-newViewRangeHeight_min*0.5, self.verticalViewRange_precision), round(extremaCenter+newViewRangeHeight_min*0.5, self.verticalViewRange_precision)]
            self.__onVViewRangeUpdate(1)
        
    #[2]: Vertical Position and Magnification
    #---Vertical Position
    def __editVPosition(self, delta_drag = None, delta_scroll = None):
        if   (delta_drag   != None): effectiveDelta = -delta_drag  *(self.verticalViewRange[1]-self.verticalViewRange[0])/self.displayBox_graphics['MAIN']['DRAWBOX'][3]
        elif (delta_scroll != None): effectiveDelta = -delta_scroll*(self.verticalViewRange[1]-self.verticalViewRange[0])/50
        vVR_effective = [self.verticalViewRange[0]+effectiveDelta, self.verticalViewRange[1]+effectiveDelta]
        self.verticalViewRange = vVR_effective
        self.__onVViewRangeUpdate(0)
        
    #---Vertical Magnification
    def __editVMagFactor(self, delta_drag = None, delta_scroll = None, anchor = 'CENTER'):
        if   (delta_drag   != None): newMagnitudeFactor = self.verticalViewRange_magnification + delta_drag*200/self.displayBox_graphics['MAIN']['DRAWBOX'][3]
        elif (delta_scroll != None): newMagnitudeFactor = self.verticalViewRange_magnification + delta_scroll
        #Rounding
        newMagnitudeFactor = round(newMagnitudeFactor, 1)
        #Boundary Control
        if   (newMagnitudeFactor < _GD_DISPLAYBOX_VVR_MAGNITUDE_MIN): newMagnitudeFactor = _GD_DISPLAYBOX_VVR_MAGNITUDE_MIN
        elif (_GD_DISPLAYBOX_VVR_MAGNITUDE_MAX < newMagnitudeFactor): newMagnitudeFactor = _GD_DISPLAYBOX_VVR_MAGNITUDE_MAX
        #Variation Check and response
        if (newMagnitudeFactor != self.verticalViewRange_magnification):
            #Calculate new viewRange
            self.verticalViewRange_magnification = newMagnitudeFactor
            verticalExtremaDelta = self.verticalValue_max-self.verticalValue_min
            verticalExtremaDelta_magnified = verticalExtremaDelta*100/self.verticalViewRange_magnification
            if (anchor == 'CENTER'):
                vVRCenter = (self.verticalViewRange[0]+self.verticalViewRange[1])/2
                vVR_effective = [vVRCenter-verticalExtremaDelta_magnified*0.5, vVRCenter+verticalExtremaDelta_magnified*0.5]
            elif (anchor == 'BOTTOM'): vVR_effective = [self.verticalViewRange[0], self.verticalViewRange[0]+verticalExtremaDelta_magnified]
            elif (anchor == 'TOP'):    vVR_effective = [self.verticalViewRange[1]-verticalExtremaDelta_magnified, self.verticalViewRange[1]]
            self.verticalViewRange = [round(vVR_effective[0], self.verticalViewRange_precision), round(vVR_effective[1], self.verticalViewRange_precision)]
            self.__onVViewRangeUpdate(1)
            
    #---Reset vVR_price
    def __editVVR_toExtremaCenter(self, extension_b = 0.1, extension_t = 0.1):
        #Extension Limit Control
        if (extension_b < 0): extension_b = 0
        if (extension_t < 0): extension_t = 0
        extensionLimit_min = (100/_GD_DISPLAYBOX_VVR_MAGNITUDE_MAX)-1
        extensionLimit_max = (100/_GD_DISPLAYBOX_VVR_MAGNITUDE_MIN)-1
        extensionSum = extension_b + extension_t
        if ((extensionLimit_min <= extensionSum) and (extensionSum <= extensionLimit_max)):
            extension_b = extension_b
            extension_t = extension_t
        else:
            extensionSumScaler = extensionSum / extensionLimit_max
            extension_b = extension_b / extensionSumScaler
            extension_t = extension_t / extensionSumScaler
        #ViewRange and new Magnification Computation
        verticalExtremaCenter = (self.verticalValue_min+self.verticalValue_max)/2
        verticalExtremaDelta = self.verticalValue_max-self.verticalValue_min
        if (verticalExtremaDelta == 0):
            verticalExtremaDelta = 1
            vVR_effective = [-verticalExtremaDelta*0.5, verticalExtremaDelta*0.5]
        else:
            verticalExtremaDelta_b = verticalExtremaDelta*(0.5+extension_b)
            verticalExtremaDelta_t = verticalExtremaDelta*(0.5+extension_t)
            vVR_effective = [verticalExtremaCenter-verticalExtremaDelta_b, verticalExtremaCenter+verticalExtremaDelta_t]
        self.verticalViewRange = [vVR_effective[0], vVR_effective[1]]
        self.verticalViewRange_magnification = round(verticalExtremaDelta/(vVR_effective[1]-vVR_effective[0])*100, 1)
        self.__onVViewRangeUpdate(1)
        
    #---Post Vertical ViewRange Update
    def __onVViewRangeUpdate(self, updateType):
        #Update RCLCGs
        self.displayBox_graphics['MAIN']['RCLCG'].updateProjection(projection_y0 = self.verticalViewRange[0], projection_y1 = self.verticalViewRange[1])
        self.displayBox_graphics['MAIN']['RCLCG_XFIXED'].updateProjection(projection_y0 = self.verticalViewRange[0], projection_y1 = self.verticalViewRange[1])

        #Horizontal Grid Lines
        gridContentsUpdateFlag = False
        if (updateType == 1):
            viewRangeHeight = self.verticalViewRange[1]-self.verticalViewRange[0]
            viewRangeHeight_OOM = math.floor(math.log(viewRangeHeight, 10))
            for intervalFactor in (0.1, 0.25, 0.5, 0.75, 1, 2.5, 5, 7.5):
                intervalHeight = intervalFactor*pow(10, viewRangeHeight_OOM)
                if (intervalHeight == 0): return # <--- Temporary fix
                bottomEnd = int(self.verticalViewRange[0]/intervalHeight)    *intervalHeight
                topEnd    = (int(self.verticalViewRange[1]/intervalHeight)+1)*intervalHeight
                nIntervals = int((topEnd-bottomEnd)/intervalHeight)+1
                if (nIntervals+1 <= self.nMaxHorizontalGridLines): 
                    horizontalGridIntervals = list()
                    value = bottomEnd
                    while (value <= topEnd): horizontalGridIntervals.append(value); value += intervalHeight
                    self.horizontalGridIntervalHeight = intervalHeight
                    break
            gridContentsUpdateFlag = True
        elif (updateType == 0):
            bottomEnd = int(self.verticalViewRange[0]/self.horizontalGridIntervalHeight)*self.horizontalGridIntervalHeight
            topEnd    = (int(self.verticalViewRange[1]/self.horizontalGridIntervalHeight)+1)*self.horizontalGridIntervalHeight
            if ((self.horizontalGridIntervals[0] != bottomEnd) or (self.horizontalGridIntervals[-1] != topEnd)):
                horizontalGridIntervals = list()
                value = bottomEnd
                while (value <= topEnd): horizontalGridIntervals.append(value); value += self.horizontalGridIntervalHeight
                gridContentsUpdateFlag = True
                
        pixelPerUnitHeight = self.displayBox_graphics['MAIN']['DRAWBOX'][3]*self.scaler / (self.verticalViewRange[1]-self.verticalViewRange[0])
        if (gridContentsUpdateFlag == True):
            self.horizontalGridIntervals = horizontalGridIntervals
            for index in range (self.nMaxHorizontalGridLines):
                if (index < len(self.horizontalGridIntervals)):
                    verticalValue = self.horizontalGridIntervals[index]
                    yPos_Line = round((verticalValue-self.horizontalGridIntervals[0])*pixelPerUnitHeight, 1)
                    #Grid Lines
                    self.displayBox_graphics['MAIN']['HORIZONTALGRID_LINES'][index].y       = yPos_Line;         self.displayBox_graphics['MAIN']['HORIZONTALGRID_LINES'][index].y2       = yPos_Line
                    self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_LINES'][index].y = yPos_Line;         self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_LINES'][index].y2 = yPos_Line
                    if (self.displayBox_graphics['MAIN']['HORIZONTALGRID_LINES'][index].visible       == False): self.displayBox_graphics['MAIN']['HORIZONTALGRID_LINES'][index].visible       = True
                    if (self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_LINES'][index].visible == False): self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_LINES'][index].visible = True
                    #Grid Text
                    if (verticalValue == 0): verticalValue_formatted = "0"
                    else:                    verticalValue_formatted = atmEta_Auxillaries.simpleValueFormatter(value = verticalValue, precision = 2)
                    self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_TEXTS'][index].setText(verticalValue_formatted)
                    self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_TEXTS'][index].moveTo(y = round((yPos_Line)/self.scaler-_GD_DISPLAYBOX_GRID_HORIZONTALTEXTHEIGHT/2))
                    if (self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_TEXTS'][index].hidden == True): self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_TEXTS'][index].show()
                else:
                    if (self.displayBox_graphics['MAIN']['HORIZONTALGRID_LINES'][index].visible == True):       self.displayBox_graphics['MAIN']['HORIZONTALGRID_LINES'][index].visible = False
                    if (self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_LINES'][index].visible == True): self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_LINES'][index].visible = False
                    if (self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_TEXTS'][index].hidden == False): self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_TEXTS'][index].hide()
        projectionY0 = (self.verticalViewRange[0]-self.horizontalGridIntervals[0])*pixelPerUnitHeight
        projectionY1 = projectionY0+self.displayBox_graphics['MAIN']['DRAWBOX'][3]*self.scaler
        self.displayBox_graphics['MAIN']['HORIZONTALGRID_CAMGROUP'].updateProjection(projection_y0=projectionY0, projection_y1=projectionY1)
        self.displayBox_graphics['MAINGRID_Y']['HORIZONTALGRID_CAMGROUP'].updateProjection(projection_y0=projectionY0, projection_y1=projectionY1)
    #View Control END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    


    #Targe Data -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def setTarget(self, target):
        if (target == None):
            self.simulationCode   = None
            self.simulation       = None
            self.assetName        = None
            self.targetPrecisions = None
            self.data_FetchComplete = False
            self.data_Fetching      = False
            self.data_Fetching_RID = None
            self.frameSprites['DATALOADINGCOVER'].visible = False
            self.dataLoadingGaugeBar.hide()
            self.dataLoadingTextBox.hide()
            self.dataLoadingTextBox_perc.hide()
            self.data_ForDisplay       = dict()
            self.data_DrawQueue        = set()
            self.data_Drawn            = set()
            self.data_DrawRemovalQueue = set()
        else:
            self.simulationCode   = target[0]
            self.assetName        = target[1]
            self.simulation       = self.ipcA.getPRD(processName = 'SIMULATIONMANAGER', prdAddress = ('SIMULATIONS', self.simulationCode))
            self.targetPrecisions = 1
            self.data_FetchComplete = False
            self.data_Fetching      = True
            self.data_Fetching_RID = self.ipcA.sendFAR(targetProcess = 'DATAMANAGER', functionID = 'fetchSimulationDailyReports', functionParams = {'simulationCode': self.simulationCode}, farrHandler = self.__setTarget_onDailyReportsFetchResponse_FARR)
            self.frameSprites['DATALOADINGCOVER'].visible = True
            self.dataLoadingGaugeBar.show()
            self.dataLoadingTextBox.show()
            self.dataLoadingTextBox_perc.show()
            self.dataLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_DAILYREPORTVIEWER:FETCHINGDAILYREPORTS'))
            self.dataLoadingTextBox_perc.updateText("-")
            self.data_ForDisplay       = dict()
            self.data_DrawQueue        = set()
            self.data_Drawn            = set()
            self.data_DrawRemovalQueue = set()
        self.__dataDrawer_RemoveDrawings()

    def __setTarget_onDailyReportsFetchResponse_FARR(self, responder, requestID, functionResult):
        if (responder == 'DATAMANAGER'):
            _result         = functionResult['result']
            _simulationCode = functionResult['simulationCode']
            _dailyReports   = functionResult['dailyReports']
            _failureType    = functionResult['failureType']
            if ((_simulationCode == self.simulationCode) and (requestID == self.data_Fetching_RID)):
                if (_result == True):
                    #Generate display data
                    for _ts in _dailyReports: self.data_ForDisplay[_ts] = _dailyReports[_ts][self.assetName]
                    #Fetch Completion Handling
                    #---Fetch Control
                    self.data_FetchComplete = True
                    self.data_Fetching      = False
                    self.frameSprites['DATALOADINGCOVER'].visible = False
                    self.dataLoadingGaugeBar.hide()
                    self.dataLoadingTextBox.hide()
                    self.dataLoadingTextBox_perc.hide()
                    #---ViewRange
                    self.horizontalViewRange_magnification = _GD_DISPLAYBOX_MAIN_HVR_MINMAGNITUDE
                    self.horizontalViewRange = [self.simulation['simulationRange'][0], None]
                    self.horizontalViewRange[1] = round(self.horizontalViewRange[0]+(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
                    self.__onHViewRangeUpdate(1)
                    self.__editVVR_toExtremaCenter()
                    #---Draw Queue
                    for _ts in self.data_ForDisplay:
                        t_open  = _ts
                        t_close = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = t_open, mrktReg = None, nTicks = 1)-1
                        classification = 0
                        classification += 0b1000*(0 <= t_open -self.horizontalViewRange[0])
                        classification += 0b0100*(0 <= t_open -self.horizontalViewRange[1])
                        classification += 0b0010*(0 <  t_close-self.horizontalViewRange[0])
                        classification += 0b0001*(0 <  t_close-self.horizontalViewRange[1])
                        if ((classification == 0b0010) or (classification == 0b1010) or (classification == 0b1011) or (classification == 0b0011)): self.data_DrawQueue.add(t_open)
                else:
                    print(termcolor.colored("[GUI-{:s}] A failure returned from DATAMANAGER while attempting to fetch tradeLog for simulation '{:s}'.\n *".format(str(self.name), _simulationCode), 'light_red'), termcolor.colored(_failureType, 'light_red'))
                    self.data_Fetching_RID = None
    #Kline Data END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def getGroupRequirement(): return 30
#'tradeLogViewer' END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

