"""
宠物食谱网站 - 社区功能一键设置脚本
自动完成社区功能的数据库迁移、验证和演示数据创建
"""

import sys
import os
from datetime import datetime, timedelta
import random

# 添加项目根目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir) if 'migrations' in current_dir else current_dir
if 'backend' not in backend_dir:
    backend_dir = os.path.join(backend_dir, 'backend')
sys.path.insert(0, backend_dir)

def setup_environment():
    """设置环境和导入"""
    try:
        from app import create_app
        from app.extensions import db
        from app.models.user_model import User
        from app.models.recipe_model import Recipe, RecipeStatus
        from app.models.recipe_like_model import RecipeLike
        from app.models.recipe_favorite_model import RecipeFavorite
        from app.models.pet_model import Pet
        from sqlalchemy import text
        
        return create_app(), db, {
            'User': User, 'Recipe': Recipe, 'RecipeStatus': RecipeStatus,
            'RecipeLike': RecipeLike, 'RecipeFavorite': RecipeFavorite,
            'Pet': Pet, 'text': text
        }
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        print("请确保在正确的项目目录中运行此脚本")
        sys.exit(1)

def run_community_migration(app, db, models):
    """运行社区功能数据库迁移"""
    print("🚀 开始社区功能数据库迁移...")
    
    with app.app_context():
        try:
            # 创建点赞表
            result = db.session.execute(models['text']("""
                SELECT name FROM sqlite_master WHERE type='table' AND name='recipe_likes'
            """)).fetchone()
            
            if not result:
                print("📋 创建点赞表...")
                db.session.execute(models['text']("""
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
                
                # 创建索引
                db.session.execute(models['text']("""
                    CREATE INDEX idx_recipe_likes_user_id ON recipe_likes(user_id)
                """))
                db.session.execute(models['text']("""
                    CREATE INDEX idx_recipe_likes_recipe_id ON recipe_likes(recipe_id)
                """))
                print("   ✅ 点赞表创建成功")
            else:
                print("   ✓ 点赞表已存在")
            
            # 检查并添加likes_count字段
            columns_result = db.session.execute(models['text']("""
                PRAGMA table_info(recipes)
            """)).fetchall()
            
            columns = [row[1] for row in columns_result]
            
            if 'likes_count' not in columns:
                print("📋 添加likes_count字段...")
                db.session.execute(models['text']("""
                    ALTER TABLE recipes ADD COLUMN likes_count INTEGER DEFAULT 0
                """))
                print("   ✅ likes_count字段添加成功")
            else:
                print("   ✓ likes_count字段已存在")
            
            # 初始化现有食谱的点赞数
            db.session.execute(models['text']("""
                UPDATE recipes 
                SET likes_count = (
                    SELECT COUNT(*) FROM recipe_likes 
                    WHERE recipe_likes.recipe_id = recipes.id
                )
            """))
            
            # 创建性能优化索引
            indexes_to_create = [
                ("idx_recipes_public_status", "recipes(is_public, status, is_active)"),
                ("idx_recipes_created_at", "recipes(created_at)"),
                ("idx_recipes_likes_count", "recipes(likes_count)")
            ]
            
            for index_name, index_definition in indexes_to_create:
                try:
                    db.session.execute(models['text'](f"""
                        CREATE INDEX IF NOT EXISTS {index_name} ON {index_definition}
                    """))
                except Exception as e:
                    print(f"   ⚠️ 创建索引 {index_name} 时出现警告: {e}")
            
            db.session.commit()
            print("✅ 数据库迁移完成")
            return True
            
        except Exception as e:
            print(f"❌ 迁移失败: {e}")
            db.session.rollback()
            return False

def verify_community_setup(app, db, models):
    """验证社区功能设置"""
    print("🔍 验证社区功能设置...")
    
    with app.app_context():
        try:
            # 检查点赞表
            result = db.session.execute(models['text']("""
                SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='recipe_likes'
            """)).fetchone()
            
            if result[0] == 0:
                print("   ❌ 点赞表未找到")
                return False
            
            # 检查likes_count字段
            columns_result = db.session.execute(models['text']("""
                PRAGMA table_info(recipes)
            """)).fetchall()
            
            columns = [row[1] for row in columns_result]
            if 'likes_count' not in columns:
                print("   ❌ likes_count字段未找到")
                return False
            
            # 检查公开食谱数量
            public_recipes = models['Recipe'].query.filter_by(
                is_public=True, 
                is_active=True
            ).count()
            
            print(f"   ✓ 找到 {public_recipes} 个公开食谱")
            
            # 检查点赞数据
            likes_count = models['RecipeLike'].query.count()
            print(f"   ✓ 找到 {likes_count} 个点赞记录")
            
            # 检查收藏数据
            favorites_count = models['RecipeFavorite'].query.count()
            print(f"   ✓ 找到 {favorites_count} 个收藏记录")
            
            print("✅ 社区功能验证通过")
            return True
            
        except Exception as e:
            print(f"❌ 验证失败: {e}")
            return False

def create_demo_data(app, db, models):
    """创建演示数据"""
    print("🎭 创建社区功能演示数据...")
    
    with app.app_context():
        try:
            # 检查是否已有足够的演示数据
            public_recipes = models['Recipe'].query.filter_by(is_public=True).count()
            
            if public_recipes >= 5:
                print(f"   ✓ 已有 {public_recipes} 个公开食谱，跳过演示数据创建")
                return True
            
            # 获取现有用户
            users = models['User'].query.limit(3).all()
            if len(users) < 2:
                print("   ⚠️ 用户数量不足，无法创建演示数据")
                print("   提示：请先注册一些用户账号")
                return True
            
            # 获取现有食谱
            recipes = models['Recipe'].query.filter_by(is_active=True).limit(10).all()
            
            if len(recipes) < 3:
                print("   ⚠️ 食谱数量不足，无法创建演示数据")
                print("   提示：请先创建一些食谱")
                return True
            
            # 将部分食谱设为公开
            recipes_to_publish = recipes[:min(5, len(recipes))]
            for i, recipe in enumerate(recipes_to_publish):
                if not recipe.is_public:
                    recipe.is_public = True
                    recipe.status = models['RecipeStatus'].PUBLISHED
                    recipe.updated_at = datetime.utcnow()
                    print(f"   📢 将食谱 '{recipe.name}' 设为公开")
            
            # 创建随机点赞数据
            demo_likes_created = 0
            for recipe in recipes_to_publish:
                # 随机选择用户进行点赞
                liking_users = random.sample(users, min(random.randint(1, 3), len(users)))
                
                for user in liking_users:
                    # 检查是否已经点赞
                    existing_like = models['RecipeLike'].query.filter_by(
                        user_id=user.id,
                        recipe_id=recipe.id
                    ).first()
                    
                    if not existing_like:
                        like = models['RecipeLike'](
                            user_id=user.id,
                            recipe_id=recipe.id,
                            created_at=datetime.utcnow() - timedelta(
                                days=random.randint(0, 30),
                                hours=random.randint(0, 23)
                            )
                        )
                        db.session.add(like)
                        demo_likes_created += 1
            
            # 创建随机收藏数据
            demo_favorites_created = 0
            for recipe in recipes_to_publish:
                # 随机选择用户进行收藏
                favoriting_users = random.sample(users, min(random.randint(0, 2), len(users)))
                
                for user in favoriting_users:
                    # 检查是否已经收藏
                    existing_favorite = models['RecipeFavorite'].query.filter_by(
                        user_id=user.id,
                        recipe_id=recipe.id
                    ).first()
                    
                    if not existing_favorite:
                        favorite = models['RecipeFavorite'](
                            user_id=user.id,
                            recipe_id=recipe.id,
                            created_at=datetime.utcnow() - timedelta(
                                days=random.randint(0, 20),
                                hours=random.randint(0, 23)
                            )
                        )
                        db.session.add(favorite)
                        demo_favorites_created += 1
            
            # 更新使用次数
            for recipe in recipes_to_publish:
                if not recipe.usage_count or recipe.usage_count == 0:
                    recipe.usage_count = random.randint(1, 15)
            
            # 更新点赞数缓存
            db.session.execute(models['text']("""
                UPDATE recipes 
                SET likes_count = (
                    SELECT COUNT(*) FROM recipe_likes 
                    WHERE recipe_likes.recipe_id = recipes.id
                )
            """))
            
            db.session.commit()
            
            print(f"   ✅ 创建了 {demo_likes_created} 个点赞记录")
            print(f"   ✅ 创建了 {demo_favorites_created} 个收藏记录")
            print(f"   ✅ 发布了 {len(recipes_to_publish)} 个公开食谱")
            
            return True
            
        except Exception as e:
            print(f"❌ 创建演示数据失败: {e}")
            db.session.rollback()
            return False

def show_community_stats(app, db, models):
    """显示社区统计信息"""
    print("📊 社区功能统计信息:")
    
    with app.app_context():
        try:
            # 公开食谱数量
            public_recipes = models['Recipe'].query.filter_by(
                is_public=True, 
                is_active=True
            ).count()
            
            # 活跃用户数量（发布过公开食谱的用户）
            active_users = db.session.query(models['Recipe'].user_id).filter_by(
                is_public=True, 
                is_active=True
            ).distinct().count()
            
            # 总点赞数
            total_likes = models['RecipeLike'].query.count()
            
            # 总收藏数
            total_favorites = models['RecipeFavorite'].query.count()
            
            # 最受欢迎的食谱
            popular_recipe = models['Recipe'].query.filter_by(
                is_public=True
            ).order_by(models['Recipe'].likes_count.desc()).first()
            
            print(f"   🍽️  公开食谱: {public_recipes}")
            print(f"   👥 活跃用户: {active_users}")
            print(f"   ❤️  总点赞数: {total_likes}")
            print(f"   ⭐ 总收藏数: {total_favorites}")
            
            if popular_recipe:
                print(f"   🏆 最受欢迎: '{popular_recipe.name}' ({popular_recipe.likes_count} 点赞)")
            
        except Exception as e:
            print(f"   ❌ 无法获取统计信息: {e}")

def main():
    """主函数"""
    print("🐾 宠物食谱网站 - 社区功能设置助手")
    print("=" * 50)
    
    # 设置环境
    app, db, models = setup_environment()
    
    success = True
    
    # 1. 运行数据库迁移
    if not run_community_migration(app, db, models):
        success = False
    
    # 2. 验证设置
    if success and not verify_community_setup(app, db, models):
        success = False
    
    # 3. 创建演示数据（可选）
    if success:
        create_demo_data(app, db, models)
    
    # 4. 显示统计信息
    if success:
        show_community_stats(app, db, models)
    
    print("=" * 50)
    
    if success:
        print("🎉 社区功能设置完成！")
        print("\n✨ 现在您可以:")
        print("   • 访问 /community 查看社区页面")
        print("   • 将您的食谱设为公开分享")
        print("   • 点赞和收藏其他用户的食谱")
        print("   • 在社区中发现优质食谱")
        
        print("\n🔗 快速链接:")
        print("   • 社区页面: http://localhost:5000/community")
        print("   • 用户中心: http://localhost:5000/user_center")
        print("   • 创建食谱: http://localhost:5000/recipe/create_recipe")
        
        print("\n📖 更多信息请查看 COMMUNITY_FEATURES.md")
    else:
        print("❌ 社区功能设置失败")
        print("\n🔧 请检查:")
        print("   • 数据库连接是否正常")
        print("   • 是否有足够的权限")
        print("   • 错误日志信息")
        sys.exit(1)

if __name__ == '__main__':
    main()