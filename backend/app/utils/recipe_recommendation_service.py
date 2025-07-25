"""
食谱推荐算法服务
基于食材相似性和营养匹配度推荐食谱
"""

import math
from typing import List, Dict, Tuple, Set
from collections import defaultdict
from app.models.ingredient_model import Ingredient, IngredientCategory
from app.models.recipe_model import Recipe
from app.models.recipe_ingredient_model import RecipeIngredient
from app.models.pet_model import Pet
from app.utils.nutrition_ratio_config import NutritionRatioService, NutritionProfile
from app.extensions import db

class RecipeRecommendationService:
    """食谱推荐服务类"""
    
    def __init__(self):
        self.nutrition_service = NutritionRatioService()
    
    def get_recommendations(self,
                        selected_ingredient_ids: List[int],
                        pet_id: int = None,
                        exclude_allergens: List[int] = None,
                        limit: int = 2) -> List[Dict]:
        """
        获取食谱推荐
        
        Args:
            selected_ingredient_ids: 用户选择的食材ID列表
            pet_id: 宠物ID（用于获取过敏信息）
            exclude_allergens: 需要排除的过敏食材ID列表
            limit: 返回推荐数量限制
            
        Returns:
            推荐食谱列表
        """
        try:
            # 获取宠物信息和过敏食材
            pet = None
            allergen_ids = set(exclude_allergens or [])
            
            if pet_id:
                pet = Pet.query.get(pet_id)
                if pet and pet.special_needs:
                    # 解析过敏食材（假设存储格式为 "过敏:食材ID1,食材ID2"）
                    allergen_ids.update(self._extract_allergen_ids(pet.special_needs))
            
            # 获取用户选择的食材信息
            selected_ingredients = Ingredient.query.filter(
                Ingredient.id.in_(selected_ingredient_ids)
            ).all()
            
            if not selected_ingredients:
                return []
            
            # 获取候选食谱（排除包含过敏食材的食谱）
            candidate_recipes = self._get_candidate_recipes(allergen_ids)
            
            # 计算推荐分数
            recommendations = []
            for recipe in candidate_recipes:
                score_data = self._calculate_recommendation_score(
                    recipe, selected_ingredients, pet
                )
                
                if score_data['total_score'] > 0.3:  # 最低分数阈值
                    recommendations.append({
                        'recipe': recipe,
                        'score_data': score_data,
                        'total_score': score_data['total_score']
                    })
            
            # 按分数排序并限制数量
            recommendations.sort(key=lambda x: x['total_score'], reverse=True)
            recommendations = recommendations[:limit]
            
            # 格式化返回结果
            return [self._format_recommendation(rec) for rec in recommendations]
            
        except Exception as e:
            print(f"推荐算法错误: {e}")
            return []
    
    def _get_candidate_recipes(self, allergen_ids: Set[int]) -> List[Recipe]:
        """获取候选食谱（排除过敏食材）"""
        query = db.session.query(Recipe).filter(
            Recipe.status == 'published',
            Recipe.is_public == True,
            Recipe.total_weight > 0  # 确保食谱有实际内容
        )
        
        # 排除包含过敏食材的食谱
        if allergen_ids:
            subquery = db.session.query(RecipeIngredient.recipe_id).filter(
                RecipeIngredient.ingredient_id.in_(allergen_ids)
            ).subquery()
            
            query = query.filter(~Recipe.id.in_(subquery))
        
        return query.limit(50).all()  # 限制候选数量以提高性能
    
    def _calculate_recommendation_score(self,
                                    recipe: Recipe, 
                                    selected_ingredients: List[Ingredient],
                                    pet: Pet = None) -> Dict:
        """
        计算推荐分数
        
        权重分配：
        - 食材相似性：40%
        - 营养匹配度：35%
        - 宠物适用性：25%
        """
        # 1. 食材相似性分数 (40%)
        ingredient_similarity = self._calculate_ingredient_similarity(
            recipe, selected_ingredients
        )
        
        # 2. 营养匹配度分数 (35%)
        nutrition_match = self._calculate_nutrition_match(recipe, pet)
        
        # 3. 宠物适用性分数 (25%)
        pet_suitability = self._calculate_pet_suitability(recipe, pet)
        
        # 计算加权总分
        total_score = (
            ingredient_similarity * 0.40 +
            nutrition_match * 0.35 +
            pet_suitability * 0.25
        )
        
        return {
            'ingredient_similarity': ingredient_similarity,
            'nutrition_match': nutrition_match,
            'pet_suitability': pet_suitability,
            'total_score': total_score
        }
    
    def _calculate_ingredient_similarity(self, 
                                    recipe: Recipe, 
                                    selected_ingredients: List[Ingredient]) -> float:
        """计算食材相似性分数"""
        if not selected_ingredients:
            return 0.0
        
        # 获取食谱中的食材
        recipe_ingredients = [ri.ingredient for ri in recipe.ingredients]
        
        if not recipe_ingredients:
            return 0.0
        
        # 1. 直接匹配分数（共同食材）
        selected_ids = {ing.id for ing in selected_ingredients}
        recipe_ids = {ing.id for ing in recipe_ingredients}
        common_ingredients = selected_ids.intersection(recipe_ids)
        
        direct_match_score = len(common_ingredients) / len(selected_ids)
        
        # 2. 分类相似性分数
        category_similarity = self._calculate_category_similarity(
            selected_ingredients, recipe_ingredients
        )
        
        # 3. 营养特征相似性
        nutrition_similarity = self._calculate_nutrition_feature_similarity(
            selected_ingredients, recipe_ingredients
        )
        
        # 综合相似性分数
        similarity_score = (
            direct_match_score * 0.5 +      # 直接匹配权重最高
            category_similarity * 0.3 +      # 分类相似性
            nutrition_similarity * 0.2       # 营养特征相似性
        )
        
        return min(similarity_score, 1.0)
    
    def _calculate_category_similarity(self, 
                                    selected_ingredients: List[Ingredient],
                                    recipe_ingredients: List[Ingredient]) -> float:
        """计算食材分类相似性"""
        selected_categories = defaultdict(int)
        recipe_categories = defaultdict(int)
        
        # 统计分类分布
        for ing in selected_ingredients:
            selected_categories[ing.category.value] += 1
        
        for ing in recipe_ingredients:
            recipe_categories[ing.category.value] += 1
        
        # 计算分类向量的余弦相似度
        all_categories = set(selected_categories.keys()) | set(recipe_categories.keys())
        
        if not all_categories:
            return 0.0
        
        # 构建向量
        selected_vector = [selected_categories[cat] for cat in all_categories]
        recipe_vector = [recipe_categories[cat] for cat in all_categories]
        
        # 计算余弦相似度
        return self._cosine_similarity(selected_vector, recipe_vector)
    
    def _calculate_nutrition_feature_similarity(self,
                                            selected_ingredients: List[Ingredient],
                                            recipe_ingredients: List[Ingredient]) -> float:
        """计算营养特征相似性"""
        # 计算选择食材的平均营养特征
        selected_features = self._get_average_nutrition_features(selected_ingredients)
        recipe_features = self._get_average_nutrition_features(recipe_ingredients)
        
        if not selected_features or not recipe_features:
            return 0.0
        
        # 计算特征向量的余弦相似度
        selected_vector = list(selected_features.values())
        recipe_vector = list(recipe_features.values())
        
        return self._cosine_similarity(selected_vector, recipe_vector)
    
    def _get_average_nutrition_features(self, ingredients: List[Ingredient]) -> Dict:
        """获取食材的平均营养特征"""
        if not ingredients:
            return {}
        
        total_features = {
            'protein': 0.0,
            'fat': 0.0,
            'carbohydrate': 0.0,
            'calories': 0.0,
            'calcium': 0.0,
            'phosphorus': 0.0
        }
        
        for ing in ingredients:
            total_features['protein'] += ing.protein or 0
            total_features['fat'] += ing.fat or 0
            total_features['carbohydrate'] += ing.carbohydrate or 0
            total_features['calories'] += ing.calories or 0
            total_features['calcium'] += ing.calcium or 0
            total_features['phosphorus'] += ing.phosphorus or 0
        
        # 计算平均值
        count = len(ingredients)
        return {key: value / count for key, value in total_features.items()}
    
    def _calculate_nutrition_match(self, recipe: Recipe, pet: Pet = None) -> float:
        """计算营养匹配度分数"""
        if not pet:
            return 0.5  # 没有宠物信息时给予中等分数
        
        # 获取宠物的营养需求
        pet_type = 'dog' if pet.species.lower() == 'dog' else 'cat'
        
        # 根据宠物信息选择合适的营养方案
        suitable_profiles = self.nutrition_service.get_suitable_plans(
            pet.species, pet.age, self._parse_special_needs(pet.special_needs)
        )
        
        if not suitable_profiles:
            return 0.5
        
        # 使用第一个推荐方案作为标准
        target_plan = self.nutrition_service.get_plan(suitable_profiles[0])
        if not target_plan:
            return 0.5
        
        # 计算食谱营养比例
        if recipe.total_weight <= 0:
            return 0.0
        
        recipe_ratios = {
            'protein_percent': (recipe.total_protein / recipe.total_weight) * 100,
            'fat_percent': (recipe.total_fat / recipe.total_weight) * 100,
            'carb_percent': (recipe.total_carbohydrate / recipe.total_weight) * 100
        }
        
        # 计算与目标的匹配程度
        target_nutrition = target_plan.nutrition_targets
        
        protein_match = self._calculate_range_match(
            recipe_ratios['protein_percent'],
            target_nutrition.protein_min,
            target_nutrition.protein_max
        )
        
        fat_match = self._calculate_range_match(
            recipe_ratios['fat_percent'],
            target_nutrition.fat_min,
            target_nutrition.fat_max
        )
        
        carb_match = 1.0 if recipe_ratios['carb_percent'] <= target_nutrition.carb_max else 0.5
        
        # 综合营养匹配分数
        nutrition_score = (protein_match + fat_match + carb_match) / 3
        
        return nutrition_score
    
    def _calculate_pet_suitability(self, recipe: Recipe, pet: Pet = None) -> float:
        """计算宠物适用性分数"""
        if not pet:
            return 0.8  # 没有宠物信息时给予较高基础分数
        
        suitability_score = 0.0
        
        # 基础适用性检查
        if pet.species.lower() == 'dog' and recipe.suitable_for_dogs:
            suitability_score += 0.4
        elif pet.species.lower() == 'cat' and recipe.suitable_for_cats:
            suitability_score += 0.4
        
        # 年龄适用性检查
        if pet.age < 1:  # 幼体
            if (pet.species.lower() == 'dog' and recipe.suitable_for_puppies) or \
                (pet.species.lower() == 'cat' and recipe.suitable_for_kittens):
                suitability_score += 0.3
        elif pet.age >= 7:  # 老年
            if recipe.suitable_for_seniors:
                suitability_score += 0.3
        else:  # 成年
            suitability_score += 0.3
        
        # 特殊需求适用性
        if pet.special_needs:
            special_match = self._check_special_needs_match(recipe, pet.special_needs)
            suitability_score += special_match * 0.3
        else:
            suitability_score += 0.3
        
        return min(suitability_score, 1.0)
    
    def _calculate_range_match(self, value: float, min_val: float, max_val: float) -> float:
        """计算数值与目标范围的匹配程度"""
        if min_val <= value <= max_val:
            return 1.0  # 完全匹配
        elif value < min_val:
            # 低于最小值的惩罚
            ratio = value / min_val if min_val > 0 else 0
            return max(ratio, 0.0)
        else:
            # 高于最大值的惩罚
            if max_val > 0:
                excess_ratio = (value - max_val) / max_val
                return max(1.0 - excess_ratio * 0.5, 0.0)
            return 0.5
    
    def _check_special_needs_match(self, recipe: Recipe, special_needs: str) -> float:
        """检查特殊需求匹配度"""
        if not special_needs:
            return 1.0
        
        needs = special_needs.lower()
        match_score = 0.0
        
        # 根据特殊需求检查食谱适用性
        if '减重' in needs or '肥胖' in needs:
            # 检查是否为低热量、高蛋白配方
            if recipe.total_weight > 0:
                calories_per_100g = (recipe.total_calories / recipe.total_weight) * 100
                protein_percent = (recipe.total_protein / recipe.total_weight) * 100
                
                if calories_per_100g < 300 and protein_percent >= 20:
                    match_score += 0.8
        
        if '肾' in needs:
            # 检查是否为低蛋白、低磷配方
            if recipe.total_weight > 0:
                protein_percent = (recipe.total_protein / recipe.total_weight) * 100
                if protein_percent < 20:
                    match_score += 0.7
        
        if '美毛' in needs:
            # 检查是否含有丰富的omega脂肪酸
            if recipe.total_omega_3 > 0 or recipe.total_omega_6 > 0:
                match_score += 0.8
        
        return min(match_score, 1.0) if match_score > 0 else 0.5
    
    def _cosine_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """计算两个向量的余弦相似度"""
        if len(vector1) != len(vector2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vector1, vector2))
        magnitude1 = math.sqrt(sum(a * a for a in vector1))
        magnitude2 = math.sqrt(sum(b * b for b in vector2))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _extract_allergen_ids(self, special_needs: str) -> Set[int]:
        """从特殊需求字符串中提取过敏食材ID"""
        allergen_ids = set()
        
        if not special_needs:
            return allergen_ids
        
        # 解析过敏信息（假设格式为 "过敏:海鲜,坚果" 或包含食材ID）
        needs_lower = special_needs.lower()
        
        if '过敏' in needs_lower:
            # 这里可以根据实际存储格式来解析
            # 简单示例：查找已知过敏食材
            allergen_keywords = {
                '海鲜': ['三文鱼', '鳕鱼', '金枪鱼'],
                '坚果': ['核桃', '杏仁'],
                '乳制品': ['牛奶', '奶酪', '酸奶'],
                '鸡蛋': ['鸡蛋'],
                '牛肉': ['牛肉']
            }
            
            for allergen_type, ingredient_names in allergen_keywords.items():
                if allergen_type in needs_lower:
                    # 查找对应的食材ID
                    ingredients = Ingredient.query.filter(
                        Ingredient.name.in_(ingredient_names)
                    ).all()
                    allergen_ids.update(ing.id for ing in ingredients)
        
        return allergen_ids
    
    def _parse_special_needs(self, special_needs: str) -> List[str]:
        """解析特殊需求为列表"""
        if not special_needs:
            return []
        
        # 简单的解析逻辑，根据逗号分割
        return [need.strip() for need in special_needs.split(',') if need.strip()]
    
    def _format_recommendation(self, recommendation: Dict) -> Dict:
        """格式化推荐结果"""
        recipe = recommendation['recipe']
        score_data = recommendation['score_data']
        
        # 获取食材信息
        ingredients_info = []
        for ri in recipe.ingredients:
            ingredients_info.append({
                'id': ri.ingredient.id,
                'name': ri.ingredient.name,
                'category': ri.ingredient.category.value,
                'weight': ri.weight,
                'percentage': round((ri.weight / recipe.total_weight) * 100, 1) if recipe.total_weight > 0 else 0
            })
        
        # 计算营养比例
        nutrition_ratios = {}
        if recipe.total_weight > 0:
            nutrition_ratios = {
                'protein_percent': round((recipe.total_protein / recipe.total_weight) * 100, 1),
                'fat_percent': round((recipe.total_fat / recipe.total_weight) * 100, 1),
                'carb_percent': round((recipe.total_carbohydrate / recipe.total_weight) * 100, 1),
                'calories_per_100g': round((recipe.total_calories / recipe.total_weight) * 100, 1)
            }
        
        return {
            'recipe_id': recipe.id,
            'name': recipe.name,
            'description': recipe.description,
            'total_weight': recipe.total_weight,
            'total_calories': recipe.total_calories,
            'ingredients': ingredients_info,
            'nutrition_ratios': nutrition_ratios,
            'recommendation_score': round(recommendation['total_score'], 3),
            'score_breakdown': {
                'ingredient_similarity': round(score_data['ingredient_similarity'], 3),
                'nutrition_match': round(score_data['nutrition_match'], 3),
                'pet_suitability': round(score_data['pet_suitability'], 3)
            },
            'match_highlights': self._generate_match_highlights(score_data)
        }
    
    def _generate_match_highlights(self, score_data: Dict) -> List[str]:
        """生成匹配亮点说明"""
        highlights = []
        
        if score_data['ingredient_similarity'] > 0.7:
            highlights.append("食材选择高度匹配")
        elif score_data['ingredient_similarity'] > 0.4:
            highlights.append("食材类型相似")
        
        if score_data['nutrition_match'] > 0.8:
            highlights.append("营养配比优秀")
        elif score_data['nutrition_match'] > 0.6:
            highlights.append("营养搭配合理")
        
        if score_data['pet_suitability'] > 0.8:
            highlights.append("非常适合您的宠物")
        elif score_data['pet_suitability'] > 0.6:
            highlights.append("适合您的宠物")
        
        return highlights