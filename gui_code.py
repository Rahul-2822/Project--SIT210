# -*- coding: utf-8 -*-

import sys
import serial
import re
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QProgressBar
from PyQt5.QtCore import QTimer, QPropertyAnimation
from PyQt5.QtGui import QColor

# Set up the serial connection to the Arduino
try:
    ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)  # Use /dev/ttyACM0
except serial.SerialException:
    print("Error: Could not open serial port. Check if the Arduino is connected to /dev/ttyACM0.")
    sys.exit(1)

class DataMonitor(QWidget):
    def __init__(self):
        super().__init__()
        
        # Set up the GUI layout
        self.setWindowTitle("Air Quality and Noise Monitoring System")
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet("background-color: #1C1E26; color: #ECEFF4; font-family: Arial; font-size: 16px;")

        self.layout = QVBoxLayout()

        # Create labels for each sensor reading
        self.co2_label = QLabel("CO2 (PPM): ")
        self.heat_index_label = QLabel("Heat Index (C): ")
        self.sound_level_label = QLabel("Sound Level (dB): ")

        # Create progress bars for CO2, Heat Index, and Sound Level
        self.co2_progress = QProgressBar()
        self.heat_index_progress = QProgressBar()
        self.sound_level_progress = QProgressBar()

        # Set label and progress bar styles
        label_style = """
            QLabel {
                font-size: 18px;
                padding: 15px;
                border-radius: 10px;
                background-color: #3B4252;
                color: #A3BE8C;
                margin: 10px;
                text-align: center;
                font-weight: bold;
                border: 2px solid #88C0D0;
            }
        """
        progress_style = """
            QProgressBar {
                background-color: #3B4252;
                border-radius: 10px;
                text-align: center;
                height: 30px;
            }
            QProgressBar::chunk {
                background-color: #88C0D0;
                border-radius: 10px;
            }
        """
        self.co2_label.setStyleSheet(label_style)
        self.heat_index_label.setStyleSheet(label_style)
        self.sound_level_label.setStyleSheet(label_style)
        
        self.co2_progress.setStyleSheet(progress_style)
        self.heat_index_progress.setStyleSheet(progress_style)
        self.sound_level_progress.setStyleSheet(progress_style)

        # Add labels and progress bars to the layout
        self.layout.addWidget(self.co2_label)
        self.layout.addWidget(self.co2_progress)
        self.layout.addWidget(self.heat_index_label)
        self.layout.addWidget(self.heat_index_progress)
        self.layout.addWidget(self.sound_level_label)
        self.layout.addWidget(self.sound_level_progress)
        
        # Set the layout
        self.setLayout(self.layout)

        # Set up a timer to periodically read data from the serial port
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_data)
        self.timer.start(1000)  # Update every second

    def animate_label(self, label):
        """Creates a pulsing color animation for a label to indicate data update."""
        # Set up the animation to change the text color to a highlight color and back
        animation = QPropertyAnimation(label, b"styleSheet")
        animation.setDuration(500)
        animation.setKeyValueAt(0, "color: #ECEFF4;")  # Starting color (default)
        animation.setKeyValueAt(0.5, "color: #EBCB8B;")  # Highlight color
        animation.setKeyValueAt(1, "color: #ECEFF4;")  # End color (default)
        animation.start()

    def update_data(self):
        # Read data from the serial port
        if ser.in_waiting > 0:
            data = ser.readline().decode('utf-8').strip()
            self.update_data_labels(data)

    def update_data_labels(self, data):
        data_parts = data.split(":")
        
        # Check if data format is valid
        if len(data_parts) < 2:
            return

        # Clean the data to remove any unwanted characters (like non-ASCII characters or the degree symbol)
        cleaned_value = re.sub(r'[^\d.]', '', data_parts[1].strip())  # Keep only digits and the decimal point

        # Update the labels and progress bars based on the received data
        if "CO2" in data_parts[0]:
            co2_value = float(cleaned_value)
            self.co2_label.setText(f"CO2 (PPM): {co2_value}")
            self.co2_progress.setValue(int(co2_value))  # Set progress bar value
            self.animate_label(self.co2_label)
        elif "Heat Index" in data_parts[0]:
            try:
                heat_index_value = float(cleaned_value)
                self.heat_index_label.setText(f"Heat Index (C): {heat_index_value}\u00B0C")
                self.heat_index_progress.setValue(int(heat_index_value))  # Set progress bar value
                self.animate_label(self.heat_index_label)
            except ValueError:
                print(f"Invalid heat index value: {data_parts[1]}")
        elif "Sound Level" in data_parts[0]:
            sound_level_value = float(cleaned_value)
            self.sound_level_label.setText(f"Sound Level (dB): {sound_level_value}")
            self.sound_level_progress.setValue(int(sound_level_value))  # Set progress bar value
            self.animate_label(self.sound_level_label)

# Initialize the application and widget
app = QApplication(sys.argv)
window = DataMonitor()
window.show()
sys.exit(app.exec_())
