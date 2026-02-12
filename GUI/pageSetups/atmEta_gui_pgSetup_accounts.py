#ATM Modules
import atmEta_IPC
import atmEta_Auxillaries
from GUI import atmEta_gui_AdvancedPygletGroups
from GUI.atmEta_gui_TextControl import textObject_SL, textObject_SL_I, textObject_SL_IE
from GUI.atmEta_gui_Generals import passiveGraphics_typeA,\
                                    passiveGraphics_wrapperTypeA,\
                                    passiveGraphics_wrapperTypeB,\
                                    passiveGraphics_wrapperTypeC,\
                                    textBox_typeA,\
                                    imageBox_typeA,\
                                    button_typeA,\
                                    button_typeB,\
                                    switch_typeA,\
                                    switch_typeB,\
                                    switch_typeC,\
                                    slider_typeA,\
                                    scrollBar_typeA,\
                                    textInputBox_typeA,\
                                    LED_typeA,\
                                    gaugeBar_typeA,\
                                    selectionBox_typeA,\
                                    selectionBox_typeB,\
                                    selectionBox_typeC,\
                                    subPageBox_typeA
from GUI.atmEta_gui_ChartDrawer          import chartDrawer
from GUI.atmEta_gui_PeriodicReportViewer import periodicReportViewer
from GUI.atmEta_gui_NeuralNetworkViewer  import neuralNetworkViewer

#Python Modules
import pyglet
import pprint
import termcolor
import os
import string
import time
import json
import random
from datetime import datetime, timezone, tzinfo
from cryptography.fernet import Fernet
import base64
import hashlib

#Constants
_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT

_ASSETPRECISIONS    = {'USDT': 8, 'USDC': 8, 'BTC': 6}
_ASSETPRECISIONS_S  = {'USDT': 4, 'USDC': 4, 'BTC': 4}
_ASSETPRECISIONS_XS = {'USDT': 2, 'USDC': 2, 'BTC': 2}

_POSITIONDATA_SELECTIONBOXCOLUMNINDEX = {'tradable':                {'BASIC': None, 'TRADER': 2,    'DETAIL': 2},
                                         'tradeStatus':             {'BASIC': 2,    'TRADER': 3,    'DETAIL': 3},
                                         'reduceOnly':              {'BASIC': None, 'TRADER': 4,    'DETAIL': 4},
                                         'leverage':                {'BASIC': 3,    'TRADER': None, 'DETAIL': 5},
                                         'isolated':                {'BASIC': 4,    'TRADER': None, 'DETAIL': 6},
                                         'quantity':                {'BASIC': 5,    'TRADER': None, 'DETAIL': 7},
                                         'isolatedWalletBalance':   {'BASIC': None, 'TRADER': None, 'DETAIL': 8},
                                         'positionInitialMargin':   {'BASIC': None, 'TRADER': None, 'DETAIL': 9},
                                         'openOrderInitialMargin':  {'BASIC': None, 'TRADER': None, 'DETAIL': 10},
                                         'maintenanceMargin':       {'BASIC': None, 'TRADER': None, 'DETAIL': 11},
                                         'entryPrice':              {'BASIC': 6,    'TRADER': None, 'DETAIL': 12},
                                         'currentPrice':            {'BASIC': 7,    'TRADER': None, 'DETAIL': 13},
                                         'liquidationPrice':        {'BASIC': 8,    'TRADER': None, 'DETAIL': 14},
                                         'unrealizedPNL':           {'BASIC': 9,    'TRADER': None, 'DETAIL': 15},
                                         'assumedRatio':            {'BASIC': 10,   'TRADER': 8,    'DETAIL': 16},
                                         'weightedAssumedRatio':    {'BASIC': None, 'TRADER': None, 'DETAIL': 17},
                                         'allocatedBalance':        {'BASIC': 11,   'TRADER': None, 'DETAIL': 18},
                                         'maxAllocatedBalance':     {'BASIC': None, 'TRADER': 9,    'DETAIL': 19},
                                         'commitmentRate':          {'BASIC': 12,   'TRADER': None, 'DETAIL': 20},
                                         'riskLevel':               {'BASIC': 13,   'TRADER': None, 'DETAIL': 21},
                                         'currencyAnalysisCode':    {'BASIC': None, 'TRADER': 5,    'DETAIL': 22},
                                         'tradeConfigurationCode':  {'BASIC': None, 'TRADER': 6,    'DETAIL': 23},
                                         'priority':                {'BASIC': None, 'TRADER': 7,    'DETAIL': 24},
                                         'tradeControlTracker':     {'BASIC': None, 'TRADER': 10,   'DETAIL': 25},
                                         'abruptClearingRecords':   {'BASIC': None, 'TRADER': 11,   'DETAIL': 26}}

_PERIODICPOSITIONSSORTING_ACTIVATIONSORTTYPES = {'LEVERAGE', 'UNREALIZEDPNL', 'COMMITMENTRATE', 'RISKLEVEL'}
_PERIODICPOSITIONSSORTING_INTERVAL_NS         = 5e9

