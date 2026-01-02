"""
Service Area Validation Utility - Geographic API Integration (Option C)

MULTI-OFFICE SERVICE AREA:
Service area covers 100 miles from EACH of the following:
- All 50 US state capitals
- All major cities in Canada

This means an address in San Jose, CA is IN-AREA because it's within 100 miles
of Sacramento (CA state capital), even though it's 2546 miles from NYC.

APPROACH:
1. Geocode user's address using Nominatim API
2. Calculate distance to ALL office locations using Haversine formula
3. Return IN-AREA if within 100 miles of ANY office location
4. If geocoding fails, give benefit of doubt (assume IN-AREA)
"""

import os
import math
import json
import urllib.request
import urllib.parse
import time
from typing import Tuple, Optional, List

SERVICE_RADIUS_MILES = 100

# Nominatim API endpoint (free, no API key required)
GEOCODING_API = "https://nominatim.openstreetmap.org/search"

# Cache for geocoding results to avoid repeated API calls
_geocoding_cache = {}

# MULTI-OFFICE LOCATIONS: 100-mile radius from EACH of these locations
# Format: (name, latitude, longitude)
OFFICE_LOCATIONS = [
    # US State Capitals (all 50 states)
    ("Montgomery, AL", 32.3792, -86.3077),
    ("Juneau, AK", 58.3019, -134.4197),
    ("Phoenix, AZ", 33.4484, -112.0740),
    ("Little Rock, AR", 34.7465, -92.2896),
    ("Sacramento, CA", 38.5816, -121.4944),
    ("Denver, CO", 39.7392, -104.9903),
    ("Hartford, CT", 41.7658, -72.6734),
    ("Dover, DE", 39.1582, -75.5244),
    ("Tallahassee, FL", 30.4383, -84.2807),
    ("Atlanta, GA", 33.7490, -84.3880),
    ("Honolulu, HI", 21.3099, -157.8581),
    ("Boise, ID", 43.6150, -116.2023),
    ("Springfield, IL", 39.7817, -89.6501),
    ("Indianapolis, IN", 39.7684, -86.1581),
    ("Des Moines, IA", 41.5868, -93.6250),
    ("Topeka, KS", 39.0473, -95.6752),
    ("Frankfort, KY", 38.2009, -84.8733),
    ("Baton Rouge, LA", 30.4515, -91.1871),
    ("Augusta, ME", 44.3106, -69.7795),
    ("Annapolis, MD", 38.9784, -76.4922),
    ("Boston, MA", 42.3601, -71.0589),
    ("Lansing, MI", 42.7325, -84.5555),
    ("Saint Paul, MN", 44.9537, -93.0900),
    ("Jackson, MS", 32.2988, -90.1848),
    ("Jefferson City, MO", 38.5767, -92.1735),
    ("Helena, MT", 46.5891, -112.0391),
    ("Lincoln, NE", 40.8136, -96.7026),
    ("Carson City, NV", 39.1638, -119.7674),
    ("Concord, NH", 43.2081, -71.5376),
    ("Trenton, NJ", 40.2206, -74.7597),
    ("Santa Fe, NM", 35.6870, -105.9378),
    ("Albany, NY", 42.6526, -73.7562),
    ("Raleigh, NC", 35.7796, -78.6382),
    ("Bismarck, ND", 46.8083, -100.7837),
    ("Columbus, OH", 39.9612, -82.9988),
    ("Oklahoma City, OK", 35.4676, -97.5164),
    ("Salem, OR", 44.9429, -123.0351),
    ("Harrisburg, PA", 40.2732, -76.8867),
    ("Providence, RI", 41.8240, -71.4128),
    ("Columbia, SC", 34.0007, -81.0348),
    ("Pierre, SD", 44.3683, -100.3510),
    ("Nashville, TN", 36.1627, -86.7816),
    ("Austin, TX", 30.2672, -97.7431),
    ("Salt Lake City, UT", 40.7608, -111.8910),
    ("Montpelier, VT", 44.2601, -72.5754),
    ("Richmond, VA", 37.5407, -77.4360),
    ("Olympia, WA", 47.0379, -122.9007),
    ("Charleston, WV", 38.3498, -81.6326),
    ("Madison, WI", 43.0731, -89.4012),
    ("Cheyenne, WY", 41.1400, -104.8202),
    
    # Major Canadian Cities
    ("Toronto, ON", 43.6532, -79.3832),
    ("Montreal, QC", 45.5017, -73.5673),
    ("Vancouver, BC", 49.2827, -123.1207),
    ("Calgary, AB", 51.0447, -114.0719),
    ("Edmonton, AB", 53.5461, -113.4938),
    ("Ottawa, ON", 45.4215, -75.6972),
    ("Winnipeg, MB", 49.8951, -97.1384),
    ("Quebec City, QC", 46.8139, -71.2080),
    ("Hamilton, ON", 43.2557, -79.8711),
    ("Kitchener, ON", 43.4516, -80.4925),
    ("London, ON", 42.9849, -81.2453),
    ("Victoria, BC", 48.4284, -123.3656),
    ("Halifax, NS", 44.6488, -63.5752),
    ("Windsor, ON", 42.3149, -83.0364),
    ("Saskatoon, SK", 52.1332, -106.6700),
    ("Regina, SK", 50.4452, -104.6189),
]


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
    
    MULTI-OFFICE LOGIC:
    Returns True if address is within 100 miles of ANY of:
    - All 50 US state capitals
    - All major Canadian cities
    
    Strategy:
    1. Geocode the address to lat/lon
    2. Calculate distance to ALL office locations using Haversine formula
    3. Return True if distance <= 100 miles from ANY location
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
    
    user_lat, user_lon = coords
    
    # Check distance to ALL office locations
    closest_office = None
    closest_distance = float('inf')
    
    for office_name, office_lat, office_lon in OFFICE_LOCATIONS:
        distance = haversine_distance(user_lat, user_lon, office_lat, office_lon)
        
        if distance < closest_distance:
            closest_distance = distance
            closest_office = office_name
    
    in_area = closest_distance <= SERVICE_RADIUS_MILES
    
    print(f"[Service Area] '{address}' → {user_lat:.4f}, {user_lon:.4f} → {closest_distance:.1f} miles from {closest_office} → {'IN' if in_area else 'OUT'}")
    
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
    print(f"Service Radius: {SERVICE_RADIUS_MILES} miles from ANY of {len(OFFICE_LOCATIONS)} office locations")
    print("=" * 80)
    
    test_addresses = [
        "143 schott st san jose ca",        # Should be IN-AREA (near Sacramento, CA capital)
        "10880 Malibu Point, California",   # Should be IN-AREA (near Sacramento)
        "123 Main St, Boston, MA",          # Should be IN-AREA (Boston is MA capital)
        "20 Broadway, New York, NY",        # Should be IN-AREA (near Albany, NY capital)
        "Rural Alaska, 1000 miles from Juneau",  # Should be OUT-OF-AREA
    ]
    
    for address in test_addresses:
        result = is_in_service_area(address)
        status = "✓ IN-AREA" if result else "✗ OUT-OF-AREA"
        print(f"{status:15} | {address}")
        print("-" * 80)
