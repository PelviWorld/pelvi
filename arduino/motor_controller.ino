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

void setup() {
  Serial.begin(115200);
  Serial.println("System startet...");

  // Setze Pin-Modi für Schrittmotoren
  pinMode(X_STEP_PIN, OUTPUT);
  pinMode(X_DIR_PIN, OUTPUT);
  pinMode(X_ENABLE_PIN, OUTPUT);
  pinMode(X_MIN_PIN, INPUT_PULLUP);

  pinMode(Y_STEP_PIN, OUTPUT);
  pinMode(Y_DIR_PIN, OUTPUT);
  pinMode(Y_ENABLE_PIN, OUTPUT);
  pinMode(Y_MIN_PIN, INPUT_PULLUP);

  pinMode(Z_STEP_PIN, OUTPUT);
  pinMode(Z_DIR_PIN, OUTPUT);
  pinMode(Z_ENABLE_PIN, OUTPUT);
  pinMode(Z_MIN_PIN, INPUT_PULLUP);

  pinMode(E0_STEP_PIN, OUTPUT);
  pinMode(E0_DIR_PIN, OUTPUT);
  pinMode(E0_ENABLE_PIN, OUTPUT);
  pinMode(E0_MIN_PIN, INPUT_PULLUP);

  pinMode(E1_STEP_PIN, OUTPUT);
  pinMode(E1_DIR_PIN, OUTPUT);
  pinMode(E1_ENABLE_PIN, OUTPUT);
  pinMode(E1_MIN_PIN, INPUT_PULLUP);

  // Setze Pin-Modi für DC-Motorsteuerung
  pinMode(MOTOR_IN1_PIN, OUTPUT);
  pinMode(MOTOR_IN2_PIN, OUTPUT);

  // Motor initial stoppen
  digitalWrite(MOTOR_IN1_PIN, LOW);
  digitalWrite(MOTOR_IN2_PIN, LOW);

  // Aktiviere Schrittmotoren
  enableMotors();

  // Homing durchführen
  Serial.println("Homing wird ausgeführt...");
  homing();
  Serial.println("Homing abgeschlossen.");

  // Setze die Zeit des letzten Bewegungsbefehls
  lastMovementTime = millis();
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    processCommand(command);
  }

  // Überprüfe, ob die Motoren deaktiviert werden sollen
  if (motorsEnabled && (millis() - lastMovementTime >= motorDisableDelay)) {
    disableMotors();
  }
}

void homing() {
  enableMotors(); // Stelle sicher, dass die Motoren aktiviert sind

  // Richtung zu den Endschaltern setzen (LOW für Min-Endschalter)
  digitalWrite(X_DIR_PIN, LOW);
  digitalWrite(Y_DIR_PIN, LOW);
  digitalWrite(Z_DIR_PIN, LOW);
  digitalWrite(E0_DIR_PIN, LOW);
  digitalWrite(E1_DIR_PIN, LOW);

  bool axisHomed[5] = {false, false, false, false, false};
  unsigned long homingDelay = 1000000 / homingSpeed;  // Verzögerung zwischen Schritten in Mikrosekunden

  while (!(axisHomed[0] && axisHomed[1] && axisHomed[2] && axisHomed[3] && axisHomed[4])) {
    if (!axisHomed[0]) {
      if (digitalRead(X_MIN_PIN) == LOW) {
        axisHomed[0] = true;
        currentX = 0;
        Serial.println("X-Achse gehomed.");
      } else {
        stepMotor(X_STEP_PIN);
      }
    }
    if (!axisHomed[1]) {
      if (digitalRead(Y_MIN_PIN) == LOW) {
        axisHomed[1] = true;
        currentY = 0;
        Serial.println("Y-Achse gehomed.");
      } else {
        stepMotor(Y_STEP_PIN);
      }
    }
    if (!axisHomed[2]) {
      if (digitalRead(Z_MIN_PIN) == LOW) {
        axisHomed[2] = true;
        currentZ = 0;
        Serial.println("Z-Achse gehomed.");
      } else {
        stepMotor(Z_STEP_PIN);
      }
    }
    if (!axisHomed[3]) {
      if (digitalRead(E0_MIN_PIN) == LOW) {
        axisHomed[3] = true;
        currentE0 = 0;
        Serial.println("E0-Achse gehomed.");
      } else {
        stepMotor(E0_STEP_PIN);
      }
    }
    if (!axisHomed[4]) {
      if (digitalRead(E1_MIN_PIN) == LOW) {
        axisHomed[4] = true;
        currentE1 = 0;
        Serial.println("E1-Achse gehomed.");
      } else {
        stepMotor(E1_STEP_PIN);
      }
    }
    delayMicroseconds(homingDelay);
  }

  lastMovementTime = millis(); // Aktualisiere die Zeit des letzten Bewegungsbefehls
}

