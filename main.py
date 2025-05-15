import cv2
import numpy as np
from ultralytics import YOLO
from control_drone import Drone
import serial
import serial.tools.list_ports
from detect_obj import detect_obj

yolo_model = YOLO('yolov8n.pt')
yolo_model.track
vebcamera = cv2.VideoCapture(0)

ports = serial.tools.list_ports.comports()
for port in ports:
    print(f"Порт: {port.device}, Описание: {port.description}")


def check_port(port):
    ports = [p.device for p in serial.tools.list_ports.comports()]
    if port in ports:
        print(f"Порт {port} найден")
        try:
            ser = serial.Serial(port, baudrate=115200, timeout=1)
            ser.close()
            print(f"Порт {port} доступен")
            return True
        except serial.SerialException as e:
            print(f"Порт {port} найден, но недоступен: {e}")
            return False
    else:
        print(f"Порт {port} не найден. Доступные порты: {ports}")
        return False


window_width = 800
window_height = 500

#drone_obj = Drone("COM1")
#detect_obj(cv2, yolo_model, vebcamera, drone_obj)
detect_obj(cv2, yolo_model, vebcamera)
