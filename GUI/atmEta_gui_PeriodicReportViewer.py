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
import itertools
import bisect

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

_GD_DISPLAYBOX_MAIN_MINPIXELWIDTH    = 0.5
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

_VVR_PRECISIONUPDATETHRESHOLD = 2
_VVR_PRECISIONCOMPENSATOR     = -2
_VVR_HGLCENTER                = 0

_TIMEINTERVAL_MOUSEINTERPRETATION_NS = 10e6
_TIMEINTERVAL_POSTDRAGWAITTIME       = 500e6
_TIMEINTERVAL_POSTSCROLLWAITTIME     = 500e6
_TIMEINTERVAL_POSHIGHLIGHTUPDATE     = 10e6

_TIMELIMIT_DRAWQUEUE_NS       = 10e6
_TIMELIMIT_RCLCGPROCESSING_NS = 10e6
_TIMELIMIT_DRAWREMOVAL_NS     = 10e6

_GD_LOADINGGAUGEBAR_HEIGHT = 150

_DESCRIPTIONTEXT_DISPLAYMODE_VERTICALVALUE_FORMATTINGMODE = {'BALANCE':             0,
                                                             'COMMITMENTRATE':      1,
                                                             'RISKLEVEL':           1,
                                                             'NTRADES_TOTAL':       2,
                                                             'NTRADES_BUY':         2,
                                                             'NTRADES_SELL':        2,
                                                             'NTRADES_ENTRY':       2,
                                                             'NTRADES_CLEAR':       2,
                                                             'NTRADES_EXIT':        2,
                                                             'NTRADES_FSLIMMED':    2,
                                                             'NTRADES_FSLCLOSE':    2,
                                                             'NTRADES_LIQUIDATION': 2,
                                                             'NTRADES_FORCECLEAR':  2,
                                                             'NTRADES_UNKNOWN':     2,
                                                             'NTRADES_GAIN':        2,
                                                             'NTRADES_LOSS':        2,
                                                            }
_DATADRAWER_DISPLAYMODE_DATADRAWMETHOD = {'BALANCE':             (0, ('marginBalance_open', 'marginBalance_min', 'marginBalance_max', 'marginBalance_close', 'walletBalance_open', 'walletBalance_min', 'walletBalance_max', 'walletBalance_close')),
                                          'COMMITMENTRATE':      (1, ('commitmentRate_open', 'commitmentRate_min', 'commitmentRate_max', 'commitmentRate_close')),
                                          'RISKLEVEL':           (1, ('riskLevel_open', 'riskLevel_min', 'riskLevel_max', 'riskLevel_close')),
                                          'NTRADES_TOTAL':       (2, 'nTrades'),
                                          'NTRADES_BUY':         (2, 'nTrades_buy'),
                                          'NTRADES_SELL':        (2, 'nTrades_sell'),
                                          'NTRADES_ENTRY':       (2, 'nTrades_entry'),
                                          'NTRADES_CLEAR':       (2, 'nTrades_clear'),
                                          'NTRADES_EXIT':        (2, 'nTrades_exit'),
                                          'NTRADES_FSLIMMED':    (2, 'nTrades_fslImmed'),
                                          'NTRADES_FSLCLOSE':    (2, 'nTrades_fslClose'),
                                          'NTRADES_LIQUIDATION': (2, 'nTrades_liquidation'),
                                          'NTRADES_FORCECLEAR':  (2, 'nTrades_forceClear'),
                                          'NTRADES_UNKNOWN':     (2, 'nTrades_unknown'),
                                          'NTRADES_GAIN':        (2, 'nTrades_gain'),
                                          'NTRADES_LOSS':        (2, 'nTrades_loss'),
                                          }
_DATADRAWER_DISPLAYMODE_VERTICALEXTREMACHECKMODE = {'BALANCE':        (['marginBalance_min', 'marginBalance_max', 'walletBalance_min', 'walletBalance_max'], 1),
                                                    'COMMITMENTRATE': (['commitmentRate_min', 'commitmentRate_max'], 100),
                                                    'RISKLEVEL':      (['riskLevel_min', 'riskLevel_max'],           100),
                                                    'NTRADES_TOTAL':       (['nTrades',],             1),
                                                    'NTRADES_BUY':         (['nTrades_buy',],         1),
                                                    'NTRADES_SELL':        (['nTrades_sell',],        1),
                                                    'NTRADES_ENTRY':       (['nTrades_entry',],       1),
                                                    'NTRADES_CLEAR':       (['nTrades_clear',],       1),
                                                    'NTRADES_EXIT':        (['nTrades_exit',],        1),
                                                    'NTRADES_FSLIMMED':    (['nTrades_fslImmed',],    1),
                                                    'NTRADES_FSLCLOSE':    (['nTrades_fslClose',],    1),
                                                    'NTRADES_LIQUIDATION': (['nTrades_liquidation',], 1),
                                                    'NTRADES_FORCECLEAR':  (['nTrades_forceClear',],  1),
                                                    'NTRADES_UNKNOWN':     (['nTrades_unknown',],     1),
                                                    'NTRADES_GAIN':        (['nTrades_gain',],        1),
                                                    'NTRADES_LOSS':        (['nTrades_loss',],        1),
                                                   }