void processCommand(String command) {
  if (command.startsWith("XY")) {
    int commaIndex = command.indexOf(',');
    if (commaIndex > -1) {
      float xTarget = command.substring(2, commaIndex).toFloat();
      float yTarget = command.substring(commaIndex + 1).toFloat();
      Serial.print("Bewege XY zu: ");
      Serial.print(xTarget);
      Serial.print(", ");
      Serial.println(yTarget);
      moveXY(xTarget, yTarget);
    } else {
      Serial.println("Ungültiger XY-Befehl.");
    }
  } else if (command.startsWith("ZE0")) {
    int commaIndex = command.indexOf(',');
    if (commaIndex > -1) {
      float zTarget = command.substring(3, commaIndex).toFloat();
      float e0Target = command.substring(commaIndex + 1).toFloat();
      Serial.print("Bewege Z und E0 zu: ");
      Serial.print(zTarget);
      Serial.print(", ");
      Serial.println(e0Target);
      moveZE0(zTarget, e0Target);
    } else {
      Serial.println("Ungültiger ZE0-Befehl.");
    }
  } else if (command.startsWith("E1")) {
    float e1Target = command.substring(2).toFloat();
    Serial.print("Bewege E1 zu: ");
    Serial.println(e1Target);
    moveE1(e1Target);
  } else if (command == "MOTOR FORWARD") {
    motorForward();
    Serial.println("Motor läuft vorwärts.");
  } else if (command == "MOTOR REVERSE") {
    motorReverse();
    Serial.println("Motor läuft rückwärts.");
  } else if (command == "MOTOR STOP") {
    motorStop();
    Serial.println("Motor gestoppt.");
  } else {
    Serial.println("Unbekannter Befehl.");
  }
}

void moveXY(float xTarget, float yTarget) {
  enableMotors(); // Aktiviere Motoren vor der Bewegung

  if (xTarget < 0) xTarget = 0;
  if (xTarget > X_MAX_POS) xTarget = X_MAX_POS;
  if (yTarget < 0) yTarget = 0;
  if (yTarget > Y_MAX_POS) yTarget = Y_MAX_POS;

  long xSteps = (xTarget - currentX) * stepsPerMM;
  long ySteps = (yTarget - currentY) * stepsPerMM;

  moveLinear(X_STEP_PIN, X_DIR_PIN, xSteps, Y_STEP_PIN, Y_DIR_PIN, ySteps);

  currentX = xTarget;
  currentY = yTarget;

  lastMovementTime = millis(); // Aktualisiere die Zeit des letzten Bewegungsbefehls

  Serial.println("Bewegung XY abgeschlossen.");
}

void moveZE0(float zTarget, float e0Target) {
  enableMotors(); // Aktiviere Motoren vor der Bewegung

  if (zTarget < 0) zTarget = 0;
  if (zTarget > Z_MAX_POS) zTarget = Z_MAX_POS;
  if (e0Target < 0) e0Target = 0;
  if (e0Target > E0_MAX_POS) e0Target = E0_MAX_POS;

  long zSteps = (zTarget - currentZ) * stepsPerMM;
  long e0Steps = (e0Target - currentE0) * stepsPerMM;

  moveLinear(Z_STEP_PIN, Z_DIR_PIN, zSteps, E0_STEP_PIN, E0_DIR_PIN, e0Steps);

  currentZ = zTarget;
  currentE0 = e0Target;

  lastMovementTime = millis(); // Aktualisiere die Zeit des letzten Bewegungsbefehls

  Serial.println("Bewegung ZE0 abgeschlossen.");
}

void moveE1(float e1Target) {
  enableMotors(); // Aktiviere Motoren vor der Bewegung

  if (e1Target < 0) e1Target = 0;
  if (e1Target > E1_MAX_POS) e1Target = E1_MAX_POS;

  long e1Steps = (e1Target - currentE1) * stepsPerMM;

  moveAxis(E1_STEP_PIN, E1_DIR_PIN, e1Steps);

  currentE1 = e1Target;

  lastMovementTime = millis(); // Aktualisiere die Zeit des letzten Bewegungsbefehls

  Serial.println("Bewegung E1 abgeschlossen.");
}

void moveAxis(int stepPin, int dirPin, long steps) {
  bool dir = steps >= 0;
  digitalWrite(dirPin, dir ? HIGH : LOW);
  steps = abs(steps);

  unsigned long stepDelay = 1000000 / maxSpeed;  // Verzögerung zwischen Schritten in Mikrosekunden

  for (long i = 0; i < steps; i++) {
    stepMotor(stepPin);
    delayMicroseconds(stepDelay);  // Geschwindigkeit anpassen
  }
}

void moveLinear(int stepPin1, int dirPin1, long steps1, int stepPin2, int dirPin2, long steps2) {
  bool dir1 = steps1 >= 0;
  bool dir2 = steps2 >= 0;
  digitalWrite(dirPin1, dir1 ? HIGH : LOW);
  digitalWrite(dirPin2, dir2 ? HIGH : LOW);
  steps1 = abs(steps1);
  steps2 = abs(steps2);

  long maxSteps = max(steps1, steps2);
  unsigned long stepDelay = 1000000 / maxSpeed;  // Verzögerung zwischen Schritten in Mikrosekunden

  for (long i = 0; i < maxSteps; i++) {
    if (i < steps1) {
      stepMotor(stepPin1);
    }
    if (i < steps2) {
      stepMotor(stepPin2);
    }
    delayMicroseconds(stepDelay);  // Geschwindigkeit anpassen
  }
}

void stepMotor(int stepPin) {
  digitalWrite(stepPin, HIGH);
  delayMicroseconds(2);
  digitalWrite(stepPin, LOW);
}

// Funktionen zum Aktivieren und Deaktivieren der Motoren
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

// Funktionen zur Steuerung des DC-Motors
void motorForward() {
  digitalWrite(MOTOR_IN1_PIN, HIGH);
  digitalWrite(MOTOR_IN2_PIN, LOW);
}

void motorReverse() {
  digitalWrite(MOTOR_IN1_PIN, LOW);
  digitalWrite(MOTOR_IN2_PIN, HIGH);
}

void motorStop() {
  digitalWrite(MOTOR_IN1_PIN, LOW);
  digitalWrite(MOTOR_IN2_PIN, LOW);
}
