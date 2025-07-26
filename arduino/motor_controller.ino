#include <Adafruit_NeoPixel.h>

// DC-Motorsteuerung Pins (H-Brücke)
#define MOTOR_IN1_PIN 40 // Verbunden mit IN1 der H-Brücke
#define MOTOR_IN2_PIN 44 // Verbunden mit IN2 der H-Brücke

// WS2812 LED-Konfiguration
#define LED_PIN 6
#define LED_COUNT 144
Adafruit_NeoPixel statusLED(LED_COUNT, LED_PIN, NEO_GRB + NEO_KHZ800);

// Achsdaten
struct AxisState
{
  const char *name;
  int stepPin;
  int dirPin;
  int minPin;
  int enablePin;
  float maxPos;
  long stepsRemaining;
  unsigned long lastStepTime;
  bool direction;
  double currentPosition;
  bool isHomed;
  float currentSpeed;
  float targetSpeed;
  float accelerationPerMicro;
};

const int nrOfAxes = 4;
AxisState axes[nrOfAxes] = {
    {"X", 54, 55, 3, 38, 300.0, 0, 0, true, 0.0, false, 0.0, 0.0, 0.0},
    {"Y", 60, 61, 14, 56, 475.0, 0, 0, true, 0.0, false, 0.0, 0.0, 0.0},
    {"Z", 46, 48, 18, 62, 290.0, 0, 0, true, 0.0, false, 0.0, 0.0, 0.0},
    {"E0", 26, 28, 2, 24, 180.0, 0, 0, true, 0.0, false, 0.0, 0.0, 0.0}};

// Konfiguration
const double stepsPerMM = 800.0;          // Schritte pro mm (gemäß Ihrer Kalibrierung)
const double stepSize = 1.0 / stepsPerMM; // Schrittgröße (in mm)
const int maxSpeed = 12000;               // Maximale Geschwindigkeit (Schritte pro Sekunde)
const float acceleration = 4000.0;        // Beschleunigung (Schritte pro Sekunde^2)
const int homingSpeed = 25000;            // Homing-Geschwindigkeit (Schritte pro Sekunde)
const int microseconsPerSecond = 1000000; // Mikrosekunden pro Sekunde

// Variablen für die Motoraktivierung
unsigned long lastMovementTime = 0;
bool motorsEnabled = true;
const unsigned long motorDisableDelay = 5000; // 5 Sekunden nach der letzten Bewegung

double getCurrentPosition(int axisIndex)
{
  if (axisIndex >= 0 && axisIndex < nrOfAxes)
  {
    return axes[axisIndex].currentPosition;
  }
  return 0.0;
}

void setCurrentPosition(int axisIndex, double position)
{
  if (axisIndex >= 0 && axisIndex < nrOfAxes)
  {
    axes[axisIndex].currentPosition = position;
  }
}

void initializePins()
{
  for (int i = 0; i < nrOfAxes; i++)
  {
    pinMode(axes[i].stepPin, OUTPUT);
    pinMode(axes[i].dirPin, OUTPUT);
    pinMode(axes[i].minPin, INPUT_PULLUP);
    pinMode(axes[i].enablePin, OUTPUT);
  }

  pinMode(MOTOR_IN1_PIN, OUTPUT);
  pinMode(MOTOR_IN2_PIN, OUTPUT);

  digitalWrite(MOTOR_IN1_PIN, LOW);
  digitalWrite(MOTOR_IN2_PIN, LOW);
}

void stepMotor(int stepPin)
{
  lastMovementTime = millis();
  digitalWrite(stepPin, HIGH);
  delayMicroseconds(2);
  digitalWrite(stepPin, LOW);
}

void moveStep(const int axis, const unsigned long currentTime, const int deltaTime)
{
  const unsigned long stepInterval = microseconsPerSecond / axes[axis].currentSpeed;
  if (deltaTime >= stepInterval)
  {
    digitalWrite(axes[axis].dirPin, axes[axis].direction ? HIGH : LOW);
    stepMotor(axes[axis].stepPin);
    axes[axis].stepsRemaining--;
    axes[axis].lastStepTime = currentTime;

    double position = getCurrentPosition(axis);
    position += axes[axis].direction ? stepSize : -stepSize;
    setCurrentPosition(axis, position);

    checkMovementFinished(axis);
  }
}