#'periodicReportViewer' -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class periodicReportViewer:
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
        self.effectiveTextStyle = self.visualManager.getTextStyle('periodicReportViewer_'+self.textStyle)
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
            self.images['DATALOADINGCOVER'] = self.imageManager.getImageByCode("periodicReportViewer_typeA_"+self.style+"_dataLoadingCover", self.width*self.scaler, self.height*self.scaler)
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
        self.target    = None
        self.assetName = None
        self.periodicReports                    = dict()
        self.periodicReports_display            = dict()
        self.periodicReports_display_timestamps = list()
        self.displayMode = 'BALANCE'
        self.fetchComplete = True
        self.fetching      = False
        self.fetching_RID  = None
        self.drawQueue        = set()
        self.drawn            = set()
        self.drawRemovalQueue = set()
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
        self.gridColor       = self.visualManager.getFromColorTable('PERIODICREPORTVIEWER_GRID')
        self.gridColor_Heavy = self.visualManager.getFromColorTable('PERIODICREPORTVIEWER_GRIDHEAVY')
        self.guideColor      = self.visualManager.getFromColorTable('PERIODICREPORTVIEWER_GUIDECONTENT')
        self.posHighlightColor_hovered  = self.visualManager.getFromColorTable('PERIODICREPORTVIEWER_POSHOVERED')
        self.posHighlightColor_selected = self.visualManager.getFromColorTable('PERIODICREPORTVIEWER_POSSELECTED')
        
        #<Horizontal ViewRange & Vertical Grid>
        #---Horizontal ViewRange
        self.intervalID = 11
        self.expectedKlineTemporalWidth = _EXPECTEDTEMPORALWIDTHS[self.intervalID]
        self.horizontalViewRangeWidth_min = None; self.horizontalViewRangeWidth_max = None
        self.horizontalViewRangeWidth_m = None;   self.horizontalViewRangeWidth_b = None
        self.horizontalViewRange = [None, None]
        self.horizontalViewRange_timestampsInViewRange  = list()
        self.horizontalViewRange_timestampsInBufferZone = list()
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
        self.verticalViewRange_precision = 0
        #---Horizontal Grid
        self.horizontalGridIntervals      = list()
        self.horizontalGridIntervalHeight = None
        self.nMaxHorizontalGridLines      = None

        #Object Configuration
        self.sysFunc_editGUIOConfig = kwargs['sysFunctions']['EDITGUIOCONFIG']
        self.objectConfig = dict()
        oc_imported = kwargs['guioConfig'].get(self.name, None)
        if oc_imported is None: self.__initializeObjectConfig()
        else:                   self.objectConfig = oc_imported.copy()
        self.__configureDisplayBoxes(onInit = True)
        self.__matchGUIOsToConfig()
        
        #Object Status
        self.status = "DEFAULT"
        self.hidden = False

        #Post-Initialization
        self.__setHVRParams()
        self.__initializeRCLCG()
        self.horizontalViewRange_magnification = 100
        hvg_end = round(time.time()+self.expectedKlineTemporalWidth*5)
        hvr_beg = round(hvg_end-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
        self.horizontalViewRange = [hvr_beg, hvg_end]
        self.__onHViewRangeUpdate(1)
        self.__editVVR_toExtremaCenter()

        #Object Cover Graphics
        self.frameSprites['DATALOADINGCOVER'].visible = False
        self.dataLoadingGaugeBar.hide()
        self.dataLoadingTextBox.hide()
        self.dataLoadingTextBox_perc.hide()
    #Initialization END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #Object Configuration & GUIO Initialization ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __configureSettingsSubPageObjects(self):
        #[1]: Instances
        ssp         = self.settingsSubPage
        ssp_GUIOs   = ssp.GUIOs
        ssp_addGUIO = ssp.addGUIO
        vm_getTP    = self.visualManager.getTextPack

        #[2]: Objection Generation
        sp_vswidth = 4000
        yPos_beg   = 20000
        #Title
        ssp_addGUIO("TITLE_MAIN", atmEta_gui_Generals.passiveGraphics_wrapperTypeB, {'groupOrder': 0, 'xPos': 0, 'yPos': yPos_beg, 'width': sp_vswidth, 'height': 200, 'style': 'styleA', 'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:TITLE_VIEWERSETTINGS')})
        yPosPoint0 = yPos_beg-350
        ssp_addGUIO("DISPLAYMODE_TEXT",         atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos':  yPosPoint0,     'width': 1750, 'height': 250, 'style': 'styleB', 'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:DISPLAYMODE'), 'fontSize': 80})
        ssp_addGUIO("DISPLAYMODE_SELECTIONBOX", atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 2, 'xPos': 1850, 'yPos':  yPosPoint0,     'width': 2150, 'height': 250, 'style': 'styleA', 'name': 'DISPLAYMODE_SELECTION', 'nDisplay': 10, 'fontSize': 80, 'expansionDir': 0, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
        ssp_addGUIO("TIMEZONE_TEXT",            atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos':  yPosPoint0-350, 'width': 1750, 'height': 250, 'style': 'styleB', 'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:TIMEZONE'), 'fontSize': 80})
        ssp_addGUIO("TIMEZONE_SELECTIONBOX",    atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 2, 'xPos': 1850, 'yPos':  yPosPoint0-350, 'width': 2150, 'height': 250, 'style': 'styleA', 'name': 'TIMEZONE_SELECTION', 'nDisplay': 10, 'fontSize': 80, 'expansionDir': 0, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
        ssp_addGUIO("INTERVAL_TEXT",            atmEta_gui_Generals.textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos':  yPosPoint0-700, 'width': 1750, 'height': 250, 'style': 'styleB', 'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:INTERVAL'), 'fontSize': 80})
        ssp_addGUIO("INTERVAL_SELECTIONBOX",    atmEta_gui_Generals.selectionBox_typeB, {'groupOrder': 2, 'xPos': 1850, 'yPos':  yPosPoint0-700, 'width': 2150, 'height': 250, 'style': 'styleA', 'name': 'INTERVAL_SELECTION', 'nDisplay': 10, 'fontSize': 80, 'expansionDir': 0, 'selectionUpdateFunction': self.__onSettingsContentUpdate})
        yPosPoint1 = yPosPoint0-1000
        ssp_addGUIO("LINECOLOR_TITLE",     atmEta_gui_Generals.passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1, 'width': sp_vswidth, 'height': 250, 'style': 'styleB', 'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:LINE'), 'fontSize': 90, 'anchor': 'SW'})
        ssp_addGUIO("LINECOLOR_TEXT",      atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350, 'width': 900, 'height': 250, 'style': 'styleA', 'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:COLOR'), 'fontSize': 80})
        ssp_addGUIO("LINECOLOR_LED",       atmEta_gui_Generals.LED_typeA,                    {'groupOrder': 0, 'xPos': 1000, 'yPos': yPosPoint1-350, 'width': 950, 'height': 250, 'style': 'styleA', 'mode': True})
        ssp_addGUIO("LINEWIDTH_TEXT",      atmEta_gui_Generals.textBox_typeA,                {'groupOrder': 0, 'xPos': 2050, 'yPos': yPosPoint1-350, 'width': 900, 'height': 250, 'style': 'styleA', 'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:WIDTH'), 'fontSize': 80})
        ssp_addGUIO("LINEWIDTH_TEXTINPUT", atmEta_gui_Generals.textInputBox_typeA,           {'groupOrder': 0, 'xPos': 3050, 'yPos': yPosPoint1-350, 'width': 950, 'height': 250, 'style': 'styleA', 'name': 'WidthTextInputBox', 'text': "", 'fontSize': 80, 'textUpdateFunction': self.__onSettingsContentUpdate})
        for index, cType in enumerate(('R', 'G', 'B', 'A')):
            ssp_addGUIO(f"LINECOLOR_{cType}_TEXT",   atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-700-350*index, 'width':  500, 'height': 250, 'style': 'styleA', 'text': cType, 'fontSize': 80})
            ssp_addGUIO(f"LINECOLOR_{cType}_SLIDER", atmEta_gui_Generals.slider_typeA,  {'groupOrder': 0, 'xPos':  600, 'yPos': yPosPoint1-650-350*index, 'width': 2600, 'height': 150, 'style': 'styleA', 'name': f'Color_{cType}', 'valueUpdateFunction': self.__onSettingsContentUpdate})
            ssp_addGUIO(f"LINECOLOR_{cType}_VALUE",  atmEta_gui_Generals.textBox_typeA, {'groupOrder': 0, 'xPos': 3300, 'yPos': yPosPoint1-700-350*index, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "-", 'fontSize': 80})
        yPosPoint2 = yPosPoint1-1750
        ssp_addGUIO("APPLYNEWSETTINGS",  atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2-350, 'width': sp_vswidth, 'height': 250, 'style': 'styleA', 'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:APPLYSETTINGS'), 'fontSize': 80, 'name': 'ApplySettings',   'releaseFunction': self.__onSettingsContentUpdate})
        ssp_addGUIO("SAVECONFIGURATION", atmEta_gui_Generals.button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2-700, 'width': sp_vswidth, 'height': 250, 'style': 'styleA', 'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:SAVECONFIG'),    'fontSize': 80, 'name': 'SAVECONFIG', 'releaseFunction': self.__onSettingsContentUpdate})
        
        #[3]: Selections Setup
        #---[3-1]: Display Mode
        displayModeSelections = {'BALANCE':             {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:BALANCE')},
                                 'COMMITMENTRATE':      {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:COMMITMENTRATE')},
                                 'RISKLEVEL':           {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:RISKLEVEL')},
                                 'NTRADES_TOTAL':       {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:NTRADES_TOTAL')},
                                 'NTRADES_BUY':         {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:NTRADES_BUY')},
                                 'NTRADES_SELL':        {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:NTRADES_SELL')},
                                 'NTRADES_ENTRY':       {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:NTRADES_ENTRY')},
                                 'NTRADES_CLEAR':       {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:NTRADES_CLEAR')},
                                 'NTRADES_EXIT':        {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:NTRADES_EXIT')},
                                 'NTRADES_FSLIMMED':    {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:NTRADES_FSLIMMED')},
                                 'NTRADES_FSLCLOSE':    {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:NTRADES_FSLCLOSE')},
                                 'NTRADES_LIQUIDATION': {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:NTRADES_LIQUIDATION')},
                                 'NTRADES_FORCECLEAR':  {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:NTRADES_FORCECLEAR')},
                                 'NTRADES_UNKNOWN':     {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:NTRADES_UNKNOWN')},
                                 'NTRADES_GAIN':        {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:NTRADES_GAIN')},
                                 'NTRADES_LOSS':        {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:NTRADES_LOSS')},
                                }
        ssp_GUIOs["DISPLAYMODE_SELECTIONBOX"].setSelectionList(displayModeSelections, displayTargets = 'all')
        #---[3-2]: Time Zone
        timeZoneSelections = {'LOCAL': {'text': 'LOCAL'}}
        for hour in range (24): 
            timeZoneSelections[f'UTC+{hour}'] = {'text': f'UTC+{hour}'}
        ssp_GUIOs["TIMEZONE_SELECTIONBOX"].setSelectionList(timeZoneSelections, displayTargets = 'all')
        #---[3-3]: Interval
        intervals = {atmEta_Auxillaries.KLINE_INTERVAL_ID_1m:  {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:INTERVAL_1MIN')},
                     atmEta_Auxillaries.KLINE_INTERVAL_ID_3m:  {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:INTERVAL_3MIN')},
                     atmEta_Auxillaries.KLINE_INTERVAL_ID_5m:  {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:INTERVAL_5MIN')},
                     atmEta_Auxillaries.KLINE_INTERVAL_ID_15m: {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:INTERVAL_15MIN')},
                     atmEta_Auxillaries.KLINE_INTERVAL_ID_30m: {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:INTERVAL_30MIN')},
                     atmEta_Auxillaries.KLINE_INTERVAL_ID_1h:  {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:INTERVAL_1HOUR')},
                     atmEta_Auxillaries.KLINE_INTERVAL_ID_2h:  {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:INTERVAL_2HOUR')},
                     atmEta_Auxillaries.KLINE_INTERVAL_ID_4h:  {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:INTERVAL_4HOUR')},
                     atmEta_Auxillaries.KLINE_INTERVAL_ID_6h:  {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:INTERVAL_6HOUR')},
                     atmEta_Auxillaries.KLINE_INTERVAL_ID_8h:  {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:INTERVAL_8HOUR')},
                     atmEta_Auxillaries.KLINE_INTERVAL_ID_12h: {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:INTERVAL_12HOUR')},
                     atmEta_Auxillaries.KLINE_INTERVAL_ID_1d:  {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:INTERVAL_1DAY')},
                     atmEta_Auxillaries.KLINE_INTERVAL_ID_3d:  {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:INTERVAL_3DAY')},
                     atmEta_Auxillaries.KLINE_INTERVAL_ID_1W:  {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:INTERVAL_1WEEK')},
                     atmEta_Auxillaries.KLINE_INTERVAL_ID_1M:  {'text': vm_getTP('GUIO_PERIODICREPORTVIEWER:INTERVAL_1MONTH')}
                    }
        ssp_GUIOs["INTERVAL_SELECTIONBOX"].setSelectionList(intervals, displayTargets = 'all')

    def __initializeObjectConfig(self):
        oc = dict()
        oc['DisplayMode']  = 'BALANCE'
        oc['TimeZone']     = 'LOCAL'
        oc['Interval']     = atmEta_Auxillaries.KLINE_INTERVAL_ID_1h
        oc['LINE_Display'] = True
        oc['LINE_Width']   = 1
        oc['LINE_ColorR%DARK'] =random.randint(64,255); oc['LINE_ColorG%DARK'] =random.randint(64,255); oc['LINE_ColorB%DARK'] =random.randint(64, 255); oc['LINE_ColorA%DARK'] =255
        oc['LINE_ColorR%LIGHT']=random.randint(64,255); oc['LINE_ColorG%LIGHT']=random.randint(64,255); oc['LINE_ColorB%LIGHT']=random.randint(64, 255); oc['LINE_ColorA%LIGHT']=255
        self.objectConfig = oc

    def __matchGUIOsToConfig(self):
        oc        = self.objectConfig
        cgt       = self.currentGUITheme
        ssp_GUIOs = self.settingsSubPage.GUIOs
        ssp_GUIOs["DISPLAYMODE_SELECTIONBOX"].setSelected(oc['DisplayMode'], callSelectionUpdateFunction = True)
        ssp_GUIOs["TIMEZONE_SELECTIONBOX"].setSelected(oc['TimeZone'],       callSelectionUpdateFunction = True)
        ssp_GUIOs["INTERVAL_SELECTIONBOX"].setSelected(oc['Interval'],       callSelectionUpdateFunction = True)
        ssp_GUIOs["LINEWIDTH_TEXTINPUT"].updateText(str(oc['LINE_Width']))
        lineColor_r = oc[f'LINE_ColorR%{cgt}']
        lineColor_g = oc[f'LINE_ColorG%{cgt}']
        lineColor_b = oc[f'LINE_ColorB%{cgt}']
        lineColor_a = oc[f'LINE_ColorA%{cgt}']
        ssp_GUIOs["LINECOLOR_LED"].updateColor(lineColor_r, lineColor_g, lineColor_b, lineColor_a)
        ssp_GUIOs["LINECOLOR_R_VALUE"].updateText(str(lineColor_r))
        ssp_GUIOs["LINECOLOR_G_VALUE"].updateText(str(lineColor_g))
        ssp_GUIOs["LINECOLOR_B_VALUE"].updateText(str(lineColor_b))
        ssp_GUIOs["LINECOLOR_A_VALUE"].updateText(str(lineColor_a))
        ssp_GUIOs["LINECOLOR_R_SLIDER"].setSliderValue(newValue = round(lineColor_r/255*100), callValueUpdateFunction = False)
        ssp_GUIOs["LINECOLOR_G_SLIDER"].setSliderValue(newValue = round(lineColor_g/255*100), callValueUpdateFunction = False)
        ssp_GUIOs["LINECOLOR_B_SLIDER"].setSliderValue(newValue = round(lineColor_b/255*100), callValueUpdateFunction = False)
        ssp_GUIOs["LINECOLOR_A_SLIDER"].setSliderValue(newValue = round(lineColor_a/255*100), callValueUpdateFunction = False)
        ssp_GUIOs["APPLYNEWSETTINGS"].deactivate()
        ssp_GUIOs["SAVECONFIGURATION"].deactivate()
    #Object Configuration & GUIO Initialization END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #DisplayBox Control ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __configureDisplayBoxes(self, onInit = False):
        #[1]: Determine Vertical DisplayBox Order
        if (True):
            self.displayBox_VerticalSection_Order = ['MAINGRID_X', 'MAIN']
            self.displayBox_VisibleBoxes = ['MAIN', 'MAINGRID_X', 'SETTINGSBUTTONFRAME']
            
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
                    #Define DisplayBox and DrawBox Dimensions for 'MAINGRID_X'
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
                        self.images['MAINGRID_X'] = self.imageManager.getImageByCode("periodicReportViewer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
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
                        self.images['SETTINGSBUTTONFRAME_DEFAULT'] = self.imageManager.getImageByCode("periodicReportViewer_typeA_"+self.style+"_displayBoxFrameInteractable_DEFAULT", self.displayBox['SETTINGSBUTTONFRAME'][2]*self.scaler, self.displayBox['SETTINGSBUTTONFRAME'][3]*self.scaler)
                        self.images['SETTINGSBUTTONFRAME_HOVERED'] = self.imageManager.getImageByCode("periodicReportViewer_typeA_"+self.style+"_displayBoxFrameInteractable_HOVERED", self.displayBox['SETTINGSBUTTONFRAME'][2]*self.scaler, self.displayBox['SETTINGSBUTTONFRAME'][3]*self.scaler)
                        self.images['SETTINGSBUTTONFRAME_PRESSED'] = self.imageManager.getImageByCode("periodicReportViewer_typeA_"+self.style+"_displayBoxFrameInteractable_PRESSED", self.displayBox['SETTINGSBUTTONFRAME'][2]*self.scaler, self.displayBox['SETTINGSBUTTONFRAME'][3]*self.scaler)
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
                        self.images['MAIN'] = self.imageManager.getImageByCode("periodicReportViewer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                        self.frameSprites['MAIN'] = pyglet.sprite.Sprite(x = displayBox[0]*self.scaler, y = displayBox[1]*self.scaler, img = self.images['MAIN'][0], batch = self.batch, group = self.group_0)
                        self.hitBox['MAINGRID_Y'] = atmEta_gui_HitBoxes.hitBox_Rectangular(drawBox_MAINGRID_Y[0], drawBox_MAINGRID_Y[1], drawBox_MAINGRID_Y[2], drawBox_MAINGRID_Y[3])
                        self.images['MAINGRID_Y'] = self.imageManager.getImageByCode("periodicReportViewer_typeA_"+self.style+"_displayBoxFrame", displayBox_MAINGRID_Y[2]*self.scaler, displayBox_MAINGRID_Y[3]*self.scaler)
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
                        self.displayBox_graphics['MAIN']['DESCRIPTIONTEXT3'] = atmEta_gui_TextControl.textObject_SL(scaler = self.scaler, batch = self.batch, group = self.group_hd0, text = self.visualManager.extractText(self.visualManager.getTextPack(f'GUIO_PERIODICREPORTVIEWER:{self.displayMode}')), 
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
                            self.images['MAIN'] = self.imageManager.getImageByCode("periodicReportViewer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
                            self.frameSprites['MAIN'].position = (displayBox[0]*self.scaler, displayBox[1]*self.scaler, self.frameSprites['MAIN'].z)
                            self.frameSprites['MAIN'].image = self.images['MAIN'][0]
                            self.hitBox['MAINGRID_Y'].reposition(xPos = drawBox_MAINGRID_Y[0], yPos = drawBox_MAINGRID_Y[1])
                            self.hitBox['MAINGRID_Y'].resize(width = drawBox_MAINGRID_Y[2], height = drawBox_MAINGRID_Y[3])
                            self.images['MAINGRID_Y'] = self.imageManager.getImageByCode("periodicReportViewer_typeA_"+self.style+"_displayBoxFrame", drawBox_MAINGRID_Y[2]*self.scaler, drawBox_MAINGRID_Y[3]*self.scaler)
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
                            self.images['MAINGRID_X'] = self.imageManager.getImageByCode("periodicReportViewer_typeA_"+self.style+"_displayBoxFrame", displayBox[2]*self.scaler, displayBox[3]*self.scaler)
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
        if (self.fetchComplete == True):
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
        while ((time.perf_counter_ns()-mei_beg < _TIMELIMIT_DRAWQUEUE_NS) and (0 < len(self.drawQueue))): self.__dataDrawer_draw(timestamp = self.drawQueue.pop())
        return (0 < len(self.drawQueue))

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
        while ((0 < len(self.drawRemovalQueue)) and (time.perf_counter_ns()-mei_beg < _TIMELIMIT_DRAWREMOVAL_NS)):
            self.__dataDrawer_RemoveExpiredDrawings(self.drawRemovalQueue.pop())
    #Processings END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





    #User Interaction Control ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def handleMouseEvent(self, event):
        if ((self.fetching == False) and (self.hidden == False)):
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
        #[1]: Instances
        dBox_g = self.displayBox_graphics
        dBox_g_m   = dBox_g['MAIN']
        dBox_g_mgX = dBox_g['MAINGRID_X']
        dBox_g_m_phh = dBox_g_m['POSHIGHLIGHT_HOVERED']
        dBox_g_m_dt1 = dBox_g_m['DESCRIPTIONTEXT1']
        dBox_g_m_dt2 = dBox_g_m['DESCRIPTIONTEXT2']
        dBox_g_m_hul = dBox_g_m['HORIZONTALGUIDELINE']
        dBox_g_m_hut = dBox_g_m['HORIZONTALGUIDETEXT']
        updated_x, updated_y                             = self.posHighlight_updatedPositions
        tsHovered, yHovered, dBox_current, dBox_previous = self.posHighlight_hoveredPos

        #[2]: Horizontal Elements Update
        if updated_x:
            #[3-1]: If Hovering Over No Display Box
            if dBox_current is None: 
                dBox_g_m_phh.visible = False
                dBox_g_m_dt1.hide()
                dBox_g_m_dt2.hide()
            #[3-2]: If Hovering Over A Display Box
            else:
                #[3-2-1]: Visibility Control
                if not dBox_g_m_phh.visible: dBox_g_m_phh.visible = True
                if dBox_g_m_dt1.isHidden(): dBox_g_m_dt1.show()
                if dBox_g_m_dt2.isHidden(): dBox_g_m_dt2.show()
                #[3-2-2]: Update Highligter Graphics
                ts_rightEnd = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = tsHovered, mrktReg = None, nTicks = 1)
                pixelPerTS  = dBox_g_mgX['DRAWBOX'][2]*self.scaler / (self.horizontalViewRange[1]-self.horizontalViewRange[0])
                highlightShape_x     = round((tsHovered-self.verticalGrid_intervals[0])*pixelPerTS, 1)
                highlightShape_width = round((ts_rightEnd-tsHovered)*pixelPerTS,                    1)
                dBox_g_m_phh.x     = highlightShape_x
                dBox_g_m_phh.width = highlightShape_width
                if not dBox_g_m_phh.visible: dBox_g_m_phh.visible = True
                #[3-2-3]: Update Data Descriptors
                #---[3-2-3-1]: Time
                displayText_time = datetime.fromtimestamp(tsHovered+self.timezoneDelta, tz = timezone.utc).strftime(" %Y/%m/%d %H:%M")
                dBox_g_m_dt1.setText(displayText_time, [((0, len(displayText_time)), 'DEFAULT')])
                #---[3-2-3-2]: Data
                self.__onPosHighlightUpdate_updateDataDescriptionText()
                
        #[3]: Vertcial Elements Update
        if updated_y:
            #[3-1]: If Hovering Over No Display Box
            if dBox_current is None:
                dBox_g_m_hul.visible = False
                dBox_g_m_hut.hide()
            #[3-2]: If Hovering Over A Display Box
            else:
                dBox_g_prev    = dBox_g.get(dBox_previous, None)
                dBox_g_current = dBox_g.get(dBox_current,  None)
                #[3-2-1]: Visibility Control
                if (dBox_g_prev is not None) and (dBox_previous != dBox_current):
                    dBox_g_prev['HORIZONTALGUIDELINE'].visible = False
                    dBox_g_prev['HORIZONTALGUIDETEXT'].hide()
                else:
                    if not dBox_g_current['HORIZONTALGUIDELINE'].visible: dBox_g_current['HORIZONTALGUIDELINE'].visible = True
                    if dBox_g_current['HORIZONTALGUIDETEXT'].isHidden():  dBox_g_current['HORIZONTALGUIDETEXT'].show()
                #[3-2-2]: Update Highligter Graphics
                pixelPerVal = dBox_g_current['DRAWBOX'][3]*self.scaler / (self.verticalViewRange[1]-self.verticalViewRange[0])
                try:    verticalHoverLine_y = round((yHovered-self.horizontalGridIntervals[0])*pixelPerVal, 1)
                except: verticalHoverLine_y = round(yHovered*pixelPerVal,                                   1)
                dBox_g_current['HORIZONTALGUIDELINE'].y  = verticalHoverLine_y
                dBox_g_current['HORIZONTALGUIDELINE'].y2 = verticalHoverLine_y
                #[3-2-3]: Update Vertical Value Text
                dFromCeiling = dBox_g_current['HORIZONTALGRID_CAMGROUP'].projection_y1-verticalHoverLine_y
                if dFromCeiling < _GD_DISPLAYBOX_GUIDE_HORIZONTALTEXTHEIGHT*self.scaler: dBox_g_current['HORIZONTALGUIDETEXT'].moveTo(y = verticalHoverLine_y/self.scaler-_GD_DISPLAYBOX_GUIDE_HORIZONTALTEXTHEIGHT)
                else:                                                                    dBox_g_current['HORIZONTALGUIDETEXT'].moveTo(y = verticalHoverLine_y/self.scaler)
                formattingMode = _DESCRIPTIONTEXT_DISPLAYMODE_VERTICALVALUE_FORMATTINGMODE[self.displayMode]
                if formattingMode == 0:
                    dBox_g_current['HORIZONTALGUIDETEXT'].setText(atmEta_Auxillaries.simpleValueFormatter(value = yHovered, precision = 3))
                elif formattingMode == 1:
                    dBox_g_current['HORIZONTALGUIDETEXT'].setText(text = f"{atmEta_Auxillaries.simpleValueFormatter(value = yHovered, precision = 3)} %")
                elif formattingMode == 2:
                    dBox_g_current['HORIZONTALGUIDETEXT'].setText(atmEta_Auxillaries.simpleValueFormatter(value = yHovered, precision = 0))

        #[4]: Reset Update Flag
        self.posHighlight_updatedPositions = None

    def __onPosHighlightUpdate_updateDataDescriptionText(self):
        #[1]: Instances
        dBox_g = self.displayBox_graphics
        dBox_g_m     = dBox_g['MAIN']
        dBox_g_m_dt2 = dBox_g_m['DESCRIPTIONTEXT2']
        tsHovered, yHovered, dBox_current, dBox_previous = self.posHighlight_hoveredPos
        prs_d = self.periodicReports_display
        dMode = self.displayMode
        func_svf = atmEta_Auxillaries.simpleValueFormatter

        #[2]: Periodic Report Timestamp
        prTS = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = tsHovered, mrktReg = None, nTicks = 0)

        #[3]: Periodic Report
        #---[3-1]: No Data Exists
        if prTS not in prs_d:
            dBox_g_m_dt2.setText(text = "", textStyle = 'DEFAULT')
            return
        #---[3-2]: Data Exists
        pr_d = prs_d[prTS]

        #------[3-2-1]: Display Mode - BALANCE
        if dMode == 'BALANCE':
            wb_open  = pr_d['walletBalance_open']
            wb_min   = pr_d['walletBalance_min']
            wb_max   = pr_d['walletBalance_max']
            wb_close = pr_d['walletBalance_close']
            mb_open  = pr_d['marginBalance_open']
            mb_min   = pr_d['marginBalance_min']
            mb_max   = pr_d['marginBalance_max']
            mb_close = pr_d['marginBalance_close']
            if   wb_open < wb_close: color_wb = 'GREEN_LIGHT'
            elif wb_open > wb_close: color_wb = 'RED_LIGHT'
            else:                    color_wb = 'DEFAULT'
            if   mb_open < mb_close: color_mb = 'GREEN_LIGHT'
            elif mb_open > mb_close: color_mb = 'RED_LIGHT'
            else:                    color_mb = 'DEFAULT'
            textString = ""
            textStyle  = []
            for newTextString, newTextStyle in ((f" [WB] OPEN: ",                                    'DEFAULT'),
                                                (f"{func_svf(value = wb_open*100,  precision = 3)}", color_wb),
                                                (f" MIN: ",                                          'DEFAULT'),
                                                (f"{func_svf(value = wb_min*100,   precision = 3)}", color_wb),
                                                (f" MAX: ",                                          'DEFAULT'),
                                                (f"{func_svf(value = wb_max*100,   precision = 3)}", color_wb),
                                                (f" CLOSE: ",                                        'DEFAULT'),
                                                (f"{func_svf(value = wb_close*100, precision = 3)}", color_wb),
                                                (" / ",                                              'DEFAULT'),
                                                (f"[MB] OPEN: ",                                     'DEFAULT'),
                                                (f"{func_svf(value = mb_open*100,  precision = 3)}", color_mb),
                                                (f" MIN: ",                                          'DEFAULT'),
                                                (f"{func_svf(value = mb_min*100,   precision = 3)}", color_mb),
                                                (f" MAX: ",                                          'DEFAULT'),
                                                (f"{func_svf(value = mb_max*100,   precision = 3)}", color_mb),
                                                (f" CLOSE: ",                                        'DEFAULT'),
                                                (f"{func_svf(value = mb_close*100, precision = 3)}", color_mb),
                                                ):
                textStyle.append(((len(textString), len(textString)+len(newTextString)-1), newTextStyle))
                textString += newTextString
            dBox_g_m_dt2.setText(text = textString, textStyle = textStyle)

        #------[3-2-2]: Display Mode - COMMITMENTRATE
        elif dMode == 'COMMITMENTRATE':
            val_open  = pr_d['commitmentRate_open']
            val_min   = pr_d['commitmentRate_min']
            val_max   = pr_d['commitmentRate_max']
            val_close = pr_d['commitmentRate_close']
            if   val_open < val_close: color = 'GREEN_LIGHT'
            elif val_open > val_close: color = 'RED_LIGHT'
            else:                      color = 'DEFAULT'
            val_open_str  = func_svf(value = val_open*100,  precision = 3)
            val_min_str   = func_svf(value = val_min*100,   precision = 3)
            val_max_str   = func_svf(value = val_max*100,   precision = 3)
            val_close_str = func_svf(value = val_close*100, precision = 3)
            displayText_open  = f" OPEN: {val_open_str} %";   tp1 =       len(displayText_open) 
            displayText_min   = f" MIN: {val_min_str} %";     tp2 = tp1 + len(displayText_min)
            displayText_max   = f" MAX: {val_max_str} %";     tp3 = tp2 + len(displayText_max)
            displayText_close = f" CLOSE: {val_close_str} %"; tp4 = tp3 + len(displayText_close)
            dBox_g_m_dt2.setText(displayText_open+displayText_min+displayText_max+displayText_close, [((0,     5),     'DEFAULT'),
                                                                                                      ((6,     tp1),   color),
                                                                                                      ((tp1+1, tp1+5), 'DEFAULT'),
                                                                                                      ((tp1+6, tp2),   color),
                                                                                                      ((tp2+1, tp2+4), 'DEFAULT'),
                                                                                                      ((tp2+5, tp3),   color),
                                                                                                      ((tp3+1, tp3+6), 'DEFAULT'),
                                                                                                      ((tp3+7, tp4-1), color)])

        #------[3-2-3]: Display Mode - RISKLEVEL
        elif dMode == 'RISKLEVEL':
            val_open  = pr_d['riskLevel_open']
            val_min   = pr_d['riskLevel_min']
            val_max   = pr_d['riskLevel_max']
            val_close = pr_d['riskLevel_close']
            if   val_open < val_close: color = 'GREEN_LIGHT'
            elif val_open > val_close: color = 'RED_LIGHT'
            else:                      color = 'DEFAULT'
            val_open_str  = func_svf(value = val_open*100,  precision = 3)
            val_min_str   = func_svf(value = val_min*100,   precision = 3)
            val_max_str   = func_svf(value = val_max*100,   precision = 3)
            val_close_str = func_svf(value = val_close*100, precision = 3)
            displayText_open  = f" OPEN: {val_open_str} %";   tp1 =       len(displayText_open) 
            displayText_min   = f" MIN: {val_min_str} %";     tp2 = tp1 + len(displayText_min)
            displayText_max   = f" MAX: {val_max_str} %";     tp3 = tp2 + len(displayText_max)
            displayText_close = f" CLOSE: {val_close_str} %"; tp4 = tp3 + len(displayText_close)
            dBox_g_m_dt2.setText(displayText_open+displayText_min+displayText_max+displayText_close, [((0,     5),     'DEFAULT'),
                                                                                                      ((6,     tp1),   color),
                                                                                                      ((tp1+1, tp1+5), 'DEFAULT'),
                                                                                                      ((tp1+6, tp2),   color),
                                                                                                      ((tp2+1, tp2+4), 'DEFAULT'),
                                                                                                      ((tp2+5, tp3),   color),
                                                                                                      ((tp3+1, tp3+6), 'DEFAULT'),
                                                                                                      ((tp3+7, tp4-1), color)])
        
        #------[3-2-4]: Display Mode - NTRADES_TOTAL
        elif dMode == 'NTRADES_TOTAL':
            text = f" Total Number of Trades: {pr_d['nTrades']}"
            dBox_g_m_dt2.setText(text = text, textStyle = 'DEFAULT')

        #------[3-2-5]: Display Mode - NTRADES_BUY
        elif dMode == 'NTRADES_BUY':
            text = f" Number of Buys: {pr_d['nTrades_buy']}"
            dBox_g_m_dt2.setText(text = text, textStyle = 'DEFAULT')

        #------[3-2-6]: Display Mode - NTRADES_SELL
        elif dMode == 'NTRADES_SELL':
            text = f" Number of Sells: {pr_d['nTrades_sell']}"
            dBox_g_m_dt2.setText(text = text, textStyle = 'DEFAULT')

        #------[3-2-7]: Display Mode - NTRADES_ENTRY
        elif dMode == 'NTRADES_ENTRY':
            text = f" Number of Entries: {pr_d['nTrades_entry']}"
            dBox_g_m_dt2.setText(text = text, textStyle = 'DEFAULT')

        #------[3-2-8]: Display Mode - NTRADES_CLEAR
        elif dMode == 'NTRADES_CLEAR':
            text = f" Number of Clears: {pr_d['nTrades_clear']}"
            dBox_g_m_dt2.setText(text = text, textStyle = 'DEFAULT')

        #------[3-2-9]: Display Mode - NTRADES_EXIT
        elif dMode == 'NTRADES_EXIT':
            text = f" Number of Exits: {pr_d['nTrades_exit']}"
            dBox_g_m_dt2.setText(text = text, textStyle = 'DEFAULT')

        #------[3-2-10]: Display Mode - NTRADES_FSLIMMED
        elif dMode == 'NTRADES_FSLIMMED':
            text = f" Number of FSLIMMEDs: {pr_d['nTrades_fslImmed']}"
            dBox_g_m_dt2.setText(text = text, textStyle = 'DEFAULT')

        #------[3-2-11]: Display Mode - NTRADES_FSLCLOSE
        elif dMode == 'NTRADES_FSLCLOSE':
            text = f" Number of FSLCLOSEs: {pr_d['nTrades_fslClose']}"
            dBox_g_m_dt2.setText(text = text, textStyle = 'DEFAULT')

        #------[3-2-12]: Display Mode - NTRADES_LIQUIDATION
        elif dMode == 'NTRADES_LIQUIDATION':
            text = f" Number of Liquidations: {pr_d['nTrades_liquidation']}"
            dBox_g_m_dt2.setText(text = text, textStyle = 'DEFAULT')

        #------[3-2-13]: Display Mode - NTRADES_FORCECLEAR
        elif dMode == 'NTRADES_FORCECLEAR':
            text = f" Number of Force Clears: {pr_d['nTrades_forceClear']}"
            dBox_g_m_dt2.setText(text = text, textStyle = 'DEFAULT')

        #------[3-2-14]: Display Mode - NTRADES_UNKNOWN
        elif dMode == 'NTRADES_UNKNOWN':
            text = f" Number of Unknown Trades: {pr_d['nTrades_unknown']}"
            dBox_g_m_dt2.setText(text = text, textStyle = 'DEFAULT')

        #------[3-2-15]: Display Mode - NTRADES_GAIN
        elif dMode == 'NTRADES_GAIN':
            text = f" Number of Gaining Trades: {pr_d['nTrades_gain']}"
            dBox_g_m_dt2.setText(text = text, textStyle = 'DEFAULT')

        #------[3-2-16]: Display Mode - NTRADES_LOSS
        elif dMode == 'NTRADES_LOSS':
            text = f" Number of Losing Trades: {pr_d['nTrades_loss']}"
            dBox_g_m_dt2.setText(text = text, textStyle = 'DEFAULT')

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
        if ((self.fetching == False) and (self.hidden == False)):
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
        if ((self.fetchComplete == False) and (self.fetching == True)):
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

        newEffectiveTextStyle = self.visualManager.getTextStyle('periodicReportViewer_'+self.textStyle)
        for styleTarget in newEffectiveTextStyle: newEffectiveTextStyle[styleTarget]['font_size'] = self.effectiveTextStyle[styleTarget]['font_size']
        self.effectiveTextStyle = newEffectiveTextStyle
        
        self.gridColor       = self.visualManager.getFromColorTable('PERIODICREPORTVIEWER_GRID')
        self.gridColor_Heavy = self.visualManager.getFromColorTable('PERIODICREPORTVIEWER_GRIDHEAVY')
        self.guideColor      = self.visualManager.getFromColorTable('PERIODICREPORTVIEWER_GUIDECONTENT')
        self.posHighlightColor_hovered  = self.visualManager.getFromColorTable('PERIODICREPORTVIEWER_POSHOVERED')
        self.posHighlightColor_selected = self.visualManager.getFromColorTable('PERIODICREPORTVIEWER_POSSELECTED')

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
        for _ts in self.drawn: self.__dataDrawer_draw(timestamp = _ts)

    def on_LanguageUpdate(self, **kwargs):
        #Bring in updated textStyle
        newEffectiveTextStyle = self.visualManager.getTextStyle('periodicReportViewer_'+self.textStyle)
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
        if self.settingsSubPage_Opened: self.settingsSubPage.hide()
        else:                           self.settingsSubPage.show()
        self.settingsSubPage_Opened = not(self.settingsSubPage_Opened)

    def __onSettingsContentUpdate(self, objectInstnace):
        #[1]: Source
        guioName       = objectInstnace.getName()
        guioName_split = guioName.split("_")
        setterType     = guioName_split[0]

        #[2]: Process Variable
        activateSaveConfigButton = False

        #[3]: Instances
        oc  = self.objectConfig
        cgt = self.currentGUITheme
        vm  = self.visualManager
        dBox_g    = self.displayBox_graphics
        ssp_GUIOs = self.settingsSubPage.GUIOs

        #[4]: Content Update Interpretation
        #---[4-1]: Display Mode
        if setterType == 'DISPLAYMODE':
            #[4-1-1]: Update Display Mode
            selectedDisplayMode = ssp_GUIOs['DISPLAYMODE_SELECTIONBOX'].getSelected()
            self.displayMode = selectedDisplayMode
            #[4-1-2]: Graphics Redrawing
            if self.target is not None:
                self.__dataDrawer_RemoveDrawings() #Remove previous graphics
                self.__addBufferZone_toDrawQueue() #Update draw queue
            #[4-1-3]: Display Mode Text Update
            if 'DESCRIPTIONTEXT3' in dBox_g['MAIN']:
                dBox_g['MAIN']['DESCRIPTIONTEXT3'].setText(vm.extractText(vm.getTextPack(f'GUIO_PERIODICREPORTVIEWER:{selectedDisplayMode}')))
            #[4-1-4]: Vertical Extremas Check & Update, Position Selection Update (For Description Texts)
            try:
                if self.__checkVerticalExtremas(): 
                    self.__onVerticalExtremaUpdate()
                self.__editVVR_toExtremaCenter()
                self.__updatePosSelection(updateType = 1)
            except: pass

        #---[4-2]: Time Zone
        elif setterType == 'TIMEZONE':
            selectedTimeZone = ssp_GUIOs['TIMEZONE_SELECTIONBOX'].getSelected()
            self.updateTimeZone(newTimeZone = selectedTimeZone)
            activateSaveConfigButton = True

        #---[4-3]: Interval
        elif setterType == 'INTERVAL':
            selectedInterval = ssp_GUIOs['INTERVAL_SELECTIONBOX'].getSelected()
            self.updateInterval(newIntervalID = selectedInterval)
            activateSaveConfigButton = True

        #---[4-4]: Save Configuration
        elif setterType == 'SAVECONFIG':
            self.sysFunc_editGUIOConfig(configName = self.name, targetContent = oc.copy())
            ssp_GUIOs["SAVECONFIGURATION"].deactivate()

        #---[4-5]: Line Color
        elif setterType == 'Color':
            cType = guioName_split[1]
            ssp_GUIOs['LINECOLOR_LED'].updateColor(rValue = round(ssp_GUIOs['LINECOLOR_R_SLIDER'].getSliderValue()*255/100),
                                                   gValue = round(ssp_GUIOs['LINECOLOR_G_SLIDER'].getSliderValue()*255/100),
                                                   bValue = round(ssp_GUIOs['LINECOLOR_B_SLIDER'].getSliderValue()*255/100),
                                                   aValue = round(ssp_GUIOs['LINECOLOR_A_SLIDER'].getSliderValue()*255/100))
            ssp_GUIOs[f"LINECOLOR_{cType}_VALUE"].updateText(str(round(ssp_GUIOs[f'LINECOLOR_{cType}_SLIDER'].getSliderValue()*255/100)))
            ssp_GUIOs['APPLYNEWSETTINGS'].activate()

        #---[4-6]: Line Width
        elif setterType == 'WidthTextInputBox':
            ssp_GUIOs['APPLYNEWSETTINGS'].activate()

        #---[4-7]: Apply Settings
        elif setterType == 'ApplySettings':
            updateTracker = False
            #Width
            width_previous = oc['LINE_Width']
            reset = False
            try:
                width = int(ssp_GUIOs["LINEWIDTH_TEXTINPUT"].getText())
                if 0 < width: oc['LINE_Width'] = width
                else: reset = False
            except: reset = True
            if reset:
                oc['LINE_Width'] = 1
                ssp_GUIOs["LINEWIDTH_TEXTINPUT"].updateText(str(oc['LINE_Width']))
            if width_previous != oc['LINE_Width']: updateTracker = True

            #Color
            color_previous = (oc[f'LINE_ColorR%{cgt}'],
                              oc[f'LINE_ColorG%{cgt}'],
                              oc[f'LINE_ColorB%{cgt}'],
                              oc[f'LINE_ColorA%{cgt}'])
            color_r, color_g, color_b, color_a = ssp_GUIOs["LINECOLOR_LED"].getColor()
            oc[f'LINE_ColorR%{cgt}'] = color_r
            oc[f'LINE_ColorG%{cgt}'] = color_g
            oc[f'LINE_ColorB%{cgt}'] = color_b
            oc[f'LINE_ColorA%{cgt}'] = color_a
            if color_previous != (color_r, color_g, color_b, color_a): updateTracker = True
            #Queue Update
            if updateTracker:
                self.__dataDrawer_RemoveDrawings() #Remove previous graphics
                self.__addBufferZone_toDrawQueue() #Update draw queue
            #Control Buttons Handling
            ssp_GUIOs['APPLYNEWSETTINGS'].deactivate()
            activateSaveConfigButton = True

        #---[5]: Save Configuration Button Activation 
        if activateSaveConfigButton and ssp_GUIOs["SAVECONFIGURATION"].deactivated: ssp_GUIOs["SAVECONFIGURATION"].activate()

    def __addBufferZone_toDrawQueue(self):
        for ts in itertools.chain(self.horizontalViewRange_timestampsInViewRange, self.horizontalViewRange_timestampsInBufferZone):
            if ts not in self.periodicReports_display: continue
            self.drawQueue.add(ts)
        
    def updateTimeZone(self, newTimeZone):
        #[1]: Object Configuration Update
        self.objectConfig['TimeZone'] = newTimeZone

        #[2]: TimeZone Delta Update
        if   newTimeZone == 'LOCAL':        self.timezoneDelta = -time.timezone
        elif newTimeZone.startswith('UTC'): self.timezoneDelta = int(newTimeZone.split("+")[1])*3600

        #[3]: Update Vertical Grids (Temporal Texts)
        if self.horizontalViewRange[0] is not None:
            self.__onHViewRangeUpdate_UpdateGrids(updateType = 1)
    
    def updateInterval(self, newIntervalID):
        #[1]: Object Configuration Update
        self.objectConfig['Interval'] = newIntervalID

        #[2]: Interval Update
        self.intervalID                 = newIntervalID
        self.expectedKlineTemporalWidth = _EXPECTEDTEMPORALWIDTHS[self.intervalID]

        #[3]: Graphics Clearing
        self.__dataDrawer_RemoveDrawings()

        #[4]: Display Date Regeneration
        self.__generateDisplayData()

        #[5]: View Update
        self.__setHVRParams()
        self.horizontalViewRange_magnification = _GD_DISPLAYBOX_MAIN_HVR_MINMAGNITUDE
        hvr_new_end = round(time.time()+self.expectedKlineTemporalWidth*5) if self.horizontalViewRange[1] is None else self.horizontalViewRange[1]
        hvr_new_beg = round(hvr_new_end-(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
        hvr_new = [hvr_new_beg, hvr_new_end]
        tz_rev  = -self.timezoneDelta
        if hvr_new[0] < tz_rev: hvr_new = [tz_rev, hvr_new[1]-hvr_new[0]+tz_rev]
        self.horizontalViewRange = hvr_new
        self.__onHViewRangeUpdate(1)
        self.__editVVR_toExtremaCenter()
    #Configuration Update Control END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------



    #Data Drawing --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def __generateDisplayData(self):
        #[1]: References
        prs   = self.periodicReports
        prs_d = self.periodicReports_display
        func_gnits = atmEta_Auxillaries.getNextIntervalTickTimestamp

        #[2]: Target Check
        target = self.target
        if target is None: 
            prs_d.clear()
            self.periodicReports_display_timestamps = list()
            return
        isTargetSimulation = (self.target[2] == 'SIMULATION')

        #[3]: Data Generation
        prs_d.clear()
        prs_TSs = sorted(prs)
        keys_summable = ['nTrades', 
                         'nTrades_buy', 
                         'nTrades_sell', 
                         'nTrades_entry', 
                         'nTrades_clear', 
                         'nTrades_exit', 
                         'nTrades_fslImmed', 
                         'nTrades_fslClose',
                         'nTrades_liquidation', 
                         'nTrades_forceClear', 
                         'nTrades_unknown', 
                         'nTrades_gain', 
                         'nTrades_loss']
        keys_ohlc = ('marginBalance', 'walletBalance', 'commitmentRate', 'riskLevel')
        if isTargetSimulation:
            keys_summable.remove('nTrades_forceClear')
            keys_summable.remove('nTrades_unknown')
        for ts in prs_TSs:
            pr     = prs[ts]
            ts_eff = func_gnits(intervalID = self.intervalID, timestamp = ts, mrktReg = None, nTicks = 0)
            if ts_eff in prs_d:
                pr_d = prs_d[ts_eff]
                for key in keys_summable:
                    pr_d[key] += pr[key]
                for key in keys_ohlc:
                    key_min   = f'{key}_min'
                    key_max   = f'{key}_max'
                    key_close = f'{key}_close'
                    if pr[key_min] < pr_d[key_min]: pr_d[key_min] = pr[key_min]
                    if pr_d[key_max] < pr[key_max]: pr_d[key_max] = pr[key_max]
                    pr_d[key_close] = pr[key_close]
            else:
                prs_d[ts_eff] = pr.copy()
                if isTargetSimulation:
                    prs_d_this = prs_d[ts_eff]
                    prs_d_this['nTrades_forceClear'] = 0
                    prs_d_this['nTrades_unknown']    = 0

        #[4]: Timestamps Update
        self.periodicReports_display_timestamps = sorted(prs_d)
    
    def __dataDrawer_draw(self, timestamp):
        try:
            if self.__dataDrawer(timestamp = timestamp): 
                self.drawn.add(timestamp)
        except Exception as e: print(termcolor.colored(f"An unexpected error occured while attempting to draw at {timestamp}\n *", 'light_yellow'), 
                                     termcolor.colored(e,                                                                          'light_yellow'))

    def __dataDrawer(self, timestamp):
        #[1]: Instances
        oc  = self.objectConfig
        cgt = self.currentGUITheme
        rclcg = self.displayBox_graphics['MAIN']['RCLCG']
        pr_d  = self.periodicReports_display[timestamp]

        #[2]: Previous Drawing Clearing
        rclcg.removeShape(shapeName = timestamp, groupName = '1')
        rclcg.removeShape(shapeName = timestamp, groupName = '2')

        #[3]: Drawing Params
        pr_d_intervalID = pr_d['_intervalID']
        if self.intervalID < pr_d_intervalID: iID_eff = pr_d_intervalID
        else:                                 iID_eff = self.intervalID
        tsWidth = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = iID_eff, timestamp = timestamp, mrktReg = None, nTicks = 1)-timestamp
        color = (oc[f'LINE_ColorR%{cgt}'],
                 oc[f'LINE_ColorG%{cgt}'],
                 oc[f'LINE_ColorB%{cgt}'],
                 oc[f'LINE_ColorA%{cgt}'])
        lineWidth = oc['LINE_Width']

        #[4]: Drawing
        dType, dCall = _DATADRAWER_DISPLAYMODE_DATADRAWMETHOD[self.displayMode]
        #---[4-1]: DrawType 0
        if dType == 0:
            #Color
            color1 = (int(color[0]/2), int(color[1]/2), int(color[2]/2), int(color[3]/2))
            color2 = color
            #X
            tail_width = round(tsWidth/5, 1)
            tail_xPos  = round(timestamp+(tsWidth-tail_width)/2, 1)
            #Y1
            d0 = pr_d[dCall[0]]
            d1 = pr_d[dCall[1]]
            d2 = pr_d[dCall[2]]
            d3 = pr_d[dCall[3]]
            if d0 < d3: body_y1 = d0; body_height1 = d3-d0
            else:       body_y1 = d3; body_height1 = d0-d3
            tail_y1      = d1
            tail_height1 = d2-d1
            #Y2
            d4 = pr_d[dCall[4]]
            d5 = pr_d[dCall[5]]
            d6 = pr_d[dCall[6]]
            d7 = pr_d[dCall[7]]
            if d4 < d7: body_y2 = d4; body_height2 = d7-d4
            else:       body_y2 = d7; body_height2 = d4-d7
            tail_y2      = d5
            tail_height2 = d6-d5
            #Drawing
            if 0 < body_height1: rclcg.addShape_Rectangle(x = timestamp, y = body_y1, width = tsWidth, height = body_height1, color = color1, shapeName = timestamp, shapeGroupName = '0', layerNumber = 1)
            else:                rclcg.addShape_Line(x = timestamp, y = body_y1, x2 = timestamp+tsWidth, y2 = body_y1, color = color1, width_y = lineWidth/2, shapeName = timestamp, shapeGroupName = '0', layerNumber = 1)
            rclcg.addShape_Rectangle(x = tail_xPos, y = tail_y1, width = tail_width, height = tail_height1, color = color1, shapeName = timestamp, shapeGroupName = '1', layerNumber = 2)
            if 0 < body_height2: rclcg.addShape_Rectangle(x = timestamp, y = body_y2, width = tsWidth, height = body_height2, color = color2, shapeName = timestamp, shapeGroupName = '2', layerNumber = 1)
            else:                rclcg.addShape_Line(x = timestamp, y = body_y2, x2 = timestamp+tsWidth, y2 = body_y2, color = color2, width_y = lineWidth/2, shapeName = timestamp, shapeGroupName = '2', layerNumber = 1)
            rclcg.addShape_Rectangle(x = tail_xPos, y = tail_y2, width = tail_width, height = tail_height2, color = color2, shapeName = timestamp, shapeGroupName = '3', layerNumber = 2)
        #---[4-2]: DrawType 1
        elif dType == 1:
            #X
            tail_width = round(tsWidth/5, 1)
            tail_xPos  = round(timestamp+(tsWidth-tail_width)/2, 1)
            #Y
            d0 = pr_d[dCall[0]]*100
            d1 = pr_d[dCall[1]]*100
            d2 = pr_d[dCall[2]]*100
            d3 = pr_d[dCall[3]]*100
            if d0 < d3: body_y = d0; body_height = d3-d0
            else:       body_y = d3; body_height = d0-d3
            tail_y      = d1
            tail_height = d2-d1
            #Drawing
            if 0 < body_height: rclcg.addShape_Rectangle(x = timestamp, y = body_y, width = tsWidth, height = body_height, color = color, shapeName = timestamp, shapeGroupName = '0', layerNumber = 1)
            else:               rclcg.addShape_Line(x = timestamp, y = body_y, x2 = timestamp+tsWidth, y2 = body_y, color = color, width_y = lineWidth/2, shapeName = timestamp, shapeGroupName = '0', layerNumber = 1)
            rclcg.addShape_Rectangle(x = tail_xPos, y = tail_y, width = tail_width, height = tail_height, color = color, shapeName = timestamp, shapeGroupName = '1', layerNumber = 2)
        #---[4-3]: DrawType 2
        elif dType == 2:
            #Drawing
            rclcg.addShape_Rectangle(x = timestamp, width = tsWidth, y = 0, height = pr_d[dCall], color = color, shapeName = timestamp, shapeGroupName = '0', layerNumber = 1)

        #[5]: Successful Draw Flag
        return True
    
    def __dataDrawer_RemoveExpiredDrawings(self, timestamp):
        #[1]: Timestamp Check
        if timestamp not in self.drawn: return

        #[2]: Remove Drawings
        rclcg = self.displayBox_graphics['MAIN']['RCLCG']
        rclcg.removeShape(shapeName = timestamp, groupName = '0')
        rclcg.removeShape(shapeName = timestamp, groupName = '1')
        rclcg.removeShape(shapeName = timestamp, groupName = '2')
        rclcg.removeShape(shapeName = timestamp, groupName = '3')

        #[3]: Remove Drawn Flag
        self.drawn.remove(timestamp)
        
    def __dataDrawer_RemoveDrawings(self):
        #[1]: Remove Drawings
        rclcg = self.displayBox_graphics['MAIN']['RCLCG']
        rclcg.removeGroup(groupName = '0')
        rclcg.removeGroup(groupName = '1')
        rclcg.removeGroup(groupName = '2')
        rclcg.removeGroup(groupName = '3')

        #[2]: Clear Drawn Flag
        self.drawn.clear()
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
        #[1]: New Position Calculation
        hvr_beg, hvr_end = self.horizontalViewRange
        if   delta_drag   is not None: effectiveDelta = -delta_drag*(hvr_end-hvr_beg)/self.displayBox_graphics['MAIN']['DRAWBOX'][2]
        elif delta_scroll is not None: effectiveDelta = -delta_scroll*self.expectedKlineTemporalWidth
        else: return
        hvr_new = [round(hvr_beg+effectiveDelta), 
                   round(hvr_end+effectiveDelta)]
        
        #[2]: Range Control
        tz_rev  = -self.timezoneDelta
        if hvr_new[0] < tz_rev: hvr_new = [tz_rev, hvr_new[1]-hvr_new[0]+tz_rev]

        #[3]: View Range Update
        self.horizontalViewRange = hvr_new
        self.__onHViewRangeUpdate(0)
        
    #---Horizontal Magnification
    def __editHMagFactor(self, delta_drag = None, delta_scroll = None):
        #[1]: New Magnification Calculation
        hvr_mag = self.horizontalViewRange_magnification
        if   delta_drag   is not None: hvr_mag_new = hvr_mag - delta_drag*200/self.displayBox_graphics['MAIN']['DRAWBOX'][2]
        elif delta_scroll is not None: hvr_mag_new = hvr_mag + delta_scroll
        else: return

        #[2]: Rounding & Range Control
        hvr_mag_new = round(hvr_mag_new, 1)
        if   hvr_mag_new < _GD_DISPLAYBOX_MAIN_HVR_MINMAGNITUDE: hvr_mag_new = _GD_DISPLAYBOX_MAIN_HVR_MINMAGNITUDE
        elif _GD_DISPLAYBOX_MAIN_HVR_MAXMAGNITUDE < hvr_mag_new: hvr_mag_new = _GD_DISPLAYBOX_MAIN_HVR_MAXMAGNITUDE

        #[3]: Variation Check
        if hvr_mag_new == hvr_mag: return

        #[4]: Horizontal View Range Update
        self.horizontalViewRange_magnification = hvr_mag_new
        hvr_new = (round(self.horizontalViewRange[1]-(hvr_mag_new*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b)), self.horizontalViewRange[1])
        tz_rev  = -self.timezoneDelta
        if hvr_new[0] < tz_rev: hvr_new = [tz_rev, hvr_new[1]-hvr_new[0]+tz_rev]
        self.horizontalViewRange = hvr_new
        self.__onHViewRangeUpdate(1)
            
    #---Post Horizontal View-Range Update
    def __onHViewRangeUpdate(self, updateType):
        #[1]: Update Process Queue
        self.__onHViewRangeUpdate_UpdateProcessQueue()

        #[2]: Update RCLCGs
        self.__onHViewRangeUpdate_UpdateRCLCGs()

        #[3]: Update Grids
        self.__onHViewRangeUpdate_UpdateGrids(updateType = updateType)

        #[4}: Find new vertical extrema within the new horizontalViewRange
        if self.__checkVerticalExtremas(): self.__onVerticalExtremaUpdate(updateType = updateType)

        #[5]: Update PosSelection
        self.__updatePosSelection(updateType = 1)
        
    def __onHViewRangeUpdate_UpdateProcessQueue(self):
        #[1]: References
        prs_TSs          = self.periodicReports_display_timestamps
        hvr_beg, hvr_end = self.horizontalViewRange
        drawn  = self.drawn
        dQueue = self.drawQueue

        #[2]: If No Timestamp Target Exists, Return
        if not prs_TSs: return

        #[3]: View Range Indices
        vr_idx_beg = bisect.bisect_left(prs_TSs,  hvr_beg)
        vr_idx_end = bisect.bisect_right(prs_TSs, hvr_end)
        
        #[4]: Buffer Zone Range Indices
        nTSsInView = vr_idx_end - vr_idx_beg
        bufLen_back    = int(nTSsInView * _GD_DISPLAYBOX_HVR_BACKWARDBUFFERFACTOR) + 1
        bufLen_forward = int(nTSsInView * _GD_DISPLAYBOX_HVR_FORWARDBUFFERFACTOR)  + 1
        br_idx_beg = max(0,            vr_idx_beg - bufLen_back)
        br_idx_end = min(len(prs_TSs), vr_idx_end + bufLen_forward)
        
        #[5]: View Range Timestamps Update
        self.horizontalViewRange_timestampsInViewRange  = prs_TSs[vr_idx_beg : vr_idx_end]
        self.horizontalViewRange_timestampsInBufferZone = prs_TSs[br_idx_beg : vr_idx_beg] + prs_TSs[vr_idx_end : br_idx_end]

        #[6]: Target Range Timestamps (List & Set)
        br_TSs_list = prs_TSs[br_idx_beg : br_idx_end]
        br_TSs_set  = set(br_TSs_list)

        #[7]: Draw Removal Queue Update
        self.drawRemovalQueue = set(drawn)-br_TSs_set

        #[8]: Draw Queue Update
        for ts in (dQueue - br_TSs_set):
            dQueue.remove(ts)
        
        #[9]: Draw Queue Update
        for ts in br_TSs_list:
            if ts in drawn: continue
            dQueue.add(ts)

    def __onHViewRangeUpdate_UpdateRCLCGs(self):
        dBox_g_MAIN      = self.displayBox_graphics['MAIN']
        hvr_beg, hvr_end = self.horizontalViewRange
        dBox_g_MAIN['RCLCG'].updateProjection(projection_x0        = hvr_beg, projection_x1 = hvr_end)
        dBox_g_MAIN['RCLCG_YFIXED'].updateProjection(projection_x0 = hvr_beg, projection_x1 = hvr_end)
            
    def __onHViewRangeUpdate_UpdateGrids(self, updateType):
        #[1]: Parameters
        dBox_g                  = self.displayBox_graphics
        vGridIntervalID_current = self.verticalGrid_intervalID
        vGridIntervals_current  = self.verticalGrid_intervals
        hvr_beg, hvr_end        = self.horizontalViewRange
        hvr_tz_beg = hvr_beg+self.timezoneDelta
        hvr_tz_end = hvr_end+self.timezoneDelta

        #[2]: Determine Vertical Grid Intervals
        updateGridContents = False
        if updateType == 1:
            for giID in atmEta_Auxillaries.GRID_INTERVAL_IDs[self.intervalID:]:
                rightEnd       = atmEta_Auxillaries.getNextIntervalTickTimestamp_GRID(giID, hvr_tz_end,           mrktReg = None, nTicks = 1)
                vGridIntervals = atmEta_Auxillaries.getTimestampList_byRange_GRID(giID,     hvr_tz_beg, rightEnd, mrktReg = None, lastTickInclusive = True)
                if len(vGridIntervals)+1 < self.nMaxVerticalGridLines: 
                    break
            self.verticalGrid_intervalID = giID
            self.verticalGrid_intervals  = vGridIntervals
            updateGridContents = True
        elif updateType == 0:
            rightEnd       = atmEta_Auxillaries.getNextIntervalTickTimestamp_GRID(vGridIntervalID_current, hvr_tz_end,           mrktReg = None, nTicks = 1)
            vGridIntervals = atmEta_Auxillaries.getTimestampList_byRange_GRID(vGridIntervalID_current,     hvr_tz_beg, rightEnd, mrktReg = None, lastTickInclusive = True)
            if (vGridIntervals_current[0] != vGridIntervals[0]) or (vGridIntervals_current[-1] != vGridIntervals[-1]):
                self.verticalGrid_intervals = vGridIntervals
                updateGridContents = True

        #[3]: Update Grid Position & Text
        vGridIntervalID_current = self.verticalGrid_intervalID
        vGridIntervals_current  = self.verticalGrid_intervals
        pixelPerTS = dBox_g['MAINGRID_X']['DRAWBOX'][2]*self.scaler / (hvr_tz_end-hvr_tz_beg)
        if updateGridContents:
            #[3-1]: Instances
            dBox_g_m_vgLines   = dBox_g['MAIN']['VERTICALGRID_LINES']
            dBox_g_mgx_vgLines = dBox_g['MAINGRID_X']['VERTICALGRID_LINES']
            dBox_g_mgx_vgTexts = dBox_g['MAINGRID_X']['VERTICALGRID_TEXTS']
            #[3-2]: Grid Loop
            for index in range (self.nMaxVerticalGridLines):
                #[3-2-1]: Active Grid
                if index < len(vGridIntervals_current) and 0 <= vGridIntervals_current[index]:
                    #[3-2-1-1]: TimeZone Timestamp
                    timestamp_tz = vGridIntervals_current[index]
                    #[3-2-1-2]: Coordinate
                    xPos = round((timestamp_tz-self.timezoneDelta-vGridIntervals_current[0])*pixelPerTS, 1)
                    #[3-2-1-3]: Lines Update
                    dBox_g_m_vgLines[index].x  = xPos
                    dBox_g_m_vgLines[index].x2 = xPos
                    if not dBox_g_m_vgLines[index].visible: dBox_g_m_vgLines[index].visible = True
                    dBox_g_mgx_vgLines[index].x  = xPos
                    dBox_g_mgx_vgLines[index].x2 = xPos
                    if not dBox_g_mgx_vgLines[index].visible: dBox_g_mgx_vgLines[index].visible = True
                    #[3-2-1-4]: Texts Update
                    if self.verticalGrid_intervalID <= 11: #Maximum 12 Hours Interval
                        if timestamp_tz % 86400 == 0: dateStrFormat = "%m/%d"
                        else:                         dateStrFormat = "%H:%M"
                    elif self.verticalGrid_intervalID <= 14: #Maximum 1 Week Interval
                        if atmEta_Auxillaries.isNewMonth(timestamp_tz): dateStrFormat = "%Y/%m"
                        else:                                           dateStrFormat = "%m/%d"
                    elif self.verticalGrid_intervalID <= 17: #Maximum 6 Months Interval
                        if atmEta_Auxillaries.isNewYear(timestamp_tz): dateStrFormat = "%Y"
                        else:                                          dateStrFormat = "%Y/%m"
                    else:
                        dateStrFormat = "%Y"
                    dBox_g_mgx_vgTexts[index].setText(datetime.fromtimestamp(timestamp_tz, tz = timezone.utc).strftime(dateStrFormat))
                    dBox_g_mgx_vgTexts[index].moveTo(x = round(xPos/self.scaler-_GD_DISPLAYBOX_GRID_VERTICALTEXTWIDTH/2))
                    if dBox_g_mgx_vgTexts[index].hidden: dBox_g_mgx_vgTexts[index].show()
                #[3-2-2]: Inactive Grid
                else:
                    if dBox_g_m_vgLines[index].visible:      dBox_g_m_vgLines[index].visible   = False
                    if dBox_g_mgx_vgLines[index].visible:    dBox_g_mgx_vgLines[index].visible = False
                    if not dBox_g_mgx_vgTexts[index].hidden: dBox_g_mgx_vgTexts[index].hide()

        #[4]: Update Grid CamGroup Projections
        proj_x0 = (hvr_beg-vGridIntervals_current[0])*pixelPerTS
        proj_x1 = proj_x0+dBox_g['MAINGRID_X']['DRAWBOX'][2]*self.scaler
        dBox_g['MAIN']['VERTICALGRID_CAMGROUP'].updateProjection(projection_x0      =proj_x0, projection_x1=proj_x1)
        dBox_g['MAINGRID_X']['VERTICALGRID_CAMGROUP'].updateProjection(projection_x0=proj_x0, projection_x1=proj_x1)

    def __checkVerticalExtremas(self):
        #[1]: Instances
        prs_d       = self.periodicReports_display
        hvr_tssInVR = self.horizontalViewRange_timestampsInViewRange

        #[2]: Timestamps Check
        if not hvr_tssInVR:
            return False

        #[3]: Display Mode Check & Data Access Keys and Multiplier
        if self.displayMode not in _DATADRAWER_DISPLAYMODE_VERTICALEXTREMACHECKMODE:
            return False
        target_keys, multiplier = _DATADRAWER_DISPLAYMODE_VERTICALEXTREMACHECKMODE[self.displayMode]

        #[4]: Extremas Search
        pr_d_first = prs_d[hvr_tssInVR[0]]
        valMin = min(pr_d_first[key] for key in target_keys)
        valMax = max(pr_d_first[key] for key in target_keys)
        for ts in hvr_tssInVR:
            pr_d = prs_d[ts]
            for key in target_keys:
                val = pr_d[key]
                if val < valMin: valMin = val
                if valMax < val: valMax = val

        #[5]: Apply Multiplier
        if multiplier != 1:
            valMin *= multiplier
            valMax *= multiplier

        #[6]: Change Check & Result Return
        dBox_g_MAIN = self.displayBox_graphics['MAIN']
        if (self.verticalValue_min != valMin) or (self.verticalValue_max != valMax):
            #[4-1]: Vertical View Range Update
            if valMin == valMax:
                valMin = valMin-1
                valMax = valMax+1
            self.verticalValue_min = valMin
            self.verticalValue_max = valMax

            #[4-2]: Y Precision & RCLCG Precision Update (If Needed)
            vvrWidth_new    = self.verticalValue_max-self.verticalValue_min
            precision_y_new = math.floor(math.log10(10 / vvrWidth_new))+_VVR_PRECISIONCOMPENSATOR
            if _VVR_PRECISIONUPDATETHRESHOLD <= abs(self.verticalViewRange_precision-precision_y_new):
                self.verticalViewRange_precision = precision_y_new
                dBox_g_MAIN['RCLCG'].setPrecision(precision_x        = None, precision_y = precision_y_new, transferObjects = True)
                dBox_g_MAIN['RCLCG_XFIXED'].setPrecision(precision_x = None, precision_y = precision_y_new, transferObjects = True)
            return True
        return False

    def __onVerticalExtremaUpdate(self, updateType = 0):
        #[1]: Instances
        vv_min  = self.verticalValue_min
        vv_max  = self.verticalValue_max
        vvr     = self.verticalViewRange

        #[2]: View Range Delta & Limits
        veDelta = vv_max-vv_min
        vrHeight_new_min = veDelta*100/_GD_DISPLAYBOX_VVR_MAGNITUDE_MAX
        vrHeight_new_max = veDelta*100/_GD_DISPLAYBOX_VVR_MAGNITUDE_MIN

        #[3]: View Range Computation
        #---[3-1]: Updating By Drag
        if updateType == 0:
            vvrCenter_prev = (vvr[0]+vvr[1])/2
            vvrHeight_prev = vvr[1]-vvr[0]
            if vvrHeight_prev < vrHeight_new_min: 
                self.verticalViewRange               = [vvrCenter_prev-vrHeight_new_min*0.5, vvrCenter_prev+vrHeight_new_min*0.5]
                self.verticalViewRange_magnification = _GD_DISPLAYBOX_VVR_MAGNITUDE_MAX
            elif vrHeight_new_max < vvrHeight_prev: 
                self.verticalViewRange               = [vvrCenter_prev-vrHeight_new_max*0.5, vvrCenter_prev+vrHeight_new_max*0.5]
                self.verticalViewRange_magnification = _GD_DISPLAYBOX_VVR_MAGNITUDE_MIN
            else:
                self.verticalViewRange_magnification = round(veDelta/vvrHeight_prev*100, 1)
            vvr_0, vvr_1 = self.verticalViewRange
            if vvrHeight_prev == vvr_1-vvr_0: self.__onVViewRangeUpdate(0)
            else:                             self.__onVViewRangeUpdate(1)
        #---[3-2]: Updating By Jump
        elif updateType == 1:
            extremaCenter = (vv_min+vv_max)/2
            self.verticalViewRange_magnification = _GD_DISPLAYBOX_VVR_MAGNITUDE_MAX
            self.verticalViewRange               = [extremaCenter-vrHeight_new_min*0.5, extremaCenter+vrHeight_new_min*0.5]
            self.__onVViewRangeUpdate(1)
        
    #[2]: Vertical Position and Magnification
    #---Vertical Position
    def __editVPosition(self, delta_drag = None, delta_scroll = None):
        #[1]: New Position Calculation
        vvr_beg, vvr_end = self.verticalViewRange
        if   delta_drag   is not None: effectiveDelta = -delta_drag  *(vvr_end-vvr_beg)/self.displayBox_graphics['MAIN']['DRAWBOX'][3]
        elif delta_scroll is not None: effectiveDelta = -delta_scroll*(vvr_end-vvr_beg)/50
        else: return

        #[2]: View Range Update
        self.verticalViewRange = [vvr_beg+effectiveDelta, vvr_end+effectiveDelta]
        self.__onVViewRangeUpdate(0)
        
    #---Vertical Magnification
    def __editVMagFactor(self, delta_drag = None, delta_scroll = None, anchor = 'CENTER'):
        #[1]: New Magnification Calculation
        vvr_mag = self.verticalViewRange_magnification
        if   delta_drag   is not None: vvr_mag_new = vvr_mag + delta_drag*200/self.displayBox_graphics['MAIN']['DRAWBOX'][3]
        elif delta_scroll is not None: vvr_mag_new = vvr_mag + delta_scroll
        else: return

        #[2]: Rounding & Range Control
        vvr_mag_new = round(vvr_mag_new, 1)
        if   vvr_mag_new < _GD_DISPLAYBOX_VVR_MAGNITUDE_MIN: vvr_mag_new = _GD_DISPLAYBOX_VVR_MAGNITUDE_MIN
        elif _GD_DISPLAYBOX_VVR_MAGNITUDE_MAX < vvr_mag_new: vvr_mag_new = _GD_DISPLAYBOX_VVR_MAGNITUDE_MAX

        #[3]: Variation Check
        if vvr_mag_new == vvr_mag: return

        #[4]: Vertical View Range Update
        self.verticalViewRange_magnification = vvr_mag_new
        veHeight         = self.verticalValue_max-self.verticalValue_min
        veHeight_mag     = veHeight*100/vvr_mag_new
        vvr_beg, vvr_end = self.verticalViewRange
        if anchor == 'CENTER':
            vVRCenter     = (vvr_beg+vvr_end)/2
            vVR_effective = [vVRCenter-veHeight_mag*0.5, vVRCenter+veHeight_mag*0.5]
        elif anchor == 'BOTTOM': 
            vVR_effective = [vvr_beg, vvr_beg+veHeight_mag]
        elif anchor == 'TOP':    
            vVR_effective = [vvr_end-veHeight_mag, vvr_end]
        self.verticalViewRange = vVR_effective
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
        #[1]: Instances
        dBox         = self.displayBox_graphics
        dBox_g_main  = dBox['MAIN']
        dBox_g_grid  = dBox['MAINGRID_Y']
        vvr_0, vvr_1 = self.verticalViewRange
        hgi          = self.horizontalGridIntervals
        hgiHeight    = self.horizontalGridIntervalHeight
        nMaxHGLs     = self.nMaxHorizontalGridLines
        scaler       = self.scaler
        func_svf = atmEta_Auxillaries.simpleValueFormatter

        #[2]: Update RCLCGs Projections
        dBox_g_main['RCLCG'].updateProjection(projection_y0        = vvr_0, projection_y1 = vvr_1)
        dBox_g_main['RCLCG_XFIXED'].updateProjection(projection_y0 = vvr_0, projection_y1 = vvr_1)

        #[3]: Compute New Horizontal Grid Lines
        hgIntervals = None
        #---[3-1]: Non-Continuous Type
        if updateType == 1:
            #[3-1-1]: View Range Height Order Of Magnitude
            viewRangeHeight_OOM = math.floor(math.log((vvr_1-vvr_0), 10))
            #[3-1-2]: Most Appropriate Interval Factor Search
            for intervalFactor in (0.1, 0.25, 0.5, 0.75, 1, 2.5, 5, 7.5):
                #[3-1-2-1]: Interval Height Calculation & Check
                intervalHeight = intervalFactor*pow(10, viewRangeHeight_OOM)
                if intervalHeight == 0: continue
                #[3-1-2-2]: Grid Interval Lines Range
                idx_beg = math.floor((vvr_0-_VVR_HGLCENTER)/intervalHeight)
                idx_end = math.ceil((vvr_1 -_VVR_HGLCENTER)/intervalHeight)
                if nMaxHGLs < (idx_end - idx_beg + 1): continue
                #[3-1-2-3]: Horizontal Grid Line Intervals Determination
                hgIntervals                       = [_VVR_HGLCENTER+(intervalHeight*glIdx) for glIdx in range(idx_beg, idx_end+1)]
                self.horizontalGridIntervalHeight = intervalHeight
                break

        #---[3-2]: Continuous Type
        elif updateType == 0:
            #[3-2-1]: Current Horizontal Grid Intervals and Height
            idx_beg = math.floor((vvr_0-_VVR_HGLCENTER)/hgiHeight)
            idx_end = math.ceil((vvr_1 -_VVR_HGLCENTER)/hgiHeight)
            hgi_new_beg = _VVR_HGLCENTER + (idx_beg*hgiHeight)
            hgi_new_end = _VVR_HGLCENTER + (idx_end*hgiHeight)
            #[3-2-2]: Horizontal Grid Line Intervals Update Check & Determination
            if not hgi or (hgi[0] != hgi_new_beg) or (hgi[-1] != hgi_new_end):
                hgIntervals = [hgiHeight*glIdx for glIdx in range(idx_beg, idx_end+1)]

        #[4]: Unit Pixel Per Height
        ppuh = dBox_g_main['DRAWBOX'][3]*scaler / (vvr_1-vvr_0)

        #[5]: Update Grid Contents
        if hgIntervals is not None:
            #[5-1]: Update Graphics
            for glIndex in range (nMaxHGLs):
                #[5-1-1]: Instances
                dBox_g_main_hg_lines = dBox_g_main['HORIZONTALGRID_LINES'][glIndex]
                dBox_g_grid_hg_lines = dBox_g_grid['HORIZONTALGRID_LINES'][glIndex]
                dBox_g_grid_hg_texts = dBox_g_grid['HORIZONTALGRID_TEXTS'][glIndex]
                #[5-2]: Active Intervals
                if (glIndex < len(hgIntervals)) and (vvr_0 <= hgIntervals[glIndex] <= vvr_1):
                    #[5-2-1]: Position
                    verticalValue = hgIntervals[glIndex]
                    yPos_Line     = round((verticalValue-hgIntervals[0])*ppuh, 1)
                    #[5-2-2]: Grid Lines Update
                    dBox_g_main_hg_lines.y  = yPos_Line
                    dBox_g_main_hg_lines.y2 = yPos_Line
                    dBox_g_grid_hg_lines.y  = yPos_Line
                    dBox_g_grid_hg_lines.y2 = yPos_Line
                    if not dBox_g_main_hg_lines.visible: dBox_g_main_hg_lines.visible = True
                    if not dBox_g_grid_hg_lines.visible: dBox_g_grid_hg_lines.visible = True
                    if abs(verticalValue - _VVR_HGLCENTER) < 1e-9:
                        dBox_g_main_hg_lines.color = self.gridColor_Heavy
                        dBox_g_main_hg_lines.width = 1.5
                    else:
                        dBox_g_main_hg_lines.color = self.gridColor
                        dBox_g_main_hg_lines.width = 1
                    #[5-2-3]: Grid Text Update
                    if verticalValue == 0: vv_str = "0"
                    else:                  vv_str = func_svf(value = verticalValue, precision = 3)
                    dBox_g_grid_hg_texts.setText(vv_str)
                    dBox_g_grid_hg_texts.moveTo(y = round((yPos_Line)/scaler-_GD_DISPLAYBOX_GRID_HORIZONTALTEXTHEIGHT/2))
                    if dBox_g_grid_hg_texts.hidden: dBox_g_grid_hg_texts.show()
                #[5-3]: Inactive Intervals
                else:
                    if dBox_g_main_hg_lines.visible:    dBox_g_main_hg_lines.visible = False
                    if dBox_g_grid_hg_lines.visible:    dBox_g_grid_hg_lines.visible = False
                    if not dBox_g_grid_hg_texts.hidden: dBox_g_grid_hg_texts.hide()

            #[5-3]: Update Horizontal Grid Intervals
            self.horizontalGridIntervals = hgIntervals

        #[6]: Update Grid Camera Groups Projections
        if self.horizontalGridIntervals:
            proj_y0 = (vvr_0-self.horizontalGridIntervals[0])*ppuh
            proj_y1 = proj_y0+dBox_g_main['DRAWBOX'][3]*scaler
            dBox_g_main['HORIZONTALGRID_CAMGROUP'].updateProjection(projection_y0=proj_y0, projection_y1=proj_y1)
            dBox_g_grid['HORIZONTALGRID_CAMGROUP'].updateProjection(projection_y0=proj_y0, projection_y1=proj_y1)
    #View Control END -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    


    #Targe Data -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def setTarget(self, target):
        if target is None:
            self.target        = None
            self.assetName     = None
            self.fetchComplete = False
            self.fetching      = False
            self.fetching_RID  = None
            self.frameSprites['DATALOADINGCOVER'].visible = False
            self.dataLoadingGaugeBar.hide()
            self.dataLoadingTextBox.hide()
            self.dataLoadingTextBox_perc.hide()
            self.periodicReports       = dict()
            self.periodicReports_display       = dict()
            self.drawQueue        = set()
            self.drawn            = set()
            self.drawRemovalQueue = set()
        else:
            targetID, assetName, targetType = target
            if   targetType == 'SIMULATION': targetInstance = self.ipcA.getPRD(processName = 'SIMULATIONMANAGER', prdAddress = ('SIMULATIONS', targetID))
            elif targetType == 'ACCOUNT':    targetInstance = self.ipcA.getPRD(processName = 'TRADEMANAGER',      prdAddress = ('ACCOUNTS',    targetID))
            self.target    = (targetID, targetInstance, targetType)
            self.assetName = assetName
            self.fetchComplete = False
            self.fetching      = True
            if targetType == 'SIMULATION':
                self.fetching_RID = self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                                                           functionID     = 'fetchSimulationPeriodicReports', 
                                                           functionParams = {'simulationCode': targetID}, 
                                                           farrHandler    = self.__setTarget_onPeriodicReportsFetchResponse_FARR)
            elif targetType == 'ACCOUNT':
                self.fetching_RID = self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                                                           functionID     = 'fetchAccountPeriodicReports', 
                                                           functionParams = {'localID': targetID}, 
                                                           farrHandler    = self.__setTarget_onPeriodicReportsFetchResponse_FARR)
            self.frameSprites['DATALOADINGCOVER'].visible = True
            self.dataLoadingGaugeBar.show()
            self.dataLoadingTextBox.show()
            self.dataLoadingTextBox_perc.show()
            self.dataLoadingTextBox.updateText(self.visualManager.getTextPack('GUIO_PERIODICREPORTVIEWER:FETCHINGPERIODICREPORTS'))
            self.dataLoadingTextBox_perc.updateText("-")
            self.periodicReports       = dict()
            self.periodicReports_display       = dict()
            self.drawQueue        = set()
            self.drawn            = set()
            self.drawRemovalQueue = set()
        self.__dataDrawer_RemoveDrawings()
        self.__initializeRCLCG()

    def __setTarget_onPeriodicReportsFetchResponse_FARR(self, responder, requestID, functionResult):
        #[1]: Responder Check
        if not responder == 'DATAMANAGER': return

        #[2]: Fetch RID Check
        if requestID != self.fetching_RID: return

        #[3]: Target Check
        if self.target is None: return
        targetID, targetInstance, targetType = self.target
        if   targetType == 'SIMULATION': fr_targetID = functionResult.get('simulationCode', None)
        elif targetType == 'ACCOUNT':    fr_targetID = functionResult.get('localID',        None)
        if fr_targetID != targetID: return

        #[4]: Results Interpretation
        result          = functionResult['result']
        periodicReports = functionResult['periodicReports']
        failureType     = functionResult['failureType']
        if result:
            #[4-1]: Import Reports Data
            for prTS, pr in periodicReports.items():
                self.periodicReports[prTS] = pr[self.assetName]

            #[4-2]: Generate Display Data
            self.__generateDisplayData()

            #[4-3]: Fetch Control Variables Reset
            self.fetchComplete = True
            self.fetching      = False

            #[4-4]: Graphics Update
            self.frameSprites['DATALOADINGCOVER'].visible = False
            self.dataLoadingGaugeBar.hide()
            self.dataLoadingTextBox.hide()
            self.dataLoadingTextBox_perc.hide()

            #[4-5]: View Range Update
            self.horizontalViewRange_magnification = _GD_DISPLAYBOX_MAIN_HVR_MINMAGNITUDE
            hvr_new_beg = self.periodicReports_display_timestamps[0]-self.expectedKlineTemporalWidth*5
            hvr_new_end = round(hvr_new_beg+(self.horizontalViewRange_magnification*self.horizontalViewRangeWidth_m+self.horizontalViewRangeWidth_b))
            hvr_new = [hvr_new_beg, hvr_new_end]
            tz_rev  = -self.timezoneDelta
            if hvr_new[0] < tz_rev: hvr_new = [tz_rev, hvr_new[1]-hvr_new[0]+tz_rev]
            self.horizontalViewRange = [hvr_new_beg, hvr_new_end]
            self.__onHViewRangeUpdate(1)
            self.__editVVR_toExtremaCenter()

            #[4-6]: Draw Queue Update
            vvr_beg, vvr_end = self.horizontalViewRange
            for ts in self.periodicReports_display:
                t_open  = ts
                t_close = atmEta_Auxillaries.getNextIntervalTickTimestamp(intervalID = self.intervalID, timestamp = t_open, mrktReg = None, nTicks = 1)-1
                classification = 0
                classification += 0b1000*(0 <= t_open -vvr_beg)
                classification += 0b0100*(0 <= t_open -vvr_end)
                classification += 0b0010*(0 <  t_close-vvr_beg)
                classification += 0b0001*(0 <  t_close-vvr_end)
                if classification in (0b0010, 0b1010, 0b1011, 0b0011): 
                    self.drawQueue.add(t_open)
        else:
            print(termcolor.colored(f"[GUI-{self.name}] A failure returned from DATAMANAGER while attempting to fetch periodic reports for account '{fr_targetID}'.\n *", 'light_red'), termcolor.colored(failureType, 'light_red'))
            self.fetching_RID = None

    #Kline Data END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
    def getGroupRequirement(): 
        return 30
#'tradeLogViewer' END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

