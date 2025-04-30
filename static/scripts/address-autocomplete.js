/**
 * Script d'intégration Google Maps pour le champ d'adresse du questionnaire candidat
 */

// Fonction principale d'initialisation
function initAddressAutocomplete() {
  // Sélection du champ d'adresse
  const addressInput = document.getElementById('address');
  
  if (!addressInput) {
    console.error("Champ d'adresse non trouvé dans le formulaire");
    return;
  }
  
  // Création de l'autocomplétion
  const autocomplete = new google.maps.places.Autocomplete(addressInput, {
    types: ['address'],
    componentRestrictions: { country: 'fr' },
    fields: ['address_components', 'formatted_address', 'geometry', 'place_id']
  });
  
  // Ajout d'un conteneur pour les coordonnées
  const coordsContainer = document.createElement('div');
  coordsContainer.id = 'address-coords-container';
  coordsContainer.style.display = 'none';
  
  // Création des champs cachés
  const latInput = document.createElement('input');
  latInput.type = 'hidden';
  latInput.id = 'address-lat';
  latInput.name = 'address-lat';
  
  const lngInput = document.createElement('input');
  lngInput.type = 'hidden';
  lngInput.id = 'address-lng';
  lngInput.name = 'address-lng';
  
  const placeIdInput = document.createElement('input');
  placeIdInput.type = 'hidden';
  placeIdInput.id = 'address-place-id';
  placeIdInput.name = 'address-place-id';
  
  coordsContainer.appendChild(latInput);
  coordsContainer.appendChild(lngInput);
  coordsContainer.appendChild(placeIdInput);
  
  // Insérer les champs cachés
  addressInput.parentNode.insertBefore(coordsContainer, addressInput.nextSibling);
  
  // Écouter les événements de l'autocomplétion
  autocomplete.addListener('place_changed', function() {
    const place = autocomplete.getPlace();
    
    if (!place.geometry) {
      return;
    }
    
    // Mise à jour des champs cachés
    latInput.value = place.geometry.location.lat();
    lngInput.value = place.geometry.location.lng();
    placeIdInput.value = place.place_id;
    
    // Mise à jour du champ d'adresse
    addressInput.value = place.formatted_address;
    addressInput.classList.add('address-validated');
    
    if (window.showNotification) {
      window.showNotification('Adresse validée avec succès', 'success');
    }
  });
}

// Chargement du script Google Maps
function loadGoogleMapsScript() {
  // Vérifier si le script est déjà chargé
  if (window.google && window.google.maps) {
    initAddressAutocomplete();
    return;
  }
  
  // Clé API Google Maps - Remplacez par votre clé API
  const apiKey = "AIzaSyBP7x3CwXNA-LM7DWvAMmvg4piOtgY6a-o";
  
  // Charger le script avec la clé API 
  const script = document.createElement('script');
  script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places`;
  script.async = true;
  script.defer = true;
  
  script.onload = function() {
    initAddressAutocomplete();
  };
  
  script.onerror = function() {
    console.error("Impossible de charger le script Google Maps. Vérifiez votre clé API et votre connexion.");
  };
  
  document.head.appendChild(script);
}

// Charger le script au chargement de la page
document.addEventListener('DOMContentLoaded', loadGoogleMapsScript);

// Ajouter des styles pour l'adresse validée
const style = document.createElement('style');
style.textContent = `
  .address-validated {
    border-color: #10B981 !important;
    background-color: rgba(16, 185, 129, 0.05) !important;
  }
  
  .pac-container {
    z-index: 10000;
    border-radius: 8px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
    font-family: 'Inter', sans-serif;
    border: none;
    margin-top: 5px;
  }
  
  .pac-item {
    padding: 10px;
    cursor: pointer;
  }
  
  .pac-item:hover {
    background-color: rgba(124, 58, 237, 0.05);
  }
  
  .pac-item-selected {
    background-color: rgba(124, 58, 237, 0.1);
  }
`;
document.head.appendChild(style);
