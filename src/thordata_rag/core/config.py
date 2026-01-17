from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # --- 必填项 ---
    THORDATA_SCRAPER_TOKEN: str
    
    # 修改点：将 OpenAI Key 设为必填，用于 DeepSeek/SiliconFlow
    OPENAI_API_KEY: str 
    OPENAI_API_BASE: str = "https://api.deepseek.com" # 默认给个 DeepSeek 地址

    # --- 可选项 ---
    # 修改点：Google Key 改为可选，防止报错
    GOOGLE_API_KEY: Optional[str] = None
    
    THORDATA_PUBLIC_TOKEN: Optional[str] = None
    THORDATA_PUBLIC_KEY: Optional[str] = None
    
    # RAG Settings
    DB_PATH: str = "./data/chroma_db"
    CHUNK_SIZE: int = 1000
    CHUNK_OVERLAP: int = 200

    # 允许 .env 中有多余字段 (extra="ignore")
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

# 实例化
try:
    settings = Settings()
except Exception as e:
    print(f"⚠️ 配置加载失败: {e}")
    # 临时给个空对象防止 import 报错，但运行时会检查
    settings = None