"""
数据库配置文件
整合所有营养相关的数据模型
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from sqlalchemy.engine import Engine
import sqlite3

# 导入所有模型
from ingredient_model import Ingredient, IngredientCategory, Base as IngredientBase
from recipe_model import Recipe, RecipeStatus, Base as RecipeBase
from recipe_ingredient_model import RecipeIngredient, Base as RecipeIngredientBase
from nutrition_requirements_model import (
    NutritionRequirement, PetType, LifeStage, ActivityLevel, 
    Base as NutritionRequirementBase
)

# 统一的Base
Base = declarative_base()

# 数据库配置
DATABASE_URL = "sqlite:///pet_nutrition.db"

# 创建数据库引擎
engine = create_engine(
    DATABASE_URL,
    echo=False,  # 设置为True可以看到SQL语句
    connect_args={"check_same_thread": False}
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLite外键约束启用
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    if isinstance(dbapi_connection, sqlite3.Connection):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_tables():
    """创建所有表"""
    # 导入所有模型以确保表被创建
    from ingredient_model import Ingredient
    from recipe_model import Recipe
    from recipe_ingredient_model import RecipeIngredient
    from nutrition_requirements_model import NutritionRequirement
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("所有数据库表创建完成")

def drop_tables():
    """删除所有表"""
    Base.metadata.drop_all(bind=engine)
    print("所有数据库表删除完成")

def init_database():
    """初始化数据库"""
    # 创建表
    create_tables()
    
    # 运行初始化数据脚本
    from init_nutrition_data import main as init_data
    init_data()

if __name__ == "__main__":
    # 初始化数据库
    init_database()