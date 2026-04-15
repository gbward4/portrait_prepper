from importlib import resources
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QMainWindow, QLabel, QSlider, QVBoxLayout, QWidget, QAction, QFileDialog, QHBoxLayout, QCheckBox, QColorDialog, QPushButton
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot, QSize


class MainWindowSignals(QObject):
    image_reverse_state_changed = pyqtSignal()
    autocontrast_state_changed = pyqtSignal()
    composite_sliders_updated = pyqtSignal()
    save_image = pyqtSignal(str)
    load_image = pyqtSignal(str)
    update_reference_image = pyqtSignal(object)
    update_composite_image = pyqtSignal(object)
    update_histogram = pyqtSignal(object)
    update_color_scheme = pyqtSignal(object)
    update_layer_color = pyqtSignal(int, QColor)
    delete_layer_request = pyqtSignal(int)

def get_button(icon_path, icon_size=25):
    button = QPushButton()
    button.setIcon(QIcon(str(icon_path)))
    button.setIconSize(QSize(icon_size, icon_size))

    return button


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.signals = MainWindowSignals()
        # self.sliders = []

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

        # Composite Image Display
        self.composite_image_label = QLabel(self)
        self.composite_image_label.setAlignment(Qt.AlignCenter)
        self.signals.update_composite_image.connect(self.update_composite_image)

        # Reference Image Display
        self.reference_image_label = QLabel(self)
        self.reference_image_label.setAlignment(Qt.AlignCenter)
        self.signals.update_reference_image.connect(self.update_reference_image)

        # Histogram Display
        self.histogram_label = QLabel(self)
        self.histogram_label.setAlignment(Qt.AlignCenter)
        self.signals.update_histogram.connect(self.update_histogram)

        # Add button
        self.add_button = get_button(icon_path=resources.files("portrait_prepper.resources") / "add.png")

        # Sliders        
        # num_sliders_default = 8

        # for idx in range(num_sliders_default):
        #     slider_group = self.get_slider_group("")
        #     slider_group.slider.setRange(0, 100)
        #     slider_spacing = int(100 / (num_sliders_default + 1))
        #     slider_group.slider.setValue((idx + 1) * slider_spacing)
        #     slider_group.slider.valueChanged.connect(self.update_composite_sliders)
        #     slider_group.layer_identity = idx  # lazy attr assigning a layer identity I pick up in controller later.  Should be a class attr, but meh for now
        #     slider_group.btn_palette.clicked.connect(lambda _, i=idx: self.change_layer_color_requested(i))
        #     slider_group.btn_trash.clicked.connect(lambda _, i=idx: self.delete_layer_requested(i))
        #     self.sliders.append(slider_group)

        self.checkbox_img_reverse = QCheckBox("Reverse Image", self)
        self.checkbox_img_reverse.setChecked(True)
        self.checkbox_img_reverse.stateChanged.connect(self.checkbox_reverse_state_changed)

        self.checkbox_autocontrast = QCheckBox("Autocontrast Image", self)
        self.checkbox_autocontrast.setChecked(True)
        self.checkbox_autocontrast.stateChanged.connect(self.autocontrast_state_changed)

        # Layout
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)

        settings_layout = QVBoxLayout() 
        settings_layout.addWidget(self.checkbox_img_reverse)
        settings_layout.addWidget(self.checkbox_autocontrast)
        settings_layout.addWidget(self.histogram_label)
        settings_layout.addWidget(self.add_button)

        images_layout = QHBoxLayout()
        images_layout.addWidget(self.composite_image_label)
        images_layout.addWidget(self.reference_image_label)

        labels_layout = QHBoxLayout()
        labels_layout.addLayout(images_layout)
        labels_layout.addLayout(settings_layout)

        self.sliders_layout = QVBoxLayout()
        # for slider_group in self.sliders:
        #     sliders_layout.addWidget(slider_group)

        main_layout.addLayout(labels_layout)
        main_layout.addLayout(self.sliders_layout)

        self.setCentralWidget(central_widget)

        self.setWindowTitle('Portrait Prepper')
        self.setGeometry(100, 100, 800, 600)

    def change_layer_color_requested(self, layer_idx):
        color = self.show_color_dialog()
        self.signals.update_layer_color.emit(layer_idx, color)

    def delete_layer_requested(self, layer_idx):
        self.signals.delete_layer_request.emit(layer_idx)

    def show_color_dialog(self):
        color_dialog = QColorDialog(self)
        color_dialog.setOption(QColorDialog.DontUseNativeDialog)

        color = color_dialog.getColor()

        if color.isValid():
            return color

    # def get_slider_group(self, label_text):
    #     label = QLabel(label_text)

    #     slider = QSlider(Qt.Horizontal)
    #     slider.setRange(0, 100)
    #     slider.setValue(50)  # Default value

    #     btn_trash = get_button(icon_path=resources.files("portrait_prepper.resources") / "trash.png")
    #     btn_palette = get_button(icon_path=resources.files("portrait_prepper.resources") / "pallette.png")

    #     slider_layout = QHBoxLayout()
    #     slider_layout.addWidget(label)
    #     slider_layout.addWidget(slider)

    #     slider_layout.addWidget(btn_trash)
    #     slider_layout.addWidget(btn_palette)

    #     slider_group = QWidget()
    #     slider_group.setLayout(slider_layout)
    #     slider_group.slider = slider
    #     slider_group.btn_palette = btn_palette
    #     slider_group.btn_trash = btn_trash

    #     return slider_group

    def checkbox_reverse_state_changed(self):
        self.signals.image_reverse_state_changed.emit()

    def autocontrast_state_changed(self):
        self.signals.autocontrast_state_changed.emit()

    def update_composite_sliders(self):
        self.signals.composite_sliders_updated.emit()

    def open_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, 'Open Image', '', 'Image Files (*.png *.jpg *.jpeg *.bmp *.gif)')

        if file_path:
            self.signals.load_image.emit(file_path)

    def save_image(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getSaveFileName(self, 'Save Image', 'composite', 'Image Files (*.png)')

        if file_path:
            self.signals.save_image.emit(file_path)

    def update_reference_image(self, pixmap):
        scaled_size = pixmap.size().scaled(600, 600, Qt.KeepAspectRatio)
        pixmap_scaled = pixmap.scaled(scaled_size, Qt.KeepAspectRatio)
        self.reference_image_label.setPixmap(pixmap_scaled)

    def update_composite_image(self, pixmap):
        scaled_size = pixmap.size().scaled(600, 600, Qt.KeepAspectRatio)
        pixmap_scaled = pixmap.scaled(scaled_size, Qt.KeepAspectRatio)
        self.composite_image_label.setPixmap(pixmap_scaled)

    def update_histogram(self, image):
        self.histogram_label.setPixmap(image)

class SliderGroup(QWidget):

    def __init__(self, layer_identity, value, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.layer_identity = layer_identity
        self.color = None
        self.label = None
        self.slider_value = value

        self.slider = None
        self.btn_palette = None
        self.btn_trash = None

        self.open()

    def open(self):
        # label = QLabel(self.label)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(self.slider_value)

        btn_trash = get_button(icon_path=resources.files("portrait_prepper.resources") / "trash.png")
        btn_palette = get_button(icon_path=resources.files("portrait_prepper.resources") / "pallette.png")

        slider_layout = QHBoxLayout()
        # slider_layout.addWidget(label)
        slider_layout.addWidget(slider)
        slider_layout.addWidget(btn_trash)
        slider_layout.addWidget(btn_palette)

        self.setLayout(slider_layout)

        # Todo fix lazy attrs
        self.slider = slider
        self.btn_palette = btn_palette
        self.btn_trash = btn_trash
