import os

from dotenv import load_dotenv

load_dotenv()

LSD_URL = os.getenv("LSD_URL")
LSD_DB = os.getenv("LSD_DB")
LSD_USER = os.getenv("LSD_USER")
LSD_HOST = os.getenv("LSD_HOST")
LSD_PASSWORD = os.getenv("LSD_PASSWORD")
