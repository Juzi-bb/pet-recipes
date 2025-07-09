# 集中的配置文件
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

class Config:
    # 从环境变量获取密钥，提供一个默认值以防万一
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-secret-key-that-you-should-change')

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///../instance/pet_recipes.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False