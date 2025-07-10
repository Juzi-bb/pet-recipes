# 需要JWT认证才能访问的示例路由
from flask import Blueprint, jsonify, request, session
from app.models.pet_model import Pet
from app import db

pet_bp = Blueprint('pet_bp', __name__)

# 这是一个示例路由，您需要添加 JWT 认证装饰器来保护它
# 并且实现完整的 CRUD 逻辑
@pet_bp.route('/add_pet', methods=['POST'])

def add_pet():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401
    
    data = request.get_json()
    user_id = session['user_id']
    
    new_pet = Pet(
        name=data['name'],
        species=data['species'],
        age=data['age'],
        weight=data['weight'],
        user_id=user_id
    )
    
    db.session.add(new_pet)
    db.session.commit()
    
    return jsonify({"message": "Pet added successfully"}), 201


@pet_bp.route('/get_pets', methods=['GET'])
def get_pets():
    if 'user_id' not in session:
        return jsonify({"message": "Unauthorized"}), 401
        
    user_id = session['user_id']
    pets = Pet.query.filter_by(user_id=user_id).all()
    
    return jsonify([{
        "name": pet.name,
        "species": pet.species,
        "age": pet.age,
        "weight": pet.weight
    } for pet in pets]), 200