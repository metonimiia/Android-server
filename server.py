import zmq
import json
import psycopg2
from datetime import datetime

conn = psycopg2.connect(
    dbname="bd_gps_lte",
    user="postgres",     
    password="Iaroslav221",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

def safe_int(val):
    try:
        return int(val) if val is not None else None
    except (ValueError, TypeError):
        return None

def insert_into_db(data):
    try:
        time_str = data.get("Время")
        time_obj = datetime.strptime(time_str, "%d.%m.%Y %H:%M:%S") if time_str else None
        latitude = data.get("Широта", 0.0)
        longitude = data.get("Долгота", 0.0)
        altitude = data.get("Высота", 0.0)
        speed = data.get("Скорость (м/с)", 0.0)
        accuracy = data.get("Точность (м)", 0.0)

        lte = data.get("LTE", data)  

        mcc = safe_int(lte.get("MCC"))#
        mnc = safe_int(lte.get("MNC"))#
        pci = safe_int(lte.get("PCI"))#
        tac = safe_int(lte.get("TAC"))
        earfcn = safe_int(lte.get("EARFCN"))
        asu = safe_int(lte.get("ASU"))
        cqi = safe_int(lte.get("CQI"))
        rsrp = safe_int(lte.get("RSRP"))#
        rsrq = safe_int(lte.get("RSRQ"))#
        rssi = safe_int(lte.get("RSSI"))#
        rssnr = safe_int(lte.get("RSSNR"))#
        timing_advance = safe_int(lte.get("TimingAdvance"))

        cursor.execute("""
            INSERT INTO gps_lte_data 
            (time, latitude, longitude, altitude, speed, accuracy,
             mcc, mnc, pci, tac, earfcn, asu, cqi, rsrp, rsrq, rssi, rssnr, timing_advance)
            VALUES (%s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (time_obj, latitude, longitude, altitude, speed, accuracy,
              mcc, mnc, pci, tac, earfcn, asu, cqi, rsrp, rsrq, rssi, rssnr, timing_advance))
        conn.commit()
        print("[DB] Данные добавлены в таблицу")
    except Exception as e:
        conn.rollback()
        print(f"[DB ERROR] {e}")


def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:2222")
    print("Сервер ZeroMQ запущен на порту 2222...")

    while True:
        try:
            message = socket.recv()
            decoded_msg = message.decode("utf-8").strip()
            if decoded_msg.lower() == "stop":
                socket.send(b"Server stop")
                break

            try:
                data = json.loads(decoded_msg)
                insert_into_db(data)
                socket.send(json.dumps({"status":"OK","message":"Данные сохранены"}, ensure_ascii=False).encode("utf-8"))
            except json.JSONDecodeError:
                socket.send("Ошибка: сообщение не является JSON".encode("utf-8"))

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[SERVER ERROR] {e}")
            try:
                socket.send(f"Ошибка сервера: {e}".encode("utf-8"))
            except:
                pass

    cursor.close()
    conn.close()
    socket.close()
    context.term()
    print("Сервер завершил работу.")

if __name__ == "__main__":
    main()
