from pathlib import Path

from PyQt6 import uic
from PyQt6.QtGui import (
    QIcon
)
from PyQt6.QtWidgets import (
    QDialog,
)

from ..assets import MAIN_UI, DIALOG_ICON



class Main(QDialog):


    def __init__(self):
        super(Main, self).__init__()
        uic.loadUi(MAIN_UI, self)
        self.setWindowIcon(QIcon(DIALOG_ICON))
        
