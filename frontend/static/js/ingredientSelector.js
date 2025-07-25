/**
 * 食材选择器
 * 处理食材加载、展示和选择功能
 */

class IngredientSelector {
    constructor() {
        this.ingredients = [];
        this.currentCategory = 'all';
        this.selectedIngredients = new Set();
        this.allergenIds = new Set(); // 新增：过敏食材ID集合
        
        this.init();
    }
    
    init() {
        this.loadIngredients();
        this.bindEvents();
        this.bindAllergenEvents(); // 新增：绑定过敏食材相关事件
    }
    
    bindEvents() {
        // 食材卡片点击事件
        $(document).on('click', '.ingredient-card', (e) => {
            if (e.target.type === 'checkbox') return; // 避免双重触发
            
            const card = $(e.currentTarget);
            const checkbox = card.find('.ingredient-checkbox');
            const ingredientId = parseInt(card.data('ingredient-id'));
            
            // 检查是否为过敏食材
            if (this.allergenIds.has(ingredientId)) {
                this.showAllergenWarning(card, ingredientId);
                return;
            }
            
            // 切换选择状态
            checkbox.prop('checked', !checkbox.prop('checked')).trigger('change');
        });
        
        // 复选框变化事件
        $(document).on('change', '.ingredient-checkbox', (e) => {
            const ingredientId = parseInt(e.target.value);
            const card = $(e.target).closest('.ingredient-card');
            
            // 检查是否为过敏食材
            if (e.target.checked && this.allergenIds.has(ingredientId)) {
                e.preventDefault();
                e.target.checked = false;
                this.showAllergenWarning(card, ingredientId);
                return;
            }
            
            if (e.target.checked) {
                this.selectIngredient(ingredientId, card);
            } else {
                this.deselectIngredient(ingredientId, card);
            }
        });
        
        // 搜索功能
        $(document).on('input', '#ingredient-search', (e) => {
            this.filterIngredients(e.target.value);
        });
        
        // 过敏食材过滤切换
        $(document).on('change', '#hide-allergens-toggle', (e) => {
            this.renderIngredients();
        });
    }
    
    // 新增：绑定过敏食材相关事件
    bindAllergenEvents() {
        // 监听过敏食材更新事件
        $(document).on('allergensUpdated', (e, allergenIds) => {
            this.allergenIds = new Set(allergenIds);
            this.renderIngredients();
            
            // 检查当前选择的食材是否有过敏风险
            this.checkSelectedIngredientsForAllergens();
        });
        
        // 强制选择过敏食材的确认
        $(document).on('click', '.force-select-allergen', (e) => {
            const ingredientId = parseInt(e.target.dataset.ingredientId);
            this.forceSelectAllergen(ingredientId);
        });
    }
    
    async loadIngredients() {
        try {
            const response = await fetch('/api/ingredients');
            const data = await response.json();
            
            if (data && Array.isArray(data)) {
                this.ingredients = data;
                this.renderIngredients();
            } else {
                console.error('Invalid ingredients data:', data);
                this.showError('加载食材数据失败');
            }
        } catch (error) {
            console.error('Failed to load ingredients:', error);
            this.showError('网络错误，请稍后重试');
        }
    }
    
    renderIngredients() {
        const container = $('#ingredients-grid');
        container.empty();
        
        if (this.ingredients.length === 0) {
            container.html(`
                <div class="col-12 text-center py-5">
                    <i class="fas fa-utensils fa-3x text-muted mb-3"></i>
                    <p class="text-muted">暂无食材数据</p>
                </div>
            `);
            return;
        }
        
        // 过滤食材
        const filteredIngredients = this.getFilteredIngredients();
        
        if (filteredIngredients.length === 0) {
            container.html(`
                <div class="col-12 text-center py-5">
                    <i class="fas fa-search fa-3x text-muted mb-3"></i>
                    <p class="text-muted">没有找到符合条件的食材</p>
                    ${this.allergenIds.size > 0 ? `
                        <small class="text-muted d-block mt-2">
                            已过滤 ${this.allergenIds.size} 种过敏食材
                            <br>
                            <button class="btn btn-link btn-sm p-0" id="show-allergens-toggle">
                                显示过敏食材
                            </button>
                        </small>
                    ` : ''}
                </div>
            `);
            return;
        }
        
        // 渲染食材卡片
        filteredIngredients.forEach(ingredient => {
            const isSelected = this.selectedIngredients.has(ingredient.id);
            const isAllergen = this.allergenIds.has(ingredient.id);
            const cardHtml = this.createIngredientCard(ingredient, isSelected, isAllergen);
            container.append(cardHtml);
        });
        
        // 添加过敏食材统计信息
        this.addAllergenFilterInfo();
    }
    
