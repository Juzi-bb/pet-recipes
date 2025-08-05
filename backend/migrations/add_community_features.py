# backend/migrations/add_community_features.py
"""
数据库迁移脚本：添加社区功能
- 创建点赞表 (recipe_likes)
- 为recipes表添加likes_count字段用于性能优化
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
sys.path.insert(0, backend_dir)

from app import create_app
from app.extensions import db
from sqlalchemy import text

def run_migration():
    """运行迁移脚本"""
    app = create_app()
    
    with app.app_context():
        print("🚀 开始添加社区功能...")
        
        try:
            # 检查并创建点赞表
            create_likes_table()
            
            # 检查并添加likes_count字段到recipes表
            add_likes_count_to_recipes()
            
            # 初始化现有食谱的点赞数
            initialize_likes_count()
            
            print("✅ 社区功能迁移完成！")
            
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            db.session.rollback()
            raise

def create_likes_table():
    """创建点赞表"""
    print("📋 检查点赞表...")
    
    # 检查表是否已存在
    result = db.session.execute(text("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='recipe_likes'
    """)).fetchone()
    
    if result:
        print("   ✓ 点赞表已存在")
        return
    
    print("   ➕ 创建点赞表...")
    
    # 创建点赞表
    db.session.execute(text("""
        CREATE TABLE recipe_likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            recipe_id INTEGER NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE,
            FOREIGN KEY (recipe_id) REFERENCES recipes (id) ON DELETE CASCADE,
            UNIQUE(user_id, recipe_id)
        )
    """))
    
    # 创建索引以提高查询性能
    db.session.execute(text("""
        CREATE INDEX idx_recipe_likes_user_id ON recipe_likes(user_id)
    """))
    
    db.session.execute(text("""
        CREATE INDEX idx_recipe_likes_recipe_id ON recipe_likes(recipe_id)
    """))
    
    db.session.commit()
    print("   ✅ 点赞表创建成功")

def add_likes_count_to_recipes():
    """为recipes表添加likes_count字段"""
    print("📋 检查recipes表结构...")
    
    # 检查likes_count字段是否已存在
    result = db.session.execute(text("""
        PRAGMA table_info(recipes)
    """)).fetchall()
    
    columns = [row[1] for row in result]  # row[1]是列名
    
    if 'likes_count' in columns:
        print("   ✓ likes_count字段已存在")
        return
    
    print("   ➕ 添加likes_count字段...")
    
    # 添加likes_count字段
    db.session.execute(text("""
        ALTER TABLE recipes ADD COLUMN likes_count INTEGER DEFAULT 0
    """))
    
    db.session.commit()
    print("   ✅ likes_count字段添加成功")

def initialize_likes_count():
    """初始化现有食谱的点赞数"""
    print("📊 初始化现有食谱的点赞数...")
    
    # 统计每个食谱的点赞数并更新
    db.session.execute(text("""
        UPDATE recipes 
        SET likes_count = (
            SELECT COUNT(*) 
            FROM recipe_likes 
            WHERE recipe_likes.recipe_id = recipes.id
        )
        WHERE likes_count IS NULL OR likes_count = 0
    """))
    
    db.session.commit()
    
    # 显示统计信息
    result = db.session.execute(text("""
        SELECT COUNT(*) as total_recipes,
               SUM(likes_count) as total_likes
        FROM recipes 
        WHERE is_public = 1
    """)).fetchone()
    
    print(f"   ✅ 初始化完成: {result[0]} 个公开食谱, 总计 {result[1] or 0} 个点赞")

def create_community_indexes():
    """创建社区功能相关的数据库索引以优化性能"""
    print("🔍 创建性能优化索引...")
    
    try:
        # 为recipes表创建复合索引，优化社区页面查询
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_recipes_public_status 
            ON recipes(is_public, status, is_active)
        """))
        
        # 为recipes表创建created_at索引，优化按时间排序
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_recipes_created_at 
            ON recipes(created_at)
        """))
        
        # 为recipes表创建likes_count索引，优化按点赞数排序
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_recipes_likes_count 
            ON recipes(likes_count)
        """))
        
        # 为recipe_favorites表创建复合索引
        db.session.execute(text("""
            CREATE INDEX IF NOT EXISTS idx_recipe_favorites_recipe_created 
            ON recipe_favorites(recipe_id, created_at)
        """))
        
        db.session.commit()
        print("   ✅ 性能优化索引创建完成")
        
    except Exception as e:
        print(f"   ⚠️ 创建索引时出现警告: {e}")
        # 索引创建失败不影响整体迁移

def verify_migration():
    """验证迁移是否成功"""
    print("🔍 验证迁移结果...")
    
    try:
        # 检查点赞表
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM sqlite_master 
            WHERE type='table' AND name='recipe_likes'
        """)).fetchone()
        
        if result[0] == 0:
            raise Exception("点赞表未创建成功")
        
        # 检查recipes表的likes_count字段
        result = db.session.execute(text("""
            PRAGMA table_info(recipes)
        """)).fetchall()
        
        columns = [row[1] for row in result]
        if 'likes_count' not in columns:
            raise Exception("likes_count字段未添加成功")
        
        # 检查数据完整性
        result = db.session.execute(text("""
            SELECT COUNT(*) FROM recipes WHERE likes_count IS NOT NULL
        """)).fetchone()
        
        print(f"   ✅ 验证通过: {result[0]} 个食谱的点赞数已初始化")
        return True
        
    except Exception as e:
        print(f"   ❌ 验证失败: {e}")
        return False

if __name__ == '__main__':
    print("🏗️  开始社区功能数据库迁移...")
    print("=" * 50)
    
    try:
        run_migration()
        create_community_indexes()
        
        if verify_migration():
            print("=" * 50)
            print("🎉 社区功能迁移全部完成！")
            print("\n✨ 新功能包括:")
            print("   • 用户可以点赞食谱")
            print("   • 社区页面按热度排序")
            print("   • 性能优化索引")
            print("   • 统计数据完整性")
        else:
            print("❌ 迁移验证失败，请检查数据库状态")
            sys.exit(1)
            
    except Exception as e:
        print(f"💥 迁移失败: {e}")
        print("\n🔧 请检查:")
        print("   • 数据库连接是否正常")
        print("   • 数据库文件权限是否正确")
        print("   • 是否有其他进程占用数据库")
        sys.exit(1)