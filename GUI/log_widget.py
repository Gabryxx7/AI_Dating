from PySide2.QtWidgets import *
from PySide2.QtGui import *

class LogWidget(QWidget):
    def __init__(self, logger):
        super(LogWidget, self).__init__()
        self.main_layout = QVBoxLayout()
        self.extra_layout = QHBoxLayout()
        self.logger = logger
        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setFont(QFont("Courier New", 9))

        self.title = QLabel("LOG")
        self.filter_label = QLabel("Filter level:")
        self.filter_combobox = QComboBox()
        for key in self.logger.logging_levels.keys():
            self.filter_combobox.addItem(str(self.logger.logging_levels[key]) + " - " + key, key)
        self.filter_combobox.currentIndexChanged.connect(self.on_combobox_changed)
        self.enable_checkbox = QCheckBox("Enable")
        self.enable_checkbox.stateChanged.connect(self.enable_checkbox_changed)
        self.console_checkbox = QCheckBox("Console")
        self.console_checkbox.stateChanged.connect(self.console_checkbox_changed)
        self.widget_checkbox = QCheckBox("Widget")
        self.widget_checkbox.stateChanged.connect(self.widget_checkbox_changed)
        self.file_checkbox = QCheckBox("File")
        self.file_checkbox.stateChanged.connect(self.file_checkbox_changed)

        self.extra_layout.addWidget(self.title)
        self.extra_layout.addWidget(self.filter_label)
        self.extra_layout.addWidget(self.filter_combobox)
        self.extra_layout.addWidget(self.enable_checkbox)
        self.extra_layout.addWidget(self.console_checkbox)
        self.extra_layout.addWidget(self.widget_checkbox)
        self.extra_layout.addWidget(self.file_checkbox)
        self.extra_layout.addStretch(1)

        self.main_layout.addLayout(self.extra_layout)
        self.main_layout.addWidget(self.text_area)
        self.check_log_status()

        self.setLayout(self.main_layout)

    def append(self, text):
        self.text_area.append(text)
        # self.text_area.moveCursor(QTextCursor.End)
        self.text_area.verticalScrollBar().setValue(self.text_area.verticalScrollBar().maximum())

    def on_combobox_changed(self, value):
        self.logger.set_min_level(self.filter_combobox.itemData(value))

    def enable_checkbox_changed(self, value):
        self.logger.setEnabled(value)
        self.check_log_status()

    def console_checkbox_changed(self, value):
        self.logger.setConsoleEnabled(value)
        self.check_log_status()

    def widget_checkbox_changed(self, value):
        self.logger.setWidgetEnabled(value)
        self.check_log_status()

    def file_checkbox_changed(self, value):
        self.logger.setFileEnabled(value)
        self.check_log_status()

    def check_log_status(self):
        self.filter_combobox.setCurrentIndex(self.logger.get_min_level_index())

        self.enable_checkbox.setChecked(self.logger.enabled)
        self.console_checkbox.setChecked(self.logger.enable_console)
        self.widget_checkbox.setChecked(self.logger.enable_widget)
        self.file_checkbox.setChecked(self.logger.save_to_file)

        self.console_checkbox.setEnabled(self.logger.enabled)
        self.widget_checkbox.setEnabled(self.logger.enabled)
        self.file_checkbox.setEnabled(self.logger.enabled)


