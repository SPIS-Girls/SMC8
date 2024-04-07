#include <MPU9250_asukiaaa.h>

#include <WiFi.h>
#include <WiFiUdp.h>
#include <OSCMessage.h>


#ifdef _ESP32_HAL_I2C_H_
#define SDA_PIN 19
#define SCL_PIN 18
#endif

char ssid[] = "Biox";      // your network SSID (name)
char pass[] = "Biox1234";  // your network password

WiFiUDP Udp;                             // A UDP instance to let us send and receive packets over UDP
const IPAddress outIp(192, 168, 1, 100);  // r/emote IP of your computer
const unsigned int outPort = 9999;       // remote port to receive OSC
const unsigned int localPort = 8888;     // local port to listen for OSC packets (actually not used for sending)


MPU9250_asukiaaa mySensor(MPU9250_ADDRESS_AD0_HIGH);  // IMU LIb
float aX, aY, aZ, aSqrt, gX, gY, gZ, mDirection, mX, mY, mZ;
float gIntX, gIntY, gIntZ;

void setup() {
  Serial.begin(115200);
  while (!Serial)
    ;
  Serial.println("started");
  Serial.begin(115200);
  Serial.println("started");

  // Connect to WiFi network
  // Serial.println();
  // Serial.println();
  // Serial.print("Connecting to ");
  // Serial.println(ssid);
  WiFi.begin(ssid, pass);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  // Serial.println("");

  // Serial.println("WiFi connected");
  // Serial.println("IP address: ");
  // Serial.println(WiFi.localIP());

  // Serial.println("Starting UDP");
  // Udp.begin(localPort);
  // Serial.print("Local port: ");
  // Serial.println(localPort);



#ifdef _ESP32_HAL_I2C_H_  // For ESP32
  Wire.begin(SDA_PIN, SCL_PIN);
  mySensor.setWire(&Wire);
#endif

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

  result = mySensor.readId(&sensorId);
  /*if (result == 0) {
    Serial.println("sensorId: " + String(sensorId));
  } else {
    Serial.println("Cannot read sensorId " + String(result));
  }
  */

  result = mySensor.accelUpdate();
  if (result == 0) {
    aX = mySensor.accelX();
    aY = mySensor.accelY();
    aZ = mySensor.accelZ();
    aSqrt = mySensor.accelSqrt();
    // Serial.println("accelX: " + String(aX));
    // Serial.println("accelY: " + String(aY));
    // Serial.println("accelZ: " + String(aZ));
    // Serial.println("accelSqrt: " + String(aSqrt));

  } else {
    Serial.println("Cannod read accel values " + String(result));
  }
  
  result = mySensor.gyroUpdate();
  if (result == 0) {
    gX = mySensor.gyroX();
    gY = mySensor.gyroY();
    gZ = mySensor.gyroZ();
    gIntX += gX;
    gIntY += gY;
    gIntZ += gZ;
    // Serial.println("gyroX: " + String(gX));
    Serial.print(gIntX);
    Serial.print(",");
    Serial.print(gIntY);
    Serial.print(",");
    Serial.println(gIntZ);

    // Serial.println("gyroY: " + String(gY));
    // Serial.println("gyroZ: " + String(gZ));
  } else {
    Serial.println("Cannot read gyro values " + String(result));
  }

  result = mySensor.magUpdate();
  if (result != 0) {
    Serial.println("cannot read mag so call begin again");
    mySensor.beginMag();
    result = mySensor.magUpdate();
  }
  if (result == 0) {
    // mX = mySensor.magX();
    // mY = mySensor.magY();
    // mZ = mySensor.magZ();
    // mDirection = mySensor.magHorizDirection();
    // Serial.println("magX: " + String(mX));
    // Serial.println("maxY: " + String(mY));
    // Serial.println("magZ: " + String(mZ));
    // Serial.println("horizontal direction: " + String(mDirection));
  } else {
    Serial.println("Cannot read mag values " + String(result));
  }

  OSCMessage msg("/LH");
  msg.add(aX);
  msg.add(aY);
  msg.add(aZ);
  msg.add(mySensor.accelSqrt());
  msg.add(gIntX);
  msg.add(gIntY);
  msg.add(gIntZ);
  Udp.beginPacket(outIp, outPort);
  msg.send(Udp);
  Udp.endPacket();
  msg.empty();

  delay(250);
}
