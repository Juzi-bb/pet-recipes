"""
路由模块初始化文件
整合所有功能路由
"""

from flask import Blueprint, render_template

# 导入所有路由蓝图
from .nutrition_api import nutrition_api_bp
from .recipe_recommendation_api import recommendation_api_bp
from .allergen_api import allergen_api_bp
from .recipe_save_api import recipe_save_api_bp
from .user import user_bp
from .recipe import recipe_bp
from .recipe_detail_api import recipe_detail_bp
from .favorite_api import favorite_api

# 创建主要的路由蓝图
main_bp = Blueprint('main', __name__)

def register_routes(app):
    """注册所有路由到Flask应用"""
    
    # 注册API路由蓝图
    app.register_blueprint(nutrition_api_bp)
    app.register_blueprint(recommendation_api_bp)
    app.register_blueprint(allergen_api_bp)
    app.register_blueprint(recipe_save_api_bp)
    app.register_blueprint(recipe_detail_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(recipe_bp)
    app.register_blueprint(favorite_api)
    
    # 注册主要功能路由
    app.register_blueprint(main_bp)
    
    print("所有路由已注册完成")

# 主要页面路由
@main_bp.route('/')
def index():
    """首页"""
    return render_template('index.html')

@main_bp.route('/create-recipe')
def create_recipe():
    """创建食谱页面"""
    from flask import session, redirect, url_for, flash
    from app.models.pet_model import Pet
    
    if 'user_id' not in session:
        flash('请先登录后再创建食谱')
        return redirect(url_for('user.login'))
    
    # 获取用户的宠物
    user_pets = Pet.query.filter_by(user_id=session['user_id']).all()
    if not user_pets:
        flash('请先添加宠物信息再创建食谱')
        return redirect(url_for('pet.add_pet'))
    
    return render_template('create_recipe.html', pets=user_pets)
