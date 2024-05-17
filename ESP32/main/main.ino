#include <MPU9250_asukiaaa.h>

#include <WiFi.h>
#include <WiFiUdp.h>
#include <OSCMessage.h>


#ifdef _ESP32_HAL_I2C_H_
#define SDA_PIN 19
#define SCL_PIN 18
#endif

#define G 9.81;

unsigned long startMillis;
unsigned long currentMillis;
const unsigned long period = 20;
const float periodSec = period / 1000.f;

char ssid[] = "Biox";      // your network SSID (name)
char pass[] = "Biox1234";  // your network password

WiFiUDP Udp;                              // A UDP instance to let us send and receive packets over UDP
const IPAddress outIp(192, 168, 1, 101);  // r/emote IP of your computer
const unsigned int outPort = 9999;        // remote port to receive OSC
const unsigned int localPort = 8888;      // local port to listen for OSC packets (actually not used for sending)

MPU9250_asukiaaa mySensor(MPU9250_ADDRESS_AD0_HIGH);  // IMU LIb
float aX, aY, aZ, aSqrt, gX, gY, gZ, mDirection, mX, mY, mZ, pitch, roll;
float aX_1, aY_1, aZ_1, gX_1, gY_1, gZ_1 = 0;
float vX, vY, vZ, vX_1, vY_1, vZ_1 = 0.f;
float accMag, gyroMag = 0.f;
float aIntX, aIntY, aIntZ = 0.f;
float phiRad, thetaRad = 0.f;

void setup() {
  Serial.begin(115200);
  while (!Serial)
    ;
  Serial.println("started");
  Serial.begin(115200);
  Serial.println("started");

  // Connect to WiFi network
  Serial.println();
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");

  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());

  Serial.println("Starting UDP");
  Udp.begin(localPort);
  Serial.print("Local port: ");
  Serial.println(localPort);


#ifdef _ESP32_HAL_I2C_H_  // For ESP32
  Wire.begin(SDA_PIN, SCL_PIN);
  mySensor.setWire(&Wire);
#endif
  startMillis = millis();
  mySensor.beginAccel();
  mySensor.beginGyro();
  mySensor.beginMag();
  // You can set your own offset for mag values
  // mySensor.magXOffset = -50;
  // mySensor.magYOffset = -55;
  // mySensor.magZOffset = -10;
}

void loop() {
  uint8_t sensorId;
  int result;

  currentMillis = millis();
  if (currentMillis - startMillis >= period) {
    result = mySensor.accelUpdate();
    if (result == 0) {
      aX = 0.1 * mySensor.accelX() + 0.9 * aX_1;
      aY = 0.1 * mySensor.accelY() + 0.9 * aY_1;
      aZ = 0.1 * mySensor.accelZ() + 0.9 * aZ_1;

      aX_1 = aX;
      aY_1 = aY;
      aZ_1 = aZ;
      aIntY += periodSec * mySensor.accelY();
      aIntX += periodSec * mySensor.accelX();
      aIntZ += periodSec * mySensor.accelZ();
      accMag = mySensor.accelSqrt();
    } else {
      Serial.println("Cannod read accel values " + String(result));
    }

    result = mySensor.gyroUpdate();
    if (result == 0) {
      gX = 0.7 * mySensor.gyroX() + 0.3 * gX;
      gY = 0.7 * mySensor.gyroY() + 0.3 * gY;
      gZ = 0.7 * mySensor.gyroZ() + 0.3 * gZ;
      gX_1 = gX;
      gY_1 = gY;
      gZ_1 = gZ;
      gyroMag = std::sqrt(gX*gX + gY*gY + gZ*gZ);
      float gXrad = gX * (M_PI / 180.0f);
      float gYrad = gY * (M_PI / 180.0f);
      float gZrad = gZ * (M_PI / 180.0f);
    } else {
      Serial.println("Cannot read gyro values " + String(result));
    }
    calcAccZ();
    result = mySensor.magUpdate();
    if (result != 0) {
      Serial.println("cannot read mag so call begin again");
      mySensor.beginMag();
      result = mySensor.magUpdate();
    }
    if (result == 0) {
      mX = mySensor.magX();
      mY = mySensor.magY();
      mZ = mySensor.magZ();
    } else {
      Serial.println("Cannot read mag values " + String(result));
    }
    sendOsc();
    startMillis = currentMillis;
  }
}

void serialOutput(float val1, float val2, float val3) {
  Serial.print(val1);
  Serial.print(",");
  Serial.print(val2);
  Serial.print(",");
  Serial.println(val3);
}

void sendOsc() {
  serialOutput(accMag, gyroMag, 0);
  OSCMessage msg("/LH");
  msg.add(accMag);
  msg.add(gyroMag);
  Udp.beginPacket(outIp, outPort);
  msg.send(Udp);
  Udp.endPacket();
  msg.empty();
}

void calcAccZ() {
  float phiHatAcc = atan2(aY, sqrt(aX * aX + aZ * aZ));
  float thetaHatAcc = atan2(-aX, sqrt(aY * aY + aZ * aZ));
  float piBy180 = (M_PI / 180.0f);
  float gXrad = gX * piBy180;
  float gYrad = gY * piBy180;
  float gZrad = gZ * piBy180;
  float rollAngle = phiHatAcc * (1.f / piBy180);
  float pitchAngle = thetaHatAcc * (1.f / piBy180);
  float phiDot = gXrad + tanf(thetaRad) * (sinf(phiRad) * gYrad + cosf(phiRad) * gZrad);
  float thetaDot = cosf(phiRad) * gYrad - sinf(phiRad) * gZrad;
  float innertialZ = -sinf(thetaHatAcc) * aX + cosf(thetaHatAcc) * sinf(phiHatAcc) * aY + cosf(thetaHatAcc) * cosf(phiHatAcc) * aZ;
  innertialZ = (innertialZ - 1) * 100.f * G;
  float accZ = -aX * sinf(phiHatAcc) + aY * sinf(thetaHatAcc) * cosf(phiHatAcc) + aZ * cosf(thetaHatAcc) * cosf(phiHatAcc);
  float vZ = vZ + innertialZ * periodSec;
}