"""
API路由定义
"""
from flask import Blueprint, request, jsonify
import logging
from faq_retrieval.services.faq_service import FAQService
from faq_retrieval.services.model_manager import model_manager

logger = logging.getLogger(__name__)

# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api/v1')
legacy_bp = Blueprint('legacy', __name__)

# 初始化FAQ服务
faq_service = FAQService()

@api_bp.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        status = faq_service.get_system_status()
        return jsonify(status), 200 if status["success"] else 503
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return jsonify({
            "success": False,
            "message": f"Health check failed: {str(e)}"
        }), 503

@api_bp.route('/faqs/initialize', methods=['POST'])
def initialize_faqs():
    """
    全量初始化FAQ数据接口
    
    Body参数:
    {
        "recreate_collection": true  // 可选，是否重新创建集合，默认true
    }
    """
    try:
        data = request.get_json() or {}
        recreate_collection = data.get('recreate_collection', True)
        
        logger.info(f"Starting full FAQ initialization, recreate_collection: {recreate_collection}")
        result = faq_service.initialize_full_data(recreate_collection)
        
        status_code = 200 if result["success"] else 500
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in initialize_faqs: {e}")
        return jsonify({
            "success": False,
            "message": f"Initialization failed: {str(e)}",
            "processed_count": 0,
            "total_count": 0
        }), 500

@api_bp.route('/faqs', methods=['POST'])
def add_faq():
    """
    添加单条FAQ接口
    
    Body参数:
    {
        "id": "faq_001",           // 必需，FAQ唯一标识
        "question": "如何重置密码？",  // 必需，问题内容
        "answer": "请联系管理员"      // 必需，答案内容
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "Request body is required"
            }), 400
        
        faq_id = data.get('id')
        question = data.get('question')
        answer = data.get('answer')
        
        if not all([faq_id, question, answer]):
            return jsonify({
                "success": False,
                "message": "id, question, and answer are required fields"
            }), 400
        
        logger.info(f"Adding new FAQ: {faq_id}")
        result = faq_service.add_single_faq(faq_id, question, answer)
        
        status_code = 201 if result["success"] else 500
        return jsonify(result), status_code
        
    except Exception as e:
        logger.error(f"Error in add_faq: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to add FAQ: {str(e)}"
        }), 500

@api_bp.route('/faqs/search', methods=['POST'])
def search_faqs():
    """
    搜索FAQ接口
    
    Body参数:
    {
        "text": "如何维修电脑？",      // 必需，查询文本
        "limit": 5,               // 可选，返回结果数量，默认5
        "similarity": 0.15        // 可选，相似度阈值，默认0.0
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                "success": False,
                "message": "Request body is required"
            }), 400
        
        query_text = data.get('text', '').strip()
        limit = data.get('limit', 5)
        similarity_threshold = data.get('similarity', 0.0)
        
        if not query_text:
            return jsonify({
                "success": False,
                "message": "text field is required"
            }), 400
        
        # 验证参数范围
        if not (1 <= limit <= 50):
            return jsonify({
                "success": False,
                "message": "limit must be between 1 and 50"
            }), 400
        
        if not (0.0 <= similarity_threshold <= 1.0):
            return jsonify({
                "success": False,
                "message": "similarity must be between 0.0 and 1.0"
            }), 400
        
        logger.info(f"Searching FAQs for query: {query_text}")
        result = faq_service.search_faqs(query_text, limit, similarity_threshold)
        
        # 兼容原有API格式
        if result["success"]:
            return jsonify({
                "results": result["results"]
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": result["message"]
            }), 500
        
    except Exception as e:
        logger.error(f"Error in search_faqs: {e}")
        return jsonify({
            "success": False,
            "message": f"Search failed: {str(e)}"
        }), 500

@api_bp.route('/faqs', methods=['GET'])
def list_all_faqs():
    """获取所有FAQ数据接口"""
    try:
        logger.info("Getting all FAQs from Qdrant")
        result = faq_service.get_all_faqs_from_qdrant()
        
        if result["success"]:
            return jsonify({
                "total_points": result["total_points"],
                "points": result["points"]
            }), 200
        else:
            return jsonify({
                "success": False,
                "message": result["message"]
            }), 500
        
    except Exception as e:
        logger.error(f"Error in list_all_faqs: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to get FAQs: {str(e)}"
        }), 500

@api_bp.route('/model/info', methods=['GET'])
def get_model_info():
    """获取模型信息接口"""
    try:
        model_info = model_manager.get_model_info()
        return jsonify({
            "success": True,
            "model_info": model_info
        }), 200
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return jsonify({
            "success": False,
            "message": f"Failed to get model info: {str(e)}"
        }), 500

# 兼容旧版API
@legacy_bp.route('/search', methods=['POST'])
def legacy_search():
    """兼容旧版搜索接口"""
    return search_faqs()

@legacy_bp.route('/list-all', methods=['GET'])
def legacy_list_all():
    """兼容旧版列表接口"""
    return list_all_faqs()

@legacy_bp.route('/health', methods=['GET'])
def legacy_health():
    """兼容旧版健康检查接口"""
    return health_check()
