from pathlib import Path

from PyQt6 import uic
from PyQt6.QtGui import (
    QIcon
)
from PyQt6.QtWidgets import (
    QDialog,
)



CWD = Path(__file__).resolve().parent
UI = (CWD / 'main.ui').as_posix()
ICON = (CWD / 'icon.png').as_posix()


class Main(QDialog):


    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi(UI, self)
        self.setWindowIcon(QIcon(ICON))
        
