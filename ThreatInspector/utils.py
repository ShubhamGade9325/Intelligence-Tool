import re
import ipaddress

def detect_indicator_type(indicator):
    """
    Detect the type of indicator:
    - IP address
    - Domain
    - URL
    - File hash (MD5, SHA1, SHA256)
    """
    # Check if it's an IP address
    try:
        ipaddress.ip_address(indicator)
        return 'ip'
    except ValueError:
        pass
    
    # Check if it's a URL
    if re.match(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', indicator):
        return 'url'
    
    # Check if it's a domain
    if re.match(r'^(?:[-A-Za-z0-9]+\.)+[A-Za-z]{2,}$', indicator):
        return 'domain'
    
    # Check if it's a hash (MD5, SHA1, SHA256)
    if re.match(r'^[a-fA-F0-9]{32}$', indicator):  # MD5
        return 'hash'
    if re.match(r'^[a-fA-F0-9]{40}$', indicator):  # SHA1
        return 'hash'
    if re.match(r'^[a-fA-F0-9]{64}$', indicator):  # SHA256
        return 'hash'
    
    # Unknown type
    return None

def validate_indicator(indicator, indicator_type):
    """
    Validate the format of the indicator based on its type
    """
    if indicator_type == 'ip':
        try:
            ipaddress.ip_address(indicator)
            return True
        except ValueError:
            return False
    
    elif indicator_type == 'url':
        return bool(re.match(r'^https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', indicator))
    
    elif indicator_type == 'domain':
        return bool(re.match(r'^(?:[-A-Za-z0-9]+\.)+[A-Za-z]{2,}$', indicator))
    
    elif indicator_type == 'hash':
        # Check if it's a hash (MD5, SHA1, SHA256)
        return bool(
            re.match(r'^[a-fA-F0-9]{32}$', indicator) or  # MD5
            re.match(r'^[a-fA-F0-9]{40}$', indicator) or  # SHA1
            re.match(r'^[a-fA-F0-9]{64}$', indicator)     # SHA256
        )
    
    return False

def get_hash_type(hash_value):
    """
    Identify the hash type based on its length
    """
    length = len(hash_value)
    if length == 32:
        return 'md5'
    elif length == 40:
        return 'sha1'
    elif length == 64:
        return 'sha256'
    else:
        return 'unknown'

def format_timestamp(timestamp):
    """
    Format a timestamp into a human-readable string
    """
    from datetime import datetime
    if isinstance(timestamp, (int, float)):
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    return timestamp
