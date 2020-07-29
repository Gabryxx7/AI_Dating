
# Std
import argparse
import collections
import json
import oyaml as yaml
import sys

# External
from PySide2.QtGui import *
from PySide2.QtWidgets import *
from GUI.log import log
import os
from GUI.person_details_widgets import PersonDetailsWidget

class TextToTreeItem:
    def __init__(self):
        self.text_list = []
        self.titem_list = []

    def append(self, text_list, titem):
        for text in text_list:
            self.text_list.append(text)
            self.titem_list.append(titem)

    # Return model indices that match string
    def find(self, find_str):
        titem_list = []
        for i, s in enumerate(self.text_list):
            if find_str in s:
                titem_list.append(self.titem_list[i])

        return titem_list


class JsonViewWidget(QWidget):
    def __init__(self, parent, fpath=None):
        super(JsonViewWidget, self).__init__(parent)

        self.parent = parent
        self.app = parent.app

        self.find_box = None
        self.tree_widget = None
        self.text_to_titem = TextToTreeItem()
        self.find_str = ""
        self.found_titem_list = []
        self.found_idx = 0

        selection_layout = QHBoxLayout()

        self.person_widget = PersonDetailsWidget(self.parent)
        self.person_widget.setStyleSheet("""
            .QWidget{
                border: 0.5px solid #777777;
                border-radius: 5px;
            }
            """)
        # self.person_widget.profile_pic.setMinimumSize(200,200)
        selection_layout.addWidget(self.person_widget)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Tree
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderLabels(["Key", "Value"])
        self.tree_widget.header().setSectionResizeMode(QHeaderView.Stretch)

        layout = QHBoxLayout()
        # Group box
        self.gbox = QGroupBox(fpath)
        self.gbox.setLayout(layout)
        # Add table to layout
        layout.addWidget(self.tree_widget)
        layout2 = QVBoxLayout()

        self.jfile = None
        self.jdata = None
        self.load_file(fpath)

        # Find UI
        find_layout = self.make_find_ui()
        layout2.addLayout(selection_layout,5)
        layout2.addLayout(find_layout,5)
        layout2.addWidget(self.gbox,90)

        self.setLayout(layout2)

    def make_find_ui(self):

        # Text box
        self.find_box = QLineEdit()
        self.find_box.returnPressed.connect(self.find_button_clicked)

        # Find Button
        find_button = QPushButton("Find")
        find_button.clicked.connect(self.find_button_clicked)

        layout = QHBoxLayout()
        layout.addWidget(self.find_box)
        layout.addWidget(find_button)

        return layout

    def find_button_clicked(self):
        find_str = self.find_box.text()

        # Very common for use to click Find on empty string
        if find_str == "":
            return

        # New search string
        if find_str != self.find_str:
            self.find_str = find_str
            self.found_titem_list = self.text_to_titem.find(self.find_str)
            self.found_idx = 0
        else:
            item_num = len(self.found_titem_list)
            self.found_idx = (self.found_idx + 1) % item_num

        self.tree_widget.setCurrentItem(self.found_titem_list[self.found_idx])

    def recurse_jdata(self, jdata, tree_widget):
        if isinstance(jdata, dict):
            for key, val in jdata.items():
                self.tree_add_row(key, val, tree_widget)
        elif isinstance(jdata, list):
            for i, val in enumerate(jdata):
                key = str(i)
                self.tree_add_row(key, val, tree_widget)
        else:
            print("This should never be reached!")

    def tree_add_row(self, key, val, tree_widget):
        text_list = []
        if isinstance(val, dict) or isinstance(val, list):
            text_list.append(key)
            row_item = QTreeWidgetItem([key])
            self.recurse_jdata(val, row_item)
        else:
            text_list.append(key)
            text_list.append(str(val))
            row_item = QTreeWidgetItem([key, str(val)])

        tree_widget.addChild(row_item)
        self.text_to_titem.append(text_list, row_item)

    def load_matches(self):
        self.unselect_person()
        self.load_data(self.app.matches_file)

    def load_recommendations(self):
        self.unselect_person()
        self.load_data(self.app.recommendations_file)

    def load_profile(self):
        self.unselect_person()
        profile_data = self.load_file(self.app.profile_file)
        self.load_data(profile_data[0])

    def unselect_person(self):
        self.person_widget.set_data(None)
        # self.person_widget.setPicturePath(None)

    def load_file(self, fpath):
        if fpath is not None:
            try:
                try:
                    self.jfile = open(fpath)
                    self.jdata = json.load(self.jfile, object_pairs_hook=collections.OrderedDict)
                except Exception as e:
                    log.i("JSON_VIEWER", "Reading yaml file")
                    self.jfile = open(fpath)
                    self.jdata = yaml.safe_load(self.jfile)
                return self.jdata
            except Exception as e:
                log.e("JSON_VIEWER", "Error opening json file: " +str(os.path.abspath(fpath)) + " " +str(e))

    def load_data(self, data, title=""):
        if isinstance(data, str):
            title = os.path.abspath(data)
            data = self.load_file(data)
        self.unselect_person()
        self.tree_widget.clear()
        self.root_item = QTreeWidgetItem(["Root"])
        self.recurse_jdata(data, self.root_item)
        self.tree_widget.addTopLevelItem(self.root_item)
        self.tree_widget.expandItem(self.root_item)
        if isinstance(data, dict):
            self.person_widget.set_data(data, True)
            self.gbox.setTitle(title)
