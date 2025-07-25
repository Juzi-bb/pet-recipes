/**
 * 过敏食材管理器
 * 处理宠物过敏食材的添加、删除和展示
 */

class AllergenManager {
    constructor() {
        this.currentPetId = null;
        this.allergens = [];
        this.commonAllergens = {};
        
        this.init();
    }
    
    init() {
        this.bindEvents();
        this.loadCommonAllergens();
    }
    
    bindEvents() {
        // 宠物选择变化
        $(document).on('change', '#pet-select', (e) => {
            this.currentPetId = e.target.value;
            if (this.currentPetId) {
                this.loadPetAllergens();
            }
        });
        
        // 添加过敏食材按钮
        $(document).on('click', '#add-allergen-btn', () => {
            this.showAddAllergenModal();
        });
        
        // 移除过敏食材
        $(document).on('click', '.remove-allergen-btn', (e) => {
            const ingredientId = parseInt(e.target.dataset.ingredientId);
            const ingredientName = e.target.dataset.ingredientName;
            this.removeAllergen(ingredientId, ingredientName);
        });
        
        // 保存过敏食材
        $(document).on('click', '#save-allergen-btn', () => {
            this.saveAllergen();
        });
        
        // 常见过敏食材快速添加
        $(document).on('click', '.common-allergen-item', (e) => {
            const ingredientId = parseInt(e.target.dataset.ingredientId);
            const ingredientName = e.target.dataset.ingredientName;
            this.quickAddAllergen(ingredientId, ingredientName);
        });
        
        // 食谱安全性检查
        $(document).on('recipeIngredientsChanged', (e, ingredientIds) => {
            this.checkRecipeSafety(ingredientIds);
        });
    }
    
    async loadPetAllergens() {
        if (!this.currentPetId) return;
        
        try {
            const response = await fetch(`/api/pet/${this.currentPetId}/allergens`);
            const data = await response.json();
            
            if (data.success) {
                this.allergens = data.allergens;
                this.renderAllergenList();
                this.updateAllergenStats(data.statistics);
                
                // 通知其他组件更新过敏食材过滤
                $(document).trigger('allergensUpdated', [this.getAllergenIds()]);
            } else {
                this.showNotification('加载过敏食材失败', 'error');
            }
        } catch (error) {
            console.error('加载过敏食材失败:', error);
            this.showNotification('网络错误，请稍后重试', 'error');
        }
    }
    
    async loadCommonAllergens() {
        try {
            const response = await fetch('/api/common-allergens');
            const data = await response.json();
            
            if (data.success) {
                this.commonAllergens = data.allergens_by_category;
                this.renderCommonAllergens();
            }
        } catch (error) {
            console.error('加载常见过敏食材失败:', error);
        }
    }
    
