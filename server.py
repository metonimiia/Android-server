import zmq
import json
import psycopg2
from datetime import datetime

conn = psycopg2.connect(dbname="bd", user="postgres",password="Iaroslav221",host="localhost", port="5432")
cursor = conn.cursor()

def safe_int(value):
    if value is None:
        return None
    try:
        return int(value)
    except:
        return None

def insert_into_db(data):
    try:
        time_str = data.get("Время")
        time_obj = None
        if time_str:
            time_obj = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S")
        latitude = data.get("Широта", 0.0)
        longitude = data.get("Долгота", 0.0)
        altitude = data.get("Высота", 0.0)
        lte = data.get("LTE", {})
        mcc = safe_int(lte.get("MCC"))
        mnc = safe_int(lte.get("MNC"))
        pci = safe_int(lte.get("PCI"))
        rsrp = safe_int(lte.get("RSRP"))
        rsrq = safe_int(lte.get("RSRQ"))
        rssi = safe_int(lte.get("RSSI"))
        rssnr = safe_int(lte.get("RSSNR"))
        cursor.execute("""
            INSERT INTO data (time, latitude, longitude, altitude,mcc, mnc, pci, rsrp, rsrq, rssi, rssnr)
            VALUES (%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s)
        """, (time_obj, latitude, longitude, altitude, mcc, mnc, pci, rsrp, rsrq, rssi, rssnr))
        conn.commit()
        print("[БД] Данные добавлены в базу данных")

    except Exception as e:
        conn.rollback()
        print("[ОШИБКА БД]", e)

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:2222")
    print("Сервер ZeroMQ сервер запущен на порту 2222")
    while True:
        try:
            message = socket.recv().decode("utf-8")
            try:
                data = json.loads(message)
                insert_into_db(data)
                answer = {"status": "OK","message": "Данные сохранены в БД"}
                socket.send(json.dumps(answer, ensure_ascii=False).encode("utf-8"))

        except KeyboardInterrupt:
            print("Сервер остановлен вручную")
            break

        except Exception as e:
            print("[ОШИБКА СЕРВЕРА]", e)
            socket.send("Ошибка сервера".encode("utf-8"))

    cursor.close()
    conn.close()
    socket.close()
    context.term()

if __name__ == "__main__":
    main()