    createIngredientCard(ingredient, isSelected = false, isAllergen = false) {
        const selectedClass = isSelected ? 'selected' : '';
        const allergenClass = isAllergen ? 'allergen-warning' : '';
        const checkedAttr = isSelected ? 'checked' : '';
        const disabledAttr = isAllergen ? 'disabled' : '';
        
        // 获取食材图片
        const imagePath = ingredient.image_filename 
            ? `/static/images/ingredients/${ingredient.image_filename}`
            : '/static/images/ingredients/default.png';
        
        // 营养摘要
        const nutritionSummary = `
            热量: ${ingredient.calories || 0} kcal/100g<br>
            蛋白质: ${ingredient.protein || 0}g<br>
            脂肪: ${ingredient.fat || 0}g
        `;
        
        // 安全性标识
        const safetyIcons = [];
        if (ingredient.is_safe_for_dogs) safetyIcons.push('<i class="fas fa-dog text-success" title="适合狗狗"></i>');
        if (ingredient.is_safe_for_cats) safetyIcons.push('<i class="fas fa-cat text-success" title="适合猫咪"></i>');
        if (ingredient.is_common_allergen) safetyIcons.push('<i class="fas fa-exclamation-triangle text-warning" title="常见过敏原"></i>');
        
        // 过敏警告
        const allergenWarning = isAllergen ? `
            <div class="allergen-overlay position-absolute top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center"
                style="background: rgba(220, 53, 69, 0.8); border-radius: 10px;">
                <div class="text-center text-white">
                    <i class="fas fa-exclamation-triangle fa-2x mb-2"></i>
                    <div class="fw-bold">过敏食材</div>
                    <small>点击查看详情</small>
                </div>
            </div>
        ` : '';
        
        return `
            <div class="col-md-6 col-lg-4 mb-3">
                <div class="ingredient-card card h-100 ${selectedClass} ${allergenClass}" 
                    data-ingredient-id="${ingredient.id}"
                    data-category="${ingredient.category}"
                    data-calories="${ingredient.calories || 0}"
                    data-protein="${ingredient.protein || 0}"
                    data-fat="${ingredient.fat || 0}">
                    
                    <div class="position-relative">
                        <img src="${imagePath}" 
                            class="card-img-top" 
                            alt="${ingredient.name}"
                            style="height: 120px; object-fit: cover; ${isAllergen ? 'filter: grayscale(50%);' : ''}"
                            onerror="this.src='/static/images/ingredients/default.png'">
                        
                        ${allergenWarning}
                        
                        <!-- 选择复选框 -->
                        <div class="position-absolute top-0 end-0 p-2">
                            <input type="checkbox" 
                                class="form-check-input ingredient-checkbox" 
                                value="${ingredient.id}"
                                ${checkedAttr}
                                ${disabledAttr}>
                        </div>
                        
                        <!-- 分类标签 -->
                        <div class="position-absolute bottom-0 start-0 p-2">
                            <span class="badge" style="background-color: ${this.getCategoryColor(ingredient.category)};">
                                ${this.getCategoryName(ingredient.category)}
                            </span>
                        </div>
                    </div>
                    
                    <div class="card-body p-3">
                        <h6 class="card-title ingredient-name mb-2 ${isAllergen ? 'text-muted' : ''}">${ingredient.name}</h6>
                        <small class="text-muted ingredient-name-en d-block mb-2">${ingredient.name_en || ''}</small>
                        
                        <!-- 营养摘要 -->
                        <div class="nutrition-summary mb-2">
                            <small class="text-muted">${nutritionSummary}</small>
                        </div>
                        
                        <!-- 安全性图标 -->
                        <div class="safety-icons text-center">
                            ${safetyIcons.join(' ')}
                            ${isAllergen ? '<i class="fas fa-ban text-danger" title="过敏食材"></i>' : ''}
                        </div>
                        
                        ${isAllergen ? `
                            <div class="text-center mt-2">
                                <button class="btn btn-outline-danger btn-sm force-select-allergen"
                                        data-ingredient-id="${ingredient.id}">
                                    <i class="fas fa-exclamation-triangle"></i> 仍要选择
                                </button>
                            </div>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }
    