void checkMovementFinished(const int axis)
{
  if (axes[axis].stepsRemaining == 0)
  {
    axes[axis].currentSpeed = 0;
    Serial.print("Achse ");
    Serial.print(axes[axis].name);
    Serial.print(" hat seine Bewegung beendet bei: ");
    Serial.println(axes[axis].currentPosition);
  } else if( axes[axis].direction == false && axes[axis].stepsRemaining > 100 && digitalRead(axes[axis].minPin) == LOW)
  {
    // Wenn wir Richtung low (false) fahren und die Achse auf den Endschalter trifft, stoppen wir sie
    // und setzen die aktuelle Geschwindigkeit und Steps Remaining auf 0
    // wir geben eine Meldung aus, damit wir im Seriellen Monitor sehen, dass die Achse auf dem Endschalter steht
    axes[axis].currentSpeed = 0;
    axes[axis].stepsRemaining = 0;
    Serial.print("Achse steht auf Endschalter ");
    Serial.print(axes[axis].name);
    Serial.print(" befindet sich aber auf Position: ");
    Serial.println(axes[axis].currentPosition);
  }
}

void calculateCurrentSpeed(const int axis, const unsigned long deltaTime)
{
  const float accelerationPerMicro = acceleration / microseconsPerSecond;
  axes[axis].targetSpeed = maxSpeed;

  if (axes[axis].currentSpeed < axes[axis].targetSpeed)
  {
    axes[axis].currentSpeed += accelerationPerMicro * deltaTime;
    if (axes[axis].currentSpeed > axes[axis].targetSpeed)
    {
      axes[axis].currentSpeed = axes[axis].targetSpeed;
    }
  }

  if (axes[axis].currentSpeed < 10.0)
  {
    axes[axis].currentSpeed = 10.0;
  }
}

void performConcurrentMovements()
{
  const unsigned long currentTime = micros();
  for (int axis = 0; axis < nrOfAxes; axis++)
  {
    if (axes[axis].stepsRemaining > 0)
    {
      const unsigned long deltaTime = currentTime - axes[axis].lastStepTime;
      calculateCurrentSpeed(axis, deltaTime);
      moveStep(axis, currentTime, deltaTime);
    }
  }
}

void updateLed()
{
  static bool previousState = false;
  bool anyMoving = false;
  for (int axis = 0; axis < nrOfAxes; axis++)
  {
    if (axes[axis].stepsRemaining > 0)
    {
      anyMoving = true;
      break;
    }
  }

  if (anyMoving != previousState)
  {
    previousState = anyMoving;

    uint32_t color = anyMoving ? statusLED.Color(255, 0, 0) : statusLED.Color(0, 255, 0);
    for (int led = 0; led < LED_COUNT; led++)
    {
      statusLED.setPixelColor(led, color);
    }
    statusLED.show();
  }
}

void homing()
{
  enableMotors();
  Serial.println("Homing wird ausgeführt...");

  const unsigned long homingDelay = microseconsPerSecond / homingSpeed;
  for (int axis = 0; axis < nrOfAxes; axis++)
  {
    axes[axis].stepsRemaining = 0;
    axes[axis].isHomed = false;
  }

  for (int axis = 0; axis < nrOfAxes; axis++)
  {
    if (digitalRead(axes[axis].minPin) == LOW)
    {
      axes[axis].isHomed = true;
    }
    else
    {
      digitalWrite(axes[axis].dirPin, LOW);
      axes[axis].isHomed = false;
    }
  }

  // Homing aller Achsen
  while (!(axes[0].isHomed && axes[1].isHomed && axes[2].isHomed && axes[3].isHomed))
  {
    for (int axis = 0; axis < nrOfAxes; axis++)
    {
      if (!axes[axis].isHomed && digitalRead(axes[axis].minPin) == LOW)
      {
        axes[axis].isHomed = true;
      }
      else if (!axes[axis].isHomed)
      {
        stepMotor(axes[axis].stepPin);
        delayMicroseconds(homingDelay);
      }
    }
  }

  // Set all axes to 0.0 after homing
  for (int axis = 0; axis < nrOfAxes; axis++)
  {
    setCurrentPosition(axis, 0.0);
  }

  lastMovementTime = millis();
  Serial.println("Homing abgeschlossen.");

  statusLED.fill(statusLED.Color(0, 255, 0));
  statusLED.show();
}

