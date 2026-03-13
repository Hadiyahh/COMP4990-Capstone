# config.py
# Purpose: Load configuration (host/user/apikey/etc.) from environment variables
#          so you don't hardcode secrets inside your code.

from dataclasses import dataclass          # lets us make a small "Settings" class automatically
import os                                  # used to read environment variables like AL_HOST
from dotenv import load_dotenv             # reads variables from a .env file into the environment

load_dotenv()                              # loads .env file from current folder (if it exists)

@dataclass                                 # tells Python to auto-generate init + repr for Settings
class Settings:
    # Where Assemblyline is hosted (example: https://localhost or https://yourserver:443)
    host: str = os.getenv("AL_HOST", "https://localhost")

    # The username tied to the API key
    user: str = os.getenv("AL_USER", "admin")

    # The API key (secret)
    apikey: str = os.getenv("AL_APIKEY", "")

    # Whether to verify SSL certs (true for real certs, false for self-signed dev)
    verify_ssl: bool = os.getenv("AL_VERIFY_SSL", "false").lower() == "true"

    # Notification queue name for async ingest (must be unique-ish)
    nq: str = os.getenv("AL_NOTIFICATION_QUEUE", "capstone-nq")

settings = Settings()                      # create a single settings object you can import anywhere