    selectIngredient(ingredientId, card) {
        this.selectedIngredients.add(ingredientId);
        card.addClass('selected');
        
        // 通知营养计算器
        if (window.nutritionCalculator) {
            nutritionCalculator.addIngredient(ingredientId);
        }
        
        // 触发事件
        $(document).trigger('ingredientsChanged');
        
        // 通知过敏检查
        this.notifyRecipeIngredientsChanged();
    }
    
    deselectIngredient(ingredientId, card) {
        this.selectedIngredients.delete(ingredientId);
        card.removeClass('selected');
        
        // 通知营养计算器
        if (window.nutritionCalculator) {
            nutritionCalculator.removeIngredient(ingredientId);
        }
        
        // 触发事件
        $(document).trigger('ingredientsChanged');
        
        // 通知过敏检查
        this.notifyRecipeIngredientsChanged();
    }
    
    filterByCategory(category) {
        this.currentCategory = category;
        this.renderIngredients();
    }
    
    filterIngredients(searchTerm) {
        this.searchTerm = searchTerm.toLowerCase();
        this.renderIngredients();
    }
    
    getFilteredIngredients() {
        let filtered = this.ingredients;
        
        // 按分类过滤
        if (this.currentCategory !== 'all') {
            filtered = filtered.filter(ing => ing.category === this.currentCategory);
        }
        
        // 按搜索词过滤
        if (this.searchTerm) {
            filtered = filtered.filter(ing => 
                ing.name.toLowerCase().includes(this.searchTerm) ||
                (ing.name_en && ing.name_en.toLowerCase().includes(this.searchTerm))
            );
        }
        
        // 过敏食材过滤
        const hideAllergens = $('#hide-allergens-toggle').is(':checked');
        if (hideAllergens && this.allergenIds.size > 0) {
            filtered = filtered.filter(ing => !this.allergenIds.has(ing.id));
        }
        
        return filtered;
    }
    
    // 新增：显示过敏食材警告
    showAllergenWarning(card, ingredientId) {
        const ingredientName = card.find('.ingredient-name').text();
        
        if (window.allergenManager) {
            const allergen = allergenManager.allergens.find(a => a.ingredient_id === ingredientId);
            if (allergen) {
                const severityText = {
                    'mild': '轻微',
                    'moderate': '中度', 
                    'severe': '严重'
                }[allergen.severity] || '未知';
                
                const message = `
                    <div class="alert alert-warning">
                        <h6><i class="fas fa-exclamation-triangle"></i> 过敏警告</h6>
                        <p><strong>${ingredientName}</strong> 是您宠物的过敏食材</p>
                        <p><strong>严重程度:</strong> ${severityText}</p>
                        ${allergen.notes ? `<p><strong>备注:</strong> ${allergen.notes}</p>` : ''}
                        <div class="mt-3">
                            <button class="btn btn-danger btn-sm force-select-allergen" 
                                    data-ingredient-id="${ingredientId}">
                                我了解风险，仍要选择
                            </button>
                            <button class="btn btn-secondary btn-sm ms-2" data-bs-dismiss="alert">
                                取消
                            </button>
                        </div>
                    </div>
                `;
                
                // 在卡片上方显示警告
                card.before(message);
            }
        } else {
            alert(`警告：${ingredientName} 是过敏食材，不建议选择！`);
        }
    }
    
    // 新增：强制选择过敏食材
    forceSelectAllergen(ingredientId) {
        if (confirm('您确定要选择这种过敏食材吗？这可能对您的宠物造成健康风险。')) {
            const card = $(`.ingredient-card[data-ingredient-id="${ingredientId}"]`);
            const checkbox = card.find('.ingredient-checkbox');
            
            checkbox.prop('disabled', false).prop('checked', true);
            this.selectIngredient(ingredientId, card);
            
            // 移除警告信息
            card.prev('.alert').remove();
            
            // 显示风险提示
            this.showRiskNotification(ingredientId);
        }
    }
    
    // 新增：显示风险通知
    showRiskNotification(ingredientId) {
        const ingredientName = this.ingredients.find(ing => ing.id === ingredientId)?.name || '未知食材';
        
        if (window.nutritionCalculator) {
            nutritionCalculator.showNotification(
                `⚠️ 风险提示：已选择过敏食材 "${ingredientName}"，请谨慎使用！`, 
                'warning'
            );
        }
    }
    
