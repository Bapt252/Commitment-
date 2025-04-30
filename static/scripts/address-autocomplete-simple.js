// Script d'autocomplétion d'adresse simplifié
document.addEventListener('DOMContentLoaded', function() {
  console.log('Initialisation du script d\'autocomplétion simplifié');
  
  // Fonction pour initialiser l'autocomplétion
  function initAutocomplete() {
    const addressInput = document.getElementById('address');
    
    if (!addressInput) {
      console.error("Champ d'adresse non trouvé");
      return;
    }
    
    console.log("Champ d'adresse trouvé:", addressInput);
    
    try {
      // Vérifier si l'API Google est disponible
      if (typeof google === 'undefined' || !google.maps || !google.maps.places) {
        console.error("API Google Maps non disponible");
        return;
      }
      
      console.log("API Google Maps disponible, création de l'autocomplétion");
      
      // Création de l'autocomplétion
      const autocomplete = new google.maps.places.Autocomplete(addressInput, {
        types: ['address'],
        componentRestrictions: { country: 'fr' }
      });
      
      console.log("Autocomplétion créée avec succès");
      
      // Écouter les changements de lieu
      autocomplete.addListener('place_changed', function() {
        const place = autocomplete.getPlace();
        console.log("Place sélectionnée:", place);
        
        if (!place.geometry) {
          console.error("Aucune information géométrique pour cette adresse");
          return;
        }
        
        // Si des champs cachés existent, mettre à jour leurs valeurs
        const latInput = document.getElementById('address-lat');
        const lngInput = document.getElementById('address-lng');
        const placeIdInput = document.getElementById('address-place-id');
        
        if (latInput) latInput.value = place.geometry.location.lat();
        if (lngInput) lngInput.value = place.geometry.location.lng();
        if (placeIdInput) placeIdInput.value = place.place_id;
        
        // Ajouter une classe visuelle pour indiquer que l'adresse est validée
        addressInput.classList.add('address-validated');
        
        // Afficher une notification si la fonction existe
        if (window.showNotification) {
          window.showNotification('Adresse validée avec succès', 'success');
        }
      });
      
    } catch (error) {
      console.error("Erreur lors de l'initialisation de l'autocomplétion:", error);
    }
  }
  
  // Si Google Maps API est déjà chargé, initialiser directement
  if (window.google && window.google.maps && window.google.maps.places) {
    console.log("Google Maps déjà chargé, initialisation immédiate");
    initAutocomplete();
  } else {
    console.log("Google Maps pas encore chargé, attente de l'événement load");
    
    // Sinon, attendre que la page soit complètement chargée
    window.addEventListener('load', function() {
      console.log("Page chargée, vérification de Google Maps");
      
      // Vérifier encore une fois si Google Maps est chargé
      if (window.google && window.google.maps && window.google.maps.places) {
        console.log("Google Maps disponible après chargement de la page");
        initAutocomplete();
      } else {
        console.log("Google Maps non disponible après chargement - tentative de chargement manuel");
        
        // Si Google Maps n'est toujours pas disponible, essayer de le charger manuellement
        const script = document.createElement('script');
        script.src = "https://maps.googleapis.com/maps/api/js?key=AIzaSyAQg9x3QE5F5xVhCh_-0a4YpLEe4_wnvO0&libraries=places&callback=initAutocompleteCallback";
        script.async = true;
        script.defer = true;
        document.head.appendChild(script);
        
        // Définir une fonction de callback globale
        window.initAutocompleteCallback = function() {
          console.log("Google Maps chargé manuellement, initialisation");
          initAutocomplete();
        };
      }
    });
  }
});

// Définir une fonction de callback globale pour être sûr
window.initAutocompleteCallback = function() {
  console.log("Callback d'autocomplétion appelé");
  const addressInput = document.getElementById('address');
  
  if (!addressInput) {
    console.error("Champ d'adresse non trouvé dans le callback");
    return;
  }
  
  try {
    if (typeof google !== 'undefined' && google.maps && google.maps.places) {
      const autocomplete = new google.maps.places.Autocomplete(addressInput, {
        types: ['address'],
        componentRestrictions: { country: 'fr' }
      });
      
      console.log("Autocomplétion initialisée dans le callback");
      
      autocomplete.addListener('place_changed', function() {
        const place = autocomplete.getPlace();
        console.log("Place sélectionnée dans le callback:", place);
        
        if (!place.geometry) return;
        
        // Mise à jour des champs cachés
        const latInput = document.getElementById('address-lat');
        const lngInput = document.getElementById('address-lng');
        const placeIdInput = document.getElementById('address-place-id');
        
        if (latInput) latInput.value = place.geometry.location.lat();
        if (lngInput) lngInput.value = place.geometry.location.lng();
        if (placeIdInput) placeIdInput.value = place.place_id;
        
        // Ajouter une classe visuelle
        addressInput.classList.add('address-validated');
        
        // Notification
        if (window.showNotification) {
          window.showNotification('Adresse validée avec succès', 'success');
        }
      });
    } else {
      console.error("API Google Maps non disponible dans le callback");
    }
  } catch (error) {
    console.error("Erreur dans le callback d'initialisation:", error);
  }
};
