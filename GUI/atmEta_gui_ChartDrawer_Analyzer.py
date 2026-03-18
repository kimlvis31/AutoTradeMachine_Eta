from .atmEta_gui_ChartDrawer import chartDrawer

class chartDrawer_analyzer(chartDrawer):
    def __init__(self, **kwargs):
        self.chartDrawerType = "ANALYZER"
        super().__init__(**kwargs)