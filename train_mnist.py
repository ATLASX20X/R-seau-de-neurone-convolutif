#!/usr/bin/env python3
"""
Script Python pour entraîner un CNN simple sur MNIST et sauvegarder les poids
pour utilisation dans le programme C++.
"""

import torch
import torch.nn as nn
import torch.optim as optim
from torchvision import datasets, transforms
import numpy as np

# Définition du CNN (même architecture que le C++)
class SimpleCNN(nn.Module):
    def __init__(self):
        super(SimpleCNN, self).__init__()
        self.conv = nn.Conv2d(1, 4, kernel_size=3)  # 1 canal -> 4 filtres, kernel 3x3
        self.pool = nn.MaxPool2d(2, 2)  # 2x2
        self.fc = nn.Linear(4 * 13 * 13, 10)  # 676 -> 10

    def forward(self, x):
        x = torch.relu(self.conv(x))
        x = self.pool(x)
        x = x.view(-1, 4 * 13 * 13)
        x = self.fc(x)
        return x

def train_model():
    print("Chargement du dataset MNIST...")
    # Data augmentation pour améliorer la généralisation
    transform_train = transforms.Compose([
        transforms.RandomAffine(degrees=5, translate=(0.1, 0.1), scale=(0.9, 1.1)),
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    transform_test = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.1307,), (0.3081,))
    ])

    train_dataset = datasets.MNIST('./data', train=True, download=True, transform=transform_train)
    test_dataset = datasets.MNIST('./data', train=False, download=True, transform=transform_test)

    train_loader = torch.utils.data.DataLoader(train_dataset, batch_size=128, shuffle=True)
    test_loader = torch.utils.data.DataLoader(test_dataset, batch_size=1000, shuffle=False)

    print("Initialisation du modele...")
    model = SimpleCNN()
    criterion = nn.CrossEntropyLoss()
    # Meilleur learning rate avec scheduler
    optimizer = optim.Adam(model.parameters(), lr=0.003)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=2, gamma=0.5)

    print("Debut de l'entrainement (10 epochs)...")
    best_accuracy = 0

    for epoch in range(10):
        model.train()
        total_loss = 0
        correct = 0
        total = 0

        for batch_idx, (data, target) in enumerate(train_loader):
            optimizer.zero_grad()
            output = model(data)
            loss = criterion(output, target)
            loss.backward()
            optimizer.step()

            total_loss += loss.item()
            _, predicted = torch.max(output.data, 1)
            total += target.size(0)
            correct += (predicted == target).sum().item()

            if batch_idx % 100 == 0:
                print(f"  Epoch {epoch+1}/10 | Batch {batch_idx}/{len(train_loader)} | "
                      f"Loss: {loss.item():.4f} | Acc: {100.*correct/total:.2f}%")

        print(f"Epoch {epoch+1} terminee | Loss moyen: {total_loss/len(train_loader):.4f} | "
              f"Accuracy: {100.*correct/total:.2f}%")

        # Evaluation sur le test set
        model.eval()
        test_correct = 0
        test_total = 0
        with torch.no_grad():
            for data, target in test_loader:
                output = model(data)
                _, predicted = torch.max(output.data, 1)
                test_total += target.size(0)
                test_correct += (predicted == target).sum().item()

        test_accuracy = 100. * test_correct / test_total
        print(f"  Test Accuracy: {test_accuracy:.2f}%")

        if test_accuracy > best_accuracy:
            best_accuracy = test_accuracy
            print(f"  Nouveau meilleur modele ! Sauvegarde...")
            save_weights(model, "model_weights_best.txt")

        scheduler.step()

    print(f"\nMeilleure accuracy finale: {best_accuracy:.2f}%")
    # Copier le meilleur modele vers model_weights.txt
    import shutil
    if best_accuracy > 0:
        shutil.copy("model_weights_best.txt", "model_weights.txt")
        print("Meilleur modele sauvegarde dans model_weights.txt")

def save_weights(model, filename):
    """Sauvegarde les poids dans un format compatible avec le C++"""
    with open(filename, 'w') as file:
        # Poids de convolution: [4][1][3][3]
        conv_weights = model.conv.weight.data.numpy()
        for f in range(4):
            for c in range(1):
                for i in range(3):
                    for j in range(3):
                        file.write(f"{conv_weights[f][c][i][j]:.6f} ")

        # Biais de convolution: [4]
        conv_bias = model.conv.bias.data.numpy()
        for f in range(4):
            file.write(f"{conv_bias[f]:.6f} ")

        # Poids de la couche dense: [10][676]
        fc_weights = model.fc.weight.data.numpy()
        for c in range(10):
            for i in range(676):
                file.write(f"{fc_weights[c][i]:.6f} ")

        # Biais de la couche dense: [10]
        fc_bias = model.fc.bias.data.numpy()
        for c in range(10):
            file.write(f"{fc_bias[c]:.6f} ")

if __name__ == "__main__":
    print("=" * 60)
    print("  ENTRAINEMENT CNN SUR MNIST POUR C++")
    print("=" * 60)
    train_model()
    print("\nTermine ! Vous pouvez maintenant utiliser ./AI.exe")
