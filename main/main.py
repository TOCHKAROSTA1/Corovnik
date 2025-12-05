from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
from ui import Ui_MainWindow  # Импортируем сгенерированный класс
from functools import partial
from utilitils.Utilitis import *
from utilitils.bot import *
import cv2, utilitils.sql as sql, serial, logging, threading as th
from time import sleep as s

logging.basicConfig(
    level=logging.DEBUG,  # Уровень логирования
    filename='app.log',   # Файл для записи логов
    filemode='w',         # Режим записи ('a' - дописывать, 'w' - перезаписывать)
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S',
    encoding="UTF-8"
)

class MyWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    update_table_signal = pyqtSignal(list)  # Сигнал с данными
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()  # Создаем экземпляр интерфейса
        self.ui.setupUi(self)  # Настраиваем интерфейс
        self.update_table_signal.connect(self.update_table)
        logging.info("Загружен gui")
        self.database = sql.sql()
        self.bot = Telegram()
        logging.info("Подключена база данных")
        theard = th.Thread(target=self.update, daemon=True)
        theard.start() 
        self.listen = True
        self.ui.com.addItems(list_port())
        self.ui.dele.clicked.connect(self.dele)
        self.ui.con.clicked.connect(self.connect)
        self.serial = None
        self.updaterow = True
        cows = self.database.r("cows")  # Получаем все записи
        nutrition = self.database.r("nutrition")
        nutrition_by_id = {n[0]: n[1:] for n in nutrition}  # {id: (mon, tue, wed, ...)}
        self.old = cows
        self.nut = {}
        self.ui.tableWidget.setRowCount(len(cows))
        self.ui.tableWidget.setColumnCount(17)
        self.ui.tableWidget.setHorizontalHeaderLabels([
    "ID", "RFID", "Имя", "Возраст", "Пол", "Вес", "Разница", "Температура", "Рекомендации", "Фото",
    "Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"
])


        for row_idx, cow in enumerate(cows):
            cow_id = cow[0]
            self.nut[str(cow[1])] = [[False, False]]
            temp = []

    # Заполняем первые 6 ячеек текстом
            for col_idx in range(9):
                self.ui.tableWidget.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(cow[col_idx])))

    # Кнопка "Показать" в колонке 6
            btn = QtWidgets.QPushButton("Показать")
            btn.clicked.connect(partial(self.show_image, cow[9], row_idx))  # cow[6] — путь к изображению
            self.ui.tableWidget.setCellWidget(row_idx, 9, btn)
    # Данные кормления
            if cow_id in nutrition_by_id:
                for day_idx, day_value in enumerate(nutrition_by_id[cow_id]):
                    temp.append(day_value)
                    self.ui.tableWidget.setItem(row_idx, 10 + day_idx, QtWidgets.QTableWidgetItem(str(day_value)))
            else:
                for day_idx in range(7):
                    self.ui.tableWidget.setItem(row_idx, 10 + day_idx, QtWidgets.QTableWidgetItem("-"))
            self.nut[str(cow[1])].append(temp[:3])
            self.nut[str(cow[1])].append(temp[3:])

            for i, d in enumerate(self.nut[str(cow[1])][1]):
                if d == None:
                    self.nut[str(cow[1])][1][i] = temp[i]
                    if i == 2:
                        break
            else:
                nut = self.nut[str(cow[1])][1][::-1]
                if nut[0] != None and nut[1] != None and nut[2] != None:
                    if (nut[0] - nut[1]) > 0.2 and (nut[1] - nut[2]) > 0.2 and self.nut[str(cow[1])][0][0] == False:
                        self.nut[str(cow[1])][0][0] = True
            for i, d in enumerate(self.nut[str(cow[1])][2][3:-1]):
                if d == None:
                    self.nut[str(cow[1])][2][i] = temp[i + 3]
                    if i == 2:
                        break
            else:
                nut = self.nut[str(cow[1])][2][::-1]
                if nut[1] != None and nut[2] != None and nut[3] != None:
                    if (nut[1] - nut[2]) > 0.2 and (nut[2] - nut[3]) > 0.2 and self.nut[str(cow[1])][0][1] == False:
                        self.nut[str(cow[1])][0][1] = True
        logging.debug(self.nut)


                    
    def connect(self):
        item = self.ui.com.currentText()
        self.serial = serial.Serial(item)
        port = th.Thread(target=self.create_record, daemon=True)
        port.start()
        logging.info(f"Подключен порт {item}")

    def update(self):
        while True:
            s(10)
            self.update_table_signal.emit([])

    def update_table(self, records):
        cows = self.database.r("cows")  # Получаем все записи
        nutrition = self.database.r("nutrition")
        nutrition_by_id = {n[0]: n[1:] for n in nutrition}  # {id: (mon, tue, wed, ...)}
        self.old = cows
        self.ui.tableWidget.setRowCount(len(cows))
        self.ui.tableWidget.setColumnCount(17)
        self.ui.tableWidget.setHorizontalHeaderLabels([
    "ID", "RFID", "Имя", "Возраст", "Пол", "Вес", "Разница", "Температура", "Рекомендации", "Фото",
    "Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"
])


        for row_idx, cow in enumerate(cows):
            cow_id = cow[0]
            temp = []

    # Заполняем первые 6 ячеек текстом
            for col_idx in range(9):
                self.ui.tableWidget.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(cow[col_idx])))

    # Кнопка "Показать" в колонке 6
            btn = QtWidgets.QPushButton("Показать")
            btn.clicked.connect(partial(self.show_image, cow[9], row_idx))  # cow[6] — путь к изображению
            self.ui.tableWidget.setCellWidget(row_idx, 9, btn)
    # Данные кормления
            if cow_id in nutrition_by_id:
                for day_idx, day_value in enumerate(nutrition_by_id[cow_id]):
                    temp.append(day_value)
                    self.ui.tableWidget.setItem(row_idx, 10 + day_idx, QtWidgets.QTableWidgetItem(str(day_value)))
            else:
                for day_idx in range(7):
                    self.ui.tableWidget.setItem(row_idx, 10 + day_idx, QtWidgets.QTableWidgetItem("-"))
        try:
            for i, d in enumerate(self.nut[str(cow[1])][1]):
                if d == None:
                    self.nut[str(cow[1])][1][i] = temp[i]
                    if i == 2:
                        break
            else:
                nut = self.nut[str(cow[1])][1][::-1]
                if (nut[0] - nut[1]) > 0.002 and (nut[1] - nut[2]) > 0.002 and self.nut[str(cow[1])][0][0] == False:
                    self.nut[str(cow[1])][0][0] = True
                    logging.debug(self.nut)
                    self.bot.send(f"У коровы с id {cow[1]} Имя коровы {cow[2]} 3 дня питается всё меньше и меньше возможна болезнь")
            for i, d in enumerate(self.nut[str(cow[1])][2][:-1]):
                if d == None:
                    self.nut[str(cow[1])][2][i] = temp[i + 3]
                    if i == 2:
                        break
            else:
                logging.debug(self.nut)
                nut = self.nut[str(cow[1])][2][::-1]
                if (nut[1] - nut[2]) > 0.002 and (nut[2] - nut[3]) > 0.002 and self.nut[str(cow[1])][0][1] == False:
                    self.nut[str(cow[1])][0][1] = True
                    self.bot.send(f"У коровы с id {cow[1]} Имя коровы {cow[2]} 3 дня питается всё меньше и меньше возможна болезнь")
        except:
            pass

    
    def photoo(self):
        cam = cv2.VideoCapture(2)
        _, ret = cam.read()
        cam.release()
        try:
            cv2.imwrite("cow.png", ret)
        except Exception as e:
            logging.error(e)
            logging.info("Повторная попытка сделать фото")
            self.photoo()

    def create_record(self):
        
        while True:
            try:
                rec = self.serial.readline().decode()[:-2]
                
                uid = rec.split(",")
                print(uid)
                database = sql.sql()
                if uid[0] == "0":
                    self.photoo()
                    with open("cow.png", "rb") as file:
                    #self.database.create_record("cows", uid[0], self.ui.name.text(), self.ui.grnder.text(), int(self.ui.old.text()), int(uid[1]) / 1000, file.read().hex())
                        database.create_record("cows", {
                        "RFID": int(uid[1]),
                        "name": self.ui.name.text(),
                        "old": int(self.ui.old.text()),
                        "gender": self.ui.grnder.text(),
                        "weight": int(uid[2]) / 1000,
                        "photo": file.read().hex(),
                        "temp": float(uid[3])
                    })
                        database.create_record("nutrition", {"mon": None})
                        self.nut[uid[1]] = [[False, False], [None, None, None], [None, None, None, None]]
                elif uid[0] == "2":
                    cows = self.database.r("cows") # Получаем все записи
                    
                    nutrition = self.database.r("nutrition")
                    nutrition_by_id = {n[0]: n[1:] for n in nutrition}  # {id: (mon, tue, wed, ...)}
                    for row_idx, cow in enumerate(cows):
                        cow_id = cow[0]
                        cow_rf = database.record("cows", cow_id)[1]
                        if cow_id in nutrition_by_id and cow_rf == int(uid[1]):
                            for day_idx, day_value in enumerate(nutrition_by_id[cow_id]):
                                if day_value == None:
                                    #print(cow_id)
                                    data = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
                                    database.update("nutrition", cow_id, {data[day_idx]: int(uid[2]) / 1000}, "id")
                                    self.update_table_signal.emit(database.r("cows"))
                                    break
                            else:
                                for day_idx, day_value in enumerate(nutrition_by_id[cow_id]):
                                    data = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]
                                    database.update("nutrition", cow_id, {data[day_idx]: None}, "id")
                                database.update("nutrition", cow_id, {"mon": int(uid[2]) / 1000}, "id")
                                for i in range(3):
                                    self.nut[uid[1]][1][i] = None
                                for i in range(4):
                                    self.nut[uid[1]][2][i] = None
                                self.nut[uid[1]] = [[False, False], [None, None, None], [None, None, None, None]]
                else:
                    old = database.record("cows", int(uid[1]), "rfid")[5]
                    c = (int(uid[2]) / 1000) - old
                    if c < 0:
                        self.bot.send(f"Корова {uid[1]} похудела относительно старых данных на {abs(c)}")
                    if float(uid[3]) >= 38.0:
                        self.bot.send(f"У корова {uid[1]} высокая темпиратура {uid[3]}")
                    database.update("cows", uid[1], {
                        "weight": int(uid[2]) / 1000,
                        "weight_change": c,
                        "temp": float(uid[3])
                    }, "rfid")
                self.update_table_signal.emit(database.r("cows"))
                database.close()
            except Exception as e:
                logging.debug(f"{e} {rec} {uid}")

    def closeEvent(self, event):
        try:
            self.serial.close()
        except:
            pass
        self.database.close()

        event.accept()  # Обязательно, чтобы окно действительно закрылось
    
    def show_image(self, path, row):
        img = bytes_to_cvimage(path)
        cv2.imshow("Image", img)

    def dele(self):
        try:
            id = int(self.ui.id.text())
            self.database.delete_record("cows", id)
            self.database.delete_record("nutrition", id)
            cows = self.database.r("cows")  # Получаем все записи
            nutrition = self.database.r("nutrition")
            nutrition_by_id = {n[0]: n[1:] for n in nutrition}  # {id: (mon, tue, wed, ...)}
            self.old = cows

            self.ui.tableWidget.setRowCount(len(cows))
            self.ui.tableWidget.setColumnCount(15)
            self.ui.tableWidget.setHorizontalHeaderLabels([
    "ID", "RFID", "Имя", "Возраст", "Пол", "Вес", "Температура", "Фото",
    "Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"
])


            for row_idx, cow in enumerate(cows):
                cow_id = cow[0]

    # Заполняем первые 6 ячеек текстом
                for col_idx in range(7):
                    self.ui.tableWidget.setItem(row_idx, col_idx, QtWidgets.QTableWidgetItem(str(cow[col_idx])))

    # Кнопка "Показать" в колонке 6
                btn = QtWidgets.QPushButton("Показать")
                btn.clicked.connect(partial(self.show_image, cow[7], row_idx))  # cow[6] — путь к изображению
                self.ui.tableWidget.setCellWidget(row_idx, 7, btn)

    # Данные кормления
                if cow_id in nutrition_by_id:
                    for day_idx, day_value in enumerate(nutrition_by_id[cow_id]):
                        self.ui.tableWidget.setItem(row_idx, 8 + day_idx, QtWidgets.QTableWidgetItem(str(day_value)))
                else:
                    for day_idx in range(7):
                        self.ui.tableWidget.setItem(row_idx, 8 + day_idx, QtWidgets.QTableWidgetItem("-"))
        except:
            pass

if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MyWindow()
    window.show()
    app.exec_()