# backend/reset_database.py
"""
数据库重置脚本
重新初始化食材库和预设食谱
"""
import os
import sys

def reset_database():
    """重置整个数据库"""
    print("🔄 Starting database reset...")
    
    # 删除数据库文件
    db_path = "instance/pet_recipes.db"
    if os.path.exists(db_path):
        os.remove(db_path)
        print("🗑️ Removed existing database")
    
    # 重新初始化食材库
    print("📝 Initializing ingredient database...")
    os.system("python init_nutrition_data.py")
    
    # 重新初始化预设食谱
    print("🍽️ Initializing preset recipes...")
    os.system("python init_preset_recipes.py")
    
    print("✅ Database reset completed!")
    print("\nYou can now start the application:")
    print("python run.py")

if __name__ == "__main__":
    confirm = input("⚠️ This will delete all existing data! Continue? (y/N): ")
    if confirm.lower() == 'y':
        reset_database()
    else:
        print("❌ Operation cancelled")