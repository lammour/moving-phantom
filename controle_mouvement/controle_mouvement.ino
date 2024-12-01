#include <Stepper.h>

bool etat = 0; // Initial state is stopped
float x = 0;
float y = 0;

// 32 steps per rotation, with a 1/64 reduction, so 32*64 steps per rotation.
int NbPasTour = 2048;
float pasX = 9.42;
float pasY = 3.768;
int nb_points = 0;

// Stepper motors (assuming 200 steps per rotation) connected to pins 6, 9, 10, and 11.
// Stepper moteurX(NbPasTour, 9, 11, 10, 6);
// Stepper moteurY1(NbPasTour, 9, 11, 10, 6);
// Stepper moteurY2(NbPasTour, 9, 11, 10, 6);

Stepper moteurX(NbPasTour, 3, 5, 4, 2);
Stepper moteurY1(NbPasTour, 7, 9, 8, 6);
Stepper moteurY2(NbPasTour, 11, 13, 12, 10);

// Pointer declarations for dynamic arrays
float* Xcoord = NULL;   // Pointer for X coordinates
float* Ycoord = NULL;   // Pointer for Y coordinates
float* speed = NULL;    // Pointer for speed values

void setup() {
  Serial.begin(9600); // Set up serial communication at 9600 baud rate
  Serial.println("=========================Début=========================");
  
  // Set initial speeds for motors
  moteurX.setSpeed(15);
  moteurY1.setSpeed(15);
  moteurY2.setSpeed(15);
}

