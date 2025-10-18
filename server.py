import zmq
import json
from pathlib import Path

COORDS_FILE = Path("coords.txt")  # Файл для записи координат

def save_coords(time, lat, lon, alt):
    with COORDS_FILE.open("a", encoding="utf-8") as f:
        f.write(f"{lat}  {lon}\n")

def main():
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:2222")
    print("Python ZeroMQ сервер запущен на порту 2222...")

    while True:
        try:
            message = socket.recv()
            decoded_msg = message.decode("utf-8").strip()
            print(f"\n[SERVER] Принято сообщение")

            if decoded_msg.lower() == "stop":
                socket.send(b"Server stop")
                print("[SERVER] Остановка по команде клиента.")
                break

            try:
                data = json.loads(decoded_msg)
                time = data.get("Время")
                lat = data.get("Широта")
                lon = data.get("Долгота")
                alt = data.get("Высота")

                print("Получены координаты:")
                print(f" Время: {time}")
                print(f" Широта: {lat}")
                print(f" Долгота: {lon}")
                print(f" Высота: {alt} м")

                save_coords(time, lat, lon, alt)

                reply = json.dumps({
                    "status": "OK",
                    "message": "Координаты получены",
                    "data": data
                }, ensure_ascii=False)

                socket.send(reply.encode("utf-8"))

            except json.JSONDecodeError:
                print("Получено не-JSON сообщение!")
                reply = "Ошибка: сообщение не является JSON"
                socket.send(reply.encode("utf-8"))

        except KeyboardInterrupt:
            print("\nСервер остановлен пользователем.")
            break
        except Exception as e:
            print(f"[Ошибка] {e}")
            socket.send(f"Ошибка сервера: {e}".encode("utf-8"))

    socket.close()
    context.term()
    print("Сервер завершил работу.")


if __name__ == "__main__":
    main()
