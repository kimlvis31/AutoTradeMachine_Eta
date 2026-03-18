from .atmEta_gui_ChartDrawer import chartDrawer

class chartDrawer_caViewer(chartDrawer):
    def __init__(self, **kwargs):
        self.chartDrawerType = "CAVIEWER"
        super().__init__(**kwargs)