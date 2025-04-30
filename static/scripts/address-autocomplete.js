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
  
  console.log('Autocomplétion Google Maps initialisée avec succès!');
}

// Créer une fonction d'initialisation globale pour que l'API Google Maps puisse l'appeler
window.initGoogleMapsAutocomplete = function() {
  console.log('Callback Google Maps appelé');
  initAddressAutocomplete();
};

// Chargement du script Google Maps
function loadGoogleMapsScript() {
  // Vérifier si le script est déjà chargé
  if (window.google && window.google.maps && window.google.maps.places) {
    console.log('API Google Maps déjà chargée, initialisation directe');
    initAddressAutocomplete();
    return;
  }
  
  // Si le script existe déjà mais n'est pas encore chargé, on ne fait rien
  if (document.querySelector('script[src*="maps.googleapis.com"]')) {
    console.log('Script Google Maps déjà en cours de chargement, attente...');
    return;
  }
  
  // Clé API Google Maps
  const apiKey = "AIzaSyBP7x3CwXNA-LM7DWvAMmvg4piOtgY6a-o";
  
  // Charger le script avec la clé API 
  const script = document.createElement('script');
  script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places&callback=initGoogleMapsAutocomplete`;
  script.async = true;
  script.defer = true;
  
  script.onerror = function() {
    console.error("Impossible de charger le script Google Maps. Vérifiez votre clé API et votre connexion.");
  };
  
  document.head.appendChild(script);
  console.log('Script Google Maps en cours de chargement...');
}

// Charger le script au chargement de la page
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', loadGoogleMapsScript);
} else {
  loadGoogleMapsScript();
}

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
