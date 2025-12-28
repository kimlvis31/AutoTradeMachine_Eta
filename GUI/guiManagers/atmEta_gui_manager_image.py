import pyglet
import os
from PIL import Image, ImageDraw

_IMAGECODETABLE = {'passiveGraphics_typeA_styleA_DEFAULT': '00x00x00xS00',
                   
                   'passiveGraphics_wrapperTypeA_styleA_DEFAULT': '00xS00x00xS00',
                   
                   'passiveGraphics_wrapperTypeB_styleA_DEFAULT': '00xS01x00xS00',
                   
                   'passiveGraphics_wrapperTypeC_styleA_DEFAULT': '00xS02x00xS00',
                   
                   'passiveGraphics_wrapperTypeC_styleB_DEFAULT': '00xS02x01xS00',
                   
                   'textBox_typeA_styleA_DEFAULT':   '01x00x00xS00',
                   'textBox_typeA_styleA_HIGHLIGHT': '01x00x00xS01',
                   'textBox_typeA_styleB_DEFAULT':   '01x00x01xS00',
                   'textBox_typeA_styleB_HIGHLIGHT': '01x00x01xS01',
                   
                   'imageBox_typeA_styleA_DEFAULT': '02x00x00xS00',
                   
                   'button_typeA_styleA_DEFAULT':      '03x00x00xS00',
                   'button_typeA_styleA_HOVERED':      '03x00x00xS01',
                   'button_typeA_styleA_PRESSED':      '03x00x00xS02',
                   'button_typeA_styleA_INACTIVEMASK': '03x00x00xSIM',
                   
                   'button_typeA_styleB_DEFAULT':      '03x00x01xS00',
                   'button_typeA_styleB_HOVERED':      '03x00x01xS01',
                   'button_typeA_styleB_PRESSED':      '03x00x01xS02',
                   'button_typeA_styleB_INACTIVEMASK': '03x00x01xSIM',
                   
                   'button_typeB_styleA_DEFAULT':      '03x01x00xS00',
                   'button_typeB_styleA_HOVERED':      '03x01x00xS01',
                   'button_typeB_styleA_PRESSED':      '03x01x00xS02',
                   'button_typeB_styleA_INACTIVEMASK': '03x01x00xSIM',
                   
                   'button_typeB_styleB_DEFAULT':      '03x01x01xS00',
                   'button_typeB_styleB_HOVERED':      '03x01x01xS01',
                   'button_typeB_styleB_PRESSED':      '03x01x01xS02',
                   'button_typeB_styleB_INACTIVEMASK': '03x01x01xSIM',
                   
                   'button_typeB_styleC_DEFAULT':      '03x01x02xS00',
                   'button_typeB_styleC_HOVERED':      '03x01x02xS01',
                   'button_typeB_styleC_PRESSED':      '03x01x02xS02',
                   'button_typeB_styleC_INACTIVEMASK': '03x01x02xSIM',
                   
                   'switch_typeA_styleA_F_DEFAULT':     '04x00x00_SxS00',
                   'switch_typeA_styleA_F_HOVERED':     '04x00x00_SxS01',
                   'switch_typeA_styleA_F_PRESSED':     '04x00x00_SxS02',
                   'switch_typeA_styleA_B_DEFAULT':     '04x00x00_BxS00',
                   'switch_typeA_styleA_B_HOVERED':     '04x00x00_BxS01',
                   'switch_typeA_styleA_B_PRESSED':     '04x00x00_BxS02',
                   'switch_typeA_styleA_INACTIVEMASK':  '04x00x00_SxSIM',
                   
                   'switch_typeB_styleA_F_DEFAULT@ON':  '04x01x00_SxS00T',
                   'switch_typeB_styleA_F_HOVERED@ON':  '04x01x00_SxS01T',
                   'switch_typeB_styleA_F_PRESSED@ON':  '04x01x00_SxS02T',
                   'switch_typeB_styleA_F_DEFAULT@OFF': '04x01x00_SxS00F',
                   'switch_typeB_styleA_F_HOVERED@OFF': '04x01x00_SxS01F',
                   'switch_typeB_styleA_F_PRESSED@OFF': '04x01x00_SxS02F',
                   'switch_typeB_styleA_B_DEFAULT':     '04x01x00_BxONxS00',
                   'switch_typeB_styleA_B_HOVERED':     '04x01x00_BxONxS01',
                   'switch_typeB_styleA_B_PRESSED':     '04x01x00_BxONxS02',
                   'switch_typeB_styleA_INACTIVEMASK':  '04x01x00_SxSIM',
                   
                   'switch_typeC_styleA_DEFAULT@ON':   '04x02x00xS00T',
                   'switch_typeC_styleA_HOVERED@ON':   '04x02x00xS01T',
                   'switch_typeC_styleA_PRESSED@ON':   '04x02x00xS02T',
                   'switch_typeC_styleA_DEFAULT@OFF':  '04x02x00xS00F',
                   'switch_typeC_styleA_HOVERED@OFF':  '04x02x00xS01F',
                   'switch_typeC_styleA_PRESSED@OFF':  '04x02x00xS02F',
                   'switch_typeC_styleA_INACTIVEMASK': '04x02x00xSIM',
                   
                   'switch_typeC_styleB_DEFAULT@ON':   '04x02x01xS00T',
                   'switch_typeC_styleB_HOVERED@ON':   '04x02x01xS01T',
                   'switch_typeC_styleB_PRESSED@ON':   '04x02x01xS02T',
                   'switch_typeC_styleB_DEFAULT@OFF':  '04x02x01xS00F',
                   'switch_typeC_styleB_HOVERED@OFF':  '04x02x01xS01F',
                   'switch_typeC_styleB_PRESSED@OFF':  '04x02x01xS02F',
                   'switch_typeC_styleB_INACTIVEMASK': '04x02x01xSIM',
                   
                   'slider_typeA_styleA_S_DEFAULT':      '05x00x00_SxS00',
                   'slider_typeA_styleA_S_HOVERED':      '05x00x00_SxS01',
                   'slider_typeA_styleA_S_PRESSED':      '05x00x00_SxS02',
                   'slider_typeA_styleA_B_DEFAULT':      '05x00x00_BxS00',
                   'slider_typeA_styleA_B_HOVERED':      '05x00x00_BxS01',
                   'slider_typeA_styleA_B_PRESSED':      '05x00x00_BxS02',
                   'slider_typeA_styleA_S_INACTIVEMASK': '05x00x00_SxSIM',
                   'slider_typeA_styleA_B_INACTIVEMASK': '05x00x00_BxSIM',
                   
                   'scrollBar_typeA_styleA_F_DEFAULT':    '06x00x00_SxS00',
                   'scrollBar_typeA_styleA_F_HOVERED':    '06x00x00_SxS01',
                   'scrollBar_typeA_styleA_F_PRESSED':    '06x00x00_SxS02',
                   'scrollBar_typeA_styleA_B_DEFAULT':    '06x00x00_BxS00',
                   'scrollBar_typeA_styleA_B_HOVERED':    '06x00x00_BxS01',
                   'scrollBar_typeA_styleA_B_PRESSED':    '06x00x00_BxS02',
                   'scrollBar_typeA_styleA_INACTIVEMASK': '06x00x00xSIM',
                   
                   'textInputBox_typeA_RAW_INACTIVEMASK':    '07x00xDFxSIM',
                   'textInputBox_typeA_styleA_DEFAULT':      '07x00x00xS00',
                   'textInputBox_typeA_styleA_HOVERED':      '07x00x00xS01',
                   'textInputBox_typeA_styleA_PRESSED':      '07x00x00xS02',
                   'textInputBox_typeA_styleA_INACTIVEMASK': '07x00x00xSIM',
                   
                   'selectionBox_typeA_styleA_DEFAULT':      '08x00x00xS00',
                   'selectionBox_typeA_styleA_HOVERED':      '08x00x00xS01',
                   'selectionBox_typeA_styleA_PRESSED':      '08x00x00xS02',
                   'selectionBox_typeA_styleA_INACTIVEMASK': '08x00x00xSIM',
                   
                   'selectionBox_typeA_styleB_DEFAULT':      '08x00x01xS00',
                   'selectionBox_typeA_styleB_HOVERED':      '08x00x01xS01',
                   'selectionBox_typeA_styleB_PRESSED':      '08x00x01xS02',
                   'selectionBox_typeA_styleB_INACTIVEMASK': '08x00x01xSIM',
                   
                   'selectionBox_typeB_styleA_DEFAULTC':     '08x01x00xS00',
                   'selectionBox_typeB_styleA_HOVEREDC':     '08x01x00xS01',
                   'selectionBox_typeB_styleA_PRESSEDC':     '08x01x00xS02',
                   'selectionBox_typeB_styleA_DEFAULTO':     '08x01x00xS10',
                   'selectionBox_typeB_styleA_HOVEREDO':     '08x01x00xS11',
                   'selectionBox_typeB_styleA_PRESSEDO':     '08x01x00xS12',
                   'selectionBox_typeB_styleA_INACTIVEMASK': '08x01x00xSIM',
                   
                   'selectionBox_typeB_styleB_DEFAULTC':     '08x01x01xS00',
                   'selectionBox_typeB_styleB_HOVEREDC':     '08x01x01xS01',
                   'selectionBox_typeB_styleB_PRESSEDC':     '08x01x01xS02',
                   'selectionBox_typeB_styleB_DEFAULTO':     '08x01x01xS10',
                   'selectionBox_typeB_styleB_HOVEREDO':     '08x01x01xS11',
                   'selectionBox_typeB_styleB_PRESSEDO':     '08x01x01xS12',
                   'selectionBox_typeB_styleB_INACTIVEMASK': '08x01x01xSIM',
                   
                   'selectionBox_typeC_styleA_DEFAULT':      '08x02x00xS00',
                   'selectionBox_typeC_styleA_HOVERED':      '08x02x00xS01',
                   'selectionBox_typeC_styleA_PRESSED':      '08x02x00xS02',
                   'selectionBox_typeC_styleA_INACTIVEMASK': '08x02x00xSIM',
                   
                   'selectionBox_typeC_styleB_DEFAULT':      '08x02x01xS00',
                   'selectionBox_typeC_styleB_HOVERED':      '08x02x01xS01',
                   'selectionBox_typeC_styleB_PRESSED':      '08x02x01xS02',
                   'selectionBox_typeC_styleB_INACTIVEMASK': '08x02x01xSIM',
                   
                   'LED_typeA_styleA_DEFAULT': '09x00x00_S00',
                   'LED_typeA_styleA_LED':     '09x00x00_SLS', #SLS: Static-LightSource
                   
                   'LED_typeA_styleB_DEFAULT': '09x00x01_S00',
                   'LED_typeA_styleB_LED':     '09x00x01_SLS', #SLS: Static-LightSource
                   
                   'gaugeBar_typeA_styleA_DEFAULT': '10x00x00_S00',
                   'gaugeBar_typeA_styleA_GAUGE':   '10x00x00_SLS', #SLS: Static-LightSource
                   
                   'gaugeBar_typeA_styleB_DEFAULT': '10x00x01_S00',
                   'gaugeBar_typeA_styleB_GAUGE':   '10x00x01_SLS', #SLS: Static-LightSource
                   
                   'subPageBox_typeA_styleA': '11x00x00_S00',
                   
                   'chartDrawer_typeA_styleA_displayBoxFrame':                     'S00x00x00_S00',
                   'chartDrawer_typeA_styleA_displayBoxFrameInteractable_DEFAULT': 'S00x00x00_S10',
                   'chartDrawer_typeA_styleA_displayBoxFrameInteractable_HOVERED': 'S00x00x00_S11',
                   'chartDrawer_typeA_styleA_displayBoxFrameInteractable_PRESSED': 'S00x00x00_S12',
                   'chartDrawer_typeA_styleA_klinesLoadingCover':                  'S00x00x00_S20',
                   
                   'dailyReportViewer_typeA_styleA_displayBoxFrame':                     'S01x00x00_S00',
                   'dailyReportViewer_typeA_styleA_displayBoxFrameInteractable_DEFAULT': 'S01x00x00_S10',
                   'dailyReportViewer_typeA_styleA_displayBoxFrameInteractable_HOVERED': 'S01x00x00_S11',
                   'dailyReportViewer_typeA_styleA_displayBoxFrameInteractable_PRESSED': 'S01x00x00_S12',
                   'dailyReportViewer_typeA_styleA_dataLoadingCover':                    'S01x00x00_S20',
                   
                   'hourlyReportViewer_typeA_styleA_displayBoxFrame':                     'S02x00x00_S00',
                   'hourlyReportViewer_typeA_styleA_displayBoxFrameInteractable_DEFAULT': 'S02x00x00_S10',
                   'hourlyReportViewer_typeA_styleA_displayBoxFrameInteractable_HOVERED': 'S02x00x00_S11',
                   'hourlyReportViewer_typeA_styleA_displayBoxFrameInteractable_PRESSED': 'S02x00x00_S12',
                   'hourlyReportViewer_typeA_styleA_dataLoadingCover':                    'S02x00x00_S20',
                   
                   'neuralNetworkViewer_typeA_styleA_displayBoxFrame':                     'S03x00x00_S00',
                   'neuralNetworkViewer_typeA_styleA_displayBoxFrameInteractable_DEFAULT': 'S03x00x00_S10',
                   'neuralNetworkViewer_typeA_styleA_displayBoxFrameInteractable_HOVERED': 'S03x00x00_S11',
                   'neuralNetworkViewer_typeA_styleA_displayBoxFrameInteractable_PRESSED': 'S03x00x00_S12',
                   'neuralNetworkViewer_typeA_styleA_dataLoadingCover':                    'S03x00x00_S20',
                   }


