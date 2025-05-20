import pickle
import os
import numpy as np
from sklearn.linear_model import LinearRegression

# Créer un modèle simple
model = LinearRegression()
# Caractéristiques: [match_score, satisfaction_contrainte1, satisfaction_contrainte2]
X = np.array([[0.9, 0.8, 0.7], [0.6, 0.5, 0.9], [0.8, 0.7, 0.6]])
# Labels: succès du match (0-1)
y = np.array([0.85, 0.70, 0.75])
model.fit(X, y)

# Sauvegarder le modèle
os.makedirs('models', exist_ok=True)
with open('models/ml_optimizer.pkl', 'wb') as f:
    pickle.dump(model, f)

print("Modèle ML initial créé avec succès!")