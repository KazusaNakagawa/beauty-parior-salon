from pydantic import BaseSettings


class Settings(BaseSettings):
    """
    :secret_key:
      generate CMD: openssl rand -hex 32
    """
    access_token_expire_minutes: int = 30
    algorithm: str = 'HS256'
    secret_key: str

    class Config:
        env_file = '.env'
