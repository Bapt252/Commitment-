#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adresses d'exemple pour les tests du système Nexten SmartMatch
"""

# Adresses françaises pour les tests
SAMPLE_ADDRESSES = [
    "20 Rue de la Paix, 75002 Paris, France",
    "10 Place Bellecour, 69002 Lyon, France",
    "42 Rue des Dames, 44000 Nantes, France",
    "5 Rue du Commerce, 33000 Bordeaux, France",
    "18 Avenue de la République, 13001 Marseille, France",
    "7 Rue des Carmes, 54000 Nancy, France",
    "25 Rue des Lices, 84000 Avignon, France",
    "15 Quai des Bateliers, 67000 Strasbourg, France",
    "8 Rue Félix Le Dantec, 29000 Quimper, France",
    "30 Place du Capitole, 31000 Toulouse, France"
]

# Couples d'adresses pour simuler des matchings entreprise-candidat
SAMPLE_MATCHING_PAIRS = [
    {
        "candidate": "10 Rue de Rivoli, 75004 Paris, France",
        "company": "Tour Montparnasse, 33 Avenue du Maine, 75015 Paris, France",
        "expected_commute": {
            "driving": 15,
            "transit": 25,
            "walking": 60
        }
    },
    {
        "candidate": "Place Bellecour, 69002 Lyon, France",
        "company": "10 Rue de la République, 69001 Lyon, France",
        "expected_commute": {
            "driving": 5,
            "transit": 10,
            "walking": 15
        }
    },
    {
        "candidate": "Nantes Atlantique, France",
        "company": "Tour Bretagne, 44000 Nantes, France",
        "expected_commute": {
            "driving": 20,
            "transit": 45,
            "walking": 120
        }
    },
    {
        "candidate": "Aéroport de Marseille Provence, France",
        "company": "4 Place Sadi Carnot, 13002 Marseille, France",
        "expected_commute": {
            "driving": 30,
            "transit": 60,
            "walking": 180
        }
    }
]

# Exemples de cas limites ou de longue distance
EDGE_CASES = [
    {
        "description": "Très longue distance",
        "origin": "Paris, France",
        "destination": "Nice, France"
    },
    {
        "description": "Destination inaccessible à pied",
        "origin": "Paris, France",
        "destination": "Mont Saint-Michel, France" 
    },
    {
        "description": "Adresse mal formatée",
        "origin": "Boulevard Haussmann Paris",
        "destination": "La Defense"
    },
    {
        "description": "Code postal uniquement",
        "origin": "75001",
        "destination": "92100"
    }
]

# Exemples d'adresses d'organisations en France
COMPANY_ADDRESSES = {
    "tech": [
        "12 Rue Ampère, 38000 Grenoble, France", # Pôle technologique
        "2 Rue Kellermann, 59100 Roubaix, France", # OVH
        "8 Rue de Londres, 75009 Paris, France", # Siège social
        "Station F, 5 Parvis Alan Turing, 75013 Paris, France" # Incubateur
    ],
    "finance": [
        "23 Avenue de la Grande Armée, 75116 Paris, France",
        "1 Boulevard Haussmann, 75009 Paris, France",
        "16 Rue de la Banque, 69002 Lyon, France"
    ],
    "education": [
        "60 Boulevard Saint-Michel, 75006 Paris, France", # Sorbonne
        "7 Place Fontenoy, 75007 Paris, France", # UNESCO
        "15 Rue Soufflot, 75005 Paris, France" # Université
    ]
}
