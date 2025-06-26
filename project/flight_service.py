import requests
import os
from django.conf import settings

class FlightSearchService:
    def __init__(self):
        # You'll need to add your SerpAPI key to settings or environment variables
        self.api_key = getattr(settings, 'SERPAPI_KEY', os.environ.get('SERPAPI_KEY'))
        self.base_url = "https://serpapi.com/search.json"
    
    def search_flights(self, departure_city, arrival_city, departure_date, 
                      return_date=None, travel_class='1', adults=1, page_token=None):
        """
        Search for flights using SerpAPI Google Flights
        """
        if not self.api_key:
            raise ValueError("SerpAPI key not configured")
        
        # Convert city names to airport codes if needed
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
        
        # Add return date if provided (round trip)
        if return_date:
            params['return_date'] = return_date
            params['type'] = '1'  # Round trip
        else:
            params['type'] = '2'  # One way
        
        # Add pagination token if provided
        if page_token:
            params['next_page_token'] = page_token
        
        try:
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            raise Exception(f"Flight search API error: {str(e)}")
    
    def _get_airport_code(self, city_input):
        """
        Convert city name to airport code or return if already a code
        This is a simple implementation - you could expand with a proper mapping
        """
        city_input = city_input.strip().upper()
        
        # If it's already a 3-letter airport code, return it
        if len(city_input) == 3 and city_input.isalpha():
            return city_input
        
        # Simple city to airport code mapping
        city_mappings = {
            'NEW YORK': 'NYC',
            'LOS ANGELES': 'LAX',
            'CHICAGO': 'CHI',
            'MIAMI': 'MIA',
            'SAN FRANCISCO': 'SFO',
            'BOSTON': 'BOS',
            'WASHINGTON': 'DCA',
            'SEATTLE': 'SEA',
            'DENVER': 'DEN',
            'ATLANTA': 'ATL',
            'LONDON': 'LHR',
            'PARIS': 'CDG',
            'TOKYO': 'NRT',
            'BERLIN': 'BER',
            'ROME': 'FCO',
            'MADRID': 'MAD',
            'AMSTERDAM': 'AMS',
            'FRANKFURT': 'FRA',
            'ZURICH': 'ZUR',
            'MUNICH': 'MUC',
            'VIENNA': 'VIE',
            'BARCELONA': 'BCN',
            'MILAN': 'MXP',
            'DUBLIN': 'DUB',
            'STOCKHOLM': 'ARN',
            'COPENHAGEN': 'CPH',
            'OSLO': 'OSL',
            'HELSINKI': 'HEL',
            'MOSCOW': 'SVO',
            'ISTANBUL': 'IST',
            'DUBAI': 'DXB',
            'DOHA': 'DOH',
            'SINGAPORE': 'SIN',
            'HONG KONG': 'HKG',
            'BEIJING': 'PEK',
            'SHANGHAI': 'PVG',
            'MUMBAI': 'BOM',
            'DELHI': 'DEL',
            'BANGKOK': 'BKK',
            'JAKARTA': 'CGK',
            'MANILA': 'MNL',
            'SYDNEY': 'SYD',
            'MELBOURNE': 'MEL',
            'PERTH': 'PER',
            'AUCKLAND': 'AKL'
        }
        
        return city_mappings.get(city_input, city_input)
    
    def format_flight_results(self, api_response):
        """
        Format the API response for easier use in templates
        """
        formatted_flights = []
        
        # Get flights from both best_flights and other_flights
        all_flights = []
        if 'best_flights' in api_response:
            all_flights.extend(api_response['best_flights'])
        if 'other_flights' in api_response:
            all_flights.extend(api_response['other_flights'])
        
        for flight in all_flights:
            # For multi-leg flights, we'll show the first and last airports
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
                    'layovers': flight.get('layovers', []),
                    'carbon_emissions': flight.get('carbon_emissions', {}),
                    'booking_token': flight.get('booking_token', ''),
                    'departure_token': flight.get('departure_token', ''),
                    'type': flight.get('type', ''),
                    'raw_data': flight  # Keep original data for debugging
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
        
        # If single flight, return that airline
        if len(flights) == 1:
            return flights[0].get('airline', 'Unknown')
        
        # For multiple flights, return first airline + "via others"
        main_airline = flights[0].get('airline', 'Unknown')
        return f"{main_airline} + others"