# client.py
# Purpose: Create and return an authenticated Assemblyline API client.

from assemblyline_client import get_client  # official helper that builds a client object
from config import settings                 # import our loaded settings (host, user, apikey, etc.)

def get_al_client():
    # get_client(host, apikey=(user, key), verify=bool)
    # - host: URL to your AL instance
    # - apikey: a tuple (username, apikey_string)
    # - verify: if False, ignore SSL cert errors (dev only)
    return get_client(
        settings.host,
        apikey=(settings.user, settings.apikey),
        verify=settings.verify_ssl
    )