import serial
import time
import struct


class MSP:
    def __init__(self, port, baudrate=115200):
        self.serial = serial.Serial(port, baudrate, timeout=1)

    def send(self, msg_id, data):
        # Формируем MSP-пакет: $M< + длина данных + msg_id + данные + контрольная сумма
        packet = bytearray(b'$M<')
        packet.append(len(data))  # Длина данных
        packet.append(msg_id)  # ID сообщения
        packet.extend(data)  # Данные
        checksum = 0
        for b in packet[3:]:  # Считаем контрольную сумму
            checksum ^= b
        packet.append(checksum)
        self.serial.write(packet)

    def receive(self):
        # Читаем ответ (упрощённый вариант)
        header = self.serial.read(3)
        if header != b'$M>':
            return None
        length = self.serial.read(1)[0]
        msg_id = self.serial.read(1)[0]
        data = self.serial.read(length)
        checksum = self.serial.read(1)[0]
        return msg_id, data


class Drone:
    def __init__(self, port):
        self.msp = MSP(port)
        self.roll = 1500  # Нейтральное значение (1500 = центр)
        self.pitch = 1500
        self.throttle = 1000  # Минимальный газ
        self.yaw = 1500
        self.armed = False

    def arm(self):
        # Включаем дрон (arming)
        self.armed = True
        self.throttle = 1000
        self.send_rc()

    def disarm(self):
        # Выключаем дрон (disarming)
        self.armed = False
        self.throttle = 1000
        self.send_rc()

    def send_rc(self):
        # Отправляем RC-команды через MSP_SET_RAW_RC (msg_id=200)
        if not self.armed:
            return
        channels = [
            self.roll, self.pitch, self.throttle, self.yaw,
            1500, 1500, 1500, 1500  # Дополнительные каналы (AUX)
        ]
        data = bytearray()
        for channel in channels:
            data.extend(struct.pack('<H', channel))  # Упаковываем в 16-битные значения
        self.msp.send(200, data)

    def set_throttle(self, value):
        # Устанавливаем газ (1000-2000)
        self.throttle = max(1000, min(2000, value))
        self.send_rc()

    def set_roll(self, value):
        # Устанавливаем roll (1000-2000)
        self.roll = max(1000, min(2000, value))
        self.send_rc()

    def set_pitch(self, value):
        # Устанавливаем pitch (1000-2000)
        self.pitch = max(1000, min(2000, value))
        self.send_rc()

    def set_yaw(self, value):
        # Устанавливаем yaw (1000-2000)
        self.yaw = max(1000, min(2000, value))
        self.send_rc()


def control_drone(center_x, center_y, target_object_id, confidence, area_percent, drone):
    print(f"center x: {center_x}, center y: {center_y}, target_object_id: {target_object_id}, confidence: {confidence},"
          f"area_percent:  {area_percent}")