void loop() {
  if (Serial.available() > 0) { // Check if data is available on the serial port
    String input = Serial.readStringUntil('\n'); // Read input until newline

    input.trim();  // Trim whitespace from input
    
    // Check if the command starts with "ROUTE"
    if (input.startsWith("ROUTE")) {
      Serial.println("ROUTE command detected.");
      etat = 0; // changement en cours, on arrête le mouvement
      
      // Split the input string
      char axe = input.charAt(6);  // Character after "ROUTE " is "X", "Y" or "S"
      String valeurs = input.substring(8);  // Capture everything after "ROUTE X/Y/S"
      
      // Count the number of values in the string
      nb_points = compterValeurs(valeurs);
      
      // Dynamically allocate an array for coordinates based on the number of values
      float* temp_values = new float[nb_points];
      
      // Extract integer values from the string
      extraireValeurs(valeurs, temp_values, nb_points);
      
      // Store values in the correct array based on "X" or "Y"
      if (axe == 'X') {
        Serial.println("Filling X coordinates.");
        // Release old array and replace it with the new one
        if (Xcoord != NULL) { delete[] Xcoord; }
        Xcoord = temp_values;
      }
      else if (axe == 'Y') {
        Serial.println("Filling Y coordinates.");
        // Release old array and replace it with the new one
        if (Ycoord != NULL) { delete[] Ycoord; }
        Ycoord = temp_values;
      }
      else if (axe == 'S') {
        Serial.println("Filling speed values.");
        // Release old array and replace it with the new one
        if (speed != NULL) { delete[] speed; }
        speed = temp_values;
      }
    }
    else if (input == "START") {
      etat = 1;
    }
    else if (input == "STOP") {
      etat = 0;
    }
    else if (input == "RESET") {
      // Convert distances to steps for each axis
      int nbPasX = round(((0 - x) / pasX) * NbPasTour);
      int nbPasY = round(((0 - y) / pasY) * NbPasTour);
      
      int directionY = (nbPasY >= 0) ? 1 : -1;
      nbPasY = abs(nbPasY);

      moteurX.setSpeed(10);
      moteurY1.setSpeed(10);
      moteurY2.setSpeed(10);

      // Back to (0,0)
      moteurX.step(nbPasX);
      for (int i = 1; i <= nbPasY; i++) {
          moteurY1.step(directionY); // Step motor Y1
          moteurY2.step(directionY); // Step motor Y2 in opposite direction
      }
      
      // Update new coordonates
      x = 0;
      y = 0;
    }
  }

  if (etat) { // If the Start button has been pressed
    Serial.print("Il y a ");
    Serial.print(nb_points);
    Serial.println(" points");

    for (int k = 0; k < nb_points; k++) {
      float xf, yf;

      // Determine where to go
      xf = float(Xcoord[k]);
      yf = float(Ycoord[k]);

      // Print start and end coordinates for the segment
      Serial.print("Segment "); 
      Serial.print(k);
      Serial.print(": Start (");
      Serial.print(x);
      Serial.print(", ");
      Serial.print(y);
      Serial.print("), End (");
      Serial.print(xf);
      Serial.print(", ");
      Serial.print(yf);
      Serial.println(")");

      // Convert distances to steps for each axis
      float nbPasX = round(((xf - x) / pasX) * NbPasTour);
      float nbPasY = round(((yf - y) / pasY) * NbPasTour);
        
      // Print step counts for each axis
      Serial.print("nbPasX : ");
      Serial.println(nbPasX);
      Serial.print("nbPasY : ");
      Serial.println(nbPasY);

      // Determine directions based on the sign of nbPasX and nbPasY
      int directionX = (nbPasX >= 0) ? 1 : -1;
      int directionY = (nbPasY >= 0) ? 1 : -1;

      // Take absolute values for step counting
      nbPasX = abs(nbPasX);
      nbPasY = abs(nbPasY);

      Serial.print("SOMMME PAS : ");
      Serial.println(nbPasX + nbPasY);

      // Calculate the distance between start and end points
      float distance = sqrt(pow((xf - x), 2) + pow((yf - y), 2));
        
      // Calculate time for movement in seconds based on speed
      float temps = distance / speed[k];

      Serial.print("speed[k] : ");
      Serial.println(speed[k]);

      Serial.print("distance : ");
      Serial.println(distance);
      Serial.print("temps : ");
      Serial.println(temps);

      // Calculate setSpeed for movement in rotation per minute
      float setSpeed = (nbPasX + nbPasY)*60/(NbPasTour * temps);
      moteurX.setSpeed(setSpeed);
      moteurY1.setSpeed(setSpeed);
      moteurY2.setSpeed(setSpeed);
      Serial.print("setSpeed : ");
      Serial.println(setSpeed);

      // Perform synchronized movement across both axes
      float maxSteps = max(nbPasX, nbPasY); // Maximum steps for synchronization
      int incrX = 0;
      int incrY = 0;

      unsigned long startTime, endTime;
      startTime = millis();

      Serial.println("début");
      for (int i = 1; i <= maxSteps; i++) {
        // Increment steps for each motor based on maxSteps
        if (incrX < i * nbPasX / maxSteps) {
          moteurX.step(directionX); // Step motor X
          incrX++;
        }
        if (incrY < i * nbPasY / maxSteps) {
          moteurY1.step(directionY); // Step motor Y1
          moteurY2.step(directionY); // Step motor Y2 in opposite direction
          incrY++;
        }
      }
      endTime = millis();
      Serial.print("Durée d'exécution : ");
      Serial.print(endTime - startTime);
      Serial.println(" microsecondes");

      // Update new coordonates
      x = xf;
      y = yf;
    }
  }
}


// Counts the number of values in a space-separated string
int compterValeurs(String valeurs) {
  int count = 1;  // At least one value
  for (int i = 0; i < valeurs.length(); i++) {
    if (valeurs.charAt(i) == ' ') {
      count++;
    }
  }
  return count;
}

// Extracts values from a space-separated string into a float array
void extraireValeurs(String valeurs, float* tableau, int taille) {
  char buffer[valeurs.length() + 1];
  valeurs.toCharArray(buffer, valeurs.length() + 1);

  // Use strtok to split values
  char* token = strtok(buffer, " ");
  int index = 0;

  while (token != NULL && index < taille) {
    tableau[index] = atof(token);  // Convert to float and store in array
    token = strtok(NULL, " ");
    index++;
  }
}