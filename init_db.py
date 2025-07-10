# --------------- 数据库初始化脚本 ---------------
# 请在项目根目录创建此文件：init_db.py

import os
import sys

# 添加项目路径到Python路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, 'backend'))

from app import create_app, db
from app.models.user_model import User
from app.models.pet_model import Pet

def init_database():
    """初始化数据库"""
    print("开始初始化数据库...")
    
    # 创建应用实例
    app = create_app()
    
    with app.app_context():
        try:
            # 删除所有表（如果存在）
            print("删除现有表...")
            db.drop_all()
            
            # 创建所有表
            print("创建数据库表...")
            db.create_all()
            
            # 创建测试用户（可选）
            print("创建测试数据...")
            test_user = User(
                username='testuser',
                nickname='测试用户'
            )
            test_user.set_password('123456')
            
            db.session.add(test_user)
            db.session.commit()
            
            # 创建测试宠物（可选）
            test_pet = Pet(
                name='小黄',
                species='狗',
                breed='金毛',
                weight=25.5,
                age=3,
                special_needs='无特殊需求',
                avatar='dog1.png',
                user_id=test_user.id
            )
            
            db.session.add(test_pet)
            db.session.commit()
            
            print("✅ 数据库初始化完成！")
            print(f"✅ 创建测试用户：用户名=testuser，密码=123456")
            print(f"✅ 创建测试宠物：小黄（金毛犬）")
            
        except Exception as e:
            print(f"❌ 数据库初始化失败：{str(e)}")
            db.session.rollback()
            return False
    
    return True

if __name__ == '__main__':
    # 确保instance目录存在
    instance_dir = os.path.join(project_root, 'backend', 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    
    print("宠物食谱网站 - 数据库初始化")
    print("=" * 40)
    
    if init_database():
        print("\n🎉 初始化成功！您现在可以启动应用了。")
        print("\n启动命令：")
        print("cd backend")
        print("python run.py")
        print("\n然后在浏览器访问：http://localhost:5001")
        print("\n测试账号：")
        print("用户名: testuser")
        print("密码: 123456")
    else:
        print("\n❌ 初始化失败，请检查错误信息。")