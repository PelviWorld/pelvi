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

// Aktuelle Positionen
float currentX = 0;
float currentY = 0;
float currentZ = 0;
float currentE0 = 0;
float currentE1 = 0;

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

  currentX = 0;
  currentY = 0;
  currentZ = 0;
  currentE0 = 0;
  currentE1 = 0;

  Serial.println("Homing abgeschlossen.");
}

void processCommand(String command) {
  if (command.startsWith("XY")) {
    float xTarget = command.substring(2).toFloat();
    float yTarget = command.substring(command.indexOf(' ') + 1).toFloat();
    moveAxis(0, xTarget);
    moveAxis(1, yTarget);
  } else if (command.startsWith("ZE0")) {
    float zTarget = command.substring(3).toFloat();
    float e0Target = command.substring(command.indexOf(' ') + 1).toFloat();
    moveAxis(2, zTarget);
    moveAxis(3, e0Target);
  } else if (command.startsWith("E1")) {
    float e1Target = command.substring(2).toFloat();
    moveAxis(4, e1Target);
  } else if (command == "MOTOR FORWARD") {
    controlMotor(true);
  } else if (command == "MOTOR REVERSE") {
    controlMotor(false);
  } else if (command == "MOTOR STOP") {
    controlMotor(false, LOW);
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

float getCurrentPosition(int axisIndex) {
  switch (axisIndex) {
    case 0: return currentX;
    case 1: return currentY;
    case 2: return currentZ;
    case 3: return currentE0;
    case 4: return currentE1;
    default: return 0;
  }
}

void setCurrentPosition(int axisIndex, float position) {
  switch (axisIndex) {
    case 0: currentX = position; break;
    case 1: currentY = position; break;
    case 2: currentZ = position; break;
    case 3: currentE0 = position; break;
    case 4: currentE1 = position; break;
  }
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
        Serial.print("Achse ");
        Serial.print(i);
        Serial.println(" hat seine Bewegung beendet.");
      }
    }
  }
}

void stepMotor(int stepPin) {
  digitalWrite(stepPin, HIGH);
  delayMicroseconds(2);
  digitalWrite(stepPin, LOW);
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

void controlMotor(bool forward, int lowOnStop = HIGH) {
  if (lowOnStop == LOW) {
    Serial.println("DC Motor gestoppt");
  } else {
    Serial.println(forward ? "DC Motor vorwärts" : "DC Motor rückwärts");
  }
  digitalWrite(MOTOR_IN1_PIN, forward ? lowOnStop : LOW);
  digitalWrite(MOTOR_IN2_PIN, forward ? LOW : lowOnStop );
}
