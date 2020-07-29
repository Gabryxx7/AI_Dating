#!/Users/marinig/opt/anaconda3/lib/python3.7
# Filename: tinderApp.py

import sys
from PySide2.QtWidgets import *
from PySide2.QtCore import *
from PySide2.QtGui import *

import qdarkstyle
import argparse
import oyaml as yaml
import csv
import json
import GUI.loginWindow as lw
import GUI.mainWindow as mw
from API.tinder_api_extended import TinderApi
from GUI.log import log
import traceback
from Threading.data_reloader import APIBackgroundWorker
from GUI.customwaitingwidget import QtCustomWaitingSpinner
import faulthandler
import time
import os
import re

class TinderApp(QApplication):
    def __init__(self, parsed_args, *args, **kwargs):
        super(TinderApp, self).__init__(*args, **kwargs)

        log.create_log_widget()
        self.data_folder = "./Data/"
        self.recommendations_folder = self.data_folder + "recommendations/"
        self.recommendations_file = self.data_folder + "recommendations.json"
        self.matches_folder = self.data_folder + "matches/"
        self.matches_file = self.data_folder + "matches.json"
        self.profile_folder = self.data_folder + "profile/"
        self.profile_file = self.data_folder + "profile.json"
        self.tinder_api = TinderApi(self.data_folder)
        self.logged_in = False

        # self.thread = QThread()  # 1a - create Worker and Thread inside the Form. No parent!
        # self.obj = worker.Worker()  # no parent!
        self.thread_pool = QThreadPool()   # 1b - create a ThreadPool and then create the Workers when you need!
        self.thread_pool.setMaxThreadCount(4)

        self.background_tasks_list = []
        self.background_info = QLabel("No background stuff!")
        self.background_count_label = QLabel("")
        self.background_completed = 0
        self.background_count_total = 0
        self.spinner = QtCustomWaitingSpinner(self, centerOnParent=False)
        self.spinner.hideSpinner()
        self.spinner.updateSize(QSize(30,30))

        """
        I wanted to make this config an object. I tried by calling yaml_load and getting
        the dictionary from a pure yaml file (without !!python/object:__main__.ConfigSingleton on top)
        Then I tried to pass the dictionary to an object like Struct(**dict) and
        class Struct:
            def __init__(self, **entries):
                self.__dict__.update(entries)

        But it did not work
        """
        self.configSingleton = ConfigSingleton()  # Transform the dict to attributes of the class ConfigSingleton
        self.config = self.configSingleton.yaml_config  # Transform the dict to attributes of the class ConfigSingleton
        self.config_file = self.configSingleton.yaml_config_file

        self.recommendations = None
        self.matches = None
        self.new_recommendations = None
        self.new_matches = None
        self.profile_info = None

        self.window = ""
        # set app icon
        self.setWindowIcon(QIcon("GUI/icons/tinder.png"))
        if parsed_args.css:
            self.updateStyle()
        else:
            if sys.platform!='darwin':
                self.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())

        # self.startMainWindow(True)
        self.startLoginWindow()

    def export_people_data_csv(self, csv_filename, people_data, keys_to_export):
        with open(csv_filename, mode='r') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=',', quotechar='"',
                                    quoting=csv.QUOTE_MINIMAL)
            for person in people_data:
                for key in person.keys():
                    to_write = []
                    if key in keys_to_export:
                        to_write = to_write + person[key]
                if len(to_write) > 0:
                    csv_writer.writerow(to_write)

    def updateData(self, list_to_fill, downloaded_data, file_path):
        if list_to_fill is not None and isinstance(list_to_fill, list):
            list_to_fill.append(downloaded_data)
            data_to_dump = list_to_fill
        else:
            data_to_dump = downloaded_data
        try:
            with open(file_path, 'w') as fp:
                json.dump(data_to_dump, fp)
            log.i("API", "Data written to: " + file_path)
        except Exception as e:
            log.e("API", "Exception saving " + file_path + " json: " + str(e))

    def get_api_data(self, doAsync=False, api_fun=None, args=[], kwargs={}, finished_callback=None, update_callback=None, info=None, tag=None):
        if not doAsync:
            kwargs["log_to_widget"] = False
            kwargs["thread_update_signal"] = None
            result = api_fun(*args, **kwargs)
            self.new_data_callback(result, finished_callback)
        else:
            obj = APIBackgroundWorker(api_fun, args, kwargs, callback=finished_callback)
            if tag is not None:
                obj.tag = tag
            obj.signals.dataReceived.connect(self.new_data_callback)  # 2 - Connect Worker`s Signals to Form method slots to post data.
            if update_callback is None:
                update_callback = self.updateBackgroundTaskInfo
            obj.signals.dataUpdate.connect(update_callback)  # 2 - Connect Worker`s Signals to Form method slots to post data.
            if info is None:
                self.addBackgroundTask(obj, "Getting Data from API: " +str(info))
            else:
                self.addBackgroundTask(obj, info)

    def read_profile(self, doAsync=True):
        self.get_api_data(doAsync, self.tinder_api.get_self,
                          [], {},
                          finished_callback=self.setProfileData,
                          update_callback=self.updateBackgroundTaskInfo,
                          info="Getting profile data",
                          tag="ProfileGetter")
    def setProfileData(self, new_data, force_overwrite=True):
        self.profile_info = new_data
        self.get_api_data(True, self.tinder_api.download_people_data_api,
                                [self.profile_info, self.profile_folder, False, 0],
                                {"force_overwrite": force_overwrite},
                                finished_callback=self.updateProfile,
                                update_callback=self.updateBackgroundTaskInfo,
                                info="Downloading Profile data to: " + str(self.profile_folder),
                                tag="ProfileDownloader")
    def updateProfile(self, downloaded_data):
        pass

    def get_matches(self, doAsync=True):
        self.get_api_data(doAsync, self.tinder_api.all_matches,
                          finished_callback=self.setNewMatches,
                          info="Getting new Matches")
    def setNewMatches(self, data):
        if 'data' in data:
            self.new_matches = data['data']['matches']
            self.updateMatchesWidgets(False, True)
    def read_matches(self, doAsync=False):
        self.get_api_data(doAsync, self.tinder_api.read_data, [self.matches_file],
                          info="Reading data from: " + str(self.matches_file),
                          finished_callback=self.setMatches,
                          tag="MatchesDownloader")
    def reload_matches(self, doAsync=False, force_overwrite=False):
        self.get_api_data(doAsync, self.tinder_api.reload_data_from_disk,
                          [self.matches_folder, self.matches_file],
                          {"force_overwrite": force_overwrite},
                          finished_callback=self.setMatches,
                          update_callback=self.updateBackgroundTaskInfo,
                          info="Reloading Matches",
                          tag="MatchesReloader")
    def download_new_matches(self,  rename_images, amount, force_overwrite=False):
        self.get_api_data(True, self.tinder_api.download_people_data_api,
                          [self.new_matches, self.matches_folder, rename_images, amount],
                          {"force_overwrite": force_overwrite},
                          finished_callback=self.updateMatches,
                          update_callback=self.updateBackgroundTaskInfo,
                          info="Downloading Matches data to: " + str(self.matches_folder),
                          tag="MatchesDownloader")
    def setMatches(self, data):
        log.d("APP", "updateMatches called")
        self.new_matches = None
        self.matches = data
        self.updateMatchesWidgets()
    def updateMatches(self, downloaded_data):
        self.updateData(self.matches, downloaded_data, self.matches_file)
        self.updateMatchesWidgets()
    def updateMatchesWidgets(self, updateList=True, updateWidgets=True):
        if self.window is not None:
            if updateList:
                self.window.matches_list.update_list(self.matches)
            if updateWidgets:
                self.window.features_panel.update_matches_widgets()


    def get_recommendations(self, doAsync=True):
        self.get_api_data(doAsync, self.tinder_api.get_recs_v2,
                              finished_callback=self.setNewRecommendations,
                              info="Getting new Recommendations")
    def setNewRecommendations(self, data):
        if 'data' in data:
            self.new_recommendations = data['data']['results']
            self.updateRecommendationsWidgets(False, True)
    # Read recommendations.json file containing all recommendations
    def read_recommendations(self, doAsync=False):
        self.get_api_data(doAsync, self.tinder_api.read_data, [self.recommendations_file],
                          info="Reading data from: " + str(self.recommendations_file),
                          finished_callback=self.setRecommendations,
                          tag="RecomendationsDownloader")
    # Redownload recommendations and writes the output to file file containing all recommendations
    def reload_recommendations(self, doAsync=False, force_overwrite=False):
        self.get_api_data(doAsync, self.tinder_api.reload_data_from_disk,
                          [self.recommendations_folder, self.recommendations_file],
                          {"force_overwrite": force_overwrite},
                          finished_callback=self.setRecommendations,
                          update_callback=self.updateBackgroundTaskInfo,
                          info="Reloading Recommendations",
                          tag="RecommendationsReloader")
    def download_new_recommendations(self, rename_images, amount, force_overwrite=False):
        self.get_api_data(True, self.tinder_api.download_people_data_api,
                          [self.new_recommendations, self.recommendations_folder, rename_images, amount],
                          {"force_overwrite": force_overwrite},
                          finished_callback=self.updateRecommendations,
                          update_callback=self.updateBackgroundTaskInfo,
                          info="Downloading Recommendations data to: " + str(self.matches_folder),
                          tag="RecommendationsDownloader")
    def setRecommendations(self, data):
        log.d("APP", "setRecommendations called")
        self.new_recommendations = None
        self.recommendations = data
        self.updateRecommendationsWidgets()
    def updateRecommendations(self, downloaded_data):
        self.updateData(self.recommendations, downloaded_data, self.recommendations_file)
        self.updateRecommendationsWidgets()
    def updateRecommendationsWidgets(self, updateList=True, updateWidgets=True):
        if self.window is not None:
            if updateList:
                self.window.recommendations_list.update_list(self.recommendations)
            if updateWidgets:
                self.window.features_panel.update_recommendations_widgets()


    def get_match_info(self, id, name):
        self.get_api_data(True, self.tinder_api.get_person, [id], finished_callback=self.person_data_received,
                          info="Getting data of " +str(name + "_"+ str(id)))

    def person_data_received(self, data):
        self.window.json_view.load_data(data["data"])
        log.d("PERSON_DATA", +str(data))

    def new_data_callback(self, data, callback, async_data=None, time_started=None, tag=None):
        if async_data is not None:
            self.completeBackgroundTask(async_data + ": completed! ", tag=tag)
        if time_started is not None:
            print(async_data + " execution time: " + str(time.time() - time_started) + "s")
        if callback is not None:
            callback(data)

    def updateStyle(self):
        log.i("APP", "Update style!")
        try:
            with open('./style.css', 'r') as cssfile:
                self.setStyleSheet(cssfile.read())
        except Exception as e:
            log.e("APP", "Update style Exception")

    def startLoginWindow(self):
        self.window = lw.LoginWindow(self, self.background_info, self.background_count_label, self.spinner, parsed_args)
        self.window.show()
        if self.config:
            self.window.form_widget.verify_login(True)

    def verify_login(self, doAsync, callback):
        log.i("APP", "Config File: " + str(os.path.abspath(self.config_file)))
        log.i("APP", "Verify login: " + str(self.config))
        self.get_api_data(doAsync, self.tinder_api.authverif,
                          [self.config['facebook']['auth_token'], self.config['facebook']['user_id']],
                          finished_callback=callback, info="Verifying login",
                          tag="LoginVerifier")

    def login_verified(self, isVerified, openMainWindow=False):
        self.logged_in = isVerified
        QApplication.processEvents()
        if openMainWindow:
            with open(self.config_file, 'w') as fy:
                yaml.dump(self.config, fy)
            self.startMainWindow(True)
        self.update_status_bar()

    def update_status_bar(self):
        if self.logged_in:
            log.i("APP", "Login verified!")
            self.window.statusBar.showMessage("Login verified!")
            self.window.setWindowTitle("TinderAI (Online)")
        else:
            log.i("APP", "Login FAILED!")
            self.window.statusBar.showMessage("Login FAILED!")
            self.window.setWindowTitle("TinderAI (OFFLINE)")

    def startMainWindow(self, doAsync=False):
        if self.window is not None:
            self.window.close()
        if self.config:
            self.window = mw.MainWindow(self, self.background_info, self.background_count_label, self.spinner, parsed_args)
            self.window.show()
            self.update_status_bar()
            self.read_recommendations(doAsync)
            self.read_matches(doAsync)
            self.read_profile(doAsync) #it should be None at the beginning, triggering the get_self_data
        else:
            self.window = lw.LoginWindow(self, parsed_args)
            self.window.show()
            self.window.form_widget.statusBar.showMessage("No config file found, login again")

    def addBackgroundTask(self, task, info=""):
        if task.tag is not None:
            while task.tag in self.background_tasks_list:
                string_matches = re.match(r"(.*)([0-9]+)", task.tag)
                if string_matches is not None:
                    # print("string_matches: " +str(string_matches.groups()))
                    task.tag = string_matches.group(1)+str(int(string_matches.group(2))+1)
                else:
                    task.tag += "_1"
            self.background_tasks_list.append(task.tag)
        self.updateBackgroundTaskInfo(info)
        self.background_count_total += 1
        if self.background_count_total <= 1:
            self.spinner.showSpinner()
            self.background_count_label.setVisible(True)
        self.updateBackgroundTaskCount()
        log.d("THREADS", "Added new background task " +str(info) +" " +str(self.background_completed) + "/" + str(self.background_count_total) +" Tasks: " +str(self.background_tasks_list), False)
        self.thread_pool.start(task)

    def completeBackgroundTask(self, info="", tag=None):
        self.updateBackgroundTaskInfo(info)
        if tag is not None and tag in self.background_tasks_list:
            self.background_tasks_list.remove(tag)
        self.background_completed += 1
        if self.background_completed >= self.background_count_total:
            self.background_count_total = 0
            self.background_completed = 0
            self.spinner.hideSpinner()
            self.updateBackgroundTaskInfo("All tasks completed!")
            self.background_count_label.setVisible(False)
        self.updateBackgroundTaskCount()
        log.d("THREADS", "Completed background task " +str(info) +" " +str(self.background_completed) + "/" + str(self.background_count_total) +" Tasks: " +str(self.background_tasks_list), False)

    def updateBackgroundTaskCount(self):
        self.background_count_label.setText(str(self.background_completed) +"/"+str(self.background_count_total))

    def updateBackgroundTaskInfo(self, text=""):
        self.background_info.setText(str(text))

