#ATM Modules
import ipc
import constants
import auxiliaries
from GUI.generals import passiveGraphics_wrapperTypeC,\
                         textBox_typeA,\
                         button_typeA,\
                         button_typeB,\
                         switch_typeB,\
                         switch_typeC,\
                         textInputBox_typeA,\
                         selectionBox_typeC

#Python Modules
import pyglet
import time
import math
from datetime import datetime, timezone

#Constants
_IPC_THREADTYPE_MT = ipc._THREADTYPE_MT
_IPC_THREADTYPE_AT = ipc._THREADTYPE_AT

_CLOCK_UPDATE_INTERVAL_NS = 100e6

#Local Formatter Functions
def statusToString(vm, status):
    vm_getTP = vm.getTextPack
    if status is None:
        status_str   = "-"
        status_color = 'BLUE_DARK'
    elif status == 'TRADING':
        status_str   = vm_getTP('MARKET:CURRENCYLIST_STATUS_TRADING')
        status_color = 'GREEN_LIGHT'
    elif status == 'SETTLING':
        status_str   = vm_getTP('MARKET:CURRENCYLIST_STATUS_SETTLING')
        status_color = 'RED_LIGHT'
    elif status == 'REMOVED':
        status_str   = vm_getTP('MARKET:CURRENCYLIST_STATUS_REMOVED')
        status_color = 'RED_DARK'
    else:
        status_str   = status
        status_color = 'ORANGE_LIGHT'
    status_ts = [('all', status_color),]
    return status_str, status_ts

def collectingToString(collecting):
    collectingStream, collectingHistorical = collecting
    if collectingStream:
        if collectingHistorical:
            collecting_str   = 'ALL'
            collecting_color = 'GREEN_LIGHT'
        else:
            collecting_str   = 'STREAM'
            collecting_color = 'BLUE_LIGHT'
    else:
        collecting_str   = 'NONE'
        collecting_color = 'GREY'
    collecting_ts = [('all', collecting_color),]
    return collecting_str, collecting_ts

def firstIntervalToString(firstInterval):
    if firstInterval is None: return "-"
    else:                     return datetime.fromtimestamp(firstInterval, tz=timezone.utc).strftime("%Y/%m/%d %H:%M")

def aRangesToString(availableRanges):
    dt_fts = datetime.fromtimestamp
    tzUTC  = timezone.utc
    if availableRanges is None: 
        return "-"
    else:
        aRanges_str = []
        for aRange in availableRanges:
            begStr = dt_fts(aRange[0], tz=tzUTC).strftime('%Y/%m/%d %H:%M')
            endStr = dt_fts(aRange[1], tz=tzUTC).strftime('%Y/%m/%d %H:%M')
            aRanges_str.append(f"[{begStr} ~ {endStr}]")
        if len(aRanges_str) == 1: return aRanges_str[0]
        else:                     return ", ".join(aRanges_str)

def availabilityToString(availability, precision = 3):
    if availability is None:
        text       = "N/A"
        textStyles = [('all', 'DEFAULT'),]
    else:
        avail_total, dummyRate = availability
        scaler = pow(10, precision+2)
        avail_total = round(math.floor(avail_total*scaler)/scaler, precision+2)
        if dummyRate is not None:
            dummyRate = max(dummyRate, pow(10, -(precision+2)))
            dummyRate = round(math.floor(dummyRate*scaler)/scaler, precision+2)
        if   avail_total == 0.000: color = 'GREY'
        elif avail_total <= 0.333: color = 'ORANGE_LIGHT'
        elif avail_total <= 0.666: color = 'BLUE_LIGHT'
        elif avail_total <  1.000: color = 'GREEN_LIGHT'
        elif avail_total == 1.000: color = 'GREEN'
        else:                      color = 'RED'
        if avail_total == 1.000: text = "100 %"
        else:                    text = f"{avail_total*100:.{precision}f} %"
        textStyles = [((0, len(text)-1), color)]
        if dummyRate is None: tBlock = " / -"
        else:                 tBlock = f" / {dummyRate*100:.{precision}f} %"
        text += tBlock
        textStyles.append(((textStyles[-1][0][1]+1, textStyles[-1][0][1]+len(tBlock)-1), 'DEFAULT'))
    return text, textStyles

