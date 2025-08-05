"""
食材百科页面路由
提供食材百科页面的渲染
"""

from flask import Blueprint, render_template, request, session, redirect, url_for
from app.models.ingredient_model import Ingredient
from app.extensions import db

ingredient_pages_bp = Blueprint('ingredient_pages', __name__)

@ingredient_pages_bp.route('/encyclopedia')
def encyclopedia():
    """食材百科主页面"""
    return render_template('ingredient_encyclopedia.html')

@ingredient_pages_bp.route('/ingredient/<int:ingredient_id>')
def ingredient_detail(ingredient_id):
    """食材详情页面"""
    # 检查食材是否存在
    ingredient = Ingredient.query.filter_by(id=ingredient_id, is_active=True).first()
    if not ingredient:
        return render_template('404.html'), 404
    
    return render_template('ingredient_detail.html', ingredient=ingredient)