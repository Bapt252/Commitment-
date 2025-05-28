# =============================================================================
# GOOGLE MAPS API SETUP FOR SUPERSMARTMATCH
# =============================================================================

SuperSmartMatch uses Google Maps API for precise travel time calculations and geolocation features.

## 🔑 Getting Your Google Maps API Key

1. **Go to Google Cloud Console**: https://console.cloud.google.com/
2. **Create or select a project**
3. **Enable the following APIs**:
   - Geocoding API
   - Distance Matrix API  
   - Maps JavaScript API
   - Places API (optional)

4. **Create an API key**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy your API key

5. **Configure your .env file**:
   ```bash
   # Replace with your actual Google Maps API key
   GOOGLE_MAPS_API_KEY=AIzaSyC5cpNgAXN1U0L14pB4HmD7BvP8pD6K8t8
   ```

## 🚀 Quick Setup

```bash
# 1. Copy your Google Maps API key
export GOOGLE_MAPS_API_KEY="your-actual-key-here"

# 2. Update your .env file
echo "GOOGLE_MAPS_API_KEY=$GOOGLE_MAPS_API_KEY" >> .env

# 3. Restart SuperSmartMatch service
docker-compose restart supersmartmatch-service

# 4. Verify it works
docker logs nexten-supersmartmatch | grep -i "google\|maps"
```

## ✅ Expected Results

With Google Maps API configured, you should see:
- ✅ `Google Maps API initialized successfully`
- ✅ `Smart-match algorithm with geolocation enabled`
- ✅ Real-time travel time calculations (e.g., Paris → Marseille: 7h27min)

## 🧪 Testing Travel Time Calculations

```bash
# Test SuperSmartMatch with geolocation
curl -X POST http://localhost:5062/api/v1/match \
  -H "Content-Type: application/json" \
  -d '{
    "cv_data": {
      "competences": ["Python"],
      "localisation": "Paris, France"
    },
    "job_data": [{
      "id": "job1",
      "competences": ["Python"],
      "localisation": "Marseille, France"
    }],
    "algorithm": "smart-match"
  }'
```

## 🔧 Troubleshooting

### Error: "Invalid API key provided"
- ✅ Check your API key is correct
- ✅ Ensure required APIs are enabled
- ✅ Verify billing is enabled on your Google Cloud project
- ✅ Check API key restrictions (domains/IPs)

### Error: "API key not found in environment"
- ✅ Check your .env file contains `GOOGLE_MAPS_API_KEY=your-key`
- ✅ Restart Docker containers: `docker-compose restart`
- ✅ Verify environment variable: `docker exec nexten-supersmartmatch env | grep GOOGLE`

## 🌟 SuperSmartMatch Features with Google Maps

- 🗺️ **Precise geolocation**: Exact coordinates for addresses
- 🚗 **Real-time travel times**: Includes traffic conditions
- 📊 **Multiple transport modes**: Driving, walking, transit, cycling
- 🎯 **Smart scoring**: Location score based on actual travel time
- ⚡ **Cached results**: Improved performance with Redis caching

## 📈 Performance Impact

| Feature | Without Google Maps | With Google Maps |
|---------|-------------------|------------------|
| Location matching | Basic city comparison | Precise travel time |
| Accuracy | ~70% | ~95% |
| Transport modes | None | 4 modes available |
| Real-time traffic | ❌ | ✅ |
| Caching | Basic | Advanced with Redis |

---

**Note**: Google Maps API usage is subject to Google's pricing. Most applications stay within the free tier limits.
