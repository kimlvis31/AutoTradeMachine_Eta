from GUI import atmEta_gui_TextPack

_SYSTEMFONT = {'ENG': 'Cascadia Mono', 'KOR': '맑은 고딕'}

_COLORTABLE = {'PAGEBACKGROUND': {'DARK': (20, 20, 20, 255), 'LIGHT': (220, 220, 220, 255)},
               
               'TEXT_WRAPPERBOX':  {'DARK': (240, 240, 240, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_WRAPPERBOX2': {'DARK': (200, 200, 200, 255), 'LIGHT': (120, 120, 120, 255)},
               
               'TEXT_BUTTON_DEFAULT':  {'DARK': (220, 220, 220, 255), 'LIGHT': ( 60,  60,  60, 255)},
               'TEXT_BUTTON_HOVERED':  {'DARK': (230, 230, 230, 255), 'LIGHT': ( 50,  50,  50, 255)},
               'TEXT_BUTTON_PRESSED':  {'DARK': (210, 210, 210, 255), 'LIGHT': ( 40,  40,  40, 255)},
               'TEXT_BUTTON_INACTIVE': {'DARK': (220, 220, 220, 255), 'LIGHT': ( 60,  60,  60, 255)},
               
               'TEXT_SWITCH_DEFAULT':  {'DARK': (220, 220, 220, 255), 'LIGHT': ( 60,  60,  60, 255)},
               'TEXT_SWITCH_HOVERED':  {'DARK': (230, 230, 230, 255), 'LIGHT': ( 50,  50,  50, 255)},
               'TEXT_SWITCH_PRESSED':  {'DARK': (210, 210, 210, 255), 'LIGHT': ( 40,  40,  40, 255)},
               'TEXT_SWITCH_INACTIVE': {'DARK': (220, 220, 220, 255), 'LIGHT': ( 60,  60,  60, 255)},
               
               'TEXT_TEXTBOX_DEFAULT':   {'DARK': (220, 220, 220, 255), 'LIGHT': ( 80,  80,  80, 255)},
               'TEXT_TEXTBOX_HIGHLIGHT': {'DARK': ( 50, 150, 200, 255), 'LIGHT': ( 50, 150, 200, 255)},
               
               'TEXT_INPUTBOX_DEFAULT':             {'DARK': (220, 220, 220, 255), 'LIGHT': ( 50,  50,  50, 255)},
               'TEXT_INPUTBOX_SELECTION':           {'DARK': (220, 220, 220, 255), 'LIGHT': ( 50,  50,  50, 255)},
               'TEXT_INPUTBOX_SELECTIONBACKGROUND': {'DARK': (255, 255, 255,  20), 'LIGHT': (  0,   0,   0,  30)},
               'TEXT_INPUTBOX_CAROT':               {'DARK': (150, 150, 150, 255), 'LIGHT': ( 50,  50,  50, 255)},
               
               'TEXT_SELECTIONBOX_DEFAULT': {'DARK': (220, 220, 220, 255), 'LIGHT': (100, 100, 100, 255)},
               
               'TEXT_CHARTDRAWER_DEFAULT':            {'DARK': (220, 220, 220, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_CHARTDRAWER_GRID':               {'DARK': (220, 220, 220, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_CHARTDRAWER_GRIDHEAVY':          {'DARK': (230, 230, 230, 255), 'LIGHT': ( 90,  90,  90, 255)},
               'TEXT_CHARTDRAWER_GUIDECONTENT':       {'DARK': (240, 240, 240, 255), 'LIGHT': ( 80,  80,  80, 255)},
               'TEXT_CHARTDRAWER_CONTENT_NAME':       {'DARK': (230, 230, 230, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_CHARTDRAWER_CONTENT_POSITIVE_1': {'DARK': (  0, 240,  80, 255), 'LIGHT': (  0, 220, 120, 255)},
               'TEXT_CHARTDRAWER_CONTENT_NEGATIVE_1': {'DARK': (240,  50,  50, 255), 'LIGHT': (240,  85,  85, 255)},
               'TEXT_CHARTDRAWER_CONTENT_NEUTRAL_1':  {'DARK': (200, 200, 200, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_CHARTDRAWER_CONTENT_POSITIVE_2': {'DARK': (255,  50,  50, 255), 'LIGHT': (255,  50,  50, 255)},
               'TEXT_CHARTDRAWER_CONTENT_NEGATIVE_2': {'DARK': (200, 200, 200, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_CHARTDRAWER_CONTENT_NEUTRAL_2':  {'DARK': (210, 210, 210, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_CHARTDRAWER_CONTENT_DEFAULT':    {'DARK': (220, 220, 220, 255), 'LIGHT': (100, 100, 100, 255)},
               
               'CHARTDRAWER_GRID':                         {'DARK': ( 50,  50,  50, 255), 'LIGHT': (200, 200, 200, 255)},
               'CHARTDRAWER_GRIDHEAVY':                    {'DARK': ( 60,  60,  60, 255), 'LIGHT': (190, 190, 190, 255)},
               'CHARTDRAWER_GUIDECONTENT':                 {'DARK': ( 70,  70,  70, 255), 'LIGHT': (180, 180, 180, 255)},
               'CHARTDRAWER_KLINECOLOR_TYPE1_INCREMENTAL': {'DARK': (100, 255, 100, 255), 'LIGHT': ( 80, 200, 150, 255)},
               'CHARTDRAWER_KLINECOLOR_TYPE1_DECREMENTAL': {'DARK': (255,  90, 100, 255), 'LIGHT': (240,  80,  80, 255)},
               'CHARTDRAWER_KLINECOLOR_TYPE1_NEUTRAL':     {'DARK': (200, 200, 200, 255), 'LIGHT': (100, 100, 100, 255)},
               'CHARTDRAWER_KLINECOLOR_TYPE2_INCREMENTAL': {'DARK': (255,  80,  80, 255), 'LIGHT': (255,  80, 100, 255)},
               'CHARTDRAWER_KLINECOLOR_TYPE2_DECREMENTAL': {'DARK': (100, 200, 255, 255), 'LIGHT': (100, 150, 255, 255)},
               'CHARTDRAWER_KLINECOLOR_TYPE2_NEUTRAL':     {'DARK': (200, 200, 200, 255), 'LIGHT': (100, 100, 100, 255)},
               'CHARTDRAWER_POSHOVERED':                   {'DARK': (255, 255, 255,  30), 'LIGHT': (  0,   0,   0,  30)},
               'CHARTDRAWER_POSSELECTED':                  {'DARK': (255, 255, 255,  60), 'LIGHT': (  0,   0,   0,  60)},
               
               'TEXT_DAILYREPORTVIEWER_DEFAULT':            {'DARK': (220, 220, 220, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_DAILYREPORTVIEWER_GRID':               {'DARK': (220, 220, 220, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_DAILYREPORTVIEWER_GRIDHEAVY':          {'DARK': (230, 230, 230, 255), 'LIGHT': ( 90,  90,  90, 255)},
               'TEXT_DAILYREPORTVIEWER_GUIDECONTENT':       {'DARK': (240, 240, 240, 255), 'LIGHT': ( 80,  80,  80, 255)},
               'TEXT_DAILYREPORTVIEWER_CONTENT_NAME':       {'DARK': (230, 230, 230, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_DAILYREPORTVIEWER_CONTENT_POSITIVE_1': {'DARK': (  0, 240,  80, 255), 'LIGHT': (  0, 220, 120, 255)},
               'TEXT_DAILYREPORTVIEWER_CONTENT_NEGATIVE_1': {'DARK': (240,  50,  50, 255), 'LIGHT': (240,  85,  85, 255)},
               'TEXT_DAILYREPORTVIEWER_CONTENT_NEUTRAL_1':  {'DARK': (200, 200, 200, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_DAILYREPORTVIEWER_CONTENT_POSITIVE_2': {'DARK': (255,  50,  50, 255), 'LIGHT': (255,  50,  50, 255)},
               'TEXT_DAILYREPORTVIEWER_CONTENT_NEGATIVE_2': {'DARK': (200, 200, 200, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_DAILYREPORTVIEWER_CONTENT_NEUTRAL_2':  {'DARK': (210, 210, 210, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_DAILYREPORTVIEWER_CONTENT_DEFAULT':    {'DARK': (220, 220, 220, 255), 'LIGHT': (100, 100, 100, 255)},
               
               'DAILYREPORTVIEWER_GRID':                         {'DARK': ( 50,  50,  50, 255), 'LIGHT': (200, 200, 200, 255)},
               'DAILYREPORTVIEWER_GRIDHEAVY':                    {'DARK': ( 60,  60,  60, 255), 'LIGHT': (190, 190, 190, 255)},
               'DAILYREPORTVIEWER_GUIDECONTENT':                 {'DARK': ( 70,  70,  70, 255), 'LIGHT': (180, 180, 180, 255)},
               'DAILYREPORTVIEWER_KLINECOLOR_TYPE1_INCREMENTAL': {'DARK': (  0, 240,  80, 255), 'LIGHT': (  0, 220, 120, 255)},
               'DAILYREPORTVIEWER_KLINECOLOR_TYPE1_DECREMENTAL': {'DARK': (240,  50,  50, 255), 'LIGHT': (240,  85,  85, 255)},
               'DAILYREPORTVIEWER_KLINECOLOR_TYPE1_NEUTRAL':     {'DARK': (200, 200, 200, 255), 'LIGHT': (100, 100, 100, 255)},
               'DAILYREPORTVIEWER_KLINECOLOR_TYPE2_INCREMENTAL': {'DARK': (255,  50,  50, 255), 'LIGHT': (255,  50,  50, 255)},
               'DAILYREPORTVIEWER_KLINECOLOR_TYPE2_DECREMENTAL': {'DARK': (  0,  45, 255, 255), 'LIGHT': (  0, 130, 255, 255)},
               'DAILYREPORTVIEWER_KLINECOLOR_TYPE2_NEUTRAL':     {'DARK': (200, 200, 200, 255), 'LIGHT': (100, 100, 100, 255)},
               'DAILYREPORTVIEWER_POSHOVERED':                   {'DARK': (255, 255, 255,  30), 'LIGHT': (  0,   0,   0,  30)},
               'DAILYREPORTVIEWER_POSSELECTED':                  {'DARK': (255, 255, 255,  60), 'LIGHT': (  0,   0,   0,  60)},
               
               'TEXT_HOURLYREPORTVIEWER_DEFAULT':            {'DARK': (220, 220, 220, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_HOURLYREPORTVIEWER_GRID':               {'DARK': (220, 220, 220, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_HOURLYREPORTVIEWER_GRIDHEAVY':          {'DARK': (230, 230, 230, 255), 'LIGHT': ( 90,  90,  90, 255)},
               'TEXT_HOURLYREPORTVIEWER_GUIDECONTENT':       {'DARK': (240, 240, 240, 255), 'LIGHT': ( 80,  80,  80, 255)},
               'TEXT_HOURLYREPORTVIEWER_CONTENT_NAME':       {'DARK': (230, 230, 230, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_HOURLYREPORTVIEWER_CONTENT_POSITIVE_1': {'DARK': (  0, 240,  80, 255), 'LIGHT': (  0, 220, 120, 255)},
               'TEXT_HOURLYREPORTVIEWER_CONTENT_NEGATIVE_1': {'DARK': (240,  50,  50, 255), 'LIGHT': (240,  85,  85, 255)},
               'TEXT_HOURLYREPORTVIEWER_CONTENT_NEUTRAL_1':  {'DARK': (200, 200, 200, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_HOURLYREPORTVIEWER_CONTENT_POSITIVE_2': {'DARK': (255,  50,  50, 255), 'LIGHT': (255,  50,  50, 255)},
               'TEXT_HOURLYREPORTVIEWER_CONTENT_NEGATIVE_2': {'DARK': (200, 200, 200, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_HOURLYREPORTVIEWER_CONTENT_NEUTRAL_2':  {'DARK': (210, 210, 210, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_HOURLYREPORTVIEWER_CONTENT_DEFAULT':    {'DARK': (220, 220, 220, 255), 'LIGHT': (100, 100, 100, 255)},
               
               'HOURLYREPORTVIEWER_GRID':                         {'DARK': ( 50,  50,  50, 255), 'LIGHT': (200, 200, 200, 255)},
               'HOURLYREPORTVIEWER_GRIDHEAVY':                    {'DARK': ( 60,  60,  60, 255), 'LIGHT': (190, 190, 190, 255)},
               'HOURLYREPORTVIEWER_GUIDECONTENT':                 {'DARK': ( 70,  70,  70, 255), 'LIGHT': (180, 180, 180, 255)},
               'HOURLYREPORTVIEWER_KLINECOLOR_TYPE1_INCREMENTAL': {'DARK': (  0, 240,  80, 255), 'LIGHT': (  0, 220, 120, 255)},
               'HOURLYREPORTVIEWER_KLINECOLOR_TYPE1_DECREMENTAL': {'DARK': (240,  50,  50, 255), 'LIGHT': (240,  85,  85, 255)},
               'HOURLYREPORTVIEWER_KLINECOLOR_TYPE1_NEUTRAL':     {'DARK': (200, 200, 200, 255), 'LIGHT': (100, 100, 100, 255)},
               'HOURLYREPORTVIEWER_KLINECOLOR_TYPE2_INCREMENTAL': {'DARK': (255,  50,  50, 255), 'LIGHT': (255,  50,  50, 255)},
               'HOURLYREPORTVIEWER_KLINECOLOR_TYPE2_DECREMENTAL': {'DARK': (  0,  45, 255, 255), 'LIGHT': (  0, 130, 255, 255)},
               'HOURLYREPORTVIEWER_KLINECOLOR_TYPE2_NEUTRAL':     {'DARK': (200, 200, 200, 255), 'LIGHT': (100, 100, 100, 255)},
               'HOURLYREPORTVIEWER_POSHOVERED':                   {'DARK': (255, 255, 255,  30), 'LIGHT': (  0,   0,   0,  30)},
               'HOURLYREPORTVIEWER_POSSELECTED':                  {'DARK': (255, 255, 255,  60), 'LIGHT': (  0,   0,   0,  60)},
               
               'TEXT_NEURALNETWORKVIEWER_DEFAULT':            {'DARK': (220, 220, 220, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_NEURALNETWORKVIEWER_CONTENT_NAME':       {'DARK': (230, 230, 230, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_NEURALNETWORKVIEWER_CONTENT_POSITIVE_1': {'DARK': (  0, 240,  80, 255), 'LIGHT': (  0, 220, 120, 255)},
               'TEXT_NEURALNETWORKVIEWER_CONTENT_NEGATIVE_1': {'DARK': (240,  50,  50, 255), 'LIGHT': (240,  85,  85, 255)},
               'TEXT_NEURALNETWORKVIEWER_CONTENT_NEUTRAL_1':  {'DARK': (200, 200, 200, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_NEURALNETWORKVIEWER_CONTENT_POSITIVE_2': {'DARK': (255,  50,  50, 255), 'LIGHT': (255,  50,  50, 255)},
               'TEXT_NEURALNETWORKVIEWER_CONTENT_NEGATIVE_2': {'DARK': (200, 200, 200, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_NEURALNETWORKVIEWER_CONTENT_NEUTRAL_2':  {'DARK': (210, 210, 210, 255), 'LIGHT': (100, 100, 100, 255)},
               'TEXT_NEURALNETWORKVIEWER_CONTENT_DEFAULT':    {'DARK': (220, 220, 220, 255), 'LIGHT': (100, 100, 100, 255)},
               
               'ICON_COLORING': {'DARK': (220, 220, 220, 255), 'LIGHT': (100, 100, 100, 255)},
               
               'SELECTIONBOX_HOVERED':      {'DARK': (255, 255, 255, 20),  'LIGHT': (  0,   0,   0,  10)},
               'SELECTIONBOX_SELECTED':     {'DARK': (255, 255, 255, 40),  'LIGHT': (  0,   0,   0,  20)},
               'SELECTIONBOX_HOVEREDSEL':   {'DARK': (255, 255, 255, 60),  'LIGHT': (  0,   0,   0,  30)},
               'SELECTIONBOX_PRESSED':      {'DARK': (  0,   0,   0, 60),  'LIGHT': (  0,   0,   0,  40)},
               'SELECTIONBOX_TITLEDIVIDER': {'DARK': (220, 220, 220, 255), 'LIGHT': ( 50,  50,  50, 255)},
               
               'TEXTCOLOR_RED':          {'DARK': (255,   0,   0, 255), 'LIGHT': (255,   0,   0, 255)},
               'TEXTCOLOR_RED_LIGHT':    {'DARK': (255,  67,  67, 255), 'LIGHT': (255,  67,  67, 255)},
               'TEXTCOLOR_RED_DARK':     {'DARK': (180,   0,   0, 255), 'LIGHT': (180,   0,   0, 255)},
               'TEXTCOLOR_ORANGE':       {'DARK': (255, 102,   0, 255), 'LIGHT': (255, 130,  45, 255)},
               'TEXTCOLOR_ORANGE_LIGHT': {'DARK': (255, 153,  83, 255), 'LIGHT': (255, 163, 101, 255)},
               'TEXTCOLOR_ORANGE_DARK':  {'DARK': (214,  87,   0, 255), 'LIGHT': (214,  87,   0, 255)},
               'TEXTCOLOR_YELLOW':       {'DARK': (255, 255,   0, 255), 'LIGHT': (255, 255,   0, 255)},
               'TEXTCOLOR_YELLOW_LIGHT': {'DARK': (255, 255,  91, 255), 'LIGHT': (255, 255, 155, 255)},
               'TEXTCOLOR_YELLOW_DARK':  {'DARK': (192, 187,   0, 255), 'LIGHT': (214, 209,   0, 255)},
               'TEXTCOLOR_GREEN':        {'DARK': (  0, 176,  80, 255), 'LIGHT': (  0, 162,  73, 255)},
               'TEXTCOLOR_GREEN_LIGHT':  {'DARK': (  0, 200,  30, 255), 'LIGHT': (  0, 208,  35, 255)},
               'TEXTCOLOR_GREEN_DARK':   {'DARK': (  0, 100,  45, 255), 'LIGHT': (  0, 100,  45, 255)},
               'TEXTCOLOR_BLUE':         {'DARK': (  0, 112, 192, 255), 'LIGHT': (  0, 112, 192, 255)},
               'TEXTCOLOR_BLUE_LIGHT':   {'DARK': ( 75, 178, 255, 255), 'LIGHT': ( 75, 178, 255, 255)},
               'TEXTCOLOR_BLUE_DARK':    {'DARK': (  0,  86, 150, 255), 'LIGHT': (  0,  86, 150, 255)},
               'TEXTCOLOR_VIOLET':       {'DARK': (112,  48, 160, 255), 'LIGHT': (112,  48, 160, 255)},
               'TEXTCOLOR_VIOLET_LIGHT': {'DARK': (163, 101, 209, 255), 'LIGHT': (163, 101, 209, 255)},
               'TEXTCOLOR_VIOLET_DARK':  {'DARK': ( 97,  41, 139, 255), 'LIGHT': ( 68,  29,  97, 255)},
               'TEXTCOLOR_CYAN':         {'DARK': (  0, 255, 255, 255), 'LIGHT': (  0, 196, 191, 255)},
               'TEXTCOLOR_CYAN_LIGHT':   {'DARK': (159, 255, 255, 255), 'LIGHT': (  0, 222, 217, 255)},
               'TEXTCOLOR_CYAN_DARK':    {'DARK': (  0, 158, 154, 255), 'LIGHT': (  0, 138, 135, 255)},
               'TEXTCOLOR_GREY':         {'DARK': (127, 127, 127, 255), 'LIGHT': (155, 155, 155, 255)},
               'TEXTCOLOR_GREY_LIGHT':   {'DARK': (167, 167, 167, 255), 'LIGHT': (180, 180, 180, 255)},
               'TEXTCOLOR_GREY_DARK':    {'DARK': ( 63,  63,  63, 255), 'LIGHT': (130, 130, 130, 255)}}

_BASETEXTSTYLES = {'wrapperBox_default': {'LIGHT': {'DEFAULT': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_WRAPPERBOX']['LIGHT'],  'anchor_x': 'center', 'anchor_y': 'center'}},
                                          'DARK':  {'DEFAULT': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_WRAPPERBOX']['DARK'],   'anchor_x': 'center', 'anchor_y': 'center'}}},
                                                          
                   'wrapperBox_default2': {'LIGHT': {'DEFAULT': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_WRAPPERBOX2']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'}},
                                           'DARK':  {'DEFAULT': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_WRAPPERBOX2']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'}}},
                                                          
                   'button_default': {'LIGHT': {'DEFAULT':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_BUTTON_DEFAULT']['LIGHT'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                'HOVERED':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_BUTTON_HOVERED']['LIGHT'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                'PRESSED':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_BUTTON_PRESSED']['LIGHT'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                'INACTIVE': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_BUTTON_INACTIVE']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'}},
                                      'DARK':  {'DEFAULT':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_BUTTON_DEFAULT']['DARK'],   'anchor_x': 'center', 'anchor_y': 'center'},
                                                'HOVERED':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_BUTTON_HOVERED']['DARK'],   'anchor_x': 'center', 'anchor_y': 'center'},
                                                'PRESSED':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_BUTTON_PRESSED']['DARK'],   'anchor_x': 'center', 'anchor_y': 'center'},
                                                'INACTIVE': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_BUTTON_INACTIVE']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'}}},
                                                               
                   'switch_default': {'LIGHT': {'DEFAULT':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_SWITCH_DEFAULT']['LIGHT'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                'HOVERED':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_SWITCH_HOVERED']['LIGHT'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                'PRESSED':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_SWITCH_PRESSED']['LIGHT'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                'INACTIVE': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_SWITCH_INACTIVE']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'}},
                                      'DARK':  {'DEFAULT':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_SWITCH_DEFAULT']['DARK'],   'anchor_x': 'center', 'anchor_y': 'center'},
                                                'HOVERED':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_SWITCH_HOVERED']['DARK'],   'anchor_x': 'center', 'anchor_y': 'center'},
                                                'PRESSED':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_SWITCH_PRESSED']['DARK'],   'anchor_x': 'center', 'anchor_y': 'center'},
                                                'INACTIVE': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_SWITCH_INACTIVE']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'}}},
                                                               
                   'textBox_default': {'LIGHT': {'DEFAULT':   {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_TEXTBOX_DEFAULT']['LIGHT'],   'anchor_x': 'center', 'anchor_y': 'center',
                                                               'selectionColor': _COLORTABLE['TEXT_INPUTBOX_SELECTION']['LIGHT'], 'selectionBackgroundColor': _COLORTABLE['TEXT_INPUTBOX_SELECTIONBACKGROUND']['LIGHT'], 'caretColor': _COLORTABLE['TEXT_INPUTBOX_CAROT']['LIGHT']},
                                                 'HIGHLIGHT': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_TEXTBOX_HIGHLIGHT']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center',
                                                               'selectionColor': _COLORTABLE['TEXT_INPUTBOX_SELECTION']['LIGHT'], 'selectionBackgroundColor': _COLORTABLE['TEXT_INPUTBOX_SELECTIONBACKGROUND']['LIGHT'], 'caretColor': _COLORTABLE['TEXT_INPUTBOX_CAROT']['LIGHT']}},
                                       'DARK':  {'DEFAULT':   {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_TEXTBOX_DEFAULT']['DARK'],   'anchor_x': 'center', 'anchor_y': 'center',
                                                               'selectionColor': _COLORTABLE['TEXT_INPUTBOX_SELECTION']['DARK'], 'selectionBackgroundColor': _COLORTABLE['TEXT_INPUTBOX_SELECTIONBACKGROUND']['DARK'], 'caretColor': _COLORTABLE['TEXT_INPUTBOX_CAROT']['DARK']},
                                                 'HIGHLIGHT': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_TEXTBOX_HIGHLIGHT']['DARK'], 'anchor_x': 'center', 'anchor_y': 'center',
                                                               'selectionColor': _COLORTABLE['TEXT_INPUTBOX_SELECTION']['DARK'], 'selectionBackgroundColor': _COLORTABLE['TEXT_INPUTBOX_SELECTIONBACKGROUND']['DARK'], 'caretColor': _COLORTABLE['TEXT_INPUTBOX_CAROT']['DARK']}}},
                                                                              
                   'textInputBox_default': {'LIGHT': {'DEFAULT': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_INPUTBOX_DEFAULT']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center',
                                                                  'selectionColor': _COLORTABLE['TEXT_INPUTBOX_SELECTION']['LIGHT'], 'selectionBackgroundColor': _COLORTABLE['TEXT_INPUTBOX_SELECTIONBACKGROUND']['LIGHT'], 'caretColor': _COLORTABLE['TEXT_INPUTBOX_CAROT']['LIGHT']}},
                                            'DARK':  {'DEFAULT': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_INPUTBOX_DEFAULT']['DARK'], 'anchor_x': 'center', 'anchor_y': 'center',
                                                                  'selectionColor': _COLORTABLE['TEXT_INPUTBOX_SELECTION']['DARK'], 'selectionBackgroundColor': _COLORTABLE['TEXT_INPUTBOX_SELECTIONBACKGROUND']['DARK'], 'caretColor': _COLORTABLE['TEXT_INPUTBOX_CAROT']['DARK']}}},

                   'selectionBox_default': {'LIGHT': {'DEFAULT': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_SELECTIONBOX_DEFAULT']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'}},
                                            'DARK':  {'DEFAULT': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_SELECTIONBOX_DEFAULT']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'}}},
                                            
                   'chartDrawer_default': {'LIGHT': {'DEFAULT':            {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_DEFAULT']['LIGHT'],            'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'GRID':               {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_GRID']['LIGHT'],               'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'GRIDHEAVY':          {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_GRIDHEAVY']['LIGHT'],          'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'GUIDECONTENT':       {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_GUIDECONTENT']['LIGHT'],       'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'CONTENT_NAME':       {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_CONTENT_NAME']['LIGHT'],       'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'CONTENT_POSITIVE_1': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_CONTENT_POSITIVE_1']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'CONTENT_NEGATIVE_1': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_CONTENT_NEGATIVE_1']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'CONTENT_NEUTRAL_1':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_CONTENT_NEUTRAL_1']['LIGHT'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'CONTENT_POSITIVE_2': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_CONTENT_POSITIVE_2']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'CONTENT_NEGATIVE_2': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_CONTENT_NEGATIVE_2']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'CONTENT_NEUTRAL_2':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_CONTENT_NEUTRAL_2']['LIGHT'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'CONTENT_DEFAULT':    {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_CONTENT_DEFAULT']['LIGHT'],    'anchor_x': 'center', 'anchor_y': 'center'}},
                                           'DARK':  {'DEFAULT':            {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_DEFAULT']['DARK'],             'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'GRID':               {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_GRID']['DARK'],                'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'GRIDHEAVY':          {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_GRIDHEAVY']['DARK'],           'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'GUIDECONTENT':       {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_GUIDECONTENT']['DARK'],        'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'CONTENT_NAME':       {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_CONTENT_NAME']['DARK'],        'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'CONTENT_POSITIVE_1': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_CONTENT_POSITIVE_1']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'CONTENT_NEGATIVE_1': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_CONTENT_NEGATIVE_1']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'CONTENT_NEUTRAL_1':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_CONTENT_NEUTRAL_1']['DARK'],   'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'CONTENT_POSITIVE_2': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_CONTENT_POSITIVE_2']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'CONTENT_NEGATIVE_2': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_CONTENT_NEGATIVE_2']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'CONTENT_NEUTRAL_2':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_CONTENT_NEUTRAL_2']['DARK'],   'anchor_x': 'center', 'anchor_y': 'center'},
                                                     'CONTENT_DEFAULT':    {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_CHARTDRAWER_CONTENT_DEFAULT']['DARK'],     'anchor_x': 'center', 'anchor_y': 'center'}}},
                                            
                   'dailyReportViewer_default': {'LIGHT': {'DEFAULT':            {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_DEFAULT']['LIGHT'],            'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'GRID':               {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_GRID']['LIGHT'],               'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'GRIDHEAVY':          {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_GRIDHEAVY']['LIGHT'],          'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'GUIDECONTENT':       {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_GUIDECONTENT']['LIGHT'],       'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'CONTENT_NAME':       {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_CONTENT_NAME']['LIGHT'],       'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'CONTENT_POSITIVE_1': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_CONTENT_POSITIVE_1']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'CONTENT_NEGATIVE_1': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_CONTENT_NEGATIVE_1']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'CONTENT_NEUTRAL_1':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_CONTENT_NEUTRAL_1']['LIGHT'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'CONTENT_POSITIVE_2': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_CONTENT_POSITIVE_2']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'CONTENT_NEGATIVE_2': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_CONTENT_NEGATIVE_2']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'CONTENT_NEUTRAL_2':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_CONTENT_NEUTRAL_2']['LIGHT'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'CONTENT_DEFAULT':    {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_CONTENT_DEFAULT']['LIGHT'],    'anchor_x': 'center', 'anchor_y': 'center'}},
                                                 'DARK': {'DEFAULT':             {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_DEFAULT']['DARK'],             'anchor_x': 'center', 'anchor_y': 'center'},
                                                          'GRID':                {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_GRID']['DARK'],                'anchor_x': 'center', 'anchor_y': 'center'},
                                                          'GRIDHEAVY':           {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_GRIDHEAVY']['DARK'],           'anchor_x': 'center', 'anchor_y': 'center'},
                                                          'GUIDECONTENT':        {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_GUIDECONTENT']['DARK'],        'anchor_x': 'center', 'anchor_y': 'center'},
                                                          'CONTENT_NAME':        {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_CONTENT_NAME']['DARK'],        'anchor_x': 'center', 'anchor_y': 'center'},
                                                          'CONTENT_POSITIVE_1':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_CONTENT_POSITIVE_1']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                          'CONTENT_NEGATIVE_1':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_CONTENT_NEGATIVE_1']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                          'CONTENT_NEUTRAL_1':   {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_CONTENT_NEUTRAL_1']['DARK'],   'anchor_x': 'center', 'anchor_y': 'center'},
                                                          'CONTENT_POSITIVE_2':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_CONTENT_POSITIVE_2']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                          'CONTENT_NEGATIVE_2':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_CONTENT_NEGATIVE_2']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                          'CONTENT_NEUTRAL_2':   {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_CONTENT_NEUTRAL_2']['DARK'],   'anchor_x': 'center', 'anchor_y': 'center'},
                                                          'CONTENT_DEFAULT':     {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_DAILYREPORTVIEWER_CONTENT_DEFAULT']['DARK'],     'anchor_x': 'center', 'anchor_y': 'center'}}},
                                            
                   'hourlyReportViewer_default': {'LIGHT': {'DEFAULT':            {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_DEFAULT']['LIGHT'],            'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'GRID':               {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_GRID']['LIGHT'],               'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'GRIDHEAVY':          {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_GRIDHEAVY']['LIGHT'],          'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'GUIDECONTENT':       {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_GUIDECONTENT']['LIGHT'],       'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'CONTENT_NAME':       {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_CONTENT_NAME']['LIGHT'],       'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'CONTENT_POSITIVE_1': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_CONTENT_POSITIVE_1']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'CONTENT_NEGATIVE_1': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_CONTENT_NEGATIVE_1']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'CONTENT_NEUTRAL_1':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_CONTENT_NEUTRAL_1']['LIGHT'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'CONTENT_POSITIVE_2': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_CONTENT_POSITIVE_2']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'CONTENT_NEGATIVE_2': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_CONTENT_NEGATIVE_2']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'CONTENT_NEUTRAL_2':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_CONTENT_NEUTRAL_2']['LIGHT'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'CONTENT_DEFAULT':    {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_CONTENT_DEFAULT']['LIGHT'],    'anchor_x': 'center', 'anchor_y': 'center'}},
                                                  'DARK': {'DEFAULT':             {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_DEFAULT']['DARK'],             'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'GRID':                {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_GRID']['DARK'],                'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'GRIDHEAVY':           {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_GRIDHEAVY']['DARK'],           'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'GUIDECONTENT':        {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_GUIDECONTENT']['DARK'],        'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'CONTENT_NAME':        {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_CONTENT_NAME']['DARK'],        'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'CONTENT_POSITIVE_1':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_CONTENT_POSITIVE_1']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'CONTENT_NEGATIVE_1':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_CONTENT_NEGATIVE_1']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'CONTENT_NEUTRAL_1':   {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_CONTENT_NEUTRAL_1']['DARK'],   'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'CONTENT_POSITIVE_2':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_CONTENT_POSITIVE_2']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'CONTENT_NEGATIVE_2':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_CONTENT_NEGATIVE_2']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'CONTENT_NEUTRAL_2':   {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_CONTENT_NEUTRAL_2']['DARK'],   'anchor_x': 'center', 'anchor_y': 'center'},
                                                           'CONTENT_DEFAULT':     {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_HOURLYREPORTVIEWER_CONTENT_DEFAULT']['DARK'],     'anchor_x': 'center', 'anchor_y': 'center'}}},
                                            
                   'neuralNetworkViewer_default': {'LIGHT': {'DEFAULT':            {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_DEFAULT']['LIGHT'],            'anchor_x': 'center', 'anchor_y': 'center'},
                                                             'CONTENT_NAME':       {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_CONTENT_NAME']['LIGHT'],       'anchor_x': 'center', 'anchor_y': 'center'},
                                                             'CONTENT_POSITIVE_1': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_CONTENT_POSITIVE_1']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'},
                                                             'CONTENT_NEGATIVE_1': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_CONTENT_NEGATIVE_1']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'},
                                                             'CONTENT_NEUTRAL_1':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_CONTENT_NEUTRAL_1']['LIGHT'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                             'CONTENT_POSITIVE_2': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_CONTENT_POSITIVE_2']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'},
                                                             'CONTENT_NEGATIVE_2': {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_CONTENT_NEGATIVE_2']['LIGHT'], 'anchor_x': 'center', 'anchor_y': 'center'},
                                                             'CONTENT_NEUTRAL_2':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_CONTENT_NEUTRAL_2']['LIGHT'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                             'CONTENT_DEFAULT':    {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_CONTENT_DEFAULT']['LIGHT'],    'anchor_x': 'center', 'anchor_y': 'center'}},
                                                   'DARK': {'DEFAULT':             {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_DEFAULT']['DARK'],             'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'CONTENT_NAME':        {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_CONTENT_NAME']['DARK'],        'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'CONTENT_POSITIVE_1':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_CONTENT_POSITIVE_1']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'CONTENT_NEGATIVE_1':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_CONTENT_NEGATIVE_1']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'CONTENT_NEUTRAL_1':   {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_CONTENT_NEUTRAL_1']['DARK'],   'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'CONTENT_POSITIVE_2':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_CONTENT_POSITIVE_2']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'CONTENT_NEGATIVE_2':  {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_CONTENT_NEGATIVE_2']['DARK'],  'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'CONTENT_NEUTRAL_2':   {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_CONTENT_NEUTRAL_2']['DARK'],   'anchor_x': 'center', 'anchor_y': 'center'},
                                                            'CONTENT_DEFAULT':     {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXT_NEURALNETWORKVIEWER_CONTENT_DEFAULT']['DARK'],     'anchor_x': 'center', 'anchor_y': 'center'}}},
                   }
for baseTextStyleCode in ('textBox_default', 'textInputBox_default', 'selectionBox_default', 'chartDrawer_default', 'dailyReportViewer_default', 'hourlyReportViewer_default', 'neuralNetworkViewer_default'):
    for guiTheme in ('LIGHT', 'DARK'):
        for baseColor in ('RED_DARK',    'RED',    'RED_LIGHT', 
                          'ORANGE_DARK', 'ORANGE', 'ORANGE_LIGHT', 
                          'YELLOW_DARK', 'YELLOW', 'YELLOW_LIGHT', 
                          'GREEN_DARK',  'GREEN',  'GREEN_LIGHT', 
                          'BLUE_DARK',   'BLUE',   'BLUE_LIGHT', 
                          'VIOLET_DARK', 'VIOLET', 'VIOLET_LIGHT', 
                          'CYAN_DARK',   'CYAN',   'CYAN_LIGHT', 
                          'GREY_DARK',   'GREY',   'GREY_LIGHT'):
            _BASETEXTSTYLES[baseTextStyleCode][guiTheme][baseColor] = {'bold': True, 'italic': False, 'color': _COLORTABLE['TEXTCOLOR_'+baseColor][guiTheme], 'anchor_x': 'center', 'anchor_y': 'center'}

#VISUAL MANAGER OBJECT ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class visualManager:
    def __init__(self, path_project, guiConfig):
        print("\nInitializing Visual Manager")
        self.guiConfig = guiConfig

        self.lastMouseInput = None

        #TextPack Read
        self.availableLanguages = atmEta_gui_TextPack.LANGUAGES
        self.textPacks = dict()
        for textHeader in atmEta_gui_TextPack.TEXTPACK.keys(): self.textPacks[textHeader] = textPack(texts = atmEta_gui_TextPack.TEXTPACK[textHeader])

        #ColorTable
        self.effectiveTextStyles = {'wrapperBox_default':          dict(),
                                    'wrapperBox_default2':         dict(),
                                    'button_default':              dict(),
                                    'switch_default':              dict(),
                                    'textBox_default':             dict(),
                                    'textInputBox_default':        dict(),
                                    'selectionBox_default':        dict(),
                                    'chartDrawer_default':         dict(),
                                    'dailyReportViewer_default':   dict(),
                                    'hourlyReportViewer_default':  dict(),
                                    'neuralNetworkViewer_default': dict()}

        #Initialize the effectiveTextStyles
        self.on_GUIThemeUpdate()
        self.on_LanguageUpdate()

        print("VISUAL Manager Initialization Complete!")

    def getTextPack(self, textHeader): return self.textPacks[textHeader]

    def extractText(self, textInstance, asLanguage = None):
        instanceType = type(textInstance)
        if   (instanceType == str):                     return textInstance
        elif (instanceType == textPack): 
            if (asLanguage in self.availableLanguages): return textInstance.get(asLanguage)
            else:                                       return textInstance.get(self.guiConfig['Language'])
        else:                                           return str(textInstance)

    def getTextStyle(self, textStyle):
        newTextStyleInstance = dict()
        for textStyleMode in self.effectiveTextStyles[textStyle]: newTextStyleInstance[textStyleMode] = self.effectiveTextStyles[textStyle][textStyleMode].copy()
        return newTextStyleInstance

    def getFromColorTable(self, colorCode):
        return _COLORTABLE[colorCode][self.guiConfig['GUITheme']]

    def getGUITheme(self):
        return self.guiConfig['GUITheme']

    def getLanguage(self):
        return self.guiConfig['Language']

    def getAvailableLanguages(self):
        return self.availableLanguages

    def getLanguageFont(self):
        return _SYSTEMFONT[self.guiConfig['Language']]

    def on_GUIThemeUpdate(self):
        for objectType in self.effectiveTextStyles.keys():
            self.effectiveTextStyles[objectType].clear()
            for styleMode in _BASETEXTSTYLES[objectType][self.guiConfig['GUITheme']].keys():
                self.effectiveTextStyles[objectType][styleMode] = _BASETEXTSTYLES[objectType][self.guiConfig['GUITheme']][styleMode].copy()
                self.effectiveTextStyles[objectType][styleMode]['font_name'] = _SYSTEMFONT[self.guiConfig['Language']]

    def on_LanguageUpdate(self):
        for objectType in self.effectiveTextStyles.keys():
            for styleMode in self.effectiveTextStyles[objectType].keys():
                self.effectiveTextStyles[objectType][styleMode]['font_name'] = _SYSTEMFONT[self.guiConfig['Language']]

    def setLastMouseEvent(self, mouseEvent):
        self.lastMouseInput = mouseEvent.copy()

    def getLastMouseEvent(self):
        return self.lastMouseInput.copy()
#VISUAL MANAGER OBJECT END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

#TEXTPACK OBJECT ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
class textPack:
    def __init__(self, texts): self.texts = texts
    def get(self, language): return self.texts[language]    
#TEXTPACK OBJECT END --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------