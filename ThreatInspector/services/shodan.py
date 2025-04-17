import requests
import logging

class ShodanService:
    """Service for interacting with the Shodan API"""
    
    BASE_URL = "https://api.shodan.io"
    
    def __init__(self, api_key):
        self.api_key = api_key
    
    def check_api_key(self):
        """Test if the API key is valid"""
        if not self.api_key:
            return False
        
        try:
            # Try to fetch API info to validate the key
            response = requests.get(
                f"{self.BASE_URL}/api-info?key={self.api_key}"
            )
            
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Error checking Shodan API key: {str(e)}")
            return False
    
    def lookup_ip(self, ip_address):
        """
        Look up information about an IP address
        
        Args:
            ip_address (str): The IP address to look up
            
        Returns:
            dict: The JSON response from Shodan
        """
        if not self.api_key:
            return {"error": "Shodan API key not configured"}
        
        # Default structure for when results are missing
        default_response = {
            "ip": ip_address,
            "hostnames": [],
            "ports": [],
            "data": []
        }
        
        try:
            response = requests.get(
                f"{self.BASE_URL}/shodan/host/{ip_address}?key={self.api_key}"
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Ensure required fields exist
                for field in ["hostnames", "ports", "data"]:
                    if field not in result:
                        result[field] = default_response[field]
                
                return result
            else:
                logging.error(f"Shodan API error: {response.status_code} - {response.text}")
                return {
                    "error": f"Shodan API returned status {response.status_code}",
                    "details": response.text,
                    **default_response
                }
                
        except Exception as e:
            logging.error(f"Error looking up IP with Shodan: {str(e)}")
            return {"error": str(e), **default_response}
    
    def lookup_domain(self, domain):
        """
        Look up information about a domain
        
        Args:
            domain (str): The domain to look up
            
        Returns:
            dict: The JSON response from Shodan
        """
        if not self.api_key:
            return {"error": "Shodan API key not configured"}
        
        # Default structure for when results are missing
        default_response = {
            "domain": domain,
            "hostnames": [],
            "ports": [],
            "data": []
        }
        
        try:
            # First try to resolve the domain to an IP
            try:
                resolve_response = requests.get(
                    f"{self.BASE_URL}/dns/resolve?hostnames={domain}&key={self.api_key}"
                )
                
                if resolve_response.status_code == 200:
                    resolved = resolve_response.json()
                    if domain in resolved and resolved[domain]:
                        ip = resolved[domain]
                        # Then look up the IP
                        return self.lookup_ip(ip)
            except Exception as e:
                logging.error(f"Error resolving domain with Shodan: {str(e)}")
            
            # If domain resolution fails or returns no IP, try to search for the domain
            response = requests.get(
                f"{self.BASE_URL}/shodan/host/search?query=hostname:{domain}&key={self.api_key}"
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Ensure required fields exist
                if "matches" in result:
                    # If we have matches, get the data from the first match
                    if len(result["matches"]) > 0:
                        match = result["matches"][0]
                        
                        # Extract hostnames
                        if "hostnames" in match:
                            default_response["hostnames"] = match["hostnames"]
                        
                        # Extract ports
                        if "ports" in match:
                            default_response["ports"] = match["ports"]
                        
                        # Use the matches as data
                        default_response["data"] = result["matches"]
                        
                        return default_response
                    
                return {**result, **default_response}
            else:
                logging.error(f"Shodan API error: {response.status_code} - {response.text}")
                return {
                    "error": f"Shodan API returned status {response.status_code}",
                    "details": response.text,
                    **default_response
                }
                
        except Exception as e:
            logging.error(f"Error looking up domain with Shodan: {str(e)}")
            return {"error": str(e), **default_response}
