# 主路由文件
from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from app.models.pet_model import Pet
from app.models.user_model import User
from app.models.recipe_model import Recipe
from app.extensions import db

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    """Home Route"""
    return render_template('index.html')

@main_bp.route('/base')
def base():
    """Base Template Route (for testing)"""
    return render_template('base.html')

# 修改用户中心路由，添加登录检测和宠物数据
@main_bp.route('/user_center')
def user_center():
    """User Center Route - Login Required"""
    # 检查用户是否已登录
    if 'user_id' not in session:
        flash('Please log in before accessing the user center.', 'error')
        return redirect(url_for('user_bp.login_page'))
    
    try:
        # 获取当前用户的宠物信息
        user_id = session['user_id']
        pets = Pet.query.filter_by(user_id=user_id).all()
        
        # 将宠物信息转换为字典格式，方便模板使用
        pets_data = []
        for pet in pets:
            pet_data = {
                'id': pet.id,
                'name': pet.name,
                'species': pet.species,
                'breed': getattr(pet, 'breed', ''),  # 如果没有breed字段，返回空字符串
                'weight': pet.weight,
                'age': pet.age,
                'special_needs': pet.special_needs or 'No special needs',
                'avatar': getattr(pet, 'avatar', 'dog1.png'),  # 默认头像
                'created_at': pet.created_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(pet, 'created_at') else 'Unknown'
            }
            pets_data.append(pet_data)
        
        return render_template('user_center.html', pets=pets_data)
    
    except Exception as e:
        flash(f'Error getting pet information: {str(e)}', 'error')
        return render_template('user_center.html', pets=[])

# 修改添加宠物路由，添加登录检测
@main_bp.route('/add_pet', methods=['GET', 'POST'])
def add_pet():
    """Add Pet Route - Login Required"""
    # 检查用户是否已登录
    if 'user_id' not in session:
        flash('Please log in to add a pet profile.', 'error')
        return redirect(url_for('user_bp.login_page'))
    
    if request.method == 'POST':
        try:
            # 获取表单数据
            name = request.form.get('name')
            species = request.form.get('species')
            breed = request.form.get('breed', '')
            weight = float(request.form.get('weight'))
            age = int(request.form.get('age'))
            avatar = request.form.get('avatar', 'dog1.png')
            
            # 处理特殊需求（多选框）
            special_needs_list = request.form.getlist('special_needs')
            special_needs = ', '.join(special_needs_list) if special_needs_list else 'None'
            
            # 数据验证
            if not name or not species:
                flash('Pet name and species are required.', 'error')
                return render_template('add_pet.html')
            
            if weight < 0.5 or weight > 80:
                flash('Weight should be between 0.5 and 80 kg.', 'error')
                return render_template('add_pet.html')
            
            if age < 0 or age > 25:
                flash('Age should be between 0 and 25.', 'error')
                return render_template('add_pet.html')
            
            # 创建新宠物记录
            new_pet = Pet(
                name=name,
                species=species,
                breed=breed,
                weight=weight,
                age=age,
                special_needs=special_needs,
                avatar=avatar,
                user_id=session['user_id']
            )
            
            db.session.add(new_pet)
            db.session.commit()
            
            flash(f'Successfully added pet {name}\'s profile!', 'success')
            return redirect(url_for('main.user_center'))
            
        except ValueError as e:
            flash('Please enter a valid number.', 'error')
            return render_template('add_pet.html')
        except Exception as e:
            db.session.rollback()
            flash(f'Error adding pet: {str(e)}', 'error')
            return render_template('add_pet.html')
    
    # GET请求，显示添加宠物表单
    return render_template('add_pet.html')

# 添加编辑宠物路由
@main_bp.route('/edit_pet/<int:pet_id>', methods=['GET', 'POST'])
def edit_pet(pet_id):
    """Edit Pet Route - Login Required"""
    # 检查用户是否已登录
    if 'user_id' not in session:
        flash('Please log in to edit pet information.', 'error')
        return redirect(url_for('user_bp.login_page'))
    
    # 查找宠物记录
    pet = Pet.query.filter_by(id=pet_id, user_id=session['user_id']).first()
    if not pet:
        flash('Pet profile not found.', 'error')
        return redirect(url_for('main.user_center'))
    
    if request.method == 'POST':
        try:
            # 更新宠物信息
            pet.name = request.form.get('name')
            pet.species = request.form.get('species')
            pet.breed = request.form.get('breed', '')
            pet.weight = float(request.form.get('weight'))
            pet.age = int(request.form.get('age'))
            pet.avatar = request.form.get('avatar', pet.avatar)
            
            # 处理特殊需求
            special_needs_list = request.form.getlist('special_needs')
            pet.special_needs = ', '.join(special_needs_list) if special_needs_list else 'None'
            
            # 数据验证
            if not pet.name or not pet.species:
                flash('Pet name and species are required.', 'error')
                return render_template('edit_pet.html', pet=pet)
            
            if pet.weight < 0.5 or pet.weight > 80:
                flash('Weight should be between 0.5 and 80 kg.', 'error')
                return render_template('edit_pet.html', pet=pet)
            
            if pet.age < 0 or pet.age > 25:
                flash('Age should be between 0 and 25.', 'error')
                return render_template('edit_pet.html', pet=pet)
            
            db.session.commit()
            flash(f'Successfully updated pet {pet.name}\'s profile!', 'success')
            return redirect(url_for('main.user_center'))
            
        except ValueError as e:
            flash('Please enter a valid number.', 'error')
            return render_template('edit_pet.html', pet=pet)
        except Exception as e:
            db.session.rollback()
            flash(f'Error updating pet profile: {str(e)}', 'error')
            return render_template('edit_pet.html', pet=pet)
    
    # GET请求，显示编辑表单
    return render_template('edit_pet.html', pet=pet)