class ConfigSingleton:
    __instance__ = None
    yaml_config_file = "./settings.yaml"
    try:
        yaml_config = yaml.safe_load(open(yaml_config_file))
    except Exception:
        yaml_config = None

    def __init__(self):
        """ Constructor. """
        if ConfigSingleton.__instance__ is None:
            ConfigSingleton.__instance__ = self
        else:
            raise Exception("You cannot create another SingletonGovt class")

    def get_instance():
        """ Static method to fetch the current instance. """
        if not ConfigSingleton.__instance__:
            ConfigSingleton()
        return ConfigSingleton.__instance__


def process_cl_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--css',  action='store_true', help='Reloads the CSS at each event, used for styling purposes')  # optional flag
    parsed_args, unparsed_args = parser.parse_known_args()
    return parsed_args, unparsed_args

"""
THIS IS SUPER IMPORTANT IN PYQT5 APPS
Without this, python won't print any unhandled exception since they happen within the app.exec_()
"""
def trap_exc_during_debug(*args):
    exc_type, exc_value, exc_traceback = sys.exc_info()
    log.e("MAIN", "General Exception: " +str(args))
    traceback.print_tb(exc_traceback, limit=None, file=sys.stdout)

if __name__ == '__main__':
    # install exception hook: without this, uncaught exception would cause application to exit
    sys.excepthook = trap_exc_during_debug
    parsed_args, unparsed_args = process_cl_args()
    # QApplication expects the first argument to be the program name.
    qt_args = sys.argv[:1] + unparsed_args

    with open("./fault_handler.log", "w") as fobj:
        faulthandler.enable(fobj)
        app = TinderApp(parsed_args, qt_args)
        app.exec_()