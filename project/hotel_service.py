import requests
import os
from django.conf import settings

class HotelSearchService:
    def __init__(self):
        # Get API key from settings (same as flights)
        self.api_key = getattr(settings, 'SERPAPI_KEY', None)
        self.base_url = "https://serpapi.com/search.json"
    
    def search_hotels(self, city, check_in_date, check_out_date, adults=2, children=0, page_token=None):
        """
        Search for hotels using SerpAPI Google Hotels or return mock data
        """
        if not self.api_key:
            # Return mock data for development/testing when API key is not set
            return self._get_mock_hotel_data(city, check_in_date, check_out_date)
        
        params = {
            'engine': 'google_hotels',
            'q': f"{city} hotels",
            'check_in_date': check_in_date,
            'check_out_date': check_out_date,
            'adults': adults,
            'children': children,
            'currency': 'USD',
            'gl': 'us',
            'hl': 'en',
            'api_key': self.api_key
        }
        
        # Add pagination token if provided
        if page_token:
            params['next_page_token'] = page_token
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            # If API fails, return mock data as fallback
            print(f"Hotel API Error: {e}, returning mock data")
            return self._get_mock_hotel_data(city, check_in_date, check_out_date)
    
    def _get_mock_hotel_data(self, city, check_in_date, check_out_date):
        """Return mock hotel data for development/testing"""
        return {
            "search_metadata": {"status": "Success (Mock Data)"},
            "properties": [
                {
                    "name": f"Grand Hotel {city}",
                    "rate_per_night": {
                        "lowest": "$150",
                        "extracted_lowest": 150
                    },
                    "total_rate": {
                        "lowest": "$450",
                        "extracted_lowest": 450
                    },
                    "gps_coordinates": {
                        "latitude": 40.7128,
                        "longitude": -74.0060
                    },
                    "hotel_class": "4-star hotel",
                    "extracted_hotel_class": 4,
                    "overall_rating": 4.2,
                    "reviews": 1248,
                    "images": [
                        {
                            "thumbnail": "https://via.placeholder.com/300x200?text=Hotel+Image"
                        }
                    ],
                    "amenities": [
                        "Free Wi-Fi",
                        "Pool",
                        "Fitness center",
                        "Restaurant",
                        "Room service"
                    ],
                    "property_token": "mock_token_1"
                },
                {
                    "name": f"Boutique Inn {city}",
                    "rate_per_night": {
                        "lowest": "$120",
                        "extracted_lowest": 120
                    },
                    "total_rate": {
                        "lowest": "$360",
                        "extracted_lowest": 360
                    },
                    "gps_coordinates": {
                        "latitude": 40.7589,
                        "longitude": -73.9851
                    },
                    "hotel_class": "3-star hotel",
                    "extracted_hotel_class": 3,
                    "overall_rating": 4.5,
                    "reviews": 892,
                    "images": [
                        {
                            "thumbnail": "https://via.placeholder.com/300x200?text=Boutique+Hotel"
                        }
                    ],
                    "amenities": [
                        "Free Wi-Fi",
                        "Continental breakfast",
                        "Pet-friendly",
                        "Business center"
                    ],
                    "property_token": "mock_token_2"
                },
                {
                    "name": f"Luxury Resort {city}",
                    "rate_per_night": {
                        "lowest": "$280",
                        "extracted_lowest": 280
                    },
                    "total_rate": {
                        "lowest": "$840",
                        "extracted_lowest": 840
                    },
                    "gps_coordinates": {
                        "latitude": 40.7831,
                        "longitude": -73.9712
                    },
                    "hotel_class": "5-star hotel",
                    "extracted_hotel_class": 5,
                    "overall_rating": 4.8,
                    "reviews": 2156,
                    "images": [
                        {
                            "thumbnail": "https://via.placeholder.com/300x200?text=Luxury+Resort"
                        }
                    ],
                    "amenities": [
                        "Spa",
                        "Pool",
                        "Fine dining",
                        "Concierge",
                        "Valet parking",
                        "Fitness center"
                    ],
                    "property_token": "mock_token_3"
                },
                {
                    "name": f"Budget Lodge {city}",
                    "rate_per_night": {
                        "lowest": "$75",
                        "extracted_lowest": 75
                    },
                    "total_rate": {
                        "lowest": "$225",
                        "extracted_lowest": 225
                    },
                    "gps_coordinates": {
                        "latitude": 40.7505,
                        "longitude": -73.9934
                    },
                    "hotel_class": "2-star hotel",
                    "extracted_hotel_class": 2,
                    "overall_rating": 3.8,
                    "reviews": 445,
                    "images": [
                        {
                            "thumbnail": "https://via.placeholder.com/300x200?text=Budget+Lodge"
                        }
                    ],
                    "amenities": [
                        "Free Wi-Fi",
                        "24-hour front desk",
                        "Laundry service"
                    ],
                    "property_token": "mock_token_4"
                }
            ],
            "serpapi_pagination": {
                "current_from": 1,
                "current_to": 4,
                "next_page_token": None
            }
        }
    
    def format_hotel_results(self, api_response):
        """Format the API response for easier use in templates"""
        formatted_hotels = []
        
        properties = api_response.get('properties', [])
        
        for hotel in properties:
            # Handle missing data gracefully
            rate_per_night = hotel.get('rate_per_night', {})
            total_rate = hotel.get('total_rate', {})
            images = hotel.get('images', [])
            
            formatted_hotel = {
                'name': hotel.get('name', 'Unknown Hotel'),
                'price_per_night': rate_per_night.get('lowest', 'N/A'),
                'price_per_night_value': rate_per_night.get('extracted_lowest', 0),
                'total_price': total_rate.get('lowest', 'N/A'),
                'total_price_value': total_rate.get('extracted_lowest', 0),
                'rating': hotel.get('overall_rating', 0),
                'reviews': hotel.get('reviews', 0),
                'hotel_class': hotel.get('hotel_class', ''),
                'star_rating': hotel.get('extracted_hotel_class', 0),
                'amenities': hotel.get('amenities', []),
                'image_url': images[0].get('thumbnail', '') if images else '',
                'property_token': hotel.get('property_token', ''),
                'coordinates': hotel.get('gps_coordinates', {}),
                'raw_data': hotel  # Keep original data for debugging
            }
            formatted_hotels.append(formatted_hotel)
        
        return formatted_hotels
    
    def _format_star_rating(self, rating):
        """Convert numeric rating to star display"""
        if not rating:
            return ""
        
        full_stars = "★" * int(rating)
        half_star = "☆" if rating % 1 >= 0.5 else ""
        empty_stars = "☆" * (5 - int(rating) - (1 if half_star else 0))
        
        return full_stars + half_star + empty_stars
    
    def _calculate_nights(self, check_in_date, check_out_date):
        """Calculate number of nights between dates"""
        try:
            from datetime import datetime
            check_in = datetime.strptime(check_in_date, '%Y-%m-%d')
            check_out = datetime.strptime(check_out_date, '%Y-%m-%d')
            return (check_out - check_in).days
        except:
            return 1