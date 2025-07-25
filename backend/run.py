# 项目的启动文件
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 先设置环境变量，再导入app
os.environ['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pet_recipes.db'

from app import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True, port=5001) # 使用一个与前端不同的端口