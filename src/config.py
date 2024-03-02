from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    :secret_key:
      generate CMD: openssl rand -hex 32
    """
    access_token_expire_minutes: int = 30
    algorithm: str = 'HS256'
    secret_key: str
    tag: str
    db_port: int
    database: str
    mysql_database: str
    test_database: str
    mysql_user: str
    mysql_password: str
    mysql_root_user: str
    mysql_root_password: str

    class Config:
        env_file = '.env'
        from_attributes = True
