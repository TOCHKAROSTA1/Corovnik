import cv2
import numpy as np  

def bytes_to_cvimage(image_bytes):
    # Преобразование байтов в numpy массив
    nparr = np.frombuffer(bytes.fromhex(image_bytes), np.uint8)
    # Декодирование изображения
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return img
