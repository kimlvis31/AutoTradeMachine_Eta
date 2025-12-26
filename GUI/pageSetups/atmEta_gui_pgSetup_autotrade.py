#ATM Modules
import atmEta_IPC
import atmEta_Auxillaries
import atmEta_Analyzers
import atmEta_RQPMFunctions
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
from GUI.atmEta_gui_ChartDrawer         import chartDrawer
from GUI.atmEta_gui_DailyReportViewer   import dailyReportViewer
from GUI.atmEta_gui_HourlyReportViewer  import hourlyReportViewer
from GUI.atmEta_gui_NeuralNetworkViewer import neuralNetworkViewer

#Python Modules
import pyglet
import pprint
import termcolor
import time
import random
import math
from datetime import datetime, timezone, tzinfo

#Constants
_IPC_THREADTYPE_MT = atmEta_IPC._THREADTYPE_MT
_IPC_THREADTYPE_AT = atmEta_IPC._THREADTYPE_AT
_IPC_PRD_INVALIDADDRESS    = atmEta_IPC._PRD_INVALIDADDRESS
_IPC_FAR_INVALIDFUNCTIONID = atmEta_IPC._FAR_INVALIDFUNCTIONID

#SETUP PAGE <MAIN> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setupPage(self):
    #Set page unique variables
    self.puVar['currencies']        = dict()
    self.puVar['currency_selected'] = None
    self.puVar['analyzerCentral'] = dict()
    self.puVar['analyzerCentral_nAnalyzersIdentified'] = False
    self.puVar['analyzerCentral_selectedAnalyzer']     = None
    self.puVar['analysisConfigurations']                              = dict()
    self.puVar['toAnalysisList_analysisConfiguration_selected']       = None
    self.puVar['toAnalysisList_waitingResponse']                      = False
    self.puVar['configurationControl_analysisConfiguration_selected'] = None
    self.puVar['currentAnalysisConfigurationPageName']                = 'MAIN'
    self.puVar['currencyAnalysis']          = dict()
    self.puVar['currencyAnalysis_selected'] = None
    self.puVar['tradeConfigurations']         = dict()
    self.puVar['tradeConfiguration_selected'] = None
    self.puVar['tradeConfiguration_current_TS_TS_Entry']           = list()
    self.puVar['tradeConfiguration_current_TS_TS_Exit']            = list()
    self.puVar['tradeConfiguration_current_TS_TS_PSL']             = list()
    self.puVar['tradeConfiguration_current_RQPM_Parameters_LONG']  = list()
    self.puVar['tradeConfiguration_current_RQPM_Parameters_SHORT'] = list()
    self.puVar['tradeConfiguration_guioGroups'] = dict()
    #---Default Analysis Configuration
    if (True):
        self.puVar['analysisConfigurations_default'] = dict()
        #NON-INDICATORS
        self.puVar['analysisConfigurations_default']['NI_MinCompleteAnalysis'] = 120
        self.puVar['analysisConfigurations_default']['NI_NAnalysisToDisplay']  = 240
        #SMA
        self.puVar['analysisConfigurations_default']['SMA_Master'] = False
        for lineIndex in range (10):
            lineNumber = lineIndex+1
            self.puVar['analysisConfigurations_default']['SMA_{:d}_LineActive'.format(lineNumber)] = False
            self.puVar['analysisConfigurations_default']['SMA_{:d}_NSamples'.format(lineNumber)]   = 10*lineNumber
        #EMA
        self.puVar['analysisConfigurations_default']['EMA_Master'] = False
        for lineIndex in range (10):
            lineNumber = lineIndex+1
            self.puVar['analysisConfigurations_default']['EMA_{:d}_LineActive'.format(lineNumber)] = False
            self.puVar['analysisConfigurations_default']['EMA_{:d}_NSamples'.format(lineNumber)]   = 10*lineNumber
        #WMA
        self.puVar['analysisConfigurations_default']['WMA_Master'] = False
        for lineIndex in range (10):
            lineNumber = lineIndex+1
            self.puVar['analysisConfigurations_default']['WMA_{:d}_LineActive'.format(lineNumber)] = False
            self.puVar['analysisConfigurations_default']['WMA_{:d}_NSamples'.format(lineNumber)]   = 10*lineNumber
        #PSAR
        self.puVar['analysisConfigurations_default']['PSAR_Master'] = False
        for lineIndex in range (5):
            lineNumber = lineIndex+1
            self.puVar['analysisConfigurations_default']['PSAR_{:d}_LineActive'.format(lineNumber)] = False
            self.puVar['analysisConfigurations_default']['PSAR_{:d}_AF0'.format(lineNumber)]        = 0.020
            self.puVar['analysisConfigurations_default']['PSAR_{:d}_AF+'.format(lineNumber)]        = 0.005*lineNumber
            self.puVar['analysisConfigurations_default']['PSAR_{:d}_AFMax'.format(lineNumber)]      = 0.200
        #BOL
        self.puVar['analysisConfigurations_default']['BOL_Master'] = False
        self.puVar['analysisConfigurations_default']['BOL_MAType'] = 'SMA'
        for lineIndex in range (10):
            lineNumber = lineIndex+1
            self.puVar['analysisConfigurations_default']['BOL_{:d}_LineActive'.format(lineNumber)] = False
            self.puVar['analysisConfigurations_default']['BOL_{:d}_NSamples'.format(lineNumber)]   = 10*lineNumber
            self.puVar['analysisConfigurations_default']['BOL_{:d}_BandWidth'.format(lineNumber)]  = 2.0
        #IVP
        self.puVar['analysisConfigurations_default']['IVP_Master'] = False
        self.puVar['analysisConfigurations_default']['IVP_NSamples']    = 500
        self.puVar['analysisConfigurations_default']['IVP_GammaFactor'] = 0.010
        self.puVar['analysisConfigurations_default']['IVP_DeltaFactor'] = 1.0
        #PIP
        self.puVar['analysisConfigurations_default']['PIP_Master']                  = False
        self.puVar['analysisConfigurations_default']['PIP_NeuralNetworkCode']       = None
        self.puVar['analysisConfigurations_default']['PIP_SwingRange']              = 0.0250
        self.puVar['analysisConfigurations_default']['PIP_NNAAlpha']                = 0.25
        self.puVar['analysisConfigurations_default']['PIP_NNABeta']                 = 10
        self.puVar['analysisConfigurations_default']['PIP_ClassicalAlpha']          = 2.0
        self.puVar['analysisConfigurations_default']['PIP_ClassicalBeta']           = 10
        self.puVar['analysisConfigurations_default']['PIP_ClassicalNSamples']       = 10
        self.puVar['analysisConfigurations_default']['PIP_ClassicalSigma']          = 3.5
        self.puVar['analysisConfigurations_default']['PIP_CSActivationThreshold1']  = 0.50
        self.puVar['analysisConfigurations_default']['PIP_CSActivationThreshold2']  = 0.20
        self.puVar['analysisConfigurations_default']['PIP_WSActivationThreshold']   = 0.10
        self.puVar['analysisConfigurations_default']['PIP_ActionSignalMode']        = 'IMPULSIVE'
        #VOL
        self.puVar['analysisConfigurations_default']['VOL_Master'] = False
        for lineIndex in range (5):
            lineNumber = lineIndex+1
            self.puVar['analysisConfigurations_default']['VOL_{:d}_LineActive'.format(lineNumber)] = False
            self.puVar['analysisConfigurations_default']['VOL_{:d}_NSamples'.format(lineNumber)]   = 20*lineNumber
        self.puVar['analysisConfigurations_default']['VOL_VolumeType'] = 'BASE'
        self.puVar['analysisConfigurations_default']['VOL_MAType']     = 'SMA'
        #MMACDSHORT
        self.puVar['analysisConfigurations_default']['MMACDSHORT_Master'] = False
        self.puVar['analysisConfigurations_default']['MMACDSHORT_SignalNSamples'] = 10
        self.puVar['analysisConfigurations_default']['MMACDSHORT_Multiplier']     = 12
        for lineIndex in range (6):
            lineNumber = lineIndex+1
            self.puVar['analysisConfigurations_default']['MMACDSHORT_MA{:d}_LineActive'.format(lineNumber)] = False
            self.puVar['analysisConfigurations_default']['MMACDSHORT_MA{:d}_NSamples'.format(lineNumber)]   = 20*lineNumber
        #MMACDLONG
        self.puVar['analysisConfigurations_default']['MMACDLONG_Master'] = False
        self.puVar['analysisConfigurations_default']['MMACDLONG_SignalNSamples'] = 10
        self.puVar['analysisConfigurations_default']['MMACDLONG_Multiplier']     = 48
        for lineIndex in range (6):
            lineNumber = lineIndex+1
            self.puVar['analysisConfigurations_default']['MMACDLONG_MA{:d}_LineActive'.format(lineNumber)] = False
            self.puVar['analysisConfigurations_default']['MMACDLONG_MA{:d}_NSamples'.format(lineNumber)]   = 20*lineNumber
        #DMIxADX
        self.puVar['analysisConfigurations_default']['DMIxADX_Master'] = False
        for lineIndex in range (5):
            lineNumber = lineIndex+1
            self.puVar['analysisConfigurations_default']['DMIxADX_{:d}_LineActive'.format(lineNumber)] = False
            self.puVar['analysisConfigurations_default']['DMIxADX_{:d}_NSamples'.format(lineNumber)]   = 10*lineNumber
        #MFI
        self.puVar['analysisConfigurations_default']['MFI_Master'] = False
        for lineIndex in range (5):
            lineNumber = lineIndex+1
            self.puVar['analysisConfigurations_default']['MFI_{:d}_LineActive'.format(lineNumber)] = False
            self.puVar['analysisConfigurations_default']['MFI_{:d}_NSamples'.format(lineNumber)]   = 10*lineNumber
        #WOI
        self.puVar['analysisConfigurations_default']['WOI_Master'] = False
        for lineIndex in range (3):
            lineNumber = lineIndex+1
            self.puVar['analysisConfigurations_default']['WOI_{:d}_LineActive'.format(lineNumber)] = False
            self.puVar['analysisConfigurations_default']['WOI_{:d}_NSamples'.format(lineNumber)]   = 10*lineNumber
            self.puVar['analysisConfigurations_default']['WOI_{:d}_Sigma'.format(lineNumber)]      = round(2.5*lineNumber, 1)
        #NES
        self.puVar['analysisConfigurations_default']['NES_Master'] = False
        for lineIndex in range (3):
            lineNumber = lineIndex+1
            self.puVar['analysisConfigurations_default']['NES_{:d}_LineActive'.format(lineNumber)] = False
            self.puVar['analysisConfigurations_default']['NES_{:d}_NSamples'.format(lineNumber)]   = 10*lineNumber
            self.puVar['analysisConfigurations_default']['NES_{:d}_Sigma'.format(lineNumber)]      = round(2.5*lineNumber, 1)
    #---Default Trade Configuration
    if (True):
        self.puVar['tradeConfigurations_default'] = {'leverage':  1,
                                                     'isolated':  True,
                                                     'direction': 'BOTH',
                                                     'tcMode':    'TS',
                                                     #TS Only
                                                     'ts_fullStopLossImmediate': None,
                                                     'ts_fullStopLossClose':     None,
                                                     'ts_weightReduce':          None,
                                                     'ts_reachAndFall':          None,
                                                     'ts_ts_entry':  [(0.000, 0.200), (0.010, 0.400), (0.020, 0.600), (0.030, 0.800), (0.040, 1.000)],
                                                     'ts_ts_exit':   [(0.010, 0.800), (0.020, 0.600), (0.030, 0.400), (0.040, 0.200), (0.050, 0.000)],
                                                     'ts_ts_psl':    [(0.010, 0.800), (0.020, 0.600), (0.030, 0.400), (0.040, 0.200), (0.050, 0.000)],
                                                     #RQPM Only
                                                     'rqpm_exitOnImpulse':         None,
                                                     'rqpm_exitOnAligned':         None,
                                                     'rqpm_exitOnProfitable':      None,
                                                     'rqpm_fullStopLossImmediate': None,
                                                     'rqpm_fullStopLossClose':     None,
                                                     'rqpm_functionType':          None,
                                                     'rqpm_functionParams_LONG':   list(),
                                                     'rqpm_functionParams_SHORT':  list()}
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
        self.GUIOs["TITLETEXT_AUTOTRADE"] = textBox_typeA(**inst, groupOrder=1, xPos= 7000, yPos=8550, width=2000, height=400, style=None, text=self.visualManager.getTextPack('AUTOTRADE:TITLE'), fontSize = 220, textInteractable = False)

        self.GUIOs["BUTTON_MOVETO_DASHBOARD"] = button_typeB(**inst,  groupOrder=2, xPos=  50, yPos=8650, width= 300, height=300, style="styleB", releaseFunction=self.pageObjectFunctions['PAGEMOVE_DASHBOARD'], image = 'dashboardIcon_512x512.png', imageSize = (225, 225), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))

        #Market
        self.GUIOs["MARKET_BLOCKTITLE"] = passiveGraphics_wrapperTypeB(**inst, groupOrder=1, xPos=100, yPos=8350, width=3600, height=200, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:BLOCKTITLE_MARKET'), fontSize = 100)
        #---Filter
        self.GUIOs["MARKET_BLOCKSUBTITLE_FILTER"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=8150, width=3600, height=200, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_CURRENCIES'), fontSize = 80)
        self.GUIOs["MARKET&FILTER_SEARCHTITLETEXT"]                            = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=7800, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:MARKET&FILTER_SEARCH'), fontSize=80, textInteractable=False)
        self.GUIOs["MARKET&FILTER_SEARCHTITLETEXTINPUTBOX"]                    = textInputBox_typeA(**inst, groupOrder=1, xPos= 900, yPos=7800, width=2800, height=250, style="styleA", text="",                                                                          fontSize=80, textUpdateFunction  =self.pageObjectFunctions['ONTEXTUPDATE_MARKET&FILTER_SEARCHTEXT'])
        self.GUIOs["MARKET&FILTER_FILTERSWITCH_TRADINGTRUE"]                   = switch_typeC(**inst,       groupOrder=1, xPos= 100, yPos=7450, width=1750, height=250, style="styleB", text=self.visualManager.getTextPack('AUTOTRADE:MARKET&FILTER_TRADINGTRUE'),       fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_MARKET&FILTER_TRADINGTRUE'])
        self.GUIOs["MARKET&FILTER_FILTERSWITCH_TRADINGFALSE"]                  = switch_typeC(**inst,       groupOrder=1, xPos=1950, yPos=7450, width=1750, height=250, style="styleB", text=self.visualManager.getTextPack('AUTOTRADE:MARKET&FILTER_TRADINGFALSE'),      fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_MARKET&FILTER_TRADINGFALSE'])
        self.GUIOs["MARKET&FILTER_FILTERSWITCH_MINNUMBEROFKLINES"]             = switch_typeC(**inst,       groupOrder=1, xPos= 100, yPos=7100, width=1750, height=250, style="styleB", text=self.visualManager.getTextPack('AUTOTRADE:MARKET&FILTER_MINNUMBEROFKLINES'), fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_MARKET&FILTER_MINNUMBEROFKLINES'])
        self.GUIOs["MARKET&FILTER_FILTERSWITCH_MINNUMBEROFKLINESTEXTINPUTBOX"] = textInputBox_typeA(**inst, groupOrder=1, xPos=1950, yPos=7100, width=1750, height=250, style="styleA", text="",                                                                          fontSize=80, textUpdateFunction  =self.pageObjectFunctions['ONTEXTUPDATE_MARKET&FILTER_MINNUMBEROFKLINES'])
        self.GUIOs["MARKET&FILTER_SORTBYTITLETEXT"]                            = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=6750, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:MARKET&FILTER_SORTBY'),            fontSize=80, textInteractable    =False)
        self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYID"]                      = switch_typeC(**inst,       groupOrder=1, xPos= 900, yPos=6750, width= 700, height=250, style="styleB", text=self.visualManager.getTextPack('AUTOTRADE:MARKET&FILTER_ID'),                fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_MARKET&FILTER_SORTBYID'])
        self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYSYMBOL"]                  = switch_typeC(**inst,       groupOrder=1, xPos=1700, yPos=6750, width= 800, height=250, style="styleB", text=self.visualManager.getTextPack('AUTOTRADE:MARKET&FILTER_SYMBOL'),            fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_MARKET&FILTER_SORTBYSYMBOL'])
        self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYFIRSTKLINE"]              = switch_typeC(**inst,       groupOrder=1, xPos=2600, yPos=6750, width=1100, height=250, style="styleB", text=self.visualManager.getTextPack('AUTOTRADE:MARKET&FILTER_FIRSTKLINE'),        fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_MARKET&FILTER_SORTBYFIRSTKLINE'])
        self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYID"].setStatus(status = True, callStatusUpdateFunction = False)
        #---Currencies
        self.GUIOs["MARKET&CURRENCIES_LISTINFO_NCURRENCIESTITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=6400, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:MARKET&CURRENCIES_NCURRENCIES'), fontSize=80, textInteractable=False)
        self.GUIOs["MARKET&CURRENCIES_LISTINFO_NCURRENCIESDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=1200, yPos=6400, width=2500, height=250, style="styleA", text="-",                                                                       fontSize=80, textInteractable=False)
        self.GUIOs["MARKET&CURRENCIES_SELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=1, xPos=100, yPos=2150, width=3600, height=4150, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_MARKET&FILTER_CURRENCYSELECTION'], elementWidths = (650, 1050, 650, 1000))
        self.GUIOs["MARKET&CURRENCIES_SELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('AUTOTRADE:MARKET&CURRENCIES_INDEX')},
                                                                                      {'text': self.visualManager.getTextPack('AUTOTRADE:MARKET&CURRENCIES_SYMBOL')},
                                                                                      {'text': self.visualManager.getTextPack('AUTOTRADE:MARKET&CURRENCIES_STATUS')},
                                                                                      {'text': self.visualManager.getTextPack('AUTOTRADE:MARKET&CURRENCIES_FIRSTKLINE')}])
        #---Information
        self.GUIOs["MARKET&INFORMATION_CURRENCYIDTITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=1800, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:MARKET&INFORMATION_CURRENCYID'), fontSize=80, textInteractable=True)
        self.GUIOs["MARKET&INFORMATION_CURRENCYIDDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=1200, yPos=1800, width=2500, height=250, style="styleA", text="-",                                                                       fontSize=80, textInteractable=True)
        self.GUIOs["MARKET&INFORMATION_DATARANGETITLETEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=1450, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:MARKET&INFORMATION_DATARANGE'),  fontSize=80, textInteractable=True)
        self.GUIOs["MARKET&INFORMATION_DATARANGEDISPLAYTEXT"]  = textBox_typeA(**inst, groupOrder=1, xPos=1200, yPos=1450, width=2500, height=250, style="styleA", text="-",                                                                       fontSize=80, textInteractable=True)
        #---To analysis list
        self.GUIOs["MARKET_BLOCKSUBTITLE_TOANALYSISLIST"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=1150, width=3600, height=200, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_TOANALYSISLIST'), fontSize = 80)
        self.GUIOs["MARKET&TOANALYSISLIST_ANALYSISCONFIGTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=800, width= 900, height=250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:MARKET&TOANALYSISLIST_CACLIST'),      fontSize=80, textInteractable  =True)
        self.GUIOs["MARKET&TOANALYSISLIST_ANALYSISCONFIGSELECTIONBOX"] = selectionBox_typeB(**inst, groupOrder=2, xPos=1100, yPos=800, width=2600, height=250, style="styleA", nDisplay = 5, fontSize = 80, expansionDir = 1, showIndex = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_MARKET&TOANALYSISLIST_CONFIGURATIONSELECTION'])
        self.GUIOs["MARKET&TOANALYSISLIST_ANALYSISCODETITLETEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=450, width= 900, height=250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:MARKET&TOANALYSISLIST_ANALYSISCODE'), fontSize=80, textInteractable  =True)
        self.GUIOs["MARKET&TOANALYSISLIST_ANALYSISCODETEXTINPUTBOX"]   = textInputBox_typeA(**inst, groupOrder=1, xPos=1100, yPos=450, width=1900, height=250, style="styleA", text="",                                                                             fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_MARKET&TOANALYSISLIST_ANALYSISCODE'])
        self.GUIOs["MARKET&TOANALYSISLIST_ANALYSISLISTADD"]                = button_typeA(**inst,   groupOrder=1, xPos=3100, yPos=450, width= 600, height=250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:MARKET&TOANALYSISLIST_ADD'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_MARKET&TOANALYSISLIST_ADDANALYSIS'])
        self.GUIOs["MARKET&TOANALYSISLIST_ANALYSISLISTADD"].deactivate()
        #Trade Manager
        self.GUIOs["TRADEMANAGER_BLOCKTITLE"] = passiveGraphics_wrapperTypeB(**inst, groupOrder=1, xPos=3800, yPos=8350, width=12100, height=200, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:BLOCKTITLE_TRADEMANAGER'), fontSize = 100)
        #---Analyzers
        self.GUIOs["TRADEMANAGER_BLOCKSUBTITLE_ANALYZERS"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=3800, yPos=8150, width=4700, height=200, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_ANALYZERS'), fontSize = 80)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFANALYZERSTITLETEXT"]                = textBox_typeA(**inst,      groupOrder=1, xPos=3800, yPos=7800, width=1400, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFANALYZERS'),              fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFANALYZERSDISPLAYTEXT"]              = textBox_typeA(**inst,      groupOrder=1, xPos=5300, yPos=7800, width= 800, height= 250, style="styleA", text="-",                                                                                                fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCAUNALLOCATEDTITLETEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos=3800, yPos=7450, width=1400, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCAUNALLOCATED'),          fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCAUNALLOCATEDDISPLAYTEXT"]           = textBox_typeA(**inst,      groupOrder=1, xPos=5300, yPos=7450, width= 800, height= 250, style="styleA", text="-",                                                                                                fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCAALLOCATEDTITLETEXT"]               = textBox_typeA(**inst,      groupOrder=1, xPos=3800, yPos=7100, width=1400, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCAALLOCATED'),            fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCAALLOCATEDDISPLAYTEXT"]             = textBox_typeA(**inst,      groupOrder=1, xPos=5300, yPos=7100, width= 800, height= 250, style="styleA", text="-",                                                                                                fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCACONFIGNOTFOUNDTITLETEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos=3800, yPos=6750, width=1400, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCACONFIGNOTFOUND'),       fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCACONFIGNOTFOUNDDISPLAYTEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos=5300, yPos=6750, width= 800, height= 250, style="styleA", text="-",                                                                                                fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCACURRENCYNOTFOUNDTITLETEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos=3800, yPos=6400, width=1400, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCACURRENCYNOTFOUND'),     fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCACURRENCYNOTFOUNDDISPLAYTEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos=5300, yPos=6400, width= 800, height= 250, style="styleA", text="-",                                                                                                fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCAWAITINGTRADINGTITLETEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos=3800, yPos=6050, width=1400, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCAWAITINGTRADING'),       fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCAWAITINGTRADINGDISPLAYTEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos=5300, yPos=6050, width= 800, height= 250, style="styleA", text="-",                                                                                                fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_AVERAGEPIPGENERATIONTIMETITLETEXT"]         = textBox_typeA(**inst,      groupOrder=1, xPos=3800, yPos=5700, width=1400, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&NANALYZERS_AVERAGEPIPGENERATIONTIME'),       fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_AVERAGEPIPGENERATIONTIMEDISPLAYTEXT"]       = textBox_typeA(**inst,      groupOrder=1, xPos=5300, yPos=5700, width= 800, height= 250, style="styleA", text="-",                                                                                                fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_ANALYZERTITLETEXT"]                         = textBox_typeA(**inst,      groupOrder=1, xPos=6200, yPos=7800, width=1000, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&NANALYZERS_ANALYZER'),                       fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_ANALYZERSELECTIONBOX"]                      = selectionBox_typeB(**inst, groupOrder=2, xPos=7300, yPos=7800, width=1200, height= 250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 0, showIndex = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_TRADEMANAGER&ANALYZERS_ANALYZER'])
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCATOTALTITLETEXT"]                  = textBox_typeA(**inst,      groupOrder=1, xPos=6200, yPos=7450, width=1400, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCATOTAL'),                fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCATOTALDISPLAYTEXT"]                = textBox_typeA(**inst,      groupOrder=1, xPos=7700, yPos=7450, width= 800, height= 250, style="styleA", text="-",                                                                                                fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAWAITINGSTREAMTITLETEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos=6200, yPos=7100, width=1400, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCAWAITINGSTREAM'),        fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAWAITINGSTREAMDISPLAYTEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos=7700, yPos=7100, width= 800, height= 250, style="styleA", text="-",                                                                                                fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAWAITINGDATAAVAILABLETITLETEXT"]   = textBox_typeA(**inst,      groupOrder=1, xPos=6200, yPos=6750, width=1400, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCAWAITINGDATAAVAILABLE'), fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAWAITINGDATAAVAILABLEDISPLAYTEXT"] = textBox_typeA(**inst,      groupOrder=1, xPos=7700, yPos=6750, width= 800, height= 250, style="styleA", text="-",                                                                                                fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAPREPARINGTITLETEXT"]              = textBox_typeA(**inst,      groupOrder=1, xPos=6200, yPos=6400, width=1400, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCAPREPARING'),            fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAPREPARINGDISPLAYTEXT"]            = textBox_typeA(**inst,      groupOrder=1, xPos=7700, yPos=6400, width= 800, height= 250, style="styleA", text="-",                                                                                                fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAANALYZINGREALTIMETITLETEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos=6200, yPos=6050, width=1400, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCAANALYZINGREALTIME'),    fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAANALYZINGREALTIMEDISPLAYTEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=7700, yPos=6050, width= 800, height= 250, style="styleA", text="-",                                                                                                fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAERRORTITLETEXT"]                  = textBox_typeA(**inst,      groupOrder=1, xPos=6200, yPos=5700, width=1400, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&NANALYZERS_NUMBEROFCAERROR'),                fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAERRORDISPLAYTEXT"]                = textBox_typeA(**inst,      groupOrder=1, xPos=7700, yPos=5700, width= 800, height= 250, style="styleA", text="-",                                                                                                fontSize=80, textInteractable=False)
        #---Configuration
        self.GUIOs["TRADEMANAGER_BLOCKSUBTITLE_CONFIGURATION"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=3800, yPos=5400, width=4700, height=200, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_CONFIGURATION'), fontSize = 80)
        _MITypes = ('SMA', 'WMA', 'EMA', 'PSAR', 'BOL', 'IVP', 'PIP')
        _SITypes = ('VOL', 'MMACDSHORT', 'MMACDLONG', 'DMIxADX', 'MFI', 'WOI', 'NES')
        for configSubPageName in ('MAIN',)+_MITypes+_SITypes:
            _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_{:s}".format(configSubPageName)
            self.GUIOs[_objName] = subPageBox_typeA(**inst, groupOrder=1, xPos=3800, yPos=1500, width=4700, height=3850, style=None, useScrollBar_V=True, useScrollBar_H=False)
            if (configSubPageName != 'MAIN'): self.GUIOs[_objName].hide()
        yPos_beg = 20000
        subPageViewSpaceWidth = self.GUIOs["TRADEMANAGER_BLOCKSUBTITLE_CONFIGURATION"].width-150
        if (True): #Configuration/MAIN
            _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"
            yPosPoint0 = yPos_beg-200
            self.GUIOs[_objName].addGUIO("TITLE_MAININDICATORS", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_MAININDICATORS'), 'fontSize': 80})
            for i, miType in enumerate(_MITypes):
                self.GUIOs[_objName].addGUIO("INDICATORMASTERSWITCH_{:s}".format(miType), switch_typeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-350-350*i, 'width': 3650, 'height': 250, 'style': 'styleB', 'name': 'IndicatorMasterSwitch_{:s}'.format(miType), 'text': miType, 'fontSize': 80})
                self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_{:s}".format(miType),       button_typeA, {'groupOrder': 0, 'xPos': 3750, 'yPos': yPosPoint0-350-350*i, 'width':  800, 'height': 250, 'style': 'styleA', 'text': ">", 'fontSize': 80, 'name': 'navButton_{:s}'.format(miType), 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
            yPosPoint1 = yPosPoint0-300-350*len(_MITypes)
            self.GUIOs[_objName].addGUIO("TITLE_SUBINDICATORS", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_SUBINDICATORS'), 'fontSize': 80})
            for i, siType in enumerate(_SITypes):
                self.GUIOs[_objName].addGUIO("INDICATORMASTERSWITCH_{:s}".format(siType), switch_typeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350-350*i, 'width': 3650, 'height': 250, 'style': 'styleB', 'name': 'IndicatorMasterSwitch_{:s}'.format(siType), 'text': siType, 'fontSize': 80})
                self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_{:s}".format(siType),       button_typeA, {'groupOrder': 0, 'xPos': 3750, 'yPos': yPosPoint1-350-350*i, 'width':  800, 'height': 250, 'style': 'styleA', 'text': ">", 'fontSize': 80, 'name': 'navButton_{:s}'.format(siType), 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
            yPosPoint2 = yPosPoint1-300-350*len(_SITypes)
            self.GUIOs[_objName].addGUIO("TITLE_OTHERS", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_OTHERS'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("MINCOMPLETEANALYSISTITLETEXT",    textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint2-350, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_MINCOMPLETEANALYSIS'), 'fontSize': 80, 'textInteractable': False})
            self.GUIOs[_objName].addGUIO("MINCOMPLETEANALYSISTEXTINPUTBOX", textInputBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': yPosPoint2-350, 'width': 2450, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("NANALYSISDISPLAYTITLETEXT",       textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint2-700, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NANALYSISDISPLAY'), 'fontSize': 80,    'textInteractable': False})
            self.GUIOs[_objName].addGUIO("NANALYSISDISPLAYTEXTINPUTBOX",    textInputBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': yPosPoint2-700, 'width': 2450, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
        if (True): #Configuration/SMA
            _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SMA"
            yPosPoint0 = yPos_beg-200
            self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0,     'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_SMASETUP'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
            yPosPoint1 = yPosPoint0-650
            for lineIndex in range (10):
                lineNumber = lineIndex+1
                self.GUIOs[_objName].addGUIO("SMA_{:d}_LINE".format(lineNumber),     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': 'SMA {:d}'.format(lineNumber), 'fontSize': 80})
                self.GUIOs[_objName].addGUIO("SMA_{:d}_NSAMPLES".format(lineNumber), textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                            'fontSize': 80})
            yPosPoint2 = yPosPoint1-350*10
            self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
        if (True): #Configuration/WMA
            _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WMA"
            yPosPoint0 = yPos_beg-200
            self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0,     'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_WMASETUP'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
            yPosPoint1 = yPosPoint0-650
            for lineIndex in range (10):
                lineNumber = lineIndex+1
                self.GUIOs[_objName].addGUIO("WMA_{:d}_LINE".format(lineNumber),     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': 'WMA {:d}'.format(lineNumber), 'fontSize': 80})
                self.GUIOs[_objName].addGUIO("WMA_{:d}_NSAMPLES".format(lineNumber), textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                            'fontSize': 80})
            yPosPoint2 = yPosPoint1-350*10
            self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
        if (True): #Configuration/EMA
            _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_EMA"
            yPosPoint0 = yPos_beg-200
            self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0,     'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_EMASETUP'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
            yPosPoint1 = yPosPoint0-650
            for lineIndex in range (10):
                lineNumber = lineIndex+1
                self.GUIOs[_objName].addGUIO("EMA_{:d}_LINE".format(lineNumber),     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': 'EMA {:d}'.format(lineNumber), 'fontSize': 80})
                self.GUIOs[_objName].addGUIO("EMA_{:d}_NSAMPLES".format(lineNumber), textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                            'fontSize': 80})
            yPosPoint2 = yPosPoint1-350*10
            self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
        if (True): #Configuration/PSAR
            _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"
            yPosPoint0 = yPos_beg-200
            self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0,     'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_PSARSETUP'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'), 'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_AF0",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1350, 'yPos': yPosPoint0-300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_AF0'),   'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_AF+",   passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2450, 'yPos': yPosPoint0-300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_AF+'),   'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_AFMAX", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3550, 'yPos': yPosPoint0-300, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_AFMAX'), 'fontSize': 80, 'anchor': 'SW'})
            yPosPoint1 = yPosPoint0-650
            for lineIndex in range (5):
                lineNumber = lineIndex+1
                self.GUIOs[_objName].addGUIO("PSAR_{:d}_LINE".format(lineNumber),  switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 1250, 'height': 250, 'style': 'styleB', 'text': 'PSAR {:d}'.format(lineNumber), 'fontSize': 80})
                self.GUIOs[_objName].addGUIO("PSAR_{:d}_AF0".format(lineNumber),   textInputBox_typeA, {'groupOrder': 0, 'xPos': 1350, 'yPos': yPosPoint1-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': "",                            'fontSize': 80})
                self.GUIOs[_objName].addGUIO("PSAR_{:d}_AF+".format(lineNumber),   textInputBox_typeA, {'groupOrder': 0, 'xPos': 2450, 'yPos': yPosPoint1-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': "",                            'fontSize': 80})
                self.GUIOs[_objName].addGUIO("PSAR_{:d}_AFMAX".format(lineNumber), textInputBox_typeA, {'groupOrder': 0, 'xPos': 3550, 'yPos': yPosPoint1-350*lineIndex, 'width': 1000, 'height': 250, 'style': 'styleA', 'text': "",                            'fontSize': 80})
            yPosPoint2 = yPosPoint1-350*5
            self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
        if (True): #Configuration/BOL
            _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"
            yPosPoint0 = yPos_beg-200
            self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",       passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0,     'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_BOLSETUP'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("BOLMATYPETITLETEXT",    textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-350, 'width': 2450, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_BOLMATYPE'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("BOLMATYPESELECTIONBOX", selectionBox_typeB,           {'groupOrder': 2, 'xPos': 2550, 'yPos': yPosPoint0-350, 'width': 2000, 'height': 250, 'style': 'styleA', 'nDisplay': 3, 'fontSize': 80})
            maTypes = {'SMA': {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_SMA')},
                       'WMA': {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_WMA')},
                       'EMA': {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_EMA')}}
            self.GUIOs[_objName].GUIOs["BOLMATYPESELECTIONBOX"].setSelectionList(selectionList = maTypes, displayTargets = 'all')
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",     passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-650, 'width': 1650, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),     'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES",  passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1750, 'yPos': yPosPoint0-650, 'width': 1350, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'),  'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_BANDWIDTH", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3200, 'yPos': yPosPoint0-650, 'width': 1350, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_BANDWIDTH'), 'fontSize': 80, 'anchor': 'SW'})
            yPosPoint1 = yPosPoint0-1000
            for lineIndex in range (10):
                lineNumber = lineIndex+1
                self.GUIOs[_objName].addGUIO("BOL_{:d}_LINE".format(lineNumber),      switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 1650, 'height': 250, 'style': 'styleB', 'text': 'BOL {:d}'.format(lineNumber), 'fontSize': 80})
                self.GUIOs[_objName].addGUIO("BOL_{:d}_NSAMPLES".format(lineNumber),  textInputBox_typeA, {'groupOrder': 0, 'xPos': 1750, 'yPos': yPosPoint1-350*lineIndex, 'width': 1350, 'height': 250, 'style': 'styleA', 'text': "",                            'fontSize': 80})
                self.GUIOs[_objName].addGUIO("BOL_{:d}_BANDWIDTH".format(lineNumber), textInputBox_typeA, {'groupOrder': 0, 'xPos': 3200, 'yPos': yPosPoint1-350*lineIndex, 'width': 1350, 'height': 250, 'style': 'styleA', 'text': "",                            'fontSize': 80})
            yPosPoint2 = yPosPoint1-350*10
            self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
        if (True): #Configuration/IVP
            _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"
            yPosPoint0 = yPos_beg-200
            self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_IVPSETUP'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("NSAMPLESTITLETEXT",             textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 350, 'width': 2000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("NSAMPLESTEXTINPUTBOX",          textInputBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': yPosPoint0- 350, 'width': 2450, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("GAMMAFACTORTITLETEXT",          textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 700, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_GAMMAFACTOR'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("GAMMAFACTORSLIDER",             slider_typeA,       {'groupOrder': 0, 'xPos': 1400, 'yPos': yPosPoint0- 650, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'IVP_GammaFactor', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
            self.GUIOs[_objName].addGUIO("GAMMAFACTORDISPLAYTEXT",        textBox_typeA,      {'groupOrder': 0, 'xPos': 3950, 'yPos': yPosPoint0- 700, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("DELTAFACTORTITLETEXT",          textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-1050, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_DELTAFACTOR'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("DELTAFACTORSLIDER",             slider_typeA,       {'groupOrder': 0, 'xPos': 1400, 'yPos': yPosPoint0-1000, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'IVP_DeltaFactor', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
            self.GUIOs[_objName].addGUIO("DELTAFACTORDISPLAYTEXT",        textBox_typeA,      {'groupOrder': 0, 'xPos': 3950, 'yPos': yPosPoint0-1050, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            yPosPoint1 = yPosPoint0-1400
            self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
        if (True): #Configuration/PIP
            _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"
            yPosPoint0 = yPos_beg-200
            self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_PIPSETUP'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("SWINGRANGETITLETEXT",                           textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 350, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_SWINGRANGE'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("SWINGRANGESLIDER",                              slider_typeA,       {'groupOrder': 0, 'xPos': 1300, 'yPos': yPosPoint0- 300, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'PIP_SwingRange', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
            self.GUIOs[_objName].addGUIO("SWINGRANGEDISPLAYTEXT",                         textBox_typeA,      {'groupOrder': 0, 'xPos': 3850, 'yPos': yPosPoint0- 350, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("NEURALNETWORKCODETITLETEXT",                    textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 700, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NEURALNETWORKCODE'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("NEURALNETWORKCODESELECTIONBOX",                 selectionBox_typeB, {'groupOrder': 0, 'xPos': 1300, 'yPos': yPosPoint0- 700, 'width': 2450, 'height': 250, 'style': 'styleA', 'name': 'PIP_NeuralNetworkCode', 'nDisplay': 10, 'fontSize': 80, 'expansionDir': 0, 'showIndex': True, 'selectionUpdateFunction': self.pageObjectFunctions['ONSELECTIONUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGSELECTIONBOX']})
            self.GUIOs[_objName].addGUIO("NEURALNETWORKCODERELEASEBUTTON",                button_typeA,       {'groupOrder': 0, 'xPos': 3850, 'yPos': yPosPoint0- 700, 'width':  700, 'height': 250, 'style': 'styleA', 'name': 'PIP_NeuralNetworkCodeRelease', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_RELEASE'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_CONFIGBUTTON']})
            self.GUIOs[_objName].addGUIO("NNAALPHAVALUETITLETEXT",                        textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-1050, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NNAALPHA'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("NNAALPHAVALUESLIDER",                           slider_typeA,       {'groupOrder': 0, 'xPos': 1300, 'yPos': yPosPoint0-1000, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'PIP_NNAAlpha', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
            self.GUIOs[_objName].addGUIO("NNAALPHAVALUEDISPLAYTEXT",                      textBox_typeA,      {'groupOrder': 0, 'xPos': 3850, 'yPos': yPosPoint0-1050, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("NNABETAVALUETITLETEXT",                         textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-1400, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NNABETA'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("NNABETAVALUESLIDER",                            slider_typeA,       {'groupOrder': 0, 'xPos': 1300, 'yPos': yPosPoint0-1350, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'PIP_NNABeta', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
            self.GUIOs[_objName].addGUIO("NNABETAVALUEDISPLAYTEXT",                       textBox_typeA,      {'groupOrder': 0, 'xPos': 3850, 'yPos': yPosPoint0-1400, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("CLASSICALALPHAVALUETITLETEXT",                  textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-1750, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_CLASSICALALPHA'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("CLASSICALALPHAVALUESLIDER",                     slider_typeA,       {'groupOrder': 0, 'xPos': 1300, 'yPos': yPosPoint0-1700, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'PIP_ClassicalAlpha', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
            self.GUIOs[_objName].addGUIO("CLASSICALALPHAVALUEDISPLAYTEXT",                textBox_typeA,      {'groupOrder': 0, 'xPos': 3850, 'yPos': yPosPoint0-1750, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("CLASSICALBETAVALUETITLETEXT",                   textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-2100, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_CLASSICALBETA'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("CLASSICALBETAVALUESLIDER",                      slider_typeA,       {'groupOrder': 0, 'xPos': 1300, 'yPos': yPosPoint0-2050, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'PIP_ClassicalBeta', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
            self.GUIOs[_objName].addGUIO("CLASSICALBETAVALUEDISPLAYTEXT",                 textBox_typeA,      {'groupOrder': 0, 'xPos': 3850, 'yPos': yPosPoint0-2100, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("CLASSICALNSAMPLESTITLETEXT",                    textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-2450, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_CLASSICALNSAMPLES'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("CLASSICALNSAMPLESTEXTINPUTBOX",                 textInputBox_typeA, {'groupOrder': 0, 'xPos': 1300, 'yPos': yPosPoint0-2450, 'width':  925, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("CLASSICALSIGMATITLETEXT",                       textBox_typeA,      {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-2450, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_CLASSICALSIGMA'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("CLASSICALSIGMATEXTINPUTBOX",                    textInputBox_typeA, {'groupOrder': 0, 'xPos': 3625, 'yPos': yPosPoint0-2450, 'width':  925, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("CLASSICALACTIVATIONTHRESHOLD1VALUETITLETEXT",   textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-2800, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_CLASSICALACTIVATIONTHRESHOLD1'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("CLASSICALACTIVATIONTHRESHOLD1VALUESLIDER",      slider_typeA,       {'groupOrder': 0, 'xPos': 1300, 'yPos': yPosPoint0-2750, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'PIP_CSActivationThreshold1', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
            self.GUIOs[_objName].addGUIO("CLASSICALACTIVATIONTHRESHOLD1VALUEDISPLAYTEXT", textBox_typeA,      {'groupOrder': 0, 'xPos': 3850, 'yPos': yPosPoint0-2800, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("CLASSICALACTIVATIONTHRESHOLD2VALUETITLETEXT",   textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-3150, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_CLASSICALACTIVATIONTHRESHOLD2'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("CLASSICALACTIVATIONTHRESHOLD2VALUESLIDER",      slider_typeA,       {'groupOrder': 0, 'xPos': 1300, 'yPos': yPosPoint0-3100, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'PIP_CSActivationThreshold2', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
            self.GUIOs[_objName].addGUIO("CLASSICALACTIVATIONTHRESHOLD2VALUEDISPLAYTEXT", textBox_typeA,      {'groupOrder': 0, 'xPos': 3850, 'yPos': yPosPoint0-3150, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("WOIACTIVATIONTHRESHOLDVALUETITLETEXT",          textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-3500, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_WOIACTIVATIONTHRESHOLD'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("WOIACTIVATIONTHRESHOLDVALUESLIDER",             slider_typeA,       {'groupOrder': 0, 'xPos': 1300, 'yPos': yPosPoint0-3450, 'width': 2450, 'height': 150, 'style': 'styleA', 'name': 'PIP_WSActivationThreshold', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']})
            self.GUIOs[_objName].addGUIO("WOIACTIVATIONTHRESHOLDVALUEDISPLAYTEXT",        textBox_typeA,      {'groupOrder': 0, 'xPos': 3850, 'yPos': yPosPoint0-3500, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("ACTIONSIGNALMODETITLETEXT",                     textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-3850, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_ACTIONSIGNALMODE'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("ACTIONSIGNALMODESELECTIONBOX",                  selectionBox_typeB, {'groupOrder': 0, 'xPos': 1300, 'yPos': yPosPoint0-3850, 'width': 3250, 'height': 250, 'style': 'styleA', 'name': 'PIP_ActionSignalMode', 'nDisplay': 10, 'fontSize': 80, 'expansionDir': 1, 'showIndex': False, 'selectionUpdateFunction': self.pageObjectFunctions['ONSELECTIONUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGSELECTIONBOX']})
            _actionSignalModes = {'IMPULSIVE': {'text': 'IMPULSIVE'},
                                  'CYCLIC':    {'text': 'CYCLIC'}}
            self.GUIOs[_objName].GUIOs["ACTIONSIGNALMODESELECTIONBOX"].setSelectionList(selectionList = _actionSignalModes, displayTargets = 'all')
            yPosPoint1 = yPosPoint0-4200
            self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
        if (True): #Configuration/VOL
            _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_VOL"
            yPosPoint0 = yPos_beg-200
            self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_VOLSETUP'), 'fontSize': 80})

            self.GUIOs[_objName].addGUIO("VOLUMETYPETITLETEXT",    textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-350, 'width': 2450, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_VOLUMETYPE'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("VOLUMETYPESELECTIONBOX", selectionBox_typeB,           {'groupOrder': 2, 'xPos': 2550, 'yPos': yPosPoint0-350, 'width': 2000, 'height': 250, 'style': 'styleA', 'nDisplay': 4, 'fontSize': 80})
            volTypes = {'BASE':    {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_VOLTYPE_BASE')},
                        'QUOTE':   {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_VOLTYPE_QUOTE')},
                        'BASETB':  {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_VOLTYPE_BASETB')},
                        'QUOTETB': {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_VOLTYPE_QUOTETB')}}
            self.GUIOs[_objName].GUIOs["VOLUMETYPESELECTIONBOX"].setSelectionList(selectionList = volTypes, displayTargets = 'all')
            self.GUIOs[_objName].addGUIO("MATYPETITLETEXT",    textBox_typeA,                {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-700, 'width': 2450, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_VOLMATYPE'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("MATYPESELECTIONBOX", selectionBox_typeB,           {'groupOrder': 2, 'xPos': 2550, 'yPos': yPosPoint0-700, 'width': 2000, 'height': 250, 'style': 'styleA', 'nDisplay': 3, 'fontSize': 80})
            maTypes = {'SMA': {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_SMA')},
                       'WMA': {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_WMA')},
                       'EMA': {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_EMA')}}
            self.GUIOs[_objName].GUIOs["MATYPESELECTIONBOX"].setSelectionList(selectionList = maTypes, displayTargets = 'all')
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",     passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-1000, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),     'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES",  passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-1000, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'),  'fontSize': 80, 'anchor': 'SW'})
            yPosPoint1 = yPosPoint0-1350
            for lineIndex in range (5):
                lineNumber = lineIndex+1
                self.GUIOs[_objName].addGUIO("VOL_{:d}_LINE".format(lineNumber),     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': 'VOL {:d}'.format(lineNumber), 'fontSize': 80})
                self.GUIOs[_objName].addGUIO("VOL_{:d}_NSAMPLES".format(lineNumber), textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                            'fontSize': 80})
            yPosPoint2 = yPosPoint1-350*5
            self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
        if (True): #Configuration/MMACDSHORT
            _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDSHORT"
            yPosPoint0 = yPos_beg-200
            self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_MMACDSHORTSETUP'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("MMACDSIGNALINTERVALTITLETEXT",    textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 350, 'width': 3000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_MMACDSIGNALINTERVAL'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("MMACDSIGNALINTERVALTEXTINPUTBOX", textInputBox_typeA, {'groupOrder': 0, 'xPos': 3100, 'yPos': yPosPoint0- 350, 'width': 1450, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("MULTIPLIERTITLETEXT",             textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 700, 'width': 3000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_MULTIPLIER'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("MULTIPLIERTEXTINPUTBOX",          textInputBox_typeA, {'groupOrder': 0, 'xPos': 3100, 'yPos': yPosPoint0- 700, 'width': 1450, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("INDEX_COLUMNTITLE1",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-1000, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("NSAMPLES_COLUMNTITLE1", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint0-1000, 'width': 1125, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("INDEX_COLUMNTITLE2",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-1000, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("NSAMPLES_COLUMNTITLE2", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3425, 'yPos': yPosPoint0-1000, 'width': 1125, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
            nMaxLines = 6
            for lineIndex in range (nMaxLines):
                lineNumber = lineIndex+1; rowNumber = math.ceil(lineNumber/2)
                if (lineIndex%2 == 0): coordX = 0
                else:                  coordX = 2325
                self.GUIOs[_objName].addGUIO("MA{:d}_LINE".format(lineNumber),     switch_typeC,       {'groupOrder': 0, 'xPos': coordX,      'yPos': yPosPoint0-1000-rowNumber*350, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': 'MA {:d}'.format(lineNumber), 'fontSize': 80})
                self.GUIOs[_objName].addGUIO("MA{:d}_NSAMPLES".format(lineNumber), textInputBox_typeA, {'groupOrder': 0, 'xPos': coordX+1100, 'yPos': yPosPoint0-1000-rowNumber*350, 'width': 1125, 'height': 250, 'style': 'styleA', 'text': "",                           'fontSize': 80})
            yPosPoint1 = yPosPoint0-1000-math.ceil(nMaxLines/2)*350
            self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
        if (True): #Configuration/MMACDLONG
            _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDLONG"
            yPosPoint0 = yPos_beg-200
            self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_MMACDLONGSETUP'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("MMACDSIGNALINTERVALTITLETEXT",    textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 350, 'width': 3000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_MMACDSIGNALINTERVAL'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("MMACDSIGNALINTERVALTEXTINPUTBOX", textInputBox_typeA, {'groupOrder': 0, 'xPos': 3100, 'yPos': yPosPoint0- 350, 'width': 1450, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("MULTIPLIERTITLETEXT",             textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0- 700, 'width': 3000, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_MULTIPLIER'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("MULTIPLIERTEXTINPUTBOX",          textInputBox_typeA, {'groupOrder': 0, 'xPos': 3100, 'yPos': yPosPoint0- 700, 'width': 1450, 'height': 250, 'style': 'styleA', 'text': "", 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("INDEX_COLUMNTITLE1",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-1000, 'width':                   1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("NSAMPLES_COLUMNTITLE1", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1100, 'yPos': yPosPoint0-1000, 'width':                   1125, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("INDEX_COLUMNTITLE2",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-1000, 'width':                   1000, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("NSAMPLES_COLUMNTITLE2", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3425, 'yPos': yPosPoint0-1000, 'width':                   1125, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
            nMaxLines = 6
            for lineIndex in range (nMaxLines):
                lineNumber = lineIndex+1; rowNumber = math.ceil(lineNumber/2)
                if (lineIndex%2 == 0): coordX = 0
                else:                  coordX = 2325
                self.GUIOs[_objName].addGUIO("MA{:d}_LINE".format(lineNumber),     switch_typeC,       {'groupOrder': 0, 'xPos': coordX,      'yPos': yPosPoint0-1000-rowNumber*350, 'width': 1000, 'height': 250, 'style': 'styleB', 'text': 'MA {:d}'.format(lineNumber), 'fontSize': 80})
                self.GUIOs[_objName].addGUIO("MA{:d}_NSAMPLES".format(lineNumber), textInputBox_typeA, {'groupOrder': 0, 'xPos': coordX+1100, 'yPos': yPosPoint0-1000-rowNumber*350, 'width': 1125, 'height': 250, 'style': 'styleA', 'text': "",                           'fontSize': 80})
            yPosPoint1 = yPosPoint0-1000-math.ceil(nMaxLines/2)*350
            self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint1-350, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
        if (True): #Configuration/DMIxADX
            _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_DMIxADX"
            yPosPoint0 = yPos_beg-200
            self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_DMIxADXSETUP'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
            yPosPoint1 = yPosPoint0-650
            for lineIndex in range (5):
                lineNumber = lineIndex+1
                self.GUIOs[_objName].addGUIO("DMIxADX_{:d}_LINE".format(lineNumber),     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': 'DMIxADX {:d}'.format(lineNumber), 'fontSize': 80})
                self.GUIOs[_objName].addGUIO("DMIxADX_{:d}_NSAMPLES".format(lineNumber), textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                                'fontSize': 80})
            yPosPoint2 = yPosPoint1-350*5
            self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
        if (True): #Configuration/MFI
            _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MFI"
            yPosPoint0 = yPos_beg-200
            self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_MFISETUP'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint0-300, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
            yPosPoint1 = yPosPoint0-650
            for lineIndex in range (5):
                lineNumber = lineIndex+1
                self.GUIOs[_objName].addGUIO("MFI_{:d}_LINE".format(lineNumber),     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleB', 'text': 'MFI {:d}'.format(lineNumber), 'fontSize': 80})
                self.GUIOs[_objName].addGUIO("MFI_{:d}_NSAMPLES".format(lineNumber), textInputBox_typeA, {'groupOrder': 0, 'xPos': 2325, 'yPos': yPosPoint1-350*lineIndex, 'width': 2225, 'height': 250, 'style': 'styleA', 'text': "",                                'fontSize': 80})
            yPosPoint2 = yPosPoint1-350*5
            self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
        if (True): #Configuration/WOI
            _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WOI"
            yPosPoint0 = yPos_beg-200
            self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_WOISETUP'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 1350, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1450, 'yPos': yPosPoint0-300, 'width': 1500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_SIGMA",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3050, 'yPos': yPosPoint0-300, 'width': 1500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_SIGMA'),    'fontSize': 80, 'anchor': 'SW'})
            yPosPoint1 = yPosPoint0-650
            for lineIndex in range (3):
                lineNumber = lineIndex+1
                self.GUIOs[_objName].addGUIO("WOI_{:d}_LINE".format(lineNumber),     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 1350, 'height': 250, 'style': 'styleB', 'text': 'WOI {:d}'.format(lineNumber), 'fontSize': 80})
                self.GUIOs[_objName].addGUIO("WOI_{:d}_NSAMPLES".format(lineNumber), textInputBox_typeA, {'groupOrder': 0, 'xPos': 1450, 'yPos': yPosPoint1-350*lineIndex, 'width': 1500, 'height': 250, 'style': 'styleA', 'text': "",                            'fontSize': 80})
                self.GUIOs[_objName].addGUIO("WOI_{:d}_SIGMA".format(lineNumber),    textInputBox_typeA, {'groupOrder': 0, 'xPos': 3050, 'yPos': yPosPoint1-350*lineIndex, 'width': 1500, 'height': 250, 'style': 'styleA', 'text': "",                            'fontSize': 80})
            yPosPoint2 = yPosPoint1-350*3
            self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
        if (True): #Configuration/NES
            _objName = "TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NES"
            yPosPoint0 = yPos_beg-200
            self.GUIOs[_objName].addGUIO("CONFIGPAGETITLE",      passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint0, 'width': subPageViewSpaceWidth, 'height': 200, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_NESSETUP'), 'fontSize': 80})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_INDEX",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint0-300, 'width': 1350, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_INDEX'),    'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_NSAMPLES", passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 1450, 'yPos': yPosPoint0-300, 'width': 1500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_NSAMPLES'), 'fontSize': 80, 'anchor': 'SW'})
            self.GUIOs[_objName].addGUIO("COLUMNTITLE_SIGMA",    passiveGraphics_wrapperTypeC, {'groupOrder': 0, 'xPos': 3050, 'yPos': yPosPoint0-300, 'width': 1500, 'height': 250, 'style': 'styleB', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_SIGMA'),    'fontSize': 80, 'anchor': 'SW'})
            yPosPoint1 = yPosPoint0-650
            for lineIndex in range (3):
                lineNumber = lineIndex+1
                self.GUIOs[_objName].addGUIO("NES_{:d}_LINE".format(lineNumber),     switch_typeC,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPosPoint1-350*lineIndex, 'width': 1350, 'height': 250, 'style': 'styleB', 'text': 'NES {:d}'.format(lineNumber), 'fontSize': 80})
                self.GUIOs[_objName].addGUIO("NES_{:d}_NSAMPLES".format(lineNumber), textInputBox_typeA, {'groupOrder': 0, 'xPos': 1450, 'yPos': yPosPoint1-350*lineIndex, 'width': 1500, 'height': 250, 'style': 'styleA', 'text': "",                            'fontSize': 80})
                self.GUIOs[_objName].addGUIO("NES_{:d}_SIGMA".format(lineNumber),    textInputBox_typeA, {'groupOrder': 0, 'xPos': 3050, 'yPos': yPosPoint1-350*lineIndex, 'width': 1500, 'height': 250, 'style': 'styleA', 'text': "",                            'fontSize': 80})
            yPosPoint2 = yPosPoint1-350*3
            self.GUIOs[_objName].addGUIO("TOCONFIGSUBPAGE_MAIN", button_typeA, {'groupOrder': 0, 'xPos': 0, 'yPos': yPosPoint2, 'width': subPageViewSpaceWidth, 'height': 250, 'style': 'styleA', 'name': 'navButton_MAIN', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATION_TOMAIN'), 'fontSize': 80, 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']})
        self.pageAuxillaryFunctions['SETANALYSISCONFIGURATIONGUIOS'](self.puVar['analysisConfigurations_default'])
        #---Configuration Control
        self.GUIOs["TRADEMANAGER_BLOCKSUBTITLE_CONFIGURATIONCONTROL"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=3800, yPos=1150, width=4700, height=200, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_CONFIGURATIONCONTROL'), fontSize = 80)
        self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_SELECTIONBOXTITLETEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos=3800, yPos=800, width= 900, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATIONCONTROL_CACLIST'), fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_SELECTIONBOX"]                   = selectionBox_typeB(**inst, groupOrder=2, xPos=4800, yPos=800, width=2900, height= 250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 1, showIndex = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONCODE'])
        self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONREMOVE"]            = button_typeA(**inst,       groupOrder=1, xPos=7800, yPos=800, width= 700, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATIONCONTROL_REMOVE'),  fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATIONCONTROL_REMOVECONFIGURATION'])
        self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONCODETITLETEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos=3800, yPos=450, width= 900, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATIONCONTROL_CACCODE'), fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONCODETEXTINPUTBOX"]  = textInputBox_typeA(**inst, groupOrder=1, xPos=4800, yPos=450, width=2900, height= 250, style="styleA", text="",                                                                                    fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONCODE'])
        self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONADD"]               = button_typeA(**inst,       groupOrder=1, xPos=7800, yPos=450, width= 700, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CONFIGURATIONCONTROL_ADD'),     fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATIONCONTROL_ADDCONFIGURATION'])
        self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONREMOVE"].deactivate()
        #---Currency Analysis Filter
        self.GUIOs["TRADEMANAGER_BLOCKSUBTITLE_CURRENCYANALYSISFILTER"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=8600, yPos=8150, width=3600, height=200, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_CURRENCYANALYSISLIST'), fontSize = 80)
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_SEARCHTITLETEXT"]                  = textBox_typeA(**inst,      groupOrder=1, xPos= 8600, yPos=7800, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISFILTER_SEARCH'),       fontSize=80, textInteractable    =False)
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_SEARCHTITLETEXTINPUTBOX"]          = textInputBox_typeA(**inst, groupOrder=1, xPos= 9400, yPos=7800, width=2800, height=250, style="styleA", text="",                                                                                           fontSize=80, textUpdateFunction  =self.pageObjectFunctions['ONTEXTUPDATE_TRADEMANAGER&CURRENCYANALYSISFILTER_SEARCHTEXT'])
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_SORTBYTITLETEXT"]                  = textBox_typeA(**inst,      groupOrder=1, xPos= 8600, yPos=7450, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISFILTER_SORTBY'),       fontSize=80, textInteractable    =False)
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYID"]            = switch_typeC(**inst,       groupOrder=1, xPos= 9400, yPos=7450, width= 700, height=250, style="styleB", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISFILTER_ID'),           fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_TRADEMANAGER&CURRENCYANALYSISFILTER_SORTBYID'])
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYZER"]      = switch_typeC(**inst,       groupOrder=1, xPos=10200, yPos=7450, width= 700, height=250, style="styleB", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISFILTER_ANALYZER'),     fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_TRADEMANAGER&CURRENCYANALYSISFILTER_SORTBYANALYZER'])
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYSISCODE"]  = switch_typeC(**inst,       groupOrder=1, xPos=11000, yPos=7450, width=1200, height=250, style="styleB", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISFILTER_ANALYSISCODE'), fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_TRADEMANAGER&CURRENCYANALYSISFILTER_SORTBYANALYSISCODE'])
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYSYMBOL"]        = switch_typeC(**inst,       groupOrder=1, xPos= 8600, yPos=7100, width= 700, height=250, style="styleB", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISFILTER_SYMBOL'),       fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_TRADEMANAGER&CURRENCYANALYSISFILTER_SORTBYSYMBOL'])
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYCONFIGURATION"] = switch_typeC(**inst,       groupOrder=1, xPos= 9400, yPos=7100, width=1500, height=250, style="styleB", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISFILTER_CACCODE'),      fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_TRADEMANAGER&CURRENCYANALYSISFILTER_SORTBYCONFIGURATION'])
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYFIRSTKLINE"]    = switch_typeC(**inst,       groupOrder=1, xPos=11000, yPos=7100, width=1200, height=250, style="styleB", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISFILTER_FIRSTKLINE'),   fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_TRADEMANAGER&CURRENCYANALYSISFILTER_SORTBYFIRSTKLINE'])
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYID"].setStatus(status = True, callStatusUpdateFunction = False)
        #---Currency Analysis
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSIS_SELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=1, xPos=8600, yPos=1850, width=3600, height=5150, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = False, singularSelect_allowRelease = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_TRADEMANAGER&ANALYSISLIST_ANALYSISSELECTION'], elementWidths = (450, 1000, 1100, 800)) #3350
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSIS_SELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_INDEX')},
                                                                                                  {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_CACODE')},
                                                                                                  {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_SYMBOL')},
                                                                                                  {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS')}])
        #---Currency Analysis Information
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_VIEWCURRENCYANALYSISCHART"]    = button_typeA(**inst,  groupOrder=1, xPos= 8600, yPos=1500, width=3600, height=250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISINFORMATION_VIEWCURRENCYANALYSISCHART'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&ANALYSISINFORMATION_VIEWCURRENCYANALYSISCHART'])
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_VIEWCURRENCYANALYSISCHART"].deactivate()
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_CONFIGURATIONCODETITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 8600, yPos=1150, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISINFORMATION_CONFIGURATIONCODE'), fontSize=80, textInteractable=True)
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_CONFIGURATIONCODEDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=10200, yPos=1150, width=2000, height=250, style="styleA", text="-",                                                                                                    fontSize=80, textInteractable=True)
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_ALLOCATEDANALYZERTITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 8600, yPos= 800, width=1500, height=250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISINFORMATION_ALLOCATEDANALYZER'), fontSize=80, textInteractable=True)
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_ALLOCATEDANALYZERDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=10200, yPos= 800, width=2000, height=250, style="styleA", text="-",                                                                                                    fontSize=80, textInteractable=True)
        #---Currency Analysis Control
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISCONTROL_REMOVEANALYSIS"] = button_typeA(**inst, groupOrder=1, xPos= 8600, yPos=450, width=3600, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISCONTROL_REMOVEANALYSIS'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&CURRENCYANALYSISCONTROL_REMOVEANALYSIS'])
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISCONTROL_REMOVEANALYSIS"].deactivate()
        #---Trade Configuration
        self.GUIOs["TRADEMANAGER_BLOCKSUBTITLE_TRADECONFIGURATION"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=12300, yPos=8150, width=3600, height=200, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_TRADECONFIGURATION'), fontSize = 80)
        self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"] = subPageBox_typeA(**inst, groupOrder=1, xPos=12300, yPos=1450, width=3600, height=6600, style=None, useScrollBar_V=True, useScrollBar_H=False)
        _objName = "TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"
        yPos_beg = 20000
        subPageViewSpaceWidth = self.GUIOs["TRADEMANAGER_BLOCKSUBTITLE_TRADECONFIGURATION"].width-150
        if (True):
            #Base
            if (True):
                self.GUIOs[_objName].addGUIO("LEVERAGETITLETEXT",      textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg- 350, 'width':  700, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_LEVERAGE'),      'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("LEVERAGESLIDER",         slider_typeA,       {'groupOrder': 0, 'xPos':  800, 'yPos': yPos_beg- 300, 'width': 1950, 'height': 150, 'style': 'styleA', 'name': 'TC_Leverage', 'valueUpdateFunction': self.pageObjectFunctions['ONVALUEUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUESLIDER']})
                self.GUIOs[_objName].addGUIO("LEVERAGEDISPLAYTEXT",    textBox_typeA,      {'groupOrder': 0, 'xPos': 2850, 'yPos': yPos_beg- 350, 'width':  600, 'height': 250, 'style': 'styleA', 'text': "",                                                                                        'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("MARGINTYPETITLETEXT",    textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg- 700, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_MARGINTYPE'),    'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("MARGINTYPESELECTIONBOX", selectionBox_typeB, {'groupOrder': 2, 'xPos': 1400, 'yPos': yPos_beg- 700, 'width': 2050, 'height': 250, 'style': 'styleA', 'nDisplay': 2, 'fontSize': 80, 'selectionUpdateFunction': None})
                marginTypes = {'CROSSED':  {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_MARGINTYPE_CROSSED')},
                               'ISOLATED': {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_MARGINTYPE_ISOLATED')}}
                self.GUIOs[_objName].GUIOs["MARGINTYPESELECTIONBOX"].setSelectionList(selectionList = marginTypes, displayTargets = 'all')
                self.GUIOs[_objName].addGUIO("DIRECTIONTITLETEXT",    textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-1050, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_DIRECTION'), 'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("DIRECTIONSELECTIONBOX", selectionBox_typeB, {'groupOrder': 2, 'xPos': 1400, 'yPos': yPos_beg-1050, 'width': 2050, 'height': 250, 'style': 'styleA', 'nDisplay': 3, 'fontSize': 80, 'selectionUpdateFunction': None})
                directionTypes = {'LONG':  {'text': "LONG"},
                                  'SHORT': {'text': "SHORT"},
                                  'BOTH':  {'text': "BOTH"}}
                self.GUIOs[_objName].GUIOs["DIRECTIONSELECTIONBOX"].setSelectionList(selectionList = directionTypes, displayTargets = 'all')
                self.GUIOs[_objName].addGUIO("TCMODETITLETEXT",    textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-1400, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TCMODE'), 'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("TCMODESELECTIONBOX", selectionBox_typeB, {'groupOrder': 2, 'xPos': 1400, 'yPos': yPos_beg-1400, 'width': 2050, 'height': 250, 'style': 'styleA', 'nDisplay': 2, 'fontSize': 80, 'name': 'TC_TCMode', 'selectionUpdateFunction': self.pageObjectFunctions['ONSELECTIONUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUESELECTIONBOX']})
                tcModes = {'TS':   {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TCMODE_TS')},
                           'RQPM': {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TCMODE_RQPM')}}
                self.GUIOs[_objName].GUIOs["TCMODESELECTIONBOX"].setSelectionList(selectionList = tcModes, displayTargets = 'all')
            #Trade Scenario
            if (True):
                self.GUIOs[_objName].addGUIO("TS_FULLSTOPLOSSIMMEDIATETITLETEXT",     textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-1750, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_FULLSTOPLOSSIMMEDIATE'), 'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("TS_FULLSTOPLOSSIMMEDIATETEXTINPUTBOX",  textInputBox_typeA, {'groupOrder': 0, 'xPos': 1400, 'yPos': yPos_beg-1750, 'width': 1550, 'height': 250, 'style': 'styleA', 'text': "",                                                                                                'fontSize': 80, 'name': 'TC_TS_FSLIMMED',      'textUpdateFunction': self.pageObjectFunctions['ONTEXTUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUETEXT']})
                self.GUIOs[_objName].addGUIO("TS_FULLSTOPLOSSIMMEDIATEUNITTEXT",      textBox_typeA,      {'groupOrder': 0, 'xPos': 3050, 'yPos': yPos_beg-1750, 'width':  400, 'height': 250, 'style': 'styleA', 'text': "%",                                                                                               'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("TS_FULLSTOPLOSSCLOSETITLETEXT",         textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-2100, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_FULLSTOPLOSSCLOSE'),     'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("TS_FULLSTOPLOSSCLOSETEXTINPUTBOX",      textInputBox_typeA, {'groupOrder': 0, 'xPos': 1400, 'yPos': yPos_beg-2100, 'width': 1550, 'height': 250, 'style': 'styleA', 'text': "",                                                                                                'fontSize': 80, 'name': 'TC_TS_FSLCLOSE',      'textUpdateFunction': self.pageObjectFunctions['ONTEXTUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUETEXT']})
                self.GUIOs[_objName].addGUIO("TS_FULLSTOPLOSSCLOSEUNITTEXT",          textBox_typeA,      {'groupOrder': 0, 'xPos': 3050, 'yPos': yPos_beg-2100, 'width':  400, 'height': 250, 'style': 'styleA', 'text': "%",                                                                                               'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("TS_WEIGHTREDUCETITLETEXT",              textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-2450, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_WEIGHTREDUCE'),          'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("TS_WEIGHTREDUCEACTIVATIONTEXTINPUTBOX", textInputBox_typeA, {'groupOrder': 0, 'xPos': 1400, 'yPos': yPos_beg-2450, 'width':  475, 'height': 250, 'style': 'styleA', 'text': "",                                                                                                'fontSize': 80, 'name': 'TC_TS_WR_Activation', 'textUpdateFunction': self.pageObjectFunctions['ONTEXTUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUETEXT']})
                self.GUIOs[_objName].addGUIO("TS_WEIGHTREDUCEACTIVATIONUNITTEXT",     textBox_typeA,      {'groupOrder': 0, 'xPos': 1975, 'yPos': yPos_beg-2450, 'width':  400, 'height': 250, 'style': 'styleA', 'text': "%",                                                                                               'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("TS_WEIGHTREDUCEAMOUNTTEXTINPUTBOX",     textInputBox_typeA, {'groupOrder': 0, 'xPos': 2475, 'yPos': yPos_beg-2450, 'width':  475, 'height': 250, 'style': 'styleA', 'text': "",                                                                                                'fontSize': 80, 'name': 'TC_TS_WR_Amount',     'textUpdateFunction': self.pageObjectFunctions['ONTEXTUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUETEXT']})
                self.GUIOs[_objName].addGUIO("TS_WEIGHTREDUCEAMOUNTUNITTEXT",         textBox_typeA,      {'groupOrder': 0, 'xPos': 3050, 'yPos': yPos_beg-2450, 'width':  400, 'height': 250, 'style': 'styleA', 'text': "%",                                                                                               'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("TS_REACHANDFALLTITLETEXT",              textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-2800, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_REACHANDFALL'),          'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("TS_REACHANDFALL1TEXTINPUTBOX",          textInputBox_typeA, {'groupOrder': 0, 'xPos': 1400, 'yPos': yPos_beg-2800, 'width':  475, 'height': 250, 'style': 'styleA', 'text': "",                                                                                                'fontSize': 80, 'name': 'TC_TS_RAF',           'textUpdateFunction': self.pageObjectFunctions['ONTEXTUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUETEXT']})
                self.GUIOs[_objName].addGUIO("TS_REACHANDFALL1UNITTEXT",              textBox_typeA,      {'groupOrder': 0, 'xPos': 1975, 'yPos': yPos_beg-2800, 'width':  400, 'height': 250, 'style': 'styleA', 'text': "%",                                                                                               'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("TS_REACHANDFALL2TEXTINPUTBOX",          textInputBox_typeA, {'groupOrder': 0, 'xPos': 2475, 'yPos': yPos_beg-2800, 'width':  475, 'height': 250, 'style': 'styleA', 'text': "",                                                                                                'fontSize': 80, 'name': 'TC_TS_RAF',           'textUpdateFunction': self.pageObjectFunctions['ONTEXTUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUETEXT']})
                self.GUIOs[_objName].addGUIO("TS_REACHANDFALL2UNITTEXT",              textBox_typeA,      {'groupOrder': 0, 'xPos': 3050, 'yPos': yPos_beg-2800, 'width':  400, 'height': 250, 'style': 'styleA', 'text': "%",                                                                                               'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("TS_TRADESCENARIOTYPETITLETEXT",         textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-3150, 'width': 1300, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO'),         'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("TS_TRADESCENARIOTYPESELECTIONBOX",      selectionBox_typeB, {'groupOrder': 2, 'xPos': 1400, 'yPos': yPos_beg-3150, 'width': 2050, 'height': 250, 'style': 'styleA', 'nDisplay': 3, 'fontSize': 80, 'name': 'TC_TS_TradeScenarioType', 'selectionUpdateFunction': self.pageObjectFunctions['ONSELECTIONUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUESELECTIONBOX']})
                tradeScenarioTypes = {'ENTRY': {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_ENTRY')},
                                      'EXIT':  {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_EXIT')},
                                      'PSL':   {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_PSL')}}
                self.GUIOs[_objName].GUIOs["TS_TRADESCENARIOTYPESELECTIONBOX"].setSelectionList(selectionList = tradeScenarioTypes, displayTargets = 'all')
                self.GUIOs[_objName].addGUIO("TS_TRADESCENARIOSELECTIONBOX", selectionBox_typeC, {'groupOrder': 2, 'xPos': 0, 'yPos': yPos_beg-5600, 'width': 3450, 'height': 2350, 'style': 'styleA', 'fontSize': 80, 'elementHeight': 250, 'multiSelect': False, 'singularSelect_allowRelease': True, 'name': 'TC_TS_TradeScenario', 'selectionUpdateFunction': self.pageObjectFunctions['ONSELECTIONUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUESELECTIONBOX'],
                                                                                                  'elementWidths': (800, 1200, 1200)})
                self.GUIOs[_objName].GUIOs["TS_TRADESCENARIOSELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_ST_INDEX')},
                                                                                                            {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_ST_PD')},
                                                                                                            {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_ST_QD')}])
                self.GUIOs[_objName].addGUIO("TS_PDTITLETEXT",               textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-5950, 'width': 2000, 'height':  250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_PD'),      'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("TS_PDTEXTINPUTBOX",            textInputBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': yPos_beg-5950, 'width':  750, 'height':  250, 'style': 'styleA', 'text': "",                                                                                                'fontSize': 80, 'name': 'TC_TS_PD', 'textUpdateFunction': self.pageObjectFunctions['ONTEXTUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUETEXT']})
                self.GUIOs[_objName].addGUIO("TS_PDUNITTEXT",                textBox_typeA,      {'groupOrder': 0, 'xPos': 2950, 'yPos': yPos_beg-5950, 'width':  500, 'height':  250, 'style': 'styleA', 'text': "%",                                                                                               'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("TS_QDTITLETEXT",               textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-6300, 'width': 2000, 'height':  250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_QD'),      'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("TS_QDTEXTINPUTBOX",            textInputBox_typeA, {'groupOrder': 0, 'xPos': 2100, 'yPos': yPos_beg-6300, 'width':  750, 'height':  250, 'style': 'styleA', 'text': "",                                                                                                'fontSize': 80, 'name': 'TC_TS_QD', 'textUpdateFunction': self.pageObjectFunctions['ONTEXTUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUETEXT']})
                self.GUIOs[_objName].addGUIO("TS_QDUNITTEXT",                textBox_typeA,      {'groupOrder': 0, 'xPos': 2950, 'yPos': yPos_beg-6300, 'width':  500, 'height':  250, 'style': 'styleA', 'text': "%",                                                                                               'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("TS_TRADESCENARIOADDBUTTON",    button_typeA,       {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-6650, 'width': 1450, 'height':  250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_ADD'),    'fontSize': 80, 'name': 'TC_TS_AddTradeScenario',    'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUEBUTTON']})
                self.GUIOs[_objName].addGUIO("TS_TRADESCENARIOEDITBUTTON",   button_typeA,       {'groupOrder': 0, 'xPos': 1550, 'yPos': yPos_beg-6650, 'width':  900, 'height':  250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_EDIT'),   'fontSize': 80, 'name': 'TC_TS_EditTradeScenario',   'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUEBUTTON']})
                self.GUIOs[_objName].addGUIO("TS_TRADESCENARIOREMOVEBUTTON", button_typeA,       {'groupOrder': 0, 'xPos': 2550, 'yPos': yPos_beg-6650, 'width':  900, 'height':  250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_TRADESCENARIO_REMOVE'), 'fontSize': 80, 'name': 'TC_TS_RemoveTradeScenario', 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUEBUTTON']})
                self.GUIOs[_objName].GUIOs["TS_TRADESCENARIOTYPESELECTIONBOX"].setSelected(itemKey = 'ENTRY', callSelectionUpdateFunction = True)
                self.puVar['tradeConfiguration_guioGroups']['TS'] = ["TS_FULLSTOPLOSSIMMEDIATETITLETEXT",
                                                                     "TS_FULLSTOPLOSSIMMEDIATETEXTINPUTBOX",
                                                                     "TS_FULLSTOPLOSSIMMEDIATEUNITTEXT",
                                                                     "TS_FULLSTOPLOSSCLOSETITLETEXT",
                                                                     "TS_FULLSTOPLOSSCLOSETEXTINPUTBOX",
                                                                     "TS_FULLSTOPLOSSCLOSEUNITTEXT",
                                                                     "TS_WEIGHTREDUCETITLETEXT",
                                                                     "TS_WEIGHTREDUCEACTIVATIONTEXTINPUTBOX",
                                                                     "TS_WEIGHTREDUCEACTIVATIONUNITTEXT",
                                                                     "TS_WEIGHTREDUCEAMOUNTTEXTINPUTBOX",
                                                                     "TS_WEIGHTREDUCEAMOUNTUNITTEXT",
                                                                     "TS_REACHANDFALLTITLETEXT",
                                                                     "TS_REACHANDFALL1TEXTINPUTBOX",
                                                                     "TS_REACHANDFALL1UNITTEXT",
                                                                     "TS_REACHANDFALL2TEXTINPUTBOX",
                                                                     "TS_REACHANDFALL2UNITTEXT",
                                                                     "TS_TRADESCENARIOTYPETITLETEXT",
                                                                     "TS_TRADESCENARIOTYPESELECTIONBOX",
                                                                     "TS_TRADESCENARIOSELECTIONBOX",
                                                                     "TS_PDTITLETEXT",
                                                                     "TS_PDTEXTINPUTBOX",
                                                                     "TS_PDUNITTEXT",
                                                                     "TS_QDTITLETEXT",
                                                                     "TS_QDTEXTINPUTBOX",
                                                                     "TS_QDUNITTEXT",
                                                                     "TS_TRADESCENARIOADDBUTTON",
                                                                     "TS_TRADESCENARIOEDITBUTTON",
                                                                     "TS_TRADESCENARIOREMOVEBUTTON"]
            #RQPM
            if (True):
                self.GUIOs[_objName].addGUIO("RQPM_EXITONIMPULSETITLETEXT",            textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-1750, 'width': 2050, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_EXITONIMPULSE'),         'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("RQPM_EXITONIMPULSETEXTINPUTBOX",         textInputBox_typeA, {'groupOrder': 0, 'xPos': 2150, 'yPos': yPos_beg-1750, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "",                                                                                                'fontSize': 80, 'name': 'TC_RQPM_EOI', 'textUpdateFunction': self.pageObjectFunctions['ONTEXTUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUETEXT']})
                self.GUIOs[_objName].addGUIO("RQPM_EXITONIMPULSEUNITTEXT",             textBox_typeA,      {'groupOrder': 0, 'xPos': 2950, 'yPos': yPos_beg-1750, 'width':  500, 'height': 250, 'style': 'styleA', 'text': "%",                                                                                               'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("RQPM_EXITONALIGNEDTITLETEXT",            textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-2100, 'width': 2050, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_EXITONALIGNED'),         'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("RQPM_EXITONALIGNEDTEXTINPUTBOX",         textInputBox_typeA, {'groupOrder': 0, 'xPos': 2150, 'yPos': yPos_beg-2100, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "",                                                                                                'fontSize': 80, 'name': 'TC_RQPM_EOA', 'textUpdateFunction': self.pageObjectFunctions['ONTEXTUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUETEXT']})
                self.GUIOs[_objName].addGUIO("RQPM_EXITONALIGNEDUNITTEXT",             textBox_typeA,      {'groupOrder': 0, 'xPos': 2950, 'yPos': yPos_beg-2100, 'width':  500, 'height': 250, 'style': 'styleA', 'text': "%",                                                                                               'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("RQPM_EXITONPROFITABLETITLETEXT",         textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-2450, 'width': 2050, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_EXITONPROFITABLE'),      'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("RQPM_EXITONPROFITABLETEXTINPUTBOX",      textInputBox_typeA, {'groupOrder': 0, 'xPos': 2150, 'yPos': yPos_beg-2450, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "",                                                                                                'fontSize': 80, 'name': 'TC_RQPM_EOP', 'textUpdateFunction': self.pageObjectFunctions['ONTEXTUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUETEXT']})
                self.GUIOs[_objName].addGUIO("RQPM_EXITONPROFITABLEUNITTEXT",          textBox_typeA,      {'groupOrder': 0, 'xPos': 2950, 'yPos': yPos_beg-2450, 'width':  500, 'height': 250, 'style': 'styleA', 'text': "%",                                                                                               'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("RQPM_FULLSTOPLOSSIMMEDIATETITLETEXT",    textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-2800, 'width': 2050, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_FULLSTOPLOSSIMMEDIATE'), 'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("RQPM_FULLSTOPLOSSIMMEDIATETEXTINPUTBOX", textInputBox_typeA, {'groupOrder': 0, 'xPos': 2150, 'yPos': yPos_beg-2800, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "",                                                                                                'fontSize': 80, 'name': 'TC_RQPM_FSLIMMED', 'textUpdateFunction': self.pageObjectFunctions['ONTEXTUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUETEXT']})
                self.GUIOs[_objName].addGUIO("RQPM_FULLSTOPLOSSIMMEDIATEUNITTEXT",     textBox_typeA,      {'groupOrder': 0, 'xPos': 2950, 'yPos': yPos_beg-2800, 'width':  500, 'height': 250, 'style': 'styleA', 'text': "%",                                                                                               'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("RQPM_FULLSTOPLOSSCLOSETITLETEXT",        textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-3150, 'width': 2050, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_FULLSTOPLOSSCLOSE'),     'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("RQPM_FULLSTOPLOSSCLOSETEXTINPUTBOX",     textInputBox_typeA, {'groupOrder': 0, 'xPos': 2150, 'yPos': yPos_beg-3150, 'width':  700, 'height': 250, 'style': 'styleA', 'text': "",                                                                                                'fontSize': 80, 'name': 'TC_RQPM_FSLCLOSE', 'textUpdateFunction': self.pageObjectFunctions['ONTEXTUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUETEXT']})
                self.GUIOs[_objName].addGUIO("RQPM_FULLSTOPLOSSCLOSEUNITTEXT",         textBox_typeA,      {'groupOrder': 0, 'xPos': 2950, 'yPos': yPos_beg-3150, 'width':  500, 'height': 250, 'style': 'styleA', 'text': "%",                                                                                               'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("RQPM_FUNCTIONTYPETITLETEXT",             textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-3500, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_FUNCTIONTYPE'), 'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("RQPM_FUNCTIONTYPESELECTIONBOX",          selectionBox_typeB, {'groupOrder': 2, 'xPos': 1300, 'yPos': yPos_beg-3500, 'width': 2150, 'height': 250, 'style': 'styleA', 'nDisplay': 10, 'fontSize': 80, 'showIndex': True, 'name': 'TC_RQPM_FunctionType', 'selectionUpdateFunction': self.pageObjectFunctions['ONSELECTIONUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUESELECTIONBOX']})
                _rqpmFunctionTypes = dict()
                for _functionType in atmEta_RQPMFunctions.RQPMFUNCTIONS_DESCRIPTORS: _rqpmFunctionTypes[_functionType] = {'text': _functionType, 'textAnchor': 'W'}
                self.GUIOs[_objName].GUIOs["RQPM_FUNCTIONTYPESELECTIONBOX"].setSelectionList(selectionList = _rqpmFunctionTypes, displayTargets = 'all')
                _firstRQPMFunctionType = None
                for _functionType in atmEta_RQPMFunctions.RQPMFUNCTIONS_DESCRIPTORS: _firstRQPMFunctionType = _functionType; break
                self.GUIOs[_objName].addGUIO("RQPM_FUNCTIONSIDETITLETEXT",            textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-3850, 'width': 1200, 'height': 250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_FUNCTIONSIDE'),      'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("RQPM_FUNCTIONSIDESELECTIONBOX",         selectionBox_typeB, {'groupOrder': 2, 'xPos': 1300, 'yPos': yPos_beg-3850, 'width': 2150, 'height': 250, 'style': 'styleA', 'nDisplay': 10, 'fontSize': 80, 'showIndex': False, 'name': 'TC_RQPM_FunctionSide', 'selectionUpdateFunction': self.pageObjectFunctions['ONSELECTIONUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUESELECTIONBOX']})
                _functionSides = {'LONG':  {'text': 'LONG'},
                                  'SHORT': {'text': 'SHORT'}}
                self.GUIOs[_objName].GUIOs["RQPM_FUNCTIONSIDESELECTIONBOX"].setSelectionList(selectionList = _functionSides, displayTargets = 'all')
                self.GUIOs[_objName].addGUIO("RQPM_PARAMETERSELECTIONBOX",            selectionBox_typeC, {'groupOrder': 2, 'xPos': 0, 'yPos': yPos_beg-6300, 'width': 3450, 'height': 2350, 'style': 'styleA', 'fontSize': 80, 'elementHeight': 250, 'multiSelect': False, 'singularSelect_allowRelease': True, 'name': 'TC_RQPM_Parameter', 'selectionUpdateFunction': self.pageObjectFunctions['ONSELECTIONUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUESELECTIONBOX'],
                                                                                                           'elementWidths': (600, 1600, 1000)})
                self.GUIOs[_objName].GUIOs["RQPM_PARAMETERSELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_PARAMETER_INDEX')},
                                                                                                          {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_PARAMETER_NAME')},
                                                                                                          {'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_PARAMETER_VALUE')}])
                self.GUIOs[_objName].addGUIO("RQPM_PARAMETERTITLETEXT",               textBox_typeA,      {'groupOrder': 0, 'xPos':    0, 'yPos': yPos_beg-6650, 'width':  800, 'height':  250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_PARAMETER'), 'fontSize': 80, 'textInteractable': False})
                self.GUIOs[_objName].addGUIO("RQPM_PARAMETERNAMEDISPLAYTEXT",         textBox_typeA,      {'groupOrder': 0, 'xPos':  900, 'yPos': yPos_beg-6650, 'width': 1150, 'height':  250, 'style': 'styleA', 'text': "-",                                                                                   'fontSize': 80, 'textInteractable': True})
                self.GUIOs[_objName].addGUIO("RQPM_PARAMETERSETTEXTINPUTBOX",         textInputBox_typeA, {'groupOrder': 0, 'xPos': 2150, 'yPos': yPos_beg-6650, 'width':  700, 'height':  250, 'style': 'styleA', 'text': "",                                                                                    'fontSize': 80, 'name': 'TC_RQPM_Parameter', 'textUpdateFunction': self.pageObjectFunctions['ONTEXTUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUETEXT']})
                self.GUIOs[_objName].GUIOs["RQPM_PARAMETERSETTEXTINPUTBOX"].deactivate()
                self.GUIOs[_objName].addGUIO("RQPM_PARAMETERSETBUTTON",               button_typeA,       {'groupOrder': 0, 'xPos': 2950, 'yPos': yPos_beg-6650, 'width':  500, 'height':  250, 'style': 'styleA', 'text': self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATION_SET'),       'fontSize': 80, 'name': 'TC_RQPM_SetParameter', 'releaseFunction': self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUEBUTTON']})
                self.GUIOs[_objName].GUIOs["RQPM_PARAMETERSETBUTTON"].deactivate()
                self.GUIOs[_objName].GUIOs["RQPM_FUNCTIONTYPESELECTIONBOX"].setSelected(itemKey = _firstRQPMFunctionType, callSelectionUpdateFunction = True)
                self.puVar['tradeConfiguration_guioGroups']['RQPM'] = ["RQPM_EXITONIMPULSETITLETEXT",
                                                                       "RQPM_EXITONIMPULSETEXTINPUTBOX",
                                                                       "RQPM_EXITONIMPULSEUNITTEXT",
                                                                       "RQPM_EXITONALIGNEDTITLETEXT",
                                                                       "RQPM_EXITONALIGNEDTEXTINPUTBOX",
                                                                       "RQPM_EXITONALIGNEDUNITTEXT",
                                                                       "RQPM_EXITONPROFITABLETITLETEXT",
                                                                       "RQPM_EXITONPROFITABLETEXTINPUTBOX",
                                                                       "RQPM_EXITONPROFITABLEUNITTEXT",
                                                                       "RQPM_FULLSTOPLOSSIMMEDIATETITLETEXT",
                                                                       "RQPM_FULLSTOPLOSSIMMEDIATETEXTINPUTBOX",
                                                                       "RQPM_FULLSTOPLOSSIMMEDIATEUNITTEXT",
                                                                       "RQPM_FULLSTOPLOSSCLOSETITLETEXT",
                                                                       "RQPM_FULLSTOPLOSSCLOSETEXTINPUTBOX",
                                                                       "RQPM_FULLSTOPLOSSCLOSEUNITTEXT",
                                                                       "RQPM_FUNCTIONTYPETITLETEXT",
                                                                       "RQPM_FUNCTIONTYPESELECTIONBOX",
                                                                       "RQPM_FUNCTIONSIDETITLETEXT",
                                                                       "RQPM_FUNCTIONSIDESELECTIONBOX",
                                                                       "RQPM_PARAMETERSELECTIONBOX",
                                                                       "RQPM_PARAMETERTITLETEXT",
                                                                       "RQPM_PARAMETERNAMEDISPLAYTEXT",
                                                                       "RQPM_PARAMETERSETTEXTINPUTBOX",
                                                                       "RQPM_PARAMETERSETBUTTON"]
        self.pageAuxillaryFunctions['SETTRADECONFIGURATIONGUIOS'](self.puVar['tradeConfigurations_default'])
        #---Trade Configuration Control
        self.GUIOs["TRADEMANAGER_BLOCKSUBTITLE_TRADECONFIGURATIONCONTROL"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=12300, yPos=1150, width=3600, height=200, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:BLOCKSUBTITLE_TRADECONFIGURATIONCONTROL'), fontSize = 80)
        self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_SELECTIONBOXTITLETEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos=12300, yPos=800, width= 800, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONS'),    fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_SELECTIONBOX"]                   = selectionBox_typeB(**inst, groupOrder=2, xPos=13200, yPos=800, width=2000, height= 250, style="styleA", nDisplay = 10, fontSize = 80, expansionDir = 1, showIndex = True, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONCODE'])
        self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONREMOVE"]            = button_typeA(**inst,       groupOrder=1, xPos=15300, yPos=800, width= 600, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATIONCONTROL_REMOVE'),            fontSize=80, releaseFunction   =self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&TRADECONFIGURATIONCONTROL_REMOVECONFIGURATION'])
        self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONCODETITLETEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos=12300, yPos=450, width= 800, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONCODE'), fontSize=80, textInteractable=False)
        self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONCODETEXTINPUTBOX"]  = textInputBox_typeA(**inst, groupOrder=1, xPos=13200, yPos=450, width=2000, height= 250, style="styleA", text="",                                                                                                   fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONCODE'])
        self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONADD"]               = button_typeA(**inst,       groupOrder=1, xPos=15300, yPos=450, width= 600, height= 250, style="styleA", text=self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&TRADECONFIGURATIONCONTROL_ADD'),               fontSize=80, releaseFunction   =self.pageObjectFunctions['ONBUTTONRELEASE_TRADEMANAGER&TRADECONFIGURATIONCONTROL_ADDCONFIGURATION'])
        self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONREMOVE"].deactivate()
        #Message Display Text
        self.GUIOs["MESSAGEDISPLAYTEXT_DISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=100, yPos=100, width=15800, height= 250, style="styleA", text="-", fontSize=80, textInteractable=True)

    elif (self.displaySpaceDefiner['ratio'] == '21:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 21000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
    elif (self.displaySpaceDefiner['ratio'] == '32:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 32000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
#SETUP PAGE <MAIN> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <LOAD> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageLoadFunction(self):
    #FAR Registration
    #---DATAMANAGER
    self.ipcA.addFARHandler('onCurrenciesUpdate', self.pageAuxillaryFunctions['_FAR_ONCURRENCIESUPDATE'], executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
    #---TRADEMANAGER
    self.ipcA.addFARHandler('onAnalyzerCentralUpdate',               self.pageAuxillaryFunctions['_FAR_ONANALYZERCENTRALUPDATE'],       executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
    self.ipcA.addFARHandler('onCurrencyAnalysisConfigurationUpdate', self.pageAuxillaryFunctions['_FAR_ONANALYSISCONFIGURATIONUPDATE'], executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
    self.ipcA.addFARHandler('onCurrencyAnalysisUpdate',              self.pageAuxillaryFunctions['_FAR_ONCURRENCYANALYSISUPDATE'],      executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
    self.ipcA.addFARHandler('onTradeConfigurationUpdate',            self.pageAuxillaryFunctions['_FAR_ONTRADECONFIGURATIONUPDATE'],    executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)

    #Get data via PRD
    self.puVar['currencies']             = self.ipcA.getPRD(processName = 'DATAMANAGER',  prdAddress = 'CURRENCIES').copy()
    self.puVar['analyzerCentral']        = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = 'ANALYZERCENTRAL').copy()
    self.puVar['analysisConfigurations'] = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = 'CURRENCYANALYSISCONFIGURATIONS').copy()
    self.puVar['currencyAnalysis']       = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = 'CURRENCYANALYSIS').copy()
    self.puVar['tradeConfigurations']    = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = 'TRADECONFIGURATIONS').copy()

    #GUIO Update
    self.pageAuxillaryFunctions['SETCURRENCYLIST']()                           #Market&Currencies List Update
    self.pageAuxillaryFunctions['UPDATECURRENCYINFO']()                        #Market&Currencies Selected Currency Info Update
    self.pageAuxillaryFunctions['UPDATEANALYZERCENTRALINFO'](updateAll = True) #TradeManager&Analyzers
    self.pageAuxillaryFunctions['SETANALYSISCONFIGURATIONLIST']()              #Market&Currencies and TradeManager&ConfigurationControl Analysis Configurations List Update
    self.pageAuxillaryFunctions['SETCURRENCYANALYSISLIST']()                   #TradeManager&CurrencyAnalysisList
    self.pageAuxillaryFunctions['UPDATECURRENCYANALYSISINFO']()                #TradeManager&CurrencyAnalysisInformation
    self.pageAuxillaryFunctions['SETTRADECONFIGURATIONLIST']()                 #TradeManager&TradeConfiguration
#SETUP PAGE <LOAD> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <ESCAPE> --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageEscapeFunction(self):
    self.ipcA.removeFARHandler('onCurrenciesUpdate')
    self.ipcA.removeFARHandler('onAnalyzerCentralUpdate')
    self.ipcA.removeFARHandler('onCurrencyAnalysisConfigurationUpdate')
    self.ipcA.removeFARHandler('onCurrencyAnalysisUpdate')
    self.ipcA.removeFARHandler('onTradeConfigurationUpdate')
#SETUP PAGE <ESCAPE> END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <PROCESS> -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageProcessFunction(self, t_elapsed_ns, onLoad = False):
    pass
#SETUP PAGE <PROCESS> END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#OBJECT FUNCTIONS -----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateObjectFunctions(self):
    objFunctions = dict()

    #<Page Navigation>
    def __pageMove_DASHBOARD(objInstance, **kwargs): 
        self.sysFunctions['LOADPAGE']('DASHBOARD')
    objFunctions['PAGEMOVE_DASHBOARD'] = __pageMove_DASHBOARD

    #<Market&Filter>
    def __onTextUpdate_Market_Filter_SearchText(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONCURRENCYFILTERUPDATE']()
    def __onSwitchStatusUpdate_Market_Filter_TradingTrue(objInstance, **kwargs):
        if (self.GUIOs["MARKET&FILTER_FILTERSWITCH_TRADINGFALSE"].getStatus() == True): self.GUIOs["MARKET&FILTER_FILTERSWITCH_TRADINGFALSE"].setStatus(status = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['ONCURRENCYFILTERUPDATE']()
    def __onSwitchStatusUpdate_Market_Filter_TradingFalse(objInstance, **kwargs):
        if (self.GUIOs["MARKET&FILTER_FILTERSWITCH_TRADINGTRUE"].getStatus() == True): self.GUIOs["MARKET&FILTER_FILTERSWITCH_TRADINGTRUE"].setStatus(status = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['ONCURRENCYFILTERUPDATE']()
    def __onSwitchStatusUpdate_Market_Filter_MinNumberOfKlines(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONCURRENCYFILTERUPDATE']()
    def __onTextUpdate_Market_Filter_MinNumberOfKlines(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONCURRENCYFILTERUPDATE']()
    def __onSwitchStatusUpdate_Market_Filter_SortByID(objInstance, **kwargs):
        if (self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYSYMBOL"].getStatus()     == True): self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status     = False, callStatusUpdateFunction = False)
        if (self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].getStatus() == True): self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].setStatus(status = False, callStatusUpdateFunction = False)
        if (self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYID"].getStatus() == False):        self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYID"].setStatus(status         = True,  callStatusUpdateFunction = False)
        else:                                                                               self.pageAuxillaryFunctions['ONCURRENCYFILTERUPDATE']()
    def __onSwitchStatusUpdate_Market_Filter_SortBySymbol(objInstance, **kwargs):
        if (self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYID"].getStatus()         == True): self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYID"].setStatus(status         = False, callStatusUpdateFunction = False)
        if (self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].getStatus() == True): self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].setStatus(status = False, callStatusUpdateFunction = False)
        if (self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYSYMBOL"].getStatus() == False):    self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status     = True,  callStatusUpdateFunction = False)
        else:                                                                               self.pageAuxillaryFunctions['ONCURRENCYFILTERUPDATE']()
    def __onSwitchStatusUpdate_Market_Filter_SortByFirstKline(objInstance, **kwargs):
        if (self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYSYMBOL"].getStatus() == True):      self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status     = False, callStatusUpdateFunction = False)
        if (self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYID"].getStatus()     == True):      self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYID"].setStatus(status         = False, callStatusUpdateFunction = False)
        if (self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].getStatus() == False): self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].setStatus(status = True,  callStatusUpdateFunction = False)
        else:                                                                                self.pageAuxillaryFunctions['ONCURRENCYFILTERUPDATE']()
    objFunctions['ONTEXTUPDATE_MARKET&FILTER_SEARCHTEXT']                = __onTextUpdate_Market_Filter_SearchText
    objFunctions['ONSWITCHSTATUSUPDATE_MARKET&FILTER_TRADINGTRUE']       = __onSwitchStatusUpdate_Market_Filter_TradingTrue
    objFunctions['ONSWITCHSTATUSUPDATE_MARKET&FILTER_TRADINGFALSE']      = __onSwitchStatusUpdate_Market_Filter_TradingFalse
    objFunctions['ONSWITCHSTATUSUPDATE_MARKET&FILTER_MINNUMBEROFKLINES'] = __onSwitchStatusUpdate_Market_Filter_MinNumberOfKlines
    objFunctions['ONTEXTUPDATE_MARKET&FILTER_MINNUMBEROFKLINES']         = __onTextUpdate_Market_Filter_MinNumberOfKlines
    objFunctions['ONSWITCHSTATUSUPDATE_MARKET&FILTER_SORTBYID']          = __onSwitchStatusUpdate_Market_Filter_SortByID
    objFunctions['ONSWITCHSTATUSUPDATE_MARKET&FILTER_SORTBYSYMBOL']      = __onSwitchStatusUpdate_Market_Filter_SortBySymbol
    objFunctions['ONSWITCHSTATUSUPDATE_MARKET&FILTER_SORTBYFIRSTKLINE']  = __onSwitchStatusUpdate_Market_Filter_SortByFirstKline

    #<Market&Currencies>
    def __onSelectionUpdate_Market_Filter_CurrencySelection(objInstance, **kwargs):
        try:    selectedCurrency_symbol = objInstance.getSelected()[0]
        except: selectedCurrency_symbol = None
        self.puVar['currency_selected'] = selectedCurrency_symbol
        self.pageAuxillaryFunctions['UPDATECURRENCYINFO']()
        self.pageAuxillaryFunctions['CHECKIFCANADDCURRENCYANALYSIS']()
    objFunctions['ONSELECTIONUPDATE_MARKET&FILTER_CURRENCYSELECTION'] = __onSelectionUpdate_Market_Filter_CurrencySelection

    #<Market&ToAnalysisList>
    def __onTextUpdate_Market_ToAnalysisList_AnalysisCode(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANADDCURRENCYANALYSIS']()
    def __onSelectionUpdate_Market_ToAnalysisList_ConfigurationSelection(objInstance, **kwargs):
        self.puVar['toAnalysisList_analysisConfiguration_selected'] = self.GUIOs["MARKET&TOANALYSISLIST_ANALYSISCONFIGSELECTIONBOX"].getSelected()
        self.pageAuxillaryFunctions['CHECKIFCANADDCURRENCYANALYSIS']()
    def __onButtonRelease_Market_ToAnalysisList_AddAnalysis(objInstance, **kwargs):
        #Collect analysis parameters
        symbol       = self.puVar['currency_selected']
        analysisCode = self.GUIOs["MARKET&TOANALYSISLIST_ANALYSISCODETEXTINPUTBOX"].getText()
        if (analysisCode == ""): analysisCode = None
        analysisConfigurationCode = self.puVar['toAnalysisList_analysisConfiguration_selected']
        #Send analysis add request
        self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'addCurrencyAnalysis', functionParams = {'currencySymbol': symbol, 'currencyAnalysisCode': analysisCode, 'currencyAnalysisConfigurationCode': analysisConfigurationCode}, farrHandler = self.pageAuxillaryFunctions['_FARR_ONANALYSISADDREQUESTRESPONSE'])
        #Deactivate button
        self.GUIOs["MARKET&TOANALYSISLIST_ANALYSISLISTADD"].deactivate()
        self.puVar['toAnalysisList_waitingResponse'] = True
    objFunctions['ONTEXTUPDATE_MARKET&TOANALYSISLIST_ANALYSISCODE']                = __onTextUpdate_Market_ToAnalysisList_AnalysisCode
    objFunctions['ONSELECTIONUPDATE_MARKET&TOANALYSISLIST_CONFIGURATIONSELECTION'] = __onSelectionUpdate_Market_ToAnalysisList_ConfigurationSelection
    objFunctions['ONBUTTONRELEASE_MARKET&TOANALYSISLIST_ADDANALYSIS']              = __onButtonRelease_Market_ToAnalysisList_AddAnalysis

    #<TradeManager&Analyzers>
    def __onSelectionUpdate_TradeManager_Analyzers_OnAnalyzerSelection(objInstance, **kwargs):
        self.puVar['analyzerCentral_selectedAnalyzer'] = self.GUIOs["TRADEMANAGER&ANALYZERS_ANALYZERSELECTIONBOX"].getSelected()
        self.pageAuxillaryFunctions['UPDATEANALYZERCENTRALINFO'](updateAll = False)
    objFunctions['ONSELECTIONUPDATE_TRADEMANAGER&ANALYZERS_ANALYZER'] = __onSelectionUpdate_TradeManager_Analyzers_OnAnalyzerSelection

    #<TradeManager&ConfigurationControl>
    def __onSelectionUpdate_TradeManager_ConfigurationControl_ConfigurationCode(objInstance, **kwargs):
        self.puVar['configurationControl_analysisConfiguration_selected'] = self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_SELECTIONBOX"].getSelected()
        self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONCODETEXTINPUTBOX"].updateText(text = self.puVar['configurationControl_analysisConfiguration_selected'])
        self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONADD"].deactivate()
        self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONREMOVE"].activate()
        configuration = self.puVar['analysisConfigurations'][self.puVar['configurationControl_analysisConfiguration_selected']]
        self.pageAuxillaryFunctions['SETANALYSISCONFIGURATIONGUIOS'](configuration)
    def __onTextUpdate_TradeManager_ConfigurationControl_ConfigurationCode(objInstance, **kwargs):
        analysisConfigurationCode_entered = self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONCODETEXTINPUTBOX"].getText()
        if (analysisConfigurationCode_entered == self.puVar['configurationControl_analysisConfiguration_selected']): self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONADD"].deactivate()
        else:                                                                                                        self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONADD"].activate()
    def __onButtonRelease_TradeManager_ConfigurationControl_AddConfiguration(objInstance, **kwargs):
        #Configuration code
        configurationCode = self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONCODETEXTINPUTBOX"].getText()
        if (configurationCode == ""): configurationCode = None
        #Format configuration
        configuration = self.pageAuxillaryFunctions['FORMATANALYSISCONFIGURATIONFROMGUIOS']()
        #Neural Network Compatability Check
        _nnNotFound   = False
        _nnCompatible = False
        _nnCode        = configuration['PIP_NeuralNetworkCode']
        if (_nnCode == None): _nnCompatible = True
        else:
            _nns = self.ipcA.getPRD(processName = 'NEURALNETWORKMANAGER', prdAddress = 'NEURALNETWORKS')
            if (_nnCode in _nns):
                _nn                    = self.ipcA.getPRD(processName = 'NEURALNETWORKMANAGER', prdAddress = 'NEURALNETWORKS')[_nnCode]
                _nn_analysisReferences = _nn['analysisReferences']
                if (configuration != None):
                    _nnCompatible   = True
                    _analysisParams = atmEta_Analyzers.constructCurrencyAnalysisParamsFromCurrencyAnalysisConfiguration(currencyAnalysisConfiguration = configuration)
                    for _aCode in _nn_analysisReferences:
                        if (_aCode not in _analysisParams): _nnCompatible = False; break
            else: _nnNotFound = True
        #Send configuration add request
        if   (configuration == None):  self.GUIOs["MESSAGEDISPLAYTEXT_DISPLAYTEXT"].updateText(text = "[LOCAL]: Unable to format the Currency Analysis Configuration. Check the configuration values",         textStyle = 'RED')
        elif (_nnNotFound   == True):  self.GUIOs["MESSAGEDISPLAYTEXT_DISPLAYTEXT"].updateText(text = "[LOCAL]: Unable to generate the Currency Analysis Configuration. Neural Network not found",             textStyle = 'RED')
        elif (_nnCompatible == False): self.GUIOs["MESSAGEDISPLAYTEXT_DISPLAYTEXT"].updateText(text = "[LOCAL]: Unable to generate the Currency Analysis Configuration. Incompatible with the Neural Network", textStyle = 'RED')
        else:
            self.ipcA.sendFAR(targetProcess  = 'TRADEMANAGER', 
                              functionID     = 'addCurrencyAnalysisConfiguration', 
                              functionParams = {'currencyAnalysisConfigurationCode': configurationCode, 
                                                'currencyAnalysisConfiguration':     configuration}, 
                              farrHandler    = self.pageAuxillaryFunctions['_FARR_ONANALYSISCONFIGURATIONCONTROLREQUESTRESPONSE'])
    def __onButtonRelease_TradeManager_ConfigurationControl_RemoveConfiguration(objInstance, **kwargs):
        configurationCode = self.puVar['configurationControl_analysisConfiguration_selected']
        if (configurationCode != None): self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'removeCurrencyAnalysisConfiguration', functionParams = {'currencyAnalysisConfigurationCode': configurationCode}, farrHandler = self.pageAuxillaryFunctions['_FARR_ONANALYSISCONFIGURATIONCONTROLREQUESTRESPONSE'])
    objFunctions['ONSELECTIONUPDATE_TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONCODE'] = __onSelectionUpdate_TradeManager_ConfigurationControl_ConfigurationCode
    objFunctions['ONTEXTUPDATE_TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONCODE']      = __onTextUpdate_TradeManager_ConfigurationControl_ConfigurationCode
    objFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATIONCONTROL_ADDCONFIGURATION']    = __onButtonRelease_TradeManager_ConfigurationControl_AddConfiguration
    objFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATIONCONTROL_REMOVECONFIGURATION'] = __onButtonRelease_TradeManager_ConfigurationControl_RemoveConfiguration

    #<TradeManager&Configuration>
    def __onButtonRelease_TradeManager_Configuration_MoveToSubPage(objInstance, **kwargs):
        pageNameTo = objInstance.name.split("_")[1]
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_{:s}".format(self.puVar['currentAnalysisConfigurationPageName'])].hide()
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_{:s}".format(pageNameTo)].show()
        self.puVar['currentAnalysisConfigurationPageName'] = pageNameTo
        #Special Cases
        if (pageNameTo == 'PIP'): self.pageAuxillaryFunctions['UPDATENEURALNETWORKCODESLIST']()
    def __oButtonRelease_TradeManager_Configuration_ConfigButton(objInstance, **kwargs):
        objName = objInstance.name
        if (objName == 'PIP_NeuralNetworkCodeRelease'):
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NEURALNETWORKCODESELECTIONBOX"].setSelected(itemKey = None, callSelectionUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NEURALNETWORKCODERELEASEBUTTON"].deactivate()
    def __onSelectionUpdate_TradeManager_Configuration_ConfigSelectionBox(objInstance, **kwargs):
        objName = objInstance.name
        if (objName == 'PIP_NeuralNetworkCode'):
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NEURALNETWORKCODERELEASEBUTTON"].activate()
    def __onValueUpdate_TradeManager_Configuration_ConfigValueSlider(objInstance, **kwargs):
        objName = objInstance.name
        if (objName == 'IVP_GammaFactor'):
            sliderValue = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["GAMMAFACTORSLIDER"].getSliderValue()
            configValue = round(sliderValue/100*(0.095)+0.005, 3)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["GAMMAFACTORDISPLAYTEXT"].updateText(text = "{:.1f} %".format(configValue*100))
        elif (objName == 'IVP_DeltaFactor'):
            sliderValue = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["DELTAFACTORSLIDER"].getSliderValue()
            configValue = round(sliderValue/100*(9.9)+0.1, 1)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["DELTAFACTORDISPLAYTEXT"].updateText(text = "{:d} %".format(int(configValue*100)))
        elif (objName == 'PIP_SwingRange'):
            sliderValue = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["SWINGRANGESLIDER"].getSliderValue()
            configValue = round(sliderValue/100*0.0490+0.0010, 3)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["SWINGRANGEDISPLAYTEXT"].updateText(text = "{:.2f} %".format(configValue*100))
        elif (objName == 'PIP_NNAAlpha'):
            sliderValue = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NNAALPHAVALUESLIDER"].getSliderValue()
            configValue = round(sliderValue/100*0.95+0.05, 2)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NNAALPHAVALUEDISPLAYTEXT"].updateText(text = "{:.2f}".format(configValue))
        elif (objName == 'PIP_NNABeta'):
            sliderValue = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NNABETAVALUESLIDER"].getSliderValue()
            configValue = int(round(sliderValue/100*18+2))
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NNABETAVALUEDISPLAYTEXT"].updateText(text = "{:d}".format(configValue))
        elif (objName == 'PIP_ClassicalAlpha'):
            sliderValue = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALALPHAVALUESLIDER"].getSliderValue()
            configValue = round(sliderValue/100*2.9+0.1, 1)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALALPHAVALUEDISPLAYTEXT"].updateText(text = "{:.1f}".format(configValue))
        elif (objName == 'PIP_ClassicalBeta'):
            sliderValue = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALBETAVALUESLIDER"].getSliderValue()
            configValue = int(round(sliderValue/100*18+2))
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALBETAVALUEDISPLAYTEXT"].updateText(text = "{:d}".format(configValue))
        elif (objName == 'PIP_CSActivationThreshold1'):
            sliderValue = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALACTIVATIONTHRESHOLD1VALUESLIDER"].getSliderValue()
            configValue = round(sliderValue/100*0.95+0.00, 2)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALACTIVATIONTHRESHOLD1VALUEDISPLAYTEXT"].updateText(text = "{:.2f}".format(configValue))
        elif (objName == 'PIP_CSActivationThreshold2'):
            sliderValue = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALACTIVATIONTHRESHOLD2VALUESLIDER"].getSliderValue()
            configValue = round(sliderValue/100*0.95+0.05, 2)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALACTIVATIONTHRESHOLD2VALUEDISPLAYTEXT"].updateText(text = "{:.2f}".format(configValue))
        elif (objName == 'PIP_WSActivationThreshold'):
            sliderValue = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["WOIACTIVATIONTHRESHOLDVALUESLIDER"].getSliderValue()
            configValue = round(sliderValue/100*0.95+0.00, 2)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["WOIACTIVATIONTHRESHOLDVALUEDISPLAYTEXT"].updateText(text = "{:.2f}".format(configValue))
    objFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_MOVETOSUBPAGE']        = __onButtonRelease_TradeManager_Configuration_MoveToSubPage
    objFunctions['ONBUTTONRELEASE_TRADEMANAGER&CONFIGURATION_CONFIGBUTTON']         = __oButtonRelease_TradeManager_Configuration_ConfigButton
    objFunctions['ONSELECTIONUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGSELECTIONBOX'] = __onSelectionUpdate_TradeManager_Configuration_ConfigSelectionBox
    objFunctions['ONVALUEUPDATE_TRADEMANAGER&CONFIGURATION_CONFIGVALUESLIDER']      = __onValueUpdate_TradeManager_Configuration_ConfigValueSlider

    #<TradeManager&CurrencyAnalysisFilter>
    def __onTextUpdate_TradeManager_CurrencyAnalysisFilter_SearchText(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONCURRENCYANALYSISFILTERUPDATE']()
    def __onSwitchStatusUpdate_TradeManager_CurrencyAnalysisFilter_SortByID(objInstance, **kwargs):
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYZER"].getStatus()      == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYZER"].setStatus(status      = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYSISCODE"].getStatus()  == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYSISCODE"].setStatus(status  = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYSYMBOL"].getStatus()        == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status        = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYCONFIGURATION"].getStatus() == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYCONFIGURATION"].setStatus(status = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].getStatus()    == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].setStatus(status    = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYID"].getStatus() == False):            self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYID"].setStatus(status            = True,  callStatusUpdateFunction = False)
        else:                                                                                                         self.pageAuxillaryFunctions['ONCURRENCYANALYSISFILTERUPDATE']()
    def __onSwitchStatusUpdate_TradeManager_CurrencyAnalysisFilter_SortByAnalyzer(objInstance, **kwargs):
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYID"].getStatus()            == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYID"].setStatus(status            = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYSISCODE"].getStatus()  == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYSISCODE"].setStatus(status  = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYSYMBOL"].getStatus()        == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status        = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYCONFIGURATION"].getStatus() == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYCONFIGURATION"].setStatus(status = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].getStatus()    == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].setStatus(status    = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYZER"].getStatus() == False):      self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYZER"].setStatus(status      = True,  callStatusUpdateFunction = False)
        else:                                                                                                         self.pageAuxillaryFunctions['ONCURRENCYANALYSISFILTERUPDATE']()
    def __onSwitchStatusUpdate_TradeManager_CurrencyAnalysisFilter_SortByAnalysisCode(objInstance, **kwargs):
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYID"].getStatus()            == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYID"].setStatus(status            = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYZER"].getStatus()      == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYZER"].setStatus(status      = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYSYMBOL"].getStatus()        == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status        = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYCONFIGURATION"].getStatus() == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYCONFIGURATION"].setStatus(status = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].getStatus()    == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].setStatus(status    = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYSISCODE"].getStatus() == False):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYSISCODE"].setStatus(status  = True,  callStatusUpdateFunction = False)
        else:                                                                                                         self.pageAuxillaryFunctions['ONCURRENCYANALYSISFILTERUPDATE']()
    def __onSwitchStatusUpdate_TradeManager_CurrencyAnalysisFilter_SortBySymbol(objInstance, **kwargs):
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYID"].getStatus()            == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYID"].setStatus(status            = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYZER"].getStatus()      == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYZER"].setStatus(status      = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYSISCODE"].getStatus()  == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYSISCODE"].setStatus(status  = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYCONFIGURATION"].getStatus() == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYCONFIGURATION"].setStatus(status = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].getStatus()    == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].setStatus(status    = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYSYMBOL"].getStatus() == False):        self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status        = True,  callStatusUpdateFunction = False)
        else:                                                                                                         self.pageAuxillaryFunctions['ONCURRENCYANALYSISFILTERUPDATE']()
    def __onSwitchStatusUpdate_TradeManager_CurrencyAnalysisFilter_SortByConfiguration(objInstance, **kwargs):
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYID"].getStatus()            == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYID"].setStatus(status            = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYZER"].getStatus()      == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYZER"].setStatus(status      = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYSISCODE"].getStatus()  == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYSISCODE"].setStatus(status  = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYSYMBOL"].getStatus()        == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status        = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].getStatus()    == True):  self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].setStatus(status    = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYCONFIGURATION"].getStatus() == False): self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYCONFIGURATION"].setStatus(status = True,  callStatusUpdateFunction = False)
        else:                                                                                                         self.pageAuxillaryFunctions['ONCURRENCYANALYSISFILTERUPDATE']()
    def __onSwitchStatusUpdate_TradeManager_CurrencyAnalysisFilter_SortByFirstKline(objInstance, **kwargs):
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYID"].getStatus()            == True): self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYID"].setStatus(status            = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYZER"].getStatus()      == True): self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYZER"].setStatus(status      = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYSISCODE"].getStatus()  == True): self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYSISCODE"].setStatus(status  = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYSYMBOL"].getStatus()        == True): self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYSYMBOL"].setStatus(status        = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYCONFIGURATION"].getStatus() == True): self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYCONFIGURATION"].setStatus(status = False, callStatusUpdateFunction = False)
        if (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].getStatus() == False):   self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].setStatus(status    = True,  callStatusUpdateFunction = False)
        else:                                                                                                        self.pageAuxillaryFunctions['ONCURRENCYANALYSISFILTERUPDATE']()
    objFunctions['ONTEXTUPDATE_TRADEMANAGER&CURRENCYANALYSISFILTER_SEARCHTEXT']                  = __onTextUpdate_TradeManager_CurrencyAnalysisFilter_SearchText
    objFunctions['ONSWITCHSTATUSUPDATE_TRADEMANAGER&CURRENCYANALYSISFILTER_SORTBYID']            = __onSwitchStatusUpdate_TradeManager_CurrencyAnalysisFilter_SortByID
    objFunctions['ONSWITCHSTATUSUPDATE_TRADEMANAGER&CURRENCYANALYSISFILTER_SORTBYANALYZER']      = __onSwitchStatusUpdate_TradeManager_CurrencyAnalysisFilter_SortByAnalyzer
    objFunctions['ONSWITCHSTATUSUPDATE_TRADEMANAGER&CURRENCYANALYSISFILTER_SORTBYANALYSISCODE']  = __onSwitchStatusUpdate_TradeManager_CurrencyAnalysisFilter_SortByAnalysisCode
    objFunctions['ONSWITCHSTATUSUPDATE_TRADEMANAGER&CURRENCYANALYSISFILTER_SORTBYSYMBOL']        = __onSwitchStatusUpdate_TradeManager_CurrencyAnalysisFilter_SortBySymbol
    objFunctions['ONSWITCHSTATUSUPDATE_TRADEMANAGER&CURRENCYANALYSISFILTER_SORTBYCONFIGURATION'] = __onSwitchStatusUpdate_TradeManager_CurrencyAnalysisFilter_SortByConfiguration
    objFunctions['ONSWITCHSTATUSUPDATE_TRADEMANAGER&CURRENCYANALYSISFILTER_SORTBYFIRSTKLINE']    = __onSwitchStatusUpdate_TradeManager_CurrencyAnalysisFilter_SortByFirstKline

    #<TradeManager&CurrencyAnalysis>
    def __onSelectionUpdate_TradeManager_AnalysisList_AnalysisSelection(objInstance, **kwargs):
        try:    currencyAnalysis_selected = objInstance.getSelected()[0]
        except: currencyAnalysis_selected = None
        self.puVar['currencyAnalysis_selected'] = currencyAnalysis_selected
        self.pageAuxillaryFunctions['UPDATECURRENCYANALYSISINFO']()
        if (currencyAnalysis_selected == None): self.GUIOs["TRADEMANAGER&CURRENCYANALYSISCONTROL_REMOVEANALYSIS"].deactivate()
        else:                                                 
            self.GUIOs["TRADEMANAGER&CURRENCYANALYSISCONTROL_REMOVEANALYSIS"].activate()
            if (self.puVar['currencyAnalysis'][currencyAnalysis_selected]['status'] == 'ANALYZINGREALTIME'): self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_VIEWCURRENCYANALYSISCHART"].activate()
            else:                                                                                            self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_VIEWCURRENCYANALYSISCHART"].deactivate()
    objFunctions['ONSELECTIONUPDATE_TRADEMANAGER&ANALYSISLIST_ANALYSISSELECTION'] = __onSelectionUpdate_TradeManager_AnalysisList_AnalysisSelection

    #<TradeManager&CurrencyAnalysisInformation>
    def __onButtonRelease_TradeManager_AnalysisInformation_ViewCurrencyAnalysisChart(objInstance, **kwargs):
        puVar_currencyAnalysis = self.sysFunctions['GETPAGEPUVAR']('CURRENCYANALYSIS')
        puVar_currencyAnalysis['currencyAnalysis_toLoad'] = self.puVar['currencyAnalysis_selected']
        self.sysFunctions['LOADPAGE']('CURRENCYANALYSIS')
    objFunctions['ONBUTTONRELEASE_TRADEMANAGER&ANALYSISINFORMATION_VIEWCURRENCYANALYSISCHART'] = __onButtonRelease_TradeManager_AnalysisInformation_ViewCurrencyAnalysisChart

    #<TradeManager&CurrencyAnalysisControl>
    def __onButtonRelease_TradeManager_CurrencyAnalysisControl_RemoveAnalysis(objInstance, **kwargs):
        analysisCode = self.puVar['currencyAnalysis_selected']
        if (analysisCode != None): self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'removeCurrencyAnalysis', functionParams = {'currencyAnalysisCode': analysisCode}, farrHandler = None)
    objFunctions['ONBUTTONRELEASE_TRADEMANAGER&CURRENCYANALYSISCONTROL_REMOVEANALYSIS'] = __onButtonRelease_TradeManager_CurrencyAnalysisControl_RemoveAnalysis

    #<TradeManager&TradeConfiguration>
    def __onValueUpdate_TradeManager_TradeConfiguration_ConfigValueSlider(objInstance, **kwargs):
        objName = objInstance.name
        if (objName == 'TC_Leverage'):
            sliderValue = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["LEVERAGESLIDER"].getSliderValue()
            configValue = round(sliderValue/100*(20-1)+1)
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["LEVERAGEDISPLAYTEXT"].updateText(text = "X {:d}".format(configValue))
    def __onSelectionUpdate_TradeManager_TradeConfiguration_ConfigValueSelectionBox(objInstance, **kwargs):
        objName = objInstance.name
        if   (objName == 'TC_TCMode'):
            _tcMode = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TCMODESELECTIONBOX"].getSelected()
            for _groupName in self.puVar['tradeConfiguration_guioGroups']:
                if (_groupName == _tcMode):
                    for _guioName in self.puVar['tradeConfiguration_guioGroups'][_groupName]: self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs[_guioName].show()
                else:
                    for _guioName in self.puVar['tradeConfiguration_guioGroups'][_groupName]: self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs[_guioName].hide()
        elif (objName == 'TC_TS_TradeScenarioType'):
            _currentTSType = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOTYPESELECTIONBOX"].getSelected()
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOSELECTIONBOX"].clearSelected()
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_PDTEXTINPUTBOX"].updateText(text = "")
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_QDTEXTINPUTBOX"].updateText(text = "")
            if   (_currentTSType == 'ENTRY'): _target = self.puVar['tradeConfiguration_current_TS_TS_Entry']
            elif (_currentTSType == 'EXIT'):  _target = self.puVar['tradeConfiguration_current_TS_TS_Exit']
            elif (_currentTSType == 'PSL'):   _target = self.puVar['tradeConfiguration_current_TS_TS_PSL']
            nTradeScenarios = len(_target)
            tradeScenarios_selectionList = dict()
            for _tradeScenarioIndex, _tradeScenario in enumerate(_target):
                #[0]: Index
                _index_str = "{:d} / {:d}".format(_tradeScenarioIndex+1, nTradeScenarios)
                #[1]: PD
                _pd_str = "{:.1f} %".format(_tradeScenario[0]*100)
                #[2]: QD
                _qd_str = "{:.1f} %".format(_tradeScenario[1]*100)
                #Finally
                tradeScenarios_selectionList[_tradeScenarioIndex] = [{'text': _index_str},
                                                                     {'text': _pd_str},
                                                                     {'text': _qd_str}]
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOSELECTIONBOX"].setSelectionList(selectionList = tradeScenarios_selectionList, keepSelected = False, displayTargets = 'all', callSelectionUpdateFunction = False)
        elif (objName == 'TC_TS_TradeScenario'):
            try:    _scenarioIndex = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOSELECTIONBOX"].getSelected()[0]
            except: _scenarioIndex = None
            if (_scenarioIndex != None):
                _currentTSType = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOTYPESELECTIONBOX"].getSelected()
                if   (_currentTSType == 'ENTRY'): _target = self.puVar['tradeConfiguration_current_TS_TS_Entry']
                elif (_currentTSType == 'EXIT'):  _target = self.puVar['tradeConfiguration_current_TS_TS_Exit']
                elif (_currentTSType == 'PSL'):   _target = self.puVar['tradeConfiguration_current_TS_TS_PSL']
                _scenario = _target[_scenarioIndex]
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_PDTEXTINPUTBOX"].updateText(text = "{:.1f}".format(_scenario[0]*100))
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_QDTEXTINPUTBOX"].updateText(text = "{:.1f}".format(_scenario[1]*100))
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOADDBUTTON"].activate()
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOREMOVEBUTTON"].activate()
            else: self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOREMOVEBUTTON"].deactivate()
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOEDITBUTTON"].deactivate()
        elif (objName == 'TC_RQPM_FunctionType'):
            #Selected Function Type
            _functionType = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FUNCTIONTYPESELECTIONBOX"].getSelected()
            #Function Parameters
            self.puVar['tradeConfiguration_current_RQPM_Parameters'] = list()
            _functionParameters_selectionBox = dict()
            if (_functionType != None):
                _functionDescriptor = atmEta_RQPMFunctions.RQPMFUNCTIONS_DESCRIPTORS[_functionType]
                for _paramIndex, _paramDescriptor in enumerate(_functionDescriptor):
                    #[0]: Index
                    _index_str = "{:d} / {:d}".format(_paramIndex+1, len(_functionDescriptor))
                    #[1]: Param Name
                    _name_str = "{:s}".format(_paramDescriptor['name'])
                    #[2]: Value
                    _value_str = _paramDescriptor['val_to_str'](x = _paramDescriptor['defaultValue'])
                    #Finally
                    _functionParameters_selectionBox[_paramIndex] = [{'text': _index_str},
                                                                     {'text': _name_str},
                                                                     {'text': _value_str}]
                    self.puVar['tradeConfiguration_current_RQPM_Parameters'].append(_paramDescriptor['defaultValue'])
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSELECTIONBOX"].setSelectionList(selectionList = _functionParameters_selectionBox, keepSelected = False, displayTargets = 'all', callSelectionUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERNAMEDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETTEXTINPUTBOX"].updateText(text = "")
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETTEXTINPUTBOX"].deactivate()
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETBUTTON"].deactivate()
        
            #Selected Function Type
            _functionType = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FUNCTIONTYPESELECTIONBOX"].getSelected()
            #Function Parameters
            self.puVar['tradeConfiguration_current_RQPM_Parameters_LONG']  = list()
            self.puVar['tradeConfiguration_current_RQPM_Parameters_SHORT'] = list()
            _functionParameters_selectionBox = dict()
            if (_functionType != None):
                _functionDescriptor = atmEta_RQPMFunctions.RQPMFUNCTIONS_DESCRIPTORS[_functionType]
                for _paramIndex, _paramDescriptor in enumerate(_functionDescriptor):
                    #[0]: Index
                    _index_str = "{:d} / {:d}".format(_paramIndex+1, len(_functionDescriptor))
                    #[1]: Param Name
                    _name_str = "{:s}".format(_paramDescriptor['name'])
                    #[2]: Value
                    _value_str = _paramDescriptor['val_to_str'](x = _paramDescriptor['defaultValue'])
                    #Finally
                    _functionParameters_selectionBox[_paramIndex] = [{'text': _index_str},
                                                                     {'text': _name_str},
                                                                     {'text': _value_str}]
                    self.puVar['tradeConfiguration_current_RQPM_Parameters_LONG'].append(_paramDescriptor['defaultValue'])
                    self.puVar['tradeConfiguration_current_RQPM_Parameters_SHORT'].append(_paramDescriptor['defaultValue'])
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSELECTIONBOX"].setSelectionList(selectionList = _functionParameters_selectionBox, keepSelected = False, displayTargets = 'all', callSelectionUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERNAMEDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETTEXTINPUTBOX"].updateText(text = "")
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETTEXTINPUTBOX"].deactivate()
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETBUTTON"].deactivate()
        elif (objName == 'TC_RQPM_FunctionSide'):
            _functionType       = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FUNCTIONTYPESELECTIONBOX"].getSelected()
            _functionSide       = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FUNCTIONSIDESELECTIONBOX"].getSelected()
            _functionDescriptor = atmEta_RQPMFunctions.RQPMFUNCTIONS_DESCRIPTORS[_functionType]
            _currentParams = self.puVar['tradeConfiguration_current_RQPM_Parameters_{:s}'.format(_functionSide)]
            for _paramIndex, _paramValue in enumerate(_currentParams):
                _newSelectionBoxItem = {'text': _functionDescriptor[_paramIndex]['val_to_str'](x = _paramValue)}
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSELECTIONBOX"].editSelectionListItem(itemKey = _paramIndex, item = _newSelectionBoxItem, columnIndex = 2)
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSELECTIONBOX"].clearSelected()
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERNAMEDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETTEXTINPUTBOX"].updateText(text = "")
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETTEXTINPUTBOX"].deactivate()
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETBUTTON"].deactivate()
        elif (objName == 'TC_RQPM_Parameter'):
            #Selected Function Type & Parameter
            _functionType = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FUNCTIONTYPESELECTIONBOX"].getSelected()
            try:    _parameterIndex = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSELECTIONBOX"].getSelected()[0]
            except: _parameterIndex = None
            if (_parameterIndex is None):
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERNAMEDISPLAYTEXT"].updateText(text = "-")
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETTEXTINPUTBOX"].updateText(text = "")
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETTEXTINPUTBOX"].deactivate()
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETBUTTON"].deactivate()
            else:
                _functionDescriptor = atmEta_RQPMFunctions.RQPMFUNCTIONS_DESCRIPTORS[_functionType]
                _paramDescriptor    = _functionDescriptor[_parameterIndex]
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERNAMEDISPLAYTEXT"].updateText(text = f"{_paramDescriptor['name']}")
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETTEXTINPUTBOX"].updateText(text = _paramDescriptor['val_to_str'](x = self.puVar['tradeConfiguration_current_RQPM_Parameters'][_parameterIndex]))
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETTEXTINPUTBOX"].activate()
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETBUTTON"].deactivate()
    def __onButtonRelease_TradeManager_TradeConfiguration_ConfigValueButton(objInstance, **kwargs):
        objName = objInstance.name
        #Add Trade Scenario
        if   (objName == 'TC_TS_AddTradeScenario'):
            try:    _scenarioIndex = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TRADESCENARIOSELECTIONBOX"].getSelected()[0]
            except: _scenarioIndex = None
            _currentTSType = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TRADESCENARIOTYPESELECTIONBOX"].getSelected()
            if   (_currentTSType == 'ENTRY'): _target = self.puVar['tradeConfiguration_current_TS_TS_Entry']
            elif (_currentTSType == 'EXIT'):  _target = self.puVar['tradeConfiguration_current_TS_TS_Exit']
            elif (_currentTSType == 'PSL'):   _target = self.puVar['tradeConfiguration_current_TS_TS_PSL']
            #Generate new scenario and append
            _pd = round(float(self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["PDTEXTINPUTBOX"].getText())/100, 3)
            _qd = round(float(self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["QDTEXTINPUTBOX"].getText())/100, 3)
            _scenario = (_pd, _qd)
            if (_scenarioIndex == None): _target.append(_scenario)
            else:                        _target.insert(_scenarioIndex+1, _scenario)
            #Update the selection box
            nTradeScenarios = len(_target)
            tradeScenarios_selectionList = dict()
            for _tradeScenarioIndex, _tradeScenario in enumerate(_target):
                #[0]: Index
                _index_str = "{:d} / {:d}".format(_tradeScenarioIndex+1, nTradeScenarios)
                #[1]: PD
                _pd_str = "{:.1f} %".format(_tradeScenario[0]*100)
                #[2]: QD
                _qd_str = "{:.1f} %".format(_tradeScenario[1]*100)
                #Finally
                tradeScenarios_selectionList[_tradeScenarioIndex] = [{'text': _index_str},
                                                                     {'text': _pd_str},
                                                                     {'text': _qd_str}]
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TRADESCENARIOSELECTIONBOX"].setSelectionList(selectionList = tradeScenarios_selectionList, keepSelected = True, displayTargets = 'all', callSelectionUpdateFunction = False)
        elif (objName == 'TC_TS_EditTradeScenario'):
            _scenarioIndex = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOSELECTIONBOX"].getSelected()[0]
            _currentTSType = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOTYPESELECTIONBOX"].getSelected()
            if   (_currentTSType == 'ENTRY'): _target = self.puVar['tradeConfiguration_current_TS_TS_Entry']
            elif (_currentTSType == 'EXIT'):  _target = self.puVar['tradeConfiguration_current_TS_TS_Exit']
            elif (_currentTSType == 'PSL'):   _target = self.puVar['tradeConfiguration_current_TS_TS_PSL']
            #Generate new scenario and append
            _pd = round(float(self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_PDTEXTINPUTBOX"].getText())/100, 3)
            _qd = round(float(self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_QDTEXTINPUTBOX"].getText())/100, 3)
            _scenario = (_pd, _qd)
            _target[_scenarioIndex] = _scenario
            #Update the selection box
            nTradeScenarios = len(_target)
            tradeScenarios_selectionList = dict()
            for _tradeScenarioIndex, _tradeScenario in enumerate(_target):
                #[0]: Index
                _index_str = "{:d} / {:d}".format(_tradeScenarioIndex+1, nTradeScenarios)
                #[1]: PD
                _pd_str = "{:.1f} %".format(_tradeScenario[0]*100)
                #[2]: QD
                _qd_str = "{:.1f} %".format(_tradeScenario[1]*100)
                #Finally
                tradeScenarios_selectionList[_tradeScenarioIndex] = [{'text': _index_str},
                                                                     {'text': _pd_str},
                                                                     {'text': _qd_str}]
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOSELECTIONBOX"].setSelectionList(selectionList = tradeScenarios_selectionList, keepSelected = True, displayTargets = 'all', callSelectionUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOEDITBUTTON"].deactivate()
        elif (objName == 'TC_TS_RemoveTradeScenario'):
            _scenarioIndex = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOSELECTIONBOX"].getSelected()[0]
            _currentTSType = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOTYPESELECTIONBOX"].getSelected()
            if   (_currentTSType == 'ENTRY'): _target = self.puVar['tradeConfiguration_current_TS_TS_Entry']
            elif (_currentTSType == 'EXIT'):  _target = self.puVar['tradeConfiguration_current_TS_TS_Exit']
            elif (_currentTSType == 'PSL'):   _target = self.puVar['tradeConfiguration_current_TS_TS_PSL']
            #Remove the scenario
            _target.pop(_scenarioIndex)
            #Update the selection box
            nTradeScenarios = len(_target)
            tradeScenarios_selectionList = dict()
            for _tradeScenarioIndex, _tradeScenario in enumerate(_target):
                #[0]: Index
                _index_str = "{:d} / {:d}".format(_tradeScenarioIndex+1, nTradeScenarios)
                #[1]: PD_Entry
                _pd_str = "{:.1f} %".format(_tradeScenario[0]*100)
                #[2]: QD
                _qd_str = "{:.1f} %".format(_tradeScenario[1]*100)
                #Finally
                tradeScenarios_selectionList[_tradeScenarioIndex] = [{'text': _index_str},
                                                                     {'text': _pd_str},
                                                                     {'text': _qd_str}]
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOSELECTIONBOX"].setSelectionList(selectionList = tradeScenarios_selectionList, keepSelected = True, displayTargets = 'all', callSelectionUpdateFunction = False)
            try:    _scenarioIndex = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOSELECTIONBOX"].getSelected()[0]
            except: _scenarioIndex = None
            if (_scenarioIndex == None): self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOREMOVEBUTTON"].deactivate()
        elif (objName == 'TC_RQPM_SetParameter'):
            _functionType   = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FUNCTIONTYPESELECTIONBOX"].getSelected()
            _functionSide   = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FUNCTIONSIDESELECTIONBOX"].getSelected()
            _parameterIndex = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSELECTIONBOX"].getSelected()[0]
            _functionDescriptor = atmEta_RQPMFunctions.RQPMFUNCTIONS_DESCRIPTORS[_functionType]
            _paramDescriptor    = _functionDescriptor[_parameterIndex]
            _paramValue_formatted = _paramDescriptor['str_to_val'](x = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETTEXTINPUTBOX"].getText())
            _paramValue_str       = _paramDescriptor['val_to_str'](x = _paramValue_formatted)
            #Selection Box
            _newSelectionBoxItem = {'text': _paramValue_str}
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSELECTIONBOX"].editSelectionListItem(itemKey = _parameterIndex, item = _newSelectionBoxItem, columnIndex = 2)
            #Text Input Box
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETTEXTINPUTBOX"].updateText(text = _paramValue_str)
            #Set Button
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETBUTTON"].deactivate()
            #Local Copy
            self.puVar['tradeConfiguration_current_RQPM_Parameters_{:s}'.format(_functionSide)][_parameterIndex] = _paramValue_formatted
    def __onTextUpdate_TradeManager_TradeConfiguration_ConfigValueText(objInstance, **kwargs):
        objName = objInstance.name
        if   (objName == 'TC_TS_FSLIMMED'):      self.pageAuxillaryFunctions['CHECKIFCANADDTRADECONFIGURATION']()
        if   (objName == 'TC_TS_FSLCLOSE'):      self.pageAuxillaryFunctions['CHECKIFCANADDTRADECONFIGURATION']()
        elif (objName == 'TC_TS_WR_Activation'): self.pageAuxillaryFunctions['CHECKIFCANADDTRADECONFIGURATION']()
        elif (objName == 'TC_TS_WR_Amount'):     self.pageAuxillaryFunctions['CHECKIFCANADDTRADECONFIGURATION']()
        elif (objName == 'TC_TS_RAF'):           self.pageAuxillaryFunctions['CHECKIFCANADDTRADECONFIGURATION']()
        elif (objName == 'TC_TS_PD'):            self.pageAuxillaryFunctions['CHECKIFCANADDTRADESCENARIO']()
        elif (objName == 'TC_TS_QD'):            self.pageAuxillaryFunctions['CHECKIFCANADDTRADESCENARIO']()
        elif (objName == 'TC_RQPM_EOI'):       self.pageAuxillaryFunctions['CHECKIFCANADDTRADECONFIGURATION']()
        elif (objName == 'TC_RQPM_EOA'):       self.pageAuxillaryFunctions['CHECKIFCANADDTRADECONFIGURATION']()
        elif (objName == 'TC_RQPM_EOP'):       self.pageAuxillaryFunctions['CHECKIFCANADDTRADECONFIGURATION']()
        elif (objName == 'TC_RQPM_FSLIMMED'):  self.pageAuxillaryFunctions['CHECKIFCANADDTRADECONFIGURATION']()
        elif (objName == 'TC_RQPM_FSLCLOSE'):  self.pageAuxillaryFunctions['CHECKIFCANADDTRADECONFIGURATION']()
        elif (objName == 'TC_RQPM_Parameter'): self.pageAuxillaryFunctions['CHECKIFCANSETRQPMFUNCTIONPARAMETER']()
    objFunctions['ONVALUEUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUESLIDER']           = __onValueUpdate_TradeManager_TradeConfiguration_ConfigValueSlider
    objFunctions['ONSELECTIONUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUESELECTIONBOX'] = __onSelectionUpdate_TradeManager_TradeConfiguration_ConfigValueSelectionBox
    objFunctions['ONBUTTONRELEASE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUEBUTTON']         = __onButtonRelease_TradeManager_TradeConfiguration_ConfigValueButton
    objFunctions['ONTEXTUPDATE_TRADEMANAGER&TRADECONFIGURATION_CONFIGVALUETEXT']              = __onTextUpdate_TradeManager_TradeConfiguration_ConfigValueText

    #<TradeManager&TradeConfigurationControl>
    def __onSelectionUpdate_TradeManager_TradeConfigurationControl_ConfigurationCode(objInstance, **kwargs):
        try:    tradeConfiguration_selected = objInstance.getSelected()
        except: tradeConfiguration_selected = None
        self.puVar['tradeConfiguration_selected'] = tradeConfiguration_selected
        self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONCODETEXTINPUTBOX"].updateText(text = self.puVar['tradeConfiguration_selected'])
        self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONADD"].deactivate()
        self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONREMOVE"].activate()
        tradeConfiguration = self.puVar['tradeConfigurations'][tradeConfiguration_selected]
        self.pageAuxillaryFunctions['SETTRADECONFIGURATIONGUIOS'](tradeConfiguration)
    def __onTextUpdate_TradeManager_TradeConfigurationControl_ConfigurationCode(objInstance, **kwargs):
        self.pageAuxillaryFunctions['CHECKIFCANADDTRADECONFIGURATION']()
    def __onButtonRelease_TradeManager_TradeConfigurationControl_AddConfiguration(objInstance, **kwargs):
        #Configuration code
        tradeConfigurationCode = self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONCODETEXTINPUTBOX"].getText()
        if (tradeConfigurationCode == ""): tradeConfigurationCode = None
        #Format configuration
        tradeConfiguration = self.pageAuxillaryFunctions['FORMATTRADECONFIGURATIONFROMGUIOS']()
        if (tradeConfiguration == None): self.GUIOs["MESSAGEDISPLAYTEXT_DISPLAYTEXT"].updateText(text = "[LOCAL]: Unable to format the configuration for the request, check the configuration values", textStyle = 'RED')
        else:
            self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', 
                              functionID = 'addTradeConfiguration', 
                              functionParams = {'tradeConfigurationCode': tradeConfigurationCode, 
                                                'tradeConfiguration':     tradeConfiguration}, 
                              farrHandler = self.pageAuxillaryFunctions['_FARR_ONTRADECONFIGURATIONCONTROLREQUESTRESPONSE'])
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_SELECTIONBOX"].setSelected(None, callSelectionUpdateFunction = False)
    def __onButtonRelease_TradeManager_TradeConfigurationControl_RemoveConfiguration(objInstance, **kwargs):
        tradeConfigurationCode = self.puVar['tradeConfiguration_selected']
        if (tradeConfigurationCode != None): self.ipcA.sendFAR(targetProcess = 'TRADEMANAGER', functionID = 'removeTradeConfiguration', functionParams = {'tradeConfigurationCode': tradeConfigurationCode}, farrHandler = self.pageAuxillaryFunctions['_FARR_ONTRADECONFIGURATIONCONTROLREQUESTRESPONSE'])
    objFunctions['ONSELECTIONUPDATE_TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONCODE'] = __onSelectionUpdate_TradeManager_TradeConfigurationControl_ConfigurationCode
    objFunctions['ONTEXTUPDATE_TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONCODE']      = __onTextUpdate_TradeManager_TradeConfigurationControl_ConfigurationCode
    objFunctions['ONBUTTONRELEASE_TRADEMANAGER&TRADECONFIGURATIONCONTROL_ADDCONFIGURATION']    = __onButtonRelease_TradeManager_TradeConfigurationControl_AddConfiguration
    objFunctions['ONBUTTONRELEASE_TRADEMANAGER&TRADECONFIGURATIONCONTROL_REMOVECONFIGURATION'] = __onButtonRelease_TradeManager_TradeConfigurationControl_RemoveConfiguration

    #Return the generated functions
    return objFunctions
#OBJECT FUNCTIONS END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUXILALRY FUNCTIONS --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateAuxillaryFunctions(self):
    auxFunctions = dict()
    
    #<_PAGELOAD>
    def __far_onCurrenciesUpdate(requester, updatedContents):
        if (requester == 'DATAMANAGER'):
            _resetList         = False
            _reapplyListFilter = False
            for updatedContent in updatedContents:
                symbol    = updatedContent['symbol']
                contentID = updatedContent['id']
                #A new currency is added
                if (contentID == '_ADDED'):
                    self.puVar['currencies'][symbol] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol))
                    _resetList = True
                else:
                    #Selected currency info update if needed & check if the currency list item needs an update
                    _updated_status     = False
                    _updated_firstKline = False
                    _updated_dataRanges = False
                    #---[1]: Currency Server Information Updated
                    if (contentID[0] == 'info_server'): 
                        try:    contentID_1 = contentID[1]
                        except: contentID_1 = None
                        #---[1-1]: Entire Server Information Updated
                        if (contentID_1 == None): self.puVar['currencies'][symbol]['info_server'] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'info_server')); _updated_status = True
                        #---[1-2]: Currency Status Updated
                        else:
                            if (contentID_1 == 'status'): self.puVar['currencies'][symbol]['info_server']['status'] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'info_server', 'status')); _updated_status = True
                    #---[2]: KlineFirstOpenTS Updated
                    elif (contentID[0] == 'kline_firstOpenTS'):
                        firstOpenTS_new = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'kline_firstOpenTS'))
                        self.puVar['currencies'][symbol]['kline_firstOpenTS'] = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'kline_firstOpenTS'))
                        _updated_firstKline = True
                    #---[3]: KlineAvailableRanges Updated
                    elif (contentID[0] == 'kline_availableRanges'):
                        dataRanges = self.ipcA.getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'kline_availableRanges'))
                        self.puVar['currencies'][symbol]['kline_availableRanges'] = dataRanges
                        _updated_dataRanges = True
                    #Update Handlers
                    #---Status
                    if (_updated_status == True):
                        if (self.puVar['currencies'][symbol]['info_server'] == None): _status_str = "-"; _status_str_color = 'BLUE_DARK'
                        else:
                            currencyStatus = self.puVar['currencies'][symbol]['info_server']['status']
                            if   (currencyStatus == 'TRADING'):  _status_str = self.visualManager.getTextPack('AUTOTRADE:MARKET&CURRENCIES_STATUS_TRADING');  _status_str_color = 'GREEN_LIGHT'
                            elif (currencyStatus == 'SETTLING'): _status_str = self.visualManager.getTextPack('AUTOTRADE:MARKET&CURRENCIES_STATUS_SETTLING'); _status_str_color = 'RED_LIGHT'
                            elif (currencyStatus == 'REMOVED'):  _status_str = self.visualManager.getTextPack('AUTOTRADE:MARKET&CURRENCIES_STATUS_REMOVED');  _status_str_color = 'RED_DARK'
                            else:                                _status_str = currencyStatus;                                                                _status_str_color = 'ORANGE_LIGHT'
                        _newSelectionBoxItem = {'text': _status_str, 'textStyles': [('all', _status_str_color),], 'textAnchor': 'CENTER'}
                        self.GUIOs["MARKET&CURRENCIES_SELECTIONBOX"].editSelectionListItem(itemKey = symbol, item = _newSelectionBoxItem, columnIndex = 2)
                        _reapplyListFilter = True
                    #---First Kline
                    if (_updated_firstKline == True):
                        if (firstOpenTS_new == None): _firstKline_str = "-"
                        else:                         _firstKline_str = datetime.fromtimestamp(firstOpenTS_new, tz=timezone.utc).strftime("%Y/%m/%d %H:%M")
                        _newSelectionBoxItem = {'text': _firstKline_str, 'textStyles': [('all', 'DEFAULT'),], 'textAnchor': 'CENTER'}
                        self.GUIOs["MARKET&CURRENCIES_SELECTIONBOX"].editSelectionListItem(itemKey = symbol, item = _newSelectionBoxItem, columnIndex = 3)
                        _reapplyListFilter = True
                    #---Data Ranges
                    if (_updated_dataRanges == True):
                        if (symbol == self.puVar['currency_selected']): 
                            if (dataRanges == None): dataRanges_str = "-"
                            else:
                                nDataRanges = len(dataRanges)
                                if (nDataRanges == 1): dataRanges_str = "{:s} ~ {:s}".format(datetime.fromtimestamp(dataRanges[0][0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"), datetime.fromtimestamp(dataRanges[0][1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
                                else:
                                    dataRanges_str = ""
                                    for dataRange in dataRanges: dataRanges_str += "({:s} ~ {:s})".format(datetime.fromtimestamp(dataRange[0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"), datetime.fromtimestamp(dataRange[1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
                            self.GUIOs["MARKET&INFORMATION_DATARANGEDISPLAYTEXT"].updateText(text = dataRanges_str)
            #If need to reapply filter
            if   (_resetList         == True): self.pageAuxillaryFunctions['SETCURRENCYLIST']()
            elif (_reapplyListFilter == True): self.pageAuxillaryFunctions['ONCURRENCYFILTERUPDATE']()
    def __far_onAnalyzerCentralUpdate(requester, updatedContents):
        if (requester == 'TRADEMANAGER'):
            for updatedContent in updatedContents:
                updatedContent_type = type(updatedContent)
                if (updatedContent_type == str):
                    if (updatedContent == 'nCurrencyAnalysis_unallocated'):
                        nCAs = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ANALYZERCENTRAL', 'nCurrencyAnalysis_unallocated'))
                        self.puVar['analyzerCentral']['nCurrencyAnalysis_unallocated'] = nCAs
                        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCAUNALLOCATEDDISPLAYTEXT"].updateText(text = str(nCAs))
                    if (updatedContent == 'nCurrencyAnalysis_allocated'):
                        nCAs = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ANALYZERCENTRAL', 'nCurrencyAnalysis_allocated'))
                        self.puVar['analyzerCentral']['nCurrencyAnalysis_allocated'] = nCAs
                        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCAALLOCATEDDISPLAYTEXT"].updateText(text = str(nCAs))
                    if (updatedContent == 'nCurrencyAnalysis_CONFIGNOTFOUND'):
                        nCAs = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ANALYZERCENTRAL', 'nCurrencyAnalysis_CONFIGNOTFOUND'))
                        self.puVar['analyzerCentral']['nCurrencyAnalysis_CONFIGNOTFOUND'] = nCAs
                        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCACONFIGNOTFOUNDDISPLAYTEXT"].updateText(text = str(nCAs))
                    if (updatedContent == 'nCurrencyAnalysis_CURRENCYNOTFOUND'):
                        nCAs = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ANALYZERCENTRAL', 'nCurrencyAnalysis_CURRENCYNOTFOUND'))
                        self.puVar['analyzerCentral']['nCurrencyAnalysis_CURRENCYNOTFOUND'] = nCAs
                        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCACURRENCYNOTFOUNDDISPLAYTEXT"].updateText(text = str(nCAs))
                    if (updatedContent == 'nCurrencyAnalysis_WAITINGTRADING'):
                        nCAs = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ANALYZERCENTRAL', 'nCurrencyAnalysis_WAITINGTRADING'))
                        self.puVar['analyzerCentral']['nCurrencyAnalysis_WAITINGTRADING'] = nCAs
                        self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCAWAITINGTRADINGDISPLAYTEXT"].updateText(text = str(nCAs))
                    elif (updatedContent == 'averagePIPGenerationTime_ns'):
                        averagePIPGenerationTime_ns = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ANALYZERCENTRAL', 'averagePIPGenerationTime_ns'))
                        self.puVar['analyzerCentral']['averagePIPGenerationTime_ns'] = averagePIPGenerationTime_ns
                        if (averagePIPGenerationTime_ns == None): self.GUIOs["TRADEMANAGER&ANALYZERS_AVERAGEPIPGENERATIONTIMEDISPLAYTEXT"].updateText(text = "-")
                        else:                                     self.GUIOs["TRADEMANAGER&ANALYZERS_AVERAGEPIPGENERATIONTIMEDISPLAYTEXT"].updateText(text = "{:.3f} ms".format(averagePIPGenerationTime_ns/1e6))
                elif (updatedContent_type == tuple):
                    if (updatedContent[0] == 'nCurrencyAnalysis_total'):
                        updatedAnalyzer = updatedContent[1]
                        nCAs = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ANALYZERCENTRAL', 'nCurrencyAnalysis_total', updatedAnalyzer))
                        self.puVar['analyzerCentral']['nCurrencyAnalysis_total'][updatedAnalyzer] = nCAs
                        if (updatedAnalyzer == self.puVar['analyzerCentral_selectedAnalyzer']): self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCATOTALDISPLAYTEXT"].updateText(text = str(nCAs))
                    elif (updatedContent[0] == 'nCurrencyAnalysis_WAITINGSTREAM'):
                        updatedAnalyzer = updatedContent[1]
                        nCAs = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ANALYZERCENTRAL', 'nCurrencyAnalysis_WAITINGSTREAM', updatedAnalyzer))
                        self.puVar['analyzerCentral']['nCurrencyAnalysis_WAITINGSTREAM'][updatedAnalyzer] = nCAs
                        if (updatedAnalyzer == self.puVar['analyzerCentral_selectedAnalyzer']): self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAWAITINGSTREAMDISPLAYTEXT"].updateText(text = str(nCAs))
                    elif (updatedContent[0] == 'nCurrencyAnalysis_WAITINGDATAAVAILABLE'):
                        updatedAnalyzer = updatedContent[1]
                        nCAs = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ANALYZERCENTRAL', 'nCurrencyAnalysis_WAITINGDATAAVAILABLE', updatedAnalyzer))
                        self.puVar['analyzerCentral']['nCurrencyAnalysis_WAITINGDATAAVAILABLE'][updatedAnalyzer] = nCAs
                        if (updatedAnalyzer == self.puVar['analyzerCentral_selectedAnalyzer']): self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAWAITINGDATAAVAILABLEDISPLAYTEXT"].updateText(text = str(nCAs))
                    elif (updatedContent[0] == 'nCurrencyAnalysis_PREPARING'):
                        updatedAnalyzer = updatedContent[1]
                        nCAs = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ANALYZERCENTRAL', 'nCurrencyAnalysis_PREPARING', updatedAnalyzer))
                        self.puVar['analyzerCentral']['nCurrencyAnalysis_PREPARING'][updatedAnalyzer] = nCAs
                        if (updatedAnalyzer == self.puVar['analyzerCentral_selectedAnalyzer']): self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAPREPARINGDISPLAYTEXT"].updateText(text = str(nCAs))
                    elif (updatedContent[0] == 'nCurrencyAnalysis_ANALYZINGREALTIME'):
                        updatedAnalyzer = updatedContent[1]
                        nCAs = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ANALYZERCENTRAL', 'nCurrencyAnalysis_ANALYZINGREALTIME', updatedAnalyzer))
                        self.puVar['analyzerCentral']['nCurrencyAnalysis_ANALYZINGREALTIME'][updatedAnalyzer] = nCAs
                        if (updatedAnalyzer == self.puVar['analyzerCentral_selectedAnalyzer']): self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAANALYZINGREALTIMEDISPLAYTEXT"].updateText(text = str(nCAs))
                    elif (updatedContent[0] == 'nCurrencyAnalysis_ERROR'):
                        updatedAnalyzer = updatedContent[1]
                        nCAs = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('ANALYZERCENTRAL', 'nCurrencyAnalysis_ERROR', updatedAnalyzer))
                        self.puVar['analyzerCentral']['nCurrencyAnalysis_ERROR'][updatedAnalyzer] = nCAs
                        if (updatedAnalyzer == self.puVar['analyzerCentral_selectedAnalyzer']): self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAERRORDISPLAYTEXT"].updateText(text = str(nCAs))
    def __far_onAnalysisConfigurationUpdate(requester, updateType, currencyAnalysisConfigurationCode):
        if (requester == 'TRADEMANAGER'):
            if (updateType == 'EDITED'):
                self.puVar['analysisConfigurations'][currencyAnalysisConfigurationCode] = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSISCONFIGURATIONS', currencyAnalysisConfigurationCode))
                if (self.puVar['analysisConfiguration_selected'] == currencyAnalysisConfigurationCode): self.pageAuxillaryFunctions['SETANALYSISCONFIGURATIONGUIOS'](configuration = self.puVar['analysisConfigurations'][currencyAnalysisConfigurationCode])
            elif (updateType == 'ADDED'):
                self.puVar['analysisConfigurations'][currencyAnalysisConfigurationCode] = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSISCONFIGURATIONS', currencyAnalysisConfigurationCode))
                self.pageAuxillaryFunctions['SETANALYSISCONFIGURATIONLIST']()
            elif (updateType == 'REMOVED'):
                del self.puVar['analysisConfigurations'][currencyAnalysisConfigurationCode]
                self.pageAuxillaryFunctions['SETANALYSISCONFIGURATIONLIST']()
                if (currencyAnalysisConfigurationCode == self.puVar['toAnalysisList_analysisConfiguration_selected']): 
                    self.puVar['toAnalysisList_analysisConfiguration_selected'] = None
                    self.GUIOs["MARKET&TOANALYSISLIST_ANALYSISLISTADD"].deactivate()
                if (currencyAnalysisConfigurationCode == self.puVar['configurationControl_analysisConfiguration_selected']): 
                    self.puVar['configurationControl_analysisConfiguration_selected'] = None
                    self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONREMOVE"].deactivate()
                    self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_CONFIGURATIONADD"].activate()
    def __far_onCurrencyAnalysisUpdate(requester, updateType, currencyAnalysisCode):
        if (requester == 'TRADEMANAGER'):
            #[1]: Status Updated
            if (updateType == 'UPDATE_STATUS'):
                _ca_status = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode, 'status'))
                self.puVar['currencyAnalysis'][currencyAnalysisCode]['status'] = _ca_status
                if   (_ca_status == 'CURRENCYNOTFOUND'):     _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_CURRENCYNOTFOUND');     _ca_status_str_color = 'RED'
                elif (_ca_status == 'CONFIGNOTFOUND'):       _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_CONFIGNOTFOUND');       _ca_status_str_color = 'RED_LIGHT'
                elif (_ca_status == 'WAITINGTRADING'):       _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_WAITINGTRADING');       _ca_status_str_color = 'ORANGE_LIGHT'
                elif (_ca_status == 'WAITINGNNCDATA'):       _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_WAITINGNNCDATA');       _ca_status_str_color = 'BLUE_DARK'
                elif (_ca_status == 'WAITINGSTREAM'):        _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_WAITINGSTREAM');        _ca_status_str_color = 'BLUE_DARK'
                elif (_ca_status == 'WAITINGDATAAVAILABLE'): _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_WAITINGDATAAVAILABLE'); _ca_status_str_color = 'BLUE_LIGHT'
                elif (_ca_status == 'PREP_QUEUED'):          _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_PREP_QUEUED');          _ca_status_str_color = 'BLUE_LIGHT'
                elif (_ca_status == 'PREP_FETCHINGKLINES'):  _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_PREP_FETCHINGKLINES');  _ca_status_str_color = 'BLUE_LIGHT'
                elif (_ca_status == 'PREP_ANALYZINGKLINES'): _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_PREP_ANALYZINGKLINES'); _ca_status_str_color = 'BLUE_LIGHT'
                elif (_ca_status == 'ANALYZINGREALTIME'):    _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_ANALYZINGREALTIME');    _ca_status_str_color = 'GREEN_LIGHT'
                elif (_ca_status == 'ERROR'):                _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_ERROR');                _ca_status_str_color = 'RED_DARK'
                _newSelectionBoxItem = {'text': _ca_status_str, 'textStyles': [('all', _ca_status_str_color),], 'textAnchor': 'CENTER'}
                self.GUIOs["TRADEMANAGER&CURRENCYANALYSIS_SELECTIONBOX"].editSelectionListItem(itemKey = currencyAnalysisCode, item = _newSelectionBoxItem, columnIndex = 3)
                if (currencyAnalysisCode == self.puVar['currencyAnalysis_selected']):
                    if (_ca_status == 'ANALYZINGREALTIME'): self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_VIEWCURRENCYANALYSISCHART"].activate()
                    else:                                   self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_VIEWCURRENCYANALYSISCHART"].deactivate()
            #[2]: Analyzer Updated
            elif (updateType == 'UPDATE_ANALYZER'):
                allocatedAnalyzer = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode, 'allocatedAnalyzer'))
                self.puVar['currencyAnalysis'][currencyAnalysisCode]['allocatedAnalyzer'] = allocatedAnalyzer
                if (currencyAnalysisCode == self.puVar['currencyAnalysis_selected']):
                    if (allocatedAnalyzer == None): self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_ALLOCATEDANALYZERDISPLAYTEXT"].updateText(text = "-")
                    else:                           self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_ALLOCATEDANALYZERDISPLAYTEXT"].updateText(text = "ANALYZER {:d}".format(allocatedAnalyzer))
            #[3]: Added
            elif (updateType == 'ADDED'):
                self.puVar['currencyAnalysis'][currencyAnalysisCode] = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('CURRENCYANALYSIS', currencyAnalysisCode))
                self.pageAuxillaryFunctions['SETCURRENCYANALYSISLIST']()
            #[4]: Removed
            elif (updateType == 'REMOVED'):
                del self.puVar['currencyAnalysis'][currencyAnalysisCode]
                self.pageAuxillaryFunctions['SETCURRENCYANALYSISLIST']()
                if (currencyAnalysisCode == self.puVar['currencyAnalysis_selected']):
                    self.puVar['currencyAnalysis_selected'] = None
                    self.pageAuxillaryFunctions['UPDATECURRENCYANALYSISINFO']()
                    self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_VIEWCURRENCYANALYSISCHART"].deactivate()
                    self.GUIOs["TRADEMANAGER&CURRENCYANALYSISCONTROL_REMOVEANALYSIS"].deactivate()
    def __far_onTradeConfigurationUpdate(requester, updateType, tradeConfigurationCode):
        if (requester == 'TRADEMANAGER'):
            if (updateType == 'ADDED'):
                self.puVar['tradeConfigurations'][tradeConfigurationCode] = self.ipcA.getPRD(processName = 'TRADEMANAGER', prdAddress = ('TRADECONFIGURATIONS', tradeConfigurationCode))
                self.pageAuxillaryFunctions['SETTRADECONFIGURATIONLIST']()
            elif (updateType == 'REMOVED'):
                del self.puVar['tradeConfigurations'][tradeConfigurationCode]
                self.pageAuxillaryFunctions['SETTRADECONFIGURATIONLIST']()
                if (tradeConfigurationCode == self.puVar['tradeConfiguration_selected']): 
                    self.puVar['tradeConfiguration_selected'] = None
                    self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONREMOVE"].deactivate()
                    self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONADD"].activate()
    auxFunctions['_FAR_ONCURRENCIESUPDATE']            = __far_onCurrenciesUpdate
    auxFunctions['_FAR_ONANALYZERCENTRALUPDATE']       = __far_onAnalyzerCentralUpdate
    auxFunctions['_FAR_ONANALYSISCONFIGURATIONUPDATE'] = __far_onAnalysisConfigurationUpdate
    auxFunctions['_FAR_ONCURRENCYANALYSISUPDATE']      = __far_onCurrencyAnalysisUpdate
    auxFunctions['_FAR_ONTRADECONFIGURATIONUPDATE']    = __far_onTradeConfigurationUpdate

    #<Market&Filter>
    def __onCurrencyFilterUpdate():
        #Localize filter settings
        filter_symbol = self.GUIOs["MARKET&FILTER_SEARCHTITLETEXTINPUTBOX"].getText()
        filter_trading = None
        if   (self.GUIOs["MARKET&FILTER_FILTERSWITCH_TRADINGTRUE"].getStatus()  == True): filter_trading = True
        elif (self.GUIOs["MARKET&FILTER_FILTERSWITCH_TRADINGFALSE"].getStatus() == True): filter_trading = False
        filter_nKlinesMin = None
        if (self.GUIOs["MARKET&FILTER_FILTERSWITCH_MINNUMBEROFKLINES"].getStatus() == True):
            try: filter_nKlinesMin = int(self.GUIOs["MARKET&FILTER_FILTERSWITCH_MINNUMBEROFKLINESTEXTINPUTBOX"].getText())
            except: pass
        filter_sort = None
        if   (self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYID"].getStatus()         == True): filter_sort = 'id'
        elif (self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYSYMBOL"].getStatus()     == True): filter_sort = 'symbol'
        elif (self.GUIOs["MARKET&FILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].getStatus() == True): filter_sort = 'firstKline'
        #Filter symbols
        symbols = list(self.puVar['currencies'].keys())
        symbols_filtered = list()
        minuteNumber_current = int(time.time()/60)
        for symbol in symbols:
            testFailed = False
            #Symbol Filter
            if not(filter_symbol in symbol): testFailed = True
            #Status Filter
            if (filter_trading == True):
                if not((self.puVar['currencies'][symbol]['info_server'] != None) and (self.puVar['currencies'][symbol]['info_server']['status'] == 'TRADING')): testFailed = True
            elif (filter_trading == False):
                if ((self.puVar['currencies'][symbol]['info_server'] != None) and (self.puVar['currencies'][symbol]['info_server']['status'] == 'TRADING')): testFailed = True
            #nKlines_min Filter
            if (filter_nKlinesMin != None):
                firstClosedOpenTS_minuteNumber = int(self.puVar['currencies'][symbol]['kline_firstOpenTS']/60)
                nKlines = minuteNumber_current-firstClosedOpenTS_minuteNumber+1
                if (nKlines < filter_nKlinesMin): testFailed = True
            #If all tests passed
            if (testFailed == False): symbols_filtered.append(symbol)
        #Symbols Sorting
        symbols_forSort = list()
        for symbol in symbols_filtered:
            currencyID       = self.puVar['currencies'][symbol]['currencyID']
            firstKlineOpenTS = self.puVar['currencies'][symbol]['kline_firstOpenTS']
            if (firstKlineOpenTS == None): symbol_forSort = (currencyID, symbol, float('inf'))
            else:                          symbol_forSort = (currencyID, symbol, firstKlineOpenTS)
            symbols_forSort.append(symbol_forSort)
        if   (filter_sort == 'id'):         symbols_forSort.sort(key = lambda x: x[0])
        elif (filter_sort == 'symbol'):     symbols_forSort.sort(key = lambda x: x[1])
        elif (filter_sort == 'firstKline'): symbols_forSort.sort(key = lambda x: x[2])
        #Finally
        symbols_filteredAndSorted = [symbol_forSort[1] for symbol_forSort in symbols_forSort]
        self.GUIOs["MARKET&CURRENCIES_SELECTIONBOX"].setDisplayTargets(displayTargets = symbols_filteredAndSorted)
        _nCurrencies_total    = len(self.puVar['currencies'])
        _nCurrencies_filtered = len(symbols_filteredAndSorted)
        self.GUIOs["MARKET&CURRENCIES_LISTINFO_NCURRENCIESDISPLAYTEXT"].updateText(text = "{:d} / {:d}".format(_nCurrencies_filtered, _nCurrencies_total))
    auxFunctions['ONCURRENCYFILTERUPDATE'] = __onCurrencyFilterUpdate

    #<Market&Currencies>
    def __setCurrencyList():
        #Format and update the selectionBox object
        currencies_selectionList = dict()
        _nCurrencies = len(self.puVar['currencies'])
        for _cIndex, _symbol in enumerate(self.puVar['currencies']):
            if (self.puVar['currencies'][_symbol]['info_server'] == None): _status_str = "-"; _status_str_color = 'BLUE_DARK'
            else:
                currencyStatus = self.puVar['currencies'][_symbol]['info_server']['status']
                if   (currencyStatus == 'TRADING'):  _status_str = self.visualManager.getTextPack('AUTOTRADE:MARKET&CURRENCIES_STATUS_TRADING');  _status_str_color = 'GREEN_LIGHT'
                elif (currencyStatus == 'SETTLING'): _status_str = self.visualManager.getTextPack('AUTOTRADE:MARKET&CURRENCIES_STATUS_SETTLING'); _status_str_color = 'RED_LIGHT'
                elif (currencyStatus == 'REMOVED'):  _status_str = self.visualManager.getTextPack('AUTOTRADE:MARKET&CURRENCIES_STATUS_REMOVED');  _status_str_color = 'RED_DARK'
                else:                                _status_str = currencyStatus;                                                                _status_str_color = 'ORANGE_LIGHT'
            firstOpenTS = self.puVar['currencies'][_symbol]['kline_firstOpenTS']
            if (firstOpenTS == None): firstOpenTS_str = "-"
            else:                     firstOpenTS_str = datetime.fromtimestamp(self.puVar['currencies'][_symbol]['kline_firstOpenTS'], tz=timezone.utc).strftime("%Y/%m/%d %H:%M")
            currencies_selectionList[_symbol] = [{'text': "{:d} / {:d}".format(_cIndex+1, _nCurrencies), 'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'},
                                                 {'text': _symbol,                                       'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'},
                                                 {'text': _status_str,                                   'textStyles': [('all', _status_str_color),], 'textAnchor': 'CENTER'},
                                                 {'text': firstOpenTS_str,                               'textStyles': [('all', 'DEFAULT'),],         'textAnchor': 'CENTER'}]
        self.GUIOs["MARKET&CURRENCIES_SELECTIONBOX"].setSelectionList(selectionList = currencies_selectionList, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)
        self.pageAuxillaryFunctions['ONCURRENCYFILTERUPDATE']()
    auxFunctions['SETCURRENCYLIST'] = __setCurrencyList

    #<Market&Information>
    def __updateCurrencyInfo():
        selectedCurrency_symbol = self.puVar['currency_selected']
        if ((selectedCurrency_symbol != None) and (selectedCurrency_symbol in self.puVar['currencies'])):
            _currency            = self.puVar['currencies'][selectedCurrency_symbol]
            _currency_currencyID = _currency['currencyID']
            _currency_dataRanges = _currency['kline_availableRanges']
            self.GUIOs["MARKET&INFORMATION_CURRENCYIDDISPLAYTEXT"].updateText(text = str(_currency_currencyID))
            if (_currency_dataRanges == None): _currency_dataRanges_str = "-"
            else:
                nDataRanges = len(_currency_dataRanges)
                if (nDataRanges == 1): _currency_dataRanges_str = "{:s} ~ {:s}".format(datetime.fromtimestamp(_currency_dataRanges[0][0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"), datetime.fromtimestamp(_currency_dataRanges[0][1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
                else:
                    _currency_dataRanges_str = ""
                    for dataRange in _currency_dataRanges: _currency_dataRanges_str += "({:s} ~ {:s})".format(datetime.fromtimestamp(dataRange[0], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"), datetime.fromtimestamp(dataRange[1], tz=timezone.utc).strftime("%Y/%m/%d %H:%M"))
            self.GUIOs["MARKET&INFORMATION_DATARANGEDISPLAYTEXT"].updateText(text = _currency_dataRanges_str)
        else:
            self.GUIOs["MARKET&INFORMATION_CURRENCYIDDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["MARKET&INFORMATION_DATARANGEDISPLAYTEXT"].updateText(text  = "-")
    auxFunctions['UPDATECURRENCYINFO'] = __updateCurrencyInfo

    #<Market&ToAnalysisList>
    def __farr_onAnalysisAddRequestResponse(responder, requestID, functionResult):
        requestResult       = functionResult['result']
        tradeManagerMessage = functionResult['message']
        if (requestResult == True): self.GUIOs["MESSAGEDISPLAYTEXT_DISPLAYTEXT"].updateText(text = tradeManagerMessage, textStyle = 'GREEN')
        else:                       self.GUIOs["MESSAGEDISPLAYTEXT_DISPLAYTEXT"].updateText(text = tradeManagerMessage, textStyle = 'RED')
        self.puVar['toAnalysisList_waitingResponse'] = False
        self.pageAuxillaryFunctions['CHECKIFCANADDCURRENCYANALYSIS']()
    def __checkIfCanAddCurrencyAnalysis():
        #---Response Waiting
        _test_waitingResponse = not(self.puVar['toAnalysisList_waitingResponse'])
        #---Currency Check
        _test_currency = False
        _currency_selected = self.puVar['currency_selected']
        if (_currency_selected != None):
            _currency = self.puVar['currencies'][_currency_selected]
            if ((_currency['info_server'] != None) and (_currency['info_server']['status'] == 'TRADING')): _test_currency = True
        #---CAC Code Check
        _test_cacCode = False
        _cacCode_selected = self.puVar['toAnalysisList_analysisConfiguration_selected']
        if (_cacCode_selected != None): _test_cacCode = True
        #---CA Code Check
        _test_caCode = False
        _aCode_entered = self.GUIOs["MARKET&TOANALYSISLIST_ANALYSISCODETEXTINPUTBOX"].getText()
        if (_aCode_entered == "") or (_aCode_entered not in self.puVar['analysisConfigurations']): _test_caCode = True
        #---Finally
        if ((_test_waitingResponse == True) and (_test_currency == True) and (_test_cacCode == True) and (_test_caCode == True)): self.GUIOs["MARKET&TOANALYSISLIST_ANALYSISLISTADD"].activate()
        else:                                                                                                                     self.GUIOs["MARKET&TOANALYSISLIST_ANALYSISLISTADD"].deactivate()
    auxFunctions['_FARR_ONANALYSISADDREQUESTRESPONSE'] = __farr_onAnalysisAddRequestResponse
    auxFunctions['CHECKIFCANADDCURRENCYANALYSIS']      = __checkIfCanAddCurrencyAnalysis

    #<TradeManager&Analyzers>
    def __updateAnalyzerCentralInfo(updateAll):
        if (self.puVar['analyzerCentral'] != _IPC_PRD_INVALIDADDRESS):
            if (updateAll == True):
                if (self.puVar['analyzerCentral_nAnalyzersIdentified'] == False):
                    nAnalyzers = self.puVar['analyzerCentral']['nAnalyzers']
                    self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFANALYZERSDISPLAYTEXT"].updateText(text = str(nAnalyzers))
                    analyzerList_formatted = {'total': {'text': 'TOTAL'}}
                    for analyzerIndex in range (nAnalyzers): analyzerList_formatted[analyzerIndex] = {'text': 'ANALYZER {:d}'.format(analyzerIndex)}
                    self.GUIOs["TRADEMANAGER&ANALYZERS_ANALYZERSELECTIONBOX"].setSelectionList(selectionList = analyzerList_formatted, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)
                    self.GUIOs["TRADEMANAGER&ANALYZERS_ANALYZERSELECTIONBOX"].setSelected(itemKey = 'total', callSelectionUpdateFunction = False)
                    self.puVar['analyzerCentral_selectedAnalyzer']     = 'total'
                    self.puVar['analyzerCentral_nAnalyzersIdentified'] = True
                self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCAUNALLOCATEDDISPLAYTEXT"].updateText(text      = str(self.puVar['analyzerCentral']['nCurrencyAnalysis_unallocated']))
                self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCAALLOCATEDDISPLAYTEXT"].updateText(text        = str(self.puVar['analyzerCentral']['nCurrencyAnalysis_allocated']))
                self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCACONFIGNOTFOUNDDISPLAYTEXT"].updateText(text   = str(self.puVar['analyzerCentral']['nCurrencyAnalysis_CONFIGNOTFOUND']))
                self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCACURRENCYNOTFOUNDDISPLAYTEXT"].updateText(text = str(self.puVar['analyzerCentral']['nCurrencyAnalysis_CURRENCYNOTFOUND']))
                self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCAWAITINGTRADINGDISPLAYTEXT"].updateText(text   = str(self.puVar['analyzerCentral']['nCurrencyAnalysis_WAITINGTRADING']))
                avgPIPGenTime_ns = self.puVar['analyzerCentral']['averagePIPGenerationTime_ns']
                if (avgPIPGenTime_ns == None): self.GUIOs["TRADEMANAGER&ANALYZERS_AVERAGEPIPGENERATIONTIMEDISPLAYTEXT"].updateText(text  = "-")
                else:                          self.GUIOs["TRADEMANAGER&ANALYZERS_AVERAGEPIPGENERATIONTIMEDISPLAYTEXT"].updateText(text  = "{:.3f} ms".format(avgPIPGenTime_ns/1e6))
            selectedAnalyzer = self.puVar['analyzerCentral_selectedAnalyzer']
            if (selectedAnalyzer != None):
                self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCATOTALDISPLAYTEXT"].updateText(text                = str(self.puVar['analyzerCentral']['nCurrencyAnalysis_total'][selectedAnalyzer]))
                self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAWAITINGSTREAMDISPLAYTEXT"].updateText(text        = str(self.puVar['analyzerCentral']['nCurrencyAnalysis_WAITINGSTREAM'][selectedAnalyzer]))
                self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAWAITINGDATAAVAILABLEDISPLAYTEXT"].updateText(text = str(self.puVar['analyzerCentral']['nCurrencyAnalysis_WAITINGDATAAVAILABLE'][selectedAnalyzer]))
                self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAPREPARINGDISPLAYTEXT"].updateText(text            = str(self.puVar['analyzerCentral']['nCurrencyAnalysis_PREPARING'][selectedAnalyzer]))
                self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAANALYZINGREALTIMEDISPLAYTEXT"].updateText(text    = str(self.puVar['analyzerCentral']['nCurrencyAnalysis_ANALYZINGREALTIME'][selectedAnalyzer]))
                self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAERRORDISPLAYTEXT"].updateText(text                = str(self.puVar['analyzerCentral']['nCurrencyAnalysis_ERROR'][selectedAnalyzer]))
        else:
            if (updateAll == True):
                self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCAUNALLOCATEDDISPLAYTEXT"].updateText(text      = "-")
                self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCAALLOCATEDDISPLAYTEXT"].updateText(text        = "-")
                self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCACONFIGNOTFOUNDDISPLAYTEXT"].updateText(text   = "-")
                self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCACURRENCYNOTFOUNDDISPLAYTEXT"].updateText(text = "-")
                self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROCAWAITINGTRADINGDISPLAYTEXT"].updateText(text   = "-")
                self.GUIOs["TRADEMANAGER&ANALYZERS_AVERAGEPIPGENERATIONTIMEDISPLAYTEXT"].updateText(text  = "-")
            self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCATOTALDISPLAYTEXT"].updateText(text                = "-")
            self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAWAITINGSTREAMDISPLAYTEXT"].updateText(text        = "-")
            self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAWAITINGDATAAVAILABLEDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAPREPARINGDISPLAYTEXT"].updateText(text            = "-")
            self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAANALYZINGREALTIMEDISPLAYTEXT"].updateText(text    = "-")
            self.GUIOs["TRADEMANAGER&ANALYZERS_NUMBEROFCAERRORDISPLAYTEXT"].updateText(text                = "-")
    auxFunctions['UPDATEANALYZERCENTRALINFO'] = __updateAnalyzerCentralInfo

    #<TradeManager&ConfigurationControl>
    def __setAnalysisConfigurationList(): #<--- This is shared with <Market&ToAnalysisList>
        analysisConfigurations_selectionList = dict()
        for analysisConfigurationCode in self.puVar['analysisConfigurations']: analysisConfigurations_selectionList[analysisConfigurationCode] = {'text': analysisConfigurationCode, 'textAnchor': 'W'}
        self.GUIOs["MARKET&TOANALYSISLIST_ANALYSISCONFIGSELECTIONBOX"].setSelectionList(selectionList = analysisConfigurations_selectionList, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)
        self.GUIOs["TRADEMANAGER&CONFIGURATIONCONTROL_SELECTIONBOX"].setSelectionList(selectionList   = analysisConfigurations_selectionList, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)
    def __setAnalysisConfigurationGUIOs(configuration):
        self.pageAuxillaryFunctions['UPDATENEURALNETWORKCODESLIST']()
        #MAIN
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_SMA"].setStatus(status        = configuration['SMA_Master'],        callStatusUpdateFunction = False)
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_EMA"].setStatus(status        = configuration['EMA_Master'],        callStatusUpdateFunction = False)
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_WMA"].setStatus(status        = configuration['WMA_Master'],        callStatusUpdateFunction = False)
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_PSAR"].setStatus(status       = configuration['PSAR_Master'],       callStatusUpdateFunction = False)
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_BOL"].setStatus(status        = configuration['BOL_Master'],        callStatusUpdateFunction = False)
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_IVP"].setStatus(status        = configuration['IVP_Master'],        callStatusUpdateFunction = False)
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_PIP"].setStatus(status        = configuration['PIP_Master'],        callStatusUpdateFunction = False)
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_VOL"].setStatus(status        = configuration['VOL_Master'],        callStatusUpdateFunction = False)
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_MMACDSHORT"].setStatus(status = configuration['MMACDSHORT_Master'], callStatusUpdateFunction = False)
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_MMACDLONG"].setStatus(status  = configuration['MMACDLONG_Master'],  callStatusUpdateFunction = False)
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_DMIxADX"].setStatus(status    = configuration['DMIxADX_Master'],    callStatusUpdateFunction = False)
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_MFI"].setStatus(status        = configuration['MFI_Master'],        callStatusUpdateFunction = False)
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_WOI"].setStatus(status        = configuration['WOI_Master'],        callStatusUpdateFunction = False)
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_NES"].setStatus(status        = configuration['NES_Master'],        callStatusUpdateFunction = False)
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["MINCOMPLETEANALYSISTEXTINPUTBOX"].updateText(text   = str(configuration['NI_MinCompleteAnalysis']))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["NANALYSISDISPLAYTEXTINPUTBOX"].updateText(text      = str(configuration['NI_NAnalysisToDisplay']))
        #SMA
        for lineIndex in range (10):
            lineNumber = lineIndex+1
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SMA"].GUIOs["SMA_{:d}_LINE".format(lineNumber)].setStatus(status = configuration['SMA_{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SMA"].GUIOs["SMA_{:d}_NSAMPLES".format(lineNumber)].updateText(text = str(configuration['SMA_{:d}_NSamples'.format(lineNumber)]))
        #EMA
        for lineIndex in range (10):
            lineNumber = lineIndex+1
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_EMA"].GUIOs["EMA_{:d}_LINE".format(lineNumber)].setStatus(status = configuration['EMA_{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_EMA"].GUIOs["EMA_{:d}_NSAMPLES".format(lineNumber)].updateText(text = str(configuration['EMA_{:d}_NSamples'.format(lineNumber)]))
        #WMA
        for lineIndex in range (10):
            lineNumber = lineIndex+1
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WMA"].GUIOs["WMA_{:d}_LINE".format(lineNumber)].setStatus(status = configuration['WMA_{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WMA"].GUIOs["WMA_{:d}_NSAMPLES".format(lineNumber)].updateText(text = str(configuration['WMA_{:d}_NSamples'.format(lineNumber)]))
        #PSAR
        for lineIndex in range (5):
            lineNumber = lineIndex+1
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs["PSAR_{:d}_LINE".format(lineNumber)].setStatus(status = configuration['PSAR_{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs["PSAR_{:d}_AF0".format(lineNumber)].updateText(text = "{:.3f}".format(configuration['PSAR_{:d}_AF0'.format(lineNumber)]))
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs["PSAR_{:d}_AF+".format(lineNumber)].updateText(text = "{:.3f}".format(configuration['PSAR_{:d}_AF+'.format(lineNumber)]))
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs["PSAR_{:d}_AFMAX".format(lineNumber)].updateText(text = "{:.3f}".format(configuration['PSAR_{:d}_AFMax'.format(lineNumber)]))
        #BOL
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"].GUIOs["BOLMATYPESELECTIONBOX"].setSelected(itemKey = configuration['BOL_MAType'], callSelectionUpdateFunction = False)
        for lineIndex in range (10):
            lineNumber = lineIndex+1
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"].GUIOs["BOL_{:d}_LINE".format(lineNumber)].setStatus(status = configuration['BOL_{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"].GUIOs["BOL_{:d}_NSAMPLES".format(lineNumber)].updateText(text = str(configuration['BOL_{:d}_NSamples'.format(lineNumber)]))
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"].GUIOs["BOL_{:d}_BANDWIDTH".format(lineNumber)].updateText(text = "{:.1f}".format(configuration['BOL_{:d}_BandWidth'.format(lineNumber)]))
        #IVP
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["NSAMPLESTEXTINPUTBOX"].updateText(text = str(configuration['IVP_NSamples']))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["GAMMAFACTORSLIDER"].setSliderValue(newValue = (configuration['IVP_GammaFactor']-0.005)*(100/0.095))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["GAMMAFACTORDISPLAYTEXT"].updateText(text = "{:.1f} %".format(configuration['IVP_GammaFactor']*100))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["DELTAFACTORSLIDER"].setSliderValue(newValue = (configuration['IVP_DeltaFactor']-0.1)*(100/9.9))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["DELTAFACTORDISPLAYTEXT"].updateText(text = "{:d} %".format(int(configuration['IVP_DeltaFactor']*100)))
        #PIP
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NEURALNETWORKCODESELECTIONBOX"].setSelected(itemKey = configuration['PIP_NeuralNetworkCode'], callSelectionUpdateFunction = False)
        if (configuration['PIP_NeuralNetworkCode'] == None): self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NEURALNETWORKCODERELEASEBUTTON"].deactivate()
        else:                                                self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NEURALNETWORKCODERELEASEBUTTON"].activate()
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["SWINGRANGESLIDER"].setSliderValue(newValue                         = (configuration['PIP_SwingRange']            -0.0010)*(100/0.0490))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NNAALPHAVALUESLIDER"].setSliderValue(newValue                      = (configuration['PIP_NNAAlpha']              -0.05)  *(100/0.95))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NNABETAVALUESLIDER"].setSliderValue(newValue                       = (configuration['PIP_NNABeta']               -2)     *(100/18))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALALPHAVALUESLIDER"].setSliderValue(newValue                = (configuration['PIP_ClassicalAlpha']        -0.1)   *(100/2.9))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALBETAVALUESLIDER"].setSliderValue(newValue                 = (configuration['PIP_ClassicalBeta']         -2)     *(100/18))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALACTIVATIONTHRESHOLD1VALUESLIDER"].setSliderValue(newValue = (configuration['PIP_CSActivationThreshold1']-0.00)  *(100/0.95))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALACTIVATIONTHRESHOLD2VALUESLIDER"].setSliderValue(newValue = (configuration['PIP_CSActivationThreshold2']-0.05)  *(100/0.95))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALNSAMPLESTEXTINPUTBOX"].updateText(text = "{:d}".format(configuration['PIP_ClassicalNSamples']))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALSIGMATEXTINPUTBOX"].updateText(text    = "{:.1f}".format(configuration['PIP_ClassicalSigma']))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["WOIACTIVATIONTHRESHOLDVALUESLIDER"].setSliderValue(newValue        = (configuration['PIP_WSActivationThreshold'] -0.00)  *(100/0.95))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["SWINGRANGEDISPLAYTEXT"].updateText(text               = "{:.2f} %".format(configuration['PIP_SwingRange']*100))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NNAALPHAVALUEDISPLAYTEXT"].updateText(text            = "{:.2f}".format(configuration['PIP_NNAAlpha']))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NNABETAVALUEDISPLAYTEXT"].updateText(text             = "{:d}".format(configuration['PIP_NNABeta']))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALALPHAVALUEDISPLAYTEXT"].updateText(text      = "{:.1f}".format(configuration['PIP_ClassicalAlpha']))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALBETAVALUEDISPLAYTEXT"].updateText(text       = "{:d}".format(configuration['PIP_ClassicalBeta']))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALACTIVATIONTHRESHOLD1VALUEDISPLAYTEXT"].updateText(text = "{:.2f}".format(configuration['PIP_CSActivationThreshold1']))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALACTIVATIONTHRESHOLD2VALUEDISPLAYTEXT"].updateText(text = "{:.2f}".format(configuration['PIP_CSActivationThreshold2']))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["WOIACTIVATIONTHRESHOLDVALUEDISPLAYTEXT"].updateText(text        = "{:.2f}".format(configuration['PIP_WSActivationThreshold']))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["ACTIONSIGNALMODESELECTIONBOX"].setSelected(itemKey = configuration['PIP_ActionSignalMode'], callSelectionUpdateFunction = False)
        #VOL
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_VOL"].GUIOs["VOLUMETYPESELECTIONBOX"].setSelected(itemKey = configuration['VOL_VolumeType'], callSelectionUpdateFunction = False)
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_VOL"].GUIOs["MATYPESELECTIONBOX"].setSelected(itemKey     = configuration['VOL_MAType'],     callSelectionUpdateFunction = False)
        for lineIndex in range (5):
            lineNumber = lineIndex+1
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_VOL"].GUIOs["VOL_{:d}_LINE".format(lineNumber)].setStatus(status = configuration['VOL_{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_VOL"].GUIOs["VOL_{:d}_NSAMPLES".format(lineNumber)].updateText(text = str(configuration['VOL_{:d}_NSamples'.format(lineNumber)]))
        #MMACDSHORT
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDSHORT"].GUIOs["MMACDSIGNALINTERVALTEXTINPUTBOX"].updateText(text = "{:d}".format(configuration['MMACDSHORT_SignalNSamples']))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDSHORT"].GUIOs["MULTIPLIERTEXTINPUTBOX"].updateText(text = "{:d}".format(configuration['MMACDSHORT_Multiplier']))
        for lineIndex in range (6):
            lineNumber = lineIndex+1
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDSHORT"].GUIOs["MA{:d}_LINE".format(lineNumber)].setStatus(status = configuration['MMACDSHORT_MA{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDSHORT"].GUIOs["MA{:d}_NSAMPLES".format(lineNumber)].updateText(text = "{:d}".format(configuration['MMACDSHORT_MA{:d}_NSamples'.format(lineNumber)]))
        #MMACDLONG
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDLONG"].GUIOs["MMACDSIGNALINTERVALTEXTINPUTBOX"].updateText(text = "{:d}".format(configuration['MMACDLONG_SignalNSamples']))
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDLONG"].GUIOs["MULTIPLIERTEXTINPUTBOX"].updateText(text = "{:d}".format(configuration['MMACDLONG_Multiplier']))
        for lineIndex in range (6):
            lineNumber = lineIndex+1
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDLONG"].GUIOs["MA{:d}_LINE".format(lineNumber)].setStatus(status = configuration['MMACDLONG_MA{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDLONG"].GUIOs["MA{:d}_NSAMPLES".format(lineNumber)].updateText(text = "{:d}".format(configuration['MMACDLONG_MA{:d}_NSamples'.format(lineNumber)]))
        #DMIxADX
        for lineIndex in range (5):
            lineNumber = lineIndex+1
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_DMIxADX"].GUIOs["DMIxADX_{:d}_LINE".format(lineNumber)].setStatus(status = configuration['DMIxADX_{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_DMIxADX"].GUIOs["DMIxADX_{:d}_NSAMPLES".format(lineNumber)].updateText(text = str(configuration['DMIxADX_{:d}_NSamples'.format(lineNumber)]))
        #MFI
        for lineIndex in range (5):
            lineNumber = lineIndex+1
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MFI"].GUIOs["MFI_{:d}_LINE".format(lineNumber)].setStatus(status = configuration['MFI_{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MFI"].GUIOs["MFI_{:d}_NSAMPLES".format(lineNumber)].updateText(text = str(configuration['MFI_{:d}_NSamples'.format(lineNumber)]))
        #WOI
        for lineIndex in range (3):
            lineNumber = lineIndex+1
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WOI"].GUIOs["WOI_{:d}_LINE".format(lineNumber)].setStatus(status = configuration['WOI_{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WOI"].GUIOs["WOI_{:d}_NSAMPLES".format(lineNumber)].updateText(text = "{:d}".format(configuration['WOI_{:d}_NSamples'.format(lineNumber)]))
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WOI"].GUIOs["WOI_{:d}_SIGMA".format(lineNumber)].updateText(text    = "{:.1f}".format(configuration['WOI_{:d}_Sigma'.format(lineNumber)]))
        #NES
        for lineIndex in range (3):
            lineNumber = lineIndex+1
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NES"].GUIOs["NES_{:d}_LINE".format(lineNumber)].setStatus(status = configuration['NES_{:d}_LineActive'.format(lineNumber)], callStatusUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NES"].GUIOs["NES_{:d}_NSAMPLES".format(lineNumber)].updateText(text = "{:d}".format(configuration['NES_{:d}_NSamples'.format(lineNumber)]))
            self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NES"].GUIOs["NES_{:d}_SIGMA".format(lineNumber)].updateText(text    = "{:.1f}".format(configuration['NES_{:d}_Sigma'.format(lineNumber)]))
    def __formatAnalysisConfigurationFromGUIOs():
        try:
            configuration = dict()
            #NI
            configuration['NI_MinCompleteAnalysis'] = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["MINCOMPLETEANALYSISTEXTINPUTBOX"].getText())
            configuration['NI_NAnalysisToDisplay']  = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["NANALYSISDISPLAYTEXTINPUTBOX"].getText())
            #SMA
            configuration['SMA_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_SMA"].getStatus()
            for lineIndex in range (10):
                lineNumber = lineIndex+1
                configuration['SMA_{:d}_LineActive'.format(lineNumber)] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SMA"].GUIOs["SMA_{:d}_LINE".format(lineNumber)].getStatus()
                configuration['SMA_{:d}_NSamples'.format(lineNumber)]   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_SMA"].GUIOs["SMA_{:d}_NSAMPLES".format(lineNumber)].getText())
            #EMA
            configuration['EMA_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_EMA"].getStatus()
            for lineIndex in range (10):
                lineNumber = lineIndex+1
                configuration['EMA_{:d}_LineActive'.format(lineNumber)] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_EMA"].GUIOs["EMA_{:d}_LINE".format(lineNumber)].getStatus()
                configuration['EMA_{:d}_NSamples'.format(lineNumber)]   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_EMA"].GUIOs["EMA_{:d}_NSAMPLES".format(lineNumber)].getText())
            #WMA
            configuration['WMA_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_WMA"].getStatus()
            for lineIndex in range (10):
                lineNumber = lineIndex+1
                configuration['WMA_{:d}_LineActive'.format(lineNumber)] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WMA"].GUIOs["WMA_{:d}_LINE".format(lineNumber)].getStatus()
                configuration['WMA_{:d}_NSamples'.format(lineNumber)]   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WMA"].GUIOs["WMA_{:d}_NSAMPLES".format(lineNumber)].getText())
            #PSAR
            configuration['PSAR_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_PSAR"].getStatus()
            for lineIndex in range (5):
                lineNumber = lineIndex+1
                configuration['PSAR_{:d}_LineActive'.format(lineNumber)] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs["PSAR_{:d}_LINE".format(lineNumber)].getStatus()
                configuration['PSAR_{:d}_AF0'.format(lineNumber)]   = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs["PSAR_{:d}_AF0".format(lineNumber)].getText()),   3)
                configuration['PSAR_{:d}_AF+'.format(lineNumber)]   = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs["PSAR_{:d}_AF+".format(lineNumber)].getText()),   3)
                configuration['PSAR_{:d}_AFMax'.format(lineNumber)] = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PSAR"].GUIOs["PSAR_{:d}_AFMAX".format(lineNumber)].getText()), 3)
            #BOL
            configuration['BOL_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_BOL"].getStatus()
            configuration['BOL_MAType'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"].GUIOs["BOLMATYPESELECTIONBOX"].getSelected()
            for lineIndex in range (10):
                lineNumber = lineIndex+1
                configuration['BOL_{:d}_LineActive'.format(lineNumber)] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"].GUIOs["BOL_{:d}_LINE".format(lineNumber)].getStatus()
                configuration['BOL_{:d}_NSamples'.format(lineNumber)]   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"].GUIOs["BOL_{:d}_NSAMPLES".format(lineNumber)].getText())
                configuration['BOL_{:d}_BandWidth'.format(lineNumber)]  = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_BOL"].GUIOs["BOL_{:d}_BANDWIDTH".format(lineNumber)].getText()), 1)
            #IVP
            configuration['IVP_Master']      = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_IVP"].getStatus()
            configuration['IVP_NSamples']    = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["NSAMPLESTEXTINPUTBOX"].getText())
            configuration['IVP_GammaFactor'] = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["GAMMAFACTORSLIDER"].getSliderValue()/100*(0.095)+0.005), 3)
            configuration['IVP_DeltaFactor'] = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_IVP"].GUIOs["DELTAFACTORSLIDER"].getSliderValue()/100*(9.9) +0.1),    1)
            #PIP
            configuration['PIP_Master']                  = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_PIP"].getStatus()
            configuration['PIP_NeuralNetworkCode']       = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NEURALNETWORKCODESELECTIONBOX"].getSelected()
            configuration['PIP_SwingRange']              = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["SWINGRANGESLIDER"].getSliderValue()                        /100*0.0490+0.0010), 3)
            configuration['PIP_NNAAlpha']                = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NNAALPHAVALUESLIDER"].getSliderValue()                     /100*0.95  +0.05),   2)
            configuration['PIP_NNABeta']                 = int(round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NNABETAVALUESLIDER"].getSliderValue()                  /100*18    +2)))
            configuration['PIP_ClassicalAlpha']          = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALALPHAVALUESLIDER"].getSliderValue()               /100*2.9   +0.1),    1)
            configuration['PIP_ClassicalBeta']           = int(round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALBETAVALUESLIDER"].getSliderValue()            /100*18    +2)))
            configuration['PIP_ClassicalNSamples']       = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALNSAMPLESTEXTINPUTBOX"].getText())
            configuration['PIP_ClassicalSigma']          = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALSIGMATEXTINPUTBOX"].getText()), 1)
            configuration['PIP_CSActivationThreshold1']  = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALACTIVATIONTHRESHOLD1VALUESLIDER"].getSliderValue()/100*0.95  +0.00),   2)
            configuration['PIP_CSActivationThreshold2']  = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["CLASSICALACTIVATIONTHRESHOLD2VALUESLIDER"].getSliderValue()/100*0.95  +0.05),   2)
            configuration['PIP_WSActivationThreshold']   = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["WOIACTIVATIONTHRESHOLDVALUESLIDER"].getSliderValue()       /100*0.95  +0.00),   2)
            configuration['PIP_ActionSignalMode']        = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["ACTIONSIGNALMODESELECTIONBOX"].getSelected()
            #VOL
            configuration['VOL_Master']     = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_VOL"].getStatus()
            configuration['VOL_VolumeType'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_VOL"].GUIOs["VOLUMETYPESELECTIONBOX"].getSelected()
            configuration['VOL_MAType']     = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_VOL"].GUIOs["MATYPESELECTIONBOX"].getSelected()
            for lineIndex in range (5):
                lineNumber = lineIndex+1
                configuration['VOL_{:d}_LineActive'.format(lineNumber)] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_VOL"].GUIOs["VOL_{:d}_LINE".format(lineNumber)].getStatus()
                configuration['VOL_{:d}_NSamples'.format(lineNumber)]   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_VOL"].GUIOs["VOL_{:d}_NSAMPLES".format(lineNumber)].getText())
            #MMACDSHORT
            configuration['MMACDSHORT_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_MMACDSHORT"].getStatus()
            configuration['MMACDSHORT_SignalNSamples'] = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDSHORT"].GUIOs["MMACDSIGNALINTERVALTEXTINPUTBOX"].getText())
            configuration['MMACDSHORT_Multiplier']     = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDSHORT"].GUIOs["MULTIPLIERTEXTINPUTBOX"].getText())
            for lineIndex in range (6):
                lineNumber = lineIndex+1
                configuration['MMACDSHORT_MA{:d}_LineActive'.format(lineNumber)] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDSHORT"].GUIOs["MA{:d}_LINE".format(lineNumber)].getStatus()
                configuration['MMACDSHORT_MA{:d}_NSamples'.format(lineNumber)]   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDSHORT"].GUIOs["MA{:d}_NSAMPLES".format(lineNumber)].getText())
            #MMACDLONG
            configuration['MMACDLONG_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_MMACDLONG"].getStatus()
            configuration['MMACDLONG_SignalNSamples'] = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDLONG"].GUIOs["MMACDSIGNALINTERVALTEXTINPUTBOX"].getText())
            configuration['MMACDLONG_Multiplier']     = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDLONG"].GUIOs["MULTIPLIERTEXTINPUTBOX"].getText())
            for lineIndex in range (6):
                lineNumber = lineIndex+1
                configuration['MMACDLONG_MA{:d}_LineActive'.format(lineNumber)] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDLONG"].GUIOs["MA{:d}_LINE".format(lineNumber)].getStatus()
                configuration['MMACDLONG_MA{:d}_NSamples'.format(lineNumber)]   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MMACDLONG"].GUIOs["MA{:d}_NSAMPLES".format(lineNumber)].getText())
            #DMIxADX
            configuration['DMIxADX_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_DMIxADX"].getStatus()
            for lineIndex in range (5):
                lineNumber = lineIndex+1
                configuration['DMIxADX_{:d}_LineActive'.format(lineNumber)] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_DMIxADX"].GUIOs["DMIxADX_{:d}_LINE".format(lineNumber)].getStatus()
                configuration['DMIxADX_{:d}_NSamples'.format(lineNumber)]   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_DMIxADX"].GUIOs["DMIxADX_{:d}_NSAMPLES".format(lineNumber)].getText())
            #MFI
            configuration['MFI_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_MFI"].getStatus()
            for lineIndex in range (5):
                lineNumber = lineIndex+1
                configuration['MFI_{:d}_LineActive'.format(lineNumber)] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MFI"].GUIOs["MFI_{:d}_LINE".format(lineNumber)].getStatus()
                configuration['MFI_{:d}_NSamples'.format(lineNumber)]   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MFI"].GUIOs["MFI_{:d}_NSAMPLES".format(lineNumber)].getText())
            #WOI
            configuration['WOI_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_WOI"].getStatus()
            for lineIndex in range (3):
                lineNumber = lineIndex+1
                configuration['WOI_{:d}_LineActive'.format(lineNumber)] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WOI"].GUIOs["WOI_{:d}_LINE".format(lineNumber)].getStatus()
                configuration['WOI_{:d}_NSamples'.format(lineNumber)]   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WOI"].GUIOs["WOI_{:d}_NSAMPLES".format(lineNumber)].getText())
                configuration['WOI_{:d}_Sigma'.format(lineNumber)]      = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_WOI"].GUIOs["WOI_{:d}_SIGMA".format(lineNumber)].getText()), 1)
            #NES
            configuration['NES_Master'] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_MAIN"].GUIOs["INDICATORMASTERSWITCH_NES"].getStatus()
            for lineIndex in range (3):
                lineNumber = lineIndex+1
                configuration['NES_{:d}_LineActive'.format(lineNumber)] = self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NES"].GUIOs["NES_{:d}_LINE".format(lineNumber)].getStatus()
                configuration['NES_{:d}_NSamples'.format(lineNumber)]   = int(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NES"].GUIOs["NES_{:d}_NSAMPLES".format(lineNumber)].getText())
                configuration['NES_{:d}_Sigma'.format(lineNumber)]      = round(float(self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_NES"].GUIOs["NES_{:d}_SIGMA".format(lineNumber)].getText()), 1)
        except Exception as e: print(e); configuration = None
        return configuration
    def __farr_onAnalysisConfigurationControlRequestResponse(responder, requestID, functionResult):
        requestResult       = functionResult['result']
        tradeManagerMessage = functionResult['message']
        if (requestResult == True): self.GUIOs["MESSAGEDISPLAYTEXT_DISPLAYTEXT"].updateText(text = tradeManagerMessage, textStyle = 'GREEN')
        else:                       self.GUIOs["MESSAGEDISPLAYTEXT_DISPLAYTEXT"].updateText(text = tradeManagerMessage, textStyle = 'RED')
    def __updateNeuralNetworkCodesList():
        _neuralNetworkCodesList = dict()
        for _nnCode in self.ipcA.getPRD(processName = 'NEURALNETWORKMANAGER', prdAddress = 'NEURALNETWORKS'): _neuralNetworkCodesList[_nnCode] = {'text': _nnCode, 'textAnchor': 'W'}
        self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NEURALNETWORKCODESELECTIONBOX"].setSelectionList(selectionList = _neuralNetworkCodesList, keepSelected = True, displayTargets = 'all')
        if (self.puVar['configurationControl_analysisConfiguration_selected'] != None): 
            _configuration = self.puVar['analysisConfigurations'][self.puVar['configurationControl_analysisConfiguration_selected']]
            if (_configuration['PIP_NeuralNetworkCode'] in _neuralNetworkCodesList): self.GUIOs["TRADEMANAGER&CONFIGURATION_CONFIGURATIONSUBPAGE_PIP"].GUIOs["NEURALNETWORKCODESELECTIONBOX"].setSelected(itemKey = _configuration['PIP_NeuralNetworkCode'], callSelectionUpdateFunction = False)
    auxFunctions['SETANALYSISCONFIGURATIONLIST']                        = __setAnalysisConfigurationList
    auxFunctions['SETANALYSISCONFIGURATIONGUIOS']                       = __setAnalysisConfigurationGUIOs
    auxFunctions['FORMATANALYSISCONFIGURATIONFROMGUIOS']                = __formatAnalysisConfigurationFromGUIOs
    auxFunctions['_FARR_ONANALYSISCONFIGURATIONCONTROLREQUESTRESPONSE'] = __farr_onAnalysisConfigurationControlRequestResponse
    auxFunctions['UPDATENEURALNETWORKCODESLIST']                        = __updateNeuralNetworkCodesList

    #<TradeManager&CurrencyAnalysisFilter>
    def __onCurrencyAnalysisFilterUpdate():
        filter_analysisCode = self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_SEARCHTITLETEXTINPUTBOX"].getText()
        analysisCodes_filtered = [analysisCode for analysisCode in self.puVar['currencyAnalysis'] if (filter_analysisCode in analysisCode)]
        if   (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYID"].getStatus()            == True): listForSort = 'id'
        elif (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYZER"].getStatus()      == True):
            listForSort = list()
            for analysisCode in self.puVar['currencyAnalysis']:
                allocatedAnalyzer = self.puVar['currencyAnalysis'][analysisCode]['allocatedAnalyzer']
                if (allocatedAnalyzer == None): listForSort.append((analysisCode, float('inf')))
                else:                           listForSort.append((analysisCode, allocatedAnalyzer))
        elif (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYANALYSISCODE"].getStatus()  == True): listForSort = 'analysisCode'
        elif (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYSYMBOL"].getStatus()        == True): listForSort = [(analysisCode, self.puVar['currencyAnalysis'][analysisCode]['currencySymbol'])                    for analysisCode in analysisCodes_filtered]
        elif (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYCONFIGURATION"].getStatus() == True): listForSort = [(analysisCode, self.puVar['currencyAnalysis'][analysisCode]['currencyAnalysisConfigurationCode']) for analysisCode in analysisCodes_filtered]
        elif (self.GUIOs["TRADEMANAGER&CURRENCYANALYSISFILTER_FILTERSWITCH_SORTBYFIRSTKLINE"].getStatus()    == True): 
            listForSort = list()
            for analysisCode in self.puVar['currencyAnalysis']:
                currenySymbol = self.puVar['currencyAnalysis'][analysisCode]['currencySymbol']
                if (currenySymbol in self.puVar['currencies']): firstOpenTS = self.puVar['currencies'][currenySymbol]['kline_firstOpenTS']
                else:                                           firstOpenTS = None
                if (firstOpenTS == None): listForSort.append((analysisCode, float('inf')))
                else:                     listForSort.append((analysisCode, firstOpenTS))
        if   (listForSort == 'id'):           analysisCodes_sorted = analysisCodes_filtered
        elif (listForSort == 'analysisCode'): analysisCodes_sorted = analysisCodes_filtered; analysisCodes_sorted.sort()
        else:                                 listForSort.sort(key = lambda x: x[1]); analysisCodes_sorted = [sortPair[0] for sortPair in listForSort]
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSIS_SELECTIONBOX"].setDisplayTargets(displayTargets = analysisCodes_sorted)
    auxFunctions['ONCURRENCYANALYSISFILTERUPDATE'] = __onCurrencyAnalysisFilterUpdate

    #<TradeManager&CurrencyAnalysis>
    def __setCurrecnyAnalysisList():
        #Format and update the selectionBox object
        _caSelectionList = dict()
        _nCAs = len(self.puVar['currencyAnalysis'])
        for _caIndex, _caCode in enumerate(self.puVar['currencyAnalysis']):
            _ca = self.puVar['currencyAnalysis'][_caCode]
            _ca_status = _ca['status']
            if   (_ca_status == 'CURRENCYNOTFOUND'):     _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_CURRENCYNOTFOUND');     _ca_status_str_color = 'RED'
            elif (_ca_status == 'CONFIGNOTFOUND'):       _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_CONFIGNOTFOUND');       _ca_status_str_color = 'RED_LIGHT'
            elif (_ca_status == 'WAITINGTRADING'):       _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_WAITINGTRADING');       _ca_status_str_color = 'ORANGE_LIGHT'
            elif (_ca_status == 'WAITINGNNCDATA'):       _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_WAITINGNNCDATA');       _ca_status_str_color = 'BLUE_DARK'
            elif (_ca_status == 'WAITINGSTREAM'):        _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_WAITINGSTREAM');        _ca_status_str_color = 'BLUE_DARK'
            elif (_ca_status == 'WAITINGDATAAVAILABLE'): _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_WAITINGDATAAVAILABLE'); _ca_status_str_color = 'BLUE_LIGHT'
            elif (_ca_status == 'PREP_QUEUED'):          _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_PREP_QUEUED');          _ca_status_str_color = 'BLUE_LIGHT'
            elif (_ca_status == 'PREP_FETCHINGKLINES'):  _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_PREP_FETCHINGKLINES');  _ca_status_str_color = 'BLUE_LIGHT'
            elif (_ca_status == 'PREP_ANALYZINGKLINES'): _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_PREP_ANALYZINGKLINES'); _ca_status_str_color = 'BLUE_LIGHT'
            elif (_ca_status == 'ANALYZINGREALTIME'):    _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_ANALYZINGREALTIME');    _ca_status_str_color = 'GREEN_LIGHT'
            elif (_ca_status == 'ERROR'):                _ca_status_str = self.visualManager.getTextPack('AUTOTRADE:TRADEMANAGER&CURRENCYANALYSISLIST_STATUS_ERROR');                _ca_status_str_color = 'RED_DARK'
            _caSelectionList[_caCode] = [{'text': "{:d} / {:d}".format(_caIndex+1, _nCAs), 'textStyles': [('all', 'DEFAULT'),],            'textAnchor': 'CENTER'},
                                         {'text': _caCode,                                 'textStyles': [('all', 'DEFAULT'),],            'textAnchor': 'CENTER'},
                                         {'text': _ca['currencySymbol'],                   'textStyles': [('all', 'DEFAULT'),],            'textAnchor': 'CENTER'},
                                         {'text': _ca_status_str,                          'textStyles': [('all', _ca_status_str_color),], 'textAnchor': 'CENTER'}]
        self.GUIOs["TRADEMANAGER&CURRENCYANALYSIS_SELECTIONBOX"].setSelectionList(selectionList = _caSelectionList, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)
        self.pageAuxillaryFunctions['ONCURRENCYANALYSISFILTERUPDATE']()
    auxFunctions['SETCURRENCYANALYSISLIST'] = __setCurrecnyAnalysisList

    #<TradeManager&CurrencyAnalysisInformation>
    def __updateCurrencyAnalysisInfo():
        selectedCurrencyAnalysis_analysisCode = self.puVar['currencyAnalysis_selected']
        if (selectedCurrencyAnalysis_analysisCode == None):
            self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_CONFIGURATIONCODEDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_ALLOCATEDANALYZERDISPLAYTEXT"].updateText(text = "-")
        else:
            selectedCurrencyAnalysis_info = self.puVar['currencyAnalysis'][selectedCurrencyAnalysis_analysisCode]
            selectedCurrencyAnalysis_configurationCode = selectedCurrencyAnalysis_info['currencyAnalysisConfigurationCode']
            selectedCurrencyAnalysis_allocatedAnalyzer = selectedCurrencyAnalysis_info['allocatedAnalyzer']
            self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_CONFIGURATIONCODEDISPLAYTEXT"].updateText(text = selectedCurrencyAnalysis_configurationCode)
            if (selectedCurrencyAnalysis_allocatedAnalyzer == None): self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_ALLOCATEDANALYZERDISPLAYTEXT"].updateText(text = "-")
            else:                                                    self.GUIOs["TRADEMANAGER&CURRENCYANALYSISINFORMATION_ALLOCATEDANALYZERDISPLAYTEXT"].updateText(text = "ANALYZER {:d}".format(selectedCurrencyAnalysis_allocatedAnalyzer))
    auxFunctions['UPDATECURRENCYANALYSISINFO'] = __updateCurrencyAnalysisInfo

    #<TradeManager&TradeConfigurationControl>
    def __checkIfCanAddTradeConfiguration():
        _tests = {#Base
                  'tcCode': False,
                  #Trade Scenario
                  'ts_fullStopLossImmediate': False,
                  'ts_fullStopLossClose':     False,
                  'ts_weightReduce':          False,
                  'ts_reachAndFall':          False,
                  #RQPM
                  'rqpm_exitOnImpulse':         False,
                  'rqpm_exitOnAligned':         False,
                  'rqpm_exitOnProfitable':      False,
                  'rqpm_fullStopLossImmediate': False,
                  'rqpm_fullStopLossClose':     False}
        _tcMode = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TCMODESELECTIONBOX"].getSelected()
        if   (_tcMode == 'TS'):  
            _tests['rqpm_exitOnImpulse']         = True
            _tests['rqpm_exitOnAligned']         = True
            _tests['rqpm_exitOnProfitable']      = True
            _tests['rqpm_fullStopLossImmediate'] = True
            _tests['rqpm_fullStopLossClose']     = True
        elif (_tcMode == 'RQPM'):
            _tests['ts_fullStopLossImmediate'] = True
            _tests['ts_fullStopLossClose']     = True
            _tests['ts_weightReduce']          = True
            _tests['ts_reachAndFall']          = True
        #Base
        if (True):
            #Trade Configuration Code
            _tcCode_entered = self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONCODETEXTINPUTBOX"].getText()
            if (_tcCode_entered not in self.puVar['tradeConfigurations']): _tests['tcCode'] = True
        #Trade Scenario
        if (_tcMode == 'TS'):
            #Full Stop Loss Immediate
            _FSLIMMED_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_FULLSTOPLOSSIMMEDIATETEXTINPUTBOX"].getText()
            if (_FSLIMMED_str == ""): _tests['ts_fullStopLossImmediate'] = True
            else:
                try:
                    _FSLIMMED = round(float(_FSLIMMED_str), 4)
                    if ((0.0000 <= _FSLIMMED) and (_FSLIMMED <= 1.0000)): _tests['ts_fullStopLossImmediate'] = True
                except: pass
            #Full Stop Loss Close
            _FSLCLOSE_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_FULLSTOPLOSSCLOSETEXTINPUTBOX"].getText()
            if (_FSLCLOSE_str == ""): _tests['ts_fullStopLossClose'] = True
            else:
                try:
                    _FSLCLOSE = round(float(_FSLCLOSE_str), 4)
                    if ((0.0000 <= _FSLCLOSE) and (_FSLCLOSE <= 1.0000)): _tests['ts_fullStopLossClose'] = True
                except: pass
            #Weight Reduce
            _WR_Activation_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_WEIGHTREDUCEACTIVATIONTEXTINPUTBOX"].getText()
            _WR_Amount_str     = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_WEIGHTREDUCEAMOUNTTEXTINPUTBOX"].getText()
            if ((_WR_Activation_str == "") and (_WR_Amount_str == "")): _tests['ts_weightReduce'] = True
            else:
                try:
                    _weightReduce_Activation = round(float(_WR_Activation_str), 4)
                    _weightReduce_Amount     = round(float(_WR_Amount_str),     4)
                    if ((0 <= _weightReduce_Activation) and (0 <= _weightReduce_Amount) and (_weightReduce_Amount <= 1.0000)): _tests['ts_weightReduce'] = True
                except: pass
            #Reach And Fall
            _RAF1_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_REACHANDFALL1TEXTINPUTBOX"].getText()
            _RAF2_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_REACHANDFALL2TEXTINPUTBOX"].getText()
            if ((_RAF1_str == "") and (_RAF2_str == "")): _tests['ts_reachAndFall'] = True
            else:
                try:
                    _RAF1 = round(float(_RAF1_str), 4)
                    _RAF2 = round(float(_RAF2_str), 4)
                    if ((0.0000 <= _RAF1) and (_RAF1 <= 1.0000) and (0.0000 <= _RAF2) and (_RAF2 <= 1.0000)): _tests['ts_reachAndFall'] = True
                except: pass
        #RQPM
        elif (_tcMode == 'RQPM'):
            #Exit on Impulse
            _EOI_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_EXITONIMPULSETEXTINPUTBOX"].getText()
            if (_EOI_str == ""): _tests['rqpm_exitOnImpulse'] = True
            else:
                try:
                    _EOI = round(float(_EOI_str)/100, 4)
                    if ((0.0000 <= _EOI) and (_EOI <= 1.0000)): _tests['rqpm_exitOnImpulse'] = True
                except: pass
            #Exit on Aligned
            _EOA_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_EXITONALIGNEDTEXTINPUTBOX"].getText()
            if (_EOA_str == ""): _tests['rqpm_exitOnAligned'] = True
            else:
                try:
                    _EOA = round(float(_EOA_str)/100, 4)
                    if (0.0000 <= _EOA): _tests['rqpm_exitOnAligned'] = True
                except: pass
            #Exit on Profitable
            _EOP_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_EXITONPROFITABLETEXTINPUTBOX"].getText()
            if (_EOP_str == ""): _tests['rqpm_exitOnProfitable'] = True
            else:
                try:
                    _EOP = round(float(_EOP_str)/100, 4)
                    if (0.0000 <= _EOP): _tests['rqpm_exitOnProfitable'] = True
                except: pass
            #Full Stop Loss Immediate
            _FSLIMMED_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FULLSTOPLOSSIMMEDIATETEXTINPUTBOX"].getText()
            if (_FSLIMMED_str == ""): _tests['rqpm_fullStopLossImmediate'] = True
            else:
                try:
                    _FSLIMMED = round(float(_FSLIMMED_str)/100, 4)
                    if ((0.0000 <= _FSLIMMED) and (_FSLIMMED <= 1.0000)): _tests['rqpm_fullStopLossImmediate'] = True
                except: pass
            #Full Stop Loss Close
            _FSLCLOSE_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FULLSTOPLOSSCLOSETEXTINPUTBOX"].getText()
            if (_FSLCLOSE_str == ""): _tests['rqpm_fullStopLossClose'] = True
            else:
                try:
                    _FSLCLOSE = round(float(_FSLCLOSE_str)/100, 4)
                    if ((0.0000 <= _FSLCLOSE) and (_FSLCLOSE <= 1.0000)): _tests['rqpm_fullStopLossClose'] = True
                except: pass
        #Finally
        _allTestsPassed = True
        for _ in _tests:
            if (_tests[_] == False): _allTestsPassed = False; break
        if (_allTestsPassed == True): self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONADD"].activate()
        else:                         self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_CONFIGURATIONADD"].deactivate()
    def __checkIfCanAddTradeScenario():
        try:
            _currentTSType = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOTYPESELECTIONBOX"].getSelected()
            if   (_currentTSType == 'ENTRY'): _target = 'tradeConfiguration_current_TS_TS_Entry'
            elif (_currentTSType == 'EXIT'):  _target = 'tradeConfiguration_current_TS_TS_Exit'
            elif (_currentTSType == 'PSL'):   _target = 'tradeConfiguration_current_TS_TS_PSL'
            #[1]: PD
            pd = round(float(self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_PDTEXTINPUTBOX"].getText())/100, 3)
            testPassed_pd = ((0 <= pd) and (pd <= 1))
            #[2]: QD
            qd = round(float(self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_QDTEXTINPUTBOX"].getText())/100, 3)
            testPassed_qd = ((0 <= qd) and (qd <= 1))
            #Finally
            if ((testPassed_pd == True) and (testPassed_qd == True)): 
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOADDBUTTON"].activate()
                #Additional Edit Button Test
                try:    _scenarioIndex = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOSELECTIONBOX"].getSelected()[0]
                except: _scenarioIndex = None
                _activateEditButton = False
                if (_scenarioIndex != None):
                    _currentScenario = self.puVar[_target][_scenarioIndex]
                    if ((pd != _currentScenario[0]) or (qd != _currentScenario[1])): _activateEditButton = True
                if (_activateEditButton == True): self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOEDITBUTTON"].activate()
                else:                             self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOEDITBUTTON"].deactivate()
            else:                                                                                            
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOADDBUTTON"].deactivate()
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOEDITBUTTON"].deactivate()
        except: 
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOADDBUTTON"].deactivate()
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOEDITBUTTON"].deactivate()
    def __checkIfCanSetRQPMFunctionParameter():
        #Conditions
        _functionType = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FUNCTIONTYPESELECTIONBOX"].getSelected()
        _functionSide = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FUNCTIONSIDESELECTIONBOX"].getSelected()
        try:    _parameterIndex = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSELECTIONBOX"].getSelected()[0]
        except: _parameterIndex = None
        _functionDescriptor = atmEta_RQPMFunctions.RQPMFUNCTIONS_DESCRIPTORS[_functionType]
        _paramDescriptor    = _functionDescriptor[_parameterIndex]
        #Test
        try:    _paramValue = _paramDescriptor['str_to_val'](x = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETTEXTINPUTBOX"].getText())
        except: _paramValue = None
        if ((_paramValue != None) and (_paramDescriptor['isAcceptable'](x = _paramValue) == True) and (_paramValue != self.puVar['tradeConfiguration_current_RQPM_Parameters_{:s}'.format(_functionSide)][_parameterIndex])): self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETBUTTON"].activate()
        else:                                                                                                                                                                                                                 self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETBUTTON"].deactivate()
    def __setTradeConfigurationList():
        tradeConfigurations_selectionList = dict()
        for tradeConfigurationCode in self.puVar['tradeConfigurations']: tradeConfigurations_selectionList[tradeConfigurationCode] = {'text': tradeConfigurationCode, 'textAnchor': 'W'}
        self.GUIOs["TRADEMANAGER&TRADECONFIGURATIONCONTROL_SELECTIONBOX"].setSelectionList(selectionList = tradeConfigurations_selectionList, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)
    def __setTradeConfigurationGUIOs(tradeConfiguration):
        #Base
        if (True):
            #---Leverage
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["LEVERAGESLIDER"].setSliderValue(newValue = (tradeConfiguration['leverage']-1)*(100/(20-1)))
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["LEVERAGEDISPLAYTEXT"].updateText(text = "X {:d}".format(tradeConfiguration['leverage']))
            #---Margin Type
            if (tradeConfiguration['isolated'] == False): _marginType = 'CROSSED'
            else:                                         _marginType = 'ISOLATED'
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["MARGINTYPESELECTIONBOX"].setSelected(itemKey = _marginType, callSelectionUpdateFunction = False)
            #---Trade Control Mode
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TCMODESELECTIONBOX"].setSelected(itemKey = tradeConfiguration['tcMode'], callSelectionUpdateFunction = False)
            #---TCMode-Dependent GUIOs
            for _groupName in self.puVar['tradeConfiguration_guioGroups']:
                if (_groupName == tradeConfiguration['tcMode']):
                    for _guioName in self.puVar['tradeConfiguration_guioGroups'][_groupName]: self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs[_guioName].show()
                else:
                    for _guioName in self.puVar['tradeConfiguration_guioGroups'][_groupName]: self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs[_guioName].hide()
            #---Direction
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["DIRECTIONSELECTIONBOX"].setSelected(itemKey = tradeConfiguration['direction'], callSelectionUpdateFunction = False)
        #Trade Scenario
        if (True):
            if (tradeConfiguration['ts_fullStopLossImmediate'] == None): self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_FULLSTOPLOSSIMMEDIATETEXTINPUTBOX"].updateText(text = "")
            else:                                                        self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_FULLSTOPLOSSIMMEDIATETEXTINPUTBOX"].updateText(text = "{:.2f}".format(tradeConfiguration['ts_fullStopLossImmediate']*100))
            if (tradeConfiguration['ts_fullStopLossClose'] == None): self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_FULLSTOPLOSSCLOSETEXTINPUTBOX"].updateText(text = "")
            else:                                                    self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_FULLSTOPLOSSCLOSETEXTINPUTBOX"].updateText(text = "{:.2f}".format(tradeConfiguration['ts_fullStopLossClose']*100))
            if (tradeConfiguration['ts_weightReduce'] == None): 
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_WEIGHTREDUCEACTIVATIONTEXTINPUTBOX"].updateText(text = "")
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_WEIGHTREDUCEAMOUNTTEXTINPUTBOX"].updateText(text     = "")
            else:                                            
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_WEIGHTREDUCEACTIVATIONTEXTINPUTBOX"].updateText(text = "{:.2f}".format(tradeConfiguration['ts_weightReduce'][0]*100))
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_WEIGHTREDUCEAMOUNTTEXTINPUTBOX"].updateText(text     = "{:.2f}".format(tradeConfiguration['ts_weightReduce'][1]*100))
            if (tradeConfiguration['ts_reachAndFall'] == None): 
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_REACHANDFALL1TEXTINPUTBOX"].updateText(text = "")
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_REACHANDFALL2TEXTINPUTBOX"].updateText(text = "")
            else:                                            
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_REACHANDFALL1TEXTINPUTBOX"].updateText(text = "{:.2f}".format(tradeConfiguration['ts_reachAndFall'][0]*100))
                self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_REACHANDFALL2TEXTINPUTBOX"].updateText(text = "{:.2f}".format(tradeConfiguration['ts_reachAndFall'][1]*100))
            _currentTSType = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOTYPESELECTIONBOX"].getSelected()
            self.puVar['tradeConfiguration_current_TS_TS_Entry'] = tradeConfiguration['ts_ts_entry'].copy()
            self.puVar['tradeConfiguration_current_TS_TS_Exit']  = tradeConfiguration['ts_ts_exit'].copy()
            self.puVar['tradeConfiguration_current_TS_TS_PSL']   = tradeConfiguration['ts_ts_psl'].copy()
            if   (_currentTSType == 'ENTRY'): _target = self.puVar['tradeConfiguration_current_TS_TS_Entry']
            elif (_currentTSType == 'EXIT'):  _target = self.puVar['tradeConfiguration_current_TS_TS_Exit']
            elif (_currentTSType == 'PSL'):   _target = self.puVar['tradeConfiguration_current_TS_TS_PSL']
            nTradeScenarios = len(_target)
            tradeScenarios_selectionList = dict()
            for _tradeScenarioIndex, _tradeScenario in enumerate(_target):
                #[0]: Index
                _index_str = "{:d} / {:d}".format(_tradeScenarioIndex+1, nTradeScenarios)
                #[1]: PD
                _pd_str = "{:.1f} %".format(_tradeScenario[0]*100)
                #[2]: QD
                _qd_str = "{:.1f} %".format(_tradeScenario[1]*100)
                #Finally
                tradeScenarios_selectionList[_tradeScenarioIndex] = [{'text': _index_str},
                                                                     {'text': _pd_str},
                                                                     {'text': _qd_str}]
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOSELECTIONBOX"].setSelectionList(selectionList = tradeScenarios_selectionList, keepSelected = False, displayTargets = 'all', callSelectionUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOSELECTIONBOX"].clearSelected()
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_PDTEXTINPUTBOX"].updateText(text = "")
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_QDTEXTINPUTBOX"].updateText(text = "")
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOADDBUTTON"].deactivate()
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOEDITBUTTON"].deactivate()
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_TRADESCENARIOREMOVEBUTTON"].deactivate()
        #RQPM
        if (True):
            if (tradeConfiguration['rqpm_exitOnImpulse'] == None):         self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_EXITONIMPULSETEXTINPUTBOX"].updateText(text         = "")
            else:                                                          self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_EXITONIMPULSETEXTINPUTBOX"].updateText(text         = f"{tradeConfiguration['rqpm_exitOnImpulse']*100:.2f}")
            if (tradeConfiguration['rqpm_exitOnAligned'] == None):         self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_EXITONALIGNEDTEXTINPUTBOX"].updateText(text         = "")
            else:                                                          self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_EXITONALIGNEDTEXTINPUTBOX"].updateText(text         = f"{tradeConfiguration['rqpm_exitOnAligned']*100:.2f}")
            if (tradeConfiguration['rqpm_exitOnProfitable'] == None):      self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_EXITONPROFITABLETEXTINPUTBOX"].updateText(text      = "")
            else:                                                          self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_EXITONPROFITABLETEXTINPUTBOX"].updateText(text      = f"{tradeConfiguration['rqpm_exitOnProfitable']*100:.2f}")
            if (tradeConfiguration['rqpm_fullStopLossImmediate'] == None): self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FULLSTOPLOSSIMMEDIATETEXTINPUTBOX"].updateText(text = "")
            else:                                                          self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FULLSTOPLOSSIMMEDIATETEXTINPUTBOX"].updateText(text = f"{tradeConfiguration['rqpm_fullStopLossImmediate']*100:.2f}")
            if (tradeConfiguration['rqpm_fullStopLossClose'] == None):     self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FULLSTOPLOSSCLOSETEXTINPUTBOX"].updateText(text     = "")
            else:                                                          self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FULLSTOPLOSSCLOSETEXTINPUTBOX"].updateText(text     = f"{tradeConfiguration['rqpm_fullStopLossClose']*100:.2f}")
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FUNCTIONTYPESELECTIONBOX"].setSelected(itemKey = tradeConfiguration['rqpm_functionType'], callSelectionUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FUNCTIONSIDESELECTIONBOX"].setSelected(itemKey = 'LONG',                                  callSelectionUpdateFunction = False)
            self.puVar['tradeConfiguration_current_RQPM_Parameters_LONG']  = tradeConfiguration['rqpm_functionParams_LONG'].copy()
            self.puVar['tradeConfiguration_current_RQPM_Parameters_SHORT'] = tradeConfiguration['rqpm_functionParams_SHORT'].copy()
            _functionParameters_selectionBox = dict()
            if (tradeConfiguration['rqpm_functionType'] is not None):
                _functionDescriptor = atmEta_RQPMFunctions.RQPMFUNCTIONS_DESCRIPTORS[tradeConfiguration['rqpm_functionType']]
                for _paramIndex, _paramDescriptor in enumerate(_functionDescriptor):
                    #[0]: Index
                    _index_str = "{:d} / {:d}".format(_paramIndex+1, len(_functionDescriptor))
                    #[1]: Param Name
                    _name_str = "{:s}".format(_paramDescriptor['name'])
                    #[2]: Value
                    _value_str = _paramDescriptor['val_to_str'](x = self.puVar['tradeConfiguration_current_RQPM_Parameters_LONG'][_paramIndex])
                    #Finally
                    _functionParameters_selectionBox[_paramIndex] = [{'text': _index_str},
                                                                     {'text': _name_str},
                                                                     {'text': _value_str}]
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSELECTIONBOX"].setSelectionList(selectionList = _functionParameters_selectionBox, keepSelected = False, displayTargets = 'all', callSelectionUpdateFunction = False)
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERNAMEDISPLAYTEXT"].updateText(text = "-")
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETTEXTINPUTBOX"].updateText(text = "")
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETTEXTINPUTBOX"].deactivate()
            self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_PARAMETERSETBUTTON"].deactivate()
    def __formatTradeConfigurationFromGUIOs():
        try:
            #Base
            if (True):
                _leverage   = round(self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["LEVERAGESLIDER"].getSliderValue()/100*(20-1)+1)
                _marginType = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["MARGINTYPESELECTIONBOX"].getSelected()
                if   (_marginType == 'CROSSED'):  _isolated = False
                elif (_marginType == 'ISOLATED'): _isolated = True
                _direction = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["DIRECTIONSELECTIONBOX"].getSelected()
                _tcMode    = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TCMODESELECTIONBOX"].getSelected()
            #Default TC-Dependent Values
            if (True):
                _TS_FSLIMMED = None
                _TS_FSLCLOSE = None
                _TS_WR       = None
                _TS_RAF      = None
                _TS_TS_Entry = list()
                _TS_TS_Exit  = list()
                _TS_TS_PSL   = list()
                _RQPM_EOI                  = None
                _RQPM_EOA                  = None
                _RQPM_EOP                  = None
                _RQPM_FSLIMMED             = None
                _RQPM_FSLCLOSE             = None
                _RQPM_FunctionType         = None
                _RQPM_FunctionParams_LONG  = list()
                _RQPM_FunctionParams_SHORT = list()
            #Trade Scenario
            if (_tcMode == 'TS'):
                #Full Stop Loss Immediate
                _TS_FSLIMMED_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_FULLSTOPLOSSIMMEDIATETEXTINPUTBOX"].getText()
                if (_TS_FSLIMMED_str == ""): _TS_FSLIMMED = None
                else:                        _TS_FSLIMMED = round(float(_TS_FSLIMMED_str)/100, 4)
                #Full Stop Loss Close
                _TS_FSLCLOSE_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_FULLSTOPLOSSCLOSETEXTINPUTBOX"].getText()
                if (_TS_FSLCLOSE_str == ""): _TS_FSLCLOSE = None
                else:                        _TS_FSLCLOSE = round(float(_TS_FSLCLOSE_str)/100, 4)
                #Weight Reduce
                _TS_WR_Activation_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_WEIGHTREDUCEACTIVATIONTEXTINPUTBOX"].getText()
                _TS_WR_Amount_str     = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_WEIGHTREDUCEAMOUNTTEXTINPUTBOX"].getText()
                if ((_TS_WR_Activation_str == "") and (_TS_WR_Amount_str == "")): _TS_WR = None
                else:
                    _TS_WR_Activation = round(float(_TS_WR_Activation_str)/100, 4)
                    _TS_WR_Amount     = round(float(_TS_WR_Amount_str)    /100, 4)
                    _TS_WR = (_TS_WR_Activation, _TS_WR_Amount)
                #Reach And Fall
                _TS_RAF1_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_REACHANDFALL1TEXTINPUTBOX"].getText()
                _TS_RAF2_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["TS_REACHANDFALL2TEXTINPUTBOX"].getText()
                if ((_TS_RAF1_str == "") and (_TS_RAF2_str == "")): _TS_RAF = None
                else:                         
                    _TS_RAF1 = round(float(_TS_RAF1_str)/100, 4)
                    _TS_RAF2 = round(float(_TS_RAF2_str)/100, 4)
                    _TS_RAF = (_TS_RAF1, _TS_RAF2)
                #Trade Scenarios
                _TS_TS_Entry = self.puVar['tradeConfiguration_current_TS_TS_Entry'].copy()
                _TS_TS_Exit  = self.puVar['tradeConfiguration_current_TS_TS_Exit'].copy()
                _TS_TS_PSL   = self.puVar['tradeConfiguration_current_TS_TS_PSL'].copy()
            #RQPM
            if (_tcMode == 'RQPM'):
                #Exit On Impulse
                _RQPM_EOI_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_EXITONIMPULSETEXTINPUTBOX"].getText()
                if (_RQPM_EOI_str == ""): _RQPM_EOI = None
                else:                     _RQPM_EOI = round(float(_RQPM_EOI_str)/100, 4)
                #Exit On Aligned
                _RQPM_EOA_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_EXITONALIGNEDTEXTINPUTBOX"].getText()
                if (_RQPM_EOA_str == ""): _RQPM_EOA = None
                else:                     _RQPM_EOA = round(float(_RQPM_EOA_str)/100, 4)
                #Exit On Profitable
                _RQPM_EOP_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_EXITONPROFITABLETEXTINPUTBOX"].getText()
                if (_RQPM_EOP_str == ""): _RQPM_EOP = None
                else:                     _RQPM_EOP = round(float(_RQPM_EOP_str)/100, 4)
                #Full Stop Loss Immediate
                _RQPM_FSLIMMED_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FULLSTOPLOSSIMMEDIATETEXTINPUTBOX"].getText()
                if (_RQPM_FSLIMMED_str == ""): _RQPM_FSLIMMED = None
                else:                          _RQPM_FSLIMMED = round(float(_RQPM_FSLIMMED_str)/100, 4)
                #Full Stop Loss Close
                _RQPM_FSLCLOSE_str = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FULLSTOPLOSSCLOSETEXTINPUTBOX"].getText()
                if (_RQPM_FSLCLOSE_str == ""): _RQPM_FSLCLOSE = None
                else:                          _RQPM_FSLCLOSE = round(float(_RQPM_FSLCLOSE_str)/100, 4)
                #Function Type
                _RQPM_FunctionType = self.GUIOs["TRADEMANAGER&TRADECONFIGURATION_CONFIGURATIONSUBPAGE"].GUIOs["RQPM_FUNCTIONTYPESELECTIONBOX"].getSelected()
                #Function Params
                _RQPM_FunctionParams_LONG  = self.puVar['tradeConfiguration_current_RQPM_Parameters_LONG'].copy()
                _RQPM_FunctionParams_SHORT = self.puVar['tradeConfiguration_current_RQPM_Parameters_SHORT'].copy()
            #Finally
            tradeConfiguration = {'leverage':  _leverage,
                                  'isolated':  _isolated,
                                  'direction': _direction,
                                  'tcMode':    _tcMode,
                                  #TS Only
                                  'ts_fullStopLossImmediate': _TS_FSLIMMED,
                                  'ts_fullStopLossClose':     _TS_FSLCLOSE,
                                  'ts_weightReduce':          _TS_WR,
                                  'ts_reachAndFall':          _TS_RAF,
                                  'ts_ts_entry':              _TS_TS_Entry,
                                  'ts_ts_exit':               _TS_TS_Exit,
                                  'ts_ts_psl':                _TS_TS_PSL,
                                  #RQPM Only
                                  'rqpm_exitOnImpulse':         _RQPM_EOI,
                                  'rqpm_exitOnAligned':         _RQPM_EOA,
                                  'rqpm_exitOnProfitable':      _RQPM_EOP,
                                  'rqpm_fullStopLossImmediate': _RQPM_FSLIMMED,
                                  'rqpm_fullStopLossClose':     _RQPM_FSLCLOSE,
                                  'rqpm_functionType':          _RQPM_FunctionType,
                                  'rqpm_functionParams_LONG':   _RQPM_FunctionParams_LONG,
                                  'rqpm_functionParams_SHORT':  _RQPM_FunctionParams_SHORT}
        except Exception as e: print(e); tradeConfiguration = None
        return tradeConfiguration
    def __farr_onTradeConfigurationControlRequestResponse(responder, requestID, functionResult):
        requestResult       = functionResult['result']
        tradeManagerMessage = functionResult['message']
        if (requestResult == True): self.GUIOs["MESSAGEDISPLAYTEXT_DISPLAYTEXT"].updateText(text = tradeManagerMessage, textStyle = 'GREEN')
        else:                       self.GUIOs["MESSAGEDISPLAYTEXT_DISPLAYTEXT"].updateText(text = tradeManagerMessage, textStyle = 'RED')
    auxFunctions['CHECKIFCANADDTRADECONFIGURATION']    = __checkIfCanAddTradeConfiguration
    auxFunctions['CHECKIFCANADDTRADESCENARIO']         = __checkIfCanAddTradeScenario
    auxFunctions['CHECKIFCANSETRQPMFUNCTIONPARAMETER'] = __checkIfCanSetRQPMFunctionParameter
    auxFunctions['SETTRADECONFIGURATIONLIST']          = __setTradeConfigurationList
    auxFunctions['SETTRADECONFIGURATIONGUIOS']         = __setTradeConfigurationGUIOs
    auxFunctions['FORMATTRADECONFIGURATIONFROMGUIOS']  = __formatTradeConfigurationFromGUIOs
    auxFunctions['_FARR_ONTRADECONFIGURATIONCONTROLREQUESTRESPONSE'] = __farr_onTradeConfigurationControlRequestResponse

    #Return the generated functions
    return auxFunctions
#AUXILALRY FUNCTIONS END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------