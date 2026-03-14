import csv
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# GPS 데이터를 저장할 리스트
gps_data_m = []

# CSV 파일 읽기
with open(r"D:\Cansat_Log_20240807_131207\cansat_log_20240807_131207.csv", 'r') as f:
    rdr = csv.reader(f)
    
    x = -1
    y = -1

    
    for line in rdr:
        if line[0] == 'GPS_DATA' and line[3] != '':
            if x == -1 and y == -1:
                x = float(line[3])
                y = float(line[5])
            
            # 위도, 경도를 메터 단위로 변환
            Lat = (float(line[3]) - x) / 100 * 111.19 * 1000
            Lon = (float(line[5]) - y) / 100 * 111.19 * 1000
            Alt = float(line[10])
            
            # 변환된 데이터를 리스트에 추가
            gps_data_m.append([line[2], Lat, Lon, Alt])
            
# CSV 파일로 저장
with open('gps_data_m.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(['UTC', 'Latitude', 'Longitude', 'Altitude'])
    writer.writerows(gps_data_m)


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

timestamps = [data[0] for data in gps_data_m]
y_coords = [data[1] for data in gps_data_m] # 위도 
x_coords = [data[2] for data in gps_data_m] # 경도
z_coords = [data[3] for data in gps_data_m]  # Altitude (고도)

ax = fig.add_subplot(111, projection='3d')
ax.scatter(x_coords, y_coords, z_coords, c='r', marker='o')

ax.set_xlabel('Longitude(m)')
ax.set_ylabel('Latitude(m)')
ax.set_zlabel('Altitude(m)')

ax.set_xlim([-200, 200])
ax.set_ylim([-200, 200])

plt.show()
