import sys
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QGridLayout, QWidget
import time
import datetime
sys.path.insert(0, '/home/elliemak/Desktop/bfsw/')
from pybfsw.gse.gsequery import GSEQuery
from magnetic_field_calculator import MagneticFieldCalculator
from argparse import ArgumentParser
from subprocess import Popen, DEVNULL



class MagnetometerStuff(QMainWindow):

    def __init__(self, latitude, longitude, altitude):
        super().__init__()
        
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude

        self.labels = ['Timestamp:', 'Temperature [C]:', 'MagX [Gauss]:', 'MagY [Gauss]:', 
                       'MagZ [Gauss]:', 'AccX [g]:', 'AccY [g]:', 'AccZ [g]:', 'Roll [deg]:', 
                       'Inclination [deg]:', 'Magnetic Azimuth [deg]:', 'True Azimuth [deg]', 
                       'Magnetic Roll Angle [deg]:', 'Total Magnetic Field [Gauss]:', 
                       'Total Gravitational Field [g]:']

        self.parameters = ['@mag_gcutime', '@mag_temp', '@mag_Bx', '@mag_By', '@mag_Bz', '@mag_Ax',
                        '@mag_Ay', '@mag_Az', '@mag_roll','@mag_pitch', '@mag_yaw', 
                        '@mag_Broll', '@mag_B', '@mag_grav']

        self.q = GSEQuery(project = 'gaps', path = '/home/gaps/mag_test_db/gsedb.sqlite')
        self.mag = self.q.make_parameter_groups(self.parameters)

        self.setWindowTitle("Many Awesome Magnetometer Things")

        self.widget = QWidget(self)
        self.layout = QGridLayout(self.widget)
        self.button_mania()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        # self.timer.start(1000)

       # OTHER LAYOUT
        self.widget.setLayout(self.layout)
        self.setCentralWidget(self.widget)

        self.show()


    def button_mania(self):

        # FIRST COLUMN DATA     
        self.etc_buttons = []

        for i in range(2):
            label = QLabel(self.labels[i])
            self.layout.addWidget(label, i, 0)

            button = QPushButton()
            button.clicked.connect(self.click_action)

            self.etc_buttons.append(button)
            self.layout.addWidget(button, i, 1)

        # ADD GPS BUTTON?
        gps_label = QLabel('Location (GPS):')
        self.layout.addWidget(gps_label, 2, 0)
        gps_button = QPushButton('INSERT DATA/gps update function')
        self.layout.addWidget(gps_button, 2, 1)


        # SECOND COLUMN SENSOR MODE
        self.sensor_buttons = [] 

        for i in range(6):
            label = QLabel(self.labels[i + 2])
            self.layout.addWidget(label, i, 2)

            button = QPushButton()
            button.clicked.connect(self.command_execute(
                        f"python3 -m pybfsw.gse.stripchart {self.parameters[i + 2]} --path {self.path}"
                    ))

            self.sensor_buttons.append(button)
            self.layout.addWidget(button, i, 3)

        # THIRD COLUMN ANGLE MODE    
        self.angle_buttons = []

        for i in range(7):
            label = QLabel(self.labels[i + 8])
            self.layout.addWidget(label, i, 4)

            button = QPushButton()
            button.clicked.connect(self.click_action)

            self.angle_buttons.append(button)
            self.layout.addWidget(button, i, 5)


    #QUERIES FROM DB
    def update(self):
        res = self.q.get_latest_value_groups(self.mag)
        values = []
        for r in res.items():
            values.append(r[1][1])

        value_key = dict(zip(self.parameters, values))

        # TIMESTAMP AND TEMPERATURE
        self.etc_buttons[1].setText(str(value_key['@mag_temp']))
        self.etc_buttons[0].setText(time.strftime("%H:%M:%S", time.localtime(value_key['@mag_gcutime'])))

        # SENSOR BUTTONS
        for i in range(6):
            self.sensor_buttons[i].setText(str('%.4f' % value_key[self.parameters[i + 2]]))

        # ANGLE BUTTONS
        for i in range(3):
            self.angle_buttons[i].setText(str('%.4f' % value_key[self.parameters[i + 8]]))
        
        calculator = MagneticFieldCalculator()
        result = calculator.calculate(
            latitude=self.latitude,
            longitude=self.longitude,
            altitude=self.altitude,
            date='2023-10-13'
        )
        field_value = result['field-value']
        mag_declination = field_value['declination']
        true_yaw = value_key['@mag_yaw'] + mag_declination['value']

        self.angle_buttons[3].setText(str('%.4f' % true_yaw))

        for i in range(3, 6):
            self.angle_buttons[i + 1].setText(str('%.4f' % value_key[self.parameters[i + 8]]))

        print('updating')

        
    def timer_callback(self):
        self.timer.setInterval(int(500))
        self.timer.start()
        self.update()


    # REPLACE THIS WITH AN ACTION MAYBE, OPEN STRIPCHART?
    def click_action(self):
        print("IT'S DOING SOMETHING TEMPORARY")

    def command_execute(self, cmd):
        print(cmd)
        return lambda: Popen(cmd.split(), stdout=DEVNULL, stderr=DEVNULL)

if __name__ == '__main__':
    p = ArgumentParser()
    # p.add_argument('-h', '--help', action='help', 
    #                help='takes longitude in deg, latitude in deg, and altitude in km')
    p.add_argument('--longitude', required = True, type = float, help = 'longitude [deg]')
    p.add_argument('--latitude', required = True, type = float, help = 'latitude [deg]')
    p.add_argument('--altitude', required = True, type = float, help = 'altitude [km]')
    args = p.parse_args()

    app = QApplication(sys.argv)
    my_gui = MagnetometerStuff(args.latitude, args.longitude, args.altitude)
    my_gui.show()
    sys.exit(app.exec_())



