import numpy as np
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# IMU 데이터 파일 경로
imupath = r"C:\Users\user\Desktop\cansat\allrange.txt"

# 데이터 읽기
with open(imupath, 'r') as f:
    s = f.readlines()

num_steps = len(s)

# 데이터 초기화
euler_angles = np.zeros((num_steps, 3))  # 오일러 각 (요, 피치, 롤)
acceleration = np.zeros((num_steps, 3))  # 가속도 (x, y, z)
timestamp = np.zeros((num_steps))  # 시간 

# 데이터 파싱
for i, x in enumerate(s):
    x = x.split()
    time_str = x[0].split('_')[1]
    # 시간을 초 단위로 변환
    timestamp[i] = (float(time_str[:2]) * 3600 + 
                    float(time_str[2:4]) * 60 + 
                    float(time_str[4:12]) / 1000000.0)
    euler_angles[i] = np.array(x[1:4], dtype=float)
    acceleration[i] = np.array(x[4:7], dtype=float)

# 초기 상태
position = np.zeros((num_steps, 3))  # 위치 초기화
velocity = np.zeros((num_steps, 3))  # 속도 초기화

# 오일러 각을 회전 행렬로 변환
rotations = R.from_euler('xyz', euler_angles)

# 시뮬레이션 루프
for t in range(1, num_steps):
    dt = timestamp[t] - timestamp[t-1]

    # 오일러 각을 이용해 회전 행렬 업데이트
    rotation_matrix = rotations[t].as_matrix()

    # 가속도를 전역 좌표계로 변환
    global_acceleration = rotation_matrix @ acceleration[t]

    # 속도 업데이트
    velocity[t] = velocity[t-1] + global_acceleration * dt

    # 위치 업데이트
    position[t] = position[t-1] + velocity[t-1] * dt + 0.5 * global_acceleration * dt**2

# 결과 출력
print("최종 위치: ", position[-1])

# 그래프 출력
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
#ax.plot(position[:, 0], position[:, 1], position[:, 2], label='Path')
ax.scatter(position[::100, 0], position[::100, 1], position[::100, 2], color='r', s=5)
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('IMU sensor 3D position')
ax.legend()

plt.show()