    renderAllergenList() {
        const container = $('#pet-allergens-list');
        container.empty();
        
        if (this.allergens.length === 0) {
            container.html(`
                <div class="text-center py-4">
                    <i class="fas fa-shield-alt fa-2x text-success mb-2"></i>
                    <p class="text-muted">该宠物暂无过敏食材记录</p>
                    <button class="btn btn-outline-primary btn-sm" id="add-allergen-btn">
                        <i class="fas fa-plus"></i> 添加过敏食材
                    </button>
                </div>
            `);
            return;
        }
        
        const allergensHtml = this.allergens.map(allergen => {
            const severityClass = {
                'mild': 'warning',
                'moderate': 'danger',
                'severe': 'dark'
            }[allergen.severity] || 'secondary';
            
            const severityText = {
                'mild': '轻微',
                'moderate': '中度',
                'severe': '严重'
            }[allergen.severity] || '未知';
            
            return `
                <div class="allergen-item card mb-2">
                    <div class="card-body p-3">
                        <div class="row align-items-center">
                            <div class="col-md-4">
                                <h6 class="mb-1">${allergen.ingredient_name}</h6>
                                <small class="text-muted">${this.getCategoryName(allergen.ingredient_category)}</small>
                            </div>
                            <div class="col-md-3">
                                <span class="badge bg-${severityClass}">${severityText}</span>
                            </div>
                            <div class="col-md-3">
                                <small class="text-muted">
                                    ${allergen.confirmed_date ? 
                                        `确认时间: ${new Date(allergen.confirmed_date).toLocaleDateString()}` : 
                                        '未确认时间'}
                                </small>
                            </div>
                            <div class="col-md-2 text-end">
                                <button class="btn btn-outline-danger btn-sm remove-allergen-btn"
                                        data-ingredient-id="${allergen.ingredient_id}"
                                        data-ingredient-name="${allergen.ingredient_name}"
                                        title="移除">
                                    <i class="fas fa-trash"></i>
                                </button>
                            </div>
                        </div>
                        ${allergen.notes ? `
                            <div class="row mt-2">
                                <div class="col-12">
                                    <small class="text-muted">
                                        <strong>备注:</strong> ${allergen.notes}
                                    </small>
                                </div>
                            </div>
                        ` : ''}
                    </div>
                </div>
            `;
        }).join('');
        
        container.html(`
            <div class="d-flex justify-content-between align-items-center mb-3">
                <h6>过敏食材列表</h6>
                <button class="btn btn-primary btn-sm" id="add-allergen-btn">
                    <i class="fas fa-plus"></i> 添加过敏食材
                </button>
            </div>
            ${allergensHtml}
        `);
    }
    
    renderCommonAllergens() {
        const container = $('#common-allergens-list');
        if (!container.length) return;
        
        const categoriesHtml = Object.entries(this.commonAllergens).map(([category, allergens]) => {
            const allergensHtml = allergens.map(allergen => `
                <div class="col-md-6 mb-2">
                    <div class="common-allergen-item btn btn-outline-warning btn-sm w-100 text-start"
                        data-ingredient-id="${allergen.id}"
                        data-ingredient-name="${allergen.name}">
                        <i class="fas fa-plus-circle me-2"></i>
                        ${allergen.name}
                        ${allergen.name_en ? `<small class="text-muted">(${allergen.name_en})</small>` : ''}
                    </div>
                </div>
            `).join('');
            
            return `
                <div class="category-section mb-4">
                    <h6 class="text-muted mb-3">
                        <i class="fas fa-tag"></i> ${this.getCategoryName(category)}
                    </h6>
                    <div class="row">
                        ${allergensHtml}
                    </div>
                </div>
            `;
        }).join('');
        
        container.html(categoriesHtml);
    }
    
    updateAllergenStats(stats) {
        const container = $('#allergen-stats');
        if (!container.length) return;
        
        const severityStats = Object.entries(stats.by_severity).map(([severity, count]) => {
            if (count === 0) return '';
            
            const severityClass = {
                'mild': 'warning',
                'moderate': 'danger',
                'severe': 'dark'
            }[severity] || 'secondary';
            
            const severityText = {
                'mild': '轻微',
                'moderate': '中度',
                'severe': '严重'
            }[severity] || '未知';
            
            return `<span class="badge bg-${severityClass} me-2">${severityText}: ${count}</span>`;
        }).join('');
        
        const statsHtml = `
            <div class="alert alert-info">
                <div class="row">
                    <div class="col-md-6">
                        <strong>过敏食材总数:</strong> ${stats.total_count}
                    </div>
                    <div class="col-md-6">
                        ${severityStats}
                    </div>
                </div>
                ${stats.recent_additions.length > 0 ? `
                    <hr>
                    <small class="text-muted">
                        <strong>最近添加:</strong>
                        ${stats.recent_additions.map(item => item.ingredient_name).join(', ')}
                    </small>
                ` : ''}
            </div>
        `;
        
        container.html(statsHtml);
    }
    
