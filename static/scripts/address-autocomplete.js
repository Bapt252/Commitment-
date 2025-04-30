/**
 * Script d'autocomplétion d'adresse avec Google Maps
 * Ce script implémente une autocomplétion d'adresse sophistiquée avec plusieurs fonctionnalités:
 * - Prédiction d'adresses pendant la saisie
 * - Extraction des coordonnées géographiques
 * - Sauvegarde du place_id pour des opérations futures
 * - Validation visuelle de l'adresse sélectionnée
 */

// Variable globale pour l'instance d'autocomplétion
let addressAutocomplete = null;

// Fonction de callback pour Google Maps API
window.initAutocompleteCallback = function() {
  console.log("Google Maps API chargée, initialisation de l'autocomplétion");
  initializeAddressAutocomplete();
};

/**
 * Initialise l'autocomplétion d'adresse
 */
function initializeAddressAutocomplete() {
  const addressInput = document.getElementById('address');
  
  if (!addressInput) {
    console.error("Erreur: Champ d'adresse non trouvé");
    return;
  }
  
  // Vérification de la disponibilité de l'API Google Maps
  if (typeof google === 'undefined' || !google.maps || !google.maps.places) {
    console.error("Erreur: L'API Google Maps n'est pas disponible");
    return;
  }
  
  try {
    // Configuration de l'autocomplétion
    addressAutocomplete = new google.maps.places.Autocomplete(addressInput, {
      types: ['address'],
      componentRestrictions: { country: 'fr' }, // Limiter aux adresses françaises
      fields: ['address_components', 'geometry', 'place_id', 'formatted_address']
    });
    
    // Style personnalisé pour améliorer l'interface
    addressInput.placeholder = "Saisissez votre adresse complète";
    
    // Gestion de l'événement de sélection d'adresse
    addressAutocomplete.addListener('place_changed', handlePlaceSelection);
    
    // Éviter la soumission du formulaire lors de la sélection d'une suggestion
    addressInput.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && document.activeElement === addressInput) {
        e.preventDefault();
      }
    });
    
    // Gérer le focus et la perte de focus
    addressInput.addEventListener('focus', function() {
      addressInput.classList.add('focused');
    });
    
    addressInput.addEventListener('blur', function() {
      addressInput.classList.remove('focused');
      
      // Validation supplémentaire lors de la perte de focus
      setTimeout(validateAddressOnBlur, 200);
    });
    
    console.log("Autocomplétion d'adresse initialisée avec succès");
  } catch (error) {
    console.error("Erreur lors de l'initialisation de l'autocomplétion:", error);
  }
}

/**
 * Gère la sélection d'une adresse dans l'autocomplétion
 */
function handlePlaceSelection() {
  const place = addressAutocomplete.getPlace();
  const addressInput = document.getElementById('address');
  
  // Vérification que nous avons bien reçu un lieu valide
  if (!place || !place.geometry) {
    console.warn("Adresse invalide ou incomplète sélectionnée");
    addressInput.classList.remove('address-validated');
    return;
  }
  
  console.log("Adresse sélectionnée:", place);
  
  // Mise à jour des champs cachés avec les coordonnées
  updateCoordinateFields(place);
  
  // Ajout d'une indication visuelle de succès
  addressInput.classList.add('address-validated');
  
  // Affichage d'une notification si disponible
  if (window.showNotification) {
    window.showNotification('Adresse validée avec succès', 'success');
  }
}

/**
 * Met à jour les champs cachés avec les coordonnées de l'adresse
 */
function updateCoordinateFields(place) {
  const latInput = document.getElementById('address-lat');
  const lngInput = document.getElementById('address-lng');
  const placeIdInput = document.getElementById('address-place-id');
  
  if (latInput && place.geometry && place.geometry.location) {
    latInput.value = place.geometry.location.lat();
  }
  
  if (lngInput && place.geometry && place.geometry.location) {
    lngInput.value = place.geometry.location.lng();
  }
  
  if (placeIdInput && place.place_id) {
    placeIdInput.value = place.place_id;
  }
}

/**
 * Validation supplémentaire lors de la perte de focus
 */
function validateAddressOnBlur() {
  const addressInput = document.getElementById('address');
  const latInput = document.getElementById('address-lat');
  
  // Si l'adresse n'est pas vide mais que nous n'avons pas de coordonnées,
  // cela signifie probablement que l'utilisateur a saisi manuellement l'adresse
  if (addressInput.value.trim() !== '' && (!latInput || !latInput.value)) {
    // Tentative de géocodage manuel de l'adresse saisie
    if (typeof google !== 'undefined' && google.maps && google.maps.Geocoder) {
      const geocoder = new google.maps.Geocoder();
      
      geocoder.geocode({ address: addressInput.value, region: 'fr' }, function(results, status) {
        if (status === google.maps.GeocoderStatus.OK && results[0]) {
          const place = results[0];
          updateCoordinateFields(place);
          addressInput.value = place.formatted_address;
          addressInput.classList.add('address-validated');
          
          if (window.showNotification) {
            window.showNotification('Adresse validée avec succès', 'success');
          }
        } else {
          addressInput.classList.remove('address-validated');
        }
      });
    }
  }
}

// Initialisation au chargement du document
document.addEventListener('DOMContentLoaded', function() {
  console.log("Document chargé, vérification de l'API Google Maps");
  
  // Si Google Maps est déjà chargé, initialiser immédiatement
  if (window.google && window.google.maps && window.google.maps.places) {
    console.log("Google Maps déjà disponible, initialisation immédiate");
    initializeAddressAutocomplete();
  } else {
    console.log("Google Maps pas encore disponible, prêt pour le callback");
    // L'initialisation se fera via le callback défini au début
  }
});
