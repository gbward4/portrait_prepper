from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot


class MainController():
    """ Main Controller Class """

    def __init__(self, view):
        self.view = view

        self.view.signals.image_reverse_state_changed.connect(self.update_reverse_image)
        self.view.signals.save_image.connect(self.save_image)
        self.view.signals.load_image.connect(self.load_image)
        self.view.signals.composite_sliders_updated.connect(self.update_sliders)

    def setup(self):
        """ Some setup actions to do before opening Main Window """

    def save_image(self, file_path):
        breakpoint()

    def load_image(self, file_path):
        breakpoint()

    def update_sliders(self, shadow_slider, midtone_slider, fleshtone_slider):
        breakpoint()

    def update_reverse_image(self, checkbox):
        breakpoint()
        if checkbox.isChecked():
            pass
