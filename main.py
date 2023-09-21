import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from ui import Ui_MainWindow

def main():
    app = QApplication(sys.argv)
    m = Ui_MainWindow()
    w = QMainWindow()
    m.setupUi(w)
    w.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
