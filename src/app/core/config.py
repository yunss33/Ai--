from functools import lru_cache
import os

from pydantic import BaseModel


class Settings(BaseModel):
    """应用统一配置入口

    所有 Python 侧的配置（应用、数据库、AI、语音等）都应从这里读取，避免各处直接访问环境变量。
    """

    # 应用基础配置
    app_name: str = os.getenv("APP_NAME", "AI Course Platform")
    env: str = os.getenv("APP_ENV", "dev")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"

    # 数据库配置
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./app.db")

    # 鉴权 / 安全配置
    secret_key: str = os.getenv("SECRET_KEY", "change-me")
    access_token_expires_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRES_MINUTES", "60"),
    )

    # 大模型 / AI 配置
    ai_api_key: str | None = os.getenv("AI_API_KEY")
    ai_model: str = os.getenv("AI_MODEL", "gpt-4o")
    ai_temperature: float = float(os.getenv("AI_TEMPERATURE", "0.7"))
    ai_api_base: str | None = os.getenv("AI_API_BASE")

    # 语音服务配置
    voice_stt_api_key: str | None = os.getenv("VOICE_STT_API_KEY")
    voice_tts_api_key: str | None = os.getenv("VOICE_TTS_API_KEY")


@lru_cache
def get_settings() -> Settings:
    """获取全局单例 Settings，避免重复解析环境变量。"""
    return Settings()
