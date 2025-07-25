# 集中的配置文件
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

class Config:
    """
    # 从环境变量获取密钥，提供一个默认值以防万一
    SECRET_KEY = os.environ.get('SECRET_KEY', 'a-very-secret-key-that-you-should-change')

    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///../instance/pet_recipes.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    """
    
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'pet-recipe-secret-key-2025'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = 'static/uploads'
    
    # 分页配置
    POSTS_PER_PAGE = 12
    RECIPES_PER_PAGE = 8
    
    # 营养计算配置
    NUTRITION_PRECISION = 2  # 营养成分保留小数位数
    MIN_RECIPE_WEIGHT = 50   # 最小食谱重量(g)
    MAX_RECIPE_WEIGHT = 2000 # 最大食谱重量(g)
    
    # 推荐算法配置
    RECOMMENDATION_LIMIT = 10     # 最大推荐数量
    SIMILARITY_THRESHOLD = 0.3    # 相似度阈值
    
    # 图表配置
    CHART_COLORS = {
        'protein': '#5580AD',
        'fat': '#B82F0D', 
        'carbohydrate': '#A1B4B2',
        'fiber': '#EDBF9D',
        'success': '#28a745',
        'warning': '#ffc107',
        'danger': '#dc3545'
    }

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'pet_nutrition.db')

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), 'pet_nutrition.db')

class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}