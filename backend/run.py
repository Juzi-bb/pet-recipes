# 项目的启动文件
from app import create_app, db
from flask_migrate import Migrate

app = create_app()
migrate = Migrate(app, db)

if __name__ == '__main__':
    app.run(debug=True, port=5001) # 使用一个与前端不同的端口