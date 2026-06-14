from pydantic_settings import BaseSettings


class TestingSettings(BaseSettings):
    TESTING: bool = False
    COOKIE_SECURE: bool = True


testing_settings = TestingSettings()
