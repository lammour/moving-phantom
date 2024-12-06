#include <Stepper.h>

// Variable indiquant l'état (0 : arrêt, 1 : mouvement)
bool etat = 0; 

// Coordonnées actuelles
float x = 0;
float y = 0;

// Paramètres des moteurs pas à pas
const int NbPasTour = 2048; // Nombre de pas par tour complet (après réduction)
const float pasX = 9.42;    // Distance en mm par pas pour l'axe X
const float pasY = 4.042;   // Distance en mm par pas pour l'axe Y

// Déclarations des moteurs pas à pas
Stepper moteurX(NbPasTour, 3, 5, 4, 2);
Stepper moteurY1(NbPasTour, 7, 9, 8, 6);
Stepper moteurY2(NbPasTour, 11, 13, 12, 10);

// Pointeurs pour les tableaux dynamiques
float* Xcoord = NULL;   // Coordonnées en X
float* Ycoord = NULL;   // Coordonnées en Y
float* speed = NULL;    // Vitesse à chaque point
int nb_points = 0;      // Nombre de points du chemin

// Initialisation
void setup() {
    Serial.begin(9600); // Configuration de la communication série

    // Configuration des vitesses des moteurs
    moteurX.setSpeed(16);
    moteurY1.setSpeed(16);
    moteurY2.setSpeed(16);
}

// Boucle principale
void loop() {
    if (Serial.available() > 0) { // Si des données sont disponibles sur le port série
        String input = Serial.readStringUntil('\n'); // Lecture des données
        input.trim(); // Suppression des espaces inutiles

        // Traitement des commandes reçues
        if (input.startsWith("ROUTE")) {
            etat = 0; // Arrêt du mouvement pendant le traitement
            char axe = input.charAt(6); // Identification de l'axe (X, Y ou S)
            String valeurs = input.substring(8); // Extraction des valeurs

            nb_points = compterValeurs(valeurs); // Calcul du nombre de points
            float* temp_values = new float[nb_points]; // Allocation dynamique du tableau
            extraireValeurs(valeurs, temp_values, nb_points); // Extraction des valeurs

            // Mise à jour des coordonnées ou vitesses en fonction de l'axe
            if (axe == 'X') {
                if (Xcoord != NULL) delete[] Xcoord;
                Xcoord = temp_values;
            } else if (axe == 'Y') {
                if (Ycoord != NULL) delete[] Ycoord;
                Ycoord = temp_values;
            } else if (axe == 'S') {
                if (speed != NULL) delete[] speed;
                speed = temp_values;
            }
        } else if (input == "START") {
            etat = 1; // Démarrage du mouvement
        } else if (input == "STOP") {
            etat = 0; // Arrêt du mouvement
        } else if (input == "RESET") {
            resetPosition(); // Réinitialisation à la position (0, 0)
        }
    }

    if (etat) { // Si l'état est actif (mouvement en cours)
        executeChemin(); // Exécution du chemin prédéfini
    }
}

// Fonction de réinitialisation à la position (0, 0)
void resetPosition() {
    int nbPasX = round(((0 - x) / pasX) * NbPasTour);
    int nbPasY = round(((0 - y) / pasY) * NbPasTour);
    int directionY = (nbPasY >= 0) ? 1 : -1;
    nbPasY = abs(nbPasY);

    moteurX.setSpeed(10);
    moteurX.step(nbPasX); // Retour sur X
    moteurX.setSpeed(16);
    for (int i = 1; i <= nbPasY; i++) {
        moteurY1.step(directionY); // Retour sur Y1
        moteurY2.step(directionY); // Retour sur Y2
    }

    x = 0;
    y = 0;
}

// Fonction d'exécution du chemin
void executeChemin() {
    for (int k = 0; k < nb_points; k++) {
        float xf = Xcoord[k];
        float yf = Ycoord[k];

        float nbPasX = round(((xf - x) / pasX) * NbPasTour);
        float nbPasY = round(((yf - y) / pasY) * NbPasTour);

        int directionX = (nbPasX >= 0) ? 1 : -1;
        int directionY = (nbPasY >= 0) ? 1 : -1;

        nbPasX = abs(nbPasX);
        nbPasY = abs(nbPasY);

        float maxSteps = max(nbPasX, nbPasY);
        float stepTempo = (speed != NULL) ? (1000 * (sqrt(pow((xf - x), 2) + pow((yf - y), 2)) / speed[k]) / maxSteps) : 1;

        int incrX = 0;
        int incrY = 0;

        unsigned long nextStepTime = millis();
        for (int i = 1; i <= maxSteps; i++) {
            while (millis() < nextStepTime) {}
            if (incrX < i * (nbPasX / maxSteps)) {
                moteurX.step(directionX);
                incrX++;
            }
            if (incrY < i * (nbPasY / maxSteps)) {
                moteurY1.step(directionY);
                moteurY2.step(directionY);
                incrY++;
            }
            nextStepTime += stepTempo;
        }

        x = xf;
        y = yf;
    }
}

// Fonction pour compter le nombre de valeurs dans une chaîne
int compterValeurs(String valeurs) {
    int count = 1;
    for (int i = 0; i < valeurs.length(); i++) {
        if (valeurs.charAt(i) == ' ') count++;
    }
    return count;
}

// Fonction pour extraire les valeurs d'une chaîne dans un tableau float
void extraireValeurs(String valeurs, float* tableau, int taille) {
    char buffer[valeurs.length() + 1];
    valeurs.toCharArray(buffer, valeurs.length() + 1);

    char* token = strtok(buffer, " ");
    int index = 0;

    while (token != NULL && index < taille) {
        tableau[index] = atof(token);
        token = strtok(NULL, " ");
        index++;
    }
}
