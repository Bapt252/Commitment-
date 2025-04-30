/**
 * Script d'intégration Google Maps pour le champ d'adresse du questionnaire candidat
 * 
 * Ce script permet de:
 * 1. Ajouter l'autocomplétion d'adresse via l'API Google Maps Places
 * 2. Valider et formater l'adresse saisie
 * 3. Stocker les coordonnées géographiques pour les calculs de distance
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
    componentRestrictions: { country: 'fr' }, // Limiter à la France (peut être modifié)
    fields: ['address_components', 'formatted_address', 'geometry', 'place_id']
  });
  
  // Ajout d'un conteneur pour les coordonnées (champs cachés)
  const coordsContainer = document.createElement('div');
  coordsContainer.id = 'address-coords-container';
  coordsContainer.style.display = 'none';
  
  // Création des champs cachés pour stocker les coordonnées
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
  
  // Insérer les champs cachés après le textarea d'adresse
  addressInput.parentNode.insertBefore(coordsContainer, addressInput.nextSibling);
  
  // Écouter les événements de l'autocomplétion
  autocomplete.addListener('place_changed', function() {
    const place = autocomplete.getPlace();
    
    if (!place.geometry) {
      // L'utilisateur a appuyé sur Entrée sans sélectionner une suggestion
      // On peut valider manuellement l'adresse via l'API backend
      validateAddressManually(addressInput.value);
      return;
    }
    
    // Mise à jour des champs cachés avec les coordonnées
    latInput.value = place.geometry.location.lat();
    lngInput.value = place.geometry.location.lng();
    placeIdInput.value = place.place_id;
    
    // Mise à jour du champ d'adresse avec l'adresse formatée
    addressInput.value = place.formatted_address;
    
    // Ajouter une classe indiquant que l'adresse est validée
    addressInput.classList.add('address-validated');
    
    // Déclencher une notification
    if (window.showNotification) {
      window.showNotification('Adresse validée avec succès', 'success');
    }
  });
  
  // Ajouter un événement sur le changement manuel de l'adresse
  addressInput.addEventListener('blur', function() {
    if (!addressInput.classList.contains('address-validated') && addressInput.value.trim() !== '') {
      validateAddressManually(addressInput.value);
    }
  });
}

// Fonction pour valider manuellement une adresse via l'API backend
function validateAddressManually(address) {
  if (!address || address.trim() === '') return;
  
  // Récupération des champs cachés
  const latInput = document.getElementById('address-lat');
  const lngInput = document.getElementById('address-lng');
  const placeIdInput = document.getElementById('address-place-id');
  const addressInput = document.getElementById('address');
  
  // Appel à l'API backend pour la géolocalisation
  fetch('/api/geo/geocode', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      address: address
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error('Erreur lors de la validation de l\'adresse');
    }
    return response.json();
  })
  .then(data => {
    // Mise à jour des champs avec les données reçues
    latInput.value = data.lat;
    lngInput.value = data.lng;
    placeIdInput.value = data.place_id;
    
    // Mise à jour du champ d'adresse avec l'adresse formatée
    addressInput.value = data.formatted_address;
    
    // Ajouter une classe indiquant que l'adresse est validée
    addressInput.classList.add('address-validated');
    
    // Déclencher une notification
    if (window.showNotification) {
      window.showNotification('Adresse validée avec succès', 'success');
    }
  })
  .catch(error => {
    console.error('Erreur de validation d\'adresse:', error);
    
    // Notification d'erreur
    if (window.showNotification) {
      window.showNotification('Impossible de valider cette adresse. Veuillez vérifier et réessayer.', 'error');
    }
    
    // Retirer la classe de validation
    addressInput.classList.remove('address-validated');
  });
}

// Fonction pour s'assurer que l'adresse est validée avant la soumission du formulaire
function setupFormValidation() {
  const form = document.getElementById('questionnaire-form');
  const submitBtn = document.getElementById('submit-btn');
  
  if (!form || !submitBtn) return;
  
  // Remplacer l'événement de clic existant par notre validation
  const originalClickHandler = submitBtn.onclick;
  
  submitBtn.onclick = function(event) {
    // Vérifier si l'adresse a été validée
    const addressInput = document.getElementById('address');
    const latInput = document.getElementById('address-lat');
    const lngInput = document.getElementById('address-lng');
    
    if (addressInput && addressInput.value.trim() !== '' && 
        (!latInput.value || !lngInput.value || !addressInput.classList.contains('address-validated'))) {
      // Empêcher la soumission
      event.preventDefault();
      
      // Valider l'adresse
      validateAddressManually(addressInput.value);
      
      // Afficher une notification
      if (window.showNotification) {
        window.showNotification('Veuillez attendre la validation de l\'adresse avant de soumettre le formulaire', 'error');
      }
      
      // Focus sur le champ d'adresse
      addressInput.scrollIntoView({ behavior: 'smooth' });
      setTimeout(() => addressInput.focus(), 500);
      
      return false;
    }
    
    // Appeler le gestionnaire d'événements original
    if (typeof originalClickHandler === 'function') {
      return originalClickHandler.call(this, event);
    }
  };
}

// Ajouter le chargement du script Google Maps
function loadGoogleMapsScript() {
  // Vérifier si le script est déjà chargé
  if (window.google && window.google.maps) {
    initAddressAutocomplete();
    setupFormValidation();
    return;
  }
  
  // Récupérer la clé API depuis le backend
  fetch('/api/geo/api-key')
    .then(response => response.json())
    .then(data => {
      // Créer et charger le script
      const script = document.createElement('script');
      script.src = `https://maps.googleapis.com/maps/api/js?key=${data.apiKey}&libraries=places`;
      script.async = true;
      script.defer = true;
      
      script.onload = function() {
        initAddressAutocomplete();
        setupFormValidation();
      };
      
      document.head.appendChild(script);
    })
    .catch(error => {
      console.error('Erreur lors de la récupération de la clé API:', error);
      
      // Charger avec une clé par défaut pour le développement (ne fonctionnera pas en production)
      const script = document.createElement('script');
      script.src = 'https://maps.googleapis.com/maps/api/js?libraries=places';
      script.async = true;
      script.defer = true;
      
      script.onload = function() {
        initAddressAutocomplete();
        setupFormValidation();
      };
      
      document.head.appendChild(script);
    });
}

// Charger le script Google Maps une fois que le DOM est prêt
document.addEventListener('DOMContentLoaded', loadGoogleMapsScript);

// Ajouter des styles pour le champ d'adresse validé
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
