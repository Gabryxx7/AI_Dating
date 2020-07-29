#!/usr/bin/env bash
sudo rm -rf build dist
sudo pyinstaller --onefile --icon=./GUI/icons/tinder.png --clean -w tinderApp.py