void initCommand()
{
  for (int axis = 0; axis < nrOfAxes; axis++)
  {
    Serial.print("AXIS ");
    Serial.print(axes[axis].name);
    Serial.print(" MAX ");
    Serial.println(axes[axis].maxPos);
  }
}

void controlMotor(bool forward, int lowOnStop = HIGH)
{
  if (lowOnStop == LOW)
  {
    Serial.println("DC Motor gestoppt");
  }
  else
  {
    Serial.println(forward ? "DC Motor vorwärts" : "DC Motor rückwärts");
  }
  digitalWrite(MOTOR_IN1_PIN, forward ? lowOnStop : LOW);
  digitalWrite(MOTOR_IN2_PIN, forward ? LOW : lowOnStop);
}

void processMotorCommand(String command)
{
  if (command == "FORWARD")
  {
    controlMotor(true);
  }
  else if (command == "REVERSE")
  {
    controlMotor(false);
  }
  else if (command == "STOP")
  {
    controlMotor(false, LOW);
  }
}

void processCommand(String command)
{
  if (command == "HOMING")
  {
    homing();
    return;
  }

  if (command == "INIT")
  {
    initCommand();
    return;
  }

  int spaceIndex = command.indexOf(' ');
  if (spaceIndex == -1)
    return;

  if (command.startsWith("MOTOR"))
  {
    String motorCommand = command.substring(spaceIndex + 1);
    processMotorCommand(motorCommand);
    return;
  }

  String axis = command.substring(0, spaceIndex);
  float value = command.substring(spaceIndex + 1).toFloat();
  processAxisCommand(axis, value);
}

void processAxisCommand(String axis, double value)
{
  for (int axis = 0; axis < nrOfAxes; axis++)
  {
    if (axis == axes[axis].name)
    {
      moveAxis(axis, value);
      return;
    }
  }
}

void moveAxis(int axis, double target)
{
  enableMotors();

  if (target > axes[axis].maxPos)
  {
    target = axes[axis].maxPos;
  }

  long steps = (target - getCurrentPosition(axis)) / stepSize;

  axes[axis].stepsRemaining = abs(steps);
  axes[axis].direction = steps >= 0;

  lastMovementTime = millis();
}

void enableMotors()
{
  if (!motorsEnabled)
  {
    for (int axis = 0; axis < nrOfAxes; axis++)
    {
      digitalWrite(axes[axis].enablePin, LOW);
    }
    motorsEnabled = true;
    Serial.println("Motoren aktiviert.");
  }
}

void disableMotors()
{
  if (motorsEnabled)
  {
    for (int axis = 0; axis < nrOfAxes; axis++)
    {
      digitalWrite(axes[axis].enablePin, HIGH);
    }
    motorsEnabled = false;
    Serial.println("Motoren deaktiviert.");
  }
}

void readNextCommand()
{
  if (Serial.available())
  {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }
}

void checkMotorStatus()
{
  if (motorsEnabled && (millis() - lastMovementTime >= motorDisableDelay))
  {
    disableMotors();
  }
}

void setup()
{
  Serial.begin(115200);
  Serial.println("System startet...");
  initializePins();
  initCommand();

  statusLED.begin();
  statusLED.setBrightness(100);
  statusLED.fill(statusLED.Color(0, 255, 0));
  statusLED.show();

  homing();
}

void loop()
{
  readNextCommand();
  checkMotorStatus();
  performConcurrentMovements();
  updateLed();
}
