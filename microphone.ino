#include <DHT.h>

// Define pins for MQ-135, DHT-22, and microphone sensor
const int MQ135_PIN = A0;  // MQ-135 sensor pin
const int DHT_PIN = 2;     // DHT-22 sensor pin
#define MIC_PIN A1         // Microphone sensor analog output connected to A1

// Set up DHT-22 sensor type
#define DHTTYPE DHT22
DHT dht(DHT_PIN, DHTTYPE);

// Calibration parameters for MQ sensors
float R0_MQ135 = 10.0;  // Base resistance for MQ-135 (in kOhms)

// Function to calculate PPM (Parts Per Million) for MQ-135
float calculatePPM_MQ135(float sensorValue) {
  float voltage = (sensorValue / 1023.0) * 3.3;
  float resistance = ((3.3 * 10.0) / voltage) - 10.0;
  float ratio = resistance / R0_MQ135;
  float calibrationFactor = 25;
  float ppm = 116.6020682 * pow(ratio, -2.769034857) * calibrationFactor;
  return ppm;
}

// Function to calculate microphone peak-to-peak in dB
float calculateDecibels() {
  unsigned long startTime = millis();
  int micMax = 0;
  int micMin = 1023;
  
  while (millis() - startTime < 50) {  // Measure over 50 ms
    int micValue = analogRead(MIC_PIN);
    if (micValue > micMax) micMax = micValue;
    if (micValue < micMin) micMin = micValue;
  }
  
  int peakToPeak = micMax - micMin;
  float voltage = (peakToPeak * 3.3) / 1023.0; // Convert to voltage (assuming 3.3V)
  float decibels = 20 * log10(voltage / 0.00631);  // Approximate to dB using a reference voltage
  
  return decibels;
}

void setup() {
  Serial.begin(9600);
  while (!Serial)
    ;

  dht.begin();
  Serial.println("Air Quality, Temperature, and Noise Monitoring System");

  delay(2000);
}

void loop() {
  // Read data from MQ-135
  int mq135Value = analogRead(MQ135_PIN);
  float co2PPM = calculatePPM_MQ135(mq135Value);

  // Read temperature and humidity from DHT-22
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();

  // Calculate Heat Index
  float heatIndex = dht.computeHeatIndex(temperature, humidity, false);  // false for Celsius

  // Print air quality and temperature data
  Serial.print("CO2 (MQ-135) PPM: ");
  Serial.println(co2PPM);
  Serial.print("Heat Index: ");
  Serial.print(heatIndex);
  Serial.println("°C");

  // Calculate and display microphone reading in decibels
  float micDecibels = calculateDecibels();
  Serial.print("Microphone Level: ");
  Serial.print(micDecibels + 15);
  Serial.print(" dB");

  // Set a threshold for noise detection (adjust as needed)
  if (micDecibels > 60) {  // Example threshold in dB; adjust based on sensor behavior
    Serial.println(" (Noise detected !!!)");
  } else {
    Serial.println(" (No noise detected...)");
  }

  Serial.println("-------------------------------");
  delay(2000);  // Adjust delay as needed
}
