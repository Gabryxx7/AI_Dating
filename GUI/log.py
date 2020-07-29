import time
from datetime import datetime
import colorama
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from GUI.log_widget import LogWidget
import os


class Singleton:
    def __init__(self, cls):
        self._cls = cls

    def Instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._cls()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `Instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._cls)

class LogColor():
    def __init__(self, name, code, html):
        self.color_name = name
        self.color_code = code
        self.color_html = html

@Singleton
class Log(object):
    def __init__(self):
        self.logging_levels = {'a':0, 'd':1, 'i':2, 's':2, 'w':3, 'e':4}
        self.min_level = 'a'
        self.log_file = "log.txt"
        self.file = open(self.log_file, "w+")
        self.enabled = True
        self.enable_console = True
        self.enable_widget = True
        self.save_to_file = True
        self.logWidget = None

        self.colors = {'red': LogColor('red', "\033[91m", "<font color=\"Red\">"),
                       'green': LogColor('green', "\033[92m", "<font color=\"Green\">"),
                       'white': LogColor('white', "\033[37m", "<font color=\"White\">"),
                       'blue': LogColor('blue', "\033[94m", "<font color=\"Blue\">"),
                       'orange': LogColor('orange', "\033[93m", "<font color=\"Orange\">"),
                       'reset': LogColor('orange', "\033[0;0m", "</>")}

    def set_min_level(self, level):
        self.i("LOGGER", "Logging Level Changed: " + self.min_level + " - " + str(self.logging_levels[self.min_level]))
        self.min_level = level

    def get_min_level_index(self):
        return list(self.logging_levels.keys()).index(self.min_level)

    def setEnabled(self, enabled):
        self.i("LOGGER", "Logging has been " + self.status_string(enabled))
        self.enabled = enabled

    def setConsoleEnabled(self, enabled):
        self.i("LOGGER", "Logging CONSOLE has been " + self.status_string(enabled))
        self.enable_console = enabled

    def setWidgetEnabled(self, enabled):
        self.i("LOGGER", "Logging WIDGET has been " + self.status_string(enabled))
        self.enable_widget = enabled

    def setFileEnabled(self, enabled):
        self.i("LOGGER", "Logging FILE has been " + self.status_string(enabled)+": " + os.path.abspath(self.log_file))
        self.save_to_file = enabled

    def status_string(self, status):
        if status:
            return "ENABLED"
        else:
            return  "DISABLED"

    def w(self, tag, text, log_to_widget=True):
        self.print("orange", tag, text, 'w', log_to_widget)

    def d(self, tag, text, log_to_widget=True):
        self.print("blue", tag, text, 'd', log_to_widget)

    def e(self, tag, text, log_to_widget=True):
        self.print("red", tag, text, 'e', log_to_widget)

    def s(self, tag, text, log_to_widget=True):
        self.print("green", tag, text, 's', log_to_widget)

    def i(self, tag, text, log_to_widget=True):
        self.print("white", tag, text, 'i', log_to_widget)

    def print(self, color_name, tag, text, log_level, log_to_widget=True):
        if self.enabled:
            color = self.colors[color_name]
            color_reset = self.colors['reset']
            if self.logging_levels[log_level] >= self.logging_levels[self.min_level]:
                dateTimeObj = datetime.now()
                timestampStr = dateTimeObj.strftime("%d-%b-%Y %H:%M:%S") + " - "
                log_text = log_level + "["+str(tag)+"]: " +str(text)
                if self.enable_widget and log_to_widget and self.logWidget is not None:
                    try:
                        final_text = timestampStr + color.color_html + " " + log_text + color_reset.color_html
                        self.logWidget.append(final_text + "\n")
                    except Exception as e:
                        print("Exception writing to LOG Widget:" + str(e))
                        pass
                if self.enable_console:
                    final_text = timestampStr + color.color_code + " " + log_text + color_reset.color_code
                    print(final_text)
                if self.save_to_file:
                    try:
                        self.file.write(timestampStr + log_text + "\n")
                    except Exception as e:
                        print("Exception writing to LOG File:" +str(e))
                        pass
    def create_log_widget(self):
        self.logWidget = LogWidget(self)


log = Log.Instance()
