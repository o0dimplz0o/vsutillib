"""
OutputTextWidget:

Output widget form just to output text in color

"""
# OTW0004 Next log ID

import inspect
import logging
import platform

from typing import Dict, Optional, Union

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtGui import QColor, QTextCursor
from PySide6.QtWidgets import QTextEdit, QWidget

from .insertTextHelpers import checkColor, LineOutput
from .SvgColor import SvgColor

from vsutillib.misc import callerName

MODULELOG = logging.getLogger(__name__)
MODULELOG.addHandler(logging.NullHandler())


class QOutputTextWidget(QTextEdit):
    """Output for running queue"""

    # log state
    __log = False
    clearSignal = Signal()
    insertTextSignal = Signal(str, dict)
    setCurrentIndexSignal = Signal()
    isDarkMode = False
    logWithCaller = False

    def __init__(
            self,
            parent: Optional[QWidget] = None,
            log: Optional[bool] = None,
            **kwargs: str) -> None:
        super().__init__(parent=parent, **kwargs)

        self.parent = parent
        self.__log = None
        self.log = log

        self.insertTextSignal.connect(self.insertText)
        self.clearSignal.connect(super().clear)
        
	# On macOS, tell this widget we're in dark mode
        # so checkColor() uses light text on dark background.
        if platform.system() == "Darwin":
            QOutputTextWidget.isDarkMode = True

    @classmethod
    def classLog(cls, setLogging: Optional[bool] = None) -> bool:
        """
        get/set logging at class level
        every class instance will log
        unless overwritten

        Args:
            setLogging (bool):
                - True class will log
                - False turn off logging
                - None returns current Value

        Returns:
            bool:

            returns the current value set
        """

        if setLogging is not None:
            if isinstance(setLogging, bool):
                cls.__log = setLogging

        return cls.__log

    @property
    def log(self) -> bool:
        """
        class property can be used to override the class global
        logging setting

        Returns:
            bool:

            True if logging is enable False otherwise
        """
        if self.__log is not None:
            return self.__log

        return QOutputTextWidget.classLog()

    @log.setter
    def log(self, value: bool) -> None:
        """set instance log variable"""
        if isinstance(value, bool) or value is None:
            self.__log = value

    def connectToInsertText(self, objSignal: Signal) -> None:
        """Connect to signal"""

        objSignal.connect(self.insertText)

    @Slot(str, dict)
    def insertText(self, strText: str, kwargs: Dict[str, Union[QColor, bool]]):
        """
        insertText - Insert text in output window.
        Cannot use standard keyword arguments on
        emit calls using a dictionary argument instead

        Args:
            strText (str): text to insert on output window
            kwargs (dict): additional arguments in dictionary
                           used like **kwargs
        """

        #strTmp = ""

        color = kwargs.pop(LineOutput.Color, None)
        replaceLine = kwargs.pop(LineOutput.ReplaceLine, False)
        appendLine = kwargs.pop(LineOutput.AppendLine, False)
        appendEnd = kwargs.pop(LineOutput.AppendEnd, False)
        logOnly = kwargs.pop(LineOutput.LogOnly, False)
        overrideLog = kwargs.pop("log", None)

        # still no restore to default the ideal configuration
        # search will continue considering abandoning color

        if not logOnly:
            color = checkColor(color, QOutputTextWidget.isDarkMode)

            if replaceLine:
                self.moveCursor(QTextCursor.StartOfLine,
                                QTextCursor.KeepAnchor)
            elif appendEnd:
                self.moveCursor(QTextCursor.End)

            if color is not None:
                self.setTextColor(color)

            if replaceLine:
                self.insertPlainText(strText)
            elif appendLine:
                self.append(strText)
            elif appendEnd:
                self.append(strText)
            else:
                self.insertPlainText(strText)

            self.ensureCursorVisible()

        log = self.log

        if overrideLog is not None:
            log = overrideLog

        if log or logOnly:

            if self.logWithCaller:
                caller = []
                if caller2 := callerName():
                    caller.append(caller2)

                if caller3 := callerName(3):
                    caller.append(caller3)

                if caller:
                    whoCalled = ".".join(caller)
                    strTmp = f"[{whoCalled}] {strText}"
                else:
                    strTmp = strText
            else:
                strTmp = strText

            strTmp = strTmp.replace("\n", " ")

            strNotEmpty = bool(strText.strip())

            if strNotEmpty and strTmp.find(u"Progress:") != 0:
                if strTmp.find("Warning") == 0:
                    MODULELOG.warning("OTW0001: %s", strTmp)
                elif strTmp.find("Error") == 0 or color == Qt.red:
                    MODULELOG.error("OTW0002: %s", strTmp)
                else:
                    if strTmp.strip():
                        MODULELOG.debug("OTW0003: %s", strTmp)