# 添加删除宠物路由
@main_bp.route('/delete_pet/<int:pet_id>')
def delete_pet(pet_id):
    """Delete Pet Route - Login Required"""
    # 检查用户是否已登录
    if 'user_id' not in session:
        flash('Please log in to delete a pet profile.', 'error')
        return redirect(url_for('user_bp.login_page'))
    
    try:
        # 查找宠物记录
        pet = Pet.query.filter_by(id=pet_id, user_id=session['user_id']).first()
        if not pet:
            flash('Pet profile not found.', 'error')
            return redirect(url_for('main.user_center'))
        
        pet_name = pet.name
        db.session.delete(pet)
        db.session.commit()
        
        flash(f'Successfully deleted pet {pet_name}\'s profile.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error deleting pet profile: {str(e)}', 'error')
    
    return redirect(url_for('main.user_center'))

# 添加登录状态检查API
@main_bp.route('/api/check_login')
def check_login():
    """API for checking user login status"""
    return {
        'logged_in': 'user_id' in session,
        'user_id': session.get('user_id'),
        'nickname': session.get('nickname')
    }

# 添加食谱相关路由
@main_bp.route('/create_recipe')
def create_recipe_redirect():
    """重定向到食谱创建页面"""
    if 'user_id' not in session:
        flash('请先登录再创建食谱')
        return redirect(url_for('user_bp.login_page'))
    return redirect(url_for('recipe_bp.create_recipe'))

@main_bp.route('/recipe/<int:recipe_id>')
def recipe_detail(recipe_id):
    """食谱详情页面"""
    if 'user_id' not in session:
        flash('请先登录')
        return redirect(url_for('user_bp.login_page'))
    
    recipe = Recipe.query.filter_by(id=recipe_id).first()
    if not recipe:
        flash('食谱不存在')
        return redirect(url_for('main.user_center'))
    
    # 检查权限 - 只有创建者或公开食谱可以查看
    if recipe.user_id != session['user_id'] and not recipe.is_public:
        flash('没有权限查看此食谱')
        return redirect(url_for('main.user_center'))
    
    return render_template('recipe_detail.html', recipe=recipe)

@main_bp.route('/my_recipes')
def my_recipes():
    """我的食谱列表"""
    if 'user_id' not in session:
        flash('请先登录')
        return redirect(url_for('user_bp.login_page'))
    
    recipes = Recipe.query.filter_by(user_id=session['user_id']).order_by(Recipe.updated_at.desc()).all()
    return render_template('my_recipes.html', recipes=recipes)

@main_bp.route('/delete_recipe/<int:recipe_id>', methods=['POST'])
def delete_recipe(recipe_id):
    """删除食谱"""
    if 'user_id' not in session:
        flash('请先登录')
        return redirect(url_for('user_bp.login_page'))
    
    recipe = Recipe.query.filter_by(id=recipe_id, user_id=session['user_id']).first()
    if not recipe:
        flash('食谱不存在')
        return redirect(url_for('main.user_center'))
    
    try:
        recipe_name = recipe.name
        db.session.delete(recipe)
        db.session.commit()
        flash(f'已删除食谱 {recipe_name}')
    except Exception as e:
        db.session.rollback()
        flash('删除失败，请重试')
    
    return redirect(url_for('main.user_center'))

# API路由用于AJAX请求
@main_bp.route('/api/pet/<int:pet_id>/info')
def api_pet_info(pet_id):
    """获取宠物信息API"""
    if 'user_id' not in session:
        return {'error': '未登录'}, 401
    
    pet = Pet.query.filter_by(id=pet_id, user_id=session['user_id']).first()
    if not pet:
        return {'error': '宠物不存在'}, 404
    
    return {
        'id': pet.id,
        'name': pet.name,
        'species': pet.species,
        'breed': pet.breed,
        'weight': pet.weight,
        'age': pet.age,
        'avatar': pet.avatar,
        'special_needs': pet.special_needs.split(',') if pet.special_needs else []
    }

@main_bp.route('/encyclopedia')
def encyclopedia():
    """食材百科页面"""
    return render_template('encyclopedia.html')

@main_bp.route('/community')
def community():
    """社区页面"""
    return render_template('community.html')
