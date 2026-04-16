from PyQt6.QtWidgets import QApplication, QMainWindow

from giaodien import Ui_MainWindow


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # Gan su kien cho nut bam
        self.ui.btnSayHello.clicked.connect(self.say_hello)

    def say_hello(self) -> None:
        name = self.ui.txtName.text().strip()
        if not name:
            self.ui.lblResult.setText("Ban chua nhap ten.")
            return
        self.ui.lblResult.setText(f"Xin chao, {name}!")


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
