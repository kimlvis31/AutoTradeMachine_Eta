#ATM Modules
import ipc
import auxiliaries
from GUI.generals import passiveGraphics_wrapperTypeC,\
                         textBox_typeA,\
                         imageBox_typeA,\
                         button_typeA,\
                         button_typeB,\
                         switch_typeC,\
                         textInputBox_typeA,\
                         selectionBox_typeB,\
                         selectionBox_typeC
from GUI.chart_drawer_account_viewer import chartDrawer_accountViewer
from GUI.periodic_report_viewer      import periodicReportViewer

#Python Modules
import pyglet
import termcolor
import time
import json
from datetime import datetime, timezone

#Constants
_IPC_THREADTYPE_MT = ipc._THREADTYPE_MT
_IPC_THREADTYPE_AT = ipc._THREADTYPE_AT

_ASSETPRECISIONS    = {'USDT': 8, 'USDC': 8, 'BTC': 6}
_ASSETPRECISIONS_S  = {'USDT': 4, 'USDC': 4, 'BTC': 4}
_ASSETPRECISIONS_XS = {'USDT': 2, 'USDC': 2, 'BTC': 2}

_CLOCK_UPDATE_INTERVAL_NS = 100e6

#SETUP PAGE <MAIN> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setupPage(self):
    #Set page unique variables
    self.puVar['accounts']                                 = dict()
    self.puVar['accounts_selected']                        = None
    self.puVar['currencyAnalysis']                         = dict()
    self.puVar['historyView_selected']                     = 'POSITIONCHART'
    self.puVar['historyView_tradeLogsFetchRID']            = None
    self.puVar['historyView_tradeLogs']                    = None
    self.puVar['historyView_tradeLogs_availableAssets']    = None
    self.puVar['historyView_tradeLogs_availablePositions'] = None
    self.puVar['clock_lastUpdated_ns']                     = 0

    #Setup Functions
    self.pageAuxillaryFunctions = __generateAuxillaryFunctions(self) #Generate auxillary functions
    self.pageLoadFunction       = __pageLoadFunction                 #Set page load function
    self.pageEscapeFunction     = __pageEscapeFunction               #Set page escape function
    self.pageProcessFunction    = __pageProcessFunction              #Set page process function
    self.pageObjectFunctions    = __generateObjectFunctions(self)    #Generate object functions

    #Setup a pyglet group for background
    self.groups['BACKGROUND'] = pyglet.graphics.Group(order = 0)

    #Generate guioInitialization base instances
    inst = {'windowInstance':      self.windowInstance,
            'displaySpaceDefiner': self.displaySpaceDefiner,
            'guioConfig':          self.guioConfig,
            'batch':               self.batch,
            'scaler':              self.displaySpaceDefiner['scaler'],
            'imageManager':        self.imageManager,
            'audioManager':        self.audioManager,
            'visualManager':       self.visualManager,
            'sysFunctions':        self.sysFunctions,
            'ipcA':                self.ipcA}

    #GUIO Initializations
    if (self.displaySpaceDefiner['ratio'] == '16:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 16000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
        self.GUIOs["TITLETEXT_ACCOUNTHISTORY"] = textBox_typeA(**inst, groupOrder=1, xPos= 5000, yPos=8550, width=6000, height=400, style=None, text=self.visualManager.getTextPack('ACCOUNTHISTORY:TITLE'), fontSize = 220, textInteractable = False)

        self.GUIOs["BUTTON_MOVETO_DASHBOARD"] = button_typeB(**inst, groupOrder=2, xPos=50, yPos=8650, width= 300, height=300, style="styleB", releaseFunction=self.pageObjectFunctions['PAGEMOVE_DASHBOARD'], image = 'dashboardIcon_512x512.png', imageSize = (225, 225), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))

        #[1]: Accounts
        #[1-1]: Accounts List
        if (True):
            self.GUIOs["BLOCKTITLE_ACCOUNTSLIST"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=8350, width=3900, height=200, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:BLOCKTITLE_ACCOUNTSLIST'), fontSize = 80)
            self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_VIRTUAL"] = switch_typeC(**inst,       groupOrder=1, xPos= 100, yPos=8000, width=1900, height= 250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTLIST_VIRTUAL'), fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_ACCOUNTLIST_FILTERSWITCH_VIRTUAL'])
            self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_ACTUAL"]  = switch_typeC(**inst,       groupOrder=1, xPos=2100, yPos=8000, width=1900, height= 250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTLIST_ACTUAL'),  fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_ACCOUNTLIST_FILTERSWITCH_ACTUAL'])
            self.GUIOs["ACCOUNTSLIST_SELECTIONBOX"]         = selectionBox_typeC(**inst, groupOrder=1, xPos= 100, yPos=2150, width=3900, height=5750, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_LIST_ACCOUNT'], 
                                                                                 elementWidths = (450, 1600, 800, 800))
            self.GUIOs["ACCOUNTSLIST_SELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTLIST_INDEX')},
                                                                                     {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTLIST_LOCALID')},
                                                                                     {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTLIST_TYPE')},
                                                                                     {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTLIST_STATUS')}])
        #[1-2}: Accounts Information & Control
        if (True):
            self.GUIOs["BLOCKTITLE_ACCOUNTSINFORMATION"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=1850, width=3900, height=200, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:BLOCKTITLE_ACCOUNTSINFORMATION'), fontSize = 80)
            #---Local ID
            self.GUIOs["ACCOUNTSINFORMATION_LOCALIDTITLETEXT"]       = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=1500, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTSINFORMATION_LOCALID'),      fontSize=80, textInteractable=False)
            self.GUIOs["ACCOUNTSINFORMATION_LOCALIDDISPLAYTEXT"]     = textBox_typeA(**inst, groupOrder=1, xPos=1400, yPos=1500, width=2600, height=250, style="styleA", text="-",                                                                             fontSize=80, textInteractable=False)
            #---Binance UserID
            self.GUIOs["ACCOUNTSINFORMATION_BINANCEUIDTITLETEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=1150, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTSINFORMATION_BINANCEUID'),   fontSize=80, textInteractable=False)
            self.GUIOs["ACCOUNTSINFORMATION_BINANCEUIDDISPLAYTEXT"]  = textBox_typeA(**inst, groupOrder=1, xPos=1400, yPos=1150, width=2600, height=250, style="styleA", text="-",                                                                             fontSize=80, textInteractable=False)
            #---Account Type
            self.GUIOs["ACCOUNTSINFORMATION_ACCOUNTTYPETITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos= 800, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTSINFORMATION_ACCOUNTTYPE'),  fontSize=80, textInteractable=False)
            self.GUIOs["ACCOUNTSINFORMATION_ACCOUNTTYPEDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=1400, yPos= 800, width=2600, height=250, style="styleA", text="-",                                                                             fontSize=80, textInteractable=False)
            #---Status
            self.GUIOs["ACCOUNTSINFORMATION_STATUSTITLETEXT"]        = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos= 450, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTSINFORMATION_STATUS'),       fontSize=80, textInteractable=False)
            self.GUIOs["ACCOUNTSINFORMATION_STATUSDISPLAYTEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos=1400, yPos= 450, width=2600, height=250, style="styleA", text="-",                                                                             fontSize=80, textInteractable=False)
            #---Trade Status
            self.GUIOs["ACCOUNTSINFORMATION_TRADESTATUSTITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos= 100, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:ACCOUNTSINFORMATION_TRADESTATUS'),  fontSize=80, textInteractable=False)
            self.GUIOs["ACCOUNTSINFORMATION_TRADESTATUSDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=1400, yPos= 100, width=2600, height=250, style="styleA", text="-",                                                                             fontSize=80, textInteractable=False) 
        
        #[2]: History
        if (True):
            self.GUIOs["BLOCKTITLE_HISTORY"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=4100, yPos=8350, width=11800, height=200, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:BLOCKTITLE_HISTORY'), fontSize = 80)
            self.GUIOs["HISTORY_VIEWTITLETEXT"]    = textBox_typeA(**inst,      groupOrder= 1, xPos=4100, yPos=8000, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_VIEWTYPE'), fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_VIEWSELECTIONBOX"] = selectionBox_typeB(**inst, groupOrder=51, xPos=5700, yPos=8000, width=2300, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_HISTORY_VIEW'])
            _viewTypes = {'POSITIONCHART':   {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_VIEWTYPE_POSITIONCHART')},
                          'PERIODICREPORTS': {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_VIEWTYPE_PERIODICREPORTS')},
                          'TRADELOGS':       {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_VIEWTYPE_TRADELOGS')}}
            self.GUIOs["HISTORY_VIEWSELECTIONBOX"].setSelectionList(selectionList = _viewTypes, displayTargets = 'all')
            self.GUIOs["HISTORY_VIEWSELECTIONBOX"].setSelected(itemKey = 'POSITIONCHART', callSelectionUpdateFunction = False)
            self.GUIOs["HISTORY_ASSETTITLETEXT"]       = textBox_typeA(**inst,      groupOrder=1,  xPos=8100, yPos=8000, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_ASSET'), fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_ASSETSELECTIONBOX"]    = selectionBox_typeB(**inst, groupOrder=51, xPos=9400, yPos=8000, width=2050, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_HISTORY_ASSET'])
            _assetSelections = {'#ALL#': {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_SELECTIONBOX_ALL')}}
            self.GUIOs["HISTORY_ASSETSELECTIONBOX"].setSelectionList(selectionList = _assetSelections, displayTargets = 'all')
            self.GUIOs["HISTORY_ASSETSELECTIONBOX"].setSelected(itemKey = '#ALL#', callSelectionUpdateFunction = False)
            self.GUIOs["HISTORY_ASSETSELECTIONBOX"].deactivate()
            self.GUIOs["HISTORY_ASSETIMAGEBOX"]        = imageBox_typeA(**inst,     groupOrder=1,  xPos=11550, yPos=8000, width= 250, height=250, style=None, image="assetTotalIcon_512x512.png")
            self.GUIOs["HISTORY_POSITIONTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1,  xPos=11900, yPos=8000, width=1400, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_POSITION'), fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_POSITIONSELECTIONBOX"] = selectionBox_typeB(**inst, groupOrder=51, xPos=13400, yPos=8000, width=2500, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_HISTORY_POSITION'])
            _positionSelections = {'#ALL#': {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_SELECTIONBOX_ALL'), 'textAnchor': 'W'}}
            self.GUIOs["HISTORY_POSITIONSELECTIONBOX"].setSelectionList(selectionList = _positionSelections, displayTargets = 'all')
            self.GUIOs["HISTORY_POSITIONSELECTIONBOX"].setSelected(itemKey = '#ALL#', callSelectionUpdateFunction = False)
            self.GUIOs["HISTORY_POSITIONSELECTIONBOX"].deactivate()
            self.puVar['GUIOGROUPS'] = dict()
        #[2-1]: Position Chart
        if (True):
            #---CA Viewer
            self.GUIOs["HISTORY_POSITIONCHART_CHARTDRAWER"] = chartDrawer_accountViewer(**inst, groupOrder=1, xPos=4100, yPos=1850, width=11800, height=6050, style="styleA", name = 'ACCOUNTHISTORY_HISTORY_POSITIONCHART_CHARTDRAWER')
            #---Position Data
            self.GUIOs["HISTORY_POSITIONCHART_TRADINGTITLETEXT"]            = textBox_typeA(**inst, groupOrder=1, xPos= 4100, yPos=1500, width=1325, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_POSITIONCHART_TRADING'),          fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_POSITIONCHART_TRADINGDISPLAYTEXT"]          = textBox_typeA(**inst, groupOrder=1, xPos= 5525, yPos=1500, width=1450, height=250, style="styleA", text="-",                                                                                     fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_POSITIONCHART_LEVERAGETITLETEXT"]           = textBox_typeA(**inst, groupOrder=1, xPos= 7075, yPos=1500, width=1325, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_POSITIONCHART_LEVERAGE'),         fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_POSITIONCHART_LEVERAGEDISPLAYTEXT"]         = textBox_typeA(**inst, groupOrder=1, xPos= 8500, yPos=1500, width=1450, height=250, style="styleA", text="-",                                                                                     fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_POSITIONCHART_MARGINMODETITLETEXT"]         = textBox_typeA(**inst, groupOrder=1, xPos=10050, yPos=1500, width=1325, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_POSITIONCHART_MARGINMODE'),       fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_POSITIONCHART_MARGINMODEDISPLAYTEXT"]       = textBox_typeA(**inst, groupOrder=1, xPos=11475, yPos=1500, width=1450, height=250, style="styleA", text="-",                                                                                     fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_POSITIONCHART_QUANTITYTITLETEXT"]           = textBox_typeA(**inst, groupOrder=1, xPos=13025, yPos=1500, width=1325, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_POSITIONCHART_QUANTITY'),         fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_POSITIONCHART_QUANTITYDISPLAYTEXT"]         = textBox_typeA(**inst, groupOrder=1, xPos=14450, yPos=1500, width=1450, height=250, style="styleA", text="-",                                                                                     fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_POSITIONCHART_ENTRYPRICETITLETEXT"]         = textBox_typeA(**inst, groupOrder=1, xPos= 4100, yPos=1150, width=1325, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_POSITIONCHART_ENTRYPRICE'),       fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_POSITIONCHART_ENTRYPRICEDISPLAYTEXT"]       = textBox_typeA(**inst, groupOrder=1, xPos= 5525, yPos=1150, width=1450, height=250, style="styleA", text="-",                                                                                     fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_POSITIONCHART_CURRENTPRICETITLETEXT"]       = textBox_typeA(**inst, groupOrder=1, xPos= 7075, yPos=1150, width=1325, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_POSITIONCHART_CURRENTPRICE'),     fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_POSITIONCHART_CURRENTPRICEDISPLAYTEXT"]     = textBox_typeA(**inst, groupOrder=1, xPos= 8500, yPos=1150, width=1450, height=250, style="styleA", text="-",                                                                                     fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_POSITIONCHART_LIQUIDATIONPRICETITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos=10050, yPos=1150, width=1325, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_POSITIONCHART_LIQUIDATIONPRICE'), fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_POSITIONCHART_LIQUIDATIONPRICEDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=11475, yPos=1150, width=1450, height=250, style="styleA", text="-",                                                                                     fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_POSITIONCHART_UNREALIZEDPNLTITLETEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos=13025, yPos=1150, width=1325, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_POSITIONCHART_UNREALIZEDPNL'),    fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_POSITIONCHART_UNREALIZEDPNLDISPLAYTEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos=14450, yPos=1150, width=1450, height=250, style="styleA", text="-",                                                                                     fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_POSITIONCHART_ASSUMEDRATIOTITLETEXT"]       = textBox_typeA(**inst, groupOrder=1, xPos= 4100, yPos= 800, width=1325, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_POSITIONCHART_ASSUMEDRATIO'),     fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_POSITIONCHART_ASSUMEDRATIODISPLAYTEXT"]     = textBox_typeA(**inst, groupOrder=1, xPos= 5525, yPos= 800, width=1450, height=250, style="styleA", text="-",                                                                                     fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_POSITIONCHART_ALLOCATEDBALANCETITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 7075, yPos= 800, width=1325, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_POSITIONCHART_ALLOCATEDBALANCE'), fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_POSITIONCHART_ALLOCATEDBALANCEDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos= 8500, yPos= 800, width=1450, height=250, style="styleA", text="-",                                                                                     fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_POSITIONCHART_COMMITMENTRATETITLETEXT"]     = textBox_typeA(**inst, groupOrder=1, xPos=10050, yPos= 800, width=1325, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_POSITIONCHART_COMMITMENTRATE'),   fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_POSITIONCHART_COMMITMENTRATEDISPLAYTEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos=11475, yPos= 800, width=1450, height=250, style="styleA", text="-",                                                                                     fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_POSITIONCHART_RISKLEVELTITLETEXT"]          = textBox_typeA(**inst, groupOrder=1, xPos=13025, yPos= 800, width=1325, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_POSITIONCHART_RISKLEVEL'),        fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_POSITIONCHART_RISKLEVELDISPLAYTEXT"]        = textBox_typeA(**inst, groupOrder=1, xPos=14450, yPos= 800, width=1450, height=250, style="styleA", text="-",                                                                                     fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_POSITIONCHART_TRADECONTROLTITLETEXT"]       = textBox_typeA(**inst, groupOrder=1, xPos= 4100, yPos= 450, width= 1325, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_POSITIONCHART_TRADECONTROL'),    fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_POSITIONCHART_TRADECONTROLDISPLAYTEXT"]     = textBox_typeA(**inst, groupOrder=1, xPos= 5525, yPos= 450, width=10375, height=250, style="styleA", text="-",                                                                                    fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_POSITIONCHART_ACRTITLETEXT"]                = textBox_typeA(**inst, groupOrder=1, xPos= 4100, yPos= 100, width= 1325, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_POSITIONCHART_ACR'),             fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_POSITIONCHART_ACRDISPLAYTEXT"]              = textBox_typeA(**inst, groupOrder=1, xPos= 5525, yPos= 100, width=10375, height=250, style="styleA", text="-",                                                                                    fontSize=80, textInteractable=True)
            #---%GUIOGROUPS%
            self.puVar['GUIOGROUPS']['POSITIONCHART'] = ["HISTORY_POSITIONCHART_CHARTDRAWER",
                                                         "HISTORY_POSITIONCHART_TRADINGTITLETEXT",
                                                         "HISTORY_POSITIONCHART_TRADINGDISPLAYTEXT",
                                                         "HISTORY_POSITIONCHART_LEVERAGETITLETEXT",
                                                         "HISTORY_POSITIONCHART_LEVERAGEDISPLAYTEXT",
                                                         "HISTORY_POSITIONCHART_MARGINMODETITLETEXT",
                                                         "HISTORY_POSITIONCHART_MARGINMODEDISPLAYTEXT",
                                                         "HISTORY_POSITIONCHART_QUANTITYTITLETEXT",
                                                         "HISTORY_POSITIONCHART_QUANTITYDISPLAYTEXT",
                                                         "HISTORY_POSITIONCHART_ENTRYPRICETITLETEXT",
                                                         "HISTORY_POSITIONCHART_ENTRYPRICEDISPLAYTEXT",
                                                         "HISTORY_POSITIONCHART_CURRENTPRICETITLETEXT",
                                                         "HISTORY_POSITIONCHART_CURRENTPRICEDISPLAYTEXT",
                                                         "HISTORY_POSITIONCHART_LIQUIDATIONPRICETITLETEXT",
                                                         "HISTORY_POSITIONCHART_LIQUIDATIONPRICEDISPLAYTEXT",
                                                         "HISTORY_POSITIONCHART_UNREALIZEDPNLTITLETEXT",
                                                         "HISTORY_POSITIONCHART_UNREALIZEDPNLDISPLAYTEXT",
                                                         "HISTORY_POSITIONCHART_ASSUMEDRATIOTITLETEXT",
                                                         "HISTORY_POSITIONCHART_ASSUMEDRATIODISPLAYTEXT",
                                                         "HISTORY_POSITIONCHART_ALLOCATEDBALANCETITLETEXT",
                                                         "HISTORY_POSITIONCHART_ALLOCATEDBALANCEDISPLAYTEXT",
                                                         "HISTORY_POSITIONCHART_COMMITMENTRATETITLETEXT",
                                                         "HISTORY_POSITIONCHART_COMMITMENTRATEDISPLAYTEXT",
                                                         "HISTORY_POSITIONCHART_RISKLEVELTITLETEXT",
                                                         "HISTORY_POSITIONCHART_RISKLEVELDISPLAYTEXT",
                                                         "HISTORY_POSITIONCHART_TRADECONTROLTITLETEXT",
                                                         "HISTORY_POSITIONCHART_TRADECONTROLDISPLAYTEXT",
                                                         "HISTORY_POSITIONCHART_ACRTITLETEXT",
                                                         "HISTORY_POSITIONCHART_ACRDISPLAYTEXT",
                                                         ]
            for _guioName in self.puVar['GUIOGROUPS']['POSITIONCHART']: self.GUIOs[_guioName].show()
        #[2-2]: Periodic Report
        if (True):
            #---Daily Report Viewer
            self.GUIOs["HISTORY_PERIODICREPORT_PERIODICREPORTVIEWER"] = periodicReportViewer(**inst, groupOrder=1, xPos=4100, yPos=100, width=11800, height=7800, style="styleA", name = 'ACCOUNTHISTORY_HISTORY_PERIODICREPORT_PERIODICREPORTVIEWER')
            #---%GUIOGROUPS%
            self.puVar['GUIOGROUPS']['PERIODICREPORTS'] = ["HISTORY_PERIODICREPORT_PERIODICREPORTVIEWER",]
            for _guioName in self.puVar['GUIOGROUPS']['PERIODICREPORTS']: self.GUIOs[_guioName].hide()
        #[2-3]: Trade Logs
        if (True):
            #---Filters & Summary
            self.GUIOs["HISTORY_TRADELOGS_NETPROFITTITLETEXT"]           = textBox_typeA(**inst,      groupOrder=1, xPos= 4100, yPos=7650, width=1100, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_NETPROFIT'),   fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_TRADELOGS_NETPROFITDISPLAYTEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos= 5300, yPos=7650, width=1525, height=250, style="styleA", text="-",                                                                            fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_GAINTITLETEXT"]                = textBox_typeA(**inst,      groupOrder=1, xPos= 6925, yPos=7650, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_GAIN'),        fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_TRADELOGS_GAINDISPLAYTEXT"]              = textBox_typeA(**inst,      groupOrder=1, xPos= 8025, yPos=7650, width=1925, height=250, style="styleA", text="-",                                                                            fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_LOSSTITLETEXT"]                = textBox_typeA(**inst,      groupOrder=1, xPos=10050, yPos=7650, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_LOSS'),        fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_TRADELOGS_LOSSDISPLAYTEXT"]              = textBox_typeA(**inst,      groupOrder=1, xPos=11150, yPos=7650, width=1925, height=250, style="styleA", text="-",                                                                            fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_TRADINGFEETITLETEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos=13175, yPos=7650, width=1100, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_TRADINGFEE'),  fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_TRADELOGS_TRADINGFEEDISPLAYTEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos=14375, yPos=7650, width=1525, height=250, style="styleA", text="-",                                                                            fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_NTOTALLOGSTITLETEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos= 4100, yPos=7300, width=1700, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_TOTAL'),       fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_TRADELOGS_NTOTALLOGSDISPLAYTEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos= 5900, yPos=7300, width=2400, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_NASSETLOGSTITLETEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos= 8400, yPos=7300, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ASSET'),       fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_TRADELOGS_NASSETLOGSDISPLAYTEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos= 9800, yPos=7300, width=2300, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_NPOSITIONLOGSTITLETEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos=12200, yPos=7300, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_POSITION'),    fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_TRADELOGS_NPOSITIONLOGSDISPLAYTEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos=13600, yPos=7300, width=2300, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERTITLETEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos= 4100, yPos=6950, width=2280, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_TIMEUTC'),     fontSize=80, textInteractable=False)
            self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERINPUTTEXT1"]         = textInputBox_typeA(**inst, groupOrder=1, xPos= 6480, yPos=6950, width=2280, height=250, style="styleA", text="",                                                                             fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_TRADELOGS_TIMEFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERINPUTTEXT2"]         = textInputBox_typeA(**inst, groupOrder=1, xPos= 8860, yPos=6950, width=2280, height=250, style="styleA", text="",                                                                             fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_TRADELOGS_TIMEFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERAPPLYBUTTON"]        = button_typeA(**inst,       groupOrder=1, xPos=11240, yPos=6950, width=2280, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_SEARCH'),      fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_TRADELOGS_TIMEFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERAPPLYBUTTON"].deactivate()
            self.GUIOs["HISTORY_TRADELOGS_NTIMELOGSDISPLAYTEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos=13620, yPos=6950, width=2280, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_SIDEFILTERBUY"]                = switch_typeC(**inst,       groupOrder=1, xPos= 4100, yPos=6600, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_BUY'),         switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NBUYDISPLAYTEXT"]              = textBox_typeA(**inst,      groupOrder=1, xPos= 5200, yPos=6600, width=1180, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_SIDEFILTERSELL"]               = switch_typeC(**inst,       groupOrder=1, xPos= 6480, yPos=6600, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_SELL'),        switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NSELLDISPLAYTEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos= 7580, yPos=6600, width=1180, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERLIQUIDATION"] = switch_typeC(**inst,       groupOrder=1, xPos= 8860, yPos=6600, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_LIQUIDATION'), switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NLIQUIDATIONDISPLAYTEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos= 9960, yPos=6600, width=1180, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERFSLIMMED"]    = switch_typeC(**inst,       groupOrder=1, xPos=11240, yPos=6600, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_FSLIMMED'),    switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NFSLIMMEDDISPLAYTEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos=12340, yPos=6600, width=1180, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERFSLCLOSE"]    = switch_typeC(**inst,       groupOrder=1, xPos=13620, yPos=6600, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_FSLCLOSE'),    switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NFSLCLOSEDISPLAYTEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos=14720, yPos=6600, width=1180, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERENTRY"]       = switch_typeC(**inst,       groupOrder=1, xPos= 4100, yPos=6250, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ENTRY'),       switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NENTRYDISPLAYTEXT"]            = textBox_typeA(**inst,      groupOrder=1, xPos= 5200, yPos=6250, width=1180, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERCLEAR"]       = switch_typeC(**inst,       groupOrder=1, xPos= 6480, yPos=6250, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_CLEAR'),       switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NCLEARDISPLAYTEXT"]            = textBox_typeA(**inst,      groupOrder=1, xPos= 7580, yPos=6250, width=1180, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTEREXIT"]        = switch_typeC(**inst,       groupOrder=1, xPos= 8860, yPos=6250, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_EXIT'),        switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NEXITDISPLAYTEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos= 9960, yPos=6250, width=1180, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERFORCECLEAR"]  = switch_typeC(**inst,       groupOrder=1, xPos=11240, yPos=6250, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_FORCECLEAR'),  switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NFORCECLEARDISPLAYTEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos=12340, yPos=6250, width=1180, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            self.GUIOs["HISTORY_TRADELOGS_LOGICSOURCEFILTERUNKNOWN"]     = switch_typeC(**inst,       groupOrder=1, xPos=13620, yPos=6250, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_UNKNOWN'),     switchStatus = True, fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'])
            self.GUIOs["HISTORY_TRADELOGS_NUNKNOWNDISPLAYTEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos=14720, yPos=6250, width=1180, height=250, style="styleA", text="- / -",                                                                        fontSize=80, textInteractable=True)
            #---Selection Box
            self.GUIOs["HISTORY_TRADELOGS_TRADELOGSELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=2, xPos=4100, yPos=100, width=11800, height=6050, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_TRADELOGS_TRADELOG'], 
                                                                                      elementWidths = (1100, 1200, 1400, 700, 700, 900, 900, 850, 850, 900, 800, 1250))
            self.GUIOs["HISTORY_TRADELOGS_TRADELOGSELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_INDEX')},          #1100
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_TIME')},           #1200
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_SYMBOL')},         #1400
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_LOGICSOURCE')},    # 700
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_SIDE')},           # 700
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_QUANTITY')},       # 900
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_PRICE')},          # 900
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_PROFIT')},         # 850
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_TRADINGFEE')},     # 850
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_TOTALQUANTITY')},  # 900
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_ENTRYPRICE')},     # 800
                                                                                                  {'text': self.visualManager.getTextPack('ACCOUNTHISTORY:HISTORY_TRADELOGS_ST_WALLETBALANCE')}]) #1250
            #---%GUIOGROUPS%
            self.puVar['GUIOGROUPS']['TRADELOGS'] = ["HISTORY_TRADELOGS_NETPROFITTITLETEXT",
                                                     "HISTORY_TRADELOGS_NETPROFITDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_GAINTITLETEXT",
                                                     "HISTORY_TRADELOGS_GAINDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_LOSSTITLETEXT",
                                                     "HISTORY_TRADELOGS_LOSSDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_TRADINGFEETITLETEXT",
                                                     "HISTORY_TRADELOGS_TRADINGFEEDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_NTOTALLOGSTITLETEXT",
                                                     "HISTORY_TRADELOGS_NTOTALLOGSDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_NASSETLOGSTITLETEXT",
                                                     "HISTORY_TRADELOGS_NASSETLOGSDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_NPOSITIONLOGSTITLETEXT",
                                                     "HISTORY_TRADELOGS_NPOSITIONLOGSDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_TIMEFILTERTITLETEXT",
                                                     "HISTORY_TRADELOGS_TIMEFILTERINPUTTEXT1",
                                                     "HISTORY_TRADELOGS_TIMEFILTERINPUTTEXT2",
                                                     "HISTORY_TRADELOGS_TIMEFILTERAPPLYBUTTON",
                                                     "HISTORY_TRADELOGS_NTIMELOGSDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_SIDEFILTERBUY",
                                                     "HISTORY_TRADELOGS_NBUYDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_SIDEFILTERSELL",
                                                     "HISTORY_TRADELOGS_NSELLDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_LOGICSOURCEFILTERLIQUIDATION",
                                                     "HISTORY_TRADELOGS_NLIQUIDATIONDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_LOGICSOURCEFILTERFSLIMMED",
                                                     "HISTORY_TRADELOGS_NFSLIMMEDDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_LOGICSOURCEFILTERFSLCLOSE",
                                                     "HISTORY_TRADELOGS_NFSLCLOSEDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_LOGICSOURCEFILTERENTRY",
                                                     "HISTORY_TRADELOGS_NENTRYDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_LOGICSOURCEFILTERCLEAR",
                                                     "HISTORY_TRADELOGS_NCLEARDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_LOGICSOURCEFILTEREXIT",
                                                     "HISTORY_TRADELOGS_NEXITDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_LOGICSOURCEFILTERFORCECLEAR",
                                                     "HISTORY_TRADELOGS_NFORCECLEARDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_LOGICSOURCEFILTERUNKNOWN",
                                                     "HISTORY_TRADELOGS_NUNKNOWNDISPLAYTEXT",
                                                     "HISTORY_TRADELOGS_TRADELOGSELECTIONBOX"]
            for _guioName in self.puVar['GUIOGROUPS']['TRADELOGS']: self.GUIOs[_guioName].hide()

        #[3]: Clock
        self.GUIOs["CLOCK_LOCAL"] = textBox_typeA(**inst, groupOrder=1, xPos= 14000, yPos=8800, width=1950, height=150, style=None, text="", anchor = 'E', fontSize = 80, textInteractable = False)
        self.GUIOs["CLOCK_UTC"]   = textBox_typeA(**inst, groupOrder=1, xPos= 14000, yPos=8650, width=1950, height=150, style=None, text="", anchor = 'E', fontSize = 80, textInteractable = False)

    elif (self.displaySpaceDefiner['ratio'] == '21:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 21000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
    elif (self.displaySpaceDefiner['ratio'] == '32:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 32000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
#SETUP PAGE <MAIN> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <LOAD> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageLoadFunction(self):
    #[1]: Instances
    puVar = self.puVar
    pafs  = self.pageAuxillaryFunctions
    func_addFARHandler = self.ipcA.addFARHandler
    func_getPRD        = self.ipcA.getPRD

    #[2]: FAR Registration
    func_addFARHandler('onAccountUpdate',          pafs['_FAR_ONACCOUNTUPDATE'],          executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #TRADEMANAGER
    func_addFARHandler('onCurrencyAnalysisUpdate', pafs['_FAR_ONCURRENCYANALYSISUPDATE'], executionThread = _IPC_THREADTYPE_MT, immediateResponse = True) #TRADEMANAGER
    
    #[3]: PRD Data
    puVar['accounts']         = func_getPRD(processName = 'TRADEMANAGER', prdAddress = 'ACCOUNTS')
    puVar['currencyAnalysis'] = func_getPRD(processName = 'TRADEMANAGER', prdAddress = 'CURRENCYANALYSIS')

    #[4]: Accounts List
    pafs['SETACCOUNTSLIST']() #Set Account List
    if puVar['accounts_selected'] not in puVar['accounts']:
        puVar['accounts_selected'] = None

    #[5]: Assets & Positions List
    pafs['SETASSETSLIST']()
    pafs['SETPOSITIONSLIST']()

    #[6]: View-Dependent Handling
    hv_sel = puVar['historyView_selected']
    if hv_sel == 'POSITIONCHART':   
        pafs['SETCHARTDRAWERTARGET']()
        pafs['UPDATEPOSITIONINFORMATION']()
    elif hv_sel == 'PERIODICREPORTS': 
        pafs['SETPERIODICREPORTSVIEWERTARGET']()
    elif hv_sel == 'TRADELOGS':       
        pafs['SETTRADELOGSLIST']()
#SETUP PAGE <LOAD> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <ESCAPE> --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageEscapeFunction(self):
    for fID in ('onAccountUpdate', 'onCurrencyAnalysisUpdate'):
        self.ipcA.removeFARHandler(functionID   = fID)
        self.ipcA.addDummyFARHandler(functionID = fID)
#SETUP PAGE <ESCAPE> END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <PROCESS> -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageProcessFunction(self, t_elapsed_ns, onLoad = False):
    #[1]: Instances
    puVar = self.puVar
    guios = self.GUIOs
    t_current_ns = time.perf_counter_ns()

    #[2]: Clock Update
    if _CLOCK_UPDATE_INTERVAL_NS <= t_current_ns-puVar['clock_lastUpdated_ns']:
        t_current_s = time.time()
        guios["CLOCK_LOCAL"].updateText(text = datetime.fromtimestamp(timestamp = t_current_s).strftime("[LOCAL] %Y/%m/%d %H:%M:%S.%f")[:-5])
        guios["CLOCK_UTC"].updateText(text   = datetime.fromtimestamp(timestamp = t_current_s, tz=timezone.utc).strftime("[UTC] %Y/%m/%d %H:%M:%S.%f")[:-5])
        puVar['clock_lastUpdated_ns'] = t_current_ns
#SETUP PAGE <PROCESS> END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#OBJECT FUNCTIONS -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateObjectFunctions(self):
    objFunctions = dict()

    #<Page Navigation>
    def __pageMove_DASHBOARD(objInstance, **kwargs): 
        self.sysFunctions['LOADPAGE']['function']('DASHBOARD')
    objFunctions['PAGEMOVE_DASHBOARD'] = __pageMove_DASHBOARD

    #<AccountsList>
    def __onStatusUpdate_AccountList_FilterSwitch_Virtual(objInstance, **kwargs):
        if (self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_ACTUAL"].getStatus() == True): self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_ACTUAL"].setStatus(status = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['ONACCOUNTSLISTFILTERUPDATE']()
    def __onStatusUpdate_AccountList_FilterSwitch_Actual(objInstance, **kwargs):
        if (self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_VIRTUAL"].getStatus() == True): self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_VIRTUAL"].setStatus(status = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['ONACCOUNTSLISTFILTERUPDATE']()
    def __onSelectionUpdate_List_Account(objInstance, **kwargs):
        try:    localID = objInstance.getSelected()[0]
        except: localID = None
        self.puVar['accounts_selected'] = localID
        self.pageAuxillaryFunctions['ONACCOUNTSELECTIONUPDATE']()
    objFunctions['ONSTATUSUPDATE_ACCOUNTLIST_FILTERSWITCH_VIRTUAL'] = __onStatusUpdate_AccountList_FilterSwitch_Virtual
    objFunctions['ONSTATUSUPDATE_ACCOUNTLIST_FILTERSWITCH_ACTUAL']  = __onStatusUpdate_AccountList_FilterSwitch_Actual
    objFunctions['ONSELECTIONUPDATE_LIST_ACCOUNT']                  = __onSelectionUpdate_List_Account

    #<History>
    def __onSelectionUpdate_History_View(objInstance, **kwargs): 
        _view_prev = self.puVar['historyView_selected']
        self.puVar['historyView_selected'] = self.GUIOs["HISTORY_VIEWSELECTIONBOX"].getSelected()
        self.pageAuxillaryFunctions['ONHISTORYVIEWUPDATE'](view_prev = _view_prev)
    def __onSelectionUpdate_History_Asset(objInstance, **kwargs): 
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        pafs  = self.pageAuxillaryFunctions
        assetName = guios["HISTORY_ASSETSELECTIONBOX"].getSelected()
        aImgBox   = guios["HISTORY_ASSETIMAGEBOX"]
        hv_sel    = puVar['historyView_selected']

        #[2]: Image Box Update
        if   assetName == '#ALL#': aImgBox.updateImage(image = "assetTotalIcon_512x512.png")
        elif assetName == 'USDT':  aImgBox.updateImage(image = "usdtIcon_512x512.png")
        elif assetName == 'USDC':  aImgBox.updateImage(image = "usdcIcon_512x512.png")

        #[3]: View-Dependent Responses
        if hv_sel == 'POSITIONCHART': 
            pafs['SETPOSITIONSLIST']()
            pafs['SETCHARTDRAWERTARGET']()
            pafs['UPDATEPOSITIONINFORMATION']()
        elif hv_sel == 'PERIODICREPORTS': 
            pafs['SETPERIODICREPORTSVIEWERTARGET']()
        elif hv_sel == 'TRADELOGS':
            pafs['SETPOSITIONSLIST']()
            pafs['ONTRADELOGSFILTERUPDATE']()
    def __onSelectionUpdate_History_Position(objInstance, **kwargs):
        #[1]: Instances
        puVar = self.puVar
        pafs  = self.pageAuxillaryFunctions
        hv_sel = puVar['historyView_selected']

        #[2]: View-Dependent Responses
        if hv_sel == 'POSITIONCHART':
            pafs['SETCHARTDRAWERTARGET']()
            pafs['UPDATEPOSITIONINFORMATION']()
        elif hv_sel == 'TRADELOGS':
            pafs['ONTRADELOGSFILTERUPDATE']()
    objFunctions['ONSELECTIONUPDATE_HISTORY_VIEW']     = __onSelectionUpdate_History_View
    objFunctions['ONSELECTIONUPDATE_HISTORY_ASSET']    = __onSelectionUpdate_History_Asset
    objFunctions['ONSELECTIONUPDATE_HISTORY_POSITION'] = __onSelectionUpdate_History_Position

    #<Trade Logs>
    def __onTextUpdate_TradeLogs_TimeFilter(objInstance, **kwargs):
        rangeBeg_str = self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERINPUTTEXT1"].getText()
        rangeEnd_str = self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERINPUTTEXT2"].getText()
        if (rangeBeg_str == ""): rangeBeg = float('-inf')
        else:
            try:    rangeBeg = datetime.strptime(rangeBeg_str, "%Y/%m/%d %H:%M:%S").timestamp()-time.timezone
            except: rangeBeg = None
        if (rangeEnd_str == ""): rangeEnd = float('inf')
        else:
            try:    rangeEnd = datetime.strptime(rangeEnd_str, "%Y/%m/%d %H:%M:%S").timestamp()-time.timezone
            except: rangeEnd = None
        if ((rangeBeg is not None) and (rangeEnd is not None) and (rangeBeg <= rangeEnd)): self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERAPPLYBUTTON"].activate()
        else:                                                                              self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERAPPLYBUTTON"].deactivate()
    def __onButtonRelease_TradeLogs_TimeFilter(objInstance, **kwargs):
        self.GUIOs["HISTORY_TRADELOGS_TIMEFILTERAPPLYBUTTON"].deactivate()
        self.pageAuxillaryFunctions['ONTRADELOGSFILTERUPDATE']()
    def __onStatusUpdate_TradeLogs_SwitchFilter(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONTRADELOGSFILTERUPDATE']()
    def __onSelectionUpdate_TradeLogs_TradeLog(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONTRADELOGSELECTIONUPDATE']()
    objFunctions['ONTEXTUPDATE_TRADELOGS_TIMEFILTER']     = __onTextUpdate_TradeLogs_TimeFilter
    objFunctions['ONBUTTONRELEASE_TRADELOGS_TIMEFILTER']  = __onButtonRelease_TradeLogs_TimeFilter
    objFunctions['ONSTATUSUPDATE_TRADELOGS_SWITCHFILTER'] = __onStatusUpdate_TradeLogs_SwitchFilter
    objFunctions['ONSELECTIONUPDATE_TRADELOGS_TRADELOG']  = __onSelectionUpdate_TradeLogs_TradeLog

    #Return the generated functions
    return objFunctions
#OBJECT FUNCTIONS END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUXILALRY FUNCTIONS --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateAuxillaryFunctions(self):
    auxFunctions = dict()
    
    #<_PAGELOAD>
    def __far_onAccountUpdate(requester, updateType, updatedContent):
        #[1]: Source Check
        if requester != 'TRADEMANAGER':
            return
        
        #[2]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        pafs  = self.pageAuxillaryFunctions
        func_getPRD = self.ipcA.getPRD

        #[3]: Update Handling
        #---[3-1]: Account Added
        if updateType == 'ADDED':
            localID = updatedContent
            puVar['accounts'][localID] = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('ACCOUNTS', localID))
            pafs['SETACCOUNTSLIST']()

        #---[3-2]: Account Removed
        elif updateType == 'REMOVED':
            localID = updatedContent
            pafs['SETACCOUNTSLIST']()
            if localID == puVar['accounts_selected']:
                puVar['accounts_selected'] = None
                pafs['ONACCOUNTSELECTIONUPDATE']()

        #---[3-3]: Status
        elif updateType == 'UPDATED_STATUS':
            localID = updatedContent
            status  = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('ACCOUNTS', localID, 'status'))
            puVar['accounts'][localID]['status'] = status
            #[3-3-1]: Selection Box Update
            if   status == 'INACTIVE': text = 'INACTIVE'; textColor = 'RED_LIGHT'
            elif status == 'ACTIVE':   text = 'ACTIVE';   textColor = 'GREEN_LIGHT'
            nsbi = {'text': text, 'textStyles': [('all', textColor),], 'textAnchor': 'CENTER'}
            guios["ACCOUNTSLIST_SELECTIONBOX"].editSelectionListItem(itemKey = localID, item = nsbi, columnIndex = 3)
            #[3-3-2]: Account Information Update
            if localID == puVar['accounts_selected']:
                if   status == 'ACTIVE':   guios["ACCOUNTSINFORMATION_STATUSDISPLAYTEXT"].updateText(text = status, textStyle = 'GREEN_LIGHT')
                elif status == 'INACTIVE': guios["ACCOUNTSINFORMATION_STATUSDISPLAYTEXT"].updateText(text = status, textStyle = 'RED_LIGHT')

        #---[3-4]: Trade Status
        elif updateType == 'UPDATED_TRADESTATUS':
            localID = updatedContent
            tStatus = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('ACCOUNTS', localID, 'tradeStatus'))
            puVar['accounts'][localID]['tradeStatus'] = tStatus
            if localID == puVar['accounts_selected']:
                if tStatus: guios["ACCOUNTSINFORMATION_TRADESTATUSDISPLAYTEXT"].updateText(text = 'TRUE',  textStyle = 'GREEN_LIGHT')
                else:       guios["ACCOUNTSINFORMATION_TRADESTATUSDISPLAYTEXT"].updateText(text = 'FALSE', textStyle = 'RED_LIGHT')

        #---[3-5]: Position Added
        elif updateType == 'UPDATED_POSITION_ADDED':
            localID  = updatedContent[0]
            symbol   = updatedContent[1]
            position = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('ACCOUNTS', localID, 'positions', symbol))
            puVar['accounts'][localID]['positions'][symbol] = position
            if localID == puVar['accounts_selected']: 
                pafs['SETPOSITIONSLIST']()

        #---[3-6]: Position Updated
        elif updateType == 'UPDATED_POSITION':
            #[3-6-1]: Position Update
            localID  = updatedContent[0]
            symbol   = updatedContent[1]
            dKey     = updatedContent[2]
            viewType = puVar['historyView_selected']
            position = puVar['accounts'][localID]['positions'][symbol]
            val      = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('ACCOUNTS', localID, 'positions', symbol, dKey))
            position[dKey] = val

            #[3-6-2]: Position Display Update (If Viewing)
            precisions = position['precisions']
            quoteAsset = position['quoteAsset']
            func_fts   = auxiliaries.floatToString
            if (localID  == puVar['accounts_selected']                          and 
                symbol   == guios["HISTORY_POSITIONSELECTIONBOX"].getSelected() and
                viewType == 'POSITIONCHART'
               ):
                #[3-6-2-1]: Tradable
                if dKey == 'tradeStatus':
                    trading = position['tradeStatus']
                    if trading:
                        trading_text   = 'TRUE'
                        trading_tStyle = 'GREEN_LIGHT'
                    else:
                        trading_text   = 'FALSE'
                        trading_tStyle = 'RED_LIGHT'
                    guios["HISTORY_POSITIONCHART_TRADINGDISPLAYTEXT"].updateText(text = trading_text, textStyle = trading_tStyle)

                #[3-6-2-2]: Leverage
                elif dKey == 'leverage':
                    leverage = position['leverage']
                    leverage_text = f'{leverage:d}'
                    guios["HISTORY_POSITIONCHART_LEVERAGEDISPLAYTEXT"].updateText(text = leverage_text)

                #[3-6-2-3]: Margin Mode
                elif dKey == 'isolated':
                    isolated = position['isolated']
                    if isolated: mMode_text = 'ISOLATED'
                    else:        mMode_text = 'CROSSED'
                    guios["HISTORY_POSITIONCHART_MARGINMODEDISPLAYTEXT"].updateText(text = mMode_text)

                #[3-6-2-4]: Quantity
                elif dKey == 'quantity':
                    quantity = position['quantity']
                    if quantity is None: qty_text = "-"
                    else:                qty_text = f"{quantity:,.{precisions['quantity']}f}"
                    guios["HISTORY_POSITIONCHART_QUANTITYDISPLAYTEXT"].updateText(text = qty_text)

                #[3-6-2-5]: Entry Price
                elif dKey == 'entryPrice':
                    ePrice = position['entryPrice']
                    cPrice = position['currentPrice']
                    if ePrice is None: ePrice_text = "-"
                    else:              ePrice_text = f"{ePrice:,.{precisions['price']}f}"
                    guios["HISTORY_POSITIONCHART_ENTRYPRICEDISPLAYTEXT"].updateText(text = ePrice_text)
                    if cPrice is None:
                        cPrice_text  = "-"
                        cPrice_color = 'DEFAULT'
                    else:
                        if ePrice is None:
                            cPrice_text  = func_fts(number = cPrice, precision = precisions['price']); 
                            cPrice_color = 'DEFAULT'
                        else:
                            pdPerc = round((cPrice/ePrice-1)*100, 3)
                            if   pdPerc < 0:  cPrice_text = f"{func_fts(number  = cPrice, precision = precisions['price']):s} [{pdPerc:.2f} %]";  cPrice_color = 'RED_LIGHT'
                            elif pdPerc == 0: cPrice_text = f"{func_fts(number  = cPrice, precision = precisions['price']):s} [{pdPerc:.2f} %]";  cPrice_color = 'DEFAULT'
                            elif 0 < pdPerc:  cPrice_text = f"{func_fts(number  = cPrice, precision = precisions['price']):s} [+{pdPerc:.2f} %]"; cPrice_color = 'GREEN_LIGHT'
                    guios["HISTORY_POSITIONCHART_CURRENTPRICEDISPLAYTEXT"].updateText(text = cPrice_text, textStyle = cPrice_color)

                #[3-6-2-6]: Current Price
                elif dKey == 'currentPrice':
                    ePrice = position['entryPrice']
                    cPrice = position['currentPrice']
                    if cPrice is None:
                        cPrice_text  = "-"
                        cPrice_color = 'DEFAULT'
                    else:
                        if ePrice is None:
                            cPrice_text  = func_fts(number = cPrice, precision = precisions['price']); 
                            cPrice_color = 'DEFAULT'
                        else:
                            pdPerc = round((cPrice/ePrice-1)*100, 3)
                            if   pdPerc < 0:  cPrice_text = f"{func_fts(number  = cPrice, precision = precisions['price']):s} [{pdPerc:.2f} %]";  cPrice_color = 'RED_LIGHT'
                            elif pdPerc == 0: cPrice_text = f"{func_fts(number  = cPrice, precision = precisions['price']):s} [{pdPerc:.2f} %]";  cPrice_color = 'DEFAULT'
                            elif 0 < pdPerc:  cPrice_text = f"{func_fts(number  = cPrice, precision = precisions['price']):s} [+{pdPerc:.2f} %]"; cPrice_color = 'GREEN_LIGHT'
                    guios["HISTORY_POSITIONCHART_CURRENTPRICEDISPLAYTEXT"].updateText(text = cPrice_text, textStyle = cPrice_color)

                #[3-6-2-7]: Liquidation Price
                elif dKey == 'liquidationPrice':
                    liqPrice = position['liquidationPrice']
                    if liqPrice is None: liqPrice_text = "-"
                    else:                liqPrice_text = f"{liqPrice:,.{precisions['price']}f}"
                    guios["HISTORY_POSITIONCHART_LIQUIDATIONPRICEDISPLAYTEXT"].updateText(text = liqPrice_text)

                #[3-6-2-8]: Unrealized Profit
                elif dKey == 'unrealizedPNL':
                    uPNL = position['unrealizedPNL']
                    pim  = position['positionInitialMargin']
                    if uPNL is None or pim is None or pim == 0:
                        uPNL_text  = "-"
                        uPNL_color = 'DEFAULT'
                    else:
                        roi = round(uPNL/pim*100, 3)
                        if   uPNL < 0:  uPNL_text = f"{func_fts(number  = uPNL, precision = _ASSETPRECISIONS_XS[quoteAsset]):s} [{roi:.2f} %]";  uPNL_color = 'RED_LIGHT'
                        elif uPNL == 0: uPNL_text = f"{func_fts(number  = uPNL, precision = _ASSETPRECISIONS_XS[quoteAsset]):s} [{roi:.2f} %]";  uPNL_color = 'DEFAULT'
                        elif 0 < uPNL:  uPNL_text = f"{func_fts(number  = uPNL, precision = _ASSETPRECISIONS_XS[quoteAsset]):s} [+{roi:.2f} %]"; uPNL_color = 'GREEN_LIGHT'
                    guios["HISTORY_POSITIONCHART_UNREALIZEDPNLDISPLAYTEXT"].updateText(text = uPNL_text, textStyle = uPNL_color)

                #[3-6-2-9]: Assumed Ratio
                elif dKey == 'assumedRatio':
                    aRatio = position['assumedRatio']
                    if aRatio is None: aRatio_text = "-"
                    else:              aRatio_text = f"{aRatio*100:.3f} %"
                    guios["HISTORY_POSITIONCHART_ASSUMEDRATIODISPLAYTEXT"].updateText(text = aRatio_text)

                #[3-6-2-10]: Allocated Balance
                elif dKey == 'allocatedBalance':
                    allocBal = position['allocatedBalance']
                    if allocBal is None: allocBal_text = "-"
                    else:                allocBal_text = f"{allocBal:.{_ASSETPRECISIONS_XS[quoteAsset]}f} {quoteAsset}"
                    guios["HISTORY_POSITIONCHART_ALLOCATEDBALANCEDISPLAYTEXT"].updateText(text = allocBal_text)

                #[3-6-2-11]: Commitment Rate
                elif dKey == 'commitmentRate':
                    cmtRate = position['commitmentRate']
                    if cmtRate is None: 
                        cmtRate_text  = "N/A"
                        cmtRate_color = 'DEFAULT'
                    else:
                        cmtRate_text = f"{cmtRate*100:.3f} %"
                        if   0.00 <= cmtRate < 0.30:  cmtRate_color = 'GREEN_DARK'
                        elif 0.30 <= cmtRate < 0.50:  cmtRate_color = 'GREEN_LIGHT'
                        elif 0.50 <= cmtRate < 0.70:  cmtRate_color = 'YELLOW'
                        elif 0.70 <= cmtRate < 0.80:  cmtRate_color = 'ORANGE_LIGHT'
                        elif 0.80 <= cmtRate < 0.90:  cmtRate_color = 'RED_LIGHT'
                        elif 0.90 <= cmtRate <= 1.00: cmtRate_color = 'RED'
                        else:                         cmtRate_color = 'VIOLET_LIGHT'
                    guios["HISTORY_POSITIONCHART_COMMITMENTRATEDISPLAYTEXT"].updateText(text = cmtRate_text, textStyle = cmtRate_color)

                #[3-6-2-12]: Risk Level
                elif dKey == 'riskLevel':
                    rl = position['riskLevel']
                    if rl is None: 
                        rl_text  = "N/A"; 
                        rl_color = 'DEFAULT'
                    else:
                        rl_text = f"{rl*100:.3f} %"
                        if   0.00 <= rl <  0.30: rl_color = 'GREEN_DARK'
                        elif 0.30 <= rl <  0.50: rl_color = 'GREEN_LIGHT'
                        elif 0.50 <= rl <  0.70: rl_color = 'ORANGE_LIGHT'
                        elif 0.70 <= rl <  0.90: rl_color = 'RED_LIGHT'
                        elif 0.90 <= rl <= 1.00: rl_color = 'RED'
                        else:                    rl_color = 'VIOLET_LIGHT'
                    guios["HISTORY_POSITIONCHART_RISKLEVELDISPLAYTEXT"].updateText(text = rl_text, textStyle = rl_color)

                #[3-6-2-13]: Risk Level
                elif dKey == 'tradeControlTracker':
                    tcTracker = position['tradeControlTracker']
                    tcTracker_text = json.dumps(tcTracker)
                    guios["HISTORY_POSITIONCHART_TRADECONTROLDISPLAYTEXT"].updateText(text = tcTracker_text)

                #[3-6-2-14]: Risk Level
                elif dKey == 'abruptClearingRecords':
                    acrs = position['abruptClearingRecords']
                    if acrs: acrs_text = str(acrs)
                    else:    acrs_text = "-"
                    guios["HISTORY_POSITIONCHART_ACRDISPLAYTEXT"].updateText(text = acrs_text)
    
        #[4]: Chart Drawer Response
        guios["HISTORY_POSITIONCHART_CHARTDRAWER"].onAccountUpdate(updateType = updateType, updatedContent = updatedContent)
    def __far_onCurrencyAnalysisUpdate(requester, updateType, currencyAnalysisCode):
        #[1]: Source Check
        if requester != 'TRADEMANAGER':
            return
        
        #[2]: Instances
        puVar  = self.puVar
        guios  = self.GUIOs
        caCode = currencyAnalysisCode
        func_getPRD = self.ipcA.getPRD

        #[3]: Update Response
        #---[3-1]: Status Updated
        if updateType == 'UPDATE_STATUS':
            status = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', caCode, 'status'))
            puVar['currencyAnalysis'][caCode]['status'] = status

        #---[3-2]: Analyzer Updated
        elif updateType == 'UPDATE_ANALYZER':
            allocatedAnalyzer = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', caCode, 'allocatedAnalyzer'))
            puVar['currencyAnalysis'][caCode]['allocatedAnalyzer'] = allocatedAnalyzer

        #---[3-3]: Added
        elif updateType == 'ADDED':
            puVar['currencyAnalysis'][caCode] = func_getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', caCode))

        #---[3-4]: Removed
        elif updateType == 'REMOVED':
            del puVar['currencyAnalysis'][caCode]

        #[4]: Chart Drawer Response
        guios["HISTORY_POSITIONCHART_CHARTDRAWER"].onCurrencyAnalysisUpdate(updateType = updateType, currencyAnalysisCode = caCode)
    auxFunctions['_FAR_ONACCOUNTUPDATE'] = __far_onAccountUpdate
    auxFunctions['_FAR_ONCURRENCYANALYSISUPDATE'] = __far_onCurrencyAnalysisUpdate





    #<Accounts List>
    def __setAccountsList():
        accounts_selectionList = dict()
        for accountIndex, localID in enumerate(self.puVar['accounts']):
            _account = self.puVar['accounts'][localID]
            #Display Table Formatting
            _status = _account['status']
            if   (_status == 'INACTIVE'): _text_status = 'INACTIVE'; _textColor_status = 'RED_LIGHT'
            elif (_status == 'ACTIVE'):   _text_status = 'ACTIVE';   _textColor_status = 'GREEN_LIGHT'
            accounts_selectionList[localID] = [{'text': str(accountIndex),       'textStyles': [('all', 'DEFAULT'),],              'textAnchor': 'CENTER'},
                                               {'text': localID,                 'textStyles': [('all', 'DEFAULT'),],              'textAnchor': 'CENTER'},
                                               {'text': _account['accountType'], 'textStyles': [('all', 'DEFAULT'),],              'textAnchor': 'CENTER'},
                                               {'text': _text_status,            'textStyles': [('all', _textColor_status),],      'textAnchor': 'CENTER'}]
        self.GUIOs["ACCOUNTSLIST_SELECTIONBOX"].setSelectionList(selectionList = accounts_selectionList, keepSelected = True, displayTargets = 'all', callSelectionUpdateFunction = False)
        self.pageAuxillaryFunctions['ONACCOUNTSLISTFILTERUPDATE']()
    def __onAccountsListFilterUpdate():
        if   (self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_VIRTUAL"].getStatus() == True): localIDs_filtered = [localID for localID in self.puVar['accounts'] if (self.puVar['accounts'][localID]['accountType'] == 'VIRTUAL')]
        elif (self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_ACTUAL"].getStatus()  == True): localIDs_filtered = [localID for localID in self.puVar['accounts'] if (self.puVar['accounts'][localID]['accountType'] == 'ACTUAL')]
        else:                                                                       localIDs_filtered = 'all'
        self.GUIOs["ACCOUNTSLIST_SELECTIONBOX"].setDisplayTargets(displayTargets = localIDs_filtered)
    auxFunctions['SETACCOUNTSLIST']            = __setAccountsList
    auxFunctions['ONACCOUNTSLISTFILTERUPDATE'] = __onAccountsListFilterUpdate

    #<Accounts Information & Control>
    def __farr_onTradeLogsRequestResponse(responder, requestID, functionResult):
        #[1]: Source Check
        if responder != 'DATAMANAGER':
            return
        
        #[2]: Function Result
        result      = functionResult['result']
        localID     = functionResult['localID']
        tradeLogs   = functionResult['tradeLogs']
        failureType = functionResult['failureType']

        #[3]: Instances
        puVar = self.puVar
        pafs  = self.pageAuxillaryFunctions

        #[4]: Result Check
        if localID != puVar['accounts_selected'] or requestID != puVar['historyView_tradeLogsFetchRID']:
            return
        if not result:
            print(termcolor.colored((f"[GUI-PAGE:ACCOUNTHISTORY] Trade Logs Fetch Request Returned A Failure\n"
                                     f" * Local ID:     {localID}\n"
                                     f" * Failure Type: {failureType}"),
                                    'light_red'))
            puVar['historyView_tradeLogsFetchRID'] = None
            return

        #[5]: Save trade logs
        #---[5-1]: Logs
        puVar['historyView_tradeLogs'] = tradeLogs
        #---[5-2]: Available Assets & Positions
        positions  = puVar['accounts'][puVar['accounts_selected']]['positions']
        assetNames = set()
        symbols    = {'#ALL#': set()}
        #------[5-2-1]: Asssets
        for tl in tradeLogs:
            assetNames.add(positions[tl['positionSymbol']]['quoteAsset'])
        #------[5-2-2]: Positions
        for assetName in assetNames: 
            symbols[assetName] = set()
        for tl in tradeLogs: 
            symbol = tl['positionSymbol']
            symbols['#ALL#'].add(symbol)
            symbols[positions[symbol]['quoteAsset']].add(symbol)
        #------[5-2-3]: Finally
        puVar['historyView_tradeLogs_availableAssets']    = assetNames
        puVar['historyView_tradeLogs_availablePositions'] = symbols

        #[6]: If Viewing Trade Logs
        if puVar['historyView_selected'] == 'TRADELOGS':
            pafs['SETASSETSLIST']()
            pafs['SETPOSITIONSLIST']()
            pafs['SETTRADELOGSLIST']()

        #[7]: Request ID Initialization
        puVar['historyView_tradeLogsFetchRID'] = None
    def __onAccountSelectionUpdate():
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        pafs  = self.pageAuxillaryFunctions

        #[2]: Account Information Display Update
        localID = puVar['accounts_selected']
        account = puVar['accounts'].get(localID, None)
        #---[2-1]: Account Not Selected
        if account is None: 
            #[2-1-1]: Account Information
            guios["ACCOUNTSINFORMATION_LOCALIDDISPLAYTEXT"].updateText(text     = "-") #Local ID
            guios["ACCOUNTSINFORMATION_BINANCEUIDDISPLAYTEXT"].updateText(text  = "-") #BUID
            guios["ACCOUNTSINFORMATION_ACCOUNTTYPEDISPLAYTEXT"].updateText(text = "-") #Account Type
            guios["ACCOUNTSINFORMATION_STATUSDISPLAYTEXT"].updateText(text      = "-") #Status
            guios["ACCOUNTSINFORMATION_TRADESTATUSDISPLAYTEXT"].updateText(text = "-") #Trade Status
            #[2-1-2]: Trade Logs
            puVar['historyView_tradeLogsFetchRID'] = None
            puVar['historyView_tradeLogs']         = None
            puVar['historyView_tradeLogs_availableAssets']    = None
            puVar['historyView_tradeLogs_availablePositions'] = None

        #---[2-2]: Account Selected
        else:
            #[2-2-1]: Account Information
            #---[2-2-1-1]: Local ID
            guios["ACCOUNTSINFORMATION_LOCALIDDISPLAYTEXT"].updateText(text = localID)
            #---[2-2-1-2]: BUID
            buid = account['buid']
            if buid is None: guios["ACCOUNTSINFORMATION_BINANCEUIDDISPLAYTEXT"].updateText(text = "-")
            else:            guios["ACCOUNTSINFORMATION_BINANCEUIDDISPLAYTEXT"].updateText(text = f"{buid}")
            #---[2-2-1-3]: Account Type
            guios["ACCOUNTSINFORMATION_ACCOUNTTYPEDISPLAYTEXT"].updateText(text = account['accountType'])
            #---[2-2-1-4]: Status
            status = account['status']
            if   status == 'INACTIVE': guios["ACCOUNTSINFORMATION_STATUSDISPLAYTEXT"].updateText(text = status, textStyle = 'RED_LIGHT')
            elif status == 'ACTIVE':   guios["ACCOUNTSINFORMATION_STATUSDISPLAYTEXT"].updateText(text = status, textStyle = 'GREEN_LIGHT')
            #---[2-2-1-5]: Trade Status
            tradeStatus = account['tradeStatus']
            if tradeStatus: guios["ACCOUNTSINFORMATION_TRADESTATUSDISPLAYTEXT"].updateText(text = "TRUE",  textStyle = 'GREEN_LIGHT')
            else:           guios["ACCOUNTSINFORMATION_TRADESTATUSDISPLAYTEXT"].updateText(text = "FALSE", textStyle = 'RED_LIGHT')
            #[2-2-2]: Trade Logs
            puVar['historyView_tradeLogsFetchRID']            = self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                                                                                  functionID     = 'fetchAccountTradeLog', 
                                                                                  functionParams = {'localID': localID}, 
                                                                                  farrHandler    = __farr_onTradeLogsRequestResponse)
            puVar['historyView_tradeLogs']                    = None
            puVar['historyView_tradeLogs_availableAssets']    = None
            puVar['historyView_tradeLogs_availablePositions'] = None

        #[3]: Assets & Positions List Update
        pafs['SETASSETSLIST']()
        pafs['SETPOSITIONSLIST']()

        #[4]: View-Dependent Response
        hv_sel = puVar['historyView_selected']
        #---[4-1]: Position Chart
        if hv_sel == 'POSITIONCHART':
            pafs['SETCHARTDRAWERTARGET']()
            pafs['UPDATEPOSITIONINFORMATION']()
        #---[4-2]: Periodic Reports
        elif hv_sel == 'PERIODICREPORTS': 
            pafs['SETPERIODICREPORTSVIEWERTARGET']()
        #---[4-3]: Trade Logs
        elif hv_sel == 'TRADELOGS':       
            pafs['SETTRADELOGSLIST']()
    auxFunctions['_FARR_ONTRADELOGSREQUESTRESPONSE'] = __farr_onTradeLogsRequestResponse
    auxFunctions['ONACCOUNTSELECTIONUPDATE']         = __onAccountSelectionUpdate

    #<History>
    def __onHistoryViewUpdate(view_prev = None):
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        pafs  = self.pageAuxillaryFunctions

        #[2]: GUIOs Hide & Show
        view_sel = puVar['historyView_selected']
        if view_prev is not None:
            for gName in puVar['GUIOGROUPS'][view_prev]: guios[gName].hide()
            for gName in puVar['GUIOGROUPS'][view_sel]:  guios[gName].show()

        #[3]: Assets & Positions List Update
        pafs['SETASSETSLIST']()
        pafs['SETPOSITIONSLIST']()

        #[4]: View-Dependent Response
        if   view_sel == 'POSITIONCHART':   pafs['SETCHARTDRAWERTARGET']()
        elif view_sel == 'PERIODICREPORTS': pafs['SETPERIODICREPORTSVIEWERTARGET']()
        elif view_sel == 'TRADELOGS':       pafs['SETTRADELOGSLIST']()
    def __setAssetsList():
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        vm_gtp = self.visualManager.getTextPack

        #[2]: No Account Selected
        localID = puVar['accounts_selected']
        account = puVar['accounts'].get(localID, None)
        if account is None:
            guios["HISTORY_ASSETSELECTIONBOX"].setSelectionList(selectionList = dict(), keepSelected = False, displayTargets = 'all')
            guios["HISTORY_ASSETSELECTIONBOX"].deactivate()

        #[3]: Account Selected
        else:
            #[3-1]: Instances
            hv_sel = puVar['historyView_selected']
            aSelBox = guios["HISTORY_ASSETSELECTIONBOX"]
            aImgBox = guios["HISTORY_ASSETIMAGEBOX"]

            #[3-2]: Position Chart
            if hv_sel == 'POSITIONCHART':
                assetSels = {'#ALL#': {'text': vm_gtp('ACCOUNTHISTORY:HISTORY_SELECTIONBOX_ALL')}}
                for assetName in set(position['quoteAsset'] for position in account['positions'].values() if position['currencyAnalysisCode'] in puVar['currencyAnalysis']):
                    assetSels[assetName] = {'text': assetName} 
                aSelBox.setSelectionList(selectionList = assetSels, keepSelected = True, displayTargets = 'all')
                aSelBox.setSelected(itemKey = '#ALL#', callSelectionUpdateFunction = False)
                aImgBox.updateImage(image = "assetTotalIcon_512x512.png")

            #[3-3]: Periodic Reports
            if hv_sel == 'PERIODICREPORTS':
                assetSels = {assetName: {'text': assetName} for assetName in ('USDT', 'USDC')}
                aSelBox.setSelectionList(selectionList = assetSels, keepSelected = True, displayTargets = 'all')
                aSelBox.setSelected(itemKey = 'USDT',  callSelectionUpdateFunction = False)
                aImgBox.updateImage(image = "usdtIcon_512x512.png")

            #[3-4]: Trade Logs
            elif hv_sel == 'TRADELOGS':
                tls_aas = puVar['historyView_tradeLogs_availableAssets']
                assetSels = {'#ALL#': {'text': vm_gtp('ACCOUNTHISTORY:HISTORY_SELECTIONBOX_ALL')}}
                if tls_aas is not None:
                    for assetName in tls_aas: 
                        assetSels[assetName] = {'text': assetName}
                aSelBox.setSelectionList(selectionList = assetSels, keepSelected = True, displayTargets = 'all')
                aSelBox.setSelected(itemKey = '#ALL#', callSelectionUpdateFunction = False)
                aImgBox.updateImage(image = "assetTotalIcon_512x512.png")

            #[3-5]: Asset Selection Box Activation
            aSelBox.activate()
    def __setPositionsList():
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        vm_gtp = self.visualManager.getTextPack

        #[2]: No Account Selected
        localID = puVar['accounts_selected']
        account = puVar['accounts'].get(localID, None)
        if account is None:
            guios["HISTORY_POSITIONSELECTIONBOX"].setSelectionList(selectionList = dict(), keepSelected = False, displayTargets = 'all')
            guios["HISTORY_POSITIONSELECTIONBOX"].deactivate()

        #[3]: Account Selected
        else:
            #[3-1]: Instances
            hv_sel    = puVar['historyView_selected']
            pSelBox   = guios["HISTORY_POSITIONSELECTIONBOX"]
            assetName = guios["HISTORY_ASSETSELECTIONBOX"].getSelected()

            #[3-2]: Periodic Reports
            if hv_sel == 'POSITIONCHART':
                symbols   = [symbol for symbol, position in account['positions'].items() 
                             if position['currencyAnalysisCode'] in puVar['currencyAnalysis'] and (assetName == '#ALL#' or assetName == position['quoteAsset'])]
                positionSels = {symbol: {'text': symbol, 'textAnchor': 'W'} for symbol in symbols}
                pSelBox.setSelectionList(selectionList = positionSels, keepSelected = True, displayTargets = 'all')
                pSelBox.activate()

            #[3-3]: Periodic Reports
            elif hv_sel == 'PERIODICREPORTS': 
                pSelBox.setSelectionList(selectionList = dict(), keepSelected = False, displayTargets = 'all')
                pSelBox.deactivate()

            #[3-4]: Trade Logs
            elif hv_sel == 'TRADELOGS':
                tls_aas = puVar['historyView_tradeLogs_availableAssets']
                tls_aps = puVar['historyView_tradeLogs_availablePositions']
                positionSels = {'#ALL#': {'text': vm_gtp('ACCOUNTHISTORY:HISTORY_SELECTIONBOX_ALL'), 'textAnchor': 'W'}}
                if tls_aas is not None:
                    for symbol in tls_aps[assetName]: 
                        positionSels[symbol] = {'text': symbol, 'textAnchor': 'W'}
                pSelBox.setSelectionList(selectionList = positionSels, keepSelected = True, displayTargets = 'all')
                pSelBox.setSelected(itemKey = '#ALL#', callSelectionUpdateFunction = False)
                pSelBox.activate()
    auxFunctions['ONHISTORYVIEWUPDATE'] = __onHistoryViewUpdate
    auxFunctions['SETASSETSLIST']       = __setAssetsList
    auxFunctions['SETPOSITIONSLIST']    = __setPositionsList

    #<Chart Drawer>
    def __setChartDrawerTarget():
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs

        #[2]: Selected Account & Position Symbol
        lID     = puVar['accounts_selected']
        account = puVar['accounts'].get(lID, None)
        symbol  = guios["HISTORY_POSITIONSELECTIONBOX"].getSelected()
        caCode  = None if account is None or symbol is None else account['positions'][symbol]['currencyAnalysisCode']

        #[3]: Chart Drawer
        if lID is not None and caCode is not None: target = (lID, caCode)
        else:                                      target = None
        self.GUIOs["HISTORY_POSITIONCHART_CHARTDRAWER"].setTarget(target = target)
    def __updatePositionInformation():
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        lID     = puVar['accounts_selected']
        account = puVar['accounts'].get(lID, None)
        symbol  = guios["HISTORY_POSITIONSELECTIONBOX"].getSelected()
        func_fts = auxiliaries.floatToString

        #[2]: Information Display Update
        #---[2-1]: No Account Selected
        if account is None or symbol not in account['positions']:
            guios["HISTORY_POSITIONCHART_TRADINGDISPLAYTEXT"].updateText(text          = "-", textStyle = 'DEFAULT')
            guios["HISTORY_POSITIONCHART_LEVERAGEDISPLAYTEXT"].updateText(text         = "-")
            guios["HISTORY_POSITIONCHART_MARGINMODEDISPLAYTEXT"].updateText(text       = "-")
            guios["HISTORY_POSITIONCHART_QUANTITYDISPLAYTEXT"].updateText(text         = "-")
            guios["HISTORY_POSITIONCHART_ENTRYPRICEDISPLAYTEXT"].updateText(text       = "-")
            guios["HISTORY_POSITIONCHART_CURRENTPRICEDISPLAYTEXT"].updateText(text     = "-", textStyle = 'DEFAULT')
            guios["HISTORY_POSITIONCHART_LIQUIDATIONPRICEDISPLAYTEXT"].updateText(text = "-")
            guios["HISTORY_POSITIONCHART_UNREALIZEDPNLDISPLAYTEXT"].updateText(text    = "-", textStyle = 'DEFAULT')
            guios["HISTORY_POSITIONCHART_ASSUMEDRATIODISPLAYTEXT"].updateText(text     = "-")
            guios["HISTORY_POSITIONCHART_ALLOCATEDBALANCEDISPLAYTEXT"].updateText(text = "-")
            guios["HISTORY_POSITIONCHART_COMMITMENTRATEDISPLAYTEXT"].updateText(text   = "-", textStyle = 'DEFAULT')
            guios["HISTORY_POSITIONCHART_RISKLEVELDISPLAYTEXT"].updateText(text        = "-", textStyle = 'DEFAULT')
            guios["HISTORY_POSITIONCHART_TRADECONTROLDISPLAYTEXT"].updateText(text     = "-")
            guios["HISTORY_POSITIONCHART_ACRDISPLAYTEXT"].updateText(text              = "-")

        #---[2-2]: Account Selected
        else:
            #[2-2-1]: Position
            position   = account['positions'][symbol]
            precisions = position['precisions']
            quoteAsset = position['quoteAsset']
            trading   = position['tradeStatus']
            leverage  = position['leverage']
            isolated  = position['isolated']
            quantity  = position['quantity']
            ePrice    = position['entryPrice']
            cPrice    = position['currentPrice']
            liqPrice  = position['liquidationPrice']
            uPNL      = position['unrealizedPNL']
            aRatio    = position['assumedRatio']
            allocBal  = position['allocatedBalance']
            cmtRate   = position['commitmentRate']
            rl        = position['riskLevel']
            tcTracker = position['tradeControlTracker']
            acrs      = position['abruptClearingRecords']

            #[2-2-2]: Texts Update
            #---[2-2-2-1]: Trading
            if trading:
                trading_text   = 'TRUE'
                trading_tStyle = 'GREEN_LIGHT'
            else:
                trading_text   = 'FALSE'
                trading_tStyle = 'RED_LIGHT'
            guios["HISTORY_POSITIONCHART_TRADINGDISPLAYTEXT"].updateText(text = trading_text, textStyle = trading_tStyle)

            #---[2-2-2-2]: Leverage
            leverage_text = f'{leverage:d}'
            guios["HISTORY_POSITIONCHART_LEVERAGEDISPLAYTEXT"].updateText(text = leverage_text)

            #---[2-2-2-3]: Margin Mode
            if isolated: mMode_text = 'ISOLATED'
            else:        mMode_text = 'CROSSED'
            guios["HISTORY_POSITIONCHART_MARGINMODEDISPLAYTEXT"].updateText(text = mMode_text)

            #---[2-2-2-4]: Quantity
            if quantity is None: qty_text = "-"
            else:                qty_text = f"{quantity:,.{precisions['quantity']}f}"
            guios["HISTORY_POSITIONCHART_QUANTITYDISPLAYTEXT"].updateText(text = qty_text)

            #---[2-2-2-5]: Entry Price
            if ePrice is None: ePrice_text = "-"
            else:              ePrice_text = f"{ePrice:,.{precisions['price']}f}"
            guios["HISTORY_POSITIONCHART_ENTRYPRICEDISPLAYTEXT"].updateText(text = ePrice_text)

            #---[2-2-2-6]: Current Price
            if cPrice is None:
                cPrice_text  = "-"
                cPrice_color = 'DEFAULT'
            else:
                if ePrice is None:
                    cPrice_text  = func_fts(number = cPrice, precision = precisions['price']); 
                    cPrice_color = 'DEFAULT'
                else:
                    pdPerc = round((cPrice/ePrice-1)*100, 3)
                    if   pdPerc < 0:  cPrice_text = f"{func_fts(number  = cPrice, precision = precisions['price']):s} [{pdPerc:.2f} %]";  cPrice_color = 'RED_LIGHT'
                    elif pdPerc == 0: cPrice_text = f"{func_fts(number  = cPrice, precision = precisions['price']):s} [{pdPerc:.2f} %]";  cPrice_color = 'DEFAULT'
                    elif 0 < pdPerc:  cPrice_text = f"{func_fts(number  = cPrice, precision = precisions['price']):s} [+{pdPerc:.2f} %]"; cPrice_color = 'GREEN_LIGHT'
            guios["HISTORY_POSITIONCHART_CURRENTPRICEDISPLAYTEXT"].updateText(text = cPrice_text, textStyle = cPrice_color)

            #---[2-2-2-7]: Liquidation Price
            if liqPrice is None: liqPrice_text = "-"
            else:                liqPrice_text = f"{liqPrice:,.{precisions['price']}f}"
            guios["HISTORY_POSITIONCHART_LIQUIDATIONPRICEDISPLAYTEXT"].updateText(text = liqPrice_text)

            #---[2-2-2-8]: Unrealized Profit
            pim = position['positionInitialMargin']
            if uPNL is None or pim is None or pim == 0:
                uPNL_text  = "-"
                uPNL_color = 'DEFAULT'
            else:
                roi = round(uPNL/pim*100, 3)
                if   uPNL < 0:  uPNL_text = f"{func_fts(number  = uPNL, precision = _ASSETPRECISIONS_XS[quoteAsset]):s} [{roi:.2f} %]";  uPNL_color = 'RED_LIGHT'
                elif uPNL == 0: uPNL_text = f"{func_fts(number  = uPNL, precision = _ASSETPRECISIONS_XS[quoteAsset]):s} [{roi:.2f} %]";  uPNL_color = 'DEFAULT'
                elif 0 < uPNL:  uPNL_text = f"{func_fts(number  = uPNL, precision = _ASSETPRECISIONS_XS[quoteAsset]):s} [+{roi:.2f} %]"; uPNL_color = 'GREEN_LIGHT'
            guios["HISTORY_POSITIONCHART_UNREALIZEDPNLDISPLAYTEXT"].updateText(text = uPNL_text, textStyle = uPNL_color)

            #---[2-2-2-9]: Assumed Ratio
            if aRatio is None: aRatio_text = "-"
            else:              aRatio_text = f"{aRatio*100:.3f} %"
            guios["HISTORY_POSITIONCHART_ASSUMEDRATIODISPLAYTEXT"].updateText(text = aRatio_text)

            #---[2-2-2-10]: Allocated Balance
            if allocBal is None: allocBal_text = "-"
            else:                allocBal_text = f"{allocBal:.{_ASSETPRECISIONS_XS[quoteAsset]}f} {quoteAsset}"
            guios["HISTORY_POSITIONCHART_ALLOCATEDBALANCEDISPLAYTEXT"].updateText(text = allocBal_text)

            #---[2-2-2-11]: Commitment Rate
            if cmtRate is None: 
                cmtRate_text  = "N/A"
                cmtRate_color = 'DEFAULT'
            else:
                cmtRate_text = f"{cmtRate*100:.3f} %"
                if   0.00 <= cmtRate < 0.30:  cmtRate_color = 'GREEN_DARK'
                elif 0.30 <= cmtRate < 0.50:  cmtRate_color = 'GREEN_LIGHT'
                elif 0.50 <= cmtRate < 0.70:  cmtRate_color = 'YELLOW'
                elif 0.70 <= cmtRate < 0.80:  cmtRate_color = 'ORANGE_LIGHT'
                elif 0.80 <= cmtRate < 0.90:  cmtRate_color = 'RED_LIGHT'
                elif 0.90 <= cmtRate <= 1.00: cmtRate_color = 'RED'
                else:                         cmtRate_color = 'VIOLET_LIGHT'
            guios["HISTORY_POSITIONCHART_COMMITMENTRATEDISPLAYTEXT"].updateText(text = cmtRate_text, textStyle = cmtRate_color)

            #---[2-2-2-12]: Risk Level
            if rl is None: 
                rl_text  = "N/A"; 
                rl_color = 'DEFAULT'
            else:
                rl_text = f"{rl*100:.3f} %"
                if   0.00 <= rl <  0.30: rl_color = 'GREEN_DARK'
                elif 0.30 <= rl <  0.50: rl_color = 'GREEN_LIGHT'
                elif 0.50 <= rl <  0.70: rl_color = 'ORANGE_LIGHT'
                elif 0.70 <= rl <  0.90: rl_color = 'RED_LIGHT'
                elif 0.90 <= rl <= 1.00: rl_color = 'RED'
                else:                    rl_color = 'VIOLET_LIGHT'
            guios["HISTORY_POSITIONCHART_RISKLEVELDISPLAYTEXT"].updateText(text = rl_text, textStyle = rl_color)

            #---[2-2-2-13]: Trade Control
            tcTracker_text = json.dumps(tcTracker)
            guios["HISTORY_POSITIONCHART_TRADECONTROLDISPLAYTEXT"].updateText(text = tcTracker_text)

            #---[2-2-2-14]: ACR (Abrupt Clearing Records)
            if acrs: acrs_text = str(acrs)
            else:    acrs_text = "-"
            guios["HISTORY_POSITIONCHART_ACRDISPLAYTEXT"].updateText(text = acrs_text)
    auxFunctions['SETCHARTDRAWERTARGET']      = __setChartDrawerTarget
    auxFunctions['UPDATEPOSITIONINFORMATION'] = __updatePositionInformation

    #<Balances>
    def __setPeriodicReportsViewerTarget():
        lID       = self.puVar['accounts_selected']
        assetName = self.GUIOs["HISTORY_ASSETSELECTIONBOX"].getSelected()
        target    = (lID, assetName, 'ACCOUNT') if lID is not None and assetName is not None else None
        self.GUIOs["HISTORY_PERIODICREPORT_PERIODICREPORTVIEWER"].setTarget(target = target)
    auxFunctions['SETPERIODICREPORTSVIEWERTARGET'] = __setPeriodicReportsViewerTarget

    #<Trade Logs>
    def __setTradeLogsList():
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        pafs  = self.pageAuxillaryFunctions
        tLogs = puVar['historyView_tradeLogs']
        if tLogs is None:
            guios["HISTORY_TRADELOGS_TRADELOGSELECTIONBOX"].clearSelectionList()
            return
        func_fts    = auxiliaries.floatToString
        func_dt_fts = datetime.fromtimestamp
        
        #[2]: Selection List Update
        nTradeLogs = len(puVar['historyView_tradeLogs'])
        positions  = puVar['accounts'][puVar['accounts_selected']]['positions']
        selList = dict()
        for tl in tLogs:
            #[2-1]: Position
            symbol = tl['positionSymbol']
            position   = positions[symbol]
            precisions = position['precisions']
            assetName  = position['quoteAsset']

            #[2-2]: Display Items
            #---[2-2-1]: Index
            tlIdx = tl['logIndex']
            index_str = f"{tlIdx+1:,d} / {nTradeLogs:,d}"

            #---[2-2-1]: Time
            time_str = func_dt_fts(tl['timestamp'], tz=timezone.utc).strftime("%Y/%m/%d %H:%M:%S")

            #---[2-2-1]: Symbol
            symbol_str = symbol

            #---[2-2-1]: Logic Source
            logicSource_str = tl['logicSource']

            #---[2-2-1]: Side
            side = tl['side']
            side_str = side
            if   side == 'BUY':         side_str_color = 'GREEN_LIGHT'
            elif side == 'SELL':        side_str_color = 'RED_LIGHT'
            elif side == 'LIQUIDATION': side_str_color = 'VIOLET_LIGHT'

            #---[2-2-1]: Quantity
            quantity_str = func_fts(number = tl['quantity'], precision = precisions['quantity'])

            #---[2-2-1]: Price
            price = tl['price']
            if price is None: price_str = "N/A"
            else:             price_str = func_fts(number = tl['price'], precision = precisions['price'])

            #---[2-2-1]: Profit
            profit = tl['profit']
            if   profit is None: profit_str = "N/A";                                                                     profit_str_color = 'DEFAULT'
            elif 0 < profit:     profit_str = "+"+func_fts(number = profit, precision = _ASSETPRECISIONS_XS[assetName]); profit_str_color = 'GREEN_LIGHT'
            elif profit == 0:    profit_str =     func_fts(number = profit, precision = _ASSETPRECISIONS_XS[assetName]); profit_str_color = 'DEFAULT'
            elif profit < 0:     profit_str =     func_fts(number = profit, precision = _ASSETPRECISIONS_XS[assetName]); profit_str_color = 'RED_LIGHT'

            #---[2-2-1]: Trading Fee
            tradingFee = tl['tradingFee']
            if tradingFee is None: tradingFee_str = "N/A"
            else:                  tradingFee_str = func_fts(number = tradingFee, precision = _ASSETPRECISIONS_XS[assetName])

            #---[2-2-1]: Total Quantity
            tQty = tl['totalQuantity']
            totalQuantity_str = func_fts(number = tQty, precision = precisions['quantity'])

            #---[2-2-1]: Entry Price
            ep = tl['entryPrice']
            if ep is None: entryPrice_str = "-"
            else:          entryPrice_str = func_fts(number = ep, precision = precisions['price'])

            #---[2-2-1]: Wallet Balance
            wb = tl['walletBalance']
            if wb is None: walletBalance_str = "N/A"
            else:          walletBalance_str = func_fts(number = wb, precision = _ASSETPRECISIONS_XS[assetName])

            #[2-3]: Record
            selList[tlIdx] = [{'text': index_str},
                              {'text': time_str},
                              {'text': symbol_str},
                              {'text': logicSource_str},
                              {'text': side_str, 'textStyles': [('all', side_str_color)]},
                              {'text': quantity_str},
                              {'text': price_str},
                              {'text': profit_str, 'textStyles': [('all', profit_str_color)]},
                              {'text': tradingFee_str},
                              {'text': totalQuantity_str},
                              {'text': entryPrice_str},
                              {'text': walletBalance_str}]
        guios["HISTORY_TRADELOGS_TRADELOGSELECTIONBOX"].setSelectionList(selectionList               = selList, 
                                                                         keepSelected                = False, 
                                                                         displayTargets              = 'all', 
                                                                         callSelectionUpdateFunction = False)
        
        #[3]: Selection Box Filter Update
        pafs['ONTRADELOGSFILTERUPDATE']()
    def __onTradeLogsFilterUpdate():
        #[1]: Instances
        puVar   = self.puVar
        guios   = self.GUIOs
        account = puVar['accounts'].get(puVar['accounts_selected'], None)



        #[2]: No Account Selected
        if account is None:
            #[2-1]: Net Proft, Gain, Loss, Trading Fee Display Update
            guios["HISTORY_TRADELOGS_NETPROFITDISPLAYTEXT"].updateText(text  = "-", textStyle = 'DEFAULT')
            guios["HISTORY_TRADELOGS_GAINDISPLAYTEXT"].updateText(text       = "-")
            guios["HISTORY_TRADELOGS_LOSSDISPLAYTEXT"].updateText(text       = "-")
            guios["HISTORY_TRADELOGS_TRADINGFEEDISPLAYTEXT"].updateText(text = "-")
            #[2-2]: Logs Counter Display Update
            guios["HISTORY_TRADELOGS_NTOTALLOGSDISPLAYTEXT"].updateText(text    = "- / -")
            guios["HISTORY_TRADELOGS_NASSETLOGSDISPLAYTEXT"].updateText(text    = "- / -")
            guios["HISTORY_TRADELOGS_NPOSITIONLOGSDISPLAYTEXT"].updateText(text = "- / -")
            guios["HISTORY_TRADELOGS_NTIMELOGSDISPLAYTEXT"].updateText(text     = "- / -")
            guios["HISTORY_TRADELOGS_NBUYDISPLAYTEXT"].updateText(text          = "- / -")
            guios["HISTORY_TRADELOGS_NSELLDISPLAYTEXT"].updateText(text         = "- / -")
            guios["HISTORY_TRADELOGS_NLIQUIDATIONDISPLAYTEXT"].updateText(text  = "- / -")
            guios["HISTORY_TRADELOGS_NFSLIMMEDDISPLAYTEXT"].updateText(text     = "- / -")
            guios["HISTORY_TRADELOGS_NFSLCLOSEDISPLAYTEXT"].updateText(text     = "- / -")
            guios["HISTORY_TRADELOGS_NENTRYDISPLAYTEXT"].updateText(text        = "- / -")
            guios["HISTORY_TRADELOGS_NCLEARDISPLAYTEXT"].updateText(text        = "- / -")
            guios["HISTORY_TRADELOGS_NEXITDISPLAYTEXT"].updateText(text         = "- / -")
            guios["HISTORY_TRADELOGS_NFORCECLEARDISPLAYTEXT"].updateText(text   = "- / -")
            guios["HISTORY_TRADELOGS_NUNKNOWNDISPLAYTEXT"].updateText(text      = "- / -")
            #[2-3]: Finally
            return
        


        #[3]: Account Data
        positions    = account['positions']
        assetName    = guios["HISTORY_ASSETSELECTIONBOX"].getSelected()
        symbol       = guios["HISTORY_POSITIONSELECTIONBOX"].getSelected()
        tls          = puVar['historyView_tradeLogs'] or []
        tls_fIndices = set()



        #[4]: Filter Params
        tFilter_beg_str = guios["HISTORY_TRADELOGS_TIMEFILTERINPUTTEXT1"].getText()
        tFilter_end_str = guios["HISTORY_TRADELOGS_TIMEFILTERINPUTTEXT2"].getText()
        if tFilter_beg_str == "": rangeBeg = float('-inf')
        else:
            try:    rangeBeg = datetime.strptime(tFilter_beg_str, "%Y/%m/%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
            except: rangeBeg = None
        if tFilter_end_str == "": rangeEnd = float('inf')
        else:
            try:    rangeEnd = datetime.strptime(tFilter_end_str, "%Y/%m/%d %H:%M:%S").replace(tzinfo=timezone.utc).timestamp()
            except: rangeEnd = None
        if rangeBeg is not None and rangeEnd is not None and rangeBeg <= rangeEnd: filter_time = (rangeBeg, rangeEnd)
        else:                                                                      filter_time = None
        filter = {'asset':        assetName,
                  'symbol':       symbol,
                  'time':         filter_time,
                  'side':         set(),
                  'logicSource':  set()}
        if guios["HISTORY_TRADELOGS_SIDEFILTERBUY"].getStatus():                filter['side'].add('BUY')
        if guios["HISTORY_TRADELOGS_SIDEFILTERSELL"].getStatus():               filter['side'].add('SELL')
        if guios["HISTORY_TRADELOGS_LOGICSOURCEFILTERLIQUIDATION"].getStatus(): filter['logicSource'].add('LIQUIDATION')
        if guios["HISTORY_TRADELOGS_LOGICSOURCEFILTERFSLIMMED"].getStatus():    filter['logicSource'].add('FSLIMMED')
        if guios["HISTORY_TRADELOGS_LOGICSOURCEFILTERFSLCLOSE"].getStatus():    filter['logicSource'].add('FSLCLOSE')
        if guios["HISTORY_TRADELOGS_LOGICSOURCEFILTERENTRY"].getStatus():       filter['logicSource'].add('ENTRY')
        if guios["HISTORY_TRADELOGS_LOGICSOURCEFILTERCLEAR"].getStatus():       filter['logicSource'].add('CLEAR')
        if guios["HISTORY_TRADELOGS_LOGICSOURCEFILTEREXIT"].getStatus():        filter['logicSource'].add('EXIT')
        if guios["HISTORY_TRADELOGS_LOGICSOURCEFILTERFORCECLEAR"].getStatus():  filter['logicSource'].add('FORCECLEAR')
        if guios["HISTORY_TRADELOGS_LOGICSOURCEFILTERUNKNOWN"].getStatus():     filter['logicSource'].add('UNKNOWN')



        #[5]: Filtering
        for tlIdx, tl in enumerate(tls):
            #Asset
            fAsset = filter['asset']
            if fAsset != '#ALL#' and positions[tl['positionSymbol']]['quoteAsset'] != fAsset:
                continue
            #Symbol
            fSymbol = filter['symbol']
            if fSymbol != '#ALL#' and tl['positionSymbol'] != fSymbol:
                continue
            #Time
            fTime = filter['time']
            if fTime is not None and not fTime[0] <= tl['timestamp'] <= fTime[1]:
                continue
            #Side
            if tl['side'] not in filter['side']: 
                continue
            #Logic Source
            if tl['logicSource'] not in filter['logicSource']: 
                continue
            #FINALLY
            tls_fIndices.add(tlIdx)
        guios["HISTORY_TRADELOGS_TRADELOGSELECTIONBOX"].setDisplayTargets(displayTargets = sorted(tls_fIndices, reverse = True))



        #[6]: Net Proft, Gain, Loss, Trading Fee Display Update
        if assetName == '#ALL#':
            guios["HISTORY_TRADELOGS_NETPROFITDISPLAYTEXT"].updateText(text  = "N/A", textStyle = 'DEFAULT')
            guios["HISTORY_TRADELOGS_GAINDISPLAYTEXT"].updateText(text       = "N/A")
            guios["HISTORY_TRADELOGS_LOSSDISPLAYTEXT"].updateText(text       = "N/A")
            guios["HISTORY_TRADELOGS_TRADINGFEEDISPLAYTEXT"].updateText(text = "N/A")
        else:
            gain       = 0
            loss       = 0
            tradingFee = 0
            for tlIdx in tls_fIndices:
                tl = tls[tlIdx]
                if tl['profit'] is not None:
                    if   0 < tl['profit']: gain +=  tl['profit']
                    elif tl['profit'] < 0: loss += -tl['profit']
                if tl['tradingFee'] is not None: 
                    tradingFee += tl['tradingFee']
            guios["HISTORY_TRADELOGS_GAINDISPLAYTEXT"].updateText(text       = f"{auxiliaries.floatToString(number = gain,       precision = _ASSETPRECISIONS_XS[assetName])} {assetName}")
            guios["HISTORY_TRADELOGS_LOSSDISPLAYTEXT"].updateText(text       = f"{auxiliaries.floatToString(number = loss,       precision = _ASSETPRECISIONS_XS[assetName])} {assetName}")
            guios["HISTORY_TRADELOGS_TRADINGFEEDISPLAYTEXT"].updateText(text = f"{auxiliaries.floatToString(number = tradingFee, precision = _ASSETPRECISIONS_XS[assetName])} {assetName}")
            netProfit = round(gain-loss-tradingFee, _ASSETPRECISIONS[assetName])
            if   netProfit < 0:  text = f"{auxiliaries.floatToString(number  = netProfit, precision = _ASSETPRECISIONS_XS[assetName])}"; textCol = 'RED_LIGHT'
            elif netProfit == 0: text = f"{auxiliaries.floatToString(number  = netProfit, precision = _ASSETPRECISIONS_XS[assetName])}"; textCol = 'DEFAULT'
            else:                text = f"+{auxiliaries.floatToString(number = netProfit, precision = _ASSETPRECISIONS_XS[assetName])}"; textCol = 'GREEN_LIGHT'
            netProfit_text      = ""
            netProfit_textStyle = []
            for _text, _tStyle in ((text,             textCol), 
                                   (f" {assetName}", 'DEFAULT')):
                netProfit_textStyle.append(((len(netProfit_text), len(netProfit_text)+len(_text)-1), _tStyle))
                netProfit_text += _text
            guios["HISTORY_TRADELOGS_NETPROFITDISPLAYTEXT"].updateText(text = netProfit_text, textStyle = netProfit_textStyle)



        #[7]: Logs Counter Display Update
        #Setup
        nLogs_total_total,       nLogs_total_viewing       = 0,0
        nLogs_asset_total,       nLogs_asset_viewing       = 0,0
        nLogs_position_total,    nLogs_position_viewing    = 0,0
        nLogs_time_total,        nLogs_time_viewing        = 0,0
        nLogs_buy_total,         nLogs_buy_viewing         = 0,0
        nLogs_sell_total,        nLogs_sell_viewing        = 0,0
        nLogs_liquidation_total, nLogs_liquidation_viewing = 0,0
        nLogs_fslImmed_total,    nLogs_fslImmed_viewing    = 0,0
        nLogs_fslClose_total,    nLogs_fslClose_viewing    = 0,0
        nLogs_entry_total,       nLogs_entry_viewing       = 0,0
        nLogs_clear_total,       nLogs_clear_viewing       = 0,0
        nLogs_exit_total,        nLogs_exit_viewing        = 0,0
        nLogs_forceClear_total,  nLogs_forceClear_viewing  = 0,0
        nLogs_unknown_total,     nLogs_unknown_viewing     = 0,0
        #Counting
        fAsset  = filter['asset']
        fSymbol = filter['symbol']
        fTime   = filter['time']
        for tlIdx, tl in enumerate(tls):
            #Main
            isViewing     = (tlIdx in tls_fIndices)
            test_asset    = (fAsset == '#ALL#' or fAsset == positions[tl['positionSymbol']]['quoteAsset'])
            test_position = (test_asset and (fSymbol == '#ALL#' or fSymbol == tl['positionSymbol']))
            test_time     = (fTime is None or fTime[0] <= tl['timestamp'] <= fTime[1])
            #---[1]: Total
            nLogs_total_total += 1
            if isViewing: nLogs_total_viewing += 1
            #---[2]: Asset
            if test_asset:
                nLogs_asset_total += 1
                if isViewing: nLogs_asset_viewing += 1
            #---[3]: Position
            if test_position:
                nLogs_position_total += 1
                if isViewing: nLogs_position_viewing += 1
            #---[4]: Time
            if test_time:
                if test_position: nLogs_time_total   += 1
                if isViewing:     nLogs_time_viewing += 1

            #Side
            log_side = tl['side']
            #---[5]: Buy
            if log_side == 'BUY':
                if test_position and test_time: nLogs_buy_total   += 1
                if isViewing:                   nLogs_buy_viewing += 1
            #---[6]: Sell
            elif log_side == 'SELL':
                if test_position and test_time: nLogs_sell_total   += 1
                if isViewing:                   nLogs_sell_viewing += 1

            #Logic Source
            log_logicSource = tl['logicSource']
            #---[7]: Liquidation
            if log_logicSource == 'LIQUIDATION':
                if test_position and test_time: nLogs_liquidation_total   += 1
                if isViewing:                   nLogs_liquidation_viewing += 1
            #---[8]: FSLIMMED
            elif log_logicSource == 'FSLIMMED':
                if test_position and test_time: nLogs_fslImmed_total   += 1
                if isViewing:                   nLogs_fslImmed_viewing += 1
            #---[9]: FSLCLOSE
            elif log_logicSource == 'FSLCLOSE':
                if test_position and test_time: nLogs_fslClose_total   += 1
                if isViewing:                   nLogs_fslClose_viewing += 1
            #---[10]: Entry
            elif log_logicSource == 'ENTRY':
                if test_position and test_time: nLogs_entry_total   += 1
                if isViewing:                   nLogs_entry_viewing += 1
            #---[11]: Clear
            elif log_logicSource == 'CLEAR':
                if test_position and test_time: nLogs_clear_total   += 1
                if isViewing:                   nLogs_clear_viewing += 1
            #---[12]: Exit
            elif log_logicSource == 'EXIT':
                if test_position and test_time: nLogs_exit_total   += 1
                if isViewing:                   nLogs_exit_viewing += 1
            #---[13]: Force Clear
            elif log_logicSource == 'FORCECLEAR':
                if test_position and test_time: nLogs_forceClear_total   += 1
                if isViewing:                   nLogs_forceClear_viewing += 1
            #---[14]: Unknown
            elif log_logicSource == 'UNKNOWN':
                if test_position and test_time: nLogs_unknown_total   += 1
                if isViewing:                   nLogs_unknown_viewing += 1
        #Text Update
        guios["HISTORY_TRADELOGS_NTOTALLOGSDISPLAYTEXT"].updateText(text    = f"{nLogs_total_viewing:,d} / {nLogs_total_total:,d}")
        guios["HISTORY_TRADELOGS_NASSETLOGSDISPLAYTEXT"].updateText(text    = f"{nLogs_asset_viewing:,d} / {nLogs_asset_total:,d}")
        guios["HISTORY_TRADELOGS_NPOSITIONLOGSDISPLAYTEXT"].updateText(text = f"{nLogs_position_viewing:,d} / {nLogs_position_total:,d}")
        guios["HISTORY_TRADELOGS_NTIMELOGSDISPLAYTEXT"].updateText(text     = f"{nLogs_time_viewing:,d} / {nLogs_time_total:,d}")
        guios["HISTORY_TRADELOGS_NBUYDISPLAYTEXT"].updateText(text          = f"{nLogs_buy_viewing:,d} / {nLogs_buy_total:,d}")
        guios["HISTORY_TRADELOGS_NSELLDISPLAYTEXT"].updateText(text         = f"{nLogs_sell_viewing:,d} / {nLogs_sell_total:,d}")
        guios["HISTORY_TRADELOGS_NLIQUIDATIONDISPLAYTEXT"].updateText(text  = f"{nLogs_liquidation_viewing:,d} / {nLogs_liquidation_total:,d}")
        guios["HISTORY_TRADELOGS_NFSLIMMEDDISPLAYTEXT"].updateText(text     = f"{nLogs_fslImmed_viewing:,d} / {nLogs_fslImmed_total:,d}")
        guios["HISTORY_TRADELOGS_NFSLCLOSEDISPLAYTEXT"].updateText(text     = f"{nLogs_fslClose_viewing:,d} / {nLogs_fslClose_total:,d}")
        guios["HISTORY_TRADELOGS_NENTRYDISPLAYTEXT"].updateText(text        = f"{nLogs_entry_viewing:,d} / {nLogs_entry_total:,d}")
        guios["HISTORY_TRADELOGS_NCLEARDISPLAYTEXT"].updateText(text        = f"{nLogs_clear_viewing:,d} / {nLogs_clear_total:,d}")
        guios["HISTORY_TRADELOGS_NEXITDISPLAYTEXT"].updateText(text         = f"{nLogs_exit_viewing:,d} / {nLogs_exit_total:,d}")
        guios["HISTORY_TRADELOGS_NFORCECLEARDISPLAYTEXT"].updateText(text   = f"{nLogs_forceClear_viewing:,d} / {nLogs_forceClear_total:,d}")
        guios["HISTORY_TRADELOGS_NUNKNOWNDISPLAYTEXT"].updateText(text      = f"{nLogs_unknown_viewing:,d} / {nLogs_unknown_total:,d}")
    def __onTradeLogSelectionUpdate():
        if (self.puVar['accounts_selected'] != None): _positions = self.puVar['accounts'][self.puVar['accounts_selected']]['positions']
        else:                                         _positions = None
        try:    _logIndex_selected = self.GUIOs["HISTORY_TRADELOGS_TRADELOGSELECTIONBOX"].getSelected()[0]
        except: _logIndex_selected = None
        if (_logIndex_selected != None):
            _tradeLog = self.puVar['historyView_tradeLogs'][_logIndex_selected]
            _positionSymbol = _tradeLog['positionSymbol']
            _precisions = _positions[_positionSymbol]['precisions']
        else: pass
    auxFunctions['SETTRADELOGSLIST']          = __setTradeLogsList
    auxFunctions['ONTRADELOGSFILTERUPDATE']   = __onTradeLogsFilterUpdate
    auxFunctions['ONTRADELOGSELECTIONUPDATE'] = __onTradeLogSelectionUpdate

    #Return the generated functions
    return auxFunctions
#AUXILALRY FUNCTIONS END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------