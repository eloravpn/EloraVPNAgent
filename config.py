import logging

import requests
from decouple import config
from dotenv import load_dotenv

load_dotenv()

# Disable IPv6
requests.packages.urllib3.util.connection.HAS_IPV6 = False


CSV_FILE_PATH = config("CSV_FILE_PATH", default="./valid_example.csv")


ELORA_BASE_API_URL = config("ELORA_TOKEN_URL", default="http://localhost:8000")
ELORA_TOKEN_PATH = config("ELORA_TOKEN_PATH", default="/api/admin/token")
ELORA_USER_NAME = config("ELORA_USER_NAME", default="admin")
ELORA_PASSWORD = config("ELORA_PASSWORD", default="admin")


CLIENT_NAME = config("CLIENT_NAME", default="Elora Agent")
