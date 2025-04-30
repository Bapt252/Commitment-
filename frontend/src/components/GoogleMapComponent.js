import React, { useEffect, useState, useCallback } from 'react';
import { GoogleMap, useJsApiLoader, Marker, InfoWindow } from '@react-google-maps/api';

const containerStyle = {
  width: '100%',
  height: '400px'
};

const defaultCenter = {
  lat: 48.856614,  // Paris coordinates (default)
  lng: 2.3522219
};

/**
 * Component for displaying a Google Map with markers
 * 
 * @param {Object} props - Component props
 * @param {Array} props.markers - Array of marker objects with lat, lng, and title
 * @param {Object} props.center - Center coordinates (lat, lng)
 * @param {number} props.zoom - Initial zoom level
 * @param {Object} props.mapOptions - Additional map options
 */
function GoogleMapComponent({ 
  markers = [], 
  center = defaultCenter, 
  zoom = 13,
  mapOptions = {} 
}) {
  const [map, setMap] = useState(null);
  const [selectedMarker, setSelectedMarker] = useState(null);
  const [mapCenter, setMapCenter] = useState(center);
  
  const { isLoaded, loadError } = useJsApiLoader({
    id: 'google-map-script',
    googleMapsApiKey: process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || ''
  });

  // Update map center when center prop changes
  useEffect(() => {
    if (center && center.lat && center.lng) {
      setMapCenter(center);
    }
  }, [center]);

  const onLoad = useCallback(function callback(map) {
    setMap(map);
  }, []);

  const onUnmount = useCallback(function callback(map) {
    setMap(null);
  }, []);

  const handleMarkerClick = (marker) => {
    setSelectedMarker(marker);
  };

  const handleInfoWindowClose = () => {
    setSelectedMarker(null);
  };

  if (loadError) {
    return <div className="p-4 bg-red-100 text-red-700 rounded">Erreur lors du chargement de Google Maps</div>;
  }

  if (!isLoaded) {
    return <div className="p-4 text-gray-600">Chargement de la carte...</div>;
  }

  return (
    <div className="rounded-lg overflow-hidden shadow-md border border-gray-200">
      <GoogleMap
        mapContainerStyle={containerStyle}
        center={mapCenter}
        zoom={zoom}
        onLoad={onLoad}
        onUnmount={onUnmount}
        options={{
          fullscreenControl: true,
          streetViewControl: false,
          mapTypeControl: true,
          ...mapOptions
        }}
      >
        {markers.map((marker, index) => (
          <Marker
            key={index}
            position={{ lat: marker.lat, lng: marker.lng }}
            onClick={() => handleMarkerClick(marker)}
            title={marker.title || ''}
            animation={window.google?.maps?.Animation?.DROP}
          />
        ))}

        {selectedMarker && (
          <InfoWindow
            position={{ lat: selectedMarker.lat, lng: selectedMarker.lng }}
            onCloseClick={handleInfoWindowClose}
          >
            <div className="p-2">
              <h3 className="font-medium">{selectedMarker.title}</h3>
              {selectedMarker.description && (
                <p className="text-sm mt-1">{selectedMarker.description}</p>
              )}
              {selectedMarker.address && (
                <p className="text-xs text-gray-600 mt-1">{selectedMarker.address}</p>
              )}
            </div>
          </InfoWindow>
        )}
      </GoogleMap>
    </div>
  );
}

export default React.memo(GoogleMapComponent);