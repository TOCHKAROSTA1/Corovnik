import cv2
import numpy as np

def compare_objects(img1_path, img2_path):
    # Загрузка изображений
    img1 = cv2.imread(img1_path, cv2.IMREAD_COLOR)
    img2 = cv2.imread(img2_path, cv2.IMREAD_COLOR)
    
    # Преобразование в оттенки серого
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    
    # Инициализация детектора ORB (можно использовать SIFT, SURF и др.)
    orb = cv2.ORB_create()
    
    # Нахождение ключевых точек и дескрипторов
    kp1, des1 = orb.detectAndCompute(gray1, None)
    kp2, des2 = orb.detectAndCompute(gray2, None)
    
    # Создание объекта BFMatcher
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
    
    # Сопоставление дескрипторов
    matches = bf.match(des1, des2)
    
    # Сортировка matches по расстоянию
    matches = sorted(matches, key=lambda x: x.distance)
    
    # Визуализация результатов (опционально)
    result = cv2.drawMatches(gray1, kp1, gray2, kp2, matches[:10], None, flags=2)
    
    # Сохранение или отображение результата
    cv2.imwrite('matches.jpg', result)
    
    # Возвращаем количество совпадений и среднее расстояние между ними
    return len(matches), sum(m.distance for m in matches) / len(matches) if matches else 0

# Пример использования
num_matches, avg_distance = compare_objects('2.jpg', '3.jpg')
print(f"Найдено совпадений: {num_matches}, Среднее расстояние: {avg_distance}")