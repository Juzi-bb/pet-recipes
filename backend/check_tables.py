# 在 backend 目录下创建此文件：check_tables.py
# 用于检查数据库表结构和数据

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from sqlalchemy import text

def check_database_tables():
    """检查数据库表结构"""
    app = create_app()
    
    with app.app_context():
        print("🔍 检查数据库表结构...\n")
        
        # 获取所有表名
        try:
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            
            print(f"📊 数据库中的表 ({len(tables)} 个):")
            for table in sorted(tables):
                print(f"  ✓ {table}")
            print()
            
        except Exception as e:
            print(f"❌ 获取表列表失败: {e}")
            return False
        
        # 检查关键表是否存在
        required_tables = [
            'users', 'pets', 'recipes', 'ingredients', 
            'recipe_ingredients', 'recipe_likes', 'recipe_favorites'
        ]
        
        print("🔍 检查必需的表:")
        missing_tables = []
        for table in required_tables:
            if table in tables:
                print(f"  ✅ {table} - 存在")
            else:
                print(f"  ❌ {table} - 不存在")
                missing_tables.append(table)
        
        if missing_tables:
            print(f"\n⚠️ 缺少表: {', '.join(missing_tables)}")
            print("请运行以下命令创建表:")
            print("python -c \"from app import create_app; from app.extensions import db; app=create_app(); app.app_context().push(); db.create_all(); print('Tables created!')\"")
            return False
        
        # 检查表结构
        print("\n🔍 检查表结构:")
        
        # 检查 recipe_likes 表
        try:
            likes_columns = inspector.get_columns('recipe_likes')
            print(f"  📋 recipe_likes 表字段 ({len(likes_columns)} 个):")
            for col in likes_columns:
                print(f"    - {col['name']}: {col['type']}")
        except Exception as e:
            print(f"  ❌ 无法获取 recipe_likes 表结构: {e}")
        
        # 检查 recipe_favorites 表
        try:
            favorites_columns = inspector.get_columns('recipe_favorites')
            print(f"  📋 recipe_favorites 表字段 ({len(favorites_columns)} 个):")
            for col in favorites_columns:
                print(f"    - {col['name']}: {col['type']}")
        except Exception as e:
            print(f"  ❌ 无法获取 recipe_favorites 表结构: {e}")
        
        # 检查数据量
        print("\n📊 数据统计:")
        data_stats = [
            ('users', 'SELECT COUNT(*) FROM users'),
            ('recipes', 'SELECT COUNT(*) FROM recipes'),
            ('recipe_likes', 'SELECT COUNT(*) FROM recipe_likes'),
            ('recipe_favorites', 'SELECT COUNT(*) FROM recipe_favorites')
        ]
        
        for table_name, query in data_stats:
            try:
                count = db.session.execute(text(query)).scalar()
                print(f"  📈 {table_name}: {count} 条记录")
            except Exception as e:
                print(f"  ❌ 查询 {table_name} 失败: {e}")
        
        print("\n✅ 数据库检查完成!")
        return True

def create_test_data():
    """创建测试数据"""
    app = create_app()
    
    with app.app_context():
        print("🔨 创建测试数据...\n")
        
        # 导入模型
        from app.models.user_model import User
        from app.models.recipe_model import Recipe, RecipeStatus
        from app.models.recipe_like_model import RecipeLike
        from app.models.recipe_favorite_model import RecipeFavorite
        
        try:
            # 检查是否已有用户
            user_count = User.query.count()
            if user_count == 0:
                print("创建测试用户...")
                test_user = User(username='testuser', nickname='Test User')
                test_user.set_password('123456')
                db.session.add(test_user)
                db.session.commit()
                print("✅ 测试用户创建成功")
            else:
                print(f"✅ 已有 {user_count} 个用户")
            
            # 检查是否已有食谱
            recipe_count = Recipe.query.count()
            if recipe_count == 0:
                print("创建测试食谱...")
                user = User.query.first()
                if user:
                    test_recipe = Recipe(
                        name='健康鸡肉餐',
                        description='营养均衡的宠物鸡肉餐',
                        user_id=user.id,
                        status=RecipeStatus.PUBLISHED,
                        is_public=True,
                        total_calories=350.0,
                        total_protein=25.0,
                        total_fat=15.0,
                        total_carbohydrate=8.0
                    )
                    db.session.add(test_recipe)
                    db.session.commit()
                    print("✅ 测试食谱创建成功")
                else:
                    print("❌ 没有用户，无法创建食谱")
            else:
                print(f"✅ 已有 {recipe_count} 个食谱")
            
            print("\n✅ 测试数据准备完成!")
            
        except Exception as e:
            print(f"❌ 创建测试数据失败: {e}")
            db.session.rollback()

if __name__ == "__main__":
    print("🚀 宠物食谱数据库检查工具\n")
    
    # 检查表结构
    success = check_database_tables()
    
    if success:
        # 询问是否创建测试数据
        response = input("\n是否创建测试数据? (y/N): ").lower().strip()
        if response in ['y', 'yes']:
            create_test_data()
        else:
            print("跳过测试数据创建")
    
    print("\n🎉 检查完成!")