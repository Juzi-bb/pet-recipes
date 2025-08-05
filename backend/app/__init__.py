# 创建和配置Flask应用
import os
import sys
from flask import Flask

# 添加backend目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.dirname(current_dir)
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# 现在可以使用绝对导入
from config import Config
from app.extensions import db, bcrypt, cors

def create_app(config_class=Config):
    # 添加template和static路径
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    template_path = os.path.join(project_root, 'frontend', 'templates')
    static_path = os.path.join(project_root, 'frontend', 'static')

    # 创建Flask app并指定模板目录
    app = Flask(__name__, instance_relative_config=True, template_folder=template_path, static_folder=static_path)
    
    # 修复：固定数据库文件路径
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 放在backend/instance目录下
    instance_dir = os.path.join(backend_dir, '..', 'instance')
    os.makedirs(instance_dir, exist_ok=True)
    database_path = os.path.join(instance_dir, 'pet_recipes.db')

    app.config['SECRET_KEY'] = 'your-secret-key-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pet_recipes.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 添加调试信息
    print(f"数据库文件路径: {database_path}")
    print(f"数据库文件存在: {os.path.exists(database_path)}")

    # 初始化扩展
    db.init_app(app)
    bcrypt.init_app(app)
    # 在这里初始化 CORS，允许来自所有源的请求，可根据需要调整
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # 导入模型（重要！确保数据库表被创建）
    from .models import (
        user_model,
        pet_model,
        ingredient_model,
        recipe_model,
        nutrition_requirements_model,
        recipe_ingredient_model,
        pet_allergen_model,
        recipe_favorite_model,
        recipe_like_model
    )

    # 创建数据库表
    with app.app_context():
        # 检查是否是首次运行
        if not os.path.exists(database_path):
            print("首次运行，创建数据库表...")
        else:
            print("数据库文件已存在，检查表结构...")

        db.create_all()

        # 显示用户数量
        try:
            from .models.user_model import User
            user_count = User.query.count()
            print(f"当前用户数量: {user_count}")
        except Exception as e:
            print(f"查询用户失败: {e}")

    # 注册蓝图
    from .routes.user import user_bp
    from .routes.pet import pet_bp
    from .routes.recipe import recipe_bp
    from .routes.main import main_bp
    from .routes.recipe_recommendation_api import recommendation_api_bp
    from .routes.recipe_save_api import recipe_save_api_bp
    from .routes.nutrition_api import nutrition_api_bp
    from .routes.favorite_api import favorite_api
    from .routes.recipe_detail_api import recipe_detail_bp
    from .routes.ingredient_encyclopedia import ingredient_encyclopedia_bp
    from .routes.ingredient_pages import ingredient_pages_bp
    from .routes.community_api import community_api

    # 修复：条件性导入 allergen_api
    try:
        from .routes.allergen_api import allergen_api_bp
        ALLERGEN_API_AVAILABLE = True
    except ImportError:
        print("Warning: allergen_api not available")
        ALLERGEN_API_AVAILABLE = False

    # 修改蓝图注册，添加页面路由
    app.register_blueprint(user_bp, url_prefix='/user')       # 页面路由
    app.register_blueprint(pet_bp, url_prefix='/api/pets')
    app.register_blueprint(recipe_bp, url_prefix='/recipe')
    app.register_blueprint(recommendation_api_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(nutrition_api_bp)
    app.register_blueprint(recipe_save_api_bp)
    app.register_blueprint(favorite_api)
    app.register_blueprint(recipe_detail_bp)
    app.register_blueprint(ingredient_encyclopedia_bp)
    app.register_blueprint(ingredient_pages_bp)
    app.register_blueprint(community_api)
    
    # 修复：条件性注册 allergen_api
    if ALLERGEN_API_AVAILABLE:
        app.register_blueprint(allergen_api_bp)

    return app
