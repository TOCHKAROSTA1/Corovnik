#include <SPI.h>
#include <MFRC522.h>
#include <GyverHX711.h>
//#include <GyverBME280.h>                      // Подключение библиотеки
#include <Servo.h>
#include "OneButton.h"
OneButton button;
Servo servo1;
Servo servo2;
//GyverBME280 bme;
#include <Adafruit_MLX90614.h>

Adafruit_MLX90614 mlx = Adafruit_MLX90614();
GyverHX711 sensor(3, 2, HX_GAIN64_A);

#define RE_DE_PIN 7  // GPIO5 для управления DE/RE

const int measureCount = 10;
unsigned long lastMeasureTime = 0;
int measureInterval = 100;  // 100 мс = 10 измерений в секунду

int count = 0;
float sum = 0;
const unsigned long MEASURE_INTERVAL1 = 100;  // Интервал между измерениями (100 мс = 10 измерений/сек)
const int MEASURE_COUNT1 = 10;                // Количество измерений для усреднения

unsigned long lastMeasureTime1 = 0;
float sum1 = 0;
int count1 = 0;
float average1 = 0;

#define RST_PIN 5
#define SS_PIN 10

MFRC522 mfrc522(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);
  pinMode(RE_DE_PIN, OUTPUT);
  Serial1.begin(9600);
  digitalWrite(RE_DE_PIN, 1);  // Режим приёма
  servo1.attach(9);
  servo2.attach(8);
  SPI.begin();
  button.setup(6, INPUT_PULLUP, true);
  delay(500);
  sensor.tare();
  //  pinMode(7, INPUT_PULLUP);
  mfrc522.PCD_Init();
  mlx.begin();
  button.attachClick(clickb);
  button.attachDoubleClick(doubleclick);
  servo1.write(90);
  servo2.write(90);

  // link the doubleclick function to be called on a doubleclick event.
}
int average;
bool flag = false;
bool up = false;
void clickb() {
  up = true;
}

void doubleclick() {
  digitalWrite(RE_DE_PIN, 1);  // Режим приёма
  Serial1.println("DATA");
  digitalWrite(RE_DE_PIN, 0);  // Режим приёма
}

void loop() {
  unsigned long currentTime = millis();
  if (sensor.available() && (currentTime - lastMeasureTime >= measureInterval)) {
    lastMeasureTime = currentTime;

    float weight = sensor.read() / 190.000;  // приведение к float для точности
    sum += weight;
    count++;

    if (count >= measureCount) {
      average = sum / measureCount;
            // сброс накопителей
      count = 0;
      sum = 0;
    }
  }
  if (currentTime - lastMeasureTime1 >= MEASURE_INTERVAL1) {
    lastMeasureTime1 = currentTime;

    float temperature = mlx.readObjectTempC();
    sum1 += temperature;
    count1++;

    if (count1 >= MEASURE_COUNT1) {
      average1 = sum1 / MEASURE_COUNT1;
      

      // Сброс накопителей
      count1 = 0;
      sum1 = 0;
    }
  }
  if (Serial1.available()) {
    String data = Serial1.readString();
    Serial.print("2," + data);
  }
  button.tick();
  if (!mfrc522.PICC_IsNewCardPresent() || !mfrc522.PICC_ReadCardSerial()) {
    return;
  }
  servo1.write(180);
  if (!up) {

    // Конвертация 4 байт UID в unsigned long (32 бита)
    unsigned long uid_hex = 0;
    for (byte i = 0; i < 4; i++) {  // Берём первые 4 байта (для 7-байтных UID нужно изменить логику)
      uid_hex = (uid_hex << 8) | mfrc522.uid.uidByte[i];
    }
   // digitalWrite(8, 1);
    /*while (!flag) {
      myservo.write(map(analogRead(A0), 0, 1023, 0, 180));
      button.tick();
    }*/
    flag = false;
    //    myservo.write(0);
    digitalWrite(8, 0);
    Serial.print("0,");
    Serial.print(uid_hex);
    Serial.print(",");
    Serial.print(average);
    Serial.print(",");
    Serial.println(average1);
    servo2.write(0);

  } else {
    // Конвертация 4 байт UID в unsigned long (32 бита)
    unsigned long uid_hex = 0;
    for (byte i = 0; i < 4; i++) {  // Берём первые 4 байта (для 7-байтных UID нужно изменить логику)
      uid_hex = (uid_hex << 8) | mfrc522.uid.uidByte[i];
    }
 //   digitalWrite(8, 1);
    /* while (!flag) {
      myservo.write(map(analogRead(A0), 0, 1023, 0, 180));
      button.tick();
    }*/
    flag = false;
    //    myservo.write(0);
    digitalWrite(8, 0);
    Serial.print("1,");
    Serial.print(uid_hex);
    Serial.print(",");
    Serial.print(average);
    Serial.print(",");
    Serial.println(average1);
    up = false;
    servo2.write(0);
  }
  delay(2000);
  servo1.write(90);
  servo2.write(90);
  mfrc522.PICC_HaltA();
}