#SETUP PAGE <MAIN> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def setupPage(self):
    #Set page unique variables
    self.puVar['fetchStatus']                            = dict()
    self.puVar['currencies']                             = dict()
    self.puVar['currencies_availabilities']              = dict()
    self.puVar['currencies_availabilities_lastComputed'] = 0
    self.puVar['currencies_selected']                    = set()
    self.puVar['currencies_lastSortBy']                  = None
    self.puVar['dbStatusRequests']                       = dict()
    self.puVar['clock_lastUpdated_ns']                   = 0

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
        self.GUIOs["TITLETEXT_DATABASE"] = textBox_typeA(**inst, groupOrder=1, xPos= 6000, yPos=8550, width=4000, height=400, style=None, text=self.visualManager.getTextPack('DATABASE:TITLE'), fontSize = 220, textInteractable = False)
        self.GUIOs["BUTTON_MOVETO_DASHBOARD"] = button_typeB(**inst,  groupOrder=2, xPos=  50, yPos=8650, width= 300, height=300, style="styleB", releaseFunction=self.pageObjectFunctions['PAGEMOVE_DASHBOARD'], image = 'dashboardIcon_512x512.png', imageSize = (225, 225), imageRGBA = self.visualManager.getFromColorTable('ICON_COLORING'))
        


        #<Local Network Import>
        self.GUIOs["BLOCKSUBTITLE_LOCALNETWORKIMPORT"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=8350, width=4700, height=200, style="styleA", text=self.visualManager.getTextPack('DATABASE:BLOCKTITLE_LOCALNETWORKIMPORT'), fontSize = 80)
        self.GUIOs["LOCALNETWORKIMPORT_IPADDRESSTITLETEXT"]     = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=8000, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:LOCALNETWORKIMPORT_IPADDRESS'),  fontSize=80, textInteractable=False)
        self.GUIOs["LOCALNETWORKIMPORT_IPADDRESSTEXTINPUTBOX"]  = textInputBox_typeA(**inst, groupOrder=1, xPos=1200, yPos=8000, width=1200, height=250, style="styleA", text="",                                                                       fontSize=80, textUpdateFunction=None)
        self.GUIOs["LOCALNETWORKIMPORT_PORTNUMBERTITLETEXT"]    = textBox_typeA(**inst,      groupOrder=1, xPos=2500, yPos=8000, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:LOCALNETWORKIMPORT_PORTNUMBER'), fontSize=80, textInteractable=False)
        self.GUIOs["LOCALNETWORKIMPORT_PORTNUMBERTEXTINPUTBOX"] = textInputBox_typeA(**inst, groupOrder=1, xPos=3600, yPos=8000, width=1200, height=250, style="styleA", text="",                                                                       fontSize=80, textUpdateFunction=None)
        self.GUIOs["LOCALNETWORKIMPORT_DBNAMETITLETEXT"]        = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=7650, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:LOCALNETWORKIMPORT_DBNAME'),     fontSize=80, textInteractable=False)
        self.GUIOs["LOCALNETWORKIMPORT_DBNAMETEXTINPUTBOX"]     = textInputBox_typeA(**inst, groupOrder=1, xPos=1200, yPos=7650, width=1200, height=250, style="styleA", text="",                                                                       fontSize=80, textUpdateFunction=None)
        self.GUIOs["LOCALNETWORKIMPORT_USERTITLETEXT"]          = textBox_typeA(**inst,      groupOrder=1, xPos=2500, yPos=7650, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:LOCALNETWORKIMPORT_USER'),       fontSize=80, textInteractable=False)
        self.GUIOs["LOCALNETWORKIMPORT_USERTEXTINPUTBOX"]       = textInputBox_typeA(**inst, groupOrder=1, xPos=3600, yPos=7650, width=1200, height=250, style="styleA", text="",                                                                       fontSize=80, textUpdateFunction=None)
        self.GUIOs["LOCALNETWORKIMPORT_PASSWORDTITLETEXT"]      = textBox_typeA(**inst,      groupOrder=1, xPos= 100, yPos=7300, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:LOCALNETWORKIMPORT_PASSWORD'),   fontSize=80, textInteractable=False)
        self.GUIOs["LOCALNETWORKIMPORT_PASSWORDTEXTINPUTBOX"]   = textInputBox_typeA(**inst, groupOrder=1, xPos=1200, yPos=7300, width=1200, height=250, style="styleA", text="",                                                                       fontSize=80, textUpdateFunction=None)
        self.GUIOs["LOCALNETWORKIMPORT_IMPORTBUTTON"]           = button_typeA(**inst,       groupOrder=1, xPos=2500, yPos=7300, width=2300, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:LOCALNETWORKIMPORT_IMPORT'),     fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_LOCALNETWORKIMPORT_IMPORTBUTTON'])
        self.GUIOs["LOCALNETWORKIMPORT_IMPORTBUTTON"].deactivate()

        #<Collection Process>
        self.GUIOs["BLOCKSUBTITLE_COLLECTIONPROCESS"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=7025, width=4700, height=200, style="styleA", text=self.visualManager.getTextPack('DATABASE:BLOCKTITLE_COLLECTIONPROCESS'), fontSize = 80)
        self.GUIOs["COLLECTIONPROCESS_LASTFETCHEDTITLETEXT"]                 = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=6675, width=1600, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:COLLECTIONPROCESS_LASTFETCHED'),               fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_LASTFETCHEDDISPLAYTEXT"]               = textBox_typeA(**inst, groupOrder=1, xPos=1800, yPos=6675, width=3000, height=250, style="styleA", text="-",                                                                                    fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_AVGMDFETCHSPEEDKLTITLETEXT"]           = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=6325, width=1600, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:COLLECTIONPROCESS_AVGMDFETCHSPEED_KL'),        fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_AVGMDFETCHSPEEDKLDISPLAYTEXT"]         = textBox_typeA(**inst, groupOrder=1, xPos=1800, yPos=6325, width=3000, height=250, style="styleA", text="-",                                                                                    fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_AVGMDFETCHSPEEDDEPTHTITLETEXT"]        = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=5975, width=1600, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:COLLECTIONPROCESS_AVGMDFETCHSPEED_DEPTH'),     fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_AVGMDFETCHSPEEDDEPTHDISPLAYTEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos=1800, yPos=5975, width=3000, height=250, style="styleA", text="-",                                                                                    fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_AVGMDFETCHSPEEDATTITLETEXT"]           = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=5625, width=1600, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:COLLECTIONPROCESS_AVGMDFETCHSPEED_AT'),        fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_AVGMDFETCHSPEEDATDISPLAYTEXT"]         = textBox_typeA(**inst, groupOrder=1, xPos=1800, yPos=5625, width=3000, height=250, style="styleA", text="-",                                                                                    fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_AVGMDFETCHSPEEDTOTALTITLETEXT"]        = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=5275, width=1600, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:COLLECTIONPROCESS_AVGMDFETCHSPEED_TOTAL'),     fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_AVGMDFETCHSPEEDTOTALDISPLAYTEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos=1800, yPos=5275, width=3000, height=250, style="styleA", text="-",                                                                                    fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_REMAININGRANGESKLTITLETEXT"]           = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=4925, width=1600, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:COLLECTIONPROCESS_REMAININGRANGES_KL'),        fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_REMAININGRANGESKLDISPLAYTEXT"]         = textBox_typeA(**inst, groupOrder=1, xPos=1800, yPos=4925, width=3000, height=250, style="styleA", text="-",                                                                                    fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_REMAININGRANGESDEPTHTITLETEXT"]        = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=4575, width=1600, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:COLLECTIONPROCESS_REMAININGRANGES_DEPTH'),     fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_REMAININGRANGESDEPTHDISPLAYTEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos=1800, yPos=4575, width=3000, height=250, style="styleA", text="-",                                                                                    fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_REMAININGRANGESATTITLETEXT"]           = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=4225, width=1600, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:COLLECTIONPROCESS_REMAININGRANGES_AT'),        fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_REMAININGRANGESATDISPLAYTEXT"]         = textBox_typeA(**inst, groupOrder=1, xPos=1800, yPos=4225, width=3000, height=250, style="styleA", text="-",                                                                                    fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_REMAININGRANGESTOTALTITLETEXT"]        = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=3875, width=1600, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:COLLECTIONPROCESS_REMAININGRANGES_TOTAL'),     fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_REMAININGRANGESTOTALDISPLAYTEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos=1800, yPos=3875, width=3000, height=250, style="styleA", text="-",                                                                                    fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_ESTIMATEDTIMEOFCOMPLETIONTITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=3525, width=1600, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:COLLECTIONPROCESS_ESTIMATEDTIMEOFCOMPLETION'), fontSize=80, textInteractable=True)
        self.GUIOs["COLLECTIONPROCESS_ESTIMATEDTIMEOFCOMPLETIONDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=1800, yPos=3525, width=3000, height=250, style="styleA", text="-",                                                                                    fontSize=80, textInteractable=True)



        #<DB Status>
        self.GUIOs["BLOCKSUBTITLE_DBSTATUS"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=100, yPos=3250, width=4700, height=200, style="styleA", text=self.visualManager.getTextPack('DATABASE:BLOCKTITLE_DBSTATUS'), fontSize = 80)
        self.GUIOs["DBSTATUS_MDBDIRECTORYTITLETEXT"]           = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=2900, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:DBSTATUS_MDBDIRECTORY'),         fontSize=80, textInteractable=True)
        self.GUIOs["DBSTATUS_MDBDIRECTORYDISPLAYTEXT"]         = textBox_typeA(**inst, groupOrder=1, xPos=2200, yPos=2900, width=2600, height=250, style="styleA", text="-",                                                                      fontSize=80, textInteractable=True)
        self.GUIOs["DBSTATUS_MDBDRIVETITLETEXT"]               = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=2550, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:DBSTATUS_MDBDRIVE'),             fontSize=80, textInteractable=True)
        self.GUIOs["DBSTATUS_MDBDRIVEDISPLAYTEXT"]             = textBox_typeA(**inst, groupOrder=1, xPos=2200, yPos=2550, width=2600, height=250, style="styleA", text="-",                                                                      fontSize=80, textInteractable=True)
        self.GUIOs["DBSTATUS_MDBSIZETOTALTITLETEXT"]           = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=2200, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:DBSTATUS_MDBSIZETOTAL'),         fontSize=80, textInteractable=True)
        self.GUIOs["DBSTATUS_MDBSIZETOTALDISPLAYTEXT"]         = textBox_typeA(**inst, groupOrder=1, xPos=2200, yPos=2200, width=2600, height=250, style="styleA", text="-",                                                                      fontSize=80, textInteractable=True)
        self.GUIOs["DBSTATUS_MDBCOMPRESSIONTITLETEXT"]         = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=1850, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:DBSTATUS_MDBCOMPRESSION'),       fontSize=80, textInteractable=True)
        self.GUIOs["DBSTATUS_MDBCOMPRESSIONDISPLAYTEXT"]       = textBox_typeA(**inst, groupOrder=1, xPos=2200, yPos=1850, width=2600, height=250, style="styleA", text="-",                                                                      fontSize=80, textInteractable=True)
        self.GUIOs["DBSTATUS_ODBSIZEACCOUNTTITLETEXT"]         = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=1500, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:DBSTATUS_ODBSIZEACCOUNT'),       fontSize=80, textInteractable=True)
        self.GUIOs["DBSTATUS_ODBSIZEACCOUNTDISPLAYTEXT"]       = textBox_typeA(**inst, groupOrder=1, xPos=2200, yPos=1500, width=2600, height=250, style="styleA", text="-",                                                                      fontSize=80, textInteractable=True)
        self.GUIOs["DBSTATUS_ODBSIZESIMULATIONTITLETEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos=1150, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:DBSTATUS_ODBSIZESIMULATION'),    fontSize=80, textInteractable=True)
        self.GUIOs["DBSTATUS_ODBSIZESIMULATIONDISPLAYTEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos=2200, yPos=1150, width=2600, height=250, style="styleA", text="-",                                                                      fontSize=80, textInteractable=True)
        self.GUIOs["DBSTATUS_ODBSIZENEURALNETWORKTITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 100, yPos= 800, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:DBSTATUS_ODBSIZENEURALNETWORK'), fontSize=80, textInteractable=True)
        self.GUIOs["DBSTATUS_ODBSIZENEURALNETWORKDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=2200, yPos= 800, width=2600, height=250, style="styleA", text="-",                                                                      fontSize=80, textInteractable=True)
        self.GUIOs["DBSTATUS_READDBSTATUSBUTTON"]              = button_typeA(**inst,  groupOrder=1, xPos= 100, yPos= 450, width=2300, height= 250, style="styleA", text=self.visualManager.getTextPack('DATABASE:DBSTATUS_READDBSTATUS'),        fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_DBSTATUS_READDBSTATUS'])
        self.GUIOs["DBSTATUS_COMPRESSMDBBUTTON"]               = button_typeA(**inst,  groupOrder=1, xPos=2500, yPos= 450, width=2300, height= 250, style="styleA", text=self.visualManager.getTextPack('DATABASE:DBSTATUS_COMPRESSMDB'),         fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_DBSTATUS_COMPRESSMDB'])



        #<Currency List>
        self.GUIOs["BLOCKSUBTITLE_CURRENCYLIST"] = passiveGraphics_wrapperTypeC(**inst, groupOrder=1, xPos=4900, yPos=8350, width=11000, height=200, style="styleA", text=self.visualManager.getTextPack('DATABASE:BLOCKTITLE_CURRENCYLIST'), fontSize = 80)
        #---Filter
        self.GUIOs["CURRENCYLIST_SEARCHTITLETEXT"]               = textBox_typeA(**inst,      groupOrder=1, xPos= 4900, yPos=8000, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_SEARCH'), fontSize=80, textInteractable=False)
        self.GUIOs["CURRENCYLIST_SEARCHTEXTINPUTBOX"]            = textInputBox_typeA(**inst, groupOrder=1, xPos= 6000, yPos=8000, width=1500, height=250, style="styleA", text="",                                                             fontSize=80, textUpdateFunction=self.pageObjectFunctions['ONTEXTUPDATE_CURRENCYLIST_SEARCHTEXT'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGTRUE"]      = switch_typeC(**inst, groupOrder=1, xPos= 7600, yPos=8000, width= 960, height=250, style="styleB", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_TRADINGTRUE'),      fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_TRADINGTRUE'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGFALSE"]     = switch_typeC(**inst, groupOrder=1, xPos= 8660, yPos=8000, width= 960, height=250, style="styleB", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_TRADINGFALSE'),     fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_TRADINGFALSE'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_COLLECTINGALL"]    = switch_typeC(**inst, groupOrder=1, xPos= 9720, yPos=8000, width=1260, height=250, style="styleB", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_COLLECTINGALL'),    fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_COLLECTINGALL'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_COLLECTINGSTREAM"] = switch_typeC(**inst, groupOrder=1, xPos=11080, yPos=8000, width=1260, height=250, style="styleB", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_COLLECTINGSTREAM'), fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_COLLECTINGSTREAM'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_COLLECTINGNONE"]   = switch_typeC(**inst, groupOrder=1, xPos=12440, yPos=8000, width=1260, height=250, style="styleB", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_COLLECTINGNONE'),   fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_COLLECTINGNONE'])
        self.GUIOs["CURRENCYLIST_AUXBUTTON_SELECTALL"]  = button_typeA(**inst, groupOrder=1, xPos=13800, yPos=8000, width=1000, height= 250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_SELECTALL'),  fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_CURRENCYLIST_SELECTALL'])
        self.GUIOs["CURRENCYLIST_AUXBUTTON_RELEASEALL"] = button_typeA(**inst, groupOrder=1, xPos=14900, yPos=8000, width=1000, height= 250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_RELEASEALL'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_CURRENCYLIST_RELEASEALL'])
        self.GUIOs["CURRENCYLIST_SORTBYTITLETEXT"]                       = textBox_typeA(**inst, groupOrder=1, xPos= 4900, yPos=7650, width=1000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_SORTBY'), fontSize=80, textInteractable=False)
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYINDEX"]              = switch_typeC(**inst,  groupOrder=1, xPos= 6000, yPos=7650, width=1500, height=250, style="styleB", name="INDEX",              text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_INDEX'),              fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBY'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYSYMBOL"]             = switch_typeC(**inst,  groupOrder=1, xPos= 7600, yPos=7650, width=1500, height=250, style="styleB", name="SYMBOL",             text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_SYMBOL'),             fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBY'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYFIRSTINTERVAL"]      = switch_typeC(**inst,  groupOrder=1, xPos= 9200, yPos=7650, width=1600, height=250, style="styleB", name="FIRSTINTERVAL",      text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_FIRSTINTERVAL'),      fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBY'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYAVAILABILITY_KL"]    = switch_typeC(**inst,  groupOrder=1, xPos=10900, yPos=7650, width=1600, height=250, style="styleB", name="AVAILABILITY_KL",    text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABILITY_KL'),    fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBY'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYAVAILABILITY_DEPTH"] = switch_typeC(**inst,  groupOrder=1, xPos=12600, yPos=7650, width=1600, height=250, style="styleB", name="AVAILABILITY_DEPTH", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABILITY_DEPTH'), fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBY'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYAVAILABILITY_AT"]    = switch_typeC(**inst,  groupOrder=1, xPos=14300, yPos=7650, width=1600, height=250, style="styleB", name="AVAILABILITY_AT",    text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABILITY_AT'),    fontSize=80, statusUpdateFunction=self.pageObjectFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBY'])
        self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYINDEX"].setStatus(status = True, callStatusUpdateFunction = False)
        self.puVar['currencies_lastSortBy'] = 'INDEX'
        
        #---List
        self.GUIOs["CURRENCYLIST_SELECTIONBOX"] = selectionBox_typeC(**inst, groupOrder=1, xPos=4900, yPos=2200, width=11000, height=5350, style="styleA", fontSize = 80, elementHeight = 250, multiSelect = True, singularSelect_allowRelease = False, selectionUpdateFunction = self.pageObjectFunctions['ONSELECTIONUPDATE_CURRENCYLIST_CURRENCYSELECTION'], 
                                                                     elementWidths = (800, 1650, 900, 1100, 1100, 1100, 1100, 1100, 1100, 800))
        self.GUIOs["CURRENCYLIST_SELECTIONBOX"].editColumnTitles(columnTitles = [{'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_INDEX')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_SYMBOL')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_STATUS')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_FIRSTINTERVAL_KL')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_FIRSTINTERVAL_DEPTH')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_FIRSTINTERVAL_AT')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABILITY_KL')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABILITY_DEPTH')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABILITY_AT')},
                                                                                 {'text': self.visualManager.getTextPack('DATABASE:CURRENCYLIST_COLLECTING')},
                                                                                 ])
        
        #---Information
        self.GUIOs["CURRENCYLIST_SYMBOLTITLETEXT"]            = textBox_typeA(**inst, groupOrder=1, xPos= 4900, yPos=1850, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_SYMBOL'),               fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_SYMBOLDISPLAYTEXT"]          = textBox_typeA(**inst, groupOrder=1, xPos= 5700, yPos=1850, width=1800, height=250, style="styleA", text="-",                                                                          fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_STATUSTITLETEXT"]            = textBox_typeA(**inst, groupOrder=1, xPos= 7600, yPos=1850, width= 700, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_STATUS'),               fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_STATUSDISPLAYTEXT"]          = textBox_typeA(**inst, groupOrder=1, xPos= 8400, yPos=1850, width=1000, height=250, style="styleA", text="-",                                                                          fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_COLLECTINGTITLETEXT"]        = textBox_typeA(**inst, groupOrder=1, xPos= 9500, yPos=1850, width=1700, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_COLLECTING_WITHTYPES'), fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_COLLECTINGDISPLAYTEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos=11300, yPos=1850, width= 850, height=250, style="styleA", text="-",                                                                          fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_COLLECTINGSTREAMSWITCH"]     = switch_typeB(**inst, groupOrder=2, xPos=12250, yPos=1850, width= 500, height=250, style="styleA", align='horizontal', switchStatus=False, statusUpdateFunction = self.pageObjectFunctions['ONSTATUSUPDATE_CURRENCYLIST_COLLECTINGSWITCH'])
        self.GUIOs["CURRENCYLIST_COLLECTINGHISTORICALSWITCH"] = switch_typeB(**inst, groupOrder=2, xPos=12850, yPos=1850, width= 500, height=250, style="styleA", align='horizontal', switchStatus=False, statusUpdateFunction = self.pageObjectFunctions['ONSTATUSUPDATE_CURRENCYLIST_COLLECTINGSWITCH'])
        self.GUIOs["CURRENCYLIST_COLLECTINGSTREAMSWITCH"].deactivate()
        self.GUIOs["CURRENCYLIST_COLLECTINGHISTORICALSWITCH"].deactivate()
        self.GUIOs["CURRENCYLIST_REFETCHDUMMYBUTTON"]    = button_typeA(**inst, groupOrder=1, xPos=13450, yPos=1850, width=1100, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_REFETCHDUMMY'), fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_CURRENCYLIST_REFETCHDUMMYBUTTON'])
        self.GUIOs["CURRENCYLIST_REFETCHDUMMYBUTTON"].deactivate()
        self.GUIOs["CURRENCYLIST_RESETBUTTON"]           = button_typeA(**inst, groupOrder=1, xPos=14650, yPos=1850, width= 650, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_RESET'),        fontSize=80, releaseFunction=self.pageObjectFunctions['ONBUTTONRELEASE_CURRENCYLIST_RESETBUTTON'])
        self.GUIOs["CURRENCYLIST_RESETSWITCH"]           = switch_typeB(**inst, groupOrder=2, xPos=15400, yPos=1850, width= 500, height=250, style="styleA", align='horizontal', switchStatus=False, statusUpdateFunction = self.pageObjectFunctions['ONSTATUSUPDATE_CURRENCYLIST_RESETSWITCH']) 
        self.GUIOs["CURRENCYLIST_RESETBUTTON"].deactivate()
        self.GUIOs["CURRENCYLIST_RESETSWITCH"].deactivate()
        self.GUIOs["CURRENCYLIST_FIRSTINTERVALKLTITLETEXT"]        = textBox_typeA(**inst, groupOrder=1, xPos= 4900, yPos=1500, width=1700, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_FIRSTINTERVAL_KL_FULL'),    fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_FIRSTINTERVALKLDISPLAYTEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos= 6700, yPos=1500, width=1800, height=250, style="styleA", text="-",                                                                              fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_FIRSTINTERVALDEPTHTITLETEXT"]     = textBox_typeA(**inst, groupOrder=1, xPos= 8600, yPos=1500, width=1700, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_FIRSTINTERVAL_DEPTH_FULL'), fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_FIRSTINTERVALDEPTHDISPLAYTEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos=10400, yPos=1500, width=1800, height=250, style="styleA", text="-",                                                                              fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_FIRSTINTERVALATTITLETEXT"]        = textBox_typeA(**inst, groupOrder=1, xPos=12300, yPos=1500, width=1700, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_FIRSTINTERVAL_AT_FULL'),    fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_FIRSTINTERVALATDISPLAYTEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos=14100, yPos=1500, width=1800, height=250, style="styleA", text="-",                                                                              fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABLERANGESKLTITLETEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos= 4900, yPos=1150, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABLERANGES_KL'),    fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABLERANGESKLDISPLAYTEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos= 7000, yPos=1150, width=7200, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABILITYKLDISPLAYTEXT"]       = textBox_typeA(**inst, groupOrder=1, xPos=14300, yPos=1150, width=1600, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABLERANGESDEPTHTITLETEXT"]   = textBox_typeA(**inst, groupOrder=1, xPos= 4900, yPos= 800, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABLERANGES_DEPTH'), fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABLERANGESDEPTHDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos= 7000, yPos= 800, width=7200, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABILITYDEPTHDISPLAYTEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos=14300, yPos= 800, width=1600, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABLERANGESATTITLETEXT"]      = textBox_typeA(**inst, groupOrder=1, xPos= 4900, yPos= 450, width=2000, height=250, style="styleA", text=self.visualManager.getTextPack('DATABASE:CURRENCYLIST_AVAILABLERANGES_AT'),    fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABLERANGESATDISPLAYTEXT"]    = textBox_typeA(**inst, groupOrder=1, xPos= 7000, yPos= 450, width=7200, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)
        self.GUIOs["CURRENCYLIST_AVAILABILITYATDISPLAYTEXT"]       = textBox_typeA(**inst, groupOrder=1, xPos=14300, yPos= 450, width=1600, height=250, style="styleA", text="-",                                                                           fontSize=80, textInteractable=True)

        #<Message>
        self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"] = textBox_typeA(**inst, groupOrder=1, xPos=  100, yPos=100, width=15800, height=250, style="styleA", text="-", fontSize=80, textInteractable=False)
        
        #<Clock>
        self.GUIOs["CLOCK_LOCAL"] = textBox_typeA(**inst, groupOrder=1, xPos= 14000, yPos=8800, width=1950, height=150, style=None, text="", anchor = 'E', fontSize = 80, textInteractable = False)
        self.GUIOs["CLOCK_UTC"]   = textBox_typeA(**inst, groupOrder=1, xPos= 14000, yPos=8650, width=1950, height=150, style=None, text="", anchor = 'E', fontSize = 80, textInteractable = False)

    elif (self.displaySpaceDefiner['ratio'] == '21:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 21000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
    elif (self.displaySpaceDefiner['ratio'] == '32:9H'):
        self.backgroundShape = pyglet.shapes.Rectangle(batch = self.batch, group = self.groups['BACKGROUND'], x = 0, y = 0, width = 32000, height = 9000, color = self.visualManager.getFromColorTable('PAGEBACKGROUND'))
#SETUP PAGE <MAIN> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <LOAD> ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageLoadFunction(self):
    #[1]: FAR Handlers Setup
    #---[1-1]: DATAMANAGER
    self.ipcA.addFARHandler('onFetchStatusUpdate', self.pageAuxillaryFunctions['_FAR_ONFETCHSTATUSUPDATE'], executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)
    self.ipcA.addFARHandler('onCurrenciesUpdate',  self.pageAuxillaryFunctions['_FAR_ONCURRENCIESUPDATE'],  executionThread = _IPC_THREADTYPE_MT, immediateResponse = True)

    #[2]: PRD Read
    #---[2-1]: Fetch Status
    fetchStatus_prd = self.ipcA.getPRD(processName = 'DATAMANAGER',  prdAddress = 'FETCHSTATUS')
    if fetchStatus_prd is not None: self.puVar['fetchStatus'] = fetchStatus_prd.copy()
    #---[2-2]: Currencies
    currencies_prd = self.ipcA.getPRD(processName = 'DATAMANAGER',  prdAddress = 'CURRENCIES')
    if currencies_prd is not None: self.puVar['currencies'] = currencies_prd.copy()

    #[3]: DB Status Read Request
    for fID in ('readMarketDBStatus', 'readAccountDBStatus', 'readSimulationDBStatus', 'readNeuralNetworkDBStatus'):
        self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER',
                          functionID     = fID,
                          functionParams = None,
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONDBSTATUSREADRESPONSE'])
    self.puVar['dbStatusRequests'] = {'market', 'account', 'simulation', 'neuralNetwork'}

    #[4]: Currencies Availability Computation
    self.pageAuxillaryFunctions['COMPUTECURRENCIESAVAILABILITY']()

    #[5]: GUIO Update
    #---[5-1]: Fetch Status Update
    self.pageAuxillaryFunctions['UPDATEFETCHSTATUSINFORMATION']()
    #---[5-2]: Currencies List Update
    self.pageAuxillaryFunctions['SETLIST']()
    #---[5-3]: Currencies Selected Currency Info Update
    self.pageAuxillaryFunctions['UPDATEINFORMATION']()
    #---[5-4]: Select & Release Buttons
    nSymbols  = len(self.puVar['currencies'])
    nSelected = len(self.puVar['currencies_selected'])
    if nSelected == nSymbols: self.GUIOs["CURRENCYLIST_AUXBUTTON_SELECTALL"].deactivate()
    else:                     self.GUIOs["CURRENCYLIST_AUXBUTTON_SELECTALL"].activate()
    if nSelected == 0: self.GUIOs["CURRENCYLIST_AUXBUTTON_RELEASEALL"].deactivate()
    else:              self.GUIOs["CURRENCYLIST_AUXBUTTON_RELEASEALL"].activate()
#SETUP PAGE <LOAD> END ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <ESCAPE> --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageEscapeFunction(self):
    for fID in ('onFetchStatusUpdate', 'onCurrenciesUpdate',):
        self.ipcA.removeFARHandler(functionID   = fID)
        self.ipcA.addDummyFARHandler(functionID = fID)
#SETUP PAGE <ESCAPE> END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#SETUP PAGE <PROCESS> -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __pageProcessFunction(self, t_elapsed_ns, onLoad = False):
    #[1]: Instances
    puVar = self.puVar
    guios = self.GUIOs
    pafs  = self.pageAuxillaryFunctions
    t_current_ns = time.perf_counter_ns()

    #[2]: Currencies Availability Computation
    cac_lastComputed = puVar['currencies_availabilities_lastComputed']
    cac_this = auxiliaries.getNextIntervalTickTimestamp(intervalID = constants.KLINTERVAL, 
                                                        timestamp  = int(time.time()), 
                                                        nTicks     = 0)
    if cac_lastComputed != cac_this:
        #[2-1]: Availabilities Computation & Selection Box Update
        pafs['COMPUTECURRENCIESAVAILABILITY'](updateSelectionBox = True)
        #[2-2]: Selected Currency Information Update
        pafs['UPDATEINFORMATION']()
        #[2-3]: Timer Update
        puVar['currencies_availabilities_lastComputed'] = cac_this

    #[3]: Clock Update
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

    #<Local Network Import>
    def __onButtonRelease_LocalNetworkImport_ImportButton(objInstance, **kwargs):
        #[1]: Parameters
        symbols = list(self.puVar['currencies_selected'])
        ipAddress  = self.GUIOs["LOCALNETWORKIMPORT_IPADDRESSTEXTINPUTBOX"].getText()
        portNumber = self.GUIOs["LOCALNETWORKIMPORT_PORTNUMBERTEXTINPUTBOX"].getText()
        dbName     = self.GUIOs["LOCALNETWORKIMPORT_DBNAMETEXTINPUTBOX"].getText()
        user       = self.GUIOs["LOCALNETWORKIMPORT_USERTEXTINPUTBOX"].getText()
        password   = self.GUIOs["LOCALNETWORKIMPORT_PASSWORDTEXTINPUTBOX"].getText()

        #[2]: Request Dispatch
        self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                          functionID     = 'loadDummyMarketDataFromLocalNetwork', 
                          functionParams = {'symbols':    symbols,
                                            'ipAddress':  ipAddress,
                                            'portNumber': portNumber,
                                            'dbName':     dbName,
                                            'user':       user,
                                            'password':   password}, 
                          farrHandler    = self.pageAuxillaryFunctions['_FARR_ONLOCALNETWORKIMPORTRESPONSE'])
        
        #[3]: Import Button Deactivation
        objInstance.deactivate()
    objFunctions['ONBUTTONRELEASE_LOCALNETWORKIMPORT_IMPORTBUTTON'] = __onButtonRelease_LocalNetworkImport_ImportButton

    #<DB Status>
    def __onButtonRelease_DBStatus_ReadDBStatus(objInstance, **kwargs):
        #[1]: Instances
        puVar             = self.puVar
        func_ipcA_sendFAR = self.ipcA.sendFAR

        #[2]: Requests Dispatch
        for fID in ('readMarketDBStatus', 'readAccountDBStatus', 'readSimulationDBStatus', 'readNeuralNetworkDBStatus'):
            func_ipcA_sendFAR(targetProcess  = 'DATAMANAGER',
                              functionID     = fID,
                              functionParams = None,
                              farrHandler = self.pageAuxillaryFunctions['_FARR_ONDBSTATUSREADRESPONSE'])
        puVar['dbStatusRequests'] = {'market', 'account', 'simulation', 'neuralNetwork'}

        #[3]: Button Deactivation
        objInstance.deactivate() 
    def __onButtonRelease_DBStatus_CompressMDB(objInstance, **kwargs):
        self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                          functionID     = 'compressMarketDB', 
                          functionParams = None, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONMDBCOMPRESSIONRESPONSE'])
        objInstance.deactivate() 
    objFunctions['ONBUTTONRELEASE_DBSTATUS_COMPRESSMDB'] = __onButtonRelease_DBStatus_CompressMDB
    objFunctions['ONBUTTONRELEASE_DBSTATUS_READDBSTATUS'] = __onButtonRelease_DBStatus_ReadDBStatus

    #<Currency List>
    #---Filter
    def __onTextUpdate_CurrencyList_SearchText(objInstance, **kwargs):
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyList_TradingTrue(objInstance, **kwargs):
        if self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGFALSE"].getStatus(): self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGFALSE"].setStatus(status = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyList_TradingFalse(objInstance, **kwargs):
        if self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGTRUE"].getStatus(): self.GUIOs["CURRENCYLIST_FILTERSWITCH_TRADINGTRUE"].setStatus(status = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onButtonRelease_CurrencyList_SelectAll(objInstance, **kwargs):
        selectionBox = self.GUIOs["CURRENCYLIST_SELECTIONBOX"]
        currencies   = self.puVar['currencies']
        nSymbols     = len(currencies)
        for idx, symbol in enumerate(currencies):
            if idx == nSymbols-1: callSelectionUpdateFunction = True
            else:                 callSelectionUpdateFunction = False
            selectionBox.addSelected(itemKey = symbol, callSelectionUpdateFunction = callSelectionUpdateFunction)
        objInstance.deactivate()
    def __onButtonRelease_CurrencyList_ReleaseAll(objInstance, **kwargs):
        self.GUIOs["CURRENCYLIST_SELECTIONBOX"].clearSelected()
        objInstance.deactivate()
    def __onSwitchStatusUpdate_CurrencyList_CollectingAll(objInstance, **kwargs):
        guios = self.GUIOs
        for gTarget in ("CURRENCYLIST_FILTERSWITCH_COLLECTINGSTREAM", 
                        "CURRENCYLIST_FILTERSWITCH_COLLECTINGNONE"):
            guio = guios[gTarget]
            if guio.getStatus(): guio.setStatus(status = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyList_CollectingStream(objInstance, **kwargs):
        guios = self.GUIOs
        for gTarget in ("CURRENCYLIST_FILTERSWITCH_COLLECTINGALL", 
                        "CURRENCYLIST_FILTERSWITCH_COLLECTINGNONE"):
            guio = guios[gTarget]
            if guio.getStatus(): guio.setStatus(status = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyList_CollectingNone(objInstance, **kwargs):
        guios = self.GUIOs
        for gTarget in ("CURRENCYLIST_FILTERSWITCH_COLLECTINGALL", 
                        "CURRENCYLIST_FILTERSWITCH_COLLECTINGSTREAM"):
            guio = guios[gTarget]
            if guio.getStatus(): guio.setStatus(status = False, callStatusUpdateFunction = False)
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __onSwitchStatusUpdate_CurrencyList_SortBy(objInstance, **kwargs):
        #[1]: Instances
        sType_prev = self.puVar['currencies_lastSortBy']
        sType_this = objInstance.getName()

        #[2]: Update Handling
        #---[2-1]: Same Switch (Turning Off Itself - Go Back To Index Sort)
        if sType_prev == sType_this:
            self.GUIOs["CURRENCYLIST_FILTERSWITCH_SORTBYINDEX"].setStatus(status = True, callStatusUpdateFunction = False)
            self.puVar['currencies_lastSortBy'] = 'INDEX'
        #---[2-2]: Different Switch (Turning On A Different Switch)
        else:
            self.GUIOs[f"CURRENCYLIST_FILTERSWITCH_SORTBY{sType_prev}"].setStatus(status = False, callStatusUpdateFunction = False)
            self.puVar['currencies_lastSortBy'] = sType_this

        #[3]: Filter Update
        if sType_prev != self.puVar['currencies_lastSortBy']:
            self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    objFunctions['ONTEXTUPDATE_CURRENCYLIST_SEARCHTEXT']               = __onTextUpdate_CurrencyList_SearchText
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_TRADINGTRUE']      = __onSwitchStatusUpdate_CurrencyList_TradingTrue
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_TRADINGFALSE']     = __onSwitchStatusUpdate_CurrencyList_TradingFalse
    objFunctions['ONBUTTONRELEASE_CURRENCYLIST_SELECTALL']             = __onButtonRelease_CurrencyList_SelectAll
    objFunctions['ONBUTTONRELEASE_CURRENCYLIST_RELEASEALL']            = __onButtonRelease_CurrencyList_ReleaseAll
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_COLLECTINGALL']    = __onSwitchStatusUpdate_CurrencyList_CollectingAll
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_COLLECTINGSTREAM'] = __onSwitchStatusUpdate_CurrencyList_CollectingStream
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_COLLECTINGNONE']   = __onSwitchStatusUpdate_CurrencyList_CollectingNone
    objFunctions['ONSWITCHSTATUSUPDATE_CURRENCYLIST_SORTBY']           = __onSwitchStatusUpdate_CurrencyList_SortBy

    #---List
    def __onSelectionUpdate_CurrencyList_CurrencySelection(objInstance, **kwargs):
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs

        #[2]: Selected Currencies & Information Update
        puVar['currencies_selected'] = set(objInstance.getSelected())
        self.pageAuxillaryFunctions['UPDATEINFORMATION']()

        #[3]: Select & Release Buttons
        nSymbols  = len(puVar['currencies'])
        nSelected = len(puVar['currencies_selected'])
        if nSelected == nSymbols: guios["CURRENCYLIST_AUXBUTTON_SELECTALL"].deactivate()
        else:                     guios["CURRENCYLIST_AUXBUTTON_SELECTALL"].activate()
        if nSelected == 0: guios["CURRENCYLIST_AUXBUTTON_RELEASEALL"].deactivate()
        else:              guios["CURRENCYLIST_AUXBUTTON_RELEASEALL"].activate()

        #[4]: Reset Buttons
        guios["CURRENCYLIST_RESETBUTTON"].deactivate()
        guios["CURRENCYLIST_RESETSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
        if 0 < nSelected: guios["CURRENCYLIST_RESETSWITCH"].activate()
        else:             guios["CURRENCYLIST_RESETSWITCH"].deactivate()

        #[5]: Local Network Import Button
        if 0 < nSelected: guios["LOCALNETWORKIMPORT_IMPORTBUTTON"].activate()
        else:             guios["LOCALNETWORKIMPORT_IMPORTBUTTON"].deactivate()
    objFunctions['ONSELECTIONUPDATE_CURRENCYLIST_CURRENCYSELECTION'] = __onSelectionUpdate_CurrencyList_CurrencySelection

    #---Information
    def __onStatusUpdate_CurrencyList_CollectingSwitch(objInstance, **kwargs):
        #[1]: Instances
        guios = self.GUIOs
        puVar = self.puVar

        #[2]: Mode Determination
        symbols = list(puVar['currencies_selected'])
        collectingStream     = guios["CURRENCYLIST_COLLECTINGSTREAMSWITCH"].getStatus()
        collectingHistorical = guios["CURRENCYLIST_COLLECTINGHISTORICALSWITCH"].getStatus()
        if not collectingStream and collectingHistorical:
            collectingHistorical = False
            guios["CURRENCYLIST_COLLECTINGHISTORICALSWITCH"].setStatus(status = False, animate = True, callStatusUpdateFunction = False)
        mode = (collectingStream, collectingHistorical)

        #[3]: Request Dispatch
        self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                          functionID     = 'setMarketDataCollection', 
                          functionParams = {'symbols': symbols,
                                            'mode':    mode}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONSETMARKETDATACOLLECTIONRESPONSE'])
        
        #[4]: Temporary Deactivation
        guios["CURRENCYLIST_COLLECTINGSTREAMSWITCH"].deactivate()
        guios["CURRENCYLIST_COLLECTINGHISTORICALSWITCH"].deactivate()  
    def __onButtonRelease_CurrencyList_RefetchDummyButton(objInstance, **kwargs):
        symbols = list(self.puVar['currencies_selected'])
        self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                          functionID     = 'refetchDummyMarketData', 
                          functionParams = {'symbols': symbols}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONREFETCHDUMMYRESPONSE'])
        objInstance.deactivate()
    def __onButtonRelease_CurrencyList_ResetButton(objInstance, **kwargs):
        symbols = list(self.puVar['currencies_selected'])
        self.ipcA.sendFAR(targetProcess  = 'DATAMANAGER', 
                          functionID     = 'resetMarketData', 
                          functionParams = {'symbols': symbols}, 
                          farrHandler = self.pageAuxillaryFunctions['_FARR_ONRESETMARKETDATARESPONSE'])
        objInstance.deactivate() 
    def __onStatusUpdate_CurrencyList_ResetSwitch(objInstance, **kwargs):
        status      = objInstance.getStatus()
        resetButton = self.GUIOs["CURRENCYLIST_RESETBUTTON"]
        if status: resetButton.activate()
        else:      resetButton.deactivate()
    objFunctions['ONSTATUSUPDATE_CURRENCYLIST_COLLECTINGSWITCH']    = __onStatusUpdate_CurrencyList_CollectingSwitch
    objFunctions['ONBUTTONRELEASE_CURRENCYLIST_REFETCHDUMMYBUTTON'] = __onButtonRelease_CurrencyList_RefetchDummyButton
    objFunctions['ONBUTTONRELEASE_CURRENCYLIST_RESETBUTTON']        = __onButtonRelease_CurrencyList_ResetButton
    objFunctions['ONSTATUSUPDATE_CURRENCYLIST_RESETSWITCH']         = __onStatusUpdate_CurrencyList_ResetSwitch

    #Return the generated functions
    return objFunctions
#OBJECT FUNCTIONS END -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------





#AUXILALRY FUNCTIONS --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
def __generateAuxillaryFunctions(self):
    auxFunctions = dict()

    #<_PAGELOAD>
    def __far_onCurrenciesUpdate(requester, updatedContents):
        #[1]: Source Check
        if requester != 'DATAMANAGER':
            return
        
        #[2]: Instances
        vm     = self.visualManager
        puVar  = self.puVar
        guios  = self.GUIOs
        getPRD = self.ipcA.getPRD
        currencies                = puVar['currencies']
        currencies_availabilities = puVar['currencies_availabilities']
        selectionBox = self.GUIOs["CURRENCYLIST_SELECTIONBOX"]
        func_cca = self.pageAuxillaryFunctions['COMPUTECURRENCIESAVAILABILITY']
        
        #[3]: Reset Flags
        resetList         = False
        reapplyListFilter = False

        #[4]: Updates Read
        checkList_singular = {'kline_firstOpenTS', 'depth_firstOpenTS', 'aggTrade_firstOpenTS', 'klines_availableRanges', 'depths_availableRanges', 'aggTrades_availableRanges', 'collecting'}
        for updatedContent in updatedContents:
            #[4-1]: Instances
            symbol    = updatedContent['symbol']
            contentID = updatedContent['id']

            #[4-2]: New Currency
            if contentID == '_ADDED':
                currencies[symbol] = getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol))
                resetList = True

            #[4-3]: Existing Currency Update
            else:
                #[4-3-1]: Instances & Updated Contents
                currencies_symbol = currencies[symbol]
                cID_0             = contentID[0]
                updated           = set()

                #[4-3-2]: Updates Check
                #---[4-3-2-1]: Currency Server Information Updated (Status)
                if contentID[0] == 'info_server': 
                    try:    cID_1 = contentID[1]
                    except: cID_1 = None
                    #[4-3-2-1-1]: Entire Server Information Updated
                    if cID_1 is None:
                        currencies_symbol['info_server'] = getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'info_server'))
                        updated.add('status')
                    #[4-3-2-1-2]: Currency Status Updated
                    else:
                        if cID_1 == 'status': 
                            currencies_symbol['info_server']['status'] = getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, 'info_server', 'status'))
                            updated.add('status')
                #---[4-3-2-2]: Singular Address Expected Updated
                elif cID_0 in checkList_singular:
                    currencies_symbol[cID_0] = getPRD(processName = 'DATAMANAGER', prdAddress = ('CURRENCIES', symbol, cID_0))
                    updated.add(cID_0)

                #[4-3-3]: Updates Response
                updateInformation = (symbol in puVar['currencies_selected'] and len(puVar['currencies_selected']) == 1)
                for u in updated:
                    #[4-3-3-1]: Status
                    if u == 'status':
                        info_server = currencies_symbol['info_server']
                        status = None if info_server is None else info_server['status']
                        status_text, status_ts = statusToString(vm = vm, status = status)
                        nsbi = {'text':       status_text, 
                                'textStyles': status_ts, 
                                'textAnchor': 'CENTER'}
                        selectionBox.editSelectionListItem(itemKey = symbol, item = nsbi, columnIndex = 2)
                        reapplyListFilter = True
                        if updateInformation:
                            guios["CURRENCYLIST_STATUSDISPLAYTEXT"].updateText(text = status_text, textStyle = status_ts)

                    #[4-3-3-2]: Kline First Interval
                    elif u == 'kline_firstOpenTS':
                        fi_text = firstIntervalToString(firstInterval = currencies_symbol['kline_firstOpenTS'])
                        nsbi = {'text':       fi_text, 
                                'textStyles': [('all', 'DEFAULT'),], 
                                'textAnchor': 'CENTER'}
                        selectionBox.editSelectionListItem(itemKey = symbol, item = nsbi, columnIndex = 3)
                        reapplyListFilter = True
                        if updateInformation:
                            guios["CURRENCYLIST_FIRSTINTERVALKLDISPLAYTEXT"].updateText(text = fi_text)

                    #[4-3-3-3]: Depth First Interval
                    elif u == 'depth_firstOpenTS':
                        fi_text = firstIntervalToString(firstInterval = currencies_symbol['depth_firstOpenTS'])
                        nsbi = {'text':       fi_text, 
                                'textStyles': [('all', 'DEFAULT'),], 
                                'textAnchor': 'CENTER'}
                        selectionBox.editSelectionListItem(itemKey = symbol, item = nsbi, columnIndex = 4)
                        reapplyListFilter = True
                        if updateInformation:
                            guios["CURRENCYLIST_FIRSTINTERVALDEPTHDISPLAYTEXT"].updateText(text = fi_text)

                    #[4-3-3-4]: AggTrade First Interval
                    elif u == 'aggTrade_firstOpenTS':
                        fi_text = firstIntervalToString(firstInterval = currencies_symbol['aggTrade_firstOpenTS'])
                        nsbi = {'text':       fi_text, 
                                'textStyles': [('all', 'DEFAULT'),], 
                                'textAnchor': 'CENTER'}
                        selectionBox.editSelectionListItem(itemKey = symbol, item = nsbi, columnIndex = 5)
                        reapplyListFilter = True
                        if updateInformation:
                            guios["CURRENCYLIST_FIRSTINTERVALATDISPLAYTEXT"].updateText(text = fi_text)

                    #[4-3-3-5]: Klines Available Ranges
                    elif u == 'klines_availableRanges':
                        func_cca(symbols = [symbol,], targets = ['kline',], updateSelectionBox = True)
                        reapplyListFilter = True
                        if updateInformation:
                            guios["CURRENCYLIST_AVAILABLERANGESKLDISPLAYTEXT"].updateText(text = aRangesToString(availableRanges = currencies_symbol['klines_availableRanges']))
                            avail_text, avail_ts = availabilityToString(availability = currencies_availabilities[symbol]['kline'])
                            guios["CURRENCYLIST_AVAILABILITYKLDISPLAYTEXT"].updateText(text = avail_text, textStyle = avail_ts)

                    #[4-3-3-6]: Depths Available Ranges
                    elif u == 'depths_availableRanges':
                        func_cca(symbols = [symbol,], targets = ['depth',], updateSelectionBox = True)
                        reapplyListFilter = True
                        if updateInformation:
                            guios["CURRENCYLIST_AVAILABLERANGESDEPTHDISPLAYTEXT"].updateText(text = aRangesToString(availableRanges = currencies_symbol['depths_availableRanges']))
                            avail_text, avail_ts = availabilityToString(availability = currencies_availabilities[symbol]['depth'])
                            guios["CURRENCYLIST_AVAILABILITYDEPTHDISPLAYTEXT"].updateText(text = avail_text, textStyle = avail_ts)

                    #[4-3-3-7]: AggTrades Available Ranges
                    elif u == 'aggTrades_availableRanges':
                        func_cca(symbols = [symbol,], targets = ['aggTrade',], updateSelectionBox = True)
                        reapplyListFilter = True
                        if updateInformation:
                            guios["CURRENCYLIST_AVAILABLERANGESATDISPLAYTEXT"].updateText(text = aRangesToString(availableRanges = currencies_symbol['aggTrades_availableRanges']))
                            avail_text, avail_ts = availabilityToString(availability = currencies_availabilities[symbol]['aggTrade'])
                            guios["CURRENCYLIST_AVAILABILITYATDISPLAYTEXT"].updateText(text = avail_text, textStyle = avail_ts)

                    #[4-3-3-8]: Collecting
                    elif u == 'collecting':
                        collecting_text, collecting_ts = collectingToString(collecting = currencies_symbol['collecting'])
                        reapplyListFilter = True
                        nsbi = {'text':       collecting_text,
                                'textStyles': collecting_ts, 
                                'textAnchor': 'CENTER'}
                        selectionBox.editSelectionListItem(itemKey = symbol, item = nsbi, columnIndex = 9)
                        if symbol in puVar['currencies_selected']:
                            collectingStream     = all(currencies[s]['collecting'][0] for s in puVar['currencies_selected'])
                            collectingHistorical = all(currencies[s]['collecting'][1] for s in puVar['currencies_selected'])
                            collecting_text, collecting_ts = collectingToString(collecting = (collectingStream, collectingHistorical))
                            guios["CURRENCYLIST_COLLECTINGDISPLAYTEXT"].updateText(text = collecting_text, textStyle = collecting_ts)
                            guios["CURRENCYLIST_COLLECTINGSTREAMSWITCH"].setStatus(status     = collectingStream,     callStatusUpdateFunction = False)
                            guios["CURRENCYLIST_COLLECTINGHISTORICALSWITCH"].setStatus(status = collectingHistorical, callStatusUpdateFunction = False)
                            guios["CURRENCYLIST_COLLECTINGSTREAMSWITCH"].activate()
                            if collectingStream: guios["CURRENCYLIST_COLLECTINGHISTORICALSWITCH"].activate()
                            else:                guios["CURRENCYLIST_COLLECTINGHISTORICALSWITCH"].deactivate()

        #[5]: Reset
        if resetList:
            self.pageAuxillaryFunctions['COMPUTECURRENCIESAVAILABILITY'](updateSelectionBox = False)
            self.pageAuxillaryFunctions['SETLIST']()
        elif reapplyListFilter: 
            self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    auxFunctions['_FAR_ONCURRENCIESUPDATE'] = __far_onCurrenciesUpdate

    #<Local Network Import>
    def __farr_onLocalNetworkImportResponse(responder, requestID, functionResult):
        #[1]: Response
        result  = functionResult['result']
        msg_str = functionResult['message']
        #[2]: Message Display
        msg_time_str = datetime.fromtimestamp(timestamp = time.time()).strftime("%Y/%m/%d %H:%M:%S")
        msg_color    = 'GREEN_LIGHT' if result else 'RED_LIGHT'
        self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = f"[{msg_time_str}] <DATAMANAGER> - {msg_str}", textStyle = msg_color)
        #[3]: Switch Reactivation
        if self.puVar['currencies_selected']: self.GUIOs["LOCALNETWORKIMPORT_IMPORTBUTTON"].activate()
    auxFunctions['_FARR_ONLOCALNETWORKIMPORTRESPONSE'] = __farr_onLocalNetworkImportResponse

    #<Data Collection>
    def __far_onFetchStatusUpdate(requester):
        self.puVar['fetchStatus'] = self.ipcA.getPRD(processName = 'DATAMANAGER',  prdAddress = 'FETCHSTATUS').copy()
        self.pageAuxillaryFunctions['UPDATEFETCHSTATUSINFORMATION']()
    def __updateFetchStatusInformation():
        #[1]: Instances
        guios = self.GUIOs
        puVar = self.puVar
        func_svf = auxiliaries.simpleValueFormatter
        func_tsf = auxiliaries.timeStringFormatter
        fStatus = puVar['fetchStatus']
        lastFetched               = fStatus['lastFetched']
        remainingRanges_kline     = fStatus['remainingRanges_kline']
        remainingRanges_depth     = fStatus['remainingRanges_depth']
        remainingRanges_aggTrade  = fStatus['remainingRanges_aggTrade']
        fetchSpeed_kline          = fStatus['fetchSpeed_kline']
        fetchSpeed_depth          = fStatus['fetchSpeed_depth']
        fetchSpeed_aggTrade       = fStatus['fetchSpeed_aggTrade']
        estimatedTimeOfCompletion = fStatus['estimatedTimeOfCompletion']

        #[2]: GUIOs Update
        #---[2-1]: Last Fetched
        if lastFetched is None:
            lastFetched_text = "-"
        else:
            symbol, target, fTime = lastFetched
            time_str = datetime.fromtimestamp(fTime).strftime("%Y/%m/%d %H:%M:%S")
            lastFetched_text = f"{symbol}@{target} [{time_str}]"
        guios["COLLECTIONPROCESS_LASTFETCHEDDISPLAYTEXT"].updateText(text = lastFetched_text, textStyle = 'DEFAULT')

        #---[2-2]: Average Fetch Speed - Kline
        if fetchSpeed_kline is None:
            fetchSpeed_kline_text = "-"
        else:
            fetchSpeed_kline_text = f"{func_svf(value = fetchSpeed_kline)} SIPS"
        guios["COLLECTIONPROCESS_AVGMDFETCHSPEEDKLDISPLAYTEXT"].updateText(text = fetchSpeed_kline_text, textStyle = 'DEFAULT')

        #---[2-3]: Average Fetch Speed - Depth
        if fetchSpeed_depth is None:
            fetchSpeed_depth_text = "-"
        else:
            fetchSpeed_depth_text = f"{func_svf(value = fetchSpeed_depth)} SIPS"
        guios["COLLECTIONPROCESS_AVGMDFETCHSPEEDDEPTHDISPLAYTEXT"].updateText(text = fetchSpeed_depth_text, textStyle = 'DEFAULT')

        #---[2-4]: Average Fetch Speed - AggTrade
        if fetchSpeed_aggTrade is None:
            fetchSpeed_aggTrade_text = "-"
        else:
            fetchSpeed_aggTrade_text = f"{func_svf(value = fetchSpeed_aggTrade)} SIPS"
        guios["COLLECTIONPROCESS_AVGMDFETCHSPEEDATDISPLAYTEXT"].updateText(text = fetchSpeed_aggTrade_text, textStyle = 'DEFAULT')

        #---[2-5]: Average Fetch Speed - Total
        fetchSpeed_total = 0
        nValidSpeed = 0
        if fetchSpeed_kline is not None:
            fetchSpeed_total += fetchSpeed_kline
            nValidSpeed      += 1
        if fetchSpeed_depth is not None:
            fetchSpeed_total += fetchSpeed_depth
            nValidSpeed      += 1
        if fetchSpeed_aggTrade is not None:
            fetchSpeed_total += fetchSpeed_aggTrade
            nValidSpeed      += 1
        if nValidSpeed: fetchSpeed_total = fetchSpeed_total/nValidSpeed
        else:           fetchSpeed_total = None
        if fetchSpeed_total is None:
            fetchSpeed_total_text = "-"
        else:
            fetchSpeed_total_text = f"{func_svf(value = fetchSpeed_total)} SIPS"
        guios["COLLECTIONPROCESS_AVGMDFETCHSPEEDTOTALDISPLAYTEXT"].updateText(text = fetchSpeed_total_text, textStyle = 'DEFAULT')

        #---[2-6]: Remaining Ranges - Kline
        if remainingRanges_kline is None:
            remainingRanges_kline_text = "-"
        else:
            remainingRanges_kline_text = f"{func_svf(value = remainingRanges_kline)} SI"
        guios["COLLECTIONPROCESS_REMAININGRANGESKLDISPLAYTEXT"].updateText(text = remainingRanges_kline_text, textStyle = 'DEFAULT')

        #---[2-7]: Remaining Ranges - Depth
        if remainingRanges_depth is None:
            remainingRanges_depth_text = "-"
        else:
            remainingRanges_depth_text = f"{func_svf(value = remainingRanges_depth)} SI"
        guios["COLLECTIONPROCESS_REMAININGRANGESDEPTHDISPLAYTEXT"].updateText(text = remainingRanges_depth_text, textStyle = 'DEFAULT')

        #---[2-8]: Remaining Ranges - AggTrade
        if remainingRanges_aggTrade is None:
            remainingRanges_aggTrade_text = "-"
        else:
            remainingRanges_aggTrade_text = f"{func_svf(value = remainingRanges_aggTrade)} SI"
        guios["COLLECTIONPROCESS_REMAININGRANGESATDISPLAYTEXT"].updateText(text = remainingRanges_aggTrade_text, textStyle = 'DEFAULT')

        #---[2-9]: Remaining Ranges - Total
        remainingRanges_total = 0
        if remainingRanges_kline    is not None: remainingRanges_total += remainingRanges_kline
        if remainingRanges_depth    is not None: remainingRanges_total += remainingRanges_depth
        if remainingRanges_aggTrade is not None: remainingRanges_total += remainingRanges_aggTrade
        remainingRanges_total_text = "-" if remainingRanges_total == 0 else f"{func_svf(value = remainingRanges_total)} SI"
        guios["COLLECTIONPROCESS_REMAININGRANGESTOTALDISPLAYTEXT"].updateText(text = remainingRanges_total_text, textStyle = 'DEFAULT')

        #---[2-10]: Estimated Time Of Completion
        if estimatedTimeOfCompletion is None:
            estimatedTimeOfCompletion_text = "-" 
        else:
            estimatedTimeOfCompletion_text = func_tsf(time_seconds = int(estimatedTimeOfCompletion))
        guios["COLLECTIONPROCESS_ESTIMATEDTIMEOFCOMPLETIONDISPLAYTEXT"].updateText(text = estimatedTimeOfCompletion_text, textStyle = 'DEFAULT')
    auxFunctions['_FAR_ONFETCHSTATUSUPDATE']     = __far_onFetchStatusUpdate
    auxFunctions['UPDATEFETCHSTATUSINFORMATION'] = __updateFetchStatusInformation

    #<DB Status>
    def __farr_onMDBCompressionResponse(responder, requestID, functionResult):
        #[1]: Response
        result   = functionResult['result']
        dbStatus = functionResult['dbStatus']
        msg_str  = functionResult['message']
        guios    = self.GUIOs

        #[2]: DB Status Display
        self.pageAuxillaryFunctions['UPDATEDBSTATUSDISPLAY'](type = 'market', dbStatus = dbStatus)

        #[3]: Message Display
        msg_time_str = datetime.fromtimestamp(timestamp = time.time()).strftime("%Y/%m/%d %H:%M:%S")
        msg_color    = 'GREEN_LIGHT' if result else 'RED_LIGHT'
        guios["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = f"[{msg_time_str}] <DATAMANAGER> - {msg_str}", textStyle = msg_color)
        guios["DBSTATUS_COMPRESSMDBBUTTON"].activate()
    def __farr_onDBStatusReadResponse(responder, requestID, functionResult):
        #[1]: Response
        type     = functionResult['type']
        result   = functionResult['result']
        dbStatus = functionResult['dbStatus']
        msg_str  = functionResult['message']
        guios    = self.GUIOs
        puVar    = self.puVar
        puVar['dbStatusRequests'].discard(type)

        #[2]: DB Status Display
        self.pageAuxillaryFunctions['UPDATEDBSTATUSDISPLAY'](type = type, dbStatus = dbStatus)
        if result:
            if not puVar['dbStatusRequests']:
                msg_time_str = datetime.fromtimestamp(timestamp = time.time()).strftime("%Y/%m/%d %H:%M:%S")
                guios["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text      = f"[{msg_time_str}] DB Status Succesfully Loaded!", 
                                                               textStyle = 'GREEN_LIGHT')
        else:
            msg_time_str = datetime.fromtimestamp(timestamp = time.time()).strftime("%Y/%m/%d %H:%M:%S")
            guios["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text      = f"[{msg_time_str}] <DATAMANAGER> - {msg_str}", 
                                                           textStyle = 'RED_LIGHT')

        #[4]: Button Reactivation
        if not puVar['dbStatusRequests']:
            guios["DBSTATUS_READDBSTATUSBUTTON"].activate()
    def __updateDBStatusDisplay(type, dbStatus):
        #[1]: Instances
        guios    = self.GUIOs
        func_dsf = auxiliaries.diskSpaceFormatter

        #[2]: DB Status Display
        #---[2-1]: Market
        if type == 'market':
            location                = dbStatus['location']
            driveSize_total         = dbStatus['driveSize_total']
            driveSize_used          = dbStatus['driveSize_used']
            driveSize_free          = dbStatus['driveSize_free']
            size_total              = dbStatus['size_total']
            size_beforeCompression  = dbStatus['size_beforeCompression']
            size_afterCompression   = dbStatus['size_afterCompression']
            directory_text         = f"{location}"                                                                              if location is not None                                                     else "N/A"
            drive_text             = f"{func_dsf(driveSize_free)} [FREE] / {func_dsf(driveSize_total)} [TOTAL]"                 if driveSize_free is not None and driveSize_total is not None               else "N/A"
            sizeTotal_text         = f"{func_dsf(size_total)}"                                                                  if size_total is not None                                                   else "N/A"
            compression_text       = f"{func_dsf(size_beforeCompression)} [BEFORE] / {func_dsf(size_afterCompression)} [AFTER]" if size_beforeCompression is not None and size_afterCompression is not None else "N/A"
            guios["DBSTATUS_MDBDIRECTORYDISPLAYTEXT"].updateText(text   = directory_text,         textStyle = 'DEFAULT')
            guios["DBSTATUS_MDBDRIVEDISPLAYTEXT"].updateText(text       = drive_text,             textStyle = 'DEFAULT')
            guios["DBSTATUS_MDBSIZETOTALDISPLAYTEXT"].updateText(text   = sizeTotal_text,         textStyle = 'DEFAULT')
            guios["DBSTATUS_MDBCOMPRESSIONDISPLAYTEXT"].updateText(text = compression_text,       textStyle = 'DEFAULT')

        #---[2-2]: Account
        elif type == 'account':
            odbSize_text = f"{func_dsf(dbStatus[1])} [FREE] / {func_dsf(dbStatus[0])} [TOTAL]" if dbStatus is not None else "N/A"
            guios["DBSTATUS_ODBSIZEACCOUNTDISPLAYTEXT"].updateText(text = odbSize_text, textStyle = 'DEFAULT')
        #---[2-3]: Simulation
        elif type == 'simulation':
            odbSize_text = f"{func_dsf(dbStatus[1])} [FREE] / {func_dsf(dbStatus[0])} [TOTAL]" if dbStatus is not None else "N/A"
            guios["DBSTATUS_ODBSIZESIMULATIONDISPLAYTEXT"].updateText(text = odbSize_text, textStyle = 'DEFAULT')

        #---[2-4]: Neural Network
        elif type == 'neuralNetwork':
            odbSize_text = f"{func_dsf(dbStatus[1])} [FREE] / {func_dsf(dbStatus[0])} [TOTAL]" if dbStatus is not None else "N/A"
            guios["DBSTATUS_ODBSIZENEURALNETWORKDISPLAYTEXT"].updateText(text = odbSize_text, textStyle = 'DEFAULT')
    auxFunctions['_FARR_ONMDBCOMPRESSIONRESPONSE'] = __farr_onMDBCompressionResponse
    auxFunctions['_FARR_ONDBSTATUSREADRESPONSE']   = __farr_onDBStatusReadResponse
    auxFunctions['UPDATEDBSTATUSDISPLAY']          = __updateDBStatusDisplay

    #<Currency List>
    #---Filter
    def __onFilterUpdate():
        #[1]: Instances
        puVar = self.puVar
        guios = self.GUIOs
        currencies                = puVar['currencies']
        currencies_availabilities = puVar['currencies_availabilities']

        #[2]: Read Filters
        filter_symbol = guios["CURRENCYLIST_SEARCHTEXTINPUTBOX"].getText()
        filter_trading = None
        if   guios["CURRENCYLIST_FILTERSWITCH_TRADINGTRUE"].getStatus():  filter_trading = True
        elif guios["CURRENCYLIST_FILTERSWITCH_TRADINGFALSE"].getStatus(): filter_trading = False
        filter_collecting = None
        if   guios["CURRENCYLIST_FILTERSWITCH_COLLECTINGALL"].getStatus():    filter_collecting = 'all'
        elif guios["CURRENCYLIST_FILTERSWITCH_COLLECTINGSTREAM"].getStatus(): filter_collecting = 'stream'
        elif guios["CURRENCYLIST_FILTERSWITCH_COLLECTINGNONE"].getStatus():   filter_collecting = 'false'
        filter_sort = puVar['currencies_lastSortBy']

        #[3]: Filter symbols
        symbols          = list(currencies)
        symbols_filtered = list()
        for symbol in symbols:
            currencies_symbol = currencies[symbol]
            #[3-1]: Symbol Filter
            if filter_symbol not in symbol: 
                continue
            #[3-2]: Status Filter
            if filter_trading is not None:
                symbol_info_server = currencies_symbol['info_server']
                if filter_trading:
                    if symbol_info_server is None or symbol_info_server['status'] != 'TRADING':
                        continue
                else:
                    if symbol_info_server is not None and symbol_info_server['status'] == 'TRADING': 
                        continue
            #[3-3]: Collecting Filter
            if filter_collecting is not None:
                collecting = currencies_symbol['collecting']
                if filter_collecting == 'all':
                    if collecting != (True, True):
                        continue
                elif filter_collecting == 'stream':
                    if collecting != (True, False):
                        continue
                elif filter_collecting == 'false':
                    if collecting != (False, False):
                        continue
                else:
                    continue
            #[3-4]: Finally
            symbols_filtered.append(symbol)

        #[4]: Sort Symbols
        #---[4-1]: Index Sort
        if filter_sort == 'INDEX':              
            symbols_forSort = symbols_filtered

        #---[4-2]: Symbol Sort
        elif filter_sort == 'SYMBOL':             
            symbols_forSort = symbols_filtered

        #---[4-3]: First Interval Sort
        elif filter_sort == 'FIRSTINTERVAL':
            symbols_forSort = []
            for symbol in symbols_filtered:
                currencies_symbol = currencies[symbol]
                fdot_kl    = currencies_symbol['kline_firstOpenTS']
                fdot_depth = currencies_symbol['depth_firstOpenTS']
                fdot_at    = currencies_symbol['aggTrade_firstOpenTS']
                if fdot_kl    is None: fdot_kl    = float('inf')
                if fdot_depth is None: fdot_depth = float('inf')
                if fdot_at    is None: fdot_at    = float('inf')
                fdot = min(fdot_kl, fdot_depth, fdot_at)
                symbols_forSort.append((symbol, fdot))
                
        #---[4-4]: Kline Availability Sort
        elif filter_sort == 'AVAILABILITY_KL':
            symbols_forSort = []
            for symbol in symbols_filtered:
                avail = currencies_availabilities[symbol]['kline']
                avail = avail[0] if avail is not None else float('-inf')
                symbols_forSort.append((symbol, avail))

        #---[4-5]: Kline Availability Sort
        elif filter_sort == 'AVAILABILITY_DEPTH':
            symbols_forSort = []
            for symbol in symbols_filtered:
                avail = currencies_availabilities[symbol]['depth']
                avail = avail[0] if avail is not None else float('-inf')
                symbols_forSort.append((symbol, avail))

        #---[4-6]: Kline Availability Sort
        elif filter_sort == 'AVAILABILITY_AT':
            symbols_forSort = []
            for symbol in symbols_filtered:
                avail = currencies_availabilities[symbol]['aggTrade']
                avail = avail[0] if avail is not None else float('-inf')
                symbols_forSort.append((symbol, avail))

        #---[4-2]: Sort
        if   filter_sort == 'INDEX':              symbols_filteredAndSorted = symbols_forSort
        elif filter_sort == 'SYMBOL':             symbols_filteredAndSorted = sorted(symbols_forSort)
        elif filter_sort == 'FIRSTINTERVAL':      symbols_filteredAndSorted = [sp[0] for sp in sorted(symbols_forSort, key = lambda x: x[1])]
        elif filter_sort == 'AVAILABILITY_KL':    symbols_filteredAndSorted = [sp[0] for sp in sorted(symbols_forSort, key = lambda x: x[1], reverse = True)]
        elif filter_sort == 'AVAILABILITY_DEPTH': symbols_filteredAndSorted = [sp[0] for sp in sorted(symbols_forSort, key = lambda x: x[1], reverse = True)]
        elif filter_sort == 'AVAILABILITY_AT':    symbols_filteredAndSorted = [sp[0] for sp in sorted(symbols_forSort, key = lambda x: x[1], reverse = True)]

        #[5]: Selection Box Update
        guios["CURRENCYLIST_SELECTIONBOX"].setDisplayTargets(displayTargets = symbols_filteredAndSorted, resetViewPosition = False)
    auxFunctions['ONFILTERUPDATE'] = __onFilterUpdate

    #---List
    def __setList():
        #[1]: Instances
        vm    = self.visualManager
        puVar = self.puVar
        guios = self.GUIOs
        currencies                = puVar['currencies']
        currencies_availabilities = puVar['currencies_availabilities']

        #[2]: Selection List Formatting
        sl           = dict()
        nCurrencies  = len(currencies)
        for cIndex, symbol in enumerate(currencies):
            #[2-1]: Instances
            currencies_symbol                = currencies[symbol]
            currencies_availabilities_symbol = currencies_availabilities[symbol]

            #[2-2]: Index
            idx_text = f"{cIndex+1} / {nCurrencies}"
            idx_ts   = [('all', 'DEFAULT'),]

            #[2-3]: Symbol
            symbol_text = symbol
            symbol_ts   = [('all', 'DEFAULT'),]

            #[2-4]: Status
            info_server = currencies_symbol['info_server']
            status = None if info_server is None else info_server['status']
            status_text, status_ts = statusToString(vm = vm, status = status)

            #[2-5]: First Interval - Kline
            fi_kl = currencies_symbol['kline_firstOpenTS']
            fi_kl_text = firstIntervalToString(firstInterval = fi_kl)
            fi_kl_ts   = [('all', 'DEFAULT'),]

            #[2-6]: First Interval - Depth
            fi_depth = currencies_symbol['depth_firstOpenTS']
            fi_depth_text = firstIntervalToString(firstInterval = fi_depth)
            fi_depth_ts   = [('all', 'DEFAULT'),]

            #[2-7]: First Interval - AggTrade
            fi_at = currencies_symbol['aggTrade_firstOpenTS']
            fi_at_text = firstIntervalToString(firstInterval = fi_at)
            fi_at_ts   = [('all', 'DEFAULT'),]

            #[2-8]: Availability - Kline
            avail_kl = currencies_availabilities_symbol['kline']
            avail_kl_text, avail_kl_ts = availabilityToString(availability = avail_kl, precision = 1)

            #[2-9]: Availability - Depth
            avail_depth = currencies_availabilities_symbol['depth']
            avail_depth_text, avail_depth_ts = availabilityToString(availability = avail_depth, precision = 1)

            #[2-10]: Availability - AggTrade
            avail_at = currencies_availabilities_symbol['aggTrade']
            avail_at_text, avail_at_ts = availabilityToString(availability = avail_at, precision = 1)
            
            #[2-11]: Collecting
            collecting = currencies_symbol['collecting']
            collecting_text, collecting_ts = collectingToString(collecting = collecting)

            #[2-12]: Finally
            sl[symbol] = [{'text': idx_text,         'textStyles': idx_ts,         'textAnchor': 'CENTER'},
                          {'text': symbol_text,      'textStyles': symbol_ts,      'textAnchor': 'CENTER'},
                          {'text': status_text,      'textStyles': status_ts,      'textAnchor': 'CENTER'},
                          {'text': fi_kl_text,       'textStyles': fi_kl_ts,       'textAnchor': 'CENTER'},
                          {'text': fi_depth_text,    'textStyles': fi_depth_ts,    'textAnchor': 'CENTER'},
                          {'text': fi_at_text,       'textStyles': fi_at_ts,       'textAnchor': 'CENTER'},
                          {'text': avail_kl_text,    'textStyles': avail_kl_ts,    'textAnchor': 'CENTER'}, #Availabilities Are Updated Separately
                          {'text': avail_depth_text, 'textStyles': avail_depth_ts, 'textAnchor': 'CENTER'}, #Availabilities Are Updated Separately
                          {'text': avail_at_text,    'textStyles': avail_at_ts,    'textAnchor': 'CENTER'}, #Availabilities Are Updated Separately
                          {'text': collecting_text,  'textStyles': collecting_ts,  'textAnchor': 'CENTER'},
                          ]
            
        #[3]: Update Selection Box & Apply Filter
        guios["CURRENCYLIST_SELECTIONBOX"].setSelectionList(selectionList = sl, displayTargets = 'all', keepSelected = True, callSelectionUpdateFunction = False)
        self.pageAuxillaryFunctions['ONFILTERUPDATE']()
    def __computeCurrenciesAvailability(symbols = None, targets = None, updateSelectionBox = False):
        #[1]: Instances
        puVar   = self.puVar
        sb_esli = self.GUIOs["CURRENCYLIST_SELECTIONBOX"].editSelectionListItem
        currencies                = puVar['currencies']
        currencies_availabilities = puVar['currencies_availabilities']
        func_ats = availabilityToString

        #[2]: Update Targets
        if symbols is None: symbols = currencies.keys()
        if targets is None: targets = ['kline', 'depth', 'aggTrade']

        #[3]: Availabilities Update
        #---[3-1]: Current Interval End
        t_current = int(time.time())
        tEnd_current = auxiliaries.getNextIntervalTickTimestamp(intervalID = constants.KLINTERVAL, 
                                                                       timestamp  = t_current, 
                                                                       nTicks     = 0)-1
        
        #---[3-2]: Selection Box Item Index
        sbiIdx = {'kline': 6, 'depth': 7, 'aggTrade': 8}

        #---[3-2]: Availabilities Computation & SelectionBox Update (If Needed)
        for symbol in symbols:
            #[3-2-1]: Instances
            if symbol not in currencies_availabilities: currencies_availabilities[symbol] = {'kline': None, 'depth': None, 'aggTrade': None}
            currencies_symbol                = currencies[symbol]
            currencies_availabilities_symbol = currencies_availabilities[symbol]

            #[3-2-2]: Availabilities Computation
            for target in targets:
                #[3-2-2-1]: Previous Availability
                availability_prev = currencies_availabilities_symbol[target]

                #[3-2-2-2]: New Availability
                fi      = currencies_symbol[f'{target}_firstOpenTS']
                aRanges = currencies_symbol[f'{target}s_availableRanges']
                dRanges = currencies_symbol[f'{target}s_dummyRanges']
                if fi is None or aRanges is None:
                    availability = None
                else:
                    tWidth = tEnd_current-fi+1
                    aWidth = sum(aRange[1]-aRange[0]+1 for aRange in aRanges)
                    dWidth = sum(dRange[1]-dRange[0]+1 for dRange in dRanges) if dRanges else 0
                    if tWidth == aWidth: avail_total = 1.0
                    else:                avail_total = aWidth/tWidth
                    if   aWidth == 0.0 or dWidth == 0.0: dummyRate = None
                    elif aWidth == dWidth:               dummyRate = 1.0
                    else:                                dummyRate = dWidth/tWidth
                    availability = (avail_total, dummyRate)
                currencies_availabilities_symbol[target] = availability

                #[3-2-2-3]: SelectionBox Update
                if updateSelectionBox and availability_prev != availability:
                    avail_text, avail_ts = func_ats(availability = availability, precision = 1)
                    sbi_new = {'text':       avail_text,
                               'textStyles': avail_ts,
                               'textAnchor': 'CENTER'}
                    sb_esli(itemKey = symbol, item = sbi_new, columnIndex = sbiIdx[target])
    auxFunctions['COMPUTECURRENCIESAVAILABILITY'] = __computeCurrenciesAvailability
    auxFunctions['SETLIST']                       = __setList

    #---Information
    def __farr_onSetMarketDataCollectionResponse(responder, requestID, functionResult):
        #[1]: Response
        result  = functionResult['result']
        msg_str = functionResult['message']
        #[2]: Message Display
        msg_time_str = datetime.fromtimestamp(timestamp = time.time()).strftime("%Y/%m/%d %H:%M:%S")
        msg_color    = 'GREEN_LIGHT' if result else 'RED_LIGHT'
        self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = f"[{msg_time_str}] <DATAMANAGER> - {msg_str}", textStyle = msg_color)
    def __farr_onRefetchDummyResponse(responder, requestID, functionResult):
        #[1]: Response
        result  = functionResult['result']
        msg_str = functionResult['message']
        #[2]: Message Display
        msg_time_str = datetime.fromtimestamp(timestamp = time.time()).strftime("%Y/%m/%d %H:%M:%S")
        msg_color    = 'GREEN_LIGHT' if result else 'RED_LIGHT'
        self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = f"[{msg_time_str}] <DATAMANAGER> - {msg_str}", textStyle = msg_color)
        #[3]: Switch Reactivation
        if self.puVar['currencies_selected']: self.GUIOs["CURRENCYLIST_REFETCHDUMMYBUTTON"].activate()
    def __farr_onResetMarketDataResponse(responder, requestID, functionResult):
        #[1]: Response
        result  = functionResult['result']
        msg_str = functionResult['message']
        #[2]: Message Display
        msg_time_str = datetime.fromtimestamp(timestamp = time.time()).strftime("%Y/%m/%d %H:%M:%S")
        msg_color    = 'GREEN_LIGHT' if result else 'RED_LIGHT'
        self.GUIOs["MESSAGE_MESSAGEDISPLAYTEXT"].updateText(text = f"[{msg_time_str}] <DATAMANAGER> - {msg_str}", textStyle = msg_color)
        if self.puVar['currencies_selected']: self.GUIOs["CURRENCYLIST_RESETBUTTON"].activate()
    def __updateInformation():
        #[1]: Instances
        vm    = self.visualManager
        guios = self.GUIOs
        puVar = self.puVar
        currencies                = puVar['currencies']
        currencies_availabilities = puVar['currencies_availabilities']
        symbols    = list(puVar['currencies_selected'])
        nSymbols   = len(symbols)

        #[2]: GUIOs Update
        #---[2-1]: No Symbol Selected
        if nSymbols == 0:
            guios["CURRENCYLIST_SYMBOLDISPLAYTEXT"].updateText(text     = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_STATUSDISPLAYTEXT"].updateText(text     = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_COLLECTINGDISPLAYTEXT"].updateText(text = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_COLLECTINGHISTORICALSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
            guios["CURRENCYLIST_COLLECTINGSTREAMSWITCH"].setStatus(status = False, callStatusUpdateFunction = False)
            guios["CURRENCYLIST_COLLECTINGHISTORICALSWITCH"].deactivate()
            guios["CURRENCYLIST_COLLECTINGSTREAMSWITCH"].deactivate()
            guios["CURRENCYLIST_REFETCHDUMMYBUTTON"].deactivate()
            guios["CURRENCYLIST_RESETSWITCH"].deactivate()
            guios["CURRENCYLIST_RESETBUTTON"].deactivate()
            guios["CURRENCYLIST_FIRSTINTERVALKLDISPLAYTEXT"].updateText(text      = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_FIRSTINTERVALDEPTHDISPLAYTEXT"].updateText(text   = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_FIRSTINTERVALATDISPLAYTEXT"].updateText(text      = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_AVAILABLERANGESKLDISPLAYTEXT"].updateText(text    = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_AVAILABILITYKLDISPLAYTEXT"].updateText(text       = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_AVAILABLERANGESDEPTHDISPLAYTEXT"].updateText(text = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_AVAILABILITYDEPTHDISPLAYTEXT"].updateText(text    = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_AVAILABLERANGESATDISPLAYTEXT"].updateText(text    = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_AVAILABILITYATDISPLAYTEXT"].updateText(text       = "-", textStyle = 'DEFAULT')

        #---[2-2]: One Symbol Selected
        elif nSymbols == 1:
            symbol = symbols[0]
            currencies_symbol                = currencies[symbol]
            currencies_availabilities_symbol = currencies_availabilities[symbol]
            #[2-2-1]: Symbol
            guios["CURRENCYLIST_SYMBOLDISPLAYTEXT"].updateText(text = symbol)

            #[2-2-2]: Status
            info_server = currencies_symbol['info_server']
            status = None if info_server is None else info_server['status']
            status_text, status_ts = statusToString(vm = vm, status = status)
            guios["CURRENCYLIST_STATUSDISPLAYTEXT"].updateText(text = status_text, textStyle = status_ts)

            #[2-2-3]: Collecting
            collectingStream, collectingHistorical = currencies_symbol['collecting']
            collecting_text, collecting_ts = collectingToString(collecting = currencies_symbol['collecting'])
            guios["CURRENCYLIST_COLLECTINGDISPLAYTEXT"].updateText(text = collecting_text, textStyle = collecting_ts)
            guios["CURRENCYLIST_COLLECTINGSTREAMSWITCH"].setStatus(status     = collectingStream,     callStatusUpdateFunction = False)
            guios["CURRENCYLIST_COLLECTINGHISTORICALSWITCH"].setStatus(status = collectingHistorical, callStatusUpdateFunction = False)
            guios["CURRENCYLIST_COLLECTINGSTREAMSWITCH"].activate()
            if collectingStream: guios["CURRENCYLIST_COLLECTINGHISTORICALSWITCH"].activate()
            else:                guios["CURRENCYLIST_COLLECTINGHISTORICALSWITCH"].deactivate()

            #[2-2-4]: Refetch Dummy
            guios["CURRENCYLIST_REFETCHDUMMYBUTTON"].activate()

            #[2-2-5]: Reset
            guios["CURRENCYLIST_RESETSWITCH"].activate()
            guios["CURRENCYLIST_RESETBUTTON"].deactivate()

            #[2-2-6]: First Intervals
            fi_kl    = currencies_symbol['kline_firstOpenTS']
            fi_depth = currencies_symbol['depth_firstOpenTS']
            fi_at    = currencies_symbol['aggTrade_firstOpenTS']
            fi_kl_text    = firstIntervalToString(firstInterval = fi_kl)
            fi_depth_text = firstIntervalToString(firstInterval = fi_depth)
            fi_at_text    = firstIntervalToString(firstInterval = fi_at)
            guios["CURRENCYLIST_FIRSTINTERVALKLDISPLAYTEXT"].updateText(text    = fi_kl_text)
            guios["CURRENCYLIST_FIRSTINTERVALDEPTHDISPLAYTEXT"].updateText(text = fi_depth_text)
            guios["CURRENCYLIST_FIRSTINTERVALATDISPLAYTEXT"].updateText(text    = fi_at_text)

            #[2-2-7]: Available Ranges
            aRanges_kl    = currencies_symbol['klines_availableRanges']
            aRanges_depth = currencies_symbol['depths_availableRanges']
            aRanges_at    = currencies_symbol['aggTrades_availableRanges']
            guios["CURRENCYLIST_AVAILABLERANGESKLDISPLAYTEXT"].updateText(text    = aRangesToString(availableRanges = aRanges_kl))
            guios["CURRENCYLIST_AVAILABLERANGESDEPTHDISPLAYTEXT"].updateText(text = aRangesToString(availableRanges = aRanges_depth))
            guios["CURRENCYLIST_AVAILABLERANGESATDISPLAYTEXT"].updateText(text    = aRangesToString(availableRanges = aRanges_at))

            #[2-2-8]: Availabilities
            avail_kl    = currencies_availabilities_symbol['kline']
            avail_depth = currencies_availabilities_symbol['depth']
            avail_at    = currencies_availabilities_symbol['aggTrade']
            avail_kl_text,    avail_kl_ts    = availabilityToString(availability = avail_kl)
            avail_depth_text, avail_depth_ts = availabilityToString(availability = avail_depth)
            avail_at_text,    avail_at_ts    = availabilityToString(availability = avail_at)
            guios["CURRENCYLIST_AVAILABILITYKLDISPLAYTEXT"].updateText(text    = avail_kl_text,    textStyle = avail_kl_ts)
            guios["CURRENCYLIST_AVAILABILITYDEPTHDISPLAYTEXT"].updateText(text = avail_depth_text, textStyle = avail_depth_ts)
            guios["CURRENCYLIST_AVAILABILITYATDISPLAYTEXT"].updateText(text    = avail_at_text,    textStyle = avail_at_ts)

        #---[2-3]: More Than One Symbols Selected
        else:
            guios["CURRENCYLIST_SYMBOLDISPLAYTEXT"].updateText(text = f"{symbols[0]} and {nSymbols-1} Others")
            collectingStream     = all(currencies[symbol]['collecting'][0] for symbol in symbols)
            collectingHistorical = all(currencies[symbol]['collecting'][1] for symbol in symbols)
            collecting_text, collecting_ts = collectingToString(collecting = (collectingStream, collectingHistorical))
            guios["CURRENCYLIST_COLLECTINGDISPLAYTEXT"].updateText(text = collecting_text, textStyle = collecting_ts)
            guios["CURRENCYLIST_COLLECTINGSTREAMSWITCH"].setStatus(status     = collectingStream,     callStatusUpdateFunction = False)
            guios["CURRENCYLIST_COLLECTINGHISTORICALSWITCH"].setStatus(status = collectingHistorical, callStatusUpdateFunction = False)
            guios["CURRENCYLIST_COLLECTINGSTREAMSWITCH"].activate()
            if collectingStream: guios["CURRENCYLIST_COLLECTINGHISTORICALSWITCH"].activate()
            else:                guios["CURRENCYLIST_COLLECTINGHISTORICALSWITCH"].deactivate()
            guios["CURRENCYLIST_REFETCHDUMMYBUTTON"].activate()
            guios["CURRENCYLIST_RESETSWITCH"].activate()
            guios["CURRENCYLIST_RESETBUTTON"].deactivate()
            guios["CURRENCYLIST_STATUSDISPLAYTEXT"].updateText(text               = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_FIRSTINTERVALKLDISPLAYTEXT"].updateText(text      = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_FIRSTINTERVALDEPTHDISPLAYTEXT"].updateText(text   = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_FIRSTINTERVALATDISPLAYTEXT"].updateText(text      = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_AVAILABLERANGESKLDISPLAYTEXT"].updateText(text    = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_AVAILABILITYKLDISPLAYTEXT"].updateText(text       = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_AVAILABLERANGESDEPTHDISPLAYTEXT"].updateText(text = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_AVAILABILITYDEPTHDISPLAYTEXT"].updateText(text    = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_AVAILABLERANGESATDISPLAYTEXT"].updateText(text    = "-", textStyle = 'DEFAULT')
            guios["CURRENCYLIST_AVAILABILITYATDISPLAYTEXT"].updateText(text       = "-", textStyle = 'DEFAULT')
    auxFunctions['_FARR_ONSETMARKETDATACOLLECTIONRESPONSE'] = __farr_onSetMarketDataCollectionResponse
    auxFunctions['_FARR_ONREFETCHDUMMYRESPONSE']            = __farr_onRefetchDummyResponse
    auxFunctions['_FARR_ONRESETMARKETDATARESPONSE']         = __farr_onResetMarketDataResponse
    auxFunctions['UPDATEINFORMATION'] = __updateInformation

    #Return the generated functions
    return auxFunctions
#AUXILALRY FUNCTIONS END ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------