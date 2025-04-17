import requests
import logging

class VirusTotalService:
    """Service for interacting with the VirusTotal API"""
    
    BASE_URL = "https://www.virustotal.com/api/v3"
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "x-apikey": api_key,
            "accept": "application/json"
        }
    
    def check_api_key(self):
        """Test if the API key is valid"""
        if not self.api_key:
            return False
        
        try:
            # Try to fetch user info as a quick API key validation
            response = requests.get(
                f"{self.BASE_URL}/users/current",
                headers=self.headers
            )
            
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Error checking VirusTotal API key: {str(e)}")
            return False
    
    def query(self, indicator, indicator_type):
        """
        Query VirusTotal for information about the specified indicator
        
        Args:
            indicator (str): The indicator value to look up
            indicator_type (str): The type of indicator ('ip', 'domain', 'url', or 'hash')
            
        Returns:
            dict: The JSON response from VirusTotal
        """
        if not self.api_key:
            return {"error": "VirusTotal API key not configured"}
        
        # Create a default data structure for error cases
        default_response = {
            "data": {
                "attributes": {
                    "last_analysis_stats": {
                        "malicious": 0,
                        "suspicious": 0,
                        "undetected": 0,
                        "timeout": 0
                    },
                    "last_analysis_results": {},
                    "categories": {}
                }
            }
        }
        
        try:
            endpoint = self._get_endpoint(indicator, indicator_type)
            
            if not endpoint:
                return {"error": f"Unsupported indicator type: {indicator_type}", **default_response}
            
            response = requests.get(
                f"{self.BASE_URL}/{endpoint}",
                headers=self.headers
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Ensure the response has the expected structure
                if "data" not in result:
                    result["data"] = default_response["data"]
                
                if "attributes" not in result["data"]:
                    result["data"]["attributes"] = default_response["data"]["attributes"]
                
                attrs = result["data"]["attributes"]
                
                # Ensure required attributes exist
                if "last_analysis_stats" not in attrs:
                    attrs["last_analysis_stats"] = default_response["data"]["attributes"]["last_analysis_stats"]
                
                # Make sure all stats fields exist
                for key in ["malicious", "suspicious", "undetected", "timeout"]:
                    if key not in attrs["last_analysis_stats"]:
                        attrs["last_analysis_stats"][key] = 0
                
                if "last_analysis_results" not in attrs:
                    attrs["last_analysis_results"] = {}
                    
                if "categories" not in attrs:
                    attrs["categories"] = {}
                
                return result
            else:
                logging.error(f"VirusTotal API error: {response.status_code} - {response.text}")
                return {
                    "error": f"VirusTotal API returned status {response.status_code}",
                    "details": response.text,
                    **default_response
                }
                
        except Exception as e:
            logging.error(f"Error querying VirusTotal: {str(e)}")
            return {"error": str(e), **default_response}
    
    def _get_endpoint(self, indicator, indicator_type):
        """
        Get the appropriate API endpoint for the given indicator type
        """
        if indicator_type == 'ip':
            return f"ip_addresses/{indicator}"
        elif indicator_type == 'domain':
            return f"domains/{indicator}"
        elif indicator_type == 'url':
            import base64
            # VirusTotal needs URLs to be base64 encoded
            url_id = base64.urlsafe_b64encode(indicator.encode()).decode().strip("=")
            return f"urls/{url_id}"
        elif indicator_type == 'hash':
            return f"files/{indicator}"
        
        return None