    // 新增：检查当前选择的食材是否有过敏风险
    checkSelectedIngredientsForAllergens() {
        const selectedAllergens = [];
        this.selectedIngredients.forEach(id => {
            if (this.allergenIds.has(id)) {
                const ingredient = this.ingredients.find(ing => ing.id === id);
                if (ingredient) {
                    selectedAllergens.push(ingredient.name);
                }
            }
        });
        
        if (selectedAllergens.length > 0) {
            if (window.nutritionCalculator) {
                nutritionCalculator.showNotification(
                    `当前食谱包含过敏食材：${selectedAllergens.join(', ')}`, 
                    'warning'
                );
            }
        }
    }
    
    // 新增：通知食谱食材变化（用于过敏检查）
    notifyRecipeIngredientsChanged() {
        const ingredientIds = Array.from(this.selectedIngredients);
        $(document).trigger('recipeIngredientsChanged', [ingredientIds]);
    }
    
    // 新增：添加过敏食材过滤信息
    addAllergenFilterInfo() {
        if (this.allergenIds.size === 0) return;
        
        const container = $('#ingredients-grid');
        const filterInfo = `
            <div class="col-12 mb-3">
                <div class="alert alert-info d-flex justify-content-between align-items-center">
                    <div>
                        <i class="fas fa-info-circle"></i>
                        已过滤 ${this.allergenIds.size} 种过敏食材
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="hide-allergens-toggle" checked>
                        <label class="form-check-label" for="hide-allergens-toggle">
                            隐藏过敏食材
                        </label>
                    </div>
                </div>
            </div>
        `;
        
        container.prepend(filterInfo);
    }
    
    getCategoryName(category) {
        const categoryNames = {
            'red_meat': '红肉',
            'white_meat': '白肉', 
            'fish': '鱼类',
            'organs': '内脏',
            'vegetables': '蔬菜',
            'fruits': '水果',
            'grains': '谷物',
            'dairy': '乳制品',
            'supplements': '营养补充剂',
            'oils': '油脂类'
        };
        return categoryNames[category] || category;
    }
    
    getCategoryColor(category) {
        const categoryColors = {
            'red_meat': '#B82F0D',      // 红肉 - 深红色
            'white_meat': '#5580AD',    // 白肉 - 蓝色
            'fish': '#A1B4B2',         // 鱼类 - 灰绿色
            'organs': '#510B0B',       // 内脏 - 深褐色
            'vegetables': '#228B22',    // 蔬菜 - 绿色
            'fruits': '#FF6347',       // 水果 - 橙红色
            'grains': '#DEB887',       // 谷物 - 浅棕色
            'dairy': '#EDBF9D',        // 乳制品 - 奶白色
            'supplements': '#9370DB',   // 营养补充剂 - 紫色
            'oils': '#FFD700'          // 油脂类 - 金色
        };
        return categoryColors[category] || '#A1B4B2';
    }
    
    showError(message) {
        $('#ingredients-grid').html(`
            <div class="col-12">
                <div class="alert alert-danger text-center">
                    <i class="fas fa-exclamation-triangle"></i>
                    ${message}
                </div>
            </div>
        `);
    }
    
    // 公共方法：获取已选择的食材数据
    getSelectedIngredientsData() {
        return this.ingredients.filter(ing => this.selectedIngredients.has(ing.id));
    }
    
    // 公共方法：清空选择
    clearSelection() {
        this.selectedIngredients.clear();
        $('.ingredient-card').removeClass('selected');
        $('.ingredient-checkbox').prop('checked', false);
        
        // 通知营养计算器
        if (window.nutritionCalculator) {
            nutritionCalculator.selectedIngredients.clear();
            nutritionCalculator.renderSelectedIngredients();
            nutritionCalculator.calculateNutrition();
        }
        
        $(document).trigger('ingredientsChanged');
    }
    
    // 公共方法：根据营养方案推荐食材
    recommendIngredientsForPlan(planId) {
        // 这个功能可以根据营养方案自动选择一些推荐的食材
        // 暂时留空，可以在后续版本中实现
        console.log('推荐食材功能将在后续版本实现');
    }
}

// 页面加载完成后自动初始化
$(document).ready(function() {
    window.ingredientSelector = new IngredientSelector();
    
    // 添加搜索框（如果页面需要）
    if ($('#ingredient-search').length === 0) {
        const searchHtml = `
            <div class="mb-3">
                <div class="input-group">
                    <span class="input-group-text">
                        <i class="fas fa-search"></i>
                    </span>
                    <input type="text" 
                        id="ingredient-search" 
                        class="form-control" 
                        placeholder="搜索食材名称...">
                </div>
            </div>
        `;
        $('#ingredients-grid').before(searchHtml);
    }
});