import logging

import requests
from decouple import config
from dotenv import load_dotenv

load_dotenv()

# Disable IPv6
requests.packages.urllib3.util.connection.HAS_IPV6 = False


CSV_FILE_PATH = config("CSV_FILE_PATH", default="./valid_example.csv")
SUBS_CSV_FILE_PATH = config("SUBS_CSV_FILE_PATH", default="./subs_example.csv")
CONFIGS_DIR = config("CONFIGS_DIR", default="./configs")
CONFIGS_Q = config("CONFIGS_Q", default="T1")
RESULTS_DIR = config("RESULTS_DIR", default="./results")
TEST_URL = config("TEST_URL", default="https://www.google.com/generate_204")


ELORA_BASE_API_URL = config("ELORA_BASE_API_URL", default="http://localhost:8000")
ELORA_TOKEN_PATH = config("ELORA_TOKEN_PATH", default="/api/admin/token")
ELORA_USER_NAME = config("ELORA_USER_NAME", default="admin")
ELORA_PASSWORD = config("ELORA_PASSWORD", default="admin")


CLIENT_NAME = config("CLIENT_NAME", default="Elora Agent")
