# Make sure you have created project/flight_service.py

import requests
import os
from django.conf import settings

# A class that handles flight search functionality with the SerpAPI Google Flights API or providing mock data when no API key is available. 
# Manages flight search requests with parameters like departure/arrival cities, dates, and travel class, then formats the API response into a standardized structure
# methods for converting city names to airport codes, formatting flight durations, and handling multi-leg flights.

class FlightSearchService:
    def __init__(self):
        self.api_key = getattr(settings, 'SERPAPI_KEY', None)
        self.base_url = "https://serpapi.com/search.json"
    
    def search_flights(self, departure_city, arrival_city, departure_date, 
                      return_date=None, travel_class='1', adults=1, page_token=None):
        """
        Search for flights using SerpAPI Google Flights or return mock data
        """
        if not self.api_key:
            return self._get_mock_flight_data(departure_city, arrival_city, departure_date)
        
        departure_id = self._get_airport_code(departure_city)
        arrival_id = self._get_airport_code(arrival_city)
        
        params = {
            'engine': 'google_flights',
            'departure_id': departure_id,
            'arrival_id': arrival_id,
            'outbound_date': departure_date,
            'travel_class': travel_class,
            'adults': adults,
            'currency': 'USD',
            'hl': 'en',
            'gl': 'us',
            'api_key': self.api_key
        }
        
        if return_date:
            params['return_date'] = return_date
            params['type'] = '1'
        else:
            params['type'] = '2'
        
        if page_token:
            params['next_page_token'] = page_token
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"API Error: {e}, returning mock data")
            return self._get_mock_flight_data(departure_city, arrival_city, departure_date)
    
    def _get_airport_code(self, city_input):
        """Convert city name to airport code or return if already a code"""
        city_input = city_input.strip().upper()
        
        if len(city_input) == 3 and city_input.isalpha():
            return city_input
        
        city_mappings = {
            'NEW YORK': 'NYC', 'BOSTON': 'BOS', 'ROME': 'FCO',
            'LOS ANGELES': 'LAX', 'CHICAGO': 'CHI', 'MIAMI': 'MIA',
            'SAN FRANCISCO': 'SFO', 'WASHINGTON': 'DCA', 'SEATTLE': 'SEA',
            'DENVER': 'DEN', 'ATLANTA': 'ATL', 'LONDON': 'LHR',
            'PARIS': 'CDG', 'TOKYO': 'NRT', 'BERLIN': 'BER'
        }
        
        return city_mappings.get(city_input, city_input)
    
    def _get_mock_flight_data(self, departure_city, arrival_city, departure_date):
        """Return mock flight data for development/testing"""
        dep_code = self._get_airport_code(departure_city)
        arr_code = self._get_airport_code(arrival_city)
        
        return {
            "search_metadata": {"status": "Success (Mock Data)"},
            "best_flights": [
                {
                    "flights": [{
                        "departure_airport": {
                            "name": f"{departure_city} Airport",
                            "id": dep_code,
                            "time": f"{departure_date} 08:30"
                        },
                        "arrival_airport": {
                            "name": f"{arrival_city} Airport", 
                            "id": arr_code,
                            "time": f"{departure_date} 11:45"
                        }
                    }],
                    "layovers": [],
                    "total_duration": 195,
                    "price": 299,
                    "airline_logo": "https://www.gstatic.com/flights/airline_logos/70px/AA.png"
                },
                {
                    "flights": [{
                        "departure_airport": {
                            "name": f"{departure_city} Airport",
                            "id": dep_code,
                            "time": f"{departure_date} 14:15"
                        },
                        "arrival_airport": {
                            "name": f"{arrival_city} Airport",
                            "id": arr_code, 
                            "time": f"{departure_date} 17:30"
                        }
                    }],
                    "layovers": [],
                    "total_duration": 195,
                    "price": 349,
                    "airline_logo": "https://www.gstatic.com/flights/airline_logos/70px/DL.png"
                }
            ],
            "serpapi_pagination": {
                "current_from": 1,
                "current_to": 2,
                "next_page_token": None
            }
        }
    
    def format_flight_results(self, api_response):
        """Format the API response for easier use in templates"""
        formatted_flights = []
        
        all_flights = []
        if 'best_flights' in api_response:
            all_flights.extend(api_response['best_flights'])
        if 'other_flights' in api_response:
            all_flights.extend(api_response['other_flights'])
        
        for flight in all_flights:
            first_flight = flight['flights'][0] if flight['flights'] else None
            last_flight = flight['flights'][-1] if flight['flights'] else None
            
            if first_flight and last_flight:
                formatted_flight = {
                    'departure_code': first_flight['departure_airport']['id'],
                    'departure_name': first_flight['departure_airport']['name'],
                    'departure_time': first_flight['departure_airport']['time'],
                    'arrival_code': last_flight['arrival_airport']['id'],
                    'arrival_name': last_flight['arrival_airport']['name'],
                    'arrival_time': last_flight['arrival_airport']['time'],
                    'duration': flight.get('total_duration', 0),
                    'duration_formatted': self._format_duration(flight.get('total_duration', 0)),
                    'price': flight.get('price', 0),
                    'airline': self._get_main_airline(flight['flights']),
                    'airline_logo': flight.get('airline_logo', ''),
                    'stops': len(flight.get('layovers', [])),
                    'booking_token': flight.get('booking_token', ''),
                }
                formatted_flights.append(formatted_flight)
        
        return formatted_flights
    
    def _format_duration(self, minutes):
        """Convert minutes to hours and minutes format"""
        if not minutes:
            return "N/A"
        
        hours = minutes // 60
        mins = minutes % 60
        
        if hours > 0:
            return f"{hours}h {mins}m"
        else:
            return f"{mins}m"
    
    def _get_main_airline(self, flights):
        """Get the primary airline for the flight"""
        if not flights:
            return "Unknown"
        
        if len(flights) == 1:
            return flights[0].get('airline', 'Unknown')
        
        main_airline = flights[0].get('airline', 'Unknown')
        return f"{main_airline} + others"