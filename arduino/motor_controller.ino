// Pin-Definitionen
#define X_STEP_PIN       54
#define X_DIR_PIN        55
#define Y_STEP_PIN       60
#define Y_DIR_PIN        61
#define Z_STEP_PIN       46
#define Z_DIR_PIN        48
#define E0_STEP_PIN      26
#define E0_DIR_PIN       28
#define E1_STEP_PIN      36
#define E1_DIR_PIN       34

#define X_ENABLE_PIN     38
#define Y_ENABLE_PIN     56
#define Z_ENABLE_PIN     62
#define E0_ENABLE_PIN    24
#define E1_ENABLE_PIN    30

#define X_MIN_PIN        3
#define Y_MIN_PIN        14
#define Z_MIN_PIN        18
#define E0_MIN_PIN       2   // Verwendet XMAX-Pin
#define E1_MIN_PIN       15  // Verwendet YMAX-Pin

// DC-Motorsteuerung Pins (H-Brücke)
#define MOTOR_IN1_PIN    40   // Verbunden mit IN1 der H-Brücke
#define MOTOR_IN2_PIN    44   // Verbunden mit IN2 der H-Brücke

// Konfiguration
const float stepsPerMM = 800.0;      // Schritte pro mm (gemäß Ihrer Kalibrierung)
const int maxSpeed = 28000;          // Maximale Geschwindigkeit (Schritte pro Sekunde)
const int homingSpeed = 25000;       // Homing-Geschwindigkeit (Schritte pro Sekunde)
const int acceleration = 70;         // Beschleunigung (Schritte pro Sekunde²)

// Maximale Achsenpositionen (Software-Endlagen in mm)
const float X_MAX_POS = 300.0;
const float Y_MAX_POS = 470.0;
const float Z_MAX_POS = 290.0;
const float E0_MAX_POS = 180.0;
const float E1_MAX_POS = 180.0;

// Axis name to axis index map
const char* axis_names[] = {"X", "Y", "Z", "E0", "E1"};

// Aktuelle Positionen
float current_position[] = {0.0, 0.0, 0.0, 0.0, 0.0};

// Variablen für die Motoraktivierung
unsigned long lastMovementTime = 0;
bool motorsEnabled = true;
const unsigned long motorDisableDelay = 30000; // 30 Sekunden in Millisekunden

struct AxisState {
  int stepPin;
  int dirPin;
  long stepsRemaining;
  unsigned long lastStepTime;
  bool direction;
};

AxisState axes[5] = {
  {X_STEP_PIN, X_DIR_PIN, 0, 0, true},
  {Y_STEP_PIN, Y_DIR_PIN, 0, 0, true},
  {Z_STEP_PIN, Z_DIR_PIN, 0, 0, true},
  {E0_STEP_PIN, E0_DIR_PIN, 0, 0, true},
  {E1_STEP_PIN, E1_DIR_PIN, 0, 0, true}
};

const unsigned long stepDelay = 1000000 / maxSpeed;  // Delay between steps in microseconds

float getCurrentPosition(int axisIndex) {
  if (axisIndex >= 0 && axisIndex < 5) {
    return current_position[axisIndex];
  }
  return 0.0;
}

void setCurrentPosition(int axisIndex, float position) {
  if (axisIndex >= 0 && axisIndex < 5) {
    current_position[axisIndex] = position;
  }
}

// Helper function to get the axis name from the axis index
const char* getAxisName(int axisIndex) {
  if (axisIndex >= 0 && axisIndex < 5) {
    return axis_names[axisIndex];
  }
  return "";
}

void initializePins() {
  int stepPins[] = {X_STEP_PIN, Y_STEP_PIN, Z_STEP_PIN, E0_STEP_PIN, E1_STEP_PIN};
  int dirPins[] = {X_DIR_PIN, Y_DIR_PIN, Z_DIR_PIN, E0_DIR_PIN, E1_DIR_PIN};
  int enablePins[] = {X_ENABLE_PIN, Y_ENABLE_PIN, Z_ENABLE_PIN, E0_ENABLE_PIN, E1_ENABLE_PIN};
  int minPins[] = {X_MIN_PIN, Y_MIN_PIN, Z_MIN_PIN, E0_MIN_PIN, E1_MIN_PIN};

  for (int i = 0; i < 5; i++) {
    pinMode(stepPins[i], OUTPUT);
    pinMode(dirPins[i], OUTPUT);
    pinMode(enablePins[i], OUTPUT);
    pinMode(minPins[i], INPUT_PULLUP);
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

      // Print information about the last step
      if (axes[i].stepsRemaining == 0) {
        String axisName = getAxisName(i);
        Serial.print("Achse ");
        Serial.print(axisName);
        Serial.println(" hat seine Bewegung beendet.");
      }
    }
  }
}

void homing() {
  Serial.println("Homing wird ausgeführt...");

  int dirPins[] = {X_DIR_PIN, Y_DIR_PIN, Z_DIR_PIN, E0_DIR_PIN, E1_DIR_PIN};
  int minPins[] = {X_MIN_PIN, Y_MIN_PIN, Z_MIN_PIN, E0_MIN_PIN, E1_MIN_PIN};
  bool axisHomed[5] = {false, false, false, false, false};
  unsigned long homingDelay = 1000000 / homingSpeed;

  for (int i = 0; i < 5; i++) {
    digitalWrite(dirPins[i], LOW);
  }

  while (!(axisHomed[0] && axisHomed[1] && axisHomed[2] && axisHomed[3] && axisHomed[4])) {
    for (int i = 0; i < 5; i++) {
      if (!axisHomed[i] && digitalRead(minPins[i]) == LOW) {
        axisHomed[i] = true;
      } else if (!axisHomed[i]) {
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
  int spaceIndex = command.indexOf(' ');
  String axis = command.substring(0, spaceIndex);
  if (spaceIndex == -1)
    return;

  if (command.startsWith("MOTOR")) {
    String motorCommand = command.substring(spaceIndex + 1);
    processMotorCommand(motorCommand);
    return;
  } else {
    float value = command.substring(spaceIndex + 1).toFloat();
    processAxisCommand(axis, value);
  }
}

void processAxisCommand(String axis, float value) {
  for (int i = 0; i < 5; i++) {
    if (axis == axis_names[i]) {
      moveAxis(i, value);
      return;
    }
  }
}

void moveAxis(int axisIndex, float target) {
  enableMotors();

  float maxPos[] = {X_MAX_POS, Y_MAX_POS, Z_MAX_POS, E0_MAX_POS, E1_MAX_POS};
  if (target > maxPos[axisIndex]) target = maxPos[axisIndex];

  long steps = (target - getCurrentPosition(axisIndex)) * stepsPerMM;

  axes[axisIndex].stepsRemaining = abs(steps);
  axes[axisIndex].direction = steps >= 0;

  setCurrentPosition(axisIndex, target);

  lastMovementTime = millis();
}


void enableMotors() {
  if (!motorsEnabled) {
    digitalWrite(X_ENABLE_PIN, LOW);
    digitalWrite(Y_ENABLE_PIN, LOW);
    digitalWrite(Z_ENABLE_PIN, LOW);
    digitalWrite(E0_ENABLE_PIN, LOW);
    digitalWrite(E1_ENABLE_PIN, LOW);
    motorsEnabled = true;
    Serial.println("Motoren aktiviert.");
  }
}

void disableMotors() {
  if (motorsEnabled) {
    digitalWrite(X_ENABLE_PIN, HIGH);
    digitalWrite(Y_ENABLE_PIN, HIGH);
    digitalWrite(Z_ENABLE_PIN, HIGH);
    digitalWrite(E0_ENABLE_PIN, HIGH);
    digitalWrite(E1_ENABLE_PIN, HIGH);
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
