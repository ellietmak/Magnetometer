import serial
import time, datetime
import struct
import sqlite3

ser = serial.Serial('/dev/ttyUSB0', 9600, timeout = 1) 

# MAKE A TABLE, MAKE A FUNCTION THAT INSERTS A ROW, WHILE LOOP THE FUNCTION

conn = sqlite3.connect('magnetometer.sqlite')
conn.execute('create table if not exists mag_data(gcutime REAL, temp REAL, mag_x REAL, mag_y REAL, mag_z REAL, acc_x REAL, acc_y REAL, acc_z REAL, roll REAL, pitch REAL, yaw REAL, mag_roll REAL, mag_field REAL, grav_field REAL);')

def to_float(s):
  try:
    fl = float(s)
  except:
    fl = -1
  return fl

# sends command: send data angle mode
def send_data_angle(ser):
  ser.write(bytes('0l\r'.encode()))
  ser.write(bytes('0WC02b03\r'.encode()))
  ser.write(bytes('0SD\r'.encode()))

  line = ser.read(125)
  
  line_decoded = line.decode()
  
  return line_decoded

# list of angle data
def send_bin_angle(ser):
  ser.write(b'\x83\r')
  line = ser.read(22)
  int_decode = struct.unpack('>BBhhhhhhhhBBh', line)

  mag_data = []
  for i in int_decode[2:8]:
      mag_data.append(i / 10)

  return mag_data

# sends command: send data sensor mode
def send_data_sensor(ser):
  ser.write(bytes('0l\r'.encode()))
  ser.write(bytes('0WC02b02\r'.encode()))
  ser.write(bytes('0SD\r'.encode()))
  
  line = ser.read(125)
  
  line_decoded = line.decode()

  return line_decoded

# list of vector data + temp
def send_bin_vector(ser):
  ser.write(b'\x80\r')
  line = ser.read(22)
  int_decode = struct.unpack('>BBhhhhhhhhBBh', line)
    
  mag_data = []
  for i in int_decode[2:8]:
      mag_data.append(i / 10000)
  
  temp = int_decode[8] / 100
  mag_data.append(temp)

  return mag_data
   

while True:
    time.sleep(1)
    ct = datetime.datetime.utcnow()
    tnow = time.time()
    # date_time = time.strftime("%m/%d/%Y, %H:%M:%S")
    
    bin_data_vec = send_bin_vector(ser)
    bin_data_ang = send_bin_angle(ser)
    
    temp = bin_data_vec[6]

    mag_x = bin_data_vec[0]
    mag_y = bin_data_vec[2]
    mag_z = bin_data_vec[4]

    acc_x = bin_data_vec[1]
    acc_y = bin_data_vec[3]
    acc_z = bin_data_vec[5]

    roll = bin_data_ang[0]
    pitch = bin_data_ang[2]
    yaw = bin_data_ang[4]
    # yaw_true = bin_data_ang[4] #- something

    mag_roll = bin_data_ang[1]
    mag_field = bin_data_ang[3] / 1000
    grav_field = bin_data_ang[5] / 1000

    
    s = f"@{ct} ({tnow}): temp = {temp}, mag_x = {mag_x}, mag_y = {mag_y}, mag_z = {mag_z}, acc_x = {acc_x}, acc_y = {acc_y}, acc_z = {acc_z}, roll = {roll}, pitch = {pitch}, yaw = {yaw}, mag_roll = {mag_roll}, mag_field = {mag_field}, grav_field = {grav_field}"

    conn.execute(f'insert into mag_data(gcutime, temp, mag_x, mag_y, mag_z, acc_x, acc_y, acc_z, roll, pitch, yaw, mag_roll, mag_field, grav_field) values ({tnow},{to_float(temp)},{to_float(mag_x)},{to_float(mag_y)},{to_float(mag_z)},{to_float(acc_x)},{to_float(acc_y)},{to_float(acc_z)},{to_float(roll)},{to_float(pitch)}, {to_float(yaw)}, {to_float(mag_roll)}, {to_float(mag_field)}, {to_float(grav_field)})')
    conn.execute('commit')

    # data_vec = send_data_sensor(ser)
    # data_ang = send_data_angle(ser)
    
    print(ct)
    # print('Vectors:', bin_data_vec)
    # print(data_vec)
    # print('Angles:', bin_data_ang)
    # print(data_ang)


