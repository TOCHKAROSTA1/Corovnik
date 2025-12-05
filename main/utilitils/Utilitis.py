import cv2
import numpy as np
import serial.tools.list_ports

def bytes_to_cvimage(image_bytes):
    # Преобразование байтов в numpy массив
    nparr = np.frombuffer(bytes.fromhex(image_bytes), np.uint8)
    # Декодирование изображения
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img

def list_port():

# Получить список всех доступных COM-портов
    ports = serial.tools.list_ports.comports()

# Вывести информацию о каждом порте
    ret_port = []
    for port in ports:
        ret_port.append(port.device)
    return ret_port