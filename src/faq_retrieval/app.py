"""
FAQ检索API服务主应用
"""
from flask import Flask, jsonify
import logging
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from faq_retrieval.config import config
from faq_retrieval.api.routes import api_bp, legacy_bp
from faq_retrieval.services.model_manager import model_manager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def create_app():
    """应用工厂函数"""
    app = Flask(__name__)
    
    # 注册蓝图
    app.register_blueprint(api_bp)
    app.register_blueprint(legacy_bp)
    
    # 在应用上下文中预加载模型
    with app.app_context():
        logger.info("Initializing embedding model on application startup...")
        try:
            if model_manager.load_model():
                logger.info("Model loaded successfully on startup")
            else:
                logger.warning("Failed to load model on startup")
        except Exception as e:
            logger.error(f"Error loading model on startup: {e}")
    
    # 错误处理
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "message": "Endpoint not found"
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error(f"Internal server error: {error}")
        return jsonify({
            "success": False,
            "message": "Internal server error"
        }), 500
    
    return app

def main():
    """主函数"""
    app = create_app()
    
    # 获取Flask配置
    flask_config = config.get_flask_config()
    
    logger.info("Starting FAQ retrieval API service...")
    logger.info(f"Model: {config.MODEL_NAME}")
    logger.info(f"Database: {config.MYSQL_HOST}:{config.MYSQL_PORT}/{config.MYSQL_DATABASE}")
    logger.info(f"Qdrant: {config.QDRANT_HOST}:{config.QDRANT_PORT}")
    
    app.run(
        host=flask_config['HOST'], 
        port=flask_config['PORT'],
        debug=flask_config['DEBUG'],
        threaded=flask_config['THREADED']
    )

if __name__ == '__main__':
    main()
