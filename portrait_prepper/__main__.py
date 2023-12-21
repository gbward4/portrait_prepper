import sys
from PyQt5.QtWidgets import QApplication

from portrait_prepper.view.gui import MainWindow
from portrait_prepper.controller.controller import MainController


def main():
    app = QApplication(sys.argv)
    gui = MainWindow()
    controller = MainController(view=gui)
    controller.setup()
    controller.view.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