#SETUP PAGE <MAIN> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setupPage(self):
    #Set page unique variables
    self.puVar['currencies'] = dict()
    self.puVar['accounts']           = dict()
    self.puVar['accounts_selected']  = None
    self.puVar['accounts_passwords'] = dict()
    self.puVar['positions_selected'] = None
    self.puVar['currencyAnalysis']          = dict()
    self.puVar['currencyAnalysis_selected'] = None
    self.puVar['currencyAnalysis_forSelectedPosition'] = set()
    self.puVar['tradeConfigurations']         = dict()
    self.puVar['tradeConfiguration_selected'] = None

    self.puVar['periodicPositionsSorting_lastSorted_ns'] = 0

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
        self.GUIOs["TITLETEXT_ACCOUNTS"] = textBox_typeA(**inst, groupOrder=1, xPos= 7000, yPos=8550, width=2000, height=400, style=None, text=self.visualManager.getTextPack('ACCOUNTS:TITLE'), fontSize = 220, textInteractable = False)

        self.GUIOs["BUTTON_MOVETO_DASHBOARD"] = button_typeB(**inst,  groupOrder=2, xPos=  50, yPos=8650, width= 300, height=300, style="styleB", releaseFunction=self.pageObjectFunctions['PAGEMOVE_DASHBOARD'], image = 'dashboardIcon_512x512.png', imageSize = (225, 225), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))

        #Accounts List
        self.GUIOs["BLOCKTITLE_ACCOUNTSLIST"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=8350, width=4900, height=200, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:BLOCKTITLE_ACCOUNTSLIST'), fontSize = 80)
        self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_VIRTUAL"] = switch_typeC(**inst,       groupOrder=1, xPos= 100, yPos=8000, width=2400, height= 250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTS:ACCOUNTLIST_VIRTUAL'), fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_ACCOUNTLIST_FILTERSWITCH_VIRTUAL'])
        self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_ACTUAL"]  = switch_typeC(**inst,       groupOrder=1, xPos=2600, yPos=8000, width=2400, height= 250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTS:ACCOUNTLIST_ACTUAL'),  fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_ACCOUNTLIST_FILTERSWITCH_ACTUAL'])
        self.GUIOs["ACCOUNTSLIST_SELECTIONBOX"]         = selectionBox_typeC(**inst, groupOrder=1, xPos= 100, yPos=4600, width=4900, height=3300, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_LIST_ACCOUNT'], elementWidths = (600, 1600, 800, 800, 800))
        self.GUIOs["ACCOUNTSLIST_SELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('ACCOUNTS:ACCOUNTLIST_INDEX')},
                                                                                 {'text': self.visualManager.getTextPack('ACCOUNTS:ACCOUNTLIST_LOCALID')},
                                                                                 {'text': self.visualManager.getTextPack('ACCOUNTS:ACCOUNTLIST_TYPE')},
                                                                                 {'text': self.visualManager.getTextPack('ACCOUNTS:ACCOUNTLIST_STATUS')},
                                                                                 {'text': self.visualManager.getTextPack('ACCOUNTS:ACCOUNTLIST_TRADESTATUS')}])

        #Accounts Information & Control
        self.GUIOs["BLOCKTITLE_ACCOUNTSINFORMATION&CONTROL"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=4300, width=4900, height=200, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:BLOCKTITLE_ACCOUNTSINFORMATION&CONTROL'), fontSize = 80)
        #---Local ID
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_LOCALIDTITLETEXT"]            = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=3950, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_LOCALID'),      fontSize=80, textInteractable=False)
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_LOCALIDTEXTINPUTBOX"]         = textInputBox_typeA(**inst, groupOrder=1, xPos=1700, yPos=3950, width=3300, height=250, style="styleA", text="",                                                                                  fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_ACCOUNTSINFORMATION&CONTROL_LOCALID'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_LOCALIDDISPLAYTEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos=1700, yPos=3950, width=3300, height=250, style="styleA", text="-",                                                                                 fontSize=80, textInteractable=False)
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_LOCALIDDISPLAYTEXT"].hide()
        #---Binance UserID
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDTITLETEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=3600, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_BINANCEUID'),   fontSize=80, textInteractable=False)
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDTEXTINPUTBOX"]      = textInputBox_typeA(**inst, groupOrder=1, xPos=1700, yPos=3600, width=3300, height=250, style="styleA", text="",                                                                                  fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_ACCOUNTSINFORMATION&CONTROL_BUID'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDTEXTINPUTBOX"].deactivate()
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDDISPLAYTEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos=1700, yPos=3600, width=3300, height=250, style="styleA", text="-",                                                                                 fontSize=80, textInteractable=False)
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDDISPLAYTEXT"].hide()
        #---Account Type
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPETITLETEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=3250, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPE'),  fontSize=80, textInteractable=False)
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPESELECTIONBOX"]     = selectionBox_typeB(**inst, groupOrder=2, xPos=1700, yPos=3250, width=3300, height=250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction=self.pageObjectFunctions['ONSELECTIONUPDATE_ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPE'])
        _accountTypes = {'VIRTUAL': {'text': 'VIRTUAL'},
                         'ACTUAL':  {'text': 'ACTUAL'}}
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPESELECTIONBOX"].setSelectionList(selectionList = _accountTypes, displayTargets = 'all')
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPESELECTIONBOX"].setSelected(itemKey = 'VIRTUAL', callSelectionUpdateFunction = False)
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPEDISPLAYTEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos=1700, yPos=3250, width=3300, height=250, style="styleA", text="-",                                                                                 fontSize=80, textInteractable=False)
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPEDISPLAYTEXT"].hide()
        #---Status
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_STATUSTITLETEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=2900, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_STATUS'),       fontSize=80, textInteractable=False)
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_STATUSDISPLAYTEXT"]           = textBox_typeA(**inst,      groupOrder=1, xPos=1700, yPos=2900, width=3300, height=250, style="styleA", text="-",                                                                                 fontSize=80, textInteractable=False)
        #---Trade Status
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSTITLETEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=2550, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_TRADESTATUS'),  fontSize=80, textInteractable=False)
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSDISPLAYTEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos=1700, yPos=2550, width=2700, height=250, style="styleA", text="-",                                                                                 fontSize=80, textInteractable=False)
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSSWITCH"]           = switch_typeB(**inst,       groupOrder=2, xPos=4500, yPos=2550, width= 500, height=250, style="styleA", align='horizontal', switchStatus=False, statusUpdateFunction = self.pageObjectFunctions['ONSTATUSUPDATE_ACCOUNTSINFORMATION&CONTROL_TRADESTATUSSWITCH'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSSWITCH"].deactivate()
        #---API Key
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTITLETEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=2200, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_APIKEY'),       fontSize=80, textInteractable=False)
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"]          = textInputBox_typeA(**inst, groupOrder=1, xPos=1700, yPos=2200, width=3300, height=250, style="styleA", text="",                                                                                  fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_ACCOUNTSINFORMATION&CONTROL_APIKEY'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"].deactivate()
        #---Secret Key
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTITLETEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=1850, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_SECRETKEY'),    fontSize=80, textInteractable=False)
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"]       = textInputBox_typeA(**inst, groupOrder=1, xPos=1700, yPos=1850, width=3300, height=250, style="styleA", text="",                                                                                  fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_ACCOUNTSINFORMATION&CONTROL_SECRETKEY'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"].deactivate()
        #---Password
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTITLETEXT"]           = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=1500, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_PASSWORD'),     fontSize=80, textInteractable=False)
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"]        = textInputBox_typeA(**inst, groupOrder=1, xPos=1700, yPos=1500, width=2200, height=250, style="styleA", text="",                                                                                  fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_ACCOUNTSINFORMATION&CONTROL_PASSWORD'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDHOLDRELEASESWITCH"]   = switch_typeC(**inst,       groupOrder=1, xPos=4000, yPos=1500, width=1000, height=250, style="styleB", text=self.visualManager.getTextPack('ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_HOLDPASSWORD'), fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSTATUSUPDATE_ACCOUNTSINFORMATION&CONTROL_PASSWORDHOLDRELEASE'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDHOLDRELEASESWITCH"].deactivate()
        #---Activation Buttons
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYENTEREDKEYSBUTTON"] = button_typeA(**inst,       groupOrder=1, xPos= 100, yPos=1150, width=3000, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYENTEREDKEYS'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYENTEREDKEYS'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_DEACTIVATEBUTTON"]            = button_typeA(**inst,       groupOrder=1, xPos=3200, yPos=1150, width=1800, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_DEACTIVATE'),            fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_ACCOUNTSINFORMATION&CONTROL_DEACTIVATE'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAFBUTTON"]         = button_typeA(**inst,       groupOrder=1, xPos= 100, yPos= 800, width=3000, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAF'),         fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAF'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_GENERATEAAFBUTTON"]           = button_typeA(**inst,       groupOrder=1, xPos=3200, yPos= 800, width=1800, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_GENERATEAAF'),           fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_ACCOUNTSINFORMATION&CONTROL_GENERATEAAF'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYENTEREDKEYSBUTTON"].deactivate()
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_DEACTIVATEBUTTON"].deactivate()
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAFBUTTON"].deactivate()
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_GENERATEAAFBUTTON"].deactivate()
        #---Account Add/Remove Buttons
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ADDACCOUNTBUTTON"]            = button_typeA(**inst,       groupOrder=1, xPos= 100, yPos= 450, width=3000, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_ADDACCOUNT'),            fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_ACCOUNTSINFORMATION&CONTROL_ADDACCOUNT'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNTBUTTON"]         = button_typeA(**inst,       groupOrder=1, xPos=3200, yPos= 450, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNT'),         fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNT'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNTBUTTONSWITCH"]   = switch_typeB(**inst,       groupOrder=2, xPos=4500, yPos= 450, width= 500, height=250, style="styleA", align='horizontal', switchStatus=False, statusUpdateFunction = self.pageObjectFunctions['ONSTATUSUPDATE_ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNTSWITCH'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ADDACCOUNTBUTTON"].deactivate()
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNTBUTTON"].deactivate()
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNTBUTTONSWITCH"].deactivate()

        #Assets
        self.GUIOs["BLOCKTITLE_ASSETS"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=5100, yPos=8350, width=10800, height=200, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:BLOCKTITLE_ASSETS'), fontSize = 80)
        self.GUIOs["ASSETS_IMAGEBOX"]  = imageBox_typeA(**inst, groupOrder=1, xPos=5100, yPos=8000, width= 250, height=250, style=None, image="usdtIcon_512x512.png")
        self.GUIOs["ASSETS_TITLETEXT"] = textBox_typeA(**inst,  groupOrder=1, xPos=5400, yPos=8000, width=4400, height=250, style=None, text="USDT", anchor='W', fontSize=120, textInteractable=False)
        self.GUIOs["ASSETS_MARGINBALANCETITLETEXT"]           = textBox_typeA(**inst, groupOrder=1, xPos= 5100, yPos=7650, width=1700, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_MARGINBALANCE'),         fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_MARGINBALANCEDISPLAYTEXT"]         = textBox_typeA(**inst, groupOrder=1, xPos= 6900, yPos=7650, width=1500, height=250, style="styleA", text="-",                                                                     fontSize=80, textInteractable=True)
        self.GUIOs["ASSETS_WALLETBALANCETITLETEXT"]           = textBox_typeA(**inst, groupOrder=1, xPos= 8500, yPos=7650, width=3300, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_WALLETBALANCE'),         fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_WALLETBALANCEDISPLAYTEXT"]         = textBox_typeA(**inst, groupOrder=1, xPos=11900, yPos=7650, width=4000, height=250, style="styleA", text="-",                                                                     fontSize=80, textInteractable=True)
        self.GUIOs["ASSETS_AVAILABLEBALANCETITLETEXT"]        = textBox_typeA(**inst, groupOrder=1, xPos= 5100, yPos=7300, width=1700, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_AVAILABLEBALANCE'),      fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_AVAILABLEBALANCEDISPLAYTEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos= 6900, yPos=7300, width=1500, height=250, style="styleA", text="-",                                                                     fontSize=80, textInteractable=True)
        self.GUIOs["ASSETS_MARGINTITLETEXT"]                  = textBox_typeA(**inst, groupOrder=1, xPos= 8500, yPos=7300, width=3300, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_MARGIN'),                fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_MARGINDISPLAYTEXT"]                = textBox_typeA(**inst, groupOrder=1, xPos=11900, yPos=7300, width=4000, height=250, style="styleA", text="-",                                                                     fontSize=80, textInteractable=True)
        self.GUIOs["ASSETS_ALLOCATABLEBALANCETITLETEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos= 5100, yPos=6950, width=1700, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_ALLOCATABLEBALANCE'),    fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_ALLOCATABLEBALANCEDISPLAYTEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos= 6900, yPos=6950, width=1500, height=250, style="styleA", text="-",                                                                     fontSize=80, textInteractable=True)
        self.GUIOs["ASSETS_POSITIONINITIALMARGINTITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 8500, yPos=6950, width=3300, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_POSITIONINITIALMARGIN'), fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_POSITIONINITIALMARGINDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=11900, yPos=6950, width=4000, height=250, style="styleA", text="-",                                                                     fontSize=80, textInteractable=True)
        self.GUIOs["ASSETS_ALLOCATEDBALANCETITLETEXT"]        = textBox_typeA(**inst, groupOrder=1, xPos= 5100, yPos=6600, width=1700, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_ALLOCATEDBALANCE'),      fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_ALLOCATEDBALANCEDISPLAYTEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos= 6900, yPos=6600, width=1500, height=250, style="styleA", text="-",                                                                     fontSize=80, textInteractable=True)
        self.GUIOs["ASSETS_UNREALIZEDPNLTITLETEXT"]           = textBox_typeA(**inst, groupOrder=1, xPos= 8500, yPos=6600, width=3300, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_UNREALIZEDPNL'),         fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_UNREALIZEDPNLDISPLAYTEXT"]         = textBox_typeA(**inst, groupOrder=1, xPos=11900, yPos=6600, width=4000, height=250, style="styleA", text="-",                                                                     fontSize=80, textInteractable=True)
        self.GUIOs["ASSETS_COMMITMENTRATETITLETEXT"]          = textBox_typeA(**inst, groupOrder=1, xPos= 5100, yPos=6250, width=1525, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_COMMITMENTRATE'),        fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_COMMITMENTRATEDISPLAYTEXT"]        = textBox_typeA(**inst, groupOrder=1, xPos= 6725, yPos=6250, width=1000, height=250, style="styleA", text="-",                                                                     fontSize=80, textInteractable=True)
        self.GUIOs["ASSETS_RISKLEVELTITLETEXT"]               = textBox_typeA(**inst, groupOrder=1, xPos= 7825, yPos=6250, width=1525, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_RISKLEVEL'),             fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_RISKLEVELDISPLAYTEXT"]             = textBox_typeA(**inst, groupOrder=1, xPos= 9450, yPos=6250, width=1000, height=250, style="styleA", text="-",                                                                     fontSize=80, textInteractable=True)
        self.GUIOs["ASSETS_BASEASSUMEDRATIOTITLETEXT"]        = textBox_typeA(**inst, groupOrder=1, xPos=10550, yPos=6250, width=1525, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_BASEASSUMEDRATIO'),      fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_BASEASSUMEDRATIODISPLAYTEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos=12175, yPos=6250, width=1000, height=250, style="styleA", text="-",                                                                     fontSize=80, textInteractable=True)
        self.GUIOs["ASSETS_WEIGHTEDASSUMEDRATIOTITLETEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos=13275, yPos=6250, width=1525, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_WEIGHTEDASSUMEDRATIO'),  fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_WEIGHTEDASSUMEDRATIODISPLAYTEXT"]  = textBox_typeA(**inst, groupOrder=1, xPos=14900, yPos=6250, width=1000, height=250, style="styleA", text="-",                                                                     fontSize=80, textInteractable=True)

        #---Select Asset
        self.GUIOs["ASSETS_ASSETTODISPLAYTITLETEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos=5100, yPos=5900, width=800, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_ASSET'), fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_ASSETTODISPLAYSELECTIONBOX"]    = selectionBox_typeB(**inst, groupOrder=2, xPos=6000, yPos=5900, width=800, height=250, style="styleA", nDisplay = 5, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_ASSETS_ASSETTODISPLAY'])
        assetsToDisplay = {'USDT': {'text': 'USDT'},
                           'USDC': {'text': 'USDC'}}
        self.GUIOs["ASSETS_ASSETTODISPLAYSELECTIONBOX"].setSelectionList(selectionList = assetsToDisplay, displayTargets = 'all')
        self.GUIOs["ASSETS_ASSETTODISPLAYSELECTIONBOX"].setSelected(itemKey = 'USDT', callSelectionUpdateFunction = False)
        #---Transfer Balance
        self.GUIOs["ASSETS_TRASNFERBALANCETITLETEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos= 6900, yPos=5900, width=1300, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_TRANSFERBALANCE'), fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_TRASNFERBALANCETEXTINPUTBOX"]   = textInputBox_typeA(**inst, groupOrder=1, xPos= 8300, yPos=5900, width=1000, height=250, style="styleA", text="", fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_ASSETS_TRANSFERBALANCE'])
        self.GUIOs["ASSETS_TRASNFERBALANCETEXTINPUTBOX"].deactivate()
        self.GUIOs["ASSETS_TRASNFERBALANCEDEPOSITBUTTON"]  = button_typeA(**inst,       groupOrder=1, xPos= 9400, yPos=5900, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_DEPOSIT'),  fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_ASSETS_DEPOSITBALANCE'])
        self.GUIOs["ASSETS_TRASNFERBALANCEWITHDRAWBUTTON"] = button_typeA(**inst,       groupOrder=1, xPos=10200, yPos=5900, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_WITHDRAW'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_ASSETS_WITHDRAWBALANCE'])
        self.GUIOs["ASSETS_TRASNFERBALANCEDEPOSITBUTTON"].deactivate()
        self.GUIOs["ASSETS_TRASNFERBALANCEWITHDRAWBUTTON"].deactivate()
        self.GUIOs["ASSETS_TRASNFERBALANCESAFETYSWITCH"]   = switch_typeB(**inst,       groupOrder=2, xPos=11000, yPos=5900, width= 500, height=250, style="styleA", align='horizontal', switchStatus=False, statusUpdateFunction = self.pageObjectFunctions['ONSTATUSUPDATE_ASSETS_BALANCETRANSFERSWITCH'])
        self.GUIOs["ASSETS_TRASNFERBALANCESAFETYSWITCH"].deactivate()
        #---Allocation Ratio
        self.GUIOs["ASSETS_ALLOCATIONRATIOTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=11600, yPos=5900, width=1200, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_ALLOCATIONRATIO'), fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_ALLOCATIONRATIOSLIDER"]       = slider_typeA(**inst,       groupOrder=1, xPos=12900, yPos=5950, width=1400, height=150, style="styleA", valueUpdateFunction=self.pageObjectFunctions['ONVALUEUPDATE_ASSETS_ALLOCATIONRATIOSLIDER'])
        self.GUIOs["ASSETS_ALLOCATIONRATIODISPLAYTEXT"]  = textBox_typeA(**inst,      groupOrder=1, xPos=14400, yPos=5900, width= 800, height=250, style="styleA", text="-", fontSize=80, textInteractable=False)
        self.GUIOs["ASSETS_ALLOCATIONRATIOAPPLYBUTTON"]  = button_typeA(**inst,       groupOrder=1, xPos=15300, yPos=5900, width= 600, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:ASSETS_APPLY'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_ASSETS_APPLYNEWALLOCATIONRATIO'])
        self.GUIOs["ASSETS_ALLOCATIONRATIOSLIDER"].deactivate()
        self.GUIOs["ASSETS_ALLOCATIONRATIOAPPLYBUTTON"].deactivate()

        #Positions
        self.GUIOs["BLOCKTITLE_POSITIONS"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=5100, yPos=5600, width=10800, height=200, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:BLOCKTITLE_POSITIONS'), fontSize = 80)
        #---Filter
        #------Search Text & Type
        self.GUIOs["POSITIONS_SEARCHTITLETEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos= 5100, yPos=5250, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_SEARCH'), fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_SEARCHTEXTINPUTBOX"]     = textInputBox_typeA(**inst, groupOrder=1, xPos= 6200, yPos=5250, width=2000, height=250, style="styleA", text="", fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONOBJECTUPDATE_POSITIONS_FILTER'])
        self.GUIOs["POSITIONS_SEARCHTYPESELECTIONBOX"] = selectionBox_typeB(**inst, groupOrder=3, xPos= 8300, yPos=5250, width=1500, height=250, style="styleA", nDisplay = 5, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONOBJECTUPDATE_POSITIONS_FILTER'])
        searchTypes = {'SYMBOL': {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_SEARCH_SYMBOL')},
                       'CACODE': {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_SEARCH_CACODE')},
                       'TCCODE': {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_SEARCH_TCCODE')}}
        self.GUIOs["POSITIONS_SEARCHTYPESELECTIONBOX"].setSelectionList(selectionList = searchTypes, displayTargets = 'all')
        self.GUIOs["POSITIONS_SEARCHTYPESELECTIONBOX"].setSelected(itemKey = 'SYMBOL', callSelectionUpdateFunction = False)
        #------Sort Type
        self.GUIOs["POSITIONS_SORTBYTITLETEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos= 9900, yPos=5250, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_SORTBY'), fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_SORTBYSELECTIONBOX"]     = selectionBox_typeB(**inst, groupOrder=3, xPos=11000, yPos=5250, width=1500, height=250, style="styleA", nDisplay = 12, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONOBJECTUPDATE_POSITIONS_FILTER'])
        sortTypes = {'INDEX':                  {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_SORTBY_INDEX')},
                     'SYMBOL':                 {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_SORTBY_SYMBOL')},
                     'LEVERAGE':               {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_SORTBY_LEVERAGE')},
                     'UNREALIZEDPNL':          {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_SORTBY_UNREALIZEDPNL')},
                     'ASSUMEDRATIO':           {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_SORTBY_ASSUMEDRATIO')},
                     'WEIGHTEDASSUMEDRATIO':   {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_SORTBY_WEIGHTEDASSUMEDRATIO')},
                     'ALLOCATEDBALANCE':       {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_SORTBY_ALLOCATEDBALANCE')},
                     'COMMITMENTRATE':         {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_SORTBY_COMMITMENTRATE')},
                     'RISKLEVEL':              {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_SORTBY_RISKLEVEL')},
                     'CACODE':                 {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_SORTBY_CACODE')},
                     'TCCODE':                 {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_SORTBY_TCCODE')},
                     'PRIORITY':               {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_SORTBY_PRIORITY')}}
        self.GUIOs["POSITIONS_SORTBYSELECTIONBOX"].setSelectionList(selectionList = sortTypes, displayTargets = 'all')
        self.GUIOs["POSITIONS_SORTBYSELECTIONBOX"].setSelected(itemKey = 'INDEX', callSelectionUpdateFunction = False)
        #------Conditional
        self.GUIOs["POSITIONS_TRADESTATUSFILTERTITLETEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos= 5100, yPos=4900, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_TRADESTATUSFILTER'), fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_TRADESTATUSFILTERSELECTIONBOX"]          = selectionBox_typeB(**inst, groupOrder=2, xPos= 7200, yPos=4900, width=1400, height=250, style="styleA", nDisplay = 5, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONOBJECTUPDATE_POSITIONS_FILTER'])
        self.GUIOs["POSITIONS_TRADABLEFILTERTITLETEXT"]                = textBox_typeA(**inst,      groupOrder=1, xPos= 8700, yPos=4900, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_TRADABLEFILTER'), fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_TRADABLEFILTERSELECTIONBOX"]             = selectionBox_typeB(**inst, groupOrder=2, xPos=10800, yPos=4900, width=1400, height=250, style="styleA", nDisplay = 5, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONOBJECTUPDATE_POSITIONS_FILTER'])
        self.GUIOs["POSITIONS_QUANTITYFILTERTITLETEXT"]                = textBox_typeA(**inst,      groupOrder=1, xPos=12300, yPos=4900, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_QUANTITYFILTER'), fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_QUANTITYFILTERSELECTIONBOX"]             = selectionBox_typeB(**inst, groupOrder=2, xPos=14400, yPos=4900, width=1500, height=250, style="styleA", nDisplay = 5, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONOBJECTUPDATE_POSITIONS_FILTER'])
        self.GUIOs["POSITIONS_ASSUMEDRATIOFILTERTITLETEXT"]            = textBox_typeA(**inst,      groupOrder=1, xPos= 5100, yPos=4550, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ASSUMEDRATIOFILTER'), fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_ASSUMEDRATIOFILTERSELECTIONBOX"]         = selectionBox_typeB(**inst, groupOrder=2, xPos= 7200, yPos=4550, width=1400, height=250, style="styleA", nDisplay = 5, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONOBJECTUPDATE_POSITIONS_FILTER'])
        self.GUIOs["POSITIONS_ALLOCATEDBALANCEFILTERTITLETEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos= 8700, yPos=4550, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ALLOCATIONBALANCEFILTER'), fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_ALLOCATEDBALANCEFILTERSELECTIONBOX"]     = selectionBox_typeB(**inst, groupOrder=2, xPos=10800, yPos=4550, width=1400, height=250, style="styleA", nDisplay = 5, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONOBJECTUPDATE_POSITIONS_FILTER'])
        self.GUIOs["POSITIONS_CURRENCYANALYSISCODEFILTERTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=12300, yPos=4550, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_CURRENCYANALYSISCODEFILTER'), fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_CURRENCYANALYSISCODEFILTERSELECTIONBOX"] = selectionBox_typeB(**inst, groupOrder=2, xPos=14400, yPos=4550, width=1500, height=250, style="styleA", nDisplay = 5, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONOBJECTUPDATE_POSITIONS_FILTER'])
        conditionTypes_tradeStatus = {'ALL':   {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_ALL')},
                                      'TRUE':  {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_TRUE')},
                                      'FALSE': {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_FALSE')}}
        conditionTypes_tradable = {'ALL':   {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_ALL')},
                                   'TRUE':  {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_TRUE')},
                                   'FALSE': {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_FALSE')}}
        conditionTypes_quantity = {'ALL':     {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_ALL')},
                                   'NONZERO': {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_NONZERO')},
                                   'ZERO':    {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_ZERO')}}
        conditionTypes_assumedRatio = {'ALL':     {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_ALL')},
                                       'NONZERO': {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_NONZERO')},
                                       'ZERO':    {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_ZERO')}}
        conditionTypes_allocatedBalance = {'ALL':     {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_ALL')},
                                           'NONZERO': {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_NONZERO')},
                                           'ZERO':    {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_ZERO')}}
        conditionTypes_currencyAnalysisCode = {'ALL':     {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_ALL')},
                                               'NONZERO': {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_NONZERO')},
                                               'ZERO':    {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FILTER_ZERO')}}
        self.GUIOs["POSITIONS_TRADESTATUSFILTERSELECTIONBOX"].setSelectionList(selectionList = conditionTypes_tradeStatus, displayTargets = 'all')
        self.GUIOs["POSITIONS_TRADESTATUSFILTERSELECTIONBOX"].setSelected(itemKey = 'ALL', callSelectionUpdateFunction = False)
        self.GUIOs["POSITIONS_TRADABLEFILTERSELECTIONBOX"].setSelectionList(selectionList = conditionTypes_tradable, displayTargets = 'all')
        self.GUIOs["POSITIONS_TRADABLEFILTERSELECTIONBOX"].setSelected(itemKey = 'ALL', callSelectionUpdateFunction = False)
        self.GUIOs["POSITIONS_QUANTITYFILTERSELECTIONBOX"].setSelectionList(selectionList = conditionTypes_quantity, displayTargets = 'all')
        self.GUIOs["POSITIONS_QUANTITYFILTERSELECTIONBOX"].setSelected(itemKey = 'ALL', callSelectionUpdateFunction = False)
        self.GUIOs["POSITIONS_ASSUMEDRATIOFILTERSELECTIONBOX"].setSelectionList(selectionList = conditionTypes_assumedRatio, displayTargets = 'all')
        self.GUIOs["POSITIONS_ASSUMEDRATIOFILTERSELECTIONBOX"].setSelected(itemKey = 'ALL', callSelectionUpdateFunction = False)
        self.GUIOs["POSITIONS_ALLOCATEDBALANCEFILTERSELECTIONBOX"].setSelectionList(selectionList = conditionTypes_allocatedBalance, displayTargets = 'all')
        self.GUIOs["POSITIONS_ALLOCATEDBALANCEFILTERSELECTIONBOX"].setSelected(itemKey = 'ALL', callSelectionUpdateFunction = False)
        self.GUIOs["POSITIONS_CURRENCYANALYSISCODEFILTERSELECTIONBOX"].setSelectionList(selectionList = conditionTypes_currencyAnalysisCode, displayTargets = 'all')
        self.GUIOs["POSITIONS_CURRENCYANALYSISCODEFILTERSELECTIONBOX"].setSelected(itemKey = 'ALL', callSelectionUpdateFunction = False)
        #---Display Mode Selector
        self.GUIOs["POSITIONS_DISPLAYMODETITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=12600, yPos=5250, width=1700, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_DISPLAYMODE'), fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_DISPLAYMODESELECTIONBOX"] = selectionBox_typeB(**inst, groupOrder=3, xPos=14400, yPos=5250, width=1500, height=250, style="styleA", nDisplay = 5, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_POSITIONS_DISPLAYMODE'])
        displayModes = {'BASIC':  {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_DISPLAYMODE_BASIC')},
                        'TRADER': {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_DISPLAYMODE_TRADER')},
                        'DETAIL': {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_DISPLAYMODE_DETAIL')}}
        self.GUIOs["POSITIONS_DISPLAYMODESELECTIONBOX"].setSelectionList(selectionList = displayModes, displayTargets = 'all')
        self.GUIOs["POSITIONS_DISPLAYMODESELECTIONBOX"].setSelected(itemKey = 'BASIC', callSelectionUpdateFunction = False)
        #---BASIC Mode
        self.GUIOs["POSITIONS_BASICMODESELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=2, xPos=5100, yPos=800, width=10800, height=3650, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_POSITIONS_POSITION'], 
                                                                           elementWidths = (600, 1200, 500, 600, 650, 750, 700, 1200, 700, 1100, 700, 750, 550, 550)) #10550
        self.GUIOs["POSITIONS_BASICMODESELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_INDEX')},            # 600
                                                                                       {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_SYMBOL')},           #1200
                                                                                       {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_TRADING')},          # 500
                                                                                       {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_LEVERAGE')},         # 600
                                                                                       {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_MARGINMODE')},       # 650
                                                                                       {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_QUANTITY')},         # 750
                                                                                       {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_ENTRYPRICE')},       # 700
                                                                                       {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_CURRENTPRICE')},     #1200
                                                                                       {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_LIQUIDATIONPRICE')}, # 700
                                                                                       {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_UNREALIZEDPNL')},    #1100
                                                                                       {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_ASSUMEDRATIO')},     # 700
                                                                                       {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_ALLOCATEDBALANCE')}, # 750
                                                                                       {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_COMMITMENTRATE')},   # 550
                                                                                       {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_RISKLEVEL')}])       # 550
        self.GUIOs["POSITIONS_FORCECLEARPOSITIONBUTTON"]       = button_typeA(**inst, groupOrder=1, xPos= 5100, yPos=450, width=10200, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_FORCECLEARPOSITION'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_POSITIONS_FORCECLEARPOSITION'])
        self.GUIOs["POSITIONS_FORCECLEARPOSITIONSAFETYSWITCH"] = switch_typeB(**inst, groupOrder=2, xPos=15400, yPos=450, width=  500, height=250, style="styleA", align='horizontal', switchStatus=False, statusUpdateFunction = self.pageObjectFunctions['ONSTATUSUPDATE_POSITIONS_FORCECLEARPOSITIONSAFETYSWTICH'])
        self.GUIOs["POSITIONS_FORCECLEARPOSITIONBUTTON"].deactivate()
        self.GUIOs["POSITIONS_FORCECLEARPOSITIONSAFETYSWITCH"].deactivate()
        #---TRADER MODE
        self.GUIOs["POSITIONS_TRADERMODESELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=2, xPos=5100, yPos=450, width=6000, height=4000, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_POSITIONS_POSITION'], 
                                                                            elementWidths = (700, 1500, 600, 600, 600, 1225, 1225, 700, 700, 900, 15000, 2000)) #5750
        self.GUIOs["POSITIONS_TRADERMODESELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_INDEX')},                  #  700
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_SYMBOL')},                 # 1500
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_TRADABLE')},               #  600
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_TRADING')},                #  600
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_REDUCEONLY')},             #  600
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_CURRENCYANALYSISCODE')},   # 1225
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_TRADECONFIGURATIONCODE')}, # 1225
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_PRIORITY')},               #  700
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_ASSUMEDRATIO')},           #  700
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_MAXALLOCATEDBALANCE')},    #  900
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_TRADECONTROL')},           # 10000
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_ABRUPTCLEARINGRECORDS')}]) # 2000
        self.GUIOs["POSITIONS_TRADERMODECACODETITLETEXT"]    = textBox_typeA(**inst,  groupOrder=1, xPos=11200, yPos=4250, width=2300, height=200, style=None, text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_CURRENCYANALYSISCODE'),   anchor='W', fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_TRADERMODETCCODETITLETEXT"]    = textBox_typeA(**inst,  groupOrder=1, xPos=13600, yPos=4250, width=2300, height=200, style=None, text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_TRADECONFIGURATIONCODE'), anchor='W', fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_TRADERMODECACODESELECTIONBOX"] = selectionBox_typeA(**inst, groupOrder=1, xPos=11200, yPos=2900, width=2300, height=1350, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, showIndex = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_POSITIONS_NEWCURRENCYANALYSISCODE'])
        self.GUIOs["POSITIONS_TRADERMODETCCODESELECTIONBOX"] = selectionBox_typeA(**inst, groupOrder=1, xPos=13600, yPos=2900, width=2300, height=1350, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, showIndex = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_POSITIONS_NEWTRADECONFIGURATIONCODE'])
        self.GUIOs["POSITIONS_TRADERMODESELECTIONBOX"].hide()
        self.GUIOs["POSITIONS_TRADERMODECACODETITLETEXT"].hide()
        self.GUIOs["POSITIONS_TRADERMODETCCODETITLETEXT"].hide()
        self.GUIOs["POSITIONS_TRADERMODETCCODESELECTIONBOX"].hide()
        self.GUIOs["POSITIONS_TRADERMODECACODESELECTIONBOX"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODETITLETEXT"]                 = textBox_typeA(**inst,      groupOrder=1, xPos=11200, yPos=2550, width=1800, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_CURRENCYANALYSISCODE'),   anchor='CENTER', fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTOLD"]              = textBox_typeA(**inst,      groupOrder=1, xPos=13100, yPos=2550, width=1350, height=250, style="styleA", text="-",                                                                         anchor='CENTER', fontSize=80, textInteractable=True)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTNEW"]              = textBox_typeA(**inst,      groupOrder=1, xPos=14550, yPos=2550, width=1350, height=250, style="styleA", text="-",                                                                         anchor='CENTER', fontSize=80, textInteractable=True)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODETITLETEXT"]                 = textBox_typeA(**inst,      groupOrder=1, xPos=11200, yPos=2200, width=1800, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_TRADECONFIGURATIONCODE'), anchor='CENTER', fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTOLD"]              = textBox_typeA(**inst,      groupOrder=1, xPos=13100, yPos=2200, width=1350, height=250, style="styleA", text="-",                                                                         anchor='CENTER', fontSize=80, textInteractable=True)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTNEW"]              = textBox_typeA(**inst,      groupOrder=1, xPos=14550, yPos=2200, width=1350, height=250, style="styleA", text="-",                                                                         anchor='CENTER', fontSize=80, textInteractable=True)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYTITLETEXT"]               = textBox_typeA(**inst,      groupOrder=1, xPos=11200, yPos=1850, width=1800, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_PRIORITY'),               anchor='CENTER', fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTOLD"]            = textBox_typeA(**inst,      groupOrder=1, xPos=13100, yPos=1850, width=1350, height=250, style="styleA", text="-",                                                                         anchor='CENTER', fontSize=80, textInteractable=True)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTNEW"]            = textInputBox_typeA(**inst, groupOrder=1, xPos=14550, yPos=1850, width=1350, height=250, style="styleA",text="", fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_POSITIONS_NEWPRIORITY'])
        self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOTITLETEXT"]           = textBox_typeA(**inst,      groupOrder=1, xPos=11200, yPos=1500, width=1800, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ASSUMEDRATIO'),           anchor='CENTER', fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTOLD"]        = textBox_typeA(**inst,      groupOrder=1, xPos=13100, yPos=1500, width=1350, height=250, style="styleA", text="-",                                                                         anchor='CENTER', fontSize=80, textInteractable=True)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTNEW"]        = textInputBox_typeA(**inst, groupOrder=1, xPos=14550, yPos=1500, width= 750, height=250, style="styleA", text="", fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_POSITIONS_NEWASSUMEDRATIO'])
        self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOUNITTEXT"]            = textBox_typeA(**inst,      groupOrder=1, xPos=15400, yPos=1500, width= 500, height=250, style="styleA", text="%",                                                                         anchor='CENTER', fontSize=80, textInteractable=True)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCETITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=11200, yPos=1150, width=1800, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_MAXALLOCATEDBALANCE'),    anchor='CENTER', fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTOLD"] = textBox_typeA(**inst,      groupOrder=1, xPos=13100, yPos=1150, width=1350, height=250, style="styleA", text="-",                                                                         anchor='CENTER', fontSize=80, textInteractable=True)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTNEW"] = textInputBox_typeA(**inst, groupOrder=1, xPos=14550, yPos=1150, width= 750, height=250, style="styleA", text="", fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_POSITIONS_NEWMAXALLOCATEDBALANCE'])
        self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEUNITTEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos=15400, yPos=1150, width= 500, height=250, style="styleA", text="%",                                                                         anchor='CENTER', fontSize=80, textInteractable=True)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSTITLETEXT"]            = textBox_typeA(**inst,      groupOrder=1, xPos=11200, yPos= 800, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_TRADESTATUS'),            anchor='CENTER', fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSVALUETEXT"]            = textBox_typeA(**inst,      groupOrder=1, xPos=12300, yPos= 800, width= 600, height=250, style="styleA", text="-",                                                                         anchor='CENTER', fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSSWITCH"]               = switch_typeB(**inst,       groupOrder=2, xPos=13000, yPos= 800, width= 500, height=250, style="styleA", align='horizontal', switchStatus=False, statusUpdateFunction = self.pageObjectFunctions['ONSTATUSUPDATE_POSITIONS_NEWTRADESTATUSSWITCH'])
        self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYTITLETEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos=13600, yPos= 800, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_REDUCEONLY'),             anchor='CENTER', fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYVALUETEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos=14700, yPos= 800, width= 600, height=250, style="styleA", text="-",                                                                         anchor='CENTER', fontSize=80, textInteractable=False)
        self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYSWITCH"]                = switch_typeB(**inst,       groupOrder=2, xPos=15400, yPos= 800, width= 500, height=250, style="styleA", align='horizontal', switchStatus=False, statusUpdateFunction = self.pageObjectFunctions['ONSTATUSUPDATE_POSITIONS_NEWREDUCEONLYSWITCH'])
        self.GUIOs["POSITIONS_TRADERMODEAPPLYBUTTON"]                             = button_typeA(**inst,       groupOrder=1, xPos=11200, yPos= 450, width=2300, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_APPLY'),                    fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_POSITIONS_APPLYNEWPARAMS'])
        self.GUIOs["POSITIONS_TRADERMODERESETTRACECONTROLTRACKERBUTTON"]          = button_typeA(**inst,       groupOrder=1, xPos=13600, yPos= 450, width=2300, height=250, style="styleA", text=self.visualManager.getTextPack('ACCOUNTS:POSITIONS_RESETTRADECONTROLTRACKER'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_POSITIONS_RESETTRADECONTROLTRACKER'])
        self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODETITLETEXT"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTOLD"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTNEW"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODETITLETEXT"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTOLD"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTNEW"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYTITLETEXT"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTOLD"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTNEW"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOTITLETEXT"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTOLD"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTNEW"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOUNITTEXT"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCETITLETEXT"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTOLD"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTNEW"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEUNITTEXT"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSTITLETEXT"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSVALUETEXT"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSSWITCH"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYTITLETEXT"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYVALUETEXT"].hide()
        self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYSWITCH"].hide()
        self.GUIOs["POSITIONS_TRADERMODEAPPLYBUTTON"].hide()
        self.GUIOs["POSITIONS_TRADERMODERESETTRACECONTROLTRACKERBUTTON"].hide()
        #---DETAIL MODE
        self.GUIOs["POSITIONS_DETAILMODESELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=2, xPos=5100, yPos=450, width=10800, height=4000, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_POSITIONS_POSITION'], 
                                                                            elementWidths = (600, 1200, 550, 550, 550, 700, 700, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1000, 1500, 1500, 1000, 15000, 3000)) #10550
        self.GUIOs["POSITIONS_DETAILMODESELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_INDEX')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_SYMBOL')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_TRADABLE')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_TRADING')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_REDUCEONLY')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_LEVERAGE')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_MARGINMODE')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_QUANTITY')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_ISOLATEDWALLETBALANCE')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_POSITIONINITIALMARGIN')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_OPENORDERINITIALMARGIN')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_MAINTENANCEMARGIN')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_ENTRYPRICE')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_CURRENTPRICE')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_LIQUIDATIONPRICE')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_UNREALIZEDPNL')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_ASSUMEDRATIO')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_WEIGHTEDASSUMEDRATIO')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_ALLOCATEDBALANCE')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_MAXALLOCATEDBALANCE')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_COMMITMENTRATE')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_RISKLEVEL')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_CURRENCYANALYSISCODE')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_TRADECONFIGURATIONCODE')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_PRIORITY')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_TRADECONTROL')},
                                                                                        {'text': self.visualManager.getTextPack('ACCOUNTS:POSITIONS_ST_ABRUPTCLEARINGRECORDS')}])
        self.GUIOs["POSITIONS_DETAILMODESELECTIONBOX"].hide()
        #Trade Manager Message
        self.GUIOs["TRADEMANAGERMESSAGE_MESSAGEDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=100, yPos=100, width=15800, height=250, style="styleA", text="-", fontSize=80, textInteractable=False)

    elif (self.displaySpaceDefiner['ratio'] == '21:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 21000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
    elif (self.displaySpaceDefiner['ratio'] == '32:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 32000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
#SETUP PAGE <MAIN> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <LOAD> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageLoadFunction(self):
    #FAR Registration
    #---TRADEMANAGER
    self.ipcA.addFARHandler('onCurrenciesUpdate',         self.pageAuxillaryFunctions['_FAR_ONCURRENCIESUPDATE'],         executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
    self.ipcA.addFARHandler('onAccountUpdate',            self.pageAuxillaryFunctions['_FAR_ONACCOUNTUPDATE'],            executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
    self.ipcA.addFARHandler('onCurrencyAnalysisUpdate',   self.pageAuxillaryFunctions['_FAR_ONCURRENCYANALYSISUPDATE'],   executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
    self.ipcA.addFARHandler('onTradeConfigurationUpdate', self.pageAuxillaryFunctions['_FAR_ONTRADECONFIGURATIONUPDATE'], executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
    
    #Get data via PRD
    self.puVar['currencies']          = self.ipcA.getPRD(processName = 'DATAMANAGER',  prdAddress = 'CURRENCIES')
    self.puVar['accounts']            = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = 'ACCOUNTS')
    self.puVar['currencyAnalysis']    = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = 'CURRENCYANALYSIS')
    self.puVar['tradeConfigurations'] = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = 'TRADECONFIGURATIONS')

    self.pageAuxillaryFunctions['SETACCOUNTSLIST']()
    self.pageAuxillaryFunctions['ONACCOUNTSELECTIONUPDATE']()
    self.pageAuxillaryFunctions['DISPLAYASSETDATA']()
    _displayMode = self.GUIOs["POSITIONS_DISPLAYMODESELECTIONBOX"].getSelected()
    if (_displayMode == 'TRADER'): self.pageAuxillaryFunctions['SETTRADECONFIGURATIONSLIST']()
    self.pageAuxillaryFunctions['SETPOSITIONSLIST']()
#SETUP PAGE <LOAD> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <ESCAPE> --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageEscapeFunction(self):
    for fID in ('onAccountUpdate',
                'onCurrencyAnalysisUpdate',
                'onTradeConfigurationUpdate',
                'onKlineStreamReceival',):
        self.ipcA.removeFARHandler(functionID   = fID)
        self.ipcA.addDummyFARHandler(functionID = fID)
#SETUP PAGE <ESCAPE> END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <PROCESS> -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageProcessFunction(self, t_elapsed_ns, onLoad = False):
    #Periodic Positions List Sorting
    _currentSortMode = self.GUIOs["POSITIONS_SORTBYSELECTIONBOX"].getSelected()
    if (_currentSortMode in _PERIODICPOSITIONSSORTING_ACTIVATIONSORTTYPES) and (self.puVar['accounts_selected'] != None):
        _t_current_ns = time.perf_counter_ns()
        if (_PERIODICPOSITIONSSORTING_INTERVAL_NS < _t_current_ns-self.puVar['periodicPositionsSorting_lastSorted_ns']):
            self.pageAuxillaryFunctions['APPLYPOSITIONSLISTFILTER'](resetViewPosition = False)
            self.puVar['periodicPositionsSorting_lastSorted_ns'] = _t_current_ns
#SETUP PAGE <PROCESS> END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#OBJECT FUNCTIONS -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateObjectFunctions(self):
    objFunctions = dict()

    #<Page Navigation>
    def __pageMove_DASHBOARD(objInstance, **kwargs): 
        self.sysFunctions['LOADPAGE']('DASHBOARD')
    objFunctions['PAGEMOVE_DASHBOARD'] = __pageMove_DASHBOARD

    #<List>
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

    #<Accounts Information & Control>
    def __onTextUpdate_AccountsInformationAndControl_LocalID(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANADDACCOUNT']()
    def __onTextUpdate_AccountsInformationAndControl_BUID(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANADDACCOUNT']()
    def __onSelectionUpdate_AccountsInformationAndControl_AccountType(objInstance, **kwargs):
        _selectedAccountType = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPESELECTIONBOX"].getSelected()
        if   (_selectedAccountType == 'VIRTUAL'): self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDTEXTINPUTBOX"].updateText(text = ""); self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDTEXTINPUTBOX"].deactivate()
        elif (_selectedAccountType == 'ACTUAL'):  self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDTEXTINPUTBOX"].updateText(text = ""); self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDTEXTINPUTBOX"].activate()
        self.pageAuxillaryFunctions['CHECKIFCANADDACCOUNT']()
    def __onStausUpdate_AccountsInformationAndControl_TradeStatusSwitch(objInstance, **kwargs):
        localID   = self.puVar['accounts_selected']
        newStatus = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSSWITCH"].getStatus()
        if (localID in self.puVar['accounts_passwords']): password = self.puVar['accounts_passwords'][localID]
        else:                                             password = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', 
                          functionID = 'setAccountTradeStatus', 
                          functionParams = {'localID':   localID,
                                            'newStatus': newStatus,
                                            'password':  password},
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONACCOUNTCONTROLREQUESTRESPONSE'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSSWITCH"].deactivate()
    def __onTextUpdate_AccountsInformationAndControl_APIKey(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANACTIVATEACCOUNT']()
    def __onTextUpdate_AccountsInformationAndControl_SecretKey(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANACTIVATEACCOUNT']()
    def __onTextUpdate_AccountsInformationAndControl_Password(objInstance, **kwargs):
        if (self.puVar['accounts_selected'] != None):
            _password_entered = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
            if (8 <= len(_password_entered)): self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDHOLDRELEASESWITCH"].activate()
            else:                             self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDHOLDRELEASESWITCH"].deactivate()
        self.pageAuxillaryFunctions['CHECKIFCANADDACCOUNT']()
    def __onStatusUpdate_AccountsInformationAndControl_PasswordHoldRelease(objInstance, **kwargs):
        switchStatus = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDHOLDRELEASESWITCH"].getStatus()
        localID = self.puVar['accounts_selected']
        if (switchStatus == True): 
            self.puVar['accounts_passwords'][localID] = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
            self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].deactivate()
        else:                      
            del self.puVar['accounts_passwords'][localID]
            self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].activate()
            self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDHOLDRELEASESWITCH"].deactivate()
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].updateText(text = "")
    def __onButtonRelease_AccountsInformationAndControl_ActivateByEnteredKeys(objInstance, **kwargs):
        localID           = self.puVar['accounts_selected']
        enteredKey_api    = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"].getText()
        enteredKey_secret = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"].getText()
        if (localID in self.puVar['accounts_passwords']): password = self.puVar['accounts_passwords'][localID]
        else:                                             password = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', 
                          functionID = 'activateAccount', 
                          functionParams = {'localID':   localID, 
                                            'apiKey':    enteredKey_api,
                                            'secretKey': enteredKey_secret,
                                            'encrypted': False,
                                            'password':  password}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONACCOUNTCONTROLREQUESTRESPONSE'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYENTEREDKEYSBUTTON"].deactivate()
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAFBUTTON"].deactivate()
    def __onButtonRelease_AccountsInformationAndControl_Deactivate(objInstance, **kwargs):
        localID = self.puVar['accounts_selected']
        if (localID in self.puVar['accounts_passwords']): password = self.puVar['accounts_passwords'][localID]
        else:                                             password = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', 
                          functionID = 'deactivateAccount', 
                          functionParams = {'localID':  localID,
                                            'password': password}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONACCOUNTCONTROLREQUESTRESPONSE'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYENTEREDKEYSBUTTON"].deactivate()
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAFBUTTON"].deactivate()
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_DEACTIVATEBUTTON"].deactivate()
    def __onButtonRelease_AccountsInformationAndControl_ActivateByAAF(objInstance, **kwargs):
        localID = self.puVar['accounts_selected']
        if (localID in self.puVar['accounts_passwords']): password = self.puVar['accounts_passwords'][localID]
        else:                                             password = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
        #[1]: Deactivate buttons
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYENTEREDKEYSBUTTON"].deactivate()
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAFBUTTON"].deactivate()
        #[2]: Search for files with 'aaf' extension under the root directory of all drives or the 'data' folder in the project directory and find AAF within them.
        aafs      = dict()
        rootPaths = [f"{dLetter}:/" for dLetter in string.ascii_uppercase]+[os.path.join(self.path_project, 'data'),]
        for rootPath in rootPaths:
            #Drive Existence Check
            if not os.path.exists(rootPath): 
                continue
            #AAFs Read
            try:    paths = os.listdir(rootPath)
            except: continue
            for path in paths:
                #Extension Check
                if not(path.lower().endswith('.aaf')): 
                    continue
                #File Read
                try:
                    with open(os.path.join(rootPath, path), 'r') as f: 
                        (aaf_localID, 
                         aaf_genTime_ns, 
                         aaf_apiKey_encrypted, 
                         aaf_secretKey_encrypted) = json.loads(f.read())
                except: continue
                #AAF Record
                if (aaf_localID in aafs) and (aaf_genTime_ns < aafs[aaf_localID]['genTime_ns']): continue
                aafs[aaf_localID] = {'genTime_ns':          aaf_genTime_ns,
                                     'apiKey_encrypted':    aaf_apiKey_encrypted,
                                     'secretKey_encrypted': aaf_secretKey_encrypted}
        #[3]: If no data is found
        if localID not in aafs:
            self.pageAuxillaryFunctions['CHECKIFCANACTIVATEACCOUNT']()
            self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAFBUTTON"].activate()
            self.GUIOs["TRADEMANAGERMESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = "[LOCAL] No Activation File Is Found For This Account", textStyle = 'RED_LIGHT')
            return
        aaf = aafs[localID]
        #[4]: Send account activation request
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', 
                          functionID = 'activateAccount', 
                          functionParams = {'localID':   localID, 
                                            'apiKey':    aaf['apiKey_encrypted'],
                                            'secretKey': aaf['secretKey_encrypted'],
                                            'encrypted': True,
                                            'password':  password}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONACCOUNTCONTROLREQUESTRESPONSE'])
    def __onButtonRelease_AccountsInformationAndControl_GenerateAAF(objInstance, **kwargs):
        localID = self.puVar['accounts_selected']
        if (localID in self.puVar['accounts_passwords']): password = self.puVar['accounts_passwords'][localID]
        else:                                             password = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
        #[1]: Deactivate buttons
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYENTEREDKEYSBUTTON"].deactivate()
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAFBUTTON"].deactivate()
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_GENERATEAAFBUTTON"].deactivate()
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].deactivate()
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"].deactivate()
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"].deactivate()
        #[2]: Send password verification request
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER',
                          functionID = 'verifyPassword',
                          functionParams = {'localID':   localID, 
                                            'password':  password}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONACCOUNTCONTROLREQUESTRESPONSE'])
    def __onButtonRelease_AccountsInformationAndControl_AddAccount(objInstance, **kwargs):
        localID     = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_LOCALIDTEXTINPUTBOX"].getText()
        accountType = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPESELECTIONBOX"].getSelected()
        if   (accountType == 'VIRTUAL'): binanceUID = None
        elif (accountType == 'ACTUAL'):  binanceUID = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDTEXTINPUTBOX"].getText()
        password = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER',
                          functionID = 'addAccount',
                          functionParams = {'localID':     localID, 
                                            'buid':        binanceUID,
                                            'accountType': accountType,
                                            'password':    password}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONACCOUNTCONTROLREQUESTRESPONSE'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ADDACCOUNTBUTTON"].deactivate()
    def __onButtonRelease_AccountsInformationAndControl_RemoveAccount(objInstance, **kwargs):
        localID  = self.puVar['accounts_selected']
        if (localID in self.puVar['accounts_passwords']): password = self.puVar['accounts_passwords'][localID]
        else:                                             password = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'removeAccount', functionParams = {'localID': localID, 'password': password}, farrHandler = self.pageAuxillaryFunctions['_FARR_ONACCOUNTCONTROLREQUESTRESPONSE'])
        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNTBUTTON"].deactivate()
    def __onStatusUpdate_AccountsInformationAndControl_RemoveAccountSwitch(objInstance, **kwargs):
        _switchStatus = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNTBUTTONSWITCH"].getStatus()
        if   (_switchStatus == True): self.GUIOs["ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNTBUTTON"].activate()
        else:                         self.GUIOs["ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNTBUTTON"].deactivate()
    objFunctions['ONTEXTUPDATE_ACCOUNTSINFORMATION&CONTROL_LOCALID']                  = __onTextUpdate_AccountsInformationAndControl_LocalID
    objFunctions['ONTEXTUPDATE_ACCOUNTSINFORMATION&CONTROL_BUID']                     = __onTextUpdate_AccountsInformationAndControl_BUID
    objFunctions['ONSELECTIONUPDATE_ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPE']         = __onSelectionUpdate_AccountsInformationAndControl_AccountType
    objFunctions['ONSTATUSUPDATE_ACCOUNTSINFORMATION&CONTROL_TRADESTATUSSWITCH']      = __onStausUpdate_AccountsInformationAndControl_TradeStatusSwitch
    objFunctions['ONTEXTUPDATE_ACCOUNTSINFORMATION&CONTROL_APIKEY']                   = __onTextUpdate_AccountsInformationAndControl_APIKey
    objFunctions['ONTEXTUPDATE_ACCOUNTSINFORMATION&CONTROL_SECRETKEY']                = __onTextUpdate_AccountsInformationAndControl_SecretKey
    objFunctions['ONTEXTUPDATE_ACCOUNTSINFORMATION&CONTROL_PASSWORD']                 = __onTextUpdate_AccountsInformationAndControl_Password
    objFunctions['ONSTATUSUPDATE_ACCOUNTSINFORMATION&CONTROL_PASSWORDHOLDRELEASE']    = __onStatusUpdate_AccountsInformationAndControl_PasswordHoldRelease
    objFunctions['ONBUTTONRELEASE_ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYENTEREDKEYS'] = __onButtonRelease_AccountsInformationAndControl_ActivateByEnteredKeys
    objFunctions['ONBUTTONRELEASE_ACCOUNTSINFORMATION&CONTROL_DEACTIVATE']            = __onButtonRelease_AccountsInformationAndControl_Deactivate
    objFunctions['ONBUTTONRELEASE_ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAF']         = __onButtonRelease_AccountsInformationAndControl_ActivateByAAF
    objFunctions['ONBUTTONRELEASE_ACCOUNTSINFORMATION&CONTROL_GENERATEAAF']           = __onButtonRelease_AccountsInformationAndControl_GenerateAAF
    objFunctions['ONBUTTONRELEASE_ACCOUNTSINFORMATION&CONTROL_ADDACCOUNT']            = __onButtonRelease_AccountsInformationAndControl_AddAccount
    objFunctions['ONBUTTONRELEASE_ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNT']         = __onButtonRelease_AccountsInformationAndControl_RemoveAccount
    objFunctions['ONSTATUSUPDATE_ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNTSWITCH']    = __onStatusUpdate_AccountsInformationAndControl_RemoveAccountSwitch

    #<Assets>
    def __onSelectionUpdate_Assets_AssetToDisplay(objInstance, **kwargs):
        _assetToDisplay = self.GUIOs["ASSETS_ASSETTODISPLAYSELECTIONBOX"].getSelected()
        if (_assetToDisplay == 'USDT'):
            self.GUIOs["ASSETS_TITLETEXT"].updateText(text = "USDT")
            self.GUIOs["ASSETS_IMAGEBOX"].updateImage(image = "usdtIcon_512x512.png")
        elif (_assetToDisplay == 'USDC'):
            self.GUIOs["ASSETS_TITLETEXT"].updateText(text = "USDC")
            self.GUIOs["ASSETS_IMAGEBOX"].updateImage(image = "usdcIcon_512x512.png")
        self.GUIOs["ASSETS_TRASNFERBALANCESAFETYSWITCH"].setStatus(status = False, callStatusUpdateFunction = True)
        self.pageAuxillaryFunctions['DISPLAYASSETDATA']()
    def __onTextUpdate_Assets_TransferBalance(objInstance, **kwargs):
        try:    balanceToTransfer = float(self.GUIOs["ASSETS_TRASNFERBALANCETEXTINPUTBOX"].getText())
        except: balanceToTransfer = None
        if ((balanceToTransfer != None) and (0 < balanceToTransfer)): 
            self.GUIOs["ASSETS_TRASNFERBALANCEDEPOSITBUTTON"].activate()
            self.GUIOs["ASSETS_TRASNFERBALANCEWITHDRAWBUTTON"].activate()
        else:
            self.GUIOs["ASSETS_TRASNFERBALANCEDEPOSITBUTTON"].deactivate()
            self.GUIOs["ASSETS_TRASNFERBALANCEWITHDRAWBUTTON"].deactivate()
    def __onButtonRelease_Assets_DepositBalance(objInstance, **kwargs):
        amountToTransfer = float(self.GUIOs["ASSETS_TRASNFERBALANCETEXTINPUTBOX"].getText())
        self.pageAuxillaryFunctions['SENDBALANCETRANSFERREQUEST'](amountToTransfer)
    def __onButtonRelease_Assets_WithdrawBalance(objInstance, **kwargs):
        amountToTransfer = -float(self.GUIOs["ASSETS_TRASNFERBALANCETEXTINPUTBOX"].getText())
        self.pageAuxillaryFunctions['SENDBALANCETRANSFERREQUEST'](amountToTransfer)
    def __onStatusUpdate_Assets_BalanceTransferSwitch(objInstance, **kwargs):
        _switchStatus = self.GUIOs["ASSETS_TRASNFERBALANCESAFETYSWITCH"].getStatus()
        if (_switchStatus == True): self.GUIOs["ASSETS_TRASNFERBALANCETEXTINPUTBOX"].activate()
        else:                       self.GUIOs["ASSETS_TRASNFERBALANCETEXTINPUTBOX"].deactivate(); self.GUIOs["ASSETS_TRASNFERBALANCETEXTINPUTBOX"].updateText("")
        self.GUIOs["ASSETS_TRASNFERBALANCEDEPOSITBUTTON"].deactivate()
        self.GUIOs["ASSETS_TRASNFERBALANCEWITHDRAWBUTTON"].deactivate()
    def __onValueUpdate_Assets_AllocationRatioSlider(objInstance, **kwargs):
        _sliderVal = self.GUIOs["ASSETS_ALLOCATIONRATIOSLIDER"].getSliderValue()
        self.GUIOs["ASSETS_ALLOCATIONRATIODISPLAYTEXT"].updateText("{:.1f} %".format(_sliderVal))
        _allocRatio_asset  = self.puVar['accounts'][self.puVar['accounts_selected']]['assets'][self.GUIOs["ASSETS_ASSETTODISPLAYSELECTIONBOX"].getSelected()]['allocationRatio']
        _allocRatio_slider = round(_sliderVal/100, 3)
        if (_allocRatio_asset == _allocRatio_slider): self.GUIOs["ASSETS_ALLOCATIONRATIOAPPLYBUTTON"].deactivate()
        else:                                         self.GUIOs["ASSETS_ALLOCATIONRATIOAPPLYBUTTON"].activate()
    def __onButtonRelease_Assets_ApplyNewAllocationRatio(objInstance, **kwargs):
        #Allocation Ratio
        _sliderVal = self.GUIOs["ASSETS_ALLOCATIONRATIOSLIDER"].getSliderValue()
        newAllocationRatio = round(_sliderVal/100, 3)
        #Password
        localID = self.puVar['accounts_selected']
        if (localID in self.puVar['accounts_passwords']): password = self.puVar['accounts_passwords'][localID]
        else:                                             password = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
        #Asset
        asset = self.GUIOs["ASSETS_ASSETTODISPLAYSELECTIONBOX"].getSelected()
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', 
                          functionID = 'updateAllocationRatio',
                          functionParams = {'localID':            localID,
                                            'password':           password,
                                            'asset':              asset,
                                            'newAllocationRatio': newAllocationRatio}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONACCOUNTCONTROLREQUESTRESPONSE'])
        #Buttons Temporary Deactivation
        self.GUIOs["ASSETS_ALLOCATIONRATIOAPPLYBUTTON"].deactivate()
    objFunctions['ONSELECTIONUPDATE_ASSETS_ASSETTODISPLAY']        = __onSelectionUpdate_Assets_AssetToDisplay
    objFunctions['ONTEXTUPDATE_ASSETS_TRANSFERBALANCE']            = __onTextUpdate_Assets_TransferBalance
    objFunctions['ONBUTTONRELEASE_ASSETS_DEPOSITBALANCE']          = __onButtonRelease_Assets_DepositBalance
    objFunctions['ONBUTTONRELEASE_ASSETS_WITHDRAWBALANCE']         = __onButtonRelease_Assets_WithdrawBalance
    objFunctions['ONSTATUSUPDATE_ASSETS_BALANCETRANSFERSWITCH']    = __onStatusUpdate_Assets_BalanceTransferSwitch
    objFunctions['ONVALUEUPDATE_ASSETS_ALLOCATIONRATIOSLIDER']     = __onValueUpdate_Assets_AllocationRatioSlider
    objFunctions['ONBUTTONRELEASE_ASSETS_APPLYNEWALLOCATIONRATIO'] = __onButtonRelease_Assets_ApplyNewAllocationRatio

    #<Positions>
    def __onSelectionUpdate_Positions_DisplayMode(objInstance, **kwargs):
        _displayMode = self.GUIOs["POSITIONS_DISPLAYMODESELECTIONBOX"].getSelected()
        #Objects Display
        if   (_displayMode == 'BASIC'):
            #BASIC
            self.GUIOs["POSITIONS_BASICMODESELECTIONBOX"].show()
            self.GUIOs["POSITIONS_FORCECLEARPOSITIONBUTTON"].show()
            self.GUIOs["POSITIONS_FORCECLEARPOSITIONSAFETYSWITCH"].show()
            #TRADER
            self.GUIOs["POSITIONS_TRADERMODESELECTIONBOX"].hide()
            self.GUIOs["POSITIONS_TRADERMODECACODETITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODETCCODETITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODETCCODESELECTIONBOX"].hide()
            self.GUIOs["POSITIONS_TRADERMODECACODESELECTIONBOX"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODETITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTOLD"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTNEW"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODETITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTOLD"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTNEW"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYTITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTOLD"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTNEW"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOTITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTOLD"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTNEW"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOUNITTEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCETITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTOLD"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTNEW"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEUNITTEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSTITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSVALUETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSSWITCH"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYTITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYVALUETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYSWITCH"].hide()
            self.GUIOs["POSITIONS_TRADERMODEAPPLYBUTTON"].hide()
            self.GUIOs["POSITIONS_TRADERMODERESETTRACECONTROLTRACKERBUTTON"].hide()
            #DETAIL
            self.GUIOs["POSITIONS_DETAILMODESELECTIONBOX"].hide()
        elif (_displayMode == 'TRADER'): 
            #BASIC
            self.GUIOs["POSITIONS_BASICMODESELECTIONBOX"].hide()
            self.GUIOs["POSITIONS_FORCECLEARPOSITIONBUTTON"].hide()
            self.GUIOs["POSITIONS_FORCECLEARPOSITIONSAFETYSWITCH"].hide()
            #TRADER
            self.GUIOs["POSITIONS_TRADERMODESELECTIONBOX"].show()
            self.GUIOs["POSITIONS_TRADERMODECACODETITLETEXT"].show()
            self.GUIOs["POSITIONS_TRADERMODETCCODETITLETEXT"].show()
            self.GUIOs["POSITIONS_TRADERMODETCCODESELECTIONBOX"].show()
            self.GUIOs["POSITIONS_TRADERMODECACODESELECTIONBOX"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODETITLETEXT"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTOLD"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTNEW"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODETITLETEXT"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTOLD"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTNEW"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYTITLETEXT"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTOLD"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTNEW"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOTITLETEXT"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTOLD"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTNEW"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOUNITTEXT"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCETITLETEXT"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTOLD"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTNEW"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEUNITTEXT"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSTITLETEXT"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSVALUETEXT"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSSWITCH"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYTITLETEXT"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYVALUETEXT"].show()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYSWITCH"].show()
            self.GUIOs["POSITIONS_TRADERMODEAPPLYBUTTON"].show()
            self.GUIOs["POSITIONS_TRADERMODERESETTRACECONTROLTRACKERBUTTON"].show()
            self.pageAuxillaryFunctions['SETTRADECONFIGURATIONSLIST']()
            #DETAIL
            self.GUIOs["POSITIONS_DETAILMODESELECTIONBOX"].hide()
        elif (_displayMode == 'DETAIL'): 
            #BASIC
            self.GUIOs["POSITIONS_BASICMODESELECTIONBOX"].hide()
            self.GUIOs["POSITIONS_FORCECLEARPOSITIONBUTTON"].hide()
            self.GUIOs["POSITIONS_FORCECLEARPOSITIONSAFETYSWITCH"].hide()
            #TRADER
            self.GUIOs["POSITIONS_TRADERMODESELECTIONBOX"].hide()
            self.GUIOs["POSITIONS_TRADERMODECACODETITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODETCCODETITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODETCCODESELECTIONBOX"].hide()
            self.GUIOs["POSITIONS_TRADERMODECACODESELECTIONBOX"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODETITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTOLD"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTNEW"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODETITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTOLD"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTNEW"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYTITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTOLD"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTNEW"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOTITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTOLD"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTNEW"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOUNITTEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCETITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTOLD"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTNEW"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEUNITTEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSTITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSVALUETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSSWITCH"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYTITLETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYVALUETEXT"].hide()
            self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYSWITCH"].hide()
            self.GUIOs["POSITIONS_TRADERMODEAPPLYBUTTON"].hide()
            self.GUIOs["POSITIONS_TRADERMODERESETTRACECONTROLTRACKERBUTTON"].hide()
            #DETAIL
            self.GUIOs["POSITIONS_DETAILMODESELECTIONBOX"].show()
        #List Update
        self.pageAuxillaryFunctions['SETPOSITIONSLIST']()
        #Position Selection Transfer
        if   (_displayMode == 'BASIC'):  _positionSelectionBox = self.GUIOs["POSITIONS_BASICMODESELECTIONBOX"]
        elif (_displayMode == 'TRADER'): _positionSelectionBox = self.GUIOs["POSITIONS_TRADERMODESELECTIONBOX"]
        elif (_displayMode == 'DETAIL'): _positionSelectionBox = self.GUIOs["POSITIONS_DETAILMODESELECTIONBOX"]
        _positionsSelected = _positionSelectionBox.getSelected()
        if (0 < len(_positionsSelected)): _positionSelected = _positionsSelected[0]
        else:                             _positionSelected = None
        if (_positionSelected != self.puVar['positions_selected']):
            _positionSelectionBox.clearSelected(callSelectionUpdateFunction = False)
            if (self.puVar['positions_selected'] is not None): _positionSelectionBox.addSelected(itemKey = self.puVar['positions_selected'], callSelectionUpdateFunction = False)
        self.pageAuxillaryFunctions['ONPOSITIONSELECTIONUPDATE']()
    def __onObjectUpdate_Positions_Filter(objInstance, **kwargs):
        self.pageAuxillaryFunctions['APPLYPOSITIONSLISTFILTER']()
    def __onSelectionUpdate_Positions_Position(objInstance, **kwargs):
        try:    _positionSymbol_selected = objInstance.getSelected()[0]
        except: _positionSymbol_selected = None
        self.puVar['positions_selected'] = _positionSymbol_selected
        self.puVar['currencyAnalysis_forSelectedPosition'] = set([_caCode for _caCode in self.puVar['currencyAnalysis'] if (self.puVar['currencyAnalysis'][_caCode]['currencySymbol'] == _positionSymbol_selected)])
        self.pageAuxillaryFunctions['ONPOSITIONSELECTIONUPDATE']()
    def __onStatusUpdate_Positions_ForceClearPositionSafetySwitch(objInstance, **kwargs):
        _switchStatus = self.GUIOs["POSITIONS_FORCECLEARPOSITIONSAFETYSWITCH"].getStatus()
        if (_switchStatus == True): self.GUIOs["POSITIONS_FORCECLEARPOSITIONBUTTON"].activate()
        else:                       self.GUIOs["POSITIONS_FORCECLEARPOSITIONBUTTON"].deactivate()
    def __onButtonRelease_Positions_ForceClearPosition(objInstance, **kwargs):
        #Password
        localID = self.puVar['accounts_selected']
        if (localID in self.puVar['accounts_passwords']): password = self.puVar['accounts_passwords'][localID]
        else:                                             password = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
        #Asset
        positionSymbol = self.puVar['positions_selected']
        #Request Dispatch
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', 
                          functionID = 'forceClearPosition', 
                          functionParams = {'localID':        localID,
                                            'password':       password,
                                            'positionSymbol': positionSymbol}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONACCOUNTCONTROLREQUESTRESPONSE'])
        #Buttons Temporary Deactivation
        self.GUIOs["POSITIONS_FORCECLEARPOSITIONBUTTON"].deactivate()
    def __onSelectionUpdate_Positions_NewCurrencyAnalysisCode(objInstance, **kwargs):
        try:    _caCode_selected = self.GUIOs["POSITIONS_TRADERMODECACODESELECTIONBOX"].getSelected()[0]
        except: _caCode_selected = None
        self.puVar['currencyAnalysis_selected'] = _caCode_selected
        if (_caCode_selected == None): self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTNEW"].updateText(text = "-")
        else:                          self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTNEW"].updateText(text = _caCode_selected)
        self.pageAuxillaryFunctions['CHECKIFCANAPPLYNEWPARAMS']()
    def __onSelectionUpdate_Positions_NewTradeConfigurationCode(objInstance, **kwargs):
        try:    _tcCode_selected = self.GUIOs["POSITIONS_TRADERMODETCCODESELECTIONBOX"].getSelected()[0]
        except: _tcCode_selected = None
        self.puVar['tradeConfiguration_selected'] = _tcCode_selected
        if (_tcCode_selected == None): self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTNEW"].updateText(text = "-")
        else:                          self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTNEW"].updateText(text = _tcCode_selected)
        if ((self.puVar['accounts_selected'] != None) and (self.puVar['positions_selected'] != None)): self.pageAuxillaryFunctions['CHECKIFCANAPPLYNEWPARAMS']()
    def __onTextUpdate_Positions_NewPriority(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANAPPLYNEWPARAMS']()
    def __onTextUpdate_Positions_NewAssumedRatio(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANAPPLYNEWPARAMS']()
    def __onTextUpdate_Positions_NewMaxAllocatedBalance(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANAPPLYNEWPARAMS']()
    def __onStatusUpdate_Positions_NewTradeStatusSwitch(objInstance, **kwargs):
        #Password
        localID = self.puVar['accounts_selected']
        if (localID in self.puVar['accounts_passwords']): password = self.puVar['accounts_passwords'][localID]
        else:                                             password = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
        #Asset
        positionSymbol = self.puVar['positions_selected']
        #Get new values
        newTradeStatus = self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSSWITCH"].getStatus()
        #Request Dispatch
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', 
                          functionID = 'updatePositionTradeStatus', 
                          functionParams = {'localID':        localID,
                                            'password':       password,
                                            'positionSymbol': positionSymbol,
                                            'newTradeStatus': newTradeStatus}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONACCOUNTCONTROLREQUESTRESPONSE'])
        #Buttons Temporary Deactivation
        self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSSWITCH"].deactivate()
    def __onStatusUpdate_Positions_NewReduceOnlySwitch(objInstance, **kwargs):
        #Password
        localID = self.puVar['accounts_selected']
        if (localID in self.puVar['accounts_passwords']): password = self.puVar['accounts_passwords'][localID]
        else:                                             password = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
        #Asset
        positionSymbol = self.puVar['positions_selected']
        #Get new values
        newTradeStatus = self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYSWITCH"].getStatus()
        #Request Dispatch
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', 
                          functionID = 'updatePositionReduceOnly', 
                          functionParams = {'localID':        localID,
                                            'password':       password,
                                            'positionSymbol': positionSymbol,
                                            'newReduceOnly':  newTradeStatus}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONACCOUNTCONTROLREQUESTRESPONSE'])
        #Buttons Temporary Deactivation
        self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYSWITCH"].deactivate()
    def __onButtonRelease_Positions_ApplyNewParams(objInstance, **kwargs):
        #Password
        localID = self.puVar['accounts_selected']
        if (localID in self.puVar['accounts_passwords']): password = self.puVar['accounts_passwords'][localID]
        else:                                             password = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
        #Asset
        positionSymbol = self.puVar['positions_selected']
        _position = self.puVar['accounts'][self.puVar['accounts_selected']]['positions'][self.puVar['positions_selected']]
        #Get new values
        try:    _caCode_new = self.GUIOs["POSITIONS_TRADERMODECACODESELECTIONBOX"].getSelected()[0]
        except: _caCode_new = None
        try:    _tcCode_new = self.GUIOs["POSITIONS_TRADERMODETCCODESELECTIONBOX"].getSelected()[0]
        except: _tcCode_new = None
        try:    _priority_new = int(self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTNEW"].getText())
        except: _priority_new = None
        try:    _assumedRatio_new = round(float(self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTNEW"].getText())/100, 5)
        except: _assumedRatio_new = None
        _maxAllocatedBalance_enteredStr = self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTNEW"].getText()
        if (_maxAllocatedBalance_enteredStr == ""): _maxAllocatedBalance_new = float('inf')
        else:
            try:    _maxAllocatedBalance_new = round(float(_maxAllocatedBalance_enteredStr), _position['precisions']['quote'])
            except: _maxAllocatedBalance_new = None
        #Request Dispatch
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', 
                          functionID = 'updatePositionTraderParams', 
                          functionParams = {'localID':        localID,
                                            'password':       password,
                                            'positionSymbol': positionSymbol,
                                            'newCurrencyAnalysisCode':   _caCode_new,
                                            'newTradeConfigurationCode': _tcCode_new,
                                            'newPriority':               _priority_new,
                                            'newAssumedRatio':           _assumedRatio_new,
                                            'newMaxAllocatedBalance':    _maxAllocatedBalance_new}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONACCOUNTCONTROLREQUESTRESPONSE'])
        #Buttons Temporary Deactivation
        self.GUIOs["POSITIONS_TRADERMODEAPPLYBUTTON"].deactivate()
    def __onButtonRelease_Positions_ResetTradeControlTracker(objInstance, **kwargs):
        #Password
        localID = self.puVar['accounts_selected']
        if (localID in self.puVar['accounts_passwords']): password = self.puVar['accounts_passwords'][localID]
        else:                                             password = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
        #Asset
        positionSymbol = self.puVar['positions_selected']
        #Request Dispatch
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER',
                          functionID = 'resetTradeControlTracker', 
                          functionParams = {'localID':        localID,
                                            'password':       password,
                                            'positionSymbol': positionSymbol}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONACCOUNTCONTROLREQUESTRESPONSE'])
        #Buttons Temporary Deactivation
        self.GUIOs["POSITIONS_TRADERMODERESETTRACECONTROLTRACKERBUTTON"].deactivate()
    objFunctions['ONSELECTIONUPDATE_POSITIONS_DISPLAYMODE']                 = __onSelectionUpdate_Positions_DisplayMode
    objFunctions['ONOBJECTUPDATE_POSITIONS_FILTER']                         = __onObjectUpdate_Positions_Filter
    objFunctions['ONSELECTIONUPDATE_POSITIONS_POSITION']                    = __onSelectionUpdate_Positions_Position
    objFunctions['ONSTATUSUPDATE_POSITIONS_FORCECLEARPOSITIONSAFETYSWTICH'] = __onStatusUpdate_Positions_ForceClearPositionSafetySwitch
    objFunctions['ONBUTTONRELEASE_POSITIONS_FORCECLEARPOSITION']            = __onButtonRelease_Positions_ForceClearPosition
    objFunctions['ONSELECTIONUPDATE_POSITIONS_NEWCURRENCYANALYSISCODE']     = __onSelectionUpdate_Positions_NewCurrencyAnalysisCode
    objFunctions['ONSELECTIONUPDATE_POSITIONS_NEWTRADECONFIGURATIONCODE']   = __onSelectionUpdate_Positions_NewTradeConfigurationCode
    objFunctions['ONTEXTUPDATE_POSITIONS_NEWPRIORITY']                      = __onTextUpdate_Positions_NewPriority
    objFunctions['ONTEXTUPDATE_POSITIONS_NEWASSUMEDRATIO']                  = __onTextUpdate_Positions_NewAssumedRatio
    objFunctions['ONTEXTUPDATE_POSITIONS_NEWMAXALLOCATEDBALANCE']           = __onTextUpdate_Positions_NewMaxAllocatedBalance
    objFunctions['ONSTATUSUPDATE_POSITIONS_NEWTRADESTATUSSWITCH']           = __onStatusUpdate_Positions_NewTradeStatusSwitch
    objFunctions['ONSTATUSUPDATE_POSITIONS_NEWREDUCEONLYSWITCH']            = __onStatusUpdate_Positions_NewReduceOnlySwitch
    objFunctions['ONBUTTONRELEASE_POSITIONS_APPLYNEWPARAMS']                = __onButtonRelease_Positions_ApplyNewParams
    objFunctions['ONBUTTONRELEASE_POSITIONS_RESETTRADECONTROLTRACKER']      = __onButtonRelease_Positions_ResetTradeControlTracker

    #Return the generated functions
    return objFunctions
#OBJECT FUNCTIONS END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUXILALRY FUNCTIONS --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateAuxillaryFunctions(self):
    auxFunctions = dict()
    
    #<_PAGELOAD>
    def __far_onCurrenciesUpdate(requester, updatedContents):
        if (requester == 'DATAMANAGER'):
            for updatedContent in updatedContents:
                symbol    = updatedContent['symbol']
                contentID = updatedContent['id']
                #A new currency is added
                if (contentID == '_ADDED'):
                    self.puVar['currencies'][symbol] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol))
                else:
                    #---[1]: Currency Server Information Updated
                    if (contentID[0] == 'info_server'): 
                        try:    contentID_1 = contentID[1]
                        except: contentID_1 = None
                        #---[1]: Entire Server Information Updated
                        if (contentID_1 == None): self.puVar['currencies'][symbol]['info_server'] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'info_server'))
                        #---[2]: Currency Status Updated
                        else:
                            if (contentID_1 == 'status'): self.puVar['currencies'][symbol]['info_server']['status'] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'info_server', 'status'))
    def __far_onAccountUpdate(requester, updateType, updatedContent):
        if (requester == 'TRADEMANAGER'):
            if (updateType == 'ADDED'):
                localID = updatedContent
                self.puVar['accounts'][localID] = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ACCOUNTS', localID))
                self.pageAuxillaryFunctions['SETACCOUNTSLIST']()
            elif (updateType == 'REMOVED'):
                localID = updatedContent
                self.pageAuxillaryFunctions['SETACCOUNTSLIST']()
                if (localID == self.puVar['accounts_selected']):
                    #[1]: Account Information & Control
                    self.puVar['accounts_selected'] = None
                    self.pageAuxillaryFunctions['ONACCOUNTSELECTIONUPDATE']()
                    if (localID in self.puVar['accounts_passwords']): del self.puVar['accounts_passwords'][localID]
            elif (updateType == 'UPDATED_STATUS'):
                localID = updatedContent
                newStatus = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ACCOUNTS', localID, 'status'))
                self.puVar['accounts'][localID]['status'] = newStatus
                #SelectionBox Update
                if   (newStatus == 'INACTIVE'): _text = 'INACTIVE'; _textColor = 'RED_LIGHT'
                elif (newStatus == 'ACTIVE'):   _text = 'ACTIVE';   _textColor = 'GREEN_LIGHT'
                _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', _textColor),], 'textAnchor': 'CENTER'}
                self.GUIOs["ACCOUNTSLIST_SELECTIONBOX"].editSelectionListItem(itemKey = localID, item = _newSelectionBoxItem, columnIndex = 3)
                #Account Information Update
                if (localID == self.puVar['accounts_selected']):
                    if   (newStatus == 'ACTIVE'):   self.GUIOs["ACCOUNTSINFORMATION&CONTROL_STATUSDISPLAYTEXT"].updateText(text = newStatus, textStyle = 'GREEN_LIGHT')
                    elif (newStatus == 'INACTIVE'): self.GUIOs["ACCOUNTSINFORMATION&CONTROL_STATUSDISPLAYTEXT"].updateText(text = newStatus, textStyle = 'RED_LIGHT')
            elif (updateType == 'UPDATED_TRADESTATUS'):
                localID = updatedContent
                newTradeStatus = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ACCOUNTS', localID, 'tradeStatus'))
                self.puVar['accounts'][localID]['tradeStatus'] = newTradeStatus
                #SelectionBox Update
                if (newTradeStatus == False): _text = 'FALSE'; _textColor = 'RED_LIGHT'
                else:                         _text = 'TRUE';  _textColor = 'GREEN_LIGHT'
                _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', _textColor),], 'textAnchor': 'CENTER'}
                self.GUIOs["ACCOUNTSLIST_SELECTIONBOX"].editSelectionListItem(itemKey = localID, item = _newSelectionBoxItem, columnIndex = 4)
                #Account Information Update
                if (localID == self.puVar['accounts_selected']):
                    if   (newTradeStatus == True):  self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSDISPLAYTEXT"].updateText(text = 'TRUE',  textStyle = 'GREEN_LIGHT')
                    elif (newTradeStatus == False): self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSDISPLAYTEXT"].updateText(text = 'FALSE', textStyle = 'RED_LIGHT')
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSSWITCH"].setStatus(status = newTradeStatus, callStatusUpdateFunction = False)
            elif (updateType == 'UPDATED_ASSET'):
                localID         = updatedContent[0]
                assetName       = updatedContent[1]
                updatedDataName = updatedContent[2]
                _displayingAsset = self.GUIOs["ASSETS_ASSETTODISPLAYSELECTIONBOX"].getSelected()
                _assetData       = self.puVar['accounts'][localID]['assets'][assetName]
                newValue = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ACCOUNTS', localID, 'assets', assetName, updatedDataName))
                _assetData[updatedDataName] = newValue
                if (localID == self.puVar['accounts_selected']):
                    if (_displayingAsset == assetName):
                        if (updatedDataName == 'marginBalance'):
                            if (_assetData['marginBalance'] == None): self.GUIOs["ASSETS_MARGINBALANCEDISPLAYTEXT"].updateText(text = "-")
                            else:                                     self.GUIOs["ASSETS_MARGINBALANCEDISPLAYTEXT"].updateText(text = atmEta_Auxillaries.floatToString(number = _assetData['marginBalance'], precision = _ASSETPRECISIONS[assetName]))
                        elif ((updatedDataName == 'walletBalance') or (updatedDataName == 'crossWalletBalance') or (updatedDataName == 'isolatedWalletBalance')):
                            if (_assetData['walletBalance'] == None):         _wb_total_str = "-"
                            else:                                             _wb_total_str = atmEta_Auxillaries.floatToString(number = _assetData['walletBalance'], precision = _ASSETPRECISIONS[assetName])
                            if (_assetData['crossWalletBalance'] == None):    _wb_cross_str = "-"
                            else:                                             _wb_cross_str = atmEta_Auxillaries.floatToString(number = _assetData['crossWalletBalance'], precision = _ASSETPRECISIONS[assetName])
                            if (_assetData['isolatedWalletBalance'] == None): _wb_isolated_str = "-"
                            else:                                             _wb_isolated_str = atmEta_Auxillaries.floatToString(number = _assetData['isolatedWalletBalance'], precision = _ASSETPRECISIONS[assetName])
                            self.GUIOs["ASSETS_WALLETBALANCEDISPLAYTEXT"].updateText(text = "{:s} / {:s} / {:s}".format(_wb_total_str, _wb_cross_str, _wb_isolated_str))
                        elif (updatedDataName == 'availableBalance'):
                            if (_assetData['availableBalance'] == None): self.GUIOs["ASSETS_AVAILABLEBALANCEDISPLAYTEXT"].updateText(text = "-")
                            else:                                        self.GUIOs["ASSETS_AVAILABLEBALANCEDISPLAYTEXT"].updateText(text = atmEta_Auxillaries.floatToString(number = _assetData['availableBalance'], precision = _ASSETPRECISIONS[assetName]))
                        elif ((updatedDataName == 'crossPositionInitialMargin') or (updatedDataName == 'isolatedPositionInitialMargin') or (updatedDataName == 'isolatedMargin') or (updatedDataName == 'openOrderInitialMargin')):
                            _updatePositionInitialMargin = ((updatedDataName == 'crossPositionInitialMargin') or (updatedDataName == 'isolatedPositionInitialMargin'))
                            _updateMargins               = ((updatedDataName == 'isolatedMargin') or (updatedDataName == 'openOrderInitialMargin') or (_updatePositionInitialMargin == True))
                            if (_updatePositionInitialMargin == True):
                                if (_assetData['crossPositionInitialMargin'] == None): _piMrgn_cross = "-"
                                else:                                                  _piMrgn_cross = atmEta_Auxillaries.floatToString(number = _assetData['crossPositionInitialMargin'], precision = _ASSETPRECISIONS[assetName])
                                if (_assetData['isolatedPositionInitialMargin'] == None): _piMrgn_isolated = "-"
                                else:                                                     _piMrgn_isolated = atmEta_Auxillaries.floatToString(number = _assetData['isolatedPositionInitialMargin'], precision = _ASSETPRECISIONS[assetName])
                                self.GUIOs["ASSETS_POSITIONINITIALMARGINDISPLAYTEXT"].updateText(text = "{:s} / {:s}".format(_piMrgn_cross, _piMrgn_isolated))
                            if (_updateMargins == True):
                                if ((_assetData['crossPositionInitialMargin'] == None) and (_assetData['isolatedPositionInitialMargin'] != None)): _mrgn_pi_str = "-"
                                else:
                                    _positionInitialMarginSum = 0
                                    if (_assetData['crossPositionInitialMargin']    != None): _positionInitialMarginSum += _assetData['crossPositionInitialMargin']
                                    if (_assetData['isolatedPositionInitialMargin'] != None): _positionInitialMarginSum += _assetData['isolatedPositionInitialMargin']
                                    _mrgn_pi_str = atmEta_Auxillaries.floatToString(number = _positionInitialMarginSum, precision = _ASSETPRECISIONS[assetName])
                                if (_assetData['openOrderInitialMargin'] == None): _mrgn_oo_str = "-"
                                else:                                              _mrgn_oo_str = atmEta_Auxillaries.floatToString(number = _assetData['openOrderInitialMargin'], precision = _ASSETPRECISIONS[assetName])
                                if (_assetData['crossMaintenanceMargin'] == None): _mrgn_maint_str = "-"
                                else:                                              _mrgn_maint_str = atmEta_Auxillaries.floatToString(number = _assetData['crossMaintenanceMargin'], precision = _ASSETPRECISIONS[assetName])
                                self.GUIOs["ASSETS_MARGINDISPLAYTEXT"].updateText(text = "{:s} / {:s} / {:s}".format(_mrgn_pi_str, _mrgn_oo_str, _mrgn_maint_str))
                        elif (updatedDataName == 'allocatableBalance'):
                            if (_assetData['allocatableBalance'] == None): self.GUIOs["ASSETS_ALLOCATABLEBALANCEDISPLAYTEXT"].updateText(text = "-")
                            else:                                          self.GUIOs["ASSETS_ALLOCATABLEBALANCEDISPLAYTEXT"].updateText(text = atmEta_Auxillaries.floatToString(number = _assetData['allocatableBalance'], precision = _ASSETPRECISIONS[assetName]))
                        elif (updatedDataName == 'allocatedBalance'):
                            self.GUIOs["ASSETS_ALLOCATEDBALANCEDISPLAYTEXT"].updateText(text = atmEta_Auxillaries.floatToString(number = _assetData['allocatedBalance'], precision = _ASSETPRECISIONS[assetName]))
                        elif ((updatedDataName == 'unrealizedPNL') or (updatedDataName == 'crossUnrealizedPNL') or (updatedDataName == 'isolatedUnrealizedPNL')):
                            if (_assetData['unrealizedPNL'] == None): _unPNL_total_str = "-"; _unPNL_total_strColor = 'DEFAULT'
                            else:                                             
                                if   (0 < _assetData['unrealizedPNL']):  _unPNL_total_strColor = 'GREEN_LIGHT'
                                elif (_assetData['unrealizedPNL'] < 0):  _unPNL_total_strColor = 'RED_LIGHT'
                                elif (_assetData['unrealizedPNL'] == 0): _unPNL_total_strColor = 'DEFAULT'
                                _unPNL_total_str = atmEta_Auxillaries.floatToString(number = _assetData['unrealizedPNL'], precision = _ASSETPRECISIONS[assetName])
                                if (0 < _assetData['unrealizedPNL']): _unPNL_total_str = "+"+_unPNL_total_str
                            if (_assetData['crossUnrealizedPNL'] == None): _unPNL_cross_str = "-"; _unPNL_cross_strColor = 'DEFAULT'
                            else:                                             
                                if   (0 < _assetData['crossUnrealizedPNL']):  _unPNL_cross_strColor = 'GREEN_LIGHT'
                                elif (_assetData['crossUnrealizedPNL'] < 0):  _unPNL_cross_strColor = 'RED_LIGHT'
                                elif (_assetData['crossUnrealizedPNL'] == 0): _unPNL_cross_strColor = 'DEFAULT'
                                _unPNL_cross_str = atmEta_Auxillaries.floatToString(number = _assetData['crossUnrealizedPNL'], precision = _ASSETPRECISIONS[assetName])
                                if (0 < _assetData['crossUnrealizedPNL']): _unPNL_cross_str = "+"+_unPNL_cross_str
                            if (_assetData['isolatedUnrealizedPNL'] == None): _unPNL_isolated_str = "-"; _unPNL_isolated_strColor = 'DEFAULT'
                            else:                                             
                                if   (0 < _assetData['isolatedUnrealizedPNL']):  _unPNL_isolated_strColor = 'GREEN_LIGHT'
                                elif (_assetData['isolatedUnrealizedPNL'] < 0):  _unPNL_isolated_strColor = 'RED_LIGHT'
                                elif (_assetData['isolatedUnrealizedPNL'] == 0): _unPNL_isolated_strColor = 'DEFAULT'
                                _unPNL_isolated_str = atmEta_Auxillaries.floatToString(number = _assetData['isolatedUnrealizedPNL'], precision = _ASSETPRECISIONS[assetName])
                                if (0 < _assetData['isolatedUnrealizedPNL']): _unPNL_isolated_str = "+"+_unPNL_isolated_str
                            _dtPair = ((_unPNL_total_str,    _unPNL_total_strColor), 
                                       (" / ",               'DEFAULT'), 
                                       (_unPNL_cross_str,    _unPNL_cross_strColor), 
                                       (" / ",               'DEFAULT'), 
                                       (_unPNL_isolated_str, _unPNL_isolated_strColor))
                            _displayTextStyle = list(); _displayText = ""
                            for _dt, _dts in _dtPair: _displayTextStyle.append(((len(_displayText), len(_displayText)+len(_dt)), _dts)); _displayText += _dt
                            self.GUIOs["ASSETS_UNREALIZEDPNLDISPLAYTEXT"].updateText(text = _displayText, textStyle = _displayTextStyle)
                        elif (updatedDataName == 'commitmentRate'):
                            _cr = _assetData['commitmentRate']
                            if (_cr == None): self.GUIOs["ASSETS_COMMITMENTRATEDISPLAYTEXT"].updateText(text = "N/A", textStyle = 'DEFAULT')
                            else:
                                if   (0.00 <= _cr) and (_cr <  0.30): _textColor = 'GREEN_DARK'
                                elif (0.30 <= _cr) and (_cr <  0.50): _textColor = 'GREEN_LIGHT'
                                elif (0.50 <= _cr) and (_cr <  0.70): _textColor = 'YELLOW'
                                elif (0.70 <= _cr) and (_cr <  0.80): _textColor = 'ORANGE_LIGHT'
                                elif (0.80 <= _cr) and (_cr <  0.90): _textColor = 'RED_LIGHT'
                                elif (0.90 <= _cr) and (_cr <= 1.00): _textColor = 'RED'
                                else:                                 _textColor = 'VIOLET_LIGHT'
                                self.GUIOs["ASSETS_COMMITMENTRATEDISPLAYTEXT"].updateText(text = "{:.3f} %".format(_cr*100), textStyle = _textColor)
                        elif (updatedDataName == 'riskLevel'):
                            _rl = _assetData['riskLevel']
                            if (_rl == None): self.GUIOs["ASSETS_RISKLEVELDISPLAYTEXT"].updateText(text = "N/A", textStyle = 'DEFAULT')
                            else:
                                if   (0.00 <= _rl) and (_rl <  0.30): _textColor = 'GREEN_DARK'
                                elif (0.30 <= _rl) and (_rl <  0.50): _textColor = 'GREEN_LIGHT'
                                elif (0.50 <= _rl) and (_rl <  0.70): _textColor = 'ORANGE_LIGHT'
                                elif (0.70 <= _rl) and (_rl <  0.90): _textColor = 'RED_LIGHT'
                                elif (0.90 <= _rl) and (_rl <= 1.00): _textColor = 'RED'
                                self.GUIOs["ASSETS_RISKLEVELDISPLAYTEXT"].updateText(text = "{:.3f} %".format(_rl*100), textStyle = _textColor)
                        elif (updatedDataName == 'assumedRatio'):
                            _ar_base = _assetData['assumedRatio']
                            if   (0.00 <= _ar_base) and (_ar_base <  0.10): _textColor = 'GREEN_DARK'
                            elif (0.10 <= _ar_base) and (_ar_base <  0.20): _textColor = 'GREEN_LIGHT'
                            elif (0.20 <= _ar_base) and (_ar_base <  0.30): _textColor = 'BLUE_LIGHT'
                            elif (0.30 <= _ar_base) and (_ar_base <  0.40): _textColor = 'YELLOW'
                            elif (0.40 <= _ar_base) and (_ar_base <  0.50): _textColor = 'ORANGE_LIGHT'
                            elif (0.50 <= _ar_base) and (_ar_base <= 0.60): _textColor = 'RED_LIGHT'
                            elif (0.60 <= _ar_base):                        _textColor = 'RED'
                            self.GUIOs["ASSETS_BASEASSUMEDRATIODISPLAYTEXT"].updateText(text = "{:.3f} %".format(_ar_base*100), textStyle = _textColor)
                        elif (updatedDataName == 'weightedAssumedRatio'):
                            _ar_weighted = _assetData['weightedAssumedRatio']
                            if   (0.00 <= _ar_weighted) and (_ar_weighted <  0.10): _textColor = 'GREEN_DARK'
                            elif (0.10 <= _ar_weighted) and (_ar_weighted <  0.20): _textColor = 'GREEN_LIGHT'
                            elif (0.20 <= _ar_weighted) and (_ar_weighted <  0.30): _textColor = 'BLUE_LIGHT'
                            elif (0.30 <= _ar_weighted) and (_ar_weighted <  0.40): _textColor = 'YELLOW'
                            elif (0.40 <= _ar_weighted) and (_ar_weighted <  0.50): _textColor = 'ORANGE_LIGHT'
                            elif (0.50 <= _ar_weighted) and (_ar_weighted <= 0.60): _textColor = 'RED_LIGHT'
                            elif (0.60 <= _ar_weighted):                            _textColor = 'RED'
                            self.GUIOs["ASSETS_WEIGHTEDASSUMEDRATIODISPLAYTEXT"].updateText(text = "{:.3f} %".format(_ar_weighted*100), textStyle = _textColor)
                        elif (updatedDataName == 'allocationRatio'):
                            self.GUIOs["ASSETS_ALLOCATIONRATIOSLIDER"].setSliderValue(newValue = _assetData['allocationRatio']*100, callValueUpdateFunction = True)
                            self.GUIOs["ASSETS_ALLOCATIONRATIODISPLAYTEXT"].updateText(text = "{:.1f} %".format(_assetData['allocationRatio']*100))
            elif (updateType == 'UPDATED_POSITION_ADDED'):
                localID        = updatedContent[0]
                positionSymbol = updatedContent[1]
                newPosition = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ACCOUNTS', localID, 'positions', positionSymbol))
                self.puVar['accounts'][localID]['positions'][positionSymbol] = newPosition
                if (localID == self.puVar['accounts_selected']): self.pageAuxillaryFunctions['SETPOSITIONSLIST']()
            elif (updateType == 'UPDATED_POSITION'):
                localID         = updatedContent[0]
                positionSymbol  = updatedContent[1]
                updatedDataName = updatedContent[2]
                _displayMode = self.GUIOs["POSITIONS_DISPLAYMODESELECTIONBOX"].getSelected()
                _position    = self.puVar['accounts'][localID]['positions'][positionSymbol]
                newValue = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ACCOUNTS', localID, 'positions', positionSymbol, updatedDataName))
                _position[updatedDataName] = newValue
                if (localID == self.puVar['accounts_selected']): 
                    #SelectionBox Update
                    _cIndex = _POSITIONDATA_SELECTIONBOXCOLUMNINDEX[updatedDataName][_displayMode]
                    if (_cIndex != None):
                        #[1]: Tradable
                        if (updatedDataName == 'tradable'):
                            if (_position['tradable'] == True): _text = 'TRUE';  _textColor = 'GREEN_LIGHT'
                            else:                               _text = 'FALSE'; _textColor = 'RED_LIGHT'
                            _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', _textColor),], 'textAnchor': 'CENTER'}
                        #[2]: Trade Status
                        elif (updatedDataName == 'tradeStatus'):
                            if (_position['tradeStatus'] == True): _text = 'TRUE';  _textColor = 'GREEN_LIGHT'
                            else:                                  _text = 'FALSE'; _textColor = 'RED_LIGHT'
                            _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', _textColor),], 'textAnchor': 'CENTER'}
                        #[3]: Reduce Only
                        elif (updatedDataName == 'reduceOnly'):
                            if (_position['reduceOnly'] == True): _text = 'TRUE';  _textColor = 'ORANGE_LIGHT'
                            else:                                 _text = 'FALSE'; _textColor = 'GREEN_LIGHT'
                            _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', _textColor),], 'textAnchor': 'CENTER'}
                        #[4]: Leverage
                        elif (updatedDataName == 'leverage'):
                            if (_position['leverage'] == None): _text = "-"
                            else:                               _text = str(_position['leverage'])
                            _newSelectionBoxItem = {'text': _text}
                        #[5]: Margin Mode
                        elif (updatedDataName == 'isolated'):
                            if   (_position['isolated'] == True):  _text = 'ISOLATED'
                            elif (_position['isolated'] == False): _text = 'CROSSED'
                            elif (_position['isolated'] == None):  _text = '-'
                            _newSelectionBoxItem = {'text': _text}
                        #[6]: Quantity
                        elif (updatedDataName == 'quantity'):
                            if (_position['quantity'] == None): _text = "-"
                            else:                               _text = atmEta_Auxillaries.floatToString(number = _position['quantity'], precision = _position['precisions']['quantity'])
                            _newSelectionBoxItem = {'text': _text}
                        #[7]: Isolated Wallet Balance
                        elif (updatedDataName == 'isolatedWalletBalance'):
                            if (_position['isolatedWalletBalance'] == None): _text = "-"
                            else:                                            _text = atmEta_Auxillaries.floatToString(number = _position['isolatedWalletBalance'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']])
                            _newSelectionBoxItem = {'text': _text}
                        #[8]: Position Initial Margin
                        elif (updatedDataName == 'positionInitialMargin'):
                            if (_position['positionInitialMargin'] == None): _text = "-"
                            else:                                            _text = atmEta_Auxillaries.floatToString(number = _position['positionInitialMargin'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']])
                            _newSelectionBoxItem = {'text': _text}
                        #[9]: Open Order Initial Margin
                        elif (updatedDataName == 'openOrderInitialMargin'):
                            if (_position['openOrderInitialMargin'] == None): _text = "-"
                            else:                                             _text = atmEta_Auxillaries.floatToString(number = _position['openOrderInitialMargin'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']])
                            _newSelectionBoxItem = {'text': _text}
                        #[10]: Maintenance Margin
                        elif (updatedDataName == 'maintenanceMargin'):
                            if (_position['maintenanceMargin'] == None): _text = "-"
                            else:                                        _text = atmEta_Auxillaries.floatToString(number = _position['maintenanceMargin'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']])
                            _newSelectionBoxItem = {'text': _text}
                        #[11]: Entry Price
                        elif (updatedDataName == 'entryPrice'):
                            if (_position['entryPrice'] == None): _text = "-"
                            else:                                 _text = atmEta_Auxillaries.floatToString(number = _position['entryPrice'], precision = _position['precisions']['price'])
                            _newSelectionBoxItem = {'text': _text}
                        #[12]: Current Price
                        elif (updatedDataName == 'currentPrice'):
                            if (_position['currentPrice'] == None): _text = "-"; _textColor = 'DEFAULT'
                            else:
                                if (_position['entryPrice'] == None): _text = atmEta_Auxillaries.floatToString(number = _position['currentPrice'], precision = _position['precisions']['price']); _textColor = 'DEFAULT'
                                else:
                                    _pDifferencePerc = round((_position['currentPrice']/_position['entryPrice']-1)*100, 3)
                                    if   (_pDifferencePerc < 0):  _text = "{:s} [{:.3f} %]".format(atmEta_Auxillaries.floatToString(number  = _position['currentPrice'], precision = _position['precisions']['price']), _pDifferencePerc); _textColor = 'RED_LIGHT'
                                    elif (_pDifferencePerc == 0): _text = "{:s} [{:.3f} %]".format(atmEta_Auxillaries.floatToString(number  = _position['currentPrice'], precision = _position['precisions']['price']), _pDifferencePerc); _textColor = 'DEFAULT'
                                    elif (0 < _pDifferencePerc):  _text = "{:s} [+{:.3f} %]".format(atmEta_Auxillaries.floatToString(number = _position['currentPrice'], precision = _position['precisions']['price']), _pDifferencePerc); _textColor = 'GREEN_LIGHT'
                            _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', _textColor),]}
                        #[13]: Liquidation Price
                        elif (updatedDataName == 'liquidationPrice'):
                            if (_position['liquidationPrice'] == None): _text = "-"
                            else:                  _text = atmEta_Auxillaries.floatToString(number = _position['liquidationPrice'], precision = _position['precisions']['price'])
                            _newSelectionBoxItem = {'text': _text}
                        #[14]: Unrealized PNL
                        elif (updatedDataName == 'unrealizedPNL'):
                            if ((_position['unrealizedPNL'] == None) or (_position['positionInitialMargin'] == None) or (_position['positionInitialMargin'] == 0)):
                                _text = "-"; _textColor = 'DEFAULT'
                            else:                                         
                                _roi = round(_position['unrealizedPNL']/_position['positionInitialMargin']*100, 3)
                                if   (_position['unrealizedPNL'] < 0):  _text = "{:s} [{:.3f} %]".format(atmEta_Auxillaries.floatToString(number  = _position['unrealizedPNL'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']]), _roi); _textColor = 'RED_LIGHT'
                                elif (_position['unrealizedPNL'] == 0): _text = "{:s} [{:.3f} %]".format(atmEta_Auxillaries.floatToString(number  = _position['unrealizedPNL'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']]), _roi); _textColor = 'DEFAULT'
                                elif (0 < _position['unrealizedPNL']):  _text = "{:s} [+{:.3f} %]".format(atmEta_Auxillaries.floatToString(number = _position['unrealizedPNL'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']]), _roi); _textColor = 'GREEN_LIGHT'
                            _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', _textColor),]}
                        #[15]: Assumed Ratio
                        elif (updatedDataName == 'assumedRatio'):
                            _text = "{:.3f} %".format(_position['assumedRatio']*100)
                            _newSelectionBoxItem = {'text': _text}
                        #[16]: Weighted Assumed Ratio
                        elif (updatedDataName == 'weightedAssumedRatio'):
                            _war = _position['weightedAssumedRatio']
                            if (_war == None): _text = "N/A"
                            else:              _text = "{:.3f} %".format(_position['weightedAssumedRatio']*100)
                            _newSelectionBoxItem = {'text': _text}
                        #[17]: Allocated Balance
                        elif (updatedDataName == 'allocatedBalance'):
                            _text = atmEta_Auxillaries.floatToString(number = _position['allocatedBalance'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']])
                            _newSelectionBoxItem = {'text': _text}
                        #[18]: Max Allocated Balance
                        elif (updatedDataName == 'maxAllocatedBalance'):
                            if (_position['maxAllocatedBalance'] == float('inf')): _text = 'INF'
                            else:                                                  _text = atmEta_Auxillaries.floatToString(number = _position['maxAllocatedBalance'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']])
                            _newSelectionBoxItem = {'text': _text}
                        #[19]: Commitment Rate
                        elif (updatedDataName == 'commitmentRate'):
                            _cr = _position['commitmentRate']
                            if (_cr == None): _text = "N/A"; _textColor = 'DEFAULT'
                            else:
                                _text = "{:.3f} %".format(_cr*100)
                                if   (0.00 <= _cr) and (_cr <  0.30): _textColor = 'GREEN_DARK'
                                elif (0.30 <= _cr) and (_cr <  0.50): _textColor = 'GREEN_LIGHT'
                                elif (0.50 <= _cr) and (_cr <  0.70): _textColor = 'YELLOW'
                                elif (0.70 <= _cr) and (_cr <  0.80): _textColor = 'ORANGE_LIGHT'
                                elif (0.80 <= _cr) and (_cr <  0.90): _textColor = 'RED_LIGHT'
                                elif (0.90 <= _cr) and (_cr <= 1.00): _textColor = 'RED'
                                else:                                 _textColor = 'VIOLET_LIGHT'
                            _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', _textColor),]}
                        #[20]: Risk Level
                        elif (updatedDataName == 'riskLevel'):
                            _rl = _position['riskLevel']
                            if (_rl == None): _text = "N/A"; _textColor = 'DEFAULT'
                            else:
                                if   (0.00 <= _rl) and (_rl <  0.30): _textColor = 'GREEN_DARK'
                                elif (0.30 <= _rl) and (_rl <  0.50): _textColor = 'GREEN_LIGHT'
                                elif (0.50 <= _rl) and (_rl <  0.70): _textColor = 'ORANGE_LIGHT'
                                elif (0.70 <= _rl) and (_rl <  0.90): _textColor = 'RED_LIGHT'
                                elif (0.90 <= _rl) and (_rl <= 1.00): _textColor = 'RED'
                                _text = "{:.3f} %".format(_rl*100)
                            _newSelectionBoxItem = {'text': _text, 'textStyles': [('all', _textColor),]}
                        #[21]: Currency Analysis Code
                        elif (updatedDataName == 'currencyAnalysisCode'):
                            if (_position['currencyAnalysisCode'] == None): _text = "-"
                            else:                                           _text = _position['currencyAnalysisCode']
                            _newSelectionBoxItem = {'text': _text}
                        #[22]: Trade Configuration Code
                        elif (updatedDataName == 'tradeConfigurationCode'):
                            if (_position['tradeConfigurationCode'] == None): _text = "-"
                            else:                                             _text = _position['tradeConfigurationCode']
                            _newSelectionBoxItem = {'text': _text}
                        #[23]: Priority
                        elif (updatedDataName == 'priority'):
                            _text = str(_position['priority'])
                            _newSelectionBoxItem = {'text': _text}
                        #[24]: Trade Control
                        elif (updatedDataName == 'tradeControlTracker'):
                            _text = json.dumps(_position['tradeControlTracker'])
                            _newSelectionBoxItem = {'text': _text}
                        #[25]: Abrupt Clearing Records
                        elif (updatedDataName == 'maximumProfitPrice'):
                            if (len(_position['abruptClearingRecords']) == 0): _text = '-'
                            else:                                              _text = str(_position['abruptClearingRecords'])
                            _newSelectionBoxItem = {'text': _text}
                        #Finally
                        self.GUIOs["POSITIONS_{:s}MODESELECTIONBOX".format(_displayMode)].editSelectionListItem(itemKey = positionSymbol, item = _newSelectionBoxItem, columnIndex = _cIndex)
                    #Selected Position Information Update
                    if (_displayMode == 'BASIC'):
                        if (positionSymbol == self.puVar['positions_selected']):
                            if (updatedDataName == 'quantity'): self.pageAuxillaryFunctions['CHECKIFCANFORCECLEARPOSITION']()
                    if (_displayMode == 'TRADER'):
                        if (positionSymbol == self.puVar['positions_selected']):
                            if (updatedDataName == 'currencyAnalysisCode'):
                                if (_position['currencyAnalysisCode'] == None): self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTOLD"].updateText(text = "-")
                                else:                                           self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTOLD"].updateText(text = _position['currencyAnalysisCode'])
                            elif (updatedDataName == 'tradeConfigurationCode'):
                                if (_position['tradeConfigurationCode'] == None): self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTOLD"].updateText(text = "-")
                                else:                                             self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTOLD"].updateText(text = _position['tradeConfigurationCode'])
                            elif (updatedDataName == 'priority'):
                                self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTOLD"].updateText(text = "{:d}".format(_position['priority']))
                            elif (updatedDataName == 'assumedRatio'):
                                self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTOLD"].updateText(text = "{:.3f} %".format(_position['assumedRatio']*100))
                            elif (updatedDataName == 'maxAllocatedBalance'):
                                if (_position['maxAllocatedBalance'] == float('inf')): self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTNEW"].updateText(text = "")
                                else:                                                  self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTNEW"].updateText(text = atmEta_Auxillaries.floatToString(number = _position['maxAllocatedBalance'], precision = _position['precisions']['quote']))
                            elif (updatedDataName == 'tradable'):
                                if (_position['tradable'] == True): self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSSWITCH"].activate()
                                else:                               self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSSWITCH"].deactivate()
                            elif (updatedDataName == 'tradeStatus'):
                                if (_position['tradeStatus'] == True): self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSVALUETEXT"].updateText(text = 'TRUE',  textStyle = 'GREEN_LIGHT')
                                else:                                  self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSVALUETEXT"].updateText(text = 'FALSE', textStyle = 'RED_LIGHT')
                                self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSSWITCH"].setStatus(status = _position['tradeStatus'], callStatusUpdateFunction = False)
                            elif (updatedDataName == 'reduceOnly'):
                                if (_position['reduceOnly'] == True): self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYVALUETEXT"].updateText(text = 'TRUE',  textStyle = 'ORANGE_LIGHT')
                                else:                                 self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYVALUETEXT"].updateText(text = 'FALSE', textStyle = 'GREEN_LIGHT')
                                self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYSWITCH"].setStatus(status = _position['reduceOnly'], callStatusUpdateFunction = False)
    def __far_onCurrencyAnalysisUpdate(requester, updateType, currencyAnalysisCode):
        if (requester == 'TRADEMANAGER'):
            if (updateType == 'ADDED'):
                self.puVar['currencyAnalysis'][currencyAnalysisCode] = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode))
                if (self.puVar['currencyAnalysis'][currencyAnalysisCode]['currencySymbol'] == self.puVar['positions_selected']): self.pageAuxillaryFunctions['SETCURRENCYANALYSISLIST']()
            elif (updateType == 'REMOVED'):
                if (currencyAnalysisCode in self.puVar['currencyAnalysis_forSelectedPosition']):
                    self.pageAuxillaryFunctions['SETCURRENCYANALYSISLIST']()
                    if (currencyAnalysisCode == self.puVar['currencyAnalysis_selected']):
                        self.puVar['currencyAnalysis_selected'] = None
                        self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTNEW"].updateText(text = "-")
                        self.GUIOs["POSITIONS_TRADERMODEAPPLYBUTTON"].deactivate()
    def __far_onTradeConfigurationUpdate(requester, updateType, tradeConfigurationCode):
        if (requester == 'TRADEMANAGER'):
            if (updateType == 'ADDED'):
                self.puVar['tradeConfigurations'][tradeConfigurationCode] = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('TRADECONFIGURATIONS', tradeConfigurationCode))
                self.pageAuxillaryFunctions['SETTRADECONFIGURATIONSLIST']()
            if (updateType == 'REMOVED'):
                self.pageAuxillaryFunctions['SETTRADECONFIGURATIONSLIST']()
                if (tradeConfigurationCode == self.puVar['tradeConfiguration_selected']): 
                    self.puVar['tradeConfiguration_selected'] = None
                    self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTNEW"].updateText("-")
                    self.GUIOs["POSITIONS_TRADERMODEAPPLYBUTTON"].deactivate()
    auxFunctions['_FAR_ONCURRENCIESUPDATE']         = __far_onCurrenciesUpdate
    auxFunctions['_FAR_ONACCOUNTUPDATE']            = __far_onAccountUpdate
    auxFunctions['_FAR_ONCURRENCYANALYSISUPDATE']   = __far_onCurrencyAnalysisUpdate
    auxFunctions['_FAR_ONTRADECONFIGURATIONUPDATE'] = __far_onTradeConfigurationUpdate

    #<Accounts List>
    def __setAccountsList():
        accounts_selectionList = dict()
        for accountIndex, localID in enumerate(self.puVar['accounts']):
            _account = self.puVar['accounts'][localID]
            #Display Table Formatting
            _status = _account['status']
            if   (_status == 'INACTIVE'): _text_status = 'INACTIVE'; _textColor_status = 'RED_LIGHT'
            elif (_status == 'ACTIVE'):   _text_status = 'ACTIVE';   _textColor_status = 'GREEN_LIGHT'
            _tradeStatus = _account['tradeStatus']
            if (_tradeStatus == False): _text_tradeStatus = 'FALSE'; _textColor_tradeStatus = 'RED_LIGHT'
            else:                       _text_tradeStatus = 'TRUE';  _textColor_tradeStatus = 'GREEN_LIGHT'
            accounts_selectionList[localID] = [{'text': str(accountIndex),       'textStyles': [('all', 'DEFAULT'),],              'textAnchor': 'CENTER'},
                                               {'text': localID,                 'textStyles': [('all', 'DEFAULT'),],              'textAnchor': 'CENTER'},
                                               {'text': _account['accountType'], 'textStyles': [('all', 'DEFAULT'),],              'textAnchor': 'CENTER'},
                                               {'text': _text_status,            'textStyles': [('all', _textColor_status),],      'textAnchor': 'CENTER'},
                                               {'text': _text_tradeStatus,       'textStyles': [('all', _textColor_tradeStatus),], 'textAnchor': 'CENTER'}]
        self.GUIOs["ACCOUNTSLIST_SELECTIONBOX"].setSelectionList(selectionList = accounts_selectionList, keepSelected = True, displayTargets = 'all', callSelectionUpdateFunction = False)
        #self.pageAuxillaryFunctions['ONACCOUNTSLISTFILTERUPDATE']()
    def __onAccountsListFilterUpdate():
        if   (self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_VIRTUAL"].getStatus() == True): localIDs_filtered = [localID for localID in self.puVar['accounts'] if (self.puVar['accounts'][localID]['accountType'] == 'VIRTUAL')]
        elif (self.GUIOs["ACCOUNTSLIST_FILTERSWITCH_ACTUAL"].getStatus()  == True): localIDs_filtered = [localID for localID in self.puVar['accounts'] if (self.puVar['accounts'][localID]['accountType'] == 'ACTUAL')]
        else:                                                                       localIDs_filtered = 'all'
        self.GUIOs["ACCOUNTSLIST_SELECTIONBOX"].setDisplayTargets(displayTargets = localIDs_filtered)
    auxFunctions['SETACCOUNTSLIST']            = __setAccountsList
    auxFunctions['ONACCOUNTSLISTFILTERUPDATE'] = __onAccountsListFilterUpdate

    #<Accounts Information & Control>
    def __checkIfCanAddAccount():
        #Local ID Test
        _localID_entered = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_LOCALIDTEXTINPUTBOX"].getText()
        if ((0 < len(_localID_entered)) and (_localID_entered not in self.puVar['accounts'])): _test_localID = True
        else:                                                                                  _test_localID = False
        #Binance UID
        _selectedAccountType = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPESELECTIONBOX"].getSelected()
        if (_selectedAccountType == 'ACTUAL'):
            _buid_entered = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDTEXTINPUTBOX"].getText()
            try:    int(_buid_entered); _test_buid = True
            except: _test_buid = False
        elif (_selectedAccountType == 'VIRTUAL'): _test_buid = True
        #Password
        _password_entered = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
        if (8 <= len(_password_entered)): _test_password = True
        else:                             _test_password = False
        #Finally
        _testPassed = ((_test_localID == True) and (_test_buid == True) and (_test_password == True))
        if (_testPassed == True): self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ADDACCOUNTBUTTON"].activate()
        else:                     self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ADDACCOUNTBUTTON"].deactivate()
    def __onAccountSelectionUpdate():
        localID = self.puVar['accounts_selected']
        if (localID == None): 
            #Account List
            if (True):
                #---Local ID
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_LOCALIDTEXTINPUTBOX"].show()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_LOCALIDTEXTINPUTBOX"].updateText(text = "")
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_LOCALIDDISPLAYTEXT"].hide()
                #---BUID
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDTEXTINPUTBOX"].show()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDTEXTINPUTBOX"].updateText(text = "")
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDTEXTINPUTBOX"].deactivate()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDDISPLAYTEXT"].hide()
                #---Account Type
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPESELECTIONBOX"].show()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPESELECTIONBOX"].setSelected(itemKey = 'VIRTUAL', callSelectionUpdateFunction = False)
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPEDISPLAYTEXT"].hide()
                #---Status
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_STATUSDISPLAYTEXT"].updateText(text = "-")
                #---Trade Status
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSDISPLAYTEXT"].updateText(text = "-")
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSSWITCH"].deactivate()
                #---API & Secret Keys
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"].updateText(text = "")
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"].deactivate()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"].updateText(text = "")
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"].deactivate()
                #---Password
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].updateText(text = "")
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].activate()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDHOLDRELEASESWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDHOLDRELEASESWITCH"].deactivate()
                #---Activation
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYENTEREDKEYSBUTTON"].deactivate()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_DEACTIVATEBUTTON"].deactivate()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAFBUTTON"].deactivate()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_GENERATEAAFBUTTON"].deactivate()
                #---Add & Remove
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ADDACCOUNTBUTTON"].deactivate()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNTBUTTON"].deactivate()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNTBUTTONSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNTBUTTONSWITCH"].deactivate()
            #Assets
            if (True):
                #---Asset Data
                self.pageAuxillaryFunctions['DISPLAYASSETDATA']()
                #---Asset to Display
                self.GUIOs["ASSETS_ASSETTODISPLAYSELECTIONBOX"].deactivate()
                self.GUIOs["ASSETS_TRASNFERBALANCETEXTINPUTBOX"].updateText(text = "")
                self.GUIOs["ASSETS_TRASNFERBALANCETEXTINPUTBOX"].deactivate()
                self.GUIOs["ASSETS_TRASNFERBALANCEDEPOSITBUTTON"].deactivate()
                self.GUIOs["ASSETS_TRASNFERBALANCEWITHDRAWBUTTON"].deactivate()
                self.GUIOs["ASSETS_TRASNFERBALANCESAFETYSWITCH"].deactivate()
                #---Allocation Ratio
                self.GUIOs["ASSETS_ALLOCATIONRATIOSLIDER"].deactivate()
                self.GUIOs["ASSETS_ALLOCATIONRATIOAPPLYBUTTON"].deactivate()
            #Positions
            if (True):
                self.pageAuxillaryFunctions['SETPOSITIONSLIST']()
                self.puVar['positions_selected'] = None
                self.pageAuxillaryFunctions['ONPOSITIONSELECTIONUPDATE']()
        else:
            _account = self.puVar['accounts'][localID]
            #Account List
            if (True):
                #---Local ID
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_LOCALIDTEXTINPUTBOX"].hide()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_LOCALIDDISPLAYTEXT"].updateText(text = localID)
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_LOCALIDDISPLAYTEXT"].show()
                #---BUID
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDTEXTINPUTBOX"].hide()
                _buid = _account['buid']
                if (_buid == None): self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDDISPLAYTEXT"].updateText(text = "-")
                else:               self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDDISPLAYTEXT"].updateText(text = str(_account['buid']))
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_BINANCEUIDDISPLAYTEXT"].show()
                #---Account Type
                _accountType = _account['accountType']
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPESELECTIONBOX"].hide()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPEDISPLAYTEXT"].show()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACCOUNTTYPEDISPLAYTEXT"].updateText(text = _accountType)
                #---Status
                _status = _account['status']
                if   (_status == 'INACTIVE'): self.GUIOs["ACCOUNTSINFORMATION&CONTROL_STATUSDISPLAYTEXT"].updateText(text = _account['status'], textStyle = 'RED_LIGHT')
                elif (_status == 'ACTIVE'):   self.GUIOs["ACCOUNTSINFORMATION&CONTROL_STATUSDISPLAYTEXT"].updateText(text = _account['status'], textStyle = 'GREEN_LIGHT')
                #---Trade Status
                _tradeStatus = _account['tradeStatus']
                if (_tradeStatus == False): self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSDISPLAYTEXT"].updateText(text = "FALSE", textStyle = 'RED_LIGHT')
                else:                       self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSDISPLAYTEXT"].updateText(text = "TRUE",  textStyle = 'GREEN_LIGHT')
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSSWITCH"].setStatus(status = _account['tradeStatus'], callStatusUpdateFunction = False)
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSSWITCH"].activate()
                #---API & Secret Keys
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"].updateText(text    = "")
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"].updateText(text = "")
                if (_accountType == 'VIRTUAL'):
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"].deactivate()
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"].deactivate()
                elif (_accountType == 'ACTUAL'):
                    if (_status == 'ACTIVE'):
                        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"].deactivate()
                        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"].deactivate()
                    else:
                        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"].activate()
                        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"].activate()
                #---Password
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].updateText(text = "")
                if (localID in self.puVar['accounts_passwords']):
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].deactivate()
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDHOLDRELEASESWITCH"].setStatus(status = True, callStatusUpdateFunction = False)
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDHOLDRELEASESWITCH"].activate()
                else:
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].activate()
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDHOLDRELEASESWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDHOLDRELEASESWITCH"].deactivate()
                #---Activation
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYENTEREDKEYSBUTTON"].deactivate()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_GENERATEAAFBUTTON"].deactivate()
                if ((_accountType == 'ACTUAL') and (_status == 'INACTIVE')): self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAFBUTTON"].activate()
                else:                                                        self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAFBUTTON"].deactivate()
                if ((_accountType == 'ACTUAL') and (_status == 'ACTIVE')): self.GUIOs["ACCOUNTSINFORMATION&CONTROL_DEACTIVATEBUTTON"].activate()
                else:                                                      self.GUIOs["ACCOUNTSINFORMATION&CONTROL_DEACTIVATEBUTTON"].deactivate()
                #---Add & Remove
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ADDACCOUNTBUTTON"].deactivate()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNTBUTTON"].deactivate()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNTBUTTONSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNTBUTTONSWITCH"].activate()
            #Assets
            if (True):
                #---Asset Data
                self.pageAuxillaryFunctions['DISPLAYASSETDATA']()
                #---Asset to Display
                self.GUIOs["ASSETS_ASSETTODISPLAYSELECTIONBOX"].activate()
                self.GUIOs["ASSETS_TRASNFERBALANCETEXTINPUTBOX"].deactivate()
                self.GUIOs["ASSETS_TRASNFERBALANCEDEPOSITBUTTON"].deactivate()
                self.GUIOs["ASSETS_TRASNFERBALANCEWITHDRAWBUTTON"].deactivate()
                self.GUIOs["ASSETS_TRASNFERBALANCESAFETYSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
                if (_account['accountType'] == 'VIRTUAL'): self.GUIOs["ASSETS_TRASNFERBALANCESAFETYSWITCH"].activate()
                else:                                      self.GUIOs["ASSETS_TRASNFERBALANCESAFETYSWITCH"].deactivate()
                #---Allocation Ratio
                self.GUIOs["ASSETS_ALLOCATIONRATIOSLIDER"].activate()
                self.GUIOs["ASSETS_ALLOCATIONRATIOAPPLYBUTTON"].deactivate()
            #Positions
            if (True):
                self.pageAuxillaryFunctions['SETPOSITIONSLIST']()
                self.puVar['positions_selected'] = None
                self.pageAuxillaryFunctions['ONPOSITIONSELECTIONUPDATE']()
    def __checkIfCanActivateAccount():
        _enteredKey_api    = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"].getText()
        _enteredKey_secret = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"].getText()
        if ((len(_enteredKey_api) == 64) and (len(_enteredKey_secret) == 64)): 
            self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYENTEREDKEYSBUTTON"].activate()
            self.GUIOs["ACCOUNTSINFORMATION&CONTROL_GENERATEAAFBUTTON"].activate()
        else:                                                                  
            self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYENTEREDKEYSBUTTON"].deactivate()
            self.GUIOs["ACCOUNTSINFORMATION&CONTROL_GENERATEAAFBUTTON"].deactivate()
    auxFunctions['CHECKIFCANADDACCOUNT']      = __checkIfCanAddAccount
    auxFunctions['ONACCOUNTSELECTIONUPDATE']  = __onAccountSelectionUpdate
    auxFunctions['CHECKIFCANACTIVATEACCOUNT'] = __checkIfCanActivateAccount

    #<Assets>
    def __displayAssetData():
        _localID = self.puVar['accounts_selected']
        if (_localID == None):
            self.GUIOs["ASSETS_MARGINBALANCEDISPLAYTEXT"].updateText(text         = "-")
            self.GUIOs["ASSETS_WALLETBALANCEDISPLAYTEXT"].updateText(text         = "-")
            self.GUIOs["ASSETS_AVAILABLEBALANCEDISPLAYTEXT"].updateText(text      = "-")
            self.GUIOs["ASSETS_MARGINDISPLAYTEXT"].updateText(text                = "-")
            self.GUIOs["ASSETS_ALLOCATABLEBALANCEDISPLAYTEXT"].updateText(text    = "-")
            self.GUIOs["ASSETS_POSITIONINITIALMARGINDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["ASSETS_ALLOCATEDBALANCEDISPLAYTEXT"].updateText(text      = "-")
            self.GUIOs["ASSETS_UNREALIZEDPNLDISPLAYTEXT"].updateText(text         = "-")
            self.GUIOs["ASSETS_COMMITMENTRATEDISPLAYTEXT"].updateText(text        = "-")
            self.GUIOs["ASSETS_RISKLEVELDISPLAYTEXT"].updateText(text             = "-")
            self.GUIOs["ASSETS_BASEASSUMEDRATIODISPLAYTEXT"].updateText(text      = "-")
            self.GUIOs["ASSETS_WEIGHTEDASSUMEDRATIODISPLAYTEXT"].updateText(text  = "-")
            self.GUIOs["ASSETS_ALLOCATIONRATIOSLIDER"].setSliderValue(newValue = 50, callValueUpdateFunction = False)
            self.GUIOs["ASSETS_ALLOCATIONRATIODISPLAYTEXT"].updateText("-")
        else:
            _asset_selected = self.GUIOs["ASSETS_ASSETTODISPLAYSELECTIONBOX"].getSelected()
            _assetData = self.puVar['accounts'][_localID]['assets'][_asset_selected]
            #Margin Balance
            if (_assetData['marginBalance'] == None): self.GUIOs["ASSETS_MARGINBALANCEDISPLAYTEXT"].updateText(text = "-")
            else:                                     self.GUIOs["ASSETS_MARGINBALANCEDISPLAYTEXT"].updateText(text = atmEta_Auxillaries.floatToString(number = _assetData['marginBalance'], precision = _ASSETPRECISIONS[_asset_selected]))
            #Wallet Balance
            if (_assetData['walletBalance'] == None): self.GUIOs["ASSETS_WALLETBALANCEDISPLAYTEXT"].updateText(text = "- / - / -")
            else:
                _wb_total_str    = atmEta_Auxillaries.floatToString(number = _assetData['walletBalance'],         precision = _ASSETPRECISIONS[_asset_selected])
                _wb_cross_str    = atmEta_Auxillaries.floatToString(number = _assetData['crossWalletBalance'],    precision = _ASSETPRECISIONS[_asset_selected])
                _wb_isolated_str = atmEta_Auxillaries.floatToString(number = _assetData['isolatedWalletBalance'], precision = _ASSETPRECISIONS[_asset_selected])
                self.GUIOs["ASSETS_WALLETBALANCEDISPLAYTEXT"].updateText(text = "{:s} / {:s} / {:s}".format(_wb_total_str, _wb_cross_str, _wb_isolated_str))
            #Available Balance
            if (_assetData['availableBalance'] == None) :self.GUIOs["ASSETS_AVAILABLEBALANCEDISPLAYTEXT"].updateText(text = "-")
            else:                                        self.GUIOs["ASSETS_AVAILABLEBALANCEDISPLAYTEXT"].updateText(text = atmEta_Auxillaries.floatToString(number = _assetData['availableBalance'], precision = _ASSETPRECISIONS[_asset_selected]))
            #Margin
            if (_assetData['crossPositionInitialMargin'] == None): self.GUIOs["ASSETS_MARGINDISPLAYTEXT"].updateText(text = "- / - / -")
            else:
                _mrgn_pi_str    = atmEta_Auxillaries.floatToString(number = _assetData['crossPositionInitialMargin']+_assetData['isolatedPositionInitialMargin'], precision = _ASSETPRECISIONS[_asset_selected])
                _mrgn_oo_str    = atmEta_Auxillaries.floatToString(number = _assetData['openOrderInitialMargin'],                                                 precision = _ASSETPRECISIONS[_asset_selected])
                _mrgn_maint_str = atmEta_Auxillaries.floatToString(number = _assetData['crossMaintenanceMargin'],                                                 precision = _ASSETPRECISIONS[_asset_selected])
                self.GUIOs["ASSETS_MARGINDISPLAYTEXT"].updateText(text = "{:s} / {:s} / {:s}".format(_mrgn_pi_str, _mrgn_oo_str, _mrgn_maint_str))
            #Allocatable Balance
            if (_assetData['allocatableBalance'] == None): self.GUIOs["ASSETS_ALLOCATABLEBALANCEDISPLAYTEXT"].updateText(text = "-")
            else:                                          self.GUIOs["ASSETS_ALLOCATABLEBALANCEDISPLAYTEXT"].updateText(text = atmEta_Auxillaries.floatToString(number = _assetData['allocatableBalance'], precision = _ASSETPRECISIONS[_asset_selected]))
            #Position Initial Margin
            if (_assetData['crossPositionInitialMargin'] == None): self.GUIOs["ASSETS_POSITIONINITIALMARGINDISPLAYTEXT"].updateText(text = "- / -")
            else:
                _piMrgn_cross    = atmEta_Auxillaries.floatToString(number = _assetData['crossPositionInitialMargin'], precision = _ASSETPRECISIONS[_asset_selected])
                _piMrgn_isolated = atmEta_Auxillaries.floatToString(number = _assetData['isolatedPositionInitialMargin'], precision = _ASSETPRECISIONS[_asset_selected])
                self.GUIOs["ASSETS_POSITIONINITIALMARGINDISPLAYTEXT"].updateText(text = "{:s} / {:s}".format(_piMrgn_cross, _piMrgn_isolated))
            #Allocated Balance
            self.GUIOs["ASSETS_ALLOCATEDBALANCEDISPLAYTEXT"].updateText(text = atmEta_Auxillaries.floatToString(number = _assetData['allocatedBalance'], precision = _ASSETPRECISIONS[_asset_selected]))
            #Unrealized PNL
            if (_assetData['unrealizedPNL'] == None): self.GUIOs["ASSETS_UNREALIZEDPNLDISPLAYTEXT"].updateText(text = "- / - / -", textStyle = 'DEFAULT')
            else:
                if (_assetData['unrealizedPNL'] == None): _unPNL_total_str = "-"; _unPNL_total_strColor = 'DEFAULT'
                else:                                             
                    if   (0 < _assetData['unrealizedPNL']):  _unPNL_total_strColor = 'GREEN_LIGHT'
                    elif (_assetData['unrealizedPNL'] < 0):  _unPNL_total_strColor = 'RED_LIGHT'
                    elif (_assetData['unrealizedPNL'] == 0): _unPNL_total_strColor = 'DEFAULT'
                    _unPNL_total_str = atmEta_Auxillaries.floatToString(number = _assetData['unrealizedPNL'], precision = _ASSETPRECISIONS[_asset_selected])
                    if (0 < _assetData['unrealizedPNL']): _unPNL_total_str = "+"+_unPNL_total_str
                if (_assetData['crossUnrealizedPNL'] == None): _unPNL_cross_str = "-"; _unPNL_cross_strColor = 'DEFAULT'
                else:                                             
                    if   (0 < _assetData['crossUnrealizedPNL']):  _unPNL_cross_strColor = 'GREEN_LIGHT'
                    elif (_assetData['crossUnrealizedPNL'] < 0):  _unPNL_cross_strColor = 'RED_LIGHT'
                    elif (_assetData['crossUnrealizedPNL'] == 0): _unPNL_cross_strColor = 'DEFAULT'
                    _unPNL_cross_str = atmEta_Auxillaries.floatToString(number = _assetData['crossUnrealizedPNL'], precision = _ASSETPRECISIONS[_asset_selected])
                    if (0 < _assetData['crossUnrealizedPNL']): _unPNL_cross_str = "+"+_unPNL_cross_str
                if (_assetData['isolatedUnrealizedPNL'] == None): _unPNL_isolated_str = "-"; _unPNL_isolated_strColor = 'DEFAULT'
                else:                                             
                    if   (0 < _assetData['isolatedUnrealizedPNL']):  _unPNL_isolated_strColor = 'GREEN_LIGHT'
                    elif (_assetData['isolatedUnrealizedPNL'] < 0):  _unPNL_isolated_strColor = 'RED_LIGHT'
                    elif (_assetData['isolatedUnrealizedPNL'] == 0): _unPNL_isolated_strColor = 'DEFAULT'
                    _unPNL_isolated_str = atmEta_Auxillaries.floatToString(number = _assetData['isolatedUnrealizedPNL'], precision = _ASSETPRECISIONS[_asset_selected])
                    if (0 < _assetData['isolatedUnrealizedPNL']): _unPNL_isolated_str = "+"+_unPNL_isolated_str
                _dtPair = ((_unPNL_total_str,     _unPNL_total_strColor), 
                            (" / ",               'DEFAULT'), 
                            (_unPNL_cross_str,    _unPNL_cross_strColor), 
                            (" / ",               'DEFAULT'), 
                            (_unPNL_isolated_str, _unPNL_isolated_strColor))
                _displayTextStyle = list(); _displayText = ""
                for _dt, _dts in _dtPair: _displayTextStyle.append(((len(_displayText), len(_displayText)+len(_dt)), _dts)); _displayText += _dt
                self.GUIOs["ASSETS_UNREALIZEDPNLDISPLAYTEXT"].updateText(text = _displayText, textStyle = _displayTextStyle)
            #Commitment Rate
            _cr = _assetData['commitmentRate']
            if (_cr == None): self.GUIOs["ASSETS_COMMITMENTRATEDISPLAYTEXT"].updateText(text = "N/A", textStyle = 'DEFAULT')
            else:
                if   (0.00 <= _cr) and (_cr <  0.30): _textColor = 'GREEN_DARK'
                elif (0.30 <= _cr) and (_cr <  0.50): _textColor = 'GREEN_LIGHT'
                elif (0.50 <= _cr) and (_cr <  0.70): _textColor = 'YELLOW'
                elif (0.70 <= _cr) and (_cr <  0.80): _textColor = 'ORANGE_LIGHT'
                elif (0.80 <= _cr) and (_cr <  0.90): _textColor = 'RED_LIGHT'
                elif (0.90 <= _cr) and (_cr <= 1.00): _textColor = 'RED'
                else:                                 _textColor = 'VIOLET_LIGHT'
                self.GUIOs["ASSETS_COMMITMENTRATEDISPLAYTEXT"].updateText(text = "{:.3f} %".format(_cr*100), textStyle = _textColor)
            #Risk Level
            _rl = _assetData['riskLevel']
            if (_rl == None): self.GUIOs["ASSETS_RISKLEVELDISPLAYTEXT"].updateText(text = "N/A", textStyle = 'DEFAULT')
            else:
                if   (0.00 <= _rl) and (_rl <  0.30): _textColor = 'GREEN_DARK'
                elif (0.30 <= _rl) and (_rl <  0.50): _textColor = 'GREEN_LIGHT'
                elif (0.50 <= _rl) and (_rl <  0.70): _textColor = 'ORANGE_LIGHT'
                elif (0.70 <= _rl) and (_rl <  0.90): _textColor = 'RED_LIGHT'
                elif (0.90 <= _rl) and (_rl <= 1.00): _textColor = 'RED'
                self.GUIOs["ASSETS_RISKLEVELDISPLAYTEXT"].updateText(text = "{:.3f} %".format(_rl*100), textStyle = _textColor)
            #Base Assumption Rate
            _ar_base = _assetData['assumedRatio']
            if   (0.00 <= _ar_base) and (_ar_base <  0.10): _textColor = 'GREEN_DARK'
            elif (0.10 <= _ar_base) and (_ar_base <  0.20): _textColor = 'GREEN_LIGHT'
            elif (0.20 <= _ar_base) and (_ar_base <  0.30): _textColor = 'BLUE_LIGHT'
            elif (0.30 <= _ar_base) and (_ar_base <  0.40): _textColor = 'YELLOW'
            elif (0.40 <= _ar_base) and (_ar_base <  0.50): _textColor = 'ORANGE_LIGHT'
            elif (0.50 <= _ar_base) and (_ar_base <= 0.60): _textColor = 'RED_LIGHT'
            elif (0.60 <= _ar_base):                        _textColor = 'RED'
            self.GUIOs["ASSETS_BASEASSUMEDRATIODISPLAYTEXT"].updateText(text = "{:.3f} %".format(_ar_base*100), textStyle = _textColor)
            #Weighted Assumption Rate
            _ar_weighted = _assetData['weightedAssumedRatio']
            if   (0.00 <= _ar_weighted) and (_ar_weighted <  0.10): _textColor = 'GREEN_DARK'
            elif (0.10 <= _ar_weighted) and (_ar_weighted <  0.20): _textColor = 'GREEN_LIGHT'
            elif (0.20 <= _ar_weighted) and (_ar_weighted <  0.30): _textColor = 'BLUE_LIGHT'
            elif (0.30 <= _ar_weighted) and (_ar_weighted <  0.40): _textColor = 'YELLOW'
            elif (0.40 <= _ar_weighted) and (_ar_weighted <  0.50): _textColor = 'ORANGE_LIGHT'
            elif (0.50 <= _ar_weighted) and (_ar_weighted <= 0.60): _textColor = 'RED_LIGHT'
            elif (0.60 <= _ar_weighted):                            _textColor = 'RED'
            self.GUIOs["ASSETS_WEIGHTEDASSUMEDRATIODISPLAYTEXT"].updateText(text = "{:.3f} %".format(_ar_weighted*100), textStyle = _textColor)
            #Allocation Ratio
            self.GUIOs["ASSETS_ALLOCATIONRATIOSLIDER"].setSliderValue(newValue = _assetData['allocationRatio']*100, callValueUpdateFunction = True)
            self.GUIOs["ASSETS_ALLOCATIONRATIODISPLAYTEXT"].updateText(text = "{:.1f} %".format(_assetData['allocationRatio']*100))
    def __sendBalanceTransferRequest(amountToTransfer):
        #Password
        localID = self.puVar['accounts_selected']
        if (localID in self.puVar['accounts_passwords']): password = self.puVar['accounts_passwords'][localID]
        else:                                             password = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
        #Asset
        asset = self.GUIOs["ASSETS_ASSETTODISPLAYSELECTIONBOX"].getSelected()
        #Request Dispatch
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', 
                          functionID = 'transferBalance', 
                          functionParams = {'localID':   localID,
                                            'password':  password,
                                            'asset':     asset,
                                            'amount':    amountToTransfer}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONACCOUNTCONTROLREQUESTRESPONSE'])
        #Buttons Temporary Deactivation
        self.GUIOs["ASSETS_TRASNFERBALANCEDEPOSITBUTTON"].deactivate()
        self.GUIOs["ASSETS_TRASNFERBALANCEWITHDRAWBUTTON"].deactivate()
    auxFunctions['DISPLAYASSETDATA']           = __displayAssetData
    auxFunctions['SENDBALANCETRANSFERREQUEST'] = __sendBalanceTransferRequest

    #<Positions>
    def __setPositionsList():
        displayMode = self.GUIOs["POSITIONS_DISPLAYMODESELECTIONBOX"].getSelected()
        localID     = self.puVar['accounts_selected']
        if (localID == None):
            if   (displayMode == 'BASIC'):  self.GUIOs["POSITIONS_BASICMODESELECTIONBOX"].clearSelectionList()
            elif (displayMode == 'TRADER'): self.GUIOs["POSITIONS_TRADERMODESELECTIONBOX"].clearSelectionList()
            elif (displayMode == 'DETAIL'): self.GUIOs["POSITIONS_DETAILMODESELECTIONBOX"].clearSelectionList()
        else:
            if (displayMode == 'BASIC'):
                positions = self.puVar['accounts'][localID]['positions']
                nPositions = len(positions)
                positions_selectionList = dict()
                for positionIndex, symbol in enumerate(positions):
                    _position = positions[symbol]
                    #[0]: Index
                    _index_str = "{:d} / {:d}".format(positionIndex+1, nPositions)
                    #[1]: Symbol
                    _symbol_str = symbol
                    #[2]: Trading
                    if (_position['tradeStatus'] == True): _trading_str = 'TRUE';  _trading_str_color = 'GREEN_LIGHT'
                    else:                                  _trading_str = 'FALSE'; _trading_str_color = 'RED_LIGHT'
                    #[3]: Leverage
                    if (_position['leverage'] == None): _leverage_str = "-"
                    else:                               _leverage_str = str(_position['leverage'])
                    #[4]: Margin Mode
                    if   (_position['isolated'] == True):  _marginMode_str = 'ISOLATED'
                    elif (_position['isolated'] == False): _marginMode_str = 'CROSSED'
                    elif (_position['isolated'] == None):  _marginMode_str = '-'
                    #[5]: Quantity
                    if (_position['quantity'] == None): _quantity_str = "-"
                    else:                               _quantity_str = atmEta_Auxillaries.floatToString(number = _position['quantity'], precision = _position['precisions']['quantity'])
                    #[6]: Entry Price
                    if (_position['entryPrice'] == None): _entryPrice_str = "-"
                    else:                                 _entryPrice_str = atmEta_Auxillaries.floatToString(number = _position['entryPrice'], precision = _position['precisions']['price'])
                    #[7]: Current Price
                    if (_position['currentPrice'] == None): _currentPrice_str = "-"; _currentPrice_str_color = 'DEFAULT'
                    else:
                        if (_position['entryPrice'] == None): _currentPrice_str = atmEta_Auxillaries.floatToString(number = _position['currentPrice'], precision = _position['precisions']['price']); _currentPrice_str_color = 'DEFAULT'
                        else:
                            _pDifferencePerc = round((_position['currentPrice']/_position['entryPrice']-1)*100, 3)
                            if   (_pDifferencePerc < 0):  _currentPrice_str = "{:s} [{:.3f} %]".format(atmEta_Auxillaries.floatToString(number  = _position['currentPrice'], precision = _position['precisions']['price']), _pDifferencePerc); _currentPrice_str_color = 'RED_LIGHT'
                            elif (_pDifferencePerc == 0): _currentPrice_str = "{:s} [{:.3f} %]".format(atmEta_Auxillaries.floatToString(number  = _position['currentPrice'], precision = _position['precisions']['price']), _pDifferencePerc); _currentPrice_str_color = 'DEFAULT'
                            elif (0 < _pDifferencePerc):  _currentPrice_str = "{:s} [+{:.3f} %]".format(atmEta_Auxillaries.floatToString(number = _position['currentPrice'], precision = _position['precisions']['price']), _pDifferencePerc); _currentPrice_str_color = 'GREEN_LIGHT'
                    #[8]: Liquidation Price
                    if (_position['liquidationPrice'] == None): _liquidationPrice_str = "-"
                    else:                                       _liquidationPrice_str = atmEta_Auxillaries.floatToString(number = _position['liquidationPrice'], precision = _position['precisions']['price'])
                    #[9]: UnrealizedPNL
                    if ((_position['unrealizedPNL'] == None) or (_position['positionInitialMargin'] == None) or (_position['positionInitialMargin'] == 0)):
                        _unrealizedPNL_str = "-"; _unrealizedPNL_str_color = 'DEFAULT'
                    else:                                         
                        _roi = round(_position['unrealizedPNL']/_position['positionInitialMargin']*100, 3)
                        if   (_position['unrealizedPNL'] < 0):  _unrealizedPNL_str = "{:s} [{:.3f} %]".format(atmEta_Auxillaries.floatToString(number  = _position['unrealizedPNL'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']]), _roi); _unrealizedPNL_str_color = 'RED_LIGHT'
                        elif (_position['unrealizedPNL'] == 0): _unrealizedPNL_str = "{:s} [{:.3f} %]".format(atmEta_Auxillaries.floatToString(number  = _position['unrealizedPNL'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']]), _roi); _unrealizedPNL_str_color = 'DEFAULT'
                        elif (0 < _position['unrealizedPNL']):  _unrealizedPNL_str = "{:s} [+{:.3f} %]".format(atmEta_Auxillaries.floatToString(number = _position['unrealizedPNL'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']]), _roi); _unrealizedPNL_str_color = 'GREEN_LIGHT'
                    #[10]: Assumed Ratio
                    if (_position['assumedRatio'] == None): _assumedRatio_str = "-"
                    else:                                   _assumedRatio_str = "{:.3f} %".format(_position['assumedRatio']*100)
                    #[11]: Allocated Balance
                    if (_position['assumedRatio'] == None): _allocatedBalance_str = "-"
                    else:                                   _allocatedBalance_str = atmEta_Auxillaries.floatToString(number = _position['allocatedBalance'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']])
                    #[12]: Commitment Rate
                    _cr = _position['commitmentRate']
                    if (_cr == None): _commitmentRate_str = "N/A"; _commitmentRate_str_color = 'DEFAULT'
                    else:
                        _commitmentRate_str = "{:.3f} %".format(_cr*100)
                        if   (0.00 <= _cr) and (_cr <  0.30): _commitmentRate_str_color = 'GREEN_DARK'
                        elif (0.30 <= _cr) and (_cr <  0.50): _commitmentRate_str_color = 'GREEN_LIGHT'
                        elif (0.50 <= _cr) and (_cr <  0.70): _commitmentRate_str_color = 'YELLOW'
                        elif (0.70 <= _cr) and (_cr <  0.80): _commitmentRate_str_color = 'ORANGE_LIGHT'
                        elif (0.80 <= _cr) and (_cr <  0.90): _commitmentRate_str_color = 'RED_LIGHT'
                        elif (0.90 <= _cr) and (_cr <= 1.00): _commitmentRate_str_color = 'RED'
                        else:                                 _commitmentRate_str_color = 'VIOLET_LIGHT'
                    #[13]: Risk Level
                    _rl = _position['riskLevel']
                    if (_rl == None): _riskLevel_str = "N/A"; _riskLevel_str_color = 'DEFAULT'
                    else:
                        _riskLevel_str = "{:.3f} %".format(_rl*100)
                        if   (0.00 <= _rl) and (_rl <  0.30): _riskLevel_str_color = 'GREEN_DARK'
                        elif (0.30 <= _rl) and (_rl <  0.50): _riskLevel_str_color = 'GREEN_LIGHT'
                        elif (0.50 <= _rl) and (_rl <  0.70): _riskLevel_str_color = 'ORANGE_LIGHT'
                        elif (0.70 <= _rl) and (_rl <  0.90): _riskLevel_str_color = 'RED_LIGHT'
                        elif (0.90 <= _rl) and (_rl <= 1.00): _riskLevel_str_color = 'RED'
                    #Finally
                    positions_selectionList[symbol] = [{'text': _index_str,},
                                                       {'text': _symbol_str,},
                                                       {'text': _trading_str, 'textStyles': [('all', _trading_str_color),]},
                                                       {'text': _leverage_str,},
                                                       {'text': _marginMode_str,},
                                                       {'text': _quantity_str,},
                                                       {'text': _entryPrice_str,},
                                                       {'text': _currentPrice_str, 'textStyles': [('all', _currentPrice_str_color),]},
                                                       {'text': _liquidationPrice_str,},
                                                       {'text': _unrealizedPNL_str, 'textStyles': [('all', _unrealizedPNL_str_color),]},
                                                       {'text': _assumedRatio_str,},
                                                       {'text': _allocatedBalance_str,},
                                                       {'text': _commitmentRate_str, 'textStyles': [('all', _commitmentRate_str_color),]},
                                                       {'text': _riskLevel_str, 'textStyles': [('all', _riskLevel_str_color),],}]
                self.GUIOs["POSITIONS_BASICMODESELECTIONBOX"].setSelectionList(selectionList = positions_selectionList, displayTargets = 'all', keepSelected = False, callSelectionUpdateFunction = False)
            elif (displayMode == 'TRADER'): 
                positions = self.puVar['accounts'][localID]['positions']
                nPositions = len(positions)
                positions_selectionList = dict()
                for positionIndex, symbol in enumerate(positions):
                    _position = positions[symbol]
                    #[0]: Index
                    _index_str = "{:d} / {:d}".format(positionIndex+1, nPositions)
                    #[1]: Symbol
                    _symbol_str = symbol
                    #[2]: Tradable
                    if (_position['tradable'] == True): _tradable_str = 'TRUE';  _tradable_str_color = 'GREEN_LIGHT'
                    else:                               _tradable_str = 'FALSE'; _tradable_str_color = 'RED_LIGHT'
                    #[3]: Trading
                    if (_position['tradeStatus'] == True): _trading_str = 'TRUE';  _trading_str_color = 'GREEN_LIGHT'
                    else:                                  _trading_str = 'FALSE'; _trading_str_color = 'RED_LIGHT'
                    #[4]: Reduce Only
                    if (_position['reduceOnly'] == True): _reduceOnly_str = 'TRUE';  _reduceOnly_str_color = 'ORANGE_LIGHT'
                    else:                                 _reduceOnly_str = 'FALSE'; _reduceOnly_str_color = 'GREEN_LIGHT'
                    #[5]: Currency Analysis Code
                    if (_position['currencyAnalysisCode'] == None): _currencyAnalysisCode_str = "-"
                    else:                                           _currencyAnalysisCode_str = _position['currencyAnalysisCode']
                    #[6]: Trade Configuration Code
                    if (_position['tradeConfigurationCode'] == None): _tradeConfigurationCode_str = "-"
                    else:                                             _tradeConfigurationCode_str = _position['tradeConfigurationCode']
                    #[7]: Priority
                    _priority_str = str(_position['priority'])
                    #[8]: Assumed Ratio
                    _assumedRatio_str = "{:.3f} %".format(_position['assumedRatio']*100)
                    #[9]: Max Allocated Balance
                    if (_position['maxAllocatedBalance'] == float('inf')): _maxAllocatedBalance_str = 'INF'
                    else:                                                  _maxAllocatedBalance_str = atmEta_Auxillaries.floatToString(number = _position['maxAllocatedBalance'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']])
                    #[10]: Trade Control
                    _tradeControl_str = json.dumps(_position['tradeControlTracker'])
                    #[11]: Abrupt Clearing Records
                    if (len(_position['abruptClearingRecords']) == 0): _abruptClearingRecords_str = "-"
                    else:                                              _abruptClearingRecords_str = str(_position['abruptClearingRecords'])
                    #Finally
                    positions_selectionList[symbol] = [{'text': _index_str},
                                                       {'text': _symbol_str},
                                                       {'text': _tradable_str, 'textStyles': [('all', _tradable_str_color),]},
                                                       {'text': _trading_str, 'textStyles': [('all', _trading_str_color),]},
                                                       {'text': _reduceOnly_str, 'textStyles': [('all', _reduceOnly_str_color),]},
                                                       {'text': _currencyAnalysisCode_str},
                                                       {'text': _tradeConfigurationCode_str},
                                                       {'text': _priority_str},
                                                       {'text': _assumedRatio_str},
                                                       {'text': _maxAllocatedBalance_str},
                                                       {'text': _tradeControl_str},
                                                       {'text': _abruptClearingRecords_str}]
                self.GUIOs["POSITIONS_TRADERMODESELECTIONBOX"].setSelectionList(selectionList = positions_selectionList, displayTargets = 'all', keepSelected = False, callSelectionUpdateFunction = False)
            elif (displayMode == 'DETAIL'): 
                positions = self.puVar['accounts'][localID]['positions']
                nPositions = len(positions)
                positions_selectionList = dict()
                for positionIndex, symbol in enumerate(positions):
                    _position = positions[symbol]
                    #[0]:  Index
                    _index_str = "{:d} / {:d}".format(positionIndex+1, nPositions)
                    #[1]:  Symbol
                    _symbol_str = symbol
                    #[2]:  Tradable
                    if (_position['tradable'] == True): _tradable_str = 'TRUE';  _tradable_str_color = 'GREEN_LIGHT'
                    else:                               _tradable_str = 'FALSE'; _tradable_str_color = 'RED_LIGHT'
                    #[3]:  Trading
                    if (_position['tradeStatus'] == True): _trading_str = 'TRUE';  _trading_str_color = 'GREEN_LIGHT'
                    else:                                  _trading_str = 'FALSE'; _trading_str_color = 'RED_LIGHT'
                    #[4]:  Reduce Only
                    if (_position['reduceOnly'] == True): _reduceOnly_str = 'TRUE';  _reduceOnly_str_color = 'ORANGE_LIGHT'
                    else:                                 _reduceOnly_str = 'FALSE'; _reduceOnly_str_color = 'GREEN_LIGHT'
                    #[5]:  Leverage
                    if (_position['leverage'] == None): _leverage_str = "-"
                    else:                               _leverage_str = str(_position['leverage'])
                    #[6]:  Margin Mode
                    if   (_position['isolated'] == True):  _marginMode_str = 'ISOLATED'
                    elif (_position['isolated'] == False): _marginMode_str = 'CROSSED'
                    elif (_position['isolated'] == None):  _marginMode_str = '-'
                    #[7]:  Quantity
                    if (_position['quantity'] == None): _quantity_str = "-"
                    else:                               _quantity_str = atmEta_Auxillaries.floatToString(number = _position['quantity'], precision = _position['precisions']['quantity'])
                    #[8]:  Isolated Wallet Balance
                    if (_position['isolatedWalletBalance'] == None): _isolatedWalletBalance_str = "-"
                    else:                                            _isolatedWalletBalance_str = atmEta_Auxillaries.floatToString(number = _position['isolatedWalletBalance'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']])
                    #[9]:  Position Initial Margin
                    if (_position['positionInitialMargin'] == None): _positionInitialMargin_str = "-"
                    else:                                            _positionInitialMargin_str = atmEta_Auxillaries.floatToString(number = _position['positionInitialMargin'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']])
                    #[10]: Open Order Initial Margin
                    if (_position['openOrderInitialMargin'] == None): _openOrderInitialMargin_str = "-"
                    else:                                             _openOrderInitialMargin_str = atmEta_Auxillaries.floatToString(number = _position['openOrderInitialMargin'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']])
                    #[11]: Maintenance Margin
                    if (_position['maintenanceMargin'] == None): _maintenanceMargin_str = "-"
                    else:                                        _maintenanceMargin_str = atmEta_Auxillaries.floatToString(number = _position['maintenanceMargin'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']])
                    #[12]: Entry Price
                    if (_position['entryPrice'] == None): _entryPrice_str = "-"
                    else:                                 _entryPrice_str = atmEta_Auxillaries.floatToString(number = _position['entryPrice'], precision = _position['precisions']['price'])
                    #[13]: Current Price
                    if (_position['currentPrice'] == None): _currentPrice_str = "-"; _currentPrice_str_color = 'DEFAULT'
                    else:
                        if (_position['entryPrice'] == None): _currentPrice_str = atmEta_Auxillaries.floatToString(number = _position['currentPrice'], precision = _position['precisions']['price']); _currentPrice_str_color = 'DEFAULT'
                        else:
                            _pDifferencePerc = round((_position['currentPrice']/_position['entryPrice']-1)*100, 3)
                            if   (_pDifferencePerc < 0):  _currentPrice_str = "{:s} [{:.3f} %]".format(atmEta_Auxillaries.floatToString(number  = _position['currentPrice'], precision = _position['precisions']['price']), _pDifferencePerc); _currentPrice_str_color = 'RED_LIGHT'
                            elif (_pDifferencePerc == 0): _currentPrice_str = "{:s} [{:.3f} %]".format(atmEta_Auxillaries.floatToString(number  = _position['currentPrice'], precision = _position['precisions']['price']), _pDifferencePerc); _currentPrice_str_color = 'DEFAULT'
                            elif (0 < _pDifferencePerc):  _currentPrice_str = "{:s} [+{:.3f} %]".format(atmEta_Auxillaries.floatToString(number = _position['currentPrice'], precision = _position['precisions']['price']), _pDifferencePerc); _currentPrice_str_color = 'GREEN_LIGHT'
                    #[14]: Liquidation Price
                    if (_position['liquidationPrice'] == None): _liquidationPrice_str = "-"
                    else:                                       _liquidationPrice_str = atmEta_Auxillaries.floatToString(number = _position['liquidationPrice'], precision = _position['precisions']['price'])
                    #[15]: UnrealizedPNL
                    if ((_position['unrealizedPNL'] == None) or (_position['positionInitialMargin'] == None) or (_position['positionInitialMargin'] == 0)):
                        _unrealizedPNL_str = "-"; _unrealizedPNL_str_color = 'DEFAULT'
                    else:                                         
                        _roi = round(_position['unrealizedPNL']/_position['positionInitialMargin']*100, 3)
                        if   (_position['unrealizedPNL'] < 0):  _unrealizedPNL_str = "{:s} [{:.3f} %]".format(atmEta_Auxillaries.floatToString(number  = _position['unrealizedPNL'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']]), _roi); _unrealizedPNL_str_color = 'RED_LIGHT'
                        elif (_position['unrealizedPNL'] == 0): _unrealizedPNL_str = "{:s} [{:.3f} %]".format(atmEta_Auxillaries.floatToString(number  = _position['unrealizedPNL'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']]), _roi); _unrealizedPNL_str_color = 'DEFAULT'
                        elif (0 < _position['unrealizedPNL']):  _unrealizedPNL_str = "{:s} [+{:.3f} %]".format(atmEta_Auxillaries.floatToString(number = _position['unrealizedPNL'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']]), _roi); _unrealizedPNL_str_color = 'GREEN_LIGHT'
                    #[16]: Weighted Assumed Ratio
                    _assumedRatio_str = "{:.3f} %".format(_position['assumedRatio']*100)
                    #[17]: Weighted Assumed Ratio
                    if (_position['weightedAssumedRatio'] == None): _weightedAssumedRatio_str = "N/A"
                    else:                                           _weightedAssumedRatio_str = "{:.3f} %".format(_position['weightedAssumedRatio']*100)
                    #[18]: Allocated Balance
                    _allocatedBalance_str = atmEta_Auxillaries.floatToString(number = _position['allocatedBalance'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']])
                    #[19]: Max Allocated Balance
                    if (_position['maxAllocatedBalance'] == float('inf')): _maxAllocatedBalance_str = 'INF'
                    else:                                                  _maxAllocatedBalance_str = atmEta_Auxillaries.floatToString(number = _position['maxAllocatedBalance'], precision = _ASSETPRECISIONS_XS[_position['quoteAsset']])
                    #[20]: Commitment Rate
                    _cr = _position['commitmentRate']
                    if (_cr == None): _commitmentRate_str = "N/A"; _commitmentRate_str_color = 'DEFAULT'
                    else:
                        _commitmentRate_str = "{:.3f} %".format(_cr*100)
                        if   (0.00 <= _cr) and (_cr <  0.30): _commitmentRate_str_color = 'GREEN_DARK'
                        elif (0.30 <= _cr) and (_cr <  0.50): _commitmentRate_str_color = 'GREEN_LIGHT'
                        elif (0.50 <= _cr) and (_cr <  0.70): _commitmentRate_str_color = 'YELLOW'
                        elif (0.70 <= _cr) and (_cr <  0.80): _commitmentRate_str_color = 'ORANGE_LIGHT'
                        elif (0.80 <= _cr) and (_cr <  0.90): _commitmentRate_str_color = 'RED_LIGHT'
                        elif (0.90 <= _cr) and (_cr <= 1.00): _commitmentRate_str_color = 'RED'
                        else:                                 _commitmentRate_str_color = 'VIOLET_LIGHT'
                    #[21]: Risk Level
                    _rl = _position['riskLevel']
                    if (_rl == None): _riskLevel_str = "N/A"; _riskLevel_str_color = 'DEFAULT'
                    else:
                        _riskLevel_str = "{:.3f} %".format(_rl*100)
                        if   (0.00 <= _rl) and (_rl <  0.30): _riskLevel_str_color = 'GREEN_DARK'
                        elif (0.30 <= _rl) and (_rl <  0.50): _riskLevel_str_color = 'GREEN_LIGHT'
                        elif (0.50 <= _rl) and (_rl <  0.70): _riskLevel_str_color = 'ORANGE_LIGHT'
                        elif (0.70 <= _rl) and (_rl <  0.90): _riskLevel_str_color = 'RED_LIGHT'
                        elif (0.90 <= _rl) and (_rl <= 1.00): _riskLevel_str_color = 'RED'
                    #[22]: Currency Analysis Code
                    if (_position['currencyAnalysisCode'] == None): _currencyAnalysisCode_str = "-"
                    else:                                           _currencyAnalysisCode_str = _position['currencyAnalysisCode']
                    #[23]: Trade Configuration Code
                    if (_position['tradeConfigurationCode'] == None): _tradeConfigurationCode_str = "-"
                    else:                                             _tradeConfigurationCode_str = _position['tradeConfigurationCode']
                    #[24]: Priority
                    _priority_str = str(_position['priority'])
                    #[25]: Trade Control
                    _tradeControl_str = json.dumps(_position['tradeControlTracker'])
                    #[26]: Abrupt Clearing Records
                    if (len(_position['abruptClearingRecords']) == 0): _abruptClearingRecords_str = "-"
                    else:                                              _abruptClearingRecords_str = str(_position['abruptClearingRecords'])
                    #Finally
                    positions_selectionList[symbol] = [{'text': _index_str},
                                                       {'text': _symbol_str},
                                                       {'text': _tradable_str, 'textStyles': [('all', _tradable_str_color),]},
                                                       {'text': _trading_str, 'textStyles': [('all', _trading_str_color),]},
                                                       {'text': _reduceOnly_str, 'textStyles': [('all', _reduceOnly_str_color),]},
                                                       {'text': _leverage_str,},
                                                       {'text': _marginMode_str},
                                                       {'text': _quantity_str},
                                                       {'text': _isolatedWalletBalance_str},
                                                       {'text': _positionInitialMargin_str},
                                                       {'text': _openOrderInitialMargin_str},
                                                       {'text': _maintenanceMargin_str},
                                                       {'text': _entryPrice_str},
                                                       {'text': _currentPrice_str, 'textStyles': [('all', _currentPrice_str_color),]},
                                                       {'text': _liquidationPrice_str},
                                                       {'text': _unrealizedPNL_str, 'textStyles': [('all', _unrealizedPNL_str_color),]},
                                                       {'text': _assumedRatio_str},
                                                       {'text': _weightedAssumedRatio_str},
                                                       {'text': _allocatedBalance_str},
                                                       {'text': _maxAllocatedBalance_str},
                                                       {'text': _commitmentRate_str, 'textStyles': [('all', _commitmentRate_str_color),]},
                                                       {'text': _riskLevel_str, 'textStyles': [('all', _riskLevel_str_color),],},
                                                       {'text': _currencyAnalysisCode_str},
                                                       {'text': _tradeConfigurationCode_str},
                                                       {'text': _priority_str},
                                                       {'text': _tradeControl_str},
                                                       {'text': _abruptClearingRecords_str}]
                self.GUIOs["POSITIONS_DETAILMODESELECTIONBOX"].setSelectionList(selectionList = positions_selectionList, displayTargets = 'all', keepSelected = False, callSelectionUpdateFunction = False)
        self.pageAuxillaryFunctions['APPLYPOSITIONSLISTFILTER']()
    def __applyPositionsListFilter(resetViewPosition = True):
        displayMode = self.GUIOs["POSITIONS_DISPLAYMODESELECTIONBOX"].getSelected()
        localID     = self.puVar['accounts_selected']
        if (localID != None):
            positions = self.puVar['accounts'][localID]['positions']
            #Filter Parameters
            searchText                         = self.GUIOs["POSITIONS_SEARCHTEXTINPUTBOX"].getText()
            searchType                         = self.GUIOs["POSITIONS_SEARCHTYPESELECTIONBOX"].getSelected()
            sortType                           = self.GUIOs["POSITIONS_SORTBYSELECTIONBOX"].getSelected()
            conditionType_tradeStatus          = self.GUIOs["POSITIONS_TRADESTATUSFILTERSELECTIONBOX"].getSelected()
            conditionType_tradable             = self.GUIOs["POSITIONS_TRADABLEFILTERSELECTIONBOX"].getSelected()
            conditionType_quantity             = self.GUIOs["POSITIONS_QUANTITYFILTERSELECTIONBOX"].getSelected()
            conditionType_assumedRatio         = self.GUIOs["POSITIONS_ASSUMEDRATIOFILTERSELECTIONBOX"].getSelected()
            conditionType_allocatedBalance     = self.GUIOs["POSITIONS_ALLOCATEDBALANCEFILTERSELECTIONBOX"].getSelected()
            conditionType_currencyAnalysisCode = self.GUIOs["POSITIONS_CURRENCYANALYSISCODEFILTERSELECTIONBOX"].getSelected()
            #Filtering
            _filtered = list(positions.keys())
            #---[1]: Condition Filtering - Trade Status
            if   (conditionType_tradeStatus == 'ALL'):   pass
            elif (conditionType_tradeStatus == 'TRUE'):  _filtered = [_symbol for _symbol in _filtered if (positions[_symbol]['tradeStatus'] == True)]
            elif (conditionType_tradeStatus == 'FALSE'): _filtered = [_symbol for _symbol in _filtered if (positions[_symbol]['tradeStatus'] == False)]
            #---[2]: Condition Filtering - Tradable
            if   (conditionType_tradable == 'ALL'):   pass
            elif (conditionType_tradable == 'TRUE'):  _filtered = [_symbol for _symbol in _filtered if (positions[_symbol]['tradable'] == True)]
            elif (conditionType_tradable == 'FALSE'): _filtered = [_symbol for _symbol in _filtered if (positions[_symbol]['tradable'] == False)]
            #---[3]: Condition Filtering - Quantity
            if   (conditionType_quantity == 'ALL'):     pass
            elif (conditionType_quantity == 'NONZERO'): _filtered = [_symbol for _symbol in _filtered if ((positions[_symbol]['quantity'] != None) and (positions[_symbol]['quantity'] != 0))]
            elif (conditionType_quantity == 'ZERO'):    _filtered = [_symbol for _symbol in _filtered if (positions[_symbol]['quantity'] == 0)]
            #---[4]: Condition Filtering - Assumed Balance
            if   (conditionType_assumedRatio == 'ALL'):     pass
            elif (conditionType_assumedRatio == 'NONZERO'): _filtered = [_symbol for _symbol in _filtered if (positions[_symbol]['assumedRatio'] != 0)]
            elif (conditionType_assumedRatio == 'ZERO'):    _filtered = [_symbol for _symbol in _filtered if (positions[_symbol]['assumedRatio'] == 0)]
            #---[5]: Condition Filtering - Allocated Balance
            if   (conditionType_allocatedBalance == 'ALL'):     pass
            elif (conditionType_allocatedBalance == 'NONZERO'): _filtered = [_symbol for _symbol in _filtered if (positions[_symbol]['allocatedBalance'] != 0)]
            elif (conditionType_allocatedBalance == 'ZERO'):    _filtered = [_symbol for _symbol in _filtered if (positions[_symbol]['allocatedBalance'] == 0)]
            #---[6]: Condition Filtering - Currency Analysis Code
            if   (conditionType_currencyAnalysisCode == 'ALL'):     pass
            elif (conditionType_currencyAnalysisCode == 'NONZERO'): _filtered = [_symbol for _symbol in _filtered if (0 < len([_caCode for _caCode in self.puVar['currencyAnalysis'] if (self.puVar['currencyAnalysis'][_caCode]['currencySymbol'] == _symbol)]))]
            elif (conditionType_currencyAnalysisCode == 'ZERO'):    _filtered = [_symbol for _symbol in _filtered if (len([_caCode for _caCode in self.puVar['currencyAnalysis'] if (self.puVar['currencyAnalysis'][_caCode]['currencySymbol'] == _symbol)]) == 0)]
            #---[7]: Text Filtering
            if (searchText != ""):
                if   (searchType == 'SYMBOL'): _filtered = [_symbol for _symbol in _filtered if (searchText in _symbol)]
                elif (searchType == 'CACODE'): _filtered = [_symbol for _symbol in _filtered if ((positions[_symbol]['currencyAnalysisCode']   != None) and (searchText in positions[_symbol]['currencyAnalysisCode']))]
                elif (searchType == 'TCCODE'): _filtered = [_symbol for _symbol in _filtered if ((positions[_symbol]['tradeConfigurationCode'] != None) and (searchText in positions[_symbol]['tradeConfigurationCode']))]
            #---[8]: Sorting
            if   (sortType == 'INDEX'): pass
            elif (sortType == 'SYMBOL'): _filtered.sort()
            elif (sortType == 'LEVERAGE'): 
                _forSort = list()
                for _symbol in _filtered:
                    _leverage = positions[_symbol]['leverage']
                    if (_leverage == None): _forSort.append((_symbol, float('-inf')))
                    else:                   _forSort.append((_symbol, _leverage))
                _forSort.sort(key = lambda x: x[1], reverse = True)
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'UNREALIZEDPNL'):
                _forSort = list()
                for _symbol in _filtered:
                    _unrealizedPNL = positions[_symbol]['unrealizedPNL']
                    _quantity      = positions[_symbol]['quantity']
                    if ((_quantity == None) or (_quantity == 0) or (_unrealizedPNL == None)): _forSort.append((_symbol, float('-inf')))
                    else:                                                                     _forSort.append((_symbol, _unrealizedPNL))
                _forSort.sort(key = lambda x: x[1], reverse = True)
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'ASSUMEDRATIO'): 
                _forSort = [(_symbol, positions[_symbol]['assumedRatio']) for _symbol in _filtered]
                _forSort.sort(key = lambda x: x[1], reverse = True)
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'WEIGHTEDASSUMEDRATIO'):
                _forSort = list()
                for _symbol in _filtered:
                    _weightedAssumedRatio = positions[_symbol]['weightedAssumedRatio']
                    if (_weightedAssumedRatio == None): _forSort.append((_symbol, float('-inf')))
                    else:                               _forSort.append((_symbol, _weightedAssumedRatio))
                _forSort.sort(key = lambda x: x[1], reverse = True)
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'ALLOCATEDBALANCE'): 
                _forSort = [(_symbol, positions[_symbol]['allocatedBalance']) for _symbol in _filtered]
                _forSort.sort(key = lambda x: x[1], reverse = True)
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'COMMITMENTRATE'): 
                _forSort = list()
                for _symbol in _filtered:
                    _commitmentRate = positions[_symbol]['commitmentRate']
                    if (_commitmentRate == None): _forSort.append((_symbol, float('-inf')))
                    else:                         _forSort.append((_symbol, _commitmentRate))
                _forSort.sort(key = lambda x: x[1], reverse = True)
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'RISKLEVEL'):
                _forSort = list()
                for _symbol in _filtered:
                    _riskLevel = positions[_symbol]['riskLevel']
                    if (_riskLevel == None): _forSort.append((_symbol, float('-inf')))
                    else:                    _forSort.append((_symbol, _riskLevel))
                _forSort.sort(key = lambda x: x[1], reverse = True)
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'CACODE'): 
                _forSort = [[_symbol, positions[_symbol]['currencyAnalysisCode']] for _symbol in _filtered]
                for i in range (len(_forSort)): 
                    if (_forSort[i][1] == None): _forSort[i][1] = ""
                _forSort.sort(key = lambda x: x[1])
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'TCCODE'): 
                _forSort = [[_symbol, positions[_symbol]['tradeConfigurationCode']] for _symbol in _filtered]
                for i in range (len(_forSort)): 
                    if (_forSort[i][1] == None): _forSort[i][1] = ""
                _forSort.sort(key = lambda x: x[1])
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            elif (sortType == 'PRIORITY'): 
                _forSort = [(_symbol, positions[_symbol]['priority']) for _symbol in _filtered]
                _forSort.sort(key = lambda x: x[1])
                _filtered = [_sortPair[0] for _sortPair in _forSort]
            #Finally
            if (displayMode == 'BASIC'):  self.GUIOs["POSITIONS_BASICMODESELECTIONBOX"].setDisplayTargets(displayTargets  = _filtered, resetViewPosition = resetViewPosition)
            if (displayMode == 'TRADER'): self.GUIOs["POSITIONS_TRADERMODESELECTIONBOX"].setDisplayTargets(displayTargets = _filtered, resetViewPosition = resetViewPosition)
            if (displayMode == 'DETAIL'): self.GUIOs["POSITIONS_DETAILMODESELECTIONBOX"].setDisplayTargets(displayTargets = _filtered, resetViewPosition = resetViewPosition)
    def __onPositionSelectionUpdate():
        _displayMode = self.GUIOs["POSITIONS_DISPLAYMODESELECTIONBOX"].getSelected()
        if (_displayMode == 'BASIC'):
            self.pageAuxillaryFunctions['CHECKIFCANFORCECLEARPOSITION']()
        elif (_displayMode == 'TRADER'):
            _positionSymbol = self.puVar['positions_selected']
            self.pageAuxillaryFunctions['SETCURRENCYANALYSISLIST']()
            if (_positionSymbol == None):
                #Old
                self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTOLD"].updateText(text = "-")
                self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTOLD"].updateText(text = "-")
                self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTOLD"].updateText(text = "-")
                self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTOLD"].updateText(text = "-")
                self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTOLD"].updateText(text = "-")
                self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSVALUETEXT"].updateText(text = "-")
                self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
                self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSSWITCH"].deactivate()
                self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYVALUETEXT"].updateText(text = "-")
                self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
                self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYSWITCH"].deactivate()
                #New
                self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTNEW"].updateText(text = "-")
                self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTNEW"].updateText(text = "")
                self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTNEW"].deactivate()
                self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTNEW"].updateText(text = "")
                self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTNEW"].deactivate()
                self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTNEW"].updateText(text = "")
                self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTNEW"].deactivate()
                self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEUNITTEXT"].updateText(text = "-")
                #Apply Button
                self.GUIOs["POSITIONS_TRADERMODEAPPLYBUTTON"].deactivate()
            else:
                _position = self.puVar['accounts'][self.puVar['accounts_selected']]['positions'][_positionSymbol]
                _maxAllocatedBalance = _position['maxAllocatedBalance']
                #Old
                if (_position['currencyAnalysisCode'] is None):   self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTOLD"].updateText(text = "-")
                else:                                             self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTOLD"].updateText(text = _position['currencyAnalysisCode'])
                if (_position['tradeConfigurationCode'] is None): self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTOLD"].updateText(text = "-")
                else:                                             self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTOLD"].updateText(text = _position['tradeConfigurationCode'])
                self.GUIOs["POSITIONS_TRADERMODECACODESELECTIONBOX"].clearSelected()
                self.GUIOs["POSITIONS_TRADERMODETCCODESELECTIONBOX"].clearSelected()
                self.GUIOs["POSITIONS_TRADERMODECACODESELECTIONBOX"].addSelected(itemKey = _position['currencyAnalysisCode'],   callSelectionUpdateFunction = False)
                self.GUIOs["POSITIONS_TRADERMODETCCODESELECTIONBOX"].addSelected(itemKey = _position['tradeConfigurationCode'], callSelectionUpdateFunction = False)
                self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTOLD"].updateText(text = "{:d}".format(_position['priority']))
                self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTOLD"].updateText(text = "{:.3f} %".format(_position['assumedRatio']*100))
                if (_maxAllocatedBalance == float('inf')): self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTOLD"].updateText(text = "INF")
                else:                                      self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTOLD"].updateText(text = atmEta_Auxillaries.floatToString(number = _maxAllocatedBalance, precision = _position['precisions']['quote']))
                if (_position['tradeStatus'] == True): self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSVALUETEXT"].updateText(text = "TRUE",  textStyle = 'GREEN_LIGHT')
                else:                                  self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSVALUETEXT"].updateText(text = "FALSE", textStyle = 'RED_LIGHT')
                self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSSWITCH"].setStatus(status = _position['tradeStatus'], callStatusUpdateFunction = False)
                if (_position['tradable'] == True): self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSSWITCH"].activate()
                else:                               self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSSWITCH"].deactivate()
                if (_position['reduceOnly'] == True): self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYVALUETEXT"].updateText(text = "TRUE",  textStyle = 'ORANGE_LIGHT')
                else:                                 self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYVALUETEXT"].updateText(text = "FALSE", textStyle = 'GREEN_LIGHT')
                self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYSWITCH"].setStatus(status = _position['reduceOnly'], callStatusUpdateFunction = False)
                self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYSWITCH"].activate()
                #New
                caCodes_selected = self.GUIOs["POSITIONS_TRADERMODECACODESELECTIONBOX"].getSelected()
                tcCodes_selected = self.GUIOs["POSITIONS_TRADERMODETCCODESELECTIONBOX"].getSelected()
                if caCodes_selected: self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTNEW"].updateText(text = caCodes_selected[0])
                else:                self.GUIOs["POSITIONS_TRADERMODESELECTEDCACODEVALUETEXTNEW"].updateText(text = "-")
                if tcCodes_selected: self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTNEW"].updateText(text = tcCodes_selected[0])
                else:                self.GUIOs["POSITIONS_TRADERMODESELECTEDTCCODEVALUETEXTNEW"].updateText(text = "-")
                self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTNEW"].updateText(text = f"{_position['priority']}")
                self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTNEW"].activate()
                self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTNEW"].updateText(text = f"{_position['assumedRatio']*100:.3f}")
                self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTNEW"].activate()
                if (_maxAllocatedBalance == float('inf')): self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTNEW"].updateText(text = "")
                else:                                      self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTNEW"].updateText(text = atmEta_Auxillaries.floatToString(number = _maxAllocatedBalance, precision = _position['precisions']['quote']))
                self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTNEW"].activate()
                self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEUNITTEXT"].updateText(text = _position['quoteAsset'])
                #Apply Button
                self.pageAuxillaryFunctions['CHECKIFCANAPPLYNEWPARAMS']()
        elif (_displayMode == 'DETAIL'):
            pass
    def __checkIfCanForceClearPosition():
        _positionSymbol = self.puVar['positions_selected']
        if (_positionSymbol == None):
            self.GUIOs["POSITIONS_FORCECLEARPOSITIONSAFETYSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
            self.GUIOs["POSITIONS_FORCECLEARPOSITIONSAFETYSWITCH"].deactivate()
        else:
            _position = self.puVar['accounts'][self.puVar['accounts_selected']]['positions'][_positionSymbol]
            if ((_position['quantity'] != None) and (_position['quantity'] != 0)):
                self.GUIOs["POSITIONS_FORCECLEARPOSITIONSAFETYSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
                self.GUIOs["POSITIONS_FORCECLEARPOSITIONSAFETYSWITCH"].activate()
            else:
                self.GUIOs["POSITIONS_FORCECLEARPOSITIONSAFETYSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
                self.GUIOs["POSITIONS_FORCECLEARPOSITIONSAFETYSWITCH"].deactivate()
        self.GUIOs["POSITIONS_FORCECLEARPOSITIONBUTTON"].deactivate()
    def __setCurrencyAnalysisList():
        _positionSymbol = self.puVar['positions_selected']
        if (_positionSymbol == None): self.GUIOs["POSITIONS_TRADERMODECACODESELECTIONBOX"].clearSelectionList(callSelectionUpdateFunction = False)
        else:
            currencyAnalysis_selectionList = dict()
            for _caCode in self.puVar['currencyAnalysis']:
                _ca = self.puVar['currencyAnalysis'][_caCode]
                if (_ca['currencySymbol'] == _positionSymbol): currencyAnalysis_selectionList[_caCode] = {'text': _caCode, 'textAnchor': 'W'}
            self.GUIOs["POSITIONS_TRADERMODECACODESELECTIONBOX"].setSelectionList(selectionList = currencyAnalysis_selectionList, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)
    def __setTradeConfigurationsList():
        tradeConfigurations_selectionList = dict()
        for tradeConfigurationCode in self.puVar['tradeConfigurations']: tradeConfigurations_selectionList[tradeConfigurationCode] = {'text': tradeConfigurationCode, 'textAnchor': 'W'}
        self.GUIOs["POSITIONS_TRADERMODETCCODESELECTIONBOX"].setSelectionList(selectionList = tradeConfigurations_selectionList, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)
    def __checkIfCanApplyNewParams():
        #Get previous values
        _position = self.puVar['accounts'][self.puVar['accounts_selected']]['positions'][self.puVar['positions_selected']]
        _caCode_old              = _position['currencyAnalysisCode']
        _tcCode_old              = _position['tradeConfigurationCode']
        _priority_old            = _position['priority']
        _assumedRatio_old        = _position['assumedRatio']
        _maxAllocatedBalance_old = _position['maxAllocatedBalance']
        #Get new values
        try:    _caCode_new = self.GUIOs["POSITIONS_TRADERMODECACODESELECTIONBOX"].getSelected()[0]
        except: _caCode_new = None
        try:    _tcCode_new = self.GUIOs["POSITIONS_TRADERMODETCCODESELECTIONBOX"].getSelected()[0]
        except: _tcCode_new = None
        try:    _priority_new = int(self.GUIOs["POSITIONS_TRADERMODESELECTEDPRIORITYVALUETEXTNEW"].getText())
        except: _priority_new = None
        try:    _assumedRatio_new = round(float(self.GUIOs["POSITIONS_TRADERMODESELECTEDASSUMEDRATIOVALUETEXTNEW"].getText())/100, 5)
        except: _assumedRatio_new = None
        _maxAllocatedBalance_enteredStr = self.GUIOs["POSITIONS_TRADERMODESELECTEDMAXALLOCATEDBALANCEVALUETEXTNEW"].getText()
        if (_maxAllocatedBalance_enteredStr == ""): _maxAllocatedBalance_new = float('inf')
        else:
            try:    _maxAllocatedBalance_new = round(float(_maxAllocatedBalance_enteredStr), _position['precisions']['quote'])
            except: _maxAllocatedBalance_new = None
        #Finally
        if (   (_caCode_old              != _caCode_new) 
            or (_tcCode_old              != _tcCode_new) 
            or (_priority_old            != _priority_new) 
            or (_assumedRatio_old        != _assumedRatio_new) 
            or (_maxAllocatedBalance_old != _maxAllocatedBalance_new)): self.GUIOs["POSITIONS_TRADERMODEAPPLYBUTTON"].activate()
        else:                                                           self.GUIOs["POSITIONS_TRADERMODEAPPLYBUTTON"].deactivate()
    auxFunctions['SETPOSITIONSLIST']             = __setPositionsList
    auxFunctions['APPLYPOSITIONSLISTFILTER']     = __applyPositionsListFilter
    auxFunctions['ONPOSITIONSELECTIONUPDATE']    = __onPositionSelectionUpdate
    auxFunctions['CHECKIFCANFORCECLEARPOSITION'] = __checkIfCanForceClearPosition
    auxFunctions['SETCURRENCYANALYSISLIST']      = __setCurrencyAnalysisList
    auxFunctions['SETTRADECONFIGURATIONSLIST']   = __setTradeConfigurationsList
    auxFunctions['CHECKIFCANAPPLYNEWPARAMS']     = __checkIfCanApplyNewParams

    #<#Common>
    def __farr_onAccountControlRequestResponse(responder, requestID, functionResult):
        localID             = functionResult['localID']
        responseOn          = functionResult['responseOn']
        requestResult       = functionResult['result']
        detailedResult      = functionResult.get('result_detailed', None)
        tradeManagerMessage = functionResult.get('message',         None)
        if (tradeManagerMessage is not None):
            if (requestResult == True): self.GUIOs["TRADEMANAGERMESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = tradeManagerMessage, textStyle = 'GREEN_LIGHT')
            else:                       self.GUIOs["TRADEMANAGERMESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = tradeManagerMessage, textStyle = 'RED_LIGHT')
        if   (responseOn == 'ADDACCOUNT'):
            if (requestResult == True):
                self.puVar['accounts_selected'] = localID
                self.GUIOs["ACCOUNTSLIST_SELECTIONBOX"].addSelected(itemKey = localID, callSelectionUpdateFunction = False)
                self.pageAuxillaryFunctions['ONACCOUNTSELECTIONUPDATE']()
            else: self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ADDACCOUNTBUTTON"].activate()
        elif (responseOn == 'REMOVEACCOUNT'):
            if (requestResult == False): 
                if (localID == self.puVar['accounts_selected']): self.GUIOs["ACCOUNTSINFORMATION&CONTROL_REMOVEACCOUNTBUTTON"].activate()
        elif (responseOn == 'ACTIVATEACCOUNT'):
            if (localID == self.puVar['accounts_selected']):
                if (requestResult == True): 
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"].updateText(text    = "")
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"].updateText(text = "")
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"].deactivate()
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"].deactivate()
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_DEACTIVATEBUTTON"].activate()
                else:
                    self.pageAuxillaryFunctions['CHECKIFCANACTIVATEACCOUNT']()
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAFBUTTON"].activate()
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_DEACTIVATEBUTTON"].deactivate()
        elif (responseOn == 'DEACTIVATEACCOUNT'):
            if (localID == self.puVar['accounts_selected']):
                if (requestResult == True): 
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"].updateText(text    = "")
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"].updateText(text = "")
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"].activate()
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"].activate()
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYENTEREDKEYSBUTTON"].deactivate()
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAFBUTTON"].activate()
                else:
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYENTEREDKEYSBUTTON"].deactivate()
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAFBUTTON"].deactivate()
        elif (responseOn == 'SETACCOUNTTRADESTATUS'):
            if (localID == self.puVar['accounts_selected']):
                if (requestResult == False): self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSSWITCH"].setStatus(status = self.puVar['accounts'][localID]['tradeStatus'], callStatusUpdateFunction = False)
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_TRADESTATUSSWITCH"].activate()
        elif (responseOn == 'BALANCETRANSFER'):
            if (localID == self.puVar['accounts_selected']):
                try:    balanceToTransfer = float(self.GUIOs["ASSETS_TRASNFERBALANCETEXTINPUTBOX"].getText())
                except: balanceToTransfer = None
                if ((balanceToTransfer != None) and (0 < balanceToTransfer)): 
                    self.GUIOs["ASSETS_TRASNFERBALANCEDEPOSITBUTTON"].activate()
                    self.GUIOs["ASSETS_TRASNFERBALANCEWITHDRAWBUTTON"].activate()
                else:
                    self.GUIOs["ASSETS_TRASNFERBALANCEDEPOSITBUTTON"].deactivate()
                    self.GUIOs["ASSETS_TRASNFERBALANCEWITHDRAWBUTTON"].deactivate()
        elif (responseOn == 'ALLOCATIONRATIOUPDATE'):
            if (localID == self.puVar['accounts_selected']):
                if (requestResult == False): self.GUIOs["ASSETS_ALLOCATIONRATIOAPPLYBUTTON"].activate()
        elif (responseOn == 'FORCECLEARPOSITION'):
            positionSymbol = functionResult['positionSymbol']
            if (localID == self.puVar['accounts_selected']):
                if (positionSymbol == self.puVar['positions_selected']): self.pageAuxillaryFunctions['CHECKIFCANFORCECLEARPOSITION']()
        elif (responseOn == 'UPDATEPOSITIONTRADESTATUS'):
            positionSymbol = functionResult['positionSymbol']
            if (localID == self.puVar['accounts_selected']):
                if (positionSymbol == self.puVar['positions_selected']): 
                    if (requestResult == False): self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSSWITCH"].setStatus(status = self.puVar['accounts'][localID]['positions'][positionSymbol]['tradeStatus'], callStatusUpdateFunction = False)
                    self.GUIOs["POSITIONS_TRADERMODESELECTEDTRADESTATUSSWITCH"].activate()
        elif (responseOn == 'UPDATEPOSITIONREDUCEONLY'):
            positionSymbol = functionResult['positionSymbol']
            if (localID == self.puVar['accounts_selected']):
                if (positionSymbol == self.puVar['positions_selected']): 
                    if (requestResult == False): self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYSWITCH"].setStatus(status = self.puVar['accounts'][localID]['positions'][positionSymbol]['reduceOnly'], callStatusUpdateFunction = False)
                    self.GUIOs["POSITIONS_TRADERMODESELECTEDREDUCEONLYSWITCH"].activate()
        elif (responseOn == 'UPDATEPOSITIONTRADERPARAMS'):
            positionSymbol = functionResult['positionSymbol']
            if (localID == self.puVar['accounts_selected']):
                if (positionSymbol == self.puVar['positions_selected']): self.pageAuxillaryFunctions['CHECKIFCANAPPLYNEWPARAMS']()
        elif (responseOn == 'RESETTRADECONTROLTRACKER'):
            positionSymbol = functionResult['positionSymbol']
            if (localID == self.puVar['accounts_selected']):
                if (positionSymbol == self.puVar['positions_selected']): 
                    self.GUIOs["POSITIONS_TRADERMODERESETTRACECONTROLTRACKERBUTTON"].activate()
        elif (responseOn == 'VERIFYPASSWORD'):
            if (localID == self.puVar['accounts_selected']):
                isPasswordCorrect = detailedResult['isPasswordCorrect']
                if (isPasswordCorrect):
                    #[1]: Get entered strings
                    password_entered  = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].getText()
                    apiKey_entered    = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"].getText()
                    secretKey_entered = self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"].getText()
                    #[2]: Generate encrpyted key using the password (Hash the password and convert it to 32-byte key)
                    password_hash = hashlib.sha256(password_entered.encode()).digest()
                    fernet_key    = base64.urlsafe_b64encode(password_hash)
                    cipher        = Fernet(fernet_key)
                    #[3]: Encrpyt the API Key and the Secret Key
                    apiKey_encrypted    = cipher.encrypt(apiKey_entered.encode())
                    secretKey_encrypted = cipher.encrypt(secretKey_entered.encode())
                    aaf = (localID,
                           time.time_ns(),
                           apiKey_encrypted.decode(), 
                           secretKey_encrypted.decode())
                    #[5]: Save the instance as a json file
                    fileIndex = 0
                    path_file = os.path.join(self.path_project, 'data', f'{localID}.aaf')
                    while os.path.exists(path_file):
                        path_file = os.path.join(self.path_project, 'data', f'{localID}{fileIndex}.aaf')
                        fileIndex += 1
                    with open(path_file, "w") as f: f.write(json.dumps(aaf))
                    #[6]: Reset api key and secret key input boxes and display process completion message
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"].updateText(text    = "")
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"].updateText(text = "")
                    self.GUIOs["TRADEMANAGERMESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = f"[LOCAL] Account API Keys Registration To Flash Drive Successful! Check '{path_file}'", textStyle = 'GREEN_LIGHT')
                else:
                    self.GUIOs["ACCOUNTSINFORMATION&CONTROL_GENERATEAAFBUTTON"].activate()
                    self.GUIOs["TRADEMANAGERMESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = "[LOCAL] Account API Keys Registration To Flash Drive Failed - Incorrect Password", textStyle = 'RED_LIGHT')
                #Reactivate buttons
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_ACTIVATEBYAAFBUTTON"].activate()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_PASSWORDTEXTINPUTBOX"].activate()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_APIKEYTEXTINPUTBOX"].activate()
                self.GUIOs["ACCOUNTSINFORMATION&CONTROL_SECRETKEYTEXTINPUTBOX"].activate()
    auxFunctions['_FARR_ONACCOUNTCONTROLREQUESTRESPONSE'] = __farr_onAccountControlRequestResponse

    #Return the generated functions
    return auxFunctions
#AUXILALRY FUNCTIONS END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------