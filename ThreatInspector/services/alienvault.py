import requests
import logging

class AlienVaultService:
    """Service for interacting with the AlienVault OTX API"""
    
    BASE_URL = "https://otx.alienvault.com/api/v1"
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "X-OTX-API-KEY": api_key,
            "Accept": "application/json"
        }
    
    def check_api_key(self):
        """Test if the API key is valid"""
        if not self.api_key:
            return False
        
        try:
            # Try to fetch user info to validate API key
            response = requests.get(
                f"{self.BASE_URL}/user/me",
                headers=self.headers
            )
            
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Error checking AlienVault API key: {str(e)}")
            return False
    
    def get_pulse_info(self, indicator, indicator_type):
        """
        Get pulse information for the specified indicator
        
        Args:
            indicator (str): The indicator value to look up
            indicator_type (str): The type of indicator ('ip', 'domain', 'url', or 'hash')
            
        Returns:
            dict: The JSON response from AlienVault OTX
        """
        if not self.api_key:
            return {"error": "AlienVault OTX API key not configured"}
        
        # Initialize default pulse_info structure to avoid template errors
        default_pulse_info = {
            "count": 0,
            "pulses": [],
            "references": []
        }
        
        try:
            section = self._get_section(indicator_type)
            
            if not section:
                return {"error": f"Unsupported indicator type: {indicator_type}", "pulse_info": default_pulse_info}
            
            response = requests.get(
                f"{self.BASE_URL}/indicators/{section}/{indicator}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Initialize pulse_info with default values
                result["pulse_info"] = default_pulse_info
                
                # Also fetch pulse details
                try:
                    pulse_response = requests.get(
                        f"{self.BASE_URL}/indicators/{section}/{indicator}/general",
                        headers=self.headers
                    )
                    
                    if pulse_response.status_code == 200:
                        pulse_data = pulse_response.json()
                        
                        # Ensure pulse_info has required fields
                        if "pulse_info" in pulse_data:
                            result["pulse_info"] = pulse_data["pulse_info"]
                            
                            # Ensure count exists
                            if "count" not in result["pulse_info"]:
                                result["pulse_info"]["count"] = len(result["pulse_info"].get("pulses", []))
                                
                            # Ensure pulses exists
                            if "pulses" not in result["pulse_info"]:
                                result["pulse_info"]["pulses"] = []
                                
                            # Ensure references exists
                            if "references" not in result["pulse_info"]:
                                result["pulse_info"]["references"] = []
                        else:
                            # If pulse_info not in response, use our default
                            result["pulse_info"] = default_pulse_info
                except Exception as e:
                    logging.error(f"Error fetching pulse details: {str(e)}")
                    result["pulse_error"] = str(e)
                
                return result
            else:
                logging.error(f"AlienVault API error: {response.status_code} - {response.text}")
                return {
                    "error": f"AlienVault API returned status {response.status_code}",
                    "details": response.text,
                    "pulse_info": default_pulse_info
                }
                
        except Exception as e:
            logging.error(f"Error querying AlienVault OTX: {str(e)}")
            return {"error": str(e), "pulse_info": default_pulse_info}
    
    def _get_section(self, indicator_type):
        """
        Get the appropriate API section for the given indicator type
        """
        if indicator_type == 'ip':
            return "IPv4"
        elif indicator_type == 'domain':
            return "domain"
        elif indicator_type == 'url':
            return "url"
        elif indicator_type == 'hash':
            return "file"  # AlienVault will figure out the hash type
        
        return None
