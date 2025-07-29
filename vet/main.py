import utilites.sql as sql, threading as th, cv2
from PyQt5.QtCore import pyqtSignal
from time import sleep as s
from PyQt5 import QtWidgets
from functools import partial
from ui import Ui_MainWindow  # Импортируем сгенерированный класс
from utilites.utilites import *
from utilites.gpt import *
import queue

class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    update_table_signal = pyqtSignal()  # Сигнал с данными
    update_data = pyqtSignal(str)  # Сигнал с данными
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()  # Создаем экземпляр интерфейса
        self.ui.setupUi(self)  # Настраиваем интерфейс
        self.database = sql.sql()
        self.result_queue = queue.Queue()
        self.ai = ""
        self.update_data.connect(self.data)
        self.ui.ok.clicked.connect(self.ok)
        self.ui.send.clicked.connect(self.send)
        self.update_table_signal.connect(self.update_table)
        theard = th.Thread(target=self.updated, daemon=True)
        theard.start() 
        cows = self.database.r("cows")[::-1]  # Получаем все записи
        nutrition = self.database.r("nutrition")
        nutrition_by_id = {n[0]: n[1:] for n in nutrition}  # {id: (mon, tue, wed, ...)}

        self.ui.tableWidget.setRowCount(len(cows))
        self.ui.tableWidget.setColumnCount(17)
        self.ui.tableWidget.setHorizontalHeaderLabels([
    "ID", "RFID", "Имя", "Возраст", "Пол", "Вес", "Температура", "Рекомендации" ,"Фото", "Добавить рекомендацию",
    "Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"
])


        for row_idx, cow in enumerate(cows):
            cow_id = cow[0]

    # Заполняем первые 6 ячеек текстом
            for col_idx in range(8):
                self.ui.tableWidget.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(cow[col_idx])))

    # Кнопка "Показать" в колонке 6
            btn = QtWidgets.QPushButton("Показать")
            btn.clicked.connect(partial(self.show_image, cow[8], row_idx))  # cow[6] — путь к изображению
            self.ui.tableWidget.setCellWidget(row_idx, 8, btn)
            btn1 = QtWidgets.QPushButton("Добавить")
            btn1.clicked.connect(partial(self.rec, cow[1]))  # cow[6] — путь к изображению
            self.ui.tableWidget.setCellWidget(row_idx, 9, btn1)
    # Данные кормления
            if cow_id in nutrition_by_id:
                for day_idx, day_value in enumerate(nutrition_by_id[cow_id]):
                    self.ui.tableWidget.setItem(row_idx, 10 + day_idx, QtWidgets.QTableWidgetItem(str(day_value)))
            else:
                for day_idx in range(7):
                    self.ui.tableWidget.setItem(row_idx, 10 + day_idx, QtWidgets.QTableWidgetItem("-"))
    
    def data(self, daata):
        self.ui.answer.setText(daata)
    def thread(self):
        que = self.ui.question.text()
        self.ui.question.setText("")
        self.ai += f"ВетАссистент: {gpt(que)}"
        self.ai += "\n\n"
        self.update_data.emit(self.ai)


    def send(self):
        g = th.Thread(target=self.thread)
        g.start()

    def updated(self):
        while True:
            s(10)
            self.update_table_signal.emit()

    def update_table(self):
        cows = self.database.r("cows")[::-1]  # Получаем все записи
        nutrition = self.database.r("nutrition")
        nutrition_by_id = {n[0]: n[1:] for n in nutrition}  # {id: (mon, tue, wed, ...)}

        self.ui.tableWidget.setRowCount(len(cows))
        self.ui.tableWidget.setColumnCount(17)
        self.ui.tableWidget.setHorizontalHeaderLabels([
    "ID", "RFID", "Имя", "Возраст", "Пол", "Вес", "Температура", "Рекомендации" ,"Фото", "Добавить рекомендацию",
    "Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"
])


        for row_idx, cow in enumerate(cows):
            cow_id = cow[0]

    # Заполняем первые 6 ячеек текстом
            for col_idx in range(8):
                self.ui.tableWidget.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(cow[col_idx])))

    # Кнопка "Показать" в колонке 6
            btn = QtWidgets.QPushButton("Показать")
            btn.clicked.connect(partial(self.show_image, cow[8], row_idx))  # cow[6] — путь к изображению
            self.ui.tableWidget.setCellWidget(row_idx, 8, btn)
            btn1 = QtWidgets.QPushButton("Добавить")
            btn1.clicked.connect(partial(self.rec, cow[1]))  # cow[6] — путь к изображению
            self.ui.tableWidget.setCellWidget(row_idx, 9, btn1)
    # Данные кормления
            if cow_id in nutrition_by_id:
                for day_idx, day_value in enumerate(nutrition_by_id[cow_id]):
                    self.ui.tableWidget.setItem(row_idx, 10 + day_idx, QtWidgets.QTableWidgetItem(str(day_value)))
            else:
                for day_idx in range(7):
                    self.ui.tableWidget.setItem(row_idx, 10 + day_idx, QtWidgets.QTableWidgetItem("-"))

    def update(self):
        cows = self.database.r("cows")[::-1]  # Получаем все записи
        nutrition = self.database.r("nutrition")
        nutrition_by_id = {n[0]: n[1:] for n in nutrition}  # {id: (mon, tue, wed, ...)}

        self.ui.tableWidget.setRowCount(len(cows))
        self.ui.tableWidget.setColumnCount(17)
        self.ui.tableWidget.setHorizontalHeaderLabels([
    "ID", "RFID", "Имя", "Возраст", "Пол", "Вес", "Температура", "Рекомендации" ,"Фото", "Добавить рекомендацию",
    "Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"
])


        for row_idx, cow in enumerate(cows):
            cow_id = cow[0]

    # Заполняем первые 6 ячеек текстом
            for col_idx in range(8):
                self.ui.tableWidget.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(cow[col_idx])))

    # Кнопка "Показать" в колонке 6
            btn = QtWidgets.QPushButton("Показать")
            btn.clicked.connect(partial(self.show_image, cow[8], row_idx))  # cow[6] — путь к изображению
            self.ui.tableWidget.setCellWidget(row_idx, 8, btn)
            btn1 = QtWidgets.QPushButton("Добавить")
            btn1.clicked.connect(partial(self.rec, cow[1]))  # cow[6] — путь к изображению
            self.ui.tableWidget.setCellWidget(row_idx, 9, btn1)
    # Данные кормления
            if cow_id in nutrition_by_id:
                for day_idx, day_value in enumerate(nutrition_by_id[cow_id]):
                    self.ui.tableWidget.setItem(row_idx, 10 + day_idx, QtWidgets.QTableWidgetItem(str(day_value)))
            else:
                for day_idx in range(7):
                    self.ui.tableWidget.setItem(row_idx, 10 + day_idx, QtWidgets.QTableWidgetItem("-"))

    def show_image(self, path, b):
        img = bytes_to_cvimage(path)
        cv2.imshow("Image", img)
    
    def rec(self, id):
        self.ui.rfid.setText(str(id))
    
    def ok(self):
        rfid = int(self.ui.rfid.text())
        recommendation = self.ui.rec.text()
        self.database.update("cows", rfid, {"vet": recommendation}, "rfid")
        self.update()
        self.ui.rfid.setText("")
        self.ui.rec.setText("")

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()