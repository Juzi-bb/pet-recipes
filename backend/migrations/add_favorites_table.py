# 数据库迁移脚本
import sqlite3
import os
import sys

# 添加项目根目录到路径，以便导入配置
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_database_path():
    """获取数据库文件路径"""
    # 根据您的项目结构调整路径
    possible_paths = [
        os.path.join('backend', 'instance', 'pet_recipes.db'),
        os.path.join('backend', 'app', 'db', 'pet_recipes.db'),
        os.path.join('instance', 'pet_recipes.db'),
        'pet_recipes.db'
    ]
    
    for path in possible_paths:
        if os.path.exists(path):
            print(f"📍 找到数据库文件: {path}")
            return path
    
    # 如果都不存在，尝试创建instance目录并使用默认路径
    instance_dir = 'instance'
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)
        print(f"📁 创建实例目录: {instance_dir}")
    
    default_path = os.path.join(instance_dir, 'pet_recipes.db')
    print(f"📍 使用默认数据库路径: {default_path}")
    return default_path

def check_table_exists(cursor, table_name):
    """检查表是否已存在"""
    cursor.execute('''
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name=?
    ''', (table_name,))
    return cursor.fetchone() is not None

def add_favorites_table():
    """添加收藏功能表"""
    db_path = get_database_path()
    
    if not os.path.exists(db_path):
        print(f"❌ 数据库文件不存在: {db_path}")
        print("请先运行主数据库初始化脚本")
        return False
    
    print(f"📍 使用数据库: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # 检查表是否已存在
        if check_table_exists(cursor, 'user_recipe_favorites'):
            print("ℹ️  收藏表已存在，跳过创建")
            return True
        
        print("🔄 开始创建收藏功能表...")
        
        # 创建用户食谱收藏表
        cursor.execute('''
            CREATE TABLE user_recipe_favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                recipe_id INTEGER NOT NULL,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                FOREIGN KEY (recipe_id) REFERENCES recipes(id) ON DELETE CASCADE,
                UNIQUE(user_id, recipe_id)
            )
        ''')
        
        # 创建索引
        print("🔄 创建索引...")
        
        cursor.execute('''
            CREATE INDEX idx_user_recipe_favorites_user_id 
            ON user_recipe_favorites(user_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX idx_user_recipe_favorites_recipe_id 
            ON user_recipe_favorites(recipe_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX idx_user_recipe_favorites_created_at 
            ON user_recipe_favorites(created_at)
        ''')
        
        conn.commit()
        
        # 验证表创建成功
        if check_table_exists(cursor, 'user_recipe_favorites'):
            print("✅ 收藏功能表创建成功！")
            
            # 显示表结构
            cursor.execute("PRAGMA table_info(user_recipe_favorites)")
            columns = cursor.fetchall()
            print("\n📋 表结构:")
            for col in columns:
                print(f"   - {col[1]} ({col[2]})")
            
            return True
        else:
            print("❌ 表创建验证失败")
            return False
            
    except Exception as e:
        print(f"❌ 创建收藏表时出错: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def rollback_favorites_table():
    """回滚收藏功能表（如果需要的话）"""
    db_path = get_database_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        if check_table_exists(cursor, 'user_recipe_favorites'):
            cursor.execute('DROP TABLE user_recipe_favorites')
            conn.commit()
            print("✅ 收藏表已删除")
        else:
            print("ℹ️  收藏表不存在，无需删除")
    except Exception as e:
        print(f"❌ 删除收藏表时出错: {e}")
    finally:
        conn.close()

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='收藏功能数据库迁移')
    parser.add_argument('--rollback', action='store_true', help='回滚迁移')
    args = parser.parse_args()
    
    if args.rollback:
        print("🔄 开始回滚收藏功能迁移...")
        rollback_favorites_table()
    else:
        print("🚀 开始收藏功能数据库迁移...")
        success = add_favorites_table()
        if success:
            print("\n🎉 迁移完成！现在可以使用收藏功能了。")
        else:
            print("\n💥 迁移失败，请检查错误信息。")