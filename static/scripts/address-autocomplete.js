/**
 * Script d'intégration Google Maps pour le champ d'adresse du questionnaire candidat
 */

// Fonction principale d'initialisation
function initAddressAutocomplete() {
  // Vérifier si l'autocomplétion a déjà été initialisée (pour éviter les doubles initialisations)
  if (window._addressAutocompleteInitialized) {
    console.log('Google Maps Autocomplete déjà initialisé, ignoré.');
    return;
  }
  
  console.log('Initialisation de Google Maps Autocomplete...');
  
  // Sélection du champ d'adresse
  const addressInput = document.getElementById('address');
  
  if (!addressInput) {
    console.error("Champ d'adresse non trouvé dans le formulaire");
    return;
  }
  
  try {
    // Création de l'autocomplétion
    const autocomplete = new google.maps.places.Autocomplete(addressInput, {
      types: ['address'],
      componentRestrictions: { country: 'fr' },
      fields: ['address_components', 'formatted_address', 'geometry', 'place_id']
    });
    
    // Ajout d'un conteneur pour les coordonnées (s'il n'existe pas déjà)
    let coordsContainer = document.getElementById('address-coords-container');
    if (!coordsContainer) {
      coordsContainer = document.createElement('div');
      coordsContainer.id = 'address-coords-container';
      coordsContainer.style.display = 'none';
      
      // Création des champs cachés s'ils n'existent pas déjà
      if (!document.getElementById('address-lat')) {
        const latInput = document.createElement('input');
        latInput.type = 'hidden';
        latInput.id = 'address-lat';
        latInput.name = 'address-lat';
        coordsContainer.appendChild(latInput);
      }
      
      if (!document.getElementById('address-lng')) {
        const lngInput = document.createElement('input');
        lngInput.type = 'hidden';
        lngInput.id = 'address-lng';
        lngInput.name = 'address-lng';
        coordsContainer.appendChild(lngInput);
      }
      
      if (!document.getElementById('address-place-id')) {
        const placeIdInput = document.createElement('input');
        placeIdInput.type = 'hidden';
        placeIdInput.id = 'address-place-id';
        placeIdInput.name = 'address-place-id';
        coordsContainer.appendChild(placeIdInput);
      }
      
      // Insérer les champs cachés
      addressInput.parentNode.insertBefore(coordsContainer, addressInput.nextSibling);
    }
    
    // Écouter les événements de l'autocomplétion
    autocomplete.addListener('place_changed', function() {
      const place = autocomplete.getPlace();
      console.log('Place selected:', place);
      
      if (!place.geometry) {
        console.error('Aucune géométrie trouvée pour cette adresse');
        return;
      }
      
      // Mise à jour des champs cachés
      document.getElementById('address-lat').value = place.geometry.location.lat();
      document.getElementById('address-lng').value = place.geometry.location.lng();
      document.getElementById('address-place-id').value = place.place_id;
      
      // Mise à jour du champ d'adresse
      addressInput.value = place.formatted_address;
      addressInput.classList.add('address-validated');
      
      if (window.showNotification) {
        window.showNotification('Adresse validée avec succès', 'success');
      }
    });
    
    // Marquer comme initialisé pour éviter les doublons
    window._addressAutocompleteInitialized = true;
    console.log('Autocomplétion Google Maps initialisée avec succès!');
  } catch (error) {
    console.error('Erreur lors de l\'initialisation de Google Maps Autocomplete:', error);
  }
}

// Créer une fonction d'initialisation globale pour que l'API Google Maps puisse l'appeler
window.initGoogleMapsAutocomplete = function() {
  console.log('Callback Google Maps appelé');
  initAddressAutocomplete();
};

// Ajouter des styles pour l'adresse validée si ce n'est pas déjà fait
if (!document.getElementById('google-maps-autocomplete-styles')) {
  const style = document.createElement('style');
  style.id = 'google-maps-autocomplete-styles';
  style.textContent = `
    .address-validated {
      border-color: #10B981 !important;
      background-color: rgba(16, 185, 129, 0.05) !important;
    }
    
    .pac-container {
      z-index: 10000 !important;
      border-radius: 8px !important;
      box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15) !important;
      font-family: 'Inter', sans-serif !important;
      border: none !important;
      margin-top: 5px !important;
    }
    
    .pac-item {
      padding: 10px !important;
      cursor: pointer !important;
    }
    
    .pac-item:hover {
      background-color: rgba(124, 58, 237, 0.05) !important;
    }
    
    .pac-item-selected {
      background-color: rgba(124, 58, 237, 0.1) !important;
    }
  `;
  document.head.appendChild(style);
  console.log('Styles Google Maps Autocomplete ajoutés');
}

// Vérifier si Google Maps est déjà chargé
if (window.google && window.google.maps && window.google.maps.places) {
  console.log('API Google Maps déjà chargée, initialisation directe');
  initAddressAutocomplete();
} else {
  console.log('En attente du chargement de Google Maps via le tag script...');
}
