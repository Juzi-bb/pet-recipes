"""
过敏食材管理服务
"""

from typing import List, Dict, Set
from datetime import datetime
from app.models.pet_model import Pet
from app.models.ingredient_model import Ingredient, IngredientCategory
from app.models.pet_allergen_model import PetAllergen
from app.extensions import db

class AllergenService:
    """过敏食材管理服务类"""
    
    @staticmethod
    def add_pet_allergen(pet_id: int, ingredient_id: int, severity: str = 'mild', 
                        notes: str = None, confirmed_date = None) -> bool:
        """为宠物添加过敏食材"""
        try:
            # 检查是否已存在
            existing = PetAllergen.query.filter_by(
                pet_id=pet_id, 
                ingredient_id=ingredient_id
            ).first()
            
            if existing:
                # 更新现有记录
                existing.severity = severity
                existing.notes = notes
                existing.confirmed_date = confirmed_date
                existing.updated_at = datetime.utcnow()
            else:
                # 创建新记录
                allergen = PetAllergen(
                    pet_id=pet_id,
                    ingredient_id=ingredient_id,
                    severity=severity,
                    notes=notes,
                    confirmed_date=confirmed_date
                )
                db.session.add(allergen)
            
            db.session.commit()
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"添加过敏食材失败: {e}")
            return False
    
    @staticmethod
    def remove_pet_allergen(pet_id: int, ingredient_id: int) -> bool:
        """移除宠物的过敏食材"""
        try:
            allergen = PetAllergen.query.filter_by(
                pet_id=pet_id,
                ingredient_id=ingredient_id
            ).first()
            
            if allergen:
                db.session.delete(allergen)
                db.session.commit()
                return True
            return False
            
        except Exception as e:
            db.session.rollback()
            print(f"移除过敏食材失败: {e}")
            return False
    
    @staticmethod
    def get_pet_allergens(pet_id: int) -> List[Dict]:
        """获取宠物的所有过敏食材"""
        try:
            allergens = PetAllergen.query.filter_by(pet_id=pet_id).all()
            return [allergen.to_dict() for allergen in allergens]
        except Exception as e:
            print(f"获取过敏食材失败: {e}")
            return []
    
    @staticmethod
    def get_pet_allergen_ids(pet_id: int) -> Set[int]:
        """获取宠物过敏食材的ID集合"""
        try:
            allergens = PetAllergen.query.filter_by(pet_id=pet_id).all()
            return {allergen.ingredient_id for allergen in allergens}
        except Exception as e:
            print(f"获取过敏食材ID失败: {e}")
            return set()
    
    @staticmethod
    def filter_safe_ingredients(ingredient_ids: List[int], pet_id: int) -> List[int]:
        """过滤掉宠物过敏的食材"""
        if not pet_id:
            return ingredient_ids
        
        try:
            allergen_ids = AllergenService.get_pet_allergen_ids(pet_id)
            return [id for id in ingredient_ids if id not in allergen_ids]
        except Exception as e:
            print(f"过滤过敏食材失败: {e}")
            return ingredient_ids
    
    @staticmethod
    def get_common_allergens_by_category() -> Dict[str, List[Dict]]:
        """获取按分类组织的常见过敏食材"""
        try:
            # 查询标记为常见过敏原的食材
            common_allergens = Ingredient.query.filter_by(
                is_common_allergen=True,
                is_active=True
            ).all()
            
            allergens_by_category = {}
            for ingredient in common_allergens:
                category = ingredient.category.value
                if category not in allergens_by_category:
                    allergens_by_category[category] = []
                
                allergens_by_category[category].append({
                    'id': ingredient.id,
                    'name': ingredient.name,
                    'name_en': ingredient.name_en,
                    'description': getattr(ingredient, 'description', ''),
                    'allergy_alert': getattr(ingredient, 'allergy_alert', '')
                })
            
            return allergens_by_category
            
        except Exception as e:
            print(f"获取常见过敏食材失败: {e}")
            return {}
    
    @staticmethod
    def check_recipe_safety(recipe_ingredient_ids: List[int], pet_id: int) -> Dict:
        """检查食谱对宠物的安全性"""
        try:
            if not pet_id:
                return {'is_safe': True, 'allergens': [], 'warnings': []}
            
            allergen_ids = AllergenService.get_pet_allergen_ids(pet_id)
            dangerous_ingredients = []
            warnings = []
            
            # 检查每个食材
            for ingredient_id in recipe_ingredient_ids:
                if ingredient_id in allergen_ids:
                    # 获取过敏详情
                    allergen = PetAllergen.query.filter_by(
                        pet_id=pet_id,
                        ingredient_id=ingredient_id
                    ).first()
                    
                    if allergen:
                        dangerous_ingredients.append({
                            'ingredient_id': ingredient_id,
                            'ingredient_name': allergen.ingredient.name,
                            'severity': allergen.severity,
                            'notes': allergen.notes
                        })
                        
                        # 根据严重程度生成警告
                        if allergen.severity == 'severe':
                            warnings.append(f"严重过敏: {allergen.ingredient.name}")
                        elif allergen.severity == 'moderate':
                            warnings.append(f"中度过敏: {allergen.ingredient.name}")
                        else:
                            warnings.append(f"轻微过敏: {allergen.ingredient.name}")
            
            return {
                'is_safe': len(dangerous_ingredients) == 0,
                'allergens': dangerous_ingredients,
                'warnings': warnings
            }
            
        except Exception as e:
            print(f"检查食谱安全性失败: {e}")
            return {'is_safe': True, 'allergens': [], 'warnings': []}
    
    @staticmethod
    def get_allergen_statistics(pet_id: int) -> Dict:
        """获取宠物过敏统计信息"""
        try:
            allergens = PetAllergen.query.filter_by(pet_id=pet_id).all()
            
            stats = {
                'total_count': len(allergens),
                'by_severity': {'mild': 0, 'moderate': 0, 'severe': 0},
                'by_category': {},
                'recent_additions': []
            }
            
            # 按严重程度统计
            for allergen in allergens:
                stats['by_severity'][allergen.severity] += 1
                
                # 按分类统计
                category = allergen.ingredient.category.value
                if category not in stats['by_category']:
                    stats['by_category'][category] = 0
                stats['by_category'][category] += 1
            
            # 最近添加的过敏食材（7天内）
            from datetime import datetime, timedelta
            recent_date = datetime.utcnow() - timedelta(days=7)
            recent_allergens = [a for a in allergens if a.created_at >= recent_date]
            
            stats['recent_additions'] = [
                {
                    'ingredient_name': a.ingredient.name,
                    'severity': a.severity,
                    'added_date': a.created_at.isoformat()
                }
                for a in recent_allergens
            ]
            
            return stats
            
        except Exception as e:
            print(f"获取过敏统计失败: {e}")
            return {'total_count': 0, 'by_severity': {}, 'by_category': {}, 'recent_additions': []}
