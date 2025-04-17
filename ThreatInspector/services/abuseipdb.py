import requests
import logging

class AbuseIPDBService:
    """Service for interacting with the AbuseIPDB API"""
    
    BASE_URL = "https://api.abuseipdb.com/api/v2"
    
    def __init__(self, api_key):
        self.api_key = api_key
        self.headers = {
            "Key": api_key,
            "Accept": "application/json"
        }
    
    def check_api_key(self):
        """Test if the API key is valid"""
        if not self.api_key:
            return False
        
        try:
            # Use the check endpoint with a known IP to test the API key
            response = requests.get(
                f"{self.BASE_URL}/check",
                headers=self.headers,
                params={"ipAddress": "8.8.8.8", "maxAgeInDays": 90}
            )
            
            return response.status_code == 200
        except Exception as e:
            logging.error(f"Error checking AbuseIPDB API key: {str(e)}")
            return False
    
    def check_ip(self, ip_address, max_age_in_days=90):
        """
        Check an IP address against the AbuseIPDB database
        
        Args:
            ip_address (str): The IP address to check
            max_age_in_days (int): Maximum age of reports to include
            
        Returns:
            dict: The JSON response from AbuseIPDB
        """
        if not self.api_key:
            return {"error": "AbuseIPDB API key not configured"}
        
        # Default response structure
        default_response = {
            "data": {
                "ipAddress": ip_address,
                "abuseConfidenceScore": 0,
                "countryCode": "N/A",
                "countryName": "Unknown",
                "isp": "Unknown",
                "domain": "",
                "usageType": "Unknown",
                "reports": []
            }
        }
        
        try:
            params = {
                "ipAddress": ip_address,
                "maxAgeInDays": max_age_in_days,
                "verbose": True
            }
            
            response = requests.get(
                f"{self.BASE_URL}/check",
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Ensure the response has the expected structure
                if "data" not in result:
                    result["data"] = default_response["data"]
                
                # Ensure all required fields exist
                for key in default_response["data"].keys():
                    if key not in result["data"]:
                        result["data"][key] = default_response["data"][key]
                
                return result
            else:
                logging.error(f"AbuseIPDB API error: {response.status_code} - {response.text}")
                return {
                    "error": f"AbuseIPDB API returned status {response.status_code}",
                    "details": response.text,
                    **default_response
                }
                
        except Exception as e:
            logging.error(f"Error checking IP with AbuseIPDB: {str(e)}")
            return {"error": str(e), **default_response}
    
    def get_reports(self, ip_address, max_age_in_days=90, limit=100):
        """
        Get reports for an IP address
        
        Args:
            ip_address (str): The IP address to get reports for
            max_age_in_days (int): Maximum age of reports to include
            limit (int): Maximum number of reports to return
            
        Returns:
            dict: The JSON response from AbuseIPDB
        """
        if not self.api_key:
            return {"error": "AbuseIPDB API key not configured"}
        
        # Default response structure
        default_response = {
            "data": {
                "results": [],
                "count": 0,
                "page": 1,
                "perPage": limit,
                "ipAddress": ip_address
            }
        }
        
        try:
            params = {
                "ipAddress": ip_address,
                "maxAgeInDays": max_age_in_days,
                "limit": limit
            }
            
            response = requests.get(
                f"{self.BASE_URL}/reports",
                headers=self.headers,
                params=params
            )
            
            if response.status_code == 200:
                result = response.json()
                
                # Ensure the response has the expected structure
                if "data" not in result:
                    result["data"] = default_response["data"]
                
                # Ensure all required fields exist
                for key in default_response["data"].keys():
                    if key not in result["data"]:
                        result["data"][key] = default_response["data"][key]
                
                return result
            else:
                logging.error(f"AbuseIPDB API error: {response.status_code} - {response.text}")
                return {
                    "error": f"AbuseIPDB API returned status {response.status_code}",
                    "details": response.text,
                    **default_response
                }
                
        except Exception as e:
            logging.error(f"Error getting reports from AbuseIPDB: {str(e)}")
            return {"error": str(e), **default_response}