    showAddAllergenModal() {
        if (!this.currentPetId) {
            this.showNotification('请先选择宠物', 'warning');
            return;
        }
        
        const modalHtml = `
            <div class="modal fade" id="addAllergenModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header" style="background-color: #510B0B; color: white;">
                            <h5 class="modal-title">添加过敏食材</h5>
                            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <form id="add-allergen-form">
                                <div class="mb-3">
                                    <label for="allergen-ingredient-select" class="form-label">选择食材 *</label>
                                    <select id="allergen-ingredient-select" class="form-select" required>
                                        <option value="">请选择食材</option>
                                        <!-- 食材选项将通过JavaScript加载 -->
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label for="allergen-severity" class="form-label">过敏严重程度 *</label>
                                    <select id="allergen-severity" class="form-select" required>
                                        <option value="mild">轻微 - 轻微不适或皮肤反应</option>
                                        <option value="moderate">中度 - 明显症状，需要注意</option>
                                        <option value="severe">严重 - 严重反应，绝对禁食</option>
                                    </select>
                                </div>
                                <div class="mb-3">
                                    <label for="allergen-notes" class="form-label">过敏反应描述</label>
                                    <textarea id="allergen-notes" class="form-control" rows="3" 
                                            placeholder="描述过敏反应症状，如皮肤瘙痒、呕吐、腹泻等..."></textarea>
                                </div>
                                <div class="mb-3">
                                    <label for="allergen-confirmed-date" class="form-label">确认日期</label>
                                    <input type="date" id="allergen-confirmed-date" class="form-control">
                                </div>
                            </form>
                            
                            <!-- 常见过敏食材快速选择 -->
                            <div class="mt-4">
                                <h6>常见过敏食材快速添加:</h6>
                                <div id="common-allergens-list">
                                    <!-- 常见过敏食材将在这里渲染 -->
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">取消</button>
                            <button type="button" class="btn btn-danger" id="save-allergen-btn">
                                <i class="fas fa-save"></i> 保存过敏食材
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // 移除现有模态框
        $('#addAllergenModal').remove();
        
        // 添加新模态框
        $('body').append(modalHtml);
        
        // 加载食材选项
        this.loadIngredientOptions();
        
        // 显示模态框
        $('#addAllergenModal').modal('show');
        
        // 渲染常见过敏食材
        this.renderCommonAllergens();
    }
    
    async loadIngredientOptions() {
        try {
            const response = await fetch('/api/ingredients');
            const ingredients = await response.json();
            
            const select = $('#allergen-ingredient-select');
            select.empty().append('<option value="">请选择食材</option>');
            
            // 过滤掉已经是过敏食材的
            const existingAllergenIds = this.getAllergenIds();
            
            ingredients.forEach(ingredient => {
                if (!existingAllergenIds.has(ingredient.id)) {
                    select.append(`
                        <option value="${ingredient.id}" data-category="${ingredient.category}">
                            ${ingredient.name} (${this.getCategoryName(ingredient.category)})
                        </option>
                    `);
                }
            });
        } catch (error) {
            console.error('加载食材选项失败:', error);
        }
    }
    
    async saveAllergen() {
        const ingredientId = $('#allergen-ingredient-select').val();
        const severity = $('#allergen-severity').val();
        const notes = $('#allergen-notes').val();
        const confirmedDate = $('#allergen-confirmed-date').val();
        
        if (!ingredientId) {
            this.showNotification('请选择食材', 'warning');
            return;
        }
        
        if (!severity) {
            this.showNotification('请选择过敏严重程度', 'warning');
            return;
        }
        
        try {
            const response = await fetch(`/api/pet/${this.currentPetId}/allergens`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ingredient_id: parseInt(ingredientId),
                    severity: severity,
                    notes: notes,
                    confirmed_date: confirmedDate || null
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                $('#addAllergenModal').modal('hide');
                this.showNotification(data.message, 'success');
                this.loadPetAllergens(); // 重新加载过敏食材列表
            } else {
                this.showNotification(data.error, 'error');
            }
        } catch (error) {
            console.error('保存过敏食材失败:', error);
            this.showNotification('保存失败，请稍后重试', 'error');
        }
    }
    
    async quickAddAllergen(ingredientId, ingredientName) {
        if (!this.currentPetId) {
            this.showNotification('请先选择宠物', 'warning');
            return;
        }
        
        // 检查是否已经是过敏食材
        if (this.getAllergenIds().has(ingredientId)) {
            this.showNotification(`${ingredientName} 已在过敏食材列表中`, 'warning');
            return;
        }
        
        if (confirm(`确认将 "${ingredientName}" 添加为过敏食材吗？`)) {
            try {
                const response = await fetch(`/api/pet/${this.currentPetId}/allergens`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        ingredient_id: ingredientId,
                        severity: 'mild', // 默认轻微
                        notes: '通过常见过敏食材快速添加'
                    })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.showNotification(data.message, 'success');
                    this.loadPetAllergens();
                } else {
                    this.showNotification(data.error, 'error');
                }
            } catch (error) {
                console.error('快速添加过敏食材失败:', error);
                this.showNotification('添加失败，请稍后重试', 'error');
            }
        }
    }
    
    async removeAllergen(ingredientId, ingredientName) {
        if (confirm(`确认移除 "${ingredientName}" 的过敏记录吗？`)) {
            try {
                const response = await fetch(`/api/pet/${this.currentPetId}/allergens/${ingredientId}`, {
                    method: 'DELETE'
                });
                
                const data = await response.json();
                
                if (data.success) {
                    this.showNotification(data.message, 'success');
                    this.loadPetAllergens();
                } else {
                    this.showNotification(data.error, 'error');
                }
            } catch (error) {
                console.error('移除过敏食材失败:', error);
                this.showNotification('移除失败，请稍后重试', 'error');
            }
        }
    }
    
    async checkRecipeSafety(ingredientIds) {
        if (!this.currentPetId || !ingredientIds || ingredientIds.length === 0) {
            this.clearSafetyWarnings();
            return;
        }
        
        try {
            const response = await fetch('/api/check-recipe-safety', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    ingredient_ids: ingredientIds,
                    pet_id: this.currentPetId
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.displaySafetyWarnings(data.safety_check);
            }
        } catch (error) {
            console.error('检查食谱安全性失败:', error);
        }
    }
    
    displaySafetyWarnings(safetyCheck) {
        const container = $('#recipe-safety-warnings');
        if (!container.length) return;
        
        if (safetyCheck.is_safe) {
            container.html(`
                <div class="alert alert-success">
                    <i class="fas fa-shield-alt"></i>
                    该食谱对您的宠物是安全的
                </div>
            `);
        } else {
            const warningsHtml = safetyCheck.allergens.map(allergen => {
                const severityClass = {
                    'mild': 'warning',
                    'moderate': 'danger',
                    'severe': 'danger'
                }[allergen.severity] || 'danger';
                
                return `
                    <li class="list-group-item list-group-item-${severityClass}">
                        <strong>${allergen.ingredient_name}</strong> - ${allergen.severity} 过敏
                        ${allergen.notes ? `<br><small>${allergen.notes}</small>` : ''}
                    </li>
                `;
            }).join('');
            
            container.html(`
                <div class="alert alert-danger">
                    <h6><i class="fas fa-exclamation-triangle"></i> 过敏警告</h6>
                    <p>以下食材可能对您的宠物造成过敏反应：</p>
                    <ul class="list-group list-group-flush">
                        ${warningsHtml}
                    </ul>
                    <div class="mt-3">
                        <small class="text-muted">
                            建议移除这些食材或咨询兽医意见
                        </small>
                    </div>
                </div>
            `);
        }
    }
    
    clearSafetyWarnings() {
        $('#recipe-safety-warnings').empty();
    }
    
    getAllergenIds() {
        return new Set(this.allergens.map(allergen => allergen.ingredient_id));
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
    
    showNotification(message, type = 'info') {
        // 重用营养计算器的通知方法
        if (window.nutritionCalculator) {
            nutritionCalculator.showNotification(message, type);
        } else {
            alert(message);
        }
    }
}

// 全局实例
let allergenManager;

$(document).ready(function() {
    allergenManager = new AllergenManager();
});