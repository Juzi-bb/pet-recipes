# 创建和配置Flask应用
import os
from flask import Flask
from config import Config
from .extensions import db, bcrypt, cors

def create_app(config_class=Config):
    # 添加template和static路径
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    template_path = os.path.join(project_root, 'frontend', 'templates')
    static_path = os.path.join(project_root, 'frontend', 'static')

    # 创建Flask app并指定模板目录
    app = Flask(__name__, instance_relative_config=True, template_folder=template_path, static_folder=static_path)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    bcrypt.init_app(app)
    # 在这里初始化 CORS，允许来自所有源的请求，可根据需要调整
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})

    # 注册蓝图
    from .routes.user import user_bp
    from .routes.pet import pet_bp
    # from .routes.recipe import recipe_bp # 等您实现后再取消注释

    # --------------- 修改蓝图注册，添加页面路由 ---------------
    app.register_blueprint(user_bp, url_prefix='/user')       # 页面路由
    # --------------- 结束修改 ---------------
    app.register_blueprint(pet_bp, url_prefix='/api/pets')
    # app.register_blueprint(recipe_bp, url_prefix='/api/recipes')

    # 添加main
    from .routes.main import main_bp
    app.register_blueprint(main_bp)

    return app