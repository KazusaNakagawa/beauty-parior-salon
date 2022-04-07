import os

from dotenv import load_dotenv

load_dotenv()

_SECRET_KEY = os.getenv('SECRET_KEY')

# to get a string like this run:
# generate CMD: openssl rand -hex 32
ACCESS_TOKEN_EXPIRE_MINUTES = 30
ALGORITHM = "HS256"
SECRET_KEY = _SECRET_KEY
