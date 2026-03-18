from .atmEta_gui_ChartDrawer import chartDrawer

class chartDrawer_tlViewer(chartDrawer):
    def __init__(self, **kwargs):
        self.chartDrawerType = "TLVIEWER"
        super().__init__(**kwargs)