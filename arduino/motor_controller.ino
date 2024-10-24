// DC-Motorsteuerung Pins (H-Brücke)
#define MOTOR_IN1_PIN    40   // Verbunden mit IN1 der H-Brücke
#define MOTOR_IN2_PIN    44   // Verbunden mit IN2 der H-Brücke

// Achsdaten
struct AxisState {
  const char* name;
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
};

// NAME, STEP, DIR, MIN, ENABLE, MAX_POS, STEPS_REMAINING, LAST_STEP_TIME, DIRECTION, CURRENT_POSITION, IS_HOMED
AxisState axes[5] = {
  {"X",  54,   55,  3,   38,     300.0,   0,               0,              true,      0.0,              false},
  {"Y",  60,   61,  14,  56,     470.0,   0,               0,              true,      0.0,              false},
  {"Z",  46,   48,  18,  62,     290.0,   0,               0,              true,      0.0,              false},
  {"E0", 26,   28,  2,   24,     180.0,   0,               0,              true,      0.0,              false},
  {"E1", 36,   34,  15,  30,     180.0,   0,               0,              true,      0.0,              false}
};

// Konfiguration
const double stepsPerMM = 800.0;      // Schritte pro mm (gemäß Ihrer Kalibrierung)
const double stepSize = 1.0 / stepsPerMM; // Schrittgröße (in mm)
const int maxSpeed = 28000;          // Maximale Geschwindigkeit (Schritte pro Sekunde)
const int homingSpeed = 25000;       // Homing-Geschwindigkeit (Schritte pro Sekunde)
const int acceleration = 70;         // Beschleunigung (Schritte pro Sekunde²)

// Variablen für die Motoraktivierung
unsigned long lastMovementTime = 0;
bool motorsEnabled = true;
const unsigned long motorDisableDelay = 30000; // 30 Sekunden
const unsigned long stepDelay = 1000000 / maxSpeed;  // Delay between steps in microseconds

double getCurrentPosition(int axisIndex) {
  if (axisIndex >= 0 && axisIndex < 5) {
    return axes[axisIndex].currentPosition;
  }
  return 0.0;
}

void setCurrentPosition(int axisIndex, double position) {
  if (axisIndex >= 0 && axisIndex < 5) {
    axes[axisIndex].currentPosition = position;
  }
}

void initializePins() {
  for (int i = 0; i < 5; i++) {
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

void stepMotor(int stepPin) {
  digitalWrite(stepPin, HIGH);
  delayMicroseconds(2);
  digitalWrite(stepPin, LOW);
}

void performConcurrentMovements() {
  unsigned long currentTime = micros();
  for (int i = 0; i < 5; i++) {
    if (axes[i].stepsRemaining > 0 && (currentTime - axes[i].lastStepTime >= stepDelay)) {
      digitalWrite(axes[i].dirPin, axes[i].direction ? HIGH : LOW);
      stepMotor(axes[i].stepPin);
      axes[i].stepsRemaining--;
      axes[i].lastStepTime = currentTime;

      // Update the current position
      double position = getCurrentPosition(i);
      if (axes[i].direction) {
        position += stepSize;
      } else {
        position -= stepSize;
      }
      setCurrentPosition(i, position);

      // Print information about the last step
      if (axes[i].stepsRemaining == 0) {
        Serial.print("Achse ");
        Serial.print(axes[i].name);
        Serial.print(" hat seine Bewegung beendet at: ");
        Serial.println(axes[i].currentPosition);
      }
    }
  }
}

void homing() {
  Serial.println("Homing wird ausgeführt...");

  unsigned long homingDelay = 1000000 / homingSpeed;
  for (int i = 0; i < 5; i++) {
    axes[i].isHomed = false;
  }

  for (int i = 0; i < 5; i++) {
    if (digitalRead(axes[i].minPin) == LOW) {
      axes[i].isHomed = true;
    } else {
      digitalWrite(axes[i].dirPin, LOW);
      axes[i].isHomed = false;
    }
  }

  while (!(axes[0].isHomed && axes[1].isHomed && axes[2].isHomed && axes[3].isHomed && axes[4].isHomed)) {
    for (int i = 0; i < 5; i++) {
      if (!axes[i].isHomed && digitalRead(axes[i].minPin) == LOW) {
        axes[i].isHomed = true;
      } else if (!axes[i].isHomed) {
        stepMotor(axes[i].stepPin);
        delayMicroseconds(homingDelay);
      }
    }
  }

  // Set all axes to 0.0 after homing
  for (int i = 0; i < 5; i++) {
    setCurrentPosition(i, 0.0);
  }

  Serial.println("Homing abgeschlossen.");
}

void controlMotor(bool forward, int lowOnStop = HIGH) {
  if (lowOnStop == LOW) {
    Serial.println("DC Motor gestoppt");
  } else {
    Serial.println(forward ? "DC Motor vorwärts" : "DC Motor rückwärts");
  }
  digitalWrite(MOTOR_IN1_PIN, forward ? lowOnStop : LOW);
  digitalWrite(MOTOR_IN2_PIN, forward ? LOW : lowOnStop );
}

void processMotorCommand(String command) {
  if (command == "FORWARD") {
    controlMotor(true);
  } else if (command == "REVERSE") {
    controlMotor(false);
  } else if (command == "STOP") {
    controlMotor(false, LOW);
  }
}

void processCommand(String command) {
  if (command == "HOMING") {
    homing();
    return;
  }

  int spaceIndex = command.indexOf(' ');
  if (spaceIndex == -1)
    return;

  if (command.startsWith("MOTOR")) {
    String motorCommand = command.substring(spaceIndex + 1);
    processMotorCommand(motorCommand);
    return;
  }

  String axis = command.substring(0, spaceIndex);
  float value = command.substring(spaceIndex + 1).toFloat();
  processAxisCommand(axis, value);
}

void processAxisCommand(String axis, double value) {
  for (int i = 0; i < 5; i++) {
    if (axis == axes[i].name) {
      moveAxis(i, value);
      return;
    }
  }
}

void moveAxis(int axisIndex, double target) {
  enableMotors();

  if (target > axes[axisIndex].maxPos) {
    target = axes[axisIndex].maxPos;
  }

  long steps = (target - getCurrentPosition(axisIndex)) / stepSize;

  axes[axisIndex].stepsRemaining = abs(steps);
  axes[axisIndex].direction = steps >= 0;

  lastMovementTime = millis();
}

void enableMotors() {
  if (!motorsEnabled) {
    for (int i = 0; i < 5; i++) {
      digitalWrite(axes[i].enablePin, LOW);
    }
    motorsEnabled = true;
    Serial.println("Motoren aktiviert.");
  }
}

void disableMotors() {
  if (motorsEnabled) {
    for (int i = 0; i < 5; i++) {
      digitalWrite(axes[i].enablePin, HIGH);
    }
    motorsEnabled = false;
    Serial.println("Motoren deaktiviert.");
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("System startet...");

  initializePins();
  enableMotors();
  homing();
  lastMovementTime = millis();
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }

  if (motorsEnabled && (millis() - lastMovementTime >= motorDisableDelay)) {
    disableMotors();
  }

  performConcurrentMovements();
}
