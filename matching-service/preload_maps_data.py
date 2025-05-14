#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de préchargement de données pour le client hybride
Ce script utilise l'API Google Maps pour précharger des données
réelles qui seront utilisées par le client hybride.
"""

import os
import logging
import argparse
import json
from typing import List
from dotenv import load_dotenv
from app.real_data_hybrid_client import RealDataHybridClient

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def preload_from_file(client, filename: str, modes: List[str] = ["driving", "transit"]):
    """
    Précharge des données à partir d'un fichier d'adresses
    
    Args:
        client: Client hybride
        filename: Nom du fichier d'adresses (une adresse par ligne)
        modes: Modes de transport à précharger
    """
    try:
        # Charger les adresses depuis le fichier
        with open(filename, 'r') as f:
            addresses = [line.strip() for line in f if line.strip()]
        
        logger.info(f"Chargé {len(addresses)} adresses depuis {filename}")
        
        # Précharger les données
        client.preload_data(addresses, modes)
        
    except Exception as e:
        logger.error(f"Erreur lors du préchargement depuis {filename}: {e}")

def preload_from_json(client, filename: str, modes: List[str] = ["driving", "transit"]):
    """
    Précharge des données à partir d'un fichier JSON
    
    Args:
        client: Client hybride
        filename: Nom du fichier JSON contenant des adresses
        modes: Modes de transport à précharger
    """
    try:
        # Charger les données depuis le fichier JSON
        with open(filename, 'r') as f:
            data = json.load(f)
        
        # Extraire les adresses
        addresses = []
        
        # Si c'est une liste simple
        if isinstance(data, list):
            for item in data:
                if isinstance(item, str):
                    addresses.append(item)
                elif isinstance(item, dict) and "address" in item:
                    addresses.append(item["address"])
        
        # Si c'est un dictionnaire avec une clé "addresses"
        elif isinstance(data, dict) and "addresses" in data:
            for addr in data["addresses"]:
                if isinstance(addr, str):
                    addresses.append(addr)
                elif isinstance(addr, dict) and "address" in addr:
                    addresses.append(addr["address"])
        
        # Si c'est un dictionnaire avec des candidats et des emplois
        elif isinstance(data, dict):
            # Chercher les adresses dans les champs courants
            address_fields = ["address", "location", "postal_address"]
            
            for key, items in data.items():
                if isinstance(items, list):
                    for item in items:
                        if isinstance(item, dict):
                            for field in address_fields:
                                if field in item and isinstance(item[field], str):
                                    addresses.append(item[field])
        
        # Nettoyer les adresses (enlever les doublons)
        addresses = list(set(addresses))
        
        logger.info(f"Extrait {len(addresses)} adresses uniques depuis {filename}")
        
        # Précharger les données
        client.preload_data(addresses, modes)
        
    except Exception as e:
        logger.error(f"Erreur lors du préchargement depuis {filename}: {e}")

def main():
    """Point d'entrée principal"""
    # Charger les variables d'environnement
    load_dotenv()
    
    # Vérifier la clé API Google Maps
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    if not api_key:
        logger.warning("⚠️ Clé API Google Maps non trouvée dans les variables d'environnement!")
    
    # Créer l'analyseur d'arguments
    parser = argparse.ArgumentParser(description="Préchargement de données pour le client Google Maps hybride")
    
    # Ajouter les arguments
    parser.add_argument("-f", "--file", help="Fichier d'adresses (une par ligne)")
    parser.add_argument("-j", "--json", help="Fichier JSON contenant des adresses")
    parser.add_argument("-c", "--cache", default="data/travel_data_cache.json", 
                        help="Fichier de cache des données")
    parser.add_argument("-m", "--modes", default="driving,transit", 
                        help="Modes de transport à précharger (séparés par des virgules)")
    parser.add_argument("-a", "--addresses", nargs="+", 
                        help="Liste d'adresses à précharger")
    
    # Analyser les arguments
    args = parser.parse_args()
    
    # Vérifier qu'au moins une source de données est spécifiée
    if not args.file and not args.json and not args.addresses:
        parser.print_help()
        logger.error("⚠️ Vous devez spécifier au moins une source de données (fichier, JSON ou adresses)!")
        return
    
    # Convertir les modes en liste
    modes = args.modes.split(",")
    
    # Initialiser le client
    client = RealDataHybridClient(api_key=api_key, cache_file=args.cache)
    
    # Précharger depuis un fichier d'adresses
    if args.file:
        preload_from_file(client, args.file, modes)
    
    # Précharger depuis un fichier JSON
    if args.json:
        preload_from_json(client, args.json, modes)
    
    # Précharger des adresses spécifiées en ligne de commande
    if args.addresses:
        logger.info(f"Préchargement de {len(args.addresses)} adresses spécifiées en ligne de commande")
        client.preload_data(args.addresses, modes)
    
    # Afficher les statistiques
    logger.info("=== Statistiques de préchargement ===")
    logger.info(f"Appels API: {client.stats['api_calls']}")
    logger.info(f"Appels API réussis: {client.stats['api_successes']}")
    logger.info(f"Utilisation du cache: {client.stats['cache_hits']}")
    logger.info(f"Utilisation de fallbacks: {client.stats['fallback_uses']}")
    logger.info(f"Enregistrements dans le cache: {client.stats['cache_saves']}")

if __name__ == "__main__":
    main()