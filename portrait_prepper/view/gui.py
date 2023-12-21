from PyQt5.QtWidgets import QMainWindow, QLabel, QSlider, QVBoxLayout, QWidget, QAction, QFileDialog, QHBoxLayout, QCheckBox
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot

class MainWindowSignals(QObject):
    image_reverse_state_changed = pyqtSignal(object)
    composite_sliders_updated = pyqtSignal()
    save_image = pyqtSignal(str)
    load_image = pyqtSignal(str)
    update_reference_image = pyqtSignal(object)
    update_composite_image = pyqtSignal(object)
    update_histogram = pyqtSignal(object)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.signals = MainWindowSignals()

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

        # Sliders        
        self.shadow_slider = self.create_labeled_slider("Shadow:", Qt.Horizontal)
        self.shadow_slider.slider.setRange(0, 100)
        self.shadow_slider.slider.setValue(25)
        self.shadow_slider.slider.valueChanged.connect(self.update_composite_sliders)

        self.midtone_slider = self.create_labeled_slider("Midtone:", Qt.Horizontal)
        self.midtone_slider.slider.setRange(0, 100)
        self.midtone_slider.slider.setValue(50)
        self.midtone_slider.slider.valueChanged.connect(self.update_composite_sliders)

        self.fleshtone_slider = self.create_labeled_slider("Fleshtone:", Qt.Horizontal)
        self.fleshtone_slider.slider.setRange(0, 100)
        self.fleshtone_slider.slider.setValue(75)
        self.fleshtone_slider.slider.valueChanged.connect(self.update_composite_sliders)

        # Buttons
        self.checkbox_img_reverse = QCheckBox("Reverse Image", self)
        self.checkbox_img_reverse.setChecked(True)
        self.checkbox_img_reverse.stateChanged.connect(self.checkbox_reverse_state_changed)

        # Layout
        central_widget = QWidget(self)
        main_layout = QVBoxLayout(central_widget)

        settings_layout = QVBoxLayout() 
        settings_layout.addWidget(self.checkbox_img_reverse)
        settings_layout.addWidget(self.histogram_label)

        images_layout = QHBoxLayout()
        images_layout.addWidget(self.composite_image_label)
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

        self.setWindowTitle('Portrait Prepper')
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
        self.signals.image_reverse_state_changed.emit(self.checkbox_img_reverse)

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

    def update_reference_image(self, image):
        self.reference_image_label.setPixmap(image)

    def update_composite_image(self, image):
        self.composite_image_label.setPixmap(image)

    def update_histogram(self, image):
        self.histogram_label.setPixmap(image)
