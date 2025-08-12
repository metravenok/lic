from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")
    app_env: str = Field(default="dev", alias="APP_ENV")
    site_name: str = Field(default="LicenseHub", alias="SITE_NAME")

    database_url: str = Field(..., alias="DATABASE_URL")

    jwt_secret: str = Field(..., alias="JWT_SECRET")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(default=480, alias="JWT_EXPIRE_MINUTES")

    ad_server_uri: str = Field(..., alias="AD_SERVER_URI")
    ad_base_dn: str = Field(..., alias="AD_BASE_DN")
    ad_user_dn_format: str = Field(default="{username}", alias="AD_USER_DN_FORMAT")
    ad_use_ssl: bool = Field(default=True, alias="AD_USE_SSL")
    ad_service_account_dn: str | None = Field(default=None, alias="AD_SERVICE_ACCOUNT_DN")
    ad_service_account_password: str | None = Field(default=None, alias="AD_SERVICE_ACCOUNT_PASSWORD")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()  # type: ignore