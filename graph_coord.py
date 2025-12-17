import psycopg2
import matplotlib.pyplot as plt
import numpy as np
import time

conn = psycopg2.connect(
    dbname="bd",
    user="postgres",
    password="Iaroslav221",
    host="localhost",
    port="5432"
)
cursor = conn.cursor()

def load_data():
    cursor.execute("SELECT latitude, longitude, rssi FROM data;")
    rows = cursor.fetchall()

    latitudes = []
    longitudes = []
    rssi_signal = []

    for row in rows:
        latitudes.append(row[0])
        longitudes.append(row[1])
        rssi_signal.append(row[2])

    return latitudes, longitudes, rssi_signal

plt.ion()
fig, graph = plt.subplots(figsize=(10, 6))
colorbar = None

while True:
    latitudes, longitudes, rssi_signal = load_data()
    if len(latitudes) == 0:
        time.sleep(10)
        continue

    graph.clear()
    lat = []
    lon = []
    rssi = []
    for i in range(len(rssi_signal)):
        if rssi_signal[i] is not None:
            lat.append(latitudes[i])
            lon.append(longitudes[i])
            rssi.append(int(rssi_signal[i]))

    scatter = graph.scatter(lon,lat,c=rssi, cmap="viridis",s=30,vmin=-125, vmax=-50)

    if colorbar is not None:
        colorbar.remove()

    colorbar = plt.colorbar(scatter, ax=graph)
    colorbar.set_label("RSSI(дБм)")
    colorbar.set_ticks([-125, -105, -85, -65, -50])
    colorbar.set_ticklabels([ "-125 (очень плохо)","-105 (плохо)","-85 (пойдет)","-65 (отлично)","-50 (круто)"])

    graph.set_title("Карта качества сигнала (RSSI)")
    graph.set_xlabel("Долгота")
    graph.set_ylabel("Широта")
    graph.grid(True)
    plt.pause(10)
