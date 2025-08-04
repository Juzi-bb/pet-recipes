/**
 * 收藏功能管理类
 */
class FavoritesManager {
    constructor() {
        this.favoritesCount = 0;
        this.favoritesCache = [];
        this.init();
    }

    /**
     * 初始化收藏功能
     */
    init() {
        this.loadFavoritesCount();
        this.bindEvents();
    }

    /**
     * 绑定事件监听器
     */
    bindEvents() {
        // 点击模态框外部关闭
        window.addEventListener('click', (event) => {
            const favoritesModal = document.getElementById('favoritesModal');
            const confirmModal = document.getElementById('confirmModal');
            
            if (event.target === favoritesModal) {
                this.closeFavoritesModal();
            }
            if (event.target === confirmModal) {
                this.closeConfirmModal();
            }
        });

        // ESC键关闭模态框
        document.addEventListener('keydown', (event) => {
            if (event.key === 'Escape') {
                this.closeFavoritesModal();
                this.closeConfirmModal();
            }
        });
    }

    /**
     * 加载收藏数量
     */
    async loadFavoritesCount() {
        try {
            const response = await fetch('/api/user/favorites');
            const data = await response.json();
            
            if (data.success) {
                this.favoritesCount = data.data.count;
                this.updateFavoritesCountDisplay();
            }
        } catch (error) {
            console.error('加载收藏数量失败:', error);
        }
    }

    /**
     * 更新页面上的收藏数量显示
     */
    updateFavoritesCountDisplay() {
        const countElement = document.getElementById('favoritesCount');
        if (countElement) {
            countElement.textContent = this.favoritesCount;
        }
    }

    /**
     * 切换收藏状态
     */
    async toggleFavorite(recipeId, element) {
        const isFavorited = element.classList.contains('favorited');
        
        if (isFavorited) {
            // 取消收藏需要确认
            this.showConfirmModal('确定要取消收藏这个食谱吗？', async () => {
                await this.removeFavorite(recipeId, element);
            });
        } else {
            await this.addFavorite(recipeId, element);
        }
    }

    /**
     * 添加收藏
     */
    async addFavorite(recipeId, element) {
        try {
            element.disabled = true; // 防止重复点击
            
            const response = await fetch('/api/recipe/favorite', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ recipe_id: recipeId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                element.classList.add('favorited');
                this.favoritesCount++;
                this.updateFavoritesCountDisplay();
                this.showToast('收藏成功', 'success');
                
                // 清空缓存，下次打开收藏夹时重新加载
                this.favoritesCache = [];
            } else {
                this.showToast(data.message, 'error');
            }
        } catch (error) {
            console.error('收藏失败:', error);
            this.showToast('收藏失败，请稍后重试', 'error');
        } finally {
            element.disabled = false;
        }
    }

    /**
     * 取消收藏
     */
    async removeFavorite(recipeId, element) {
        try {
            element.disabled = true; // 防止重复点击
            
            const response = await fetch(`/api/recipe/favorite/${recipeId}`, {
                method: 'DELETE'
            });
            
            const data = await response.json();
            
            if (data.success) {
                element.classList.remove('favorited');
                this.favoritesCount--;
                this.updateFavoritesCountDisplay();
                this.showToast('取消收藏成功', 'success');
                
                // 清空缓存，下次打开收藏夹时重新加载
                this.favoritesCache = [];
                
                // 如果收藏夹模态框是打开的，刷新收藏夹内容
                const modal = document.getElementById('favoritesModal');
                if (modal && modal.style.display === 'block') {
                    await this.loadFavorites();
                }
            } else {
                this.showToast(data.message, 'error');
            }
        } catch (error) {
            console.error('取消收藏失败:', error);
            this.showToast('取消收藏失败，请稍后重试', 'error');
        } finally {
            element.disabled = false;
        }
    }

    /**
     * 显示收藏夹模态框
     */
    async showFavoritesModal() {
        const modal = document.getElementById('favoritesModal');
        if (modal) {
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden'; // 防止背景滚动
            await this.loadFavorites();
        }
    }

