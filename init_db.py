# --------------- 数据库初始化脚本 ---------------
# 请在项目根目录创建此文件：init_db.py

import os
import sys

# 添加项目路径到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'backend'))

from backend.app import create_app, db
from backend.app.models.user_model import User
from backend.app.models.pet_model import Pet
from backend.app.models.ingredient_model import Ingredient, IngredientCategory

def init_database():
    """初始化数据库"""
    print("Initializing database...")
    
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        try:
            # 删除所有表（如果存在）
            print("Deleting existing tables...")
            db.drop_all()
            
            # 创建所有表
            print("Creating database tables...")
            db.create_all()
            
            # 创建测试用户（可选）
            print("Creating test data...")
            test_user = User(
                username='testuser',
                nickname='Test User'
            )
            test_user.set_password('123456')
            
            db.session.add(test_user)
            db.session.commit()
            
            # 创建测试宠物（可选）
            test_pet = Pet(
                name='Da Huang',
                species='Dog',
                breed='Golden Retriever',
                weight=25.5,
                age=3,
                special_needs='No special needs',
                avatar='dog1.png',
                user_id=test_user.id
            )
            
            db.session.add(test_pet)
            db.session.commit()
            
            # 测试添加食材
            if Ingredient.query.count() == 0:
                test_ingredient = Ingredient(
                    name='鸡胸肉',
                    category=IngredientCategory.WHITE_MEAT,
                    calories=165,
                    protein=31.0,
                    fat=3.6,
                    carbohydrate=0.0,
                    is_safe_for_dogs=True,
                    is_safe_for_cats=True,
                    image_filename='chicken_breast.jpg'
                )
                db.session.add(test_ingredient)
                db.session.commit()

            print("✅ Database initialization complete！")
            print(f"✅ Test user created: username=testuser, password=123456")
            print(f"✅ Test pet created: Da Huang (Golden Retriever)")
            print(f"✅ Test ingredients created: {len(test_ingredients)} items")

        except Exception as e:
            print(f"❌ Database initialization failed：{str(e)}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    # 确保instance目录存在
    instance_dir = os.path.join(project_root, 'backend', 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    
    print("Pet Recipe Website - Database Initialization")
    print("=" * 40)
    
    if init_database():
        print("\n🎉 Initialization successful! You can now start the application.")
        print("\nStart command:")
        print("cd backend")
        print("python run.py")
        print("\nThen visit in your browser: http://localhost:5001")
        print("\nTest account:")
        print("Username: testuser")
        print("Password: 123456")
    else:
        print("\n❌ Initialization failed, please check the error message.")