"""
qtUtils:

utility functions that use PySide2
"""


import logging
import platform

from typing import Any, Callable, Optional

#from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QScreen
from PySide6.QtWidgets import (
    QPushButton,
    QWidget,
    QToolTip
)

from .classes import QRunInThread, SvgColor

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import Qt

def centerWidget(widget):
    """ Center a widget on the primary screen (safe for macOS / M1). """

    # Must get screen from QGuiApplication, not instantiate QScreen()
    screen = QGuiApplication.primaryScreen()
    if screen is None:
        return  # failsafe—just don't center

    screen_geo = screen.availableGeometry()
    widget_geo = widget.frameGeometry()

    # Compute centered position
    center_point = screen_geo.center()
    widget_geo.moveCenter(center_point)

    widget.move(widget_geo.topLeft())

def pushButton(
        label: str,
        function: Callable[..., None],
        tooltip: str) -> QPushButton:
    """
    pushButton convenience function for QPushButton definitions

    Args:
        label (str): label for push button
        function (func): function to execute when clicked
        tooltip (str): tool tip for push button

    Returns:
        QPushButton: PySide2 QPushButton
    """

    button = QPushButton(label)
    button.resize(button.sizeHint())
    button.clicked.connect(function)
    button.setToolTip(tooltip)

    return button

def setAppStyle(app):
    """Set style to Fusion that works with Dark/Light theme"""

    app.setStyle("Fusion")

    if platform.system() == "Linux":
        # On Linux the disabled color for text is the same for enabled
        disabledColor = QColor(127, 127, 127)
        palette = app.palette()
        palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabledColor)
        app.setPalette(palette)

def darkPalette(app=None):
    """Use dark theme on windows 10"""

    palette = QPalette()

    darkColor = QColor(45, 45, 45)
    disabledColor = QColor(127, 127, 127)

    palette.setColor(QPalette.AlternateBase, darkColor)
    palette.setColor(QPalette.Base, QColor(36, 36, 36))
    palette.setColor(QPalette.BrightText, SvgColor.red)
    palette.setColor(QPalette.Button, darkColor)
    palette.setColor(QPalette.ButtonText, SvgColor.white)
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, disabledColor)
    palette.setColor(QPalette.Disabled,
                     QPalette.HighlightedText, disabledColor)
    palette.setColor(QPalette.Disabled, QPalette.Text, disabledColor)
    palette.setColor(QPalette.Disabled, QPalette.WindowText, disabledColor)
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, SvgColor.white) # was black
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Text, SvgColor.white)
    palette.setColor(QPalette.ToolTipBase, SvgColor.white)
    palette.setColor(QPalette.ToolTipText, SvgColor.white)
    palette.setColor(QPalette.Window, darkColor)
    palette.setColor(QPalette.WindowText, SvgColor.white)

    if app is not None:
        app.setStyle("Fusion")
        # app.setStyle("windowsvista")
        app.setPalette(palette)

        toolTipPalette = QPalette()
        toolTipPalette.setColor(
            QPalette.Inactive, QPalette.ToolTipText, SvgColor.white)
        toolTipPalette.setColor(
            QPalette.Inactive, QPalette.ToolTipBase, QColor(42, 130, 218)
        )
        QToolTip.setPalette(toolTipPalette)

    return palette


def qtRunFunctionInThread(function, *args, **kwargs):
    """
    Pass the function to execute Other args,
    kwargs are passed to the run function
    """

    funcStart = kwargs.pop("funcStart", None)
    funcFinished = kwargs.pop("funcFinished", None)
    funcResult = kwargs.pop("funcResult", None)
    funcError = kwargs.pop("funcError", None)

    worker = QRunInThread(function, *args, **kwargs)

    if funcStart is not None:
        worker.startSignal.connect(funcStart)
    if funcFinished is not None:
        worker.finishedSignal.connect(funcFinished)
    if funcResult is not None:
        worker.resultSignal.connect(funcResult)
    if funcError is not None:
        worker.errorSignal.connect(funcError)

    # Execute
    worker.run()
