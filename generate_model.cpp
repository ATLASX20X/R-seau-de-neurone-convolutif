#include <iostream>
#include <fstream>
#include <random>
#include <cmath>

int main() {
    std::ofstream file("model_weights.txt");
    if (!file.is_open()) {
        std::cout << "Erreur lors de la création du fichier\n";
        return 1;
    }

    std::mt19937 gen(123);
    std::normal_distribution<double> dist(0.0, 0.05);

    // Poids de convolution: 4 filtres x 1 canal x 3x3
    std::cout << "Génération des poids de convolution...\n";
    for (int f = 0; f < 4; ++f) {
        for (int i = 0; i < 3; ++i) {
            for (int j = 0; j < 3; ++j) {
                // Différents filtres pour détecter différentes caractéristiques
                double weight;
                if (f == 0) {
                    // Filtre vertical
                    weight = (j == 1) ? 0.5 : -0.1;
                } else if (f == 1) {
                    // Filtre horizontal
                    weight = (i == 1) ? 0.5 : -0.1;
                } else if (f == 2) {
                    // Filtre diagonal
                    weight = (i == j) ? 0.4 : -0.1;
                } else {
                    // Filtre aléatoire
                    weight = dist(gen);
                }
                file << weight << " ";
            }
        }
    }

    // Biais de convolution
    for (int f = 0; f < 4; ++f) {
        file << 0.1 << " ";
    }

    // Poids de la couche dense: 10 classes x 676 entrées
    std::cout << "Génération des poids de la couche dense...\n";
    for (int c = 0; c < 10; ++c) {
        for (int i = 0; i < 676; ++i) {
            // Initialisation avec une petite variation
            double weight = dist(gen);
            file << weight << " ";
        }
    }

    // Biais de la couche dense
    for (int c = 0; c < 10; ++c) {
        file << 0.0 << " ";
    }

    file.close();
    std::cout << "Modèle généré et sauvegardé dans model_weights.txt\n";
    return 0;
}
