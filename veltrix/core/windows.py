from PyQt6.QtWidgets import QMdiArea
class WindowManager:
    def __init__(self, area: QMdiArea): self.area = area
    def tile(self): self.area.tileSubWindows()
    def cascade(self): self.area.cascadeSubWindows()
