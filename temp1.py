import numpy as np
from scipy.spatial.transform import Rotation as R
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

imupath = r"C:\Users\user\Desktop\cansat\allrange.txt"

f = open(imupath,'r')
s = f.readlines()
num_steps = len(s)
# 예시 데이터 (여기에 실제 데이터를 넣으세요)
euler_angles = np.zeros((len(s), 3))  # 오일러 각 (롤, 피치, 요)
acceleration = np.zeros((len(s), 3))  # 가속도
timestamp = np.zeros((len(s))) # 시간 
for i,x in enumerate(s):
    x = x.split()
    timestamp[i] = float(x[0].split('_')[1].ljust(12,'0'))/1000000.0
    euler_angles[i] = np.array(x[1:4])
    acceleration[i] = np.array(x[7:10])

# 초기 상태
position = np.zeros((num_steps, 3))  # 위치 초기화
velocity = np.zeros((num_steps, 3))  # 속도 초기화

# 오일러 각을 회전 행렬로 변환
rotations = R.from_euler('xyz', euler_angles)

# 시뮬레이션 루프
for t in range(1, num_steps):
    dt = timestamp[t]-timestamp[t-1]

    # 오일러 각을 이용해 회전 행렬 업데이트
    rotation_matrix = rotations[t].as_matrix()

    # 가속도를 전역 좌표계로 변환
    global_acceleration = rotation_matrix @ acceleration[t]

    # 속도 업데이트
    velocity[t] = velocity[t-1] + global_acceleration * dt

    # 위치 업데이트
    position[t] = position[t-1] + velocity[t] * dt

# 결과 출력
print("최종 위치: ", position[-1])
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')

ax.plot(position[:, 0], position[:, 1], position[:, 2])
ax.scatter(position[::100,0],position[::100,1],position[::100,2])
ax.set_xlabel('X')
ax.set_ylabel('Y')
ax.set_zlabel('Z')
ax.set_title('IMU sensor 3d pos')

plt.show()