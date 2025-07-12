#!/bin/sh

.PHONY: venv install build clean
PROJECT_NAME := KiRest
SRC_DIR := src
RESOURCE_DIR := res
BUILD_DIR := build
DIST_DIR := dist

ifeq ($(OS),Windows_NT)
    OS := windows
else
    UNAME_S := $(shell uname -s)
    ifeq ($(UNAME_S),Linux)
        OS := linux
    endif
    ifeq ($(UNAME_S),Darwin)
        OS := mac
    endif
endif

MAIN := $(SRC_DIR)/main.py 

VENV_DIR := venv
ifeq ($(OS),windows)
    PYTHON=python.exe
    VENV_PYTHON := $(VENV_DIR)/Scripts/python.exe
    VENV_PYTHONINSTALLER := $(VENV_DIR)/Scripts/pyinstaller.exe
    RM := rmdir
else
    PYTHON=python3
    VENV_PYTHON := $(VENV_DIR)/bin/python
    VENV_PYTHONINSTALLER := $(VENV_DIR)/bin/pyinstaller
    RM := rm
endif

run:
	@$(VENV_PYTHON) $(MAIN)

build: install
	@$(VENV_PYTHON) $(MAIN)

venv:
	@$(PYTHON) -m venv $(VENV_DIR)
	@$(VENV_PYTHON) -m pip install --upgrade pip
	@$(VENV_PYTHON) -m pip install -r requirements.txt

install: venv
	$(VENV_PYTHON) -m pip install -r requirements.txt 

dist:
	$(VENV_PYTHONINSTALLER) --onefile --noconsole --name $(PROJECT_NAME) $(MAIN)

clean:
ifeq ($(OS),windows)
	@rmdir /s /q $(VENV_DIR)
	@rmdir /s /q "$(SRC_DIR)/__pycache__"
	@rmdir /s /q $(BUILD_DIR)
	@rmdir /s /q $(DIST_DIR)
else
	@rm -rf $(VENV_DIR)
	@rm -rf $(SRC_DIR)/__pycache__
	@rm -rf $(BUILD_DIR)
	@rm -rf $(DIST_DIR)
endif