#IMAGE MANAGER OBJECT -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class imageManager:
    def __init__(self, path_project, guiConfig):
        print("\nInitializing Image Manager")
        self.guiConfig = guiConfig
        self.imageAddress = dict()
        self.loadedImages = list()
        
        self.path_project = path_project

        #Read Image Data located at 'path_PROJECT/GUI/imgs' Folder
        for folderName in ('rsc', 'sysGen', 'rsd'):
            path_folder = os.path.join(self.path_project, 'GUI', 'imgs', folderName)
            #If the folder exists, read images in the folder
            if (os.path.isdir(path_folder) == True):
                files = os.listdir(os.path.join(self.path_project, 'GUI', 'imgs', folderName))
                for fileName in files:
                    path_file = os.path.join(self.path_project, 'GUI', 'imgs', folderName, fileName)
                    if (os.path.isfile(path_file) == True):
                        try:    self.imageAddress[fileName] = os.path.join(self.path_project, 'GUI', 'imgs', folderName, fileName)
                        except: print(r" Corrupted or unexpected file detected while attempting to load an image from 'imgs{:s}': '{:s}'".format(folderName, fileName))
            #If the folder does not exist, create the folder
            else: os.mkdir(path_folder)

        #Generate Dummy Transparent Image if wasn't loaded
        if not('#dti#.png' in self.imageAddress.keys()):
            pilImage = Image.new(mode = "RGBA", size = (1, 1))
            pilDraw = ImageDraw.Draw(pilImage)
            pilDraw.line(xy = (0, 0, 0, 0), fill = (0, 0, 0, 0))
            pilImage.save(os.path.join(self.path_project, 'GUI', 'imgs', 'sysGen', '#dti#.png'))
            self.imageAddress['#dti#.png'] = os.path.join(self.path_project, 'GUI', 'imgs', 'sysGen', '#dti#.png')

        #Image Load Result Print
        print(" * {:d} image files loaded!".format(len(self.imageAddress)))
        print("Image Manager Initialization Complete!")

    def getImage(self, imageName, resize = None):
        if (imageName in self.imageAddress.keys()):
            if (resize != None): self.__loadResizedImage(imageName, resize)
            else:                self.loadedImages.append({'imageName': imageName, 'pygletImage': pyglet.image.load(self.imageAddress[imageName])})
            return self.loadedImages[-1]['pygletImage']
        else: return None

    def getImageByCode(self, imageCode, scaledWidth, scaledHeight, objectSpecificCode = None, reloadIndex = None):
        if (objectSpecificCode == None): imageName = "{:s}@{:d}x{:d}#{:s}.png".format(_IMAGECODETABLE[imageCode], round(scaledWidth), round(scaledHeight), self.guiConfig['GUITheme'])
        else:                            imageName = "{:s}@{:d}x{:d}x{:s}#{:s}.png".format(_IMAGECODETABLE[imageCode], round(scaledWidth), round(scaledHeight), objectSpecificCode, self.guiConfig['GUITheme'])
        if not(imageName in self.imageAddress.keys()): 
            self.__generateImage(imageCode, round(scaledWidth), round(scaledHeight), objectSpecificCode, 'LIGHT')
            self.__generateImage(imageCode, round(scaledWidth), round(scaledHeight), objectSpecificCode, 'DARK')
        if (reloadIndex != None):
            loadIndex = reloadIndex
            self.loadedImages[reloadIndex] = {'imageName': imageName, 'pygletImage': pyglet.image.load(self.imageAddress[imageName])}
        else:
            loadIndex = len(self.loadedImages)
            self.loadedImages.append({'imageName': imageName, 'pygletImage': pyglet.image.load(self.imageAddress[imageName])})
        return (self.loadedImages[loadIndex]['pygletImage'], loadIndex)
    
    def getImageByLoadIndex(self, loadIndex):
        return (self.loadedImages[loadIndex]['pygletImage'], loadIndex)

    def on_GUIThemeUpdate(self):
        if   (self.guiConfig['GUITheme'] == 'LIGHT'): guiTheme_prev = 'DARK'
        elif (self.guiConfig['GUITheme'] == 'DARK'):  guiTheme_prev = 'LIGHT'
        themeIdentifier_current = '#'+self.guiConfig['GUITheme']
        themeIdentifier_prev    = '#'+guiTheme_prev
        for index, loadedImage in enumerate(self.loadedImages):
            if (themeIdentifier_prev in loadedImage['imageName']): 
                self.loadedImages[index]['imageName']   = loadedImage['imageName'].replace(themeIdentifier_prev, themeIdentifier_current)
                self.loadedImages[index]['pygletImage'] = pyglet.image.load(self.imageAddress[loadedImage['imageName']])
        
    def __generateImage(self, imageCode, scaledWidth, scaledHeight, objectSpecificCode, guiTheme):
        igMSAA = self.guiConfig['ImageGenMSAA']
        pilImage = Image.new(mode = "RGBA", size = (scaledWidth * igMSAA, scaledHeight * igMSAA))
        pilDraw = ImageDraw.Draw(pilImage); pilDraw.rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = (0, 0, 0, 0), width = 0, outline = (0, 0, 0, 0))

        codeSplit = imageCode.split("_")
        objectName = codeSplit[0]; objectType = codeSplit[1]; objectStyle = codeSplit[2]; restDefiner = codeSplit[3:]

        if (objectName == "passiveGraphics"):
            if (objectType == "wrapperTypeA"):
                if (objectStyle == "styleA"):
                    objectSpecificCodeSplit = objectSpecificCode.split("_")
                    if (restDefiner == ['DEFAULT']):
                        if   (guiTheme == 'LIGHT'):
                            color_fill = (0, 0, 0, 0); outlineWidth = int(objectSpecificCodeSplit[0]); outlineColor = (100, 100, 100, 255); radius = int(objectSpecificCodeSplit[1]); corners = (True, True, True, True); textBoxWidth = int(objectSpecificCodeSplit[2]); topOffset = int(objectSpecificCodeSplit[3])
                            pilDraw.rounded_rectangle(xy = (0, topOffset * igMSAA, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                            pilDraw.rectangle(xy = (round(scaledWidth/2-textBoxWidth/2) * igMSAA, topOffset * igMSAA, round(scaledWidth/2+textBoxWidth/2) * igMSAA, (outlineWidth + topOffset) * igMSAA), fill = (0, 0, 0, 0), width = 0)
                        elif (guiTheme == 'DARK'):
                            color_fill = (0, 0, 0, 0); outlineWidth = int(objectSpecificCodeSplit[0]); outlineColor = (200, 200, 200, 255); radius = int(objectSpecificCodeSplit[1]); corners = (True, True, True, True); textBoxWidth = int(objectSpecificCodeSplit[2]); topOffset = int(objectSpecificCodeSplit[3])
                            pilDraw.rounded_rectangle(xy = (0, topOffset * igMSAA, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                            pilDraw.rectangle(xy = (round(scaledWidth/2-textBoxWidth/2) * igMSAA, topOffset * igMSAA, round(scaledWidth/2+textBoxWidth/2) * igMSAA, (outlineWidth + topOffset) * igMSAA), fill = (0, 0, 0, 0), width = 0)
            elif (objectType == "wrapperTypeB"):
                if (objectStyle == "styleA"):
                    objectSpecificCodeSplit = objectSpecificCode.split("_")
                    if (restDefiner == ['DEFAULT']):
                        color_fill = (0, 0, 0, 0); lineWidth = int(objectSpecificCodeSplit[0]); textBoxWidth = int(objectSpecificCodeSplit[1])
                        if (guiTheme == 'LIGHT'):  lineColor = (100, 100, 100, 255)
                        elif (guiTheme == 'DARK'): lineColor = (200, 200, 200, 255)
                        pilDraw.line(xy = (0, round(scaledHeight/2) * igMSAA, scaledWidth * igMSAA, round(scaledHeight/2) * igMSAA), fill = lineColor, width = lineWidth * igMSAA)
                        pilDraw.rectangle(xy = (round(scaledWidth/2-textBoxWidth/2) * igMSAA, 0, round(scaledWidth/2+textBoxWidth/2) * igMSAA, scaledHeight * igMSAA), fill = (0, 0, 0, 0), width = 0)
            elif (objectType == "wrapperTypeC"):
                if (objectStyle == "styleA"):
                    objectSpecificCodeSplit = objectSpecificCode.split("_")
                    if (restDefiner == ['DEFAULT']):
                        color_fill = (0, 0, 0, 0); lineWidth = int(objectSpecificCodeSplit[0]); textBoxWidth = int(objectSpecificCodeSplit[1])
                        if   (guiTheme == 'LIGHT'): lineColor = (100, 100, 100, 255)
                        elif (guiTheme == 'DARK'):  lineColor = (200, 200, 200, 255)
                        pilDraw.rectangle(xy = (0, (scaledHeight-lineWidth)*igMSAA, scaledWidth*igMSAA,  scaledHeight*igMSAA),                    fill = lineColor,    width = 0)
                        pilDraw.rectangle(xy = (0, 0,                               textBoxWidth*igMSAA, round(scaledHeight-lineWidth) * igMSAA), fill = (0, 0, 0, 0), width = 0)
                elif (objectStyle == "styleB"):
                    objectSpecificCodeSplit = objectSpecificCode.split("_")
                    if (restDefiner == ['DEFAULT']):
                        color_fill = (0, 0, 0, 0); lineWidth = int(objectSpecificCodeSplit[0]); textBoxWidth = int(objectSpecificCodeSplit[1])
                        if   (guiTheme == 'LIGHT'): lineColor = (120, 120, 120, 255)
                        elif (guiTheme == 'DARK'):  lineColor = (160, 160, 160, 255)
                        pilDraw.rectangle(xy = (0, (scaledHeight-lineWidth)*igMSAA, scaledWidth*igMSAA,  scaledHeight*igMSAA),                    fill = lineColor,    width = 0)
                        pilDraw.rectangle(xy = (0, 0,                               textBoxWidth*igMSAA, round(scaledHeight-lineWidth) * igMSAA), fill = (0, 0, 0, 0), width = 0)
        elif (objectName == "textBox"):
            if (objectType == "typeA"):
                if (objectStyle == "styleA"):
                    radius = int(scaledHeight/2); corners = (True, True, True, True)
                    if (restDefiner[0] == 'DEFAULT'):
                        outlineWidth = 0; outlineColor = (0, 0, 0, 0)
                        if   (guiTheme == 'LIGHT'): color_fill = (230, 230, 230, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 30,  30,  30, 255)
                    elif (restDefiner[0] == 'HIGHLIGHT'):
                        outlineWidth = 3; outlineColor = ( 50, 150, 200, 255)
                        if   (guiTheme == 'LIGHT'): color_fill = (230, 230, 230, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 30,  30,  30, 255)
                    pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                elif (objectStyle == "styleB"):
                    radius = int(scaledHeight/2); corners = (True, True, True, True)
                    if (restDefiner[0] == 'DEFAULT'):
                        outlineWidth = 0; outlineColor = (0, 0, 0, 0)
                        if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255)
                    elif (restDefiner[0] == 'HIGHLIGHT'):
                        outlineWidth = 3; outlineColor = ( 50, 150, 200, 255)
                        if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255)
                    pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
        elif (objectName == "imageBox"):
            if (objectType == "typeA"):
                if (objectStyle == "styleA"):
                    #---DARK MODE
                    if (restDefiner == ['DEFAULT']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (255, 255, 255, 255); outlineWidth = 2; outlineColor = (50, 50, 50, 255); radius = 10; corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = (10, 10, 10, 255); outlineWidth = 2; outlineColor = (200, 200, 200, 255); radius = 10; corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
        elif (objectName == "button"):
            if (objectType == "typeA"):
                #Style A
                if (objectStyle == "styleA"):
                    outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth, scaledHeight])/2); corners = (True, True, True, True)
                    if (restDefiner == ['DEFAULT']):
                        if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 30,  30,  30, 255)
                    elif (restDefiner == ['HOVERED']):
                        if   (guiTheme == 'LIGHT'): color_fill = (255, 255, 255, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255)
                    elif (restDefiner == ['PRESSED']):
                        if   (guiTheme == 'LIGHT'): color_fill = (150, 150, 150, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 10,  10,  10, 255)
                    elif (restDefiner == ['INACTIVEMASK']): color_fill = (255, 255, 255, 100)
                    pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                #Style B
                elif (objectStyle == "styleB"):
                    outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth, scaledHeight])/4); corners = (True, True, True, True)
                    if (restDefiner == ['DEFAULT']):
                        if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 30,  30,  30, 255)
                    elif (restDefiner == ['HOVERED']):
                        if   (guiTheme == 'LIGHT'): color_fill = (255, 255, 255, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255)
                    elif (restDefiner == ['PRESSED']):
                        if   (guiTheme == 'LIGHT'): color_fill = (150, 150, 150, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 10,  10,  10, 255)
                    elif (restDefiner == ['INACTIVEMASK']): color_fill = (255, 255, 255, 100)
                    pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
            elif (objectType == "typeB"):
                if (objectStyle == "styleA"):
                    outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth, scaledHeight])/2); corners = (True, True, True, True)
                    if (restDefiner == ['DEFAULT']):
                        if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 30,  30,  30, 255)
                    elif (restDefiner == ['HOVERED']):
                        if   (guiTheme == 'LIGHT'): color_fill = (255, 255, 255, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255)
                    elif (restDefiner == ['PRESSED']):
                        if   (guiTheme == 'LIGHT'): color_fill = (150, 150, 150, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 10,  10,  10, 255)
                    elif (restDefiner == ['INACTIVEMASK']): color_fill = (255, 255, 255, 100)
                    pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                elif (objectStyle == "styleB"):
                    outlineWidth = 1; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth, scaledHeight])/4); corners = (True, True, True, True)
                    if (restDefiner == ['DEFAULT']):
                        if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 30,  30,  30, 255)
                    elif (restDefiner == ['HOVERED']):
                        if   (guiTheme == 'LIGHT'): color_fill = (255, 255, 255, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255)
                    elif (restDefiner == ['PRESSED']):
                        if   (guiTheme == 'LIGHT'): color_fill = (150, 150, 150, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 10,  10,  10, 255)
                    elif (restDefiner == ['INACTIVEMASK']): color_fill = (255, 255, 255, 100)
                    pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
        elif (objectName == "switch"):
            if   (objectType == "typeA"):
                if (objectStyle == "styleA"):
                    if (restDefiner[0] == 'F'):
                        outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth, scaledHeight])/4); corners = (True, True, True, True)
                        if (restDefiner[1] == 'DEFAULT'):
                            if   (guiTheme == 'LIGHT'): color_fill = (230, 230, 230, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 60,  60,  60, 255)
                        elif (restDefiner[1] == 'HOVERED'):
                            if   (guiTheme == 'LIGHT'): color_fill = (250, 250, 250, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 70,  70,  70, 255)
                        elif (restDefiner[1] == 'PRESSED'):
                            if   (guiTheme == 'LIGHT'): color_fill = (210, 210, 210, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255)
                    elif (restDefiner[0] == 'B'):
                        outlineWidth = 5; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth, scaledHeight])/4+outlineWidth/2); corners = (True, True, True, True)
                        if (restDefiner[1] == 'DEFAULT'):
                            if   (guiTheme == 'LIGHT'): color_fill = (130, 130, 130, 255)
                            elif (guiTheme == 'DARK'):  color_fill = (220, 220, 220, 255)
                        elif (restDefiner[1] == 'HOVERED'):
                            if   (guiTheme == 'LIGHT'): color_fill = (150, 150, 150, 255)
                            elif (guiTheme == 'DARK'):  color_fill = (230, 230, 230, 255)
                        elif (restDefiner[1] == 'PRESSED'):
                            if   (guiTheme == 'LIGHT'): color_fill = (110, 110, 110, 255)
                            elif (guiTheme == 'DARK'):  color_fill = (200, 200, 200, 255)
                    elif (restDefiner[0] == 'INACTIVEMASK'):
                        color_fill = (255, 255, 255, 100); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth, scaledHeight])/4); corners = (True, True, True, True)
                    pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
            elif (objectType == "typeB"):
                if (objectStyle == "styleA"):
                    outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(scaledHeight / 2); corners = (True, True, True, True)
                    if (restDefiner[0] == 'F'):
                        if (restDefiner[1] == 'DEFAULT@ON'):
                            if   (guiTheme == 'LIGHT'): color_fill = (150, 230, 150, 255)
                            elif (guiTheme == 'DARK'):  color_fill = (150, 230, 150, 255)
                        elif (restDefiner[1] == 'HOVERED@ON'):
                            if   (guiTheme == 'LIGHT'): color_fill = (160, 240, 160, 255)
                            elif (guiTheme == 'DARK'):  color_fill = (160, 240, 160, 255)
                        elif (restDefiner[1] == 'PRESSED@ON'):
                            if   (guiTheme == 'LIGHT'): color_fill = (140, 220, 140, 255)
                            elif (guiTheme == 'DARK'):  color_fill = (140, 220, 140, 255)
                        elif (restDefiner[1] == 'DEFAULT@OFF'):
                            if   (guiTheme == 'LIGHT'): color_fill = (150, 150, 150, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 60,  60,  60, 255)
                        elif (restDefiner[1] == 'HOVERED@OFF'):
                            if   (guiTheme == 'LIGHT'): color_fill = (160, 160, 160, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 70,  70,  70, 255)
                        elif (restDefiner[1] == 'PRESSED@OFF'):
                            if   (guiTheme == 'LIGHT'): color_fill = (130, 130, 130, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255)
                    if (restDefiner[0] == 'B'):
                        if (restDefiner[1] == 'DEFAULT'):
                            if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255)
                            elif (guiTheme == 'DARK'):  color_fill = (240, 240, 240, 255)
                        elif (restDefiner[1] == 'HOVERED'):
                            if   (guiTheme == 'LIGHT'): color_fill = (255, 255, 255, 255)
                            elif (guiTheme == 'DARK'):  color_fill = (255, 255, 255, 255)
                        elif (restDefiner[1] == 'PRESSED'):
                            if   (guiTheme == 'LIGHT'): color_fill = (230, 230, 230, 255)
                            elif (guiTheme == 'DARK'):  color_fill = (230, 230, 230, 255)
                    if (restDefiner[0] == 'INACTIVEMASK'): color_fill = (255, 255, 255, 100)
                    pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
            elif (objectType == "typeC"):
                if (objectStyle == "styleA"):
                    objectSpecificCodeSplit = objectSpecificCode.split("_")
                    outlineWidth = int(objectSpecificCodeSplit[0]); outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth, scaledHeight])/4); corners = (True, True, True, True)
                    if (restDefiner[0] == 'DEFAULT@OFF'):
                        if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255); outlineColor = (240, 240, 240, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255); outlineColor = ( 40,  40,  40, 255)
                    elif (restDefiner[0] == 'HOVERED@OFF'):
                        if   (guiTheme == 'LIGHT'): color_fill = (255, 255, 255, 255); outlineColor = (255, 255, 255, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 50,  50,  50, 255); outlineColor = ( 50,  50,  50, 255)
                    elif (restDefiner[0] == 'PRESSED@OFF'):
                        if   (guiTheme == 'LIGHT'): color_fill = (150, 150, 150, 255); outlineColor = (150, 150, 150, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 10,  10,  10, 255); outlineColor = ( 10,  10,  10, 255)
                    elif (restDefiner[0] == 'DEFAULT@ON'):
                        if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255); outlineColor = (  0, 190, 255, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255); outlineColor = (180, 230,  30, 255)
                    elif (restDefiner[0] == 'HOVERED@ON'):
                        if   (guiTheme == 'LIGHT'): color_fill = (255, 255, 255, 255); outlineColor = (  0, 190, 255, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 50,  50,  50, 255); outlineColor = (180, 230,  30, 255)
                    elif (restDefiner[0] == 'PRESSED@ON'):
                        if   (guiTheme == 'LIGHT'): color_fill = (150, 150, 150, 255); outlineColor = (  0, 190, 255, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 10,  10,  10, 255); outlineColor = (180, 230,  30, 255)
                    elif (restDefiner[0] == 'INACTIVEMASK'): color_fill = (255, 255, 255, 100); outlineColor = (0, 0, 0, 0)
                    pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                elif (objectStyle == "styleB"):
                    objectSpecificCodeSplit = objectSpecificCode.split("_")
                    outlineWidth = int(objectSpecificCodeSplit[0]); radius = round(min([scaledWidth, scaledHeight])/2); corners = (True, True, True, True)
                    if (restDefiner[0] == 'DEFAULT@OFF'):
                        if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255); outlineColor = (240, 240, 240, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255); outlineColor = ( 40,  40,  40, 255)
                    elif (restDefiner[0] == 'HOVERED@OFF'):
                        if   (guiTheme == 'LIGHT'): color_fill = (255, 255, 255, 255); outlineColor = (255, 255, 255, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 50,  50,  50, 255); outlineColor = ( 50,  50,  50, 255)
                    elif (restDefiner[0] == 'PRESSED@OFF'):
                        if   (guiTheme == 'LIGHT'): color_fill = (150, 150, 150, 255); outlineColor = (150, 150, 150, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 10,  10,  10, 255); outlineColor = ( 10,  10,  10, 255)
                    elif (restDefiner[0] == 'DEFAULT@ON'):
                        if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255); outlineColor = (  0, 190, 255, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255); outlineColor = (180, 230,  30, 255)
                    elif (restDefiner[0] == 'HOVERED@ON'):
                        if   (guiTheme == 'LIGHT'): color_fill = (255, 255, 255, 255); outlineColor = (  0, 190, 255, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 50,  50,  50, 255); outlineColor = (180, 230,  30, 255)
                    elif (restDefiner[0] == 'PRESSED@ON'):
                        if   (guiTheme == 'LIGHT'): color_fill = (150, 150, 150, 255); outlineColor = (  0, 190, 255, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 10,  10,  10, 255); outlineColor = (180, 230,  30, 255)
                    elif (restDefiner[0] == 'INACTIVEMASK'): color_fill = (255, 255, 255, 100); outlineColor = (0, 0, 0, 0)
                    pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
        elif (objectName == "slider"):
            if (objectType == "typeA"):
                if (objectStyle == "styleA"):
                    if (restDefiner == ['S', 'DEFAULT']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (180, 180, 180, 255); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = 20; corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = ( 50,  50,  50, 255); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = 20; corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    elif (restDefiner == ['S', 'HOVERED']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (190, 190, 190, 255); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = 20; corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = ( 55,  55,  55, 255); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = 20; corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    elif (restDefiner == ['S', 'PRESSED']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (160, 160, 160, 255); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = 20; corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = ( 45,  45,  45, 255); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = 20; corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    if (restDefiner == ['B', 'DEFAULT']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (240, 240, 240, 255); outlineWidth = 2; outlineColor = (100, 100, 100, 255); radius = round(scaledWidth / 2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (1 * igMSAA, 1 * igMSAA, (scaledWidth-1) * igMSAA, (scaledHeight-1) * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = (180, 180, 180, 255); outlineWidth = 1; outlineColor = (30, 30, 30, 255); radius = round(scaledWidth / 2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, (scaledWidth-1) * igMSAA, (scaledHeight-1) * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    elif (restDefiner == ['B', 'HOVERED']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (255, 255, 255, 255); outlineWidth = 2; outlineColor = (100, 100, 100, 255); radius = round(scaledWidth / 2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (1 * igMSAA, 1 * igMSAA, (scaledWidth-1) * igMSAA, (scaledHeight-1) * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = (190, 190, 190, 255); outlineWidth = 1; outlineColor = (30, 30, 30, 255); radius = round(scaledWidth / 2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, (scaledWidth-1) * igMSAA, (scaledHeight-1) * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    elif (restDefiner == ['B', 'PRESSED']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (230, 230, 230, 255); outlineWidth = 2; outlineColor = (100, 100, 100, 255); radius = round(scaledWidth / 2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (1 * igMSAA, 1 * igMSAA, (scaledWidth-1) * igMSAA, (scaledHeight-1) * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = (170, 170, 170, 255); outlineWidth = 1; outlineColor = (30, 30, 30, 255); radius = round(scaledWidth / 2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, (scaledWidth-1) * igMSAA, (scaledHeight-1) * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    elif (restDefiner == ['S', 'INACTIVEMASK']):
                        color_fill = (255, 255, 255, 100); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = 10; corners = (True, True, True, True)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    elif (restDefiner == ['B', 'INACTIVEMASK']):
                        color_fill = (255, 255, 255, 100); outlineWidth = 1; outlineColor = (0, 0, 0, 0); radius = round(scaledWidth / 2); corners = (True, True, True, True)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
        elif (objectName == "scrollBar"):
            if (objectType == "typeA"):
                if (objectStyle == "styleA"):
                    if (restDefiner == ['F', 'DEFAULT']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (180, 180, 180, 255); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth,scaledHeight])/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = ( 50,  50,  50, 255); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth,scaledHeight])/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    elif (restDefiner == ['F', 'HOVERED']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (190, 190, 190, 255); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth,scaledHeight])/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = ( 55,  55,  55, 255); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth,scaledHeight])/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    elif (restDefiner == ['F', 'PRESSED']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (160, 160, 160, 255); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth,scaledHeight])/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = ( 45,  45,  45, 255); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth,scaledHeight])/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    if (restDefiner == ['B', 'DEFAULT']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (240, 240, 240, 255); outlineWidth = 3; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth,scaledHeight])/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = (180, 180, 180, 255); outlineWidth = 3; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth,scaledHeight])/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    elif (restDefiner == ['B', 'HOVERED']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (255, 255, 255, 255); outlineWidth = 3; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth,scaledHeight])/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = (190, 190, 190, 255); outlineWidth = 3; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth,scaledHeight])/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    elif (restDefiner == ['B', 'PRESSED']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (230, 230, 230, 255); outlineWidth = 3; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth,scaledHeight])/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = (170, 170, 170, 255); outlineWidth = 3; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth,scaledHeight])/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    elif (restDefiner == ['INACTIVEMASK']):
                        color_fill = (255, 255, 255, 100); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth,scaledHeight])/2); corners = (True, True, True, True)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
        elif (objectName == "textInputBox"):
            if (objectType == "typeA"):
                if (objectStyle == "RAW"):
                    #---INACTIVE MASK
                    if (restDefiner == ['INACTIVEMASK']):
                        color_fill = (255, 255, 255, 100); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = 0; corners = (True, True, True, True)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                if (objectStyle == "styleA"):
                    if (restDefiner == ['DEFAULT']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (220, 220, 220, 255); outlineWidth = 2; outlineColor = (140, 140, 140, 255); radius = round(scaledHeight/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = ( 20,  20,  20, 255); outlineWidth = 3; outlineColor = ( 50,  50,  50, 255); radius = round(scaledHeight/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    elif (restDefiner == ['HOVERED']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (230, 230, 230, 255); outlineWidth = 2; outlineColor = (150, 150, 150, 255); radius = round(scaledHeight/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = ( 25,  25,  25, 255); outlineWidth = 3; outlineColor = ( 55,  55,  55, 255); radius = round(scaledHeight/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    elif (restDefiner == ['PRESSED']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (210, 210, 210, 255); outlineWidth = 2; outlineColor = (130, 130, 130, 255); radius = round(scaledHeight/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = ( 15,  15,  15, 255); outlineWidth = 3; outlineColor = ( 45,  45,  45, 255); radius = round(scaledHeight/2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    elif (restDefiner == ['INACTIVEMASK']):
                        color_fill = (255, 255, 255, 100); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(scaledHeight/2); corners = (True, True, True, True)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
        elif (objectName == "selectionBox"):
            if (objectType == "typeA"):
                if (objectStyle == "styleA"):
                    outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCode); corners = (True, True, True, True)
                    if (restDefiner[0] == 'DEFAULT'):
                        if   (guiTheme == 'LIGHT'): color_fill = (230, 230, 230, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 30,  30,  30, 255)
                    elif (restDefiner[0] == 'HOVERED'):
                        if   (guiTheme == 'LIGHT'): color_fill = (235, 235, 235, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255)
                    elif (restDefiner[0] == 'INACTIVEMASK'): color_fill = (255, 255, 255, 100)
                    pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                elif (objectStyle == "styleB"):
                    outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCode); corners = (True, True, True, True)
                    if (restDefiner[0] == 'DEFAULT'):
                        if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255)
                    elif (restDefiner[0] == 'HOVERED'):
                        if   (guiTheme == 'LIGHT'): color_fill = (245, 245, 245, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 50,  50,  50, 255)
                    elif (restDefiner[0] == 'INACTIVEMASK'): color_fill = (255, 255, 255, 100)
                    pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
            elif (objectType == "typeB"):
                if (objectStyle == "styleA"):
                    objectSpecificCodeSplit = objectSpecificCode.split("_")
                    if (restDefiner[0] == 'DEFAULTO'):
                        outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCodeSplit[0]); corners = (True, True, True, True)
                        directionShapeLineWidth = 2; dsWidth = scaledWidth-int(objectSpecificCodeSplit[1]); dsHeight = scaledHeight; dsDrawOffset = int(objectSpecificCodeSplit[1])
                        if   (guiTheme == 'LIGHT'): color_fill = (230, 230, 230, 255); directionShapeLineColor = ( 40,  40,  40, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 30,  30,  30, 255); directionShapeLineColor = (220, 220, 220, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        pilDraw.line(xy = ((round(dsWidth*0.35)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA, 
                                            (round(dsWidth*0.50)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA, 
                                            (round(dsWidth*0.65)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA), 
                                        fill = directionShapeLineColor, width = directionShapeLineWidth * igMSAA)
                    elif (restDefiner[0] == 'HOVEREDO'):
                        outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCodeSplit[0]); corners = (True, True, True, True)
                        directionShapeLineWidth = 2; dsWidth = scaledWidth-int(objectSpecificCodeSplit[1]); dsHeight = scaledHeight; dsDrawOffset = int(objectSpecificCodeSplit[1])
                        if   (guiTheme == 'LIGHT'): color_fill = (235, 235, 235, 255); directionShapeLineColor = ( 40,  40,  40, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255); directionShapeLineColor = (220, 220, 220, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        pilDraw.line(xy = ((round(dsWidth*0.35)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA, 
                                            (round(dsWidth*0.50)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA, 
                                            (round(dsWidth*0.65)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA), 
                                        fill = directionShapeLineColor, width = directionShapeLineWidth * igMSAA)
                    elif (restDefiner[0] == 'PRESSEDO'):
                        outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCodeSplit[0]); corners = (True, True, True, True)
                        directionShapeLineWidth = 2; dsWidth = scaledWidth-int(objectSpecificCodeSplit[1]); dsHeight = scaledHeight; dsDrawOffset = int(objectSpecificCodeSplit[1])
                        if   (guiTheme == 'LIGHT'): color_fill = (200, 200, 200, 255); directionShapeLineColor = ( 40,  40,  40, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 15,  15,  15, 255); directionShapeLineColor = (220, 220, 220, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        pilDraw.line(xy = ((round(dsWidth*0.35)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA, 
                                            (round(dsWidth*0.50)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA, 
                                            (round(dsWidth*0.65)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA), 
                                        fill = directionShapeLineColor, width = directionShapeLineWidth * igMSAA)
                    elif (restDefiner[0] == 'DEFAULTC'):
                        outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCodeSplit[0]); corners = (True, True, True, True)
                        directionShapeLineWidth = 2; dsWidth = scaledWidth-int(objectSpecificCodeSplit[1]); dsHeight = scaledHeight; dsDrawOffset = int(objectSpecificCodeSplit[1])
                        if   (guiTheme == 'LIGHT'): color_fill = (230, 230, 230, 255); directionShapeLineColor = ( 40,  40,  40, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 30,  30,  30, 255); directionShapeLineColor = (220, 220, 220, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        pilDraw.line(xy = ((round(dsWidth*0.35)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA, 
                                            (round(dsWidth*0.50)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA, 
                                            (round(dsWidth*0.65)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA), 
                                        fill = directionShapeLineColor, width = directionShapeLineWidth * igMSAA)
                    elif (restDefiner[0] == 'HOVEREDC'):
                        outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCodeSplit[0]); corners = (True, True, True, True)
                        directionShapeLineWidth = 2; dsWidth = scaledWidth-int(objectSpecificCodeSplit[1]); dsHeight = scaledHeight; dsDrawOffset = int(objectSpecificCodeSplit[1])
                        if   (guiTheme == 'LIGHT'): color_fill = (235, 235, 235, 255); directionShapeLineColor = ( 40,  40,  40, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255); directionShapeLineColor = (220, 220, 220, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        pilDraw.line(xy = ((round(dsWidth*0.35)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA, 
                                            (round(dsWidth*0.50)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA, 
                                            (round(dsWidth*0.65)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA), 
                                        fill = directionShapeLineColor, width = directionShapeLineWidth * igMSAA)
                    elif (restDefiner[0] == 'PRESSEDC'):
                        outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCodeSplit[0]); corners = (True, True, True, True)
                        directionShapeLineWidth = 2; dsWidth = scaledWidth-int(objectSpecificCodeSplit[1]); dsHeight = scaledHeight; dsDrawOffset = int(objectSpecificCodeSplit[1])
                        if   (guiTheme == 'LIGHT'): color_fill = (200, 200, 200, 255); directionShapeLineColor = ( 40,  40,  40, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 15,  15,  15, 255); directionShapeLineColor = (220, 220, 220, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        pilDraw.line(xy = ((round(dsWidth*0.35)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA, 
                                            (round(dsWidth*0.50)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA, 
                                            (round(dsWidth*0.65)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA), 
                                        fill = directionShapeLineColor, width = directionShapeLineWidth * igMSAA)
                    elif (restDefiner[0] == 'INACTIVEMASK'):
                        color_fill = (255, 255, 255, 100); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCodeSplit[0]); corners = (True, True, True, True)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                elif (objectStyle == "styleB"):
                    objectSpecificCodeSplit = objectSpecificCode.split("_")
                    if (restDefiner[0] == 'DEFAULTO'):
                        outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCodeSplit[0]); corners = (True, True, True, True)
                        directionShapeLineWidth = 2; dsWidth = scaledWidth-int(objectSpecificCodeSplit[1]); dsHeight = scaledHeight; dsDrawOffset = int(objectSpecificCodeSplit[1])
                        if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255); directionShapeLineColor = ( 40,  40,  40, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255); directionShapeLineColor = (220, 220, 220, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        pilDraw.line(xy = ((round(dsWidth*0.35)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA, 
                                            (round(dsWidth*0.50)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA, 
                                            (round(dsWidth*0.65)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA), 
                                        fill = directionShapeLineColor, width = directionShapeLineWidth * igMSAA)
                    elif (restDefiner[0] == 'HOVEREDO'):
                        outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCodeSplit[0]); corners = (True, True, True, True)
                        directionShapeLineWidth = 2; dsWidth = scaledWidth-int(objectSpecificCodeSplit[1]); dsHeight = scaledHeight; dsDrawOffset = int(objectSpecificCodeSplit[1])
                        if   (guiTheme == 'LIGHT'): color_fill = (245, 245, 245, 255); directionShapeLineColor = ( 40,  40,  40, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 50,  50,  50, 255); directionShapeLineColor = (220, 220, 220, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        pilDraw.line(xy = ((round(dsWidth*0.35)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA, 
                                            (round(dsWidth*0.50)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA, 
                                            (round(dsWidth*0.65)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA), 
                                        fill = directionShapeLineColor, width = directionShapeLineWidth * igMSAA)
                    elif (restDefiner[0] == 'PRESSEDO'):
                        outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCodeSplit[0]); corners = (True, True, True, True)
                        directionShapeLineWidth = 2; dsWidth = scaledWidth-int(objectSpecificCodeSplit[1]); dsHeight = scaledHeight; dsDrawOffset = int(objectSpecificCodeSplit[1])
                        if   (guiTheme == 'LIGHT'): color_fill = (210, 210, 210, 255); directionShapeLineColor = ( 40,  40,  40, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 25,  25,  25, 255); directionShapeLineColor = (220, 220, 220, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        pilDraw.line(xy = ((round(dsWidth*0.35)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA, 
                                            (round(dsWidth*0.50)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA, 
                                            (round(dsWidth*0.65)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA), 
                                        fill = directionShapeLineColor, width = directionShapeLineWidth * igMSAA)
                    elif (restDefiner[0] == 'DEFAULTC'):
                        outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCodeSplit[0]); corners = (True, True, True, True)
                        directionShapeLineWidth = 2; dsWidth = scaledWidth-int(objectSpecificCodeSplit[1]); dsHeight = scaledHeight; dsDrawOffset = int(objectSpecificCodeSplit[1])
                        if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255); directionShapeLineColor = ( 40,  40,  40, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255); directionShapeLineColor = (220, 220, 220, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        pilDraw.line(xy = ((round(dsWidth*0.35)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA, 
                                            (round(dsWidth*0.50)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA, 
                                            (round(dsWidth*0.65)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA), 
                                        fill = directionShapeLineColor, width = directionShapeLineWidth * igMSAA)
                    elif (restDefiner[0] == 'HOVEREDC'):
                        outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCodeSplit[0]); corners = (True, True, True, True)
                        directionShapeLineWidth = 2; dsWidth = scaledWidth-int(objectSpecificCodeSplit[1]); dsHeight = scaledHeight; dsDrawOffset = int(objectSpecificCodeSplit[1])
                        if   (guiTheme == 'LIGHT'): color_fill = (245, 245, 245, 255); directionShapeLineColor = ( 40,  40,  40, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 50,  50,  50, 255); directionShapeLineColor = (220, 220, 220, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        pilDraw.line(xy = ((round(dsWidth*0.35)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA, 
                                            (round(dsWidth*0.50)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA, 
                                            (round(dsWidth*0.65)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA), 
                                        fill = directionShapeLineColor, width = directionShapeLineWidth * igMSAA)
                    elif (restDefiner[0] == 'PRESSEDC'):
                        outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCodeSplit[0]); corners = (True, True, True, True)
                        directionShapeLineWidth = 2; dsWidth = scaledWidth-int(objectSpecificCodeSplit[1]); dsHeight = scaledHeight; dsDrawOffset = int(objectSpecificCodeSplit[1])
                        if   (guiTheme == 'LIGHT'): color_fill = (210, 210, 210, 255); directionShapeLineColor = ( 40,  40,  40, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 25,  25,  25, 255); directionShapeLineColor = (220, 220, 220, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        pilDraw.line(xy = ((round(dsWidth*0.35)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA, 
                                            (round(dsWidth*0.50)+dsDrawOffset)*igMSAA, round(dsHeight*0.42)*igMSAA, 
                                            (round(dsWidth*0.65)+dsDrawOffset)*igMSAA, round(dsHeight*0.58)*igMSAA), 
                                        fill = directionShapeLineColor, width = directionShapeLineWidth * igMSAA)
                    elif (restDefiner[0] == 'INACTIVEMASK'):
                        color_fill = (255, 255, 255, 100); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCodeSplit[0]); corners = (True, True, True, True)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
            elif (objectType == "typeC"):
                if (objectStyle == "styleA"):
                    outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCode); corners = (True, True, True, True)
                    if (restDefiner[0] == 'DEFAULT'):
                        if   (guiTheme == 'LIGHT'): color_fill = (230, 230, 230, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 30,  30,  30, 255)
                    elif (restDefiner[0] == 'HOVERED'):
                        if   (guiTheme == 'LIGHT'): color_fill = (235, 235, 235, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255)
                    elif (restDefiner[0] == 'INACTIVEMASK'): color_fill = (255, 255, 255, 100)
                    pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                elif (objectStyle == "styleB"):
                    outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = int(objectSpecificCode); corners = (True, True, True, True)
                    if (restDefiner[0] == 'DEFAULT'):
                        if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255)
                    elif (restDefiner[0] == 'HOVERED'):
                        if   (guiTheme == 'LIGHT'): color_fill = (245, 245, 245, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 50,  50,  50, 255)
                    elif (restDefiner[0] == 'INACTIVEMASK'): color_fill = (255, 255, 255, 100)
                    pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
        elif (objectName == "LED"):
            if (objectType == "typeA"):
                if (objectStyle == "styleA"):
                    if (restDefiner == ['DEFAULT']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (0, 0, 0, 0); outlineWidth = 2; outlineColor = (240, 240, 240, 255); radius = round(min([scaledWidth, scaledHeight]) / 2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = (0, 0, 0, 0); outlineWidth = 2; outlineColor = ( 40,  40,  40, 255); radius = round(min([scaledWidth, scaledHeight]) / 2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    if (restDefiner == ['LED']):
                        color_fill = (255, 255, 255, 255); outlineWidth = 2; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth, scaledHeight]) / 2); corners = (True, True, True, True)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                elif (objectStyle == "styleB"):
                    if (restDefiner == ['DEFAULT']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (0, 0, 0, 0); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth, scaledHeight]) / 2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = (0, 0, 0, 0); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth, scaledHeight]) / 2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    if (restDefiner == ['LED']):
                        color_fill = (255, 255, 255, 255); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth, scaledHeight]) / 2); corners = (True, True, True, True)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
        elif (objectName == "gaugeBar"):
            if (objectType == "typeA"):
                if (objectStyle == "styleA"):
                    if (restDefiner == ['DEFAULT']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (215, 215, 215, 255); outlineWidth = 2; outlineColor = (230, 230, 230, 255); radius = round(min([scaledWidth, scaledHeight]) / 2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = ( 25,  25,  25, 255); outlineWidth = 2; outlineColor = ( 15,  15,  15, 255); radius = round(min([scaledWidth, scaledHeight]) / 2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    if (restDefiner == ['GAUGE']):
                        color_fill = (255, 255, 255, 255); outlineWidth = 2; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth, scaledHeight]) / 2); corners = (True, True, True, True)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                elif (objectStyle == "styleB"):
                    if (restDefiner == ['DEFAULT']):
                        if (guiTheme == 'LIGHT'):
                            color_fill = (215, 215, 215, 255); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth, scaledHeight]) / 2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                        elif (guiTheme == 'DARK'):
                            color_fill = ( 25,  25,  25, 255); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth, scaledHeight]) / 2); corners = (True, True, True, True)
                            pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
                    if (restDefiner == ['GAUGE']):
                        color_fill = (255, 255, 255, 255); outlineWidth = 0; outlineColor = (0, 0, 0, 0); radius = round(min([scaledWidth, scaledHeight]) / 2); corners = (True, True, True, True)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth * igMSAA, scaledHeight * igMSAA), fill = color_fill, width = outlineWidth * igMSAA, outline = outlineColor, radius = radius * igMSAA, corners = corners)
        elif (objectName == "subPageBox"):
            if (objectType == "typeA"):
                if (objectStyle == "styleA"):
                    objectSpecificCodeSplit = objectSpecificCode.split("_")
                    radius = int(objectSpecificCodeSplit[0])
                    if   (guiTheme == 'LIGHT'): color_fill1 = (220, 220, 220, 255); color_outline = (200, 200, 200, 255)
                    elif (guiTheme == 'DARK'):  color_fill1 = ( 20,  20,  20, 255); color_outline = ( 10,  10,  10, 255)
                    pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth*igMSAA, scaledHeight*igMSAA), fill = color_fill1, width = 3*igMSAA, outline = color_outline, radius = radius*igMSAA, corners = (True,True,True,True))
        elif (objectName == "chartDrawer"):
            if (objectType == "typeA"):
                if (objectStyle == "styleA"):
                    if (restDefiner[0] == 'displayBoxFrameInteractable'):
                        if (restDefiner[1] == 'DEFAULT'):
                            if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255)
                        elif (restDefiner[1] == 'HOVERED'):
                            if   (guiTheme == 'LIGHT'): color_fill = (255, 255, 255, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 50,  50,  50, 255)
                        elif (restDefiner[1] == 'PRESSED'):
                            if   (guiTheme == 'LIGHT'): color_fill = (150, 150, 150, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 10,  10,  10, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth*igMSAA, scaledHeight*igMSAA), fill = color_fill, width = 0, outline = (0,0,0,0), radius = 10*igMSAA, corners = (True,True,True,True))
                    elif (restDefiner[0] == 'displayBoxFrame'):
                        if   (guiTheme == 'LIGHT'): color_fill = (230, 230, 230, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 30,  30,  30, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth*igMSAA, scaledHeight*igMSAA), fill = color_fill, width = 0, outline = (0,0,0,0), radius = 10*igMSAA, corners = (True,True,True,True))
                    elif (restDefiner[0] == 'klinesLoadingCover'):
                        if   (guiTheme == 'LIGHT'): color_fill = (255, 255, 255, 150)
                        elif (guiTheme == 'DARK'):  color_fill = (  0,   0,   0, 150)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth*igMSAA, scaledHeight*igMSAA), fill = color_fill, width = 0, outline = (0,0,0,0), radius = 10*igMSAA, corners = (True,True,True,True))
        elif (objectName == "dailyReportViewer"):
            if (objectType == "typeA"):
                if (objectStyle == "styleA"):
                    if (restDefiner[0] == 'displayBoxFrameInteractable'):
                        if (restDefiner[1] == 'DEFAULT'):
                            if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255)
                        elif (restDefiner[1] == 'HOVERED'):
                            if   (guiTheme == 'LIGHT'): color_fill = (255, 255, 255, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 50,  50,  50, 255)
                        elif (restDefiner[1] == 'PRESSED'):
                            if   (guiTheme == 'LIGHT'): color_fill = (150, 150, 150, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 10,  10,  10, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth*igMSAA, scaledHeight*igMSAA), fill = color_fill, width = 0, outline = (0,0,0,0), radius = 10*igMSAA, corners = (True,True,True,True))
                    elif (restDefiner[0] == 'displayBoxFrame'):
                        if   (guiTheme == 'LIGHT'): color_fill = (230, 230, 230, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 30,  30,  30, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth*igMSAA, scaledHeight*igMSAA), fill = color_fill, width = 0, outline = (0,0,0,0), radius = 10*igMSAA, corners = (True,True,True,True))
                    elif (restDefiner[0] == 'dataLoadingCover'):
                        if   (guiTheme == 'LIGHT'): color_fill = (255, 255, 255, 150)
                        elif (guiTheme == 'DARK'):  color_fill = (  0,   0,   0, 150)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth*igMSAA, scaledHeight*igMSAA), fill = color_fill, width = 0, outline = (0,0,0,0), radius = 10*igMSAA, corners = (True,True,True,True))
        elif (objectName == "hourlyReportViewer"):
            if (objectType == "typeA"):
                if (objectStyle == "styleA"):
                    if (restDefiner[0] == 'displayBoxFrameInteractable'):
                        if (restDefiner[1] == 'DEFAULT'):
                            if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255)
                        elif (restDefiner[1] == 'HOVERED'):
                            if   (guiTheme == 'LIGHT'): color_fill = (255, 255, 255, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 50,  50,  50, 255)
                        elif (restDefiner[1] == 'PRESSED'):
                            if   (guiTheme == 'LIGHT'): color_fill = (150, 150, 150, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 10,  10,  10, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth*igMSAA, scaledHeight*igMSAA), fill = color_fill, width = 0, outline = (0,0,0,0), radius = 10*igMSAA, corners = (True,True,True,True))
                    elif (restDefiner[0] == 'displayBoxFrame'):
                        if   (guiTheme == 'LIGHT'): color_fill = (230, 230, 230, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 30,  30,  30, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth*igMSAA, scaledHeight*igMSAA), fill = color_fill, width = 0, outline = (0,0,0,0), radius = 10*igMSAA, corners = (True,True,True,True))
                    elif (restDefiner[0] == 'dataLoadingCover'):
                        if   (guiTheme == 'LIGHT'): color_fill = (255, 255, 255, 150)
                        elif (guiTheme == 'DARK'):  color_fill = (  0,   0,   0, 150)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth*igMSAA, scaledHeight*igMSAA), fill = color_fill, width = 0, outline = (0,0,0,0), radius = 10*igMSAA, corners = (True,True,True,True))
        elif (objectName == "neuralNetworkViewer"):
            if (objectType == "typeA"):
                if (objectStyle == "styleA"):
                    if (restDefiner[0] == 'displayBoxFrameInteractable'):
                        if (restDefiner[1] == 'DEFAULT'):
                            if   (guiTheme == 'LIGHT'): color_fill = (240, 240, 240, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 40,  40,  40, 255)
                        elif (restDefiner[1] == 'HOVERED'):
                            if   (guiTheme == 'LIGHT'): color_fill = (255, 255, 255, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 50,  50,  50, 255)
                        elif (restDefiner[1] == 'PRESSED'):
                            if   (guiTheme == 'LIGHT'): color_fill = (150, 150, 150, 255)
                            elif (guiTheme == 'DARK'):  color_fill = ( 10,  10,  10, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth*igMSAA, scaledHeight*igMSAA), fill = color_fill, width = 0, outline = (0,0,0,0), radius = 10*igMSAA, corners = (True,True,True,True))
                    elif (restDefiner[0] == 'displayBoxFrame'):
                        if   (guiTheme == 'LIGHT'): color_fill = (230, 230, 230, 255)
                        elif (guiTheme == 'DARK'):  color_fill = ( 30,  30,  30, 255)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth*igMSAA, scaledHeight*igMSAA), fill = color_fill, width = 0, outline = (0,0,0,0), radius = 10*igMSAA, corners = (True,True,True,True))
                    elif (restDefiner[0] == 'dataLoadingCover'):
                        if   (guiTheme == 'LIGHT'): color_fill = (255, 255, 255, 150)
                        elif (guiTheme == 'DARK'):  color_fill = (  0,   0,   0, 150)
                        pilDraw.rounded_rectangle(xy = (0, 0, scaledWidth*igMSAA, scaledHeight*igMSAA), fill = color_fill, width = 0, outline = (0,0,0,0), radius = 10*igMSAA, corners = (True,True,True,True))

        else: raise Exception("An Error Occured While Attempting the Generate An Image in Image Manager: Image Code '{:s}' is Not Recognizable".format(imageCode))

        #Resize the generated PIL image, save to the local drive, and save the file's full address in the 'self.imageAddress' dict
        pilImage_resized = pilImage.resize((scaledWidth, scaledHeight), Image.HAMMING)
        if (objectSpecificCode == None): imageName = "{:s}@{:d}x{:d}#{:s}.png".format(_IMAGECODETABLE[imageCode], scaledWidth, scaledHeight, guiTheme)
        else:                            imageName = "{:s}@{:d}x{:d}x{:s}#{:s}.png".format(_IMAGECODETABLE[imageCode], scaledWidth, scaledHeight, objectSpecificCode, guiTheme)
        pilImage_resized.save(os.path.join(self.path_project, 'GUI', 'imgs', 'sysGen', imageName))
        self.imageAddress[imageName] = os.path.join(self.path_project, 'GUI', 'imgs', 'sysGen', imageName) 

    def __loadResizedImage(self, imageName, newSize):
        resizedImgName = imageName.split(".")[0]+"_rsd_{:d}x{:d}.png".format(newSize[0],newSize[1])
        if not(resizedImgName in self.imageAddress.keys()):
            imag_orig = Image.open(os.path.join(self.path_project, 'GUI', 'imgs', 'rsc', imageName))
            imag_resized = imag_orig.resize(newSize, Image.HAMMING)
            imag_resized.save(os.path.join(self.path_project, 'GUI', 'imgs', 'rsd', resizedImgName))
            self.imageAddress[resizedImgName] = os.path.join(self.path_project, 'GUI', 'imgs', 'rsd', resizedImgName)
        self.loadedImages.append({'imageName': resizedImgName, 'pygletImage': pyglet.image.load(self.imageAddress[resizedImgName])})

#IMAGE MANAGER OBJECT END ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------