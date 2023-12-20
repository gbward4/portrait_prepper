import os
import sys
import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageEnhance, ImageOps, ImageQt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QSlider, QVBoxLayout, QWidget, QAction, QFileDialog, QHBoxLayout, QCheckBox
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtCore import Qt, pyqtRemoveInputHook

class PictureEditor(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        # Menu Bar
        menubar = self.menuBar()
        file_menu = menubar.addMenu('File')

        open_action = QAction('Open', self)
        open_action.triggered.connect(self.open_image)
        file_menu.addAction(open_action)

        save_action = QAction('Save', self)
        save_action.triggered.connect(self.save_image)
        file_menu.addAction(save_action)

        exit_action = QAction('Exit', self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Image Display
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        # Original Image Display
        self.reference_image_label = QLabel(self)
        self.reference_image_label.setAlignment(Qt.AlignCenter)

        # Histogram Display
        self.histogram_label = QLabel(self)
        self.histogram_label.setAlignment(Qt.AlignCenter)

        # Sliders        
        self.shadow_slider = self.create_labeled_slider("Shadow:", Qt.Horizontal)
        self.shadow_slider.slider.setRange(0, 100)
        self.shadow_slider.slider.setValue(25)
        self.shadow_slider.slider.valueChanged.connect(self.update_image)

        self.midtone_slider = self.create_labeled_slider("Midtone:", Qt.Horizontal)
        self.midtone_slider.slider.setRange(0, 100)
        self.midtone_slider.slider.setValue(50)
        self.midtone_slider.slider.valueChanged.connect(self.update_image)

        self.fleshtone_slider = self.create_labeled_slider("Fleshtone:", Qt.Horizontal)
        self.fleshtone_slider.slider.setRange(0, 100)
        self.fleshtone_slider.slider.setValue(75)
        self.fleshtone_slider.slider.valueChanged.connect(self.update_image)

        # Buttons
        self.checkbox_reverse = QCheckBox("Reverse Image", self)
        self.checkbox_reverse.setChecked(True)
        self.checkbox_reverse.stateChanged.connect(self.checkbox_reverse_state_changed)

        # Layout
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)

        settings_layout = QVBoxLayout() 
        settings_layout.addWidget(self.checkbox_reverse)
        settings_layout.addWidget(self.histogram_label)

        images_layout = QHBoxLayout()
        images_layout.addWidget(self.image_label)
        images_layout.addWidget(self.reference_image_label)

        labels_layout = QHBoxLayout()
        labels_layout.addLayout(images_layout)
        labels_layout.addLayout(settings_layout)

        sliders_layout = QVBoxLayout()
        sliders_layout.addWidget(self.shadow_slider)
        sliders_layout.addWidget(self.midtone_slider)
        sliders_layout.addWidget(self.fleshtone_slider)

        main_layout.addLayout(labels_layout)
        main_layout.addLayout(sliders_layout)

        self.setCentralWidget(central_widget)

        self.original_image = None

        self.setWindowTitle('Picture Editor')
        self.setGeometry(100, 100, 800, 600)

    def create_labeled_slider(self, label_text, orientation):
        # Create a QLabel for the slider label
        label = QLabel(label_text)

        # Create a QSlider
        slider = QSlider(orientation)
        slider.setRange(0, 100)
        slider.setValue(50)  # Default value

        # Create a layout for the label and slider
        slider_layout = QVBoxLayout()
        slider_layout.addWidget(label)
        slider_layout.addWidget(slider)

        # Create a container widget to hold the label and slider layout
        container_widget = QWidget()
        container_widget.setLayout(slider_layout)
        container_widget.slider = slider

        return container_widget

    def checkbox_reverse_state_changed(self):
        self.original_image = self.original_image.transpose(Image.Transpose.FLIP_LEFT_RIGHT)
        self.display_reference_image(self.original_image)
        self.update_image()

    def open_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Open Image', '', 'Image Files (*.png *.jpg *.jpeg *.bmp *.gif)')

        if file_path:
            self.original_image = Image.open(file_path)
            # TODO Hack
            self.original_image = ImageOps.autocontrast(self.original_image, 0.0)

            if self.checkbox_reverse.isChecked():
                self.checkbox_reverse_state_changed()

            self.display_image(self.original_image)
            self.update_image()

    def save_image(self):
        # Todo handle no image
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, 'Save Image', 'composite', 'Image Files (*.png)')

        self.composite_image.save(file_path)

        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, 'Save Histogram', 'histogram', 'Image Files (*.png)')
        self.histogram.save(file_path)