    /**
     * 关闭收藏夹模态框
     */
    closeFavoritesModal() {
        const modal = document.getElementById('favoritesModal');
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = ''; // 恢复背景滚动
        }
    }

    /**
     * 加载收藏夹内容
     */
    async loadFavorites() {
        try {
            // 显示加载状态
            const container = document.getElementById('favoritesGrid');
            const emptyState = document.getElementById('favoritesEmptyState');
            
            if (container) {
                container.innerHTML = '<div class="loading">加载中...</div>';
            }
            
            const response = await fetch('/api/user/favorites');
            const data = await response.json();
            
            if (data.success && data.data.favorites.length > 0) {
                this.favoritesCache = data.data.favorites;
                this.renderFavorites(data.data.favorites);
                if (emptyState) emptyState.style.display = 'none';
            } else {
                if (container) container.innerHTML = '';
                if (emptyState) emptyState.style.display = 'block';
            }
        } catch (error) {
            console.error('加载收藏夹失败:', error);
            this.showToast('加载收藏夹失败', 'error');
        }
    }

    /**
     * 渲染收藏夹内容
     */
    renderFavorites(favorites) {
        const container = document.getElementById('favoritesGrid');
        if (!container) return;

        container.innerHTML = favorites.map(recipe => `
            <div class="recipe-card">
                <button class="favorite-star favorited" 
                        onclick="favoritesManager.toggleFavorite(${recipe.id}, this)">
                    <i class="fas fa-star"></i>
                </button>
                <div class="recipe-image">
                    ${recipe.image ? 
                        `<img src="${recipe.image}" alt="${recipe.name}" onerror="this.parentElement.innerHTML='<i class=\\'fas fa-utensils\\'></i>'">` : 
                        '<i class="fas fa-utensils"></i>'
                    }
                </div>
                <div class="recipe-info">
                    <h3>${this.escapeHtml(recipe.name)}</h3>
                    <p class="recipe-description">${this.escapeHtml(recipe.description || '暂无描述')}</p>
                    <div class="recipe-meta">
                        <span>收藏时间: ${new Date(recipe.favorited_at).toLocaleDateString()}</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    /**
     * HTML转义，防止XSS攻击
     */
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    /**
     * 显示确认模态框
     */
    showConfirmModal(message, onConfirm) {
        const modal = document.getElementById('confirmModal');
        const messageElement = document.getElementById('confirmMessage');
        const confirmButton = document.getElementById('confirmButton');
        
        if (modal && messageElement && confirmButton) {
            messageElement.textContent = message;
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
            
            // 移除之前的事件监听器
            const newConfirmButton = confirmButton.cloneNode(true);
            confirmButton.parentNode.replaceChild(newConfirmButton, confirmButton);
            
            // 添加新的事件监听器
            newConfirmButton.onclick = () => {
                this.closeConfirmModal();
                onConfirm();
            };
        }
    }

    /**
     * 关闭确认模态框
     */
    closeConfirmModal() {
        const modal = document.getElementById('confirmModal');
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }

    /**
     * 显示提示消息
     */
    showToast(message, type = 'success') {
        // 移除已存在的toast
        const existingToasts = document.querySelectorAll('.toast');
        existingToasts.forEach(toast => toast.remove());
        
        // 创建toast元素
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${this.escapeHtml(message)}</span>
        `;
        
        // 确保toast样式存在
        this.ensureToastStyles();
        
        document.body.appendChild(toast);
        
        // 3秒后自动消失
        setTimeout(() => {
            toast.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => {
                if (toast.parentNode) {
                    toast.parentNode.removeChild(toast);
                }
            }, 300);
        }, 3000);
    }

    /**
     * 确保toast样式存在
     */
    ensureToastStyles() {
        if (!document.querySelector('#toast-style')) {
            const style = document.createElement('style');
            style.id = 'toast-style';
            style.textContent = `
                .toast {
                    position: fixed;
                    top: 20px;
                    right: 20px;
                    padding: 15px 20px;
                    border-radius: 8px;
                    color: white;
                    font-weight: 500;
                    z-index: 10000;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    animation: slideInRight 0.3s ease;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                }
                .toast-success {
                    background: #27ae60;
                }
                .toast-error {
                    background: #e74c3c;
                }
                .loading {
                    grid-column: 1 / -1;
                    text-align: center;
                    padding: 40px;
                    color: #7f8c8d;
                    font-size: 16px;
                }
                @keyframes slideInRight {
                    from {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                    to {
                        transform: translateX(0);
                        opacity: 1;
                    }
                }
                @keyframes slideOutRight {
                    from {
                        transform: translateX(0);
                        opacity: 1;
                    }
                    to {
                        transform: translateX(100%);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    /**
     * 检查单个食谱的收藏状态
     */
    async checkFavoriteStatus(recipeId) {
        try {
            const response = await fetch(`/api/recipe/favorite-status/${recipeId}`);
            const data = await response.json();
            
            if (data.success) {
                return data.data.is_favorited;
            }
            return false;
        } catch (error) {
            console.error('检查收藏状态失败:', error);
            return false;
        }
    }
}

// 创建全局收藏管理器实例
let favoritesManager;

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    favoritesManager = new FavoritesManager();
});

// 为了向后兼容，保留全局函数
function toggleFavorite(recipeId, element) {
    if (favoritesManager) {
        return favoritesManager.toggleFavorite(recipeId, element);
    }
}

function showFavoritesModal() {
    if (favoritesManager) {
        return favoritesManager.showFavoritesModal();
    }
}

function closeFavoritesModal() {
    if (favoritesManager) {
        return favoritesManager.closeFavoritesModal();
    }
}

function closeConfirmModal() {
    if (favoritesManager) {
        return favoritesManager.closeConfirmModal();
    }
}