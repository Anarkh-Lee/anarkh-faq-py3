"""
FAQ业务服务层
处理FAQ相关的业务逻辑
"""
import logging
import time
from typing import List, Dict, Optional, Tuple
from .database import FAQRepository
from .model_manager import model_manager
from .qdrant_service import QdrantService

logger = logging.getLogger(__name__)

class FAQService:
    """FAQ业务服务"""
    
    def __init__(self):
        self.faq_repo = FAQRepository()
        self.qdrant_service = QdrantService()
        
    def initialize_full_data(self, recreate_collection: bool = True) -> Dict[str, any]:
        """
        全量数据初始化
        
        Args:
            recreate_collection: 是否重新创建集合（删除旧数据）
            
        Returns:
            包含初始化结果的字典
        """
        start_time = time.time()
        result = {
            "success": False,
            "message": "",
            "processed_count": 0,
            "total_count": 0,
            "execution_time": 0,
            "model_info": model_manager.get_model_info()
        }
        
        try:
            # 1. 检查模型是否加载
            if not model_manager.is_model_loaded():
                logger.info("Model not loaded, loading now...")
                if not model_manager.load_model():
                    result["message"] = "Failed to load embedding model"
                    return result
            
            # 2. 从数据库获取所有FAQ数据
            logger.info("Loading FAQs from database...")
            faqs = self.faq_repo.get_all_faqs()
            result["total_count"] = len(faqs)
            
            if not faqs:
                result["message"] = "No FAQ data found in database"
                result["success"] = True  # 技术上成功，但没有数据
                return result
            
            # 3. 生成向量
            logger.info(f"Generating embeddings for {len(faqs)} FAQs...")
            questions = [faq["question"] for faq in faqs]
            embeddings = model_manager.generate_embeddings(questions)
            
            if embeddings is None:
                result["message"] = "Failed to generate embeddings"
                return result
            
            # 4. 初始化Qdrant集合
            vector_size = embeddings.shape[1]
            logger.info(f"Initializing Qdrant collection with vector size: {vector_size}")
            
            if recreate_collection:
                if not self.qdrant_service.recreate_collection(vector_size):
                    result["message"] = "Failed to recreate Qdrant collection"
                    return result
            else:
                if not self.qdrant_service.ensure_collection_exists(vector_size):
                    result["message"] = "Failed to ensure Qdrant collection exists"
                    return result
            
            # 5. 批量插入向量数据
            logger.info("Upserting FAQ embeddings to Qdrant...")
            if not self.qdrant_service.upsert_points(faqs, embeddings):
                result["message"] = "Failed to upsert data to Qdrant"
                return result
            
            result["processed_count"] = len(faqs)
            result["success"] = True
            result["message"] = f"Successfully initialized {len(faqs)} FAQs"
            
        except Exception as e:
            logger.error(f"Error in full data initialization: {e}")
            result["message"] = f"Initialization failed: {str(e)}"
        
        finally:
            result["execution_time"] = round(time.time() - start_time, 2)
            
        return result
    
    def add_single_faq(self, faq_id: str, question: str, answer: str) -> Dict[str, any]:
        """
        添加单条FAQ数据
        
        Args:
            faq_id: FAQ唯一标识
            question: 问题
            answer: 答案
            
        Returns:
            包含添加结果的字典
        """
        start_time = time.time()
        result = {
            "success": False,
            "message": "",
            "faq_id": faq_id,
            "execution_time": 0,
            "model_info": model_manager.get_model_info()
        }
        
        try:
            # 1. 验证输入
            if not all([faq_id, question, answer]):
                result["message"] = "FAQ ID, question, and answer are required"
                return result
            
            # 2. 检查模型是否加载
            if not model_manager.is_model_loaded():
                logger.info("Model not loaded, loading now...")
                if not model_manager.load_model():
                    result["message"] = "Failed to load embedding model"
                    return result
            
            # 3. 添加到数据库
            logger.info(f"Adding FAQ to database: {faq_id}")
            if not self.faq_repo.add_faq(faq_id, question, answer):
                result["message"] = "Failed to add FAQ to database"
                return result
            
            # 4. 生成向量
            logger.info(f"Generating embedding for FAQ: {faq_id}")
            embeddings = model_manager.generate_embeddings([question])
            
            if embeddings is None or len(embeddings) == 0:
                result["message"] = "Failed to generate embedding"
                return result
            
            # 5. 确保Qdrant集合存在
            vector_size = embeddings.shape[1]
            if not self.qdrant_service.ensure_collection_exists(vector_size):
                result["message"] = "Failed to ensure Qdrant collection exists"
                return result
            
            # 6. 添加到Qdrant
            faq_data = {"id": faq_id, "question": question, "answer": answer}
            if not self.qdrant_service.upsert_single_point(faq_data, embeddings[0]):
                result["message"] = "Failed to add FAQ to Qdrant"
                return result
            
            result["success"] = True
            result["message"] = f"Successfully added FAQ: {faq_id}"
            
        except Exception as e:
            logger.error(f"Error adding single FAQ: {e}")
            result["message"] = f"Failed to add FAQ: {str(e)}"
        
        finally:
            result["execution_time"] = round(time.time() - start_time, 2)
            
        return result
    
    def search_faqs(self, query: str, limit: int = 5, similarity_threshold: float = 0.0) -> Dict[str, any]:
        """
        搜索FAQ
        
        Args:
            query: 查询文本
            limit: 返回结果数量限制
            similarity_threshold: 相似度阈值
            
        Returns:
            包含搜索结果的字典
        """
        start_time = time.time()
        result = {
            "success": False,
            "message": "",
            "query": query,
            "results": [],
            "execution_time": 0
        }
        
        try:
            # 1. 验证输入
            if not query.strip():
                result["message"] = "Query text is required"
                return result
            
            # 2. 检查模型是否加载
            if not model_manager.is_model_loaded():
                if not model_manager.load_model():
                    result["message"] = "Failed to load embedding model"
                    return result
            
            # 3. 生成查询向量
            query_embeddings = model_manager.generate_embeddings([query])
            if query_embeddings is None or len(query_embeddings) == 0:
                result["message"] = "Failed to generate query embedding"
                return result
            
            # 4. 在Qdrant中搜索
            search_results = self.qdrant_service.search_similar(
                query_embeddings[0], 
                limit=limit, 
                score_threshold=similarity_threshold
            )
            
            result["results"] = search_results
            result["success"] = True
            result["message"] = f"Found {len(search_results)} similar FAQs"
            
        except Exception as e:
            logger.error(f"Error searching FAQs: {e}")
            result["message"] = f"Search failed: {str(e)}"
        
        finally:
            result["execution_time"] = round(time.time() - start_time, 2)
            
        return result
    
    def get_all_faqs_from_qdrant(self) -> Dict[str, any]:
        """
        从Qdrant获取所有FAQ数据
        """
        try:
            points = self.qdrant_service.get_all_points()
            return {
                "success": True,
                "total_points": len(points),
                "points": points
            }
        except Exception as e:
            logger.error(f"Error getting all FAQs from Qdrant: {e}")
            return {
                "success": False,
                "message": f"Failed to get FAQs: {str(e)}",
                "total_points": 0,
                "points": []
            }
    
    def get_system_status(self) -> Dict[str, any]:
        """
        获取系统状态
        """
        try:
            # 数据库连接状态
            db_status = self.faq_repo.db.test_connection()
            
            # Qdrant连接状态
            qdrant_status = self.qdrant_service.connect()
            
            # 获取集合信息
            collection_info = self.qdrant_service.get_collection_info() if qdrant_status else None
            
            # 数据库FAQ数量
            db_faq_count = self.faq_repo.get_faq_count() if db_status else 0
            
            return {
                "success": True,
                "database": {
                    "connected": db_status,
                    "faq_count": db_faq_count
                },
                "qdrant": {
                    "connected": qdrant_status,
                    "collection_info": collection_info
                },
                "model": model_manager.get_model_info()
            }
            
        except Exception as e:
            logger.error(f"Error getting system status: {e}")
            return {
                "success": False,
                "message": f"Failed to get system status: {str(e)}"
            }
