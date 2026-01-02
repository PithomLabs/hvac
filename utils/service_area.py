"""
Service Area Validation Utility - Geographic API Integration (Option C)

Uses geocoding API to calculate actual distance from office location.
Service area: 30 miles from office headquarters.

APPROACH:
1. Geocode address using Nominatim (OpenStreetMap) API
2. Calculate distance using Haversine formula
3. Return True if within 30 miles, False otherwise

OFFICE LOCATION:
- Default: New York, NY (40.7128° N, 74.0060° W)
- Configurable via environment variable OFFICE_LAT, OFFICE_LON
"""

import os
import math
import json
import urllib.request
import urllib.parse
import time
from typing import Tuple, Optional

# Office headquarters location (default: New York, NY)
# Override with environment variables: OFFICE_LAT, OFFICE_LON
OFFICE_LAT = float(os.getenv("OFFICE_LAT", "40.7128"))
OFFICE_LON = float(os.getenv("OFFICE_LON", "-74.0060"))
OFFICE_NAME = os.getenv("OFFICE_NAME", "New York, NY")

SERVICE_RADIUS_MILES = 100

# Nominatim API endpoint (free, no API key required)
GEOCODING_API = "https://nominatim.openstreetmap.org/search"

# Cache for geocoding results to avoid repeated API calls
_geocoding_cache = {}


def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great circle distance between two points on Earth.
    
    Args:
        lat1, lon1: Latitude and longitude of point 1 (in degrees)
        lat2, lon2: Latitude and longitude of point 2 (in degrees)
        
    Returns:
        Distance in miles
    """
    # Convert decimal degrees to radians
    lat1_rad = math.radians(lat1)
    lon1_rad = math.radians(lon1)
    lat2_rad = math.radians(lat2)
    lon2_rad = math.radians(lon2)
    
    # Haversine formula
    dlat = lat2_rad - lat1_rad
    dlon = lon2_rad - lon1_rad
    
    a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of Earth in miles
    earth_radius_miles = 3958.8
    
    return c * earth_radius_miles


def geocode_address(address: str) -> Optional[Tuple[float, float]]:
    """
    Geocode an address to latitude/longitude using Nominatim API.
    
    Args:
        address: The address string to geocode
        
    Returns:
        Tuple of (latitude, longitude) or None if geocoding failed
    """
    # Check cache first
    if address in _geocoding_cache:
        return _geocoding_cache[address]
    
    try:
        # Nominatim requires a User-Agent header
        headers = {
            "User-Agent": "HVAC-Booking-Agent/1.0"
        }
        
        params = {
            "q": address,
            "format": "json",
            "limit": "1",
            "countrycodes": "us,ca"  # Restrict to US and Canada
        }
        
        # Build URL with query parameters
        url = f"{GEOCODING_API}?{urllib.parse.urlencode(params)}"
        
        # Create request with headers
        req = urllib.request.Request(url, headers=headers)
        
        # Rate limiting: Nominatim allows 1 request per second
        time.sleep(1.1)
        
        # Make the request
        with urllib.request.urlopen(req, timeout=5) as response:
            data = response.read()
            results = json.loads(data.decode('utf-8'))
        
        if results and len(results) > 0:
            lat = float(results[0]["lat"])
            lon = float(results[0]["lon"])
            
            # Cache the result
            _geocoding_cache[address] = (lat, lon)
            
            return (lat, lon)
        else:
            # No results found
            _geocoding_cache[address] = None
            return None
            
    except Exception as e:
        print(f"Geocoding error for '{address}': {e}")
        # Cache None to avoid repeated failed attempts
        _geocoding_cache[address] = None
        return None


def is_in_service_area(address: str) -> bool:
    """
    Check if an address is within the service area using actual geographic distance.
    
    Strategy:
    1. Geocode the address to lat/lon
    2. Calculate distance from office using Haversine formula
    3. Return True if distance <= 30 miles
    4. If geocoding fails, return True (benefit of doubt)
    
    Args:
        address: The address string to validate
        
    Returns:
        True if IN service area, False if OUT of service area
    """
    if not address:
        return True  # No address = can't validate = assume OK
    
    # Try to geocode the address
    coords = geocode_address(address)
    
    if coords is None:
        # Geocoding failed - give benefit of doubt
        print(f"[Service Area] Could not geocode '{address}', assuming IN-AREA")
        return True
    
    lat, lon = coords
    
    # Calculate distance from office
    distance = haversine_distance(OFFICE_LAT, OFFICE_LON, lat, lon)
    
    in_area = distance <= SERVICE_RADIUS_MILES
    
    print(f"[Service Area] '{address}' → {lat:.4f}, {lon:.4f} → {distance:.1f} miles from {OFFICE_NAME} → {'IN' if in_area else 'OUT'}")
    
    return in_area


def get_service_area_message() -> str:
    """Get the standard out-of-area rejection message."""
    return (
        f"Unfortunately, we are unable to accommodate that request as we do not serve "
        f"beyond a {SERVICE_RADIUS_MILES}-mile radius from our office. I recommend finding a local provider "
        f"who can assist you. No problem at all. Have a great day!"
    )


if __name__ == "__main__":
    # Test cases
    print(f"Office Location: {OFFICE_NAME} ({OFFICE_LAT}, {OFFICE_LON})")
    print(f"Service Radius: {SERVICE_RADIUS_MILES} miles")
    print("=" * 80)
    
    test_addresses = [
        "134 workshire st new york",     # Should be IN-AREA (close to NYC)
        "10880 Malibu Point, California",           # Should be OUT-OF-AREA (California, ~2800 miles)
        "123 Main St, Boston, MA",      # Should be OUT-OF-AREA (~215 miles from NYC)
        "20 Broadway, New York, NY",     # Should be IN-AREA (Manhattan)
    ]
    
    for address in test_addresses:
        result = is_in_service_area(address)
        status = "✓ IN-AREA" if result else "✗ OUT-OF-AREA"
        print(f"{status:15} | {address}")
        print("-" * 80)
