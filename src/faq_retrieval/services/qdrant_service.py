"""
Qdrant向量数据库服务
"""
import logging
import time
from typing import List, Dict, Optional
from qdrant_client import QdrantClient, models
from qdrant_client.http.models import PointStruct, Distance, VectorParams, ScrollRequest
import numpy as np
from ..config import config

logger = logging.getLogger(__name__)

class QdrantService:
    """Qdrant向量数据库服务"""
    
    def __init__(self):
        self.host = config.QDRANT_HOST
        self.port = config.QDRANT_PORT
        self.collection_name = config.COLLECTION_NAME
        self.client: Optional[QdrantClient] = None
    
    def connect(self) -> bool:
        """连接到Qdrant服务器"""
        try:
            if self.client is None:
                logger.info(f"Connecting to Qdrant at {self.host}:{self.port}")
                self.client = QdrantClient(host=self.host, port=self.port, timeout=30)
                
                # 测试连接
                self.client.get_collections()
                logger.info("Connected to Qdrant successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant: {e}")
            self.client = None
            return False
    
    def ensure_collection_exists(self, vector_size: int) -> bool:
        """确保集合存在"""
        if not self.connect():
            return False
        
        try:
            # 检查集合是否存在
            try:
                collection_info = self.client.get_collection(collection_name=self.collection_name)
                logger.info(f"Collection '{self.collection_name}' already exists")
                return True
            except Exception:
                # 集合不存在，创建新集合
                logger.info(f"Creating collection '{self.collection_name}' with vector size {vector_size}")
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=vector_size,
                        distance=Distance.COSINE
                    ),
                    timeout=60
                )
                logger.info(f"Collection '{self.collection_name}' created successfully")
                return True
                
        except Exception as e:
            logger.error(f"Error ensuring collection exists: {e}")
            return False
    
    def recreate_collection(self, vector_size: int) -> bool:
        """重新创建集合（删除旧数据）"""
        if not self.connect():
            return False
        
        try:
            # 尝试删除现有集合
            try:
                self.client.delete_collection(collection_name=self.collection_name, timeout=60)
                logger.info(f"Deleted existing collection '{self.collection_name}'")
                time.sleep(1)  # 等待删除完成
            except Exception:
                logger.info(f"Collection '{self.collection_name}' does not exist, creating new one")
            
            # 创建新集合
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE
                ),
                timeout=60
            )
            logger.info(f"Collection '{self.collection_name}' recreated successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error recreating collection: {e}")
            return False
    
    def upsert_points(self, faqs: List[Dict], embeddings: np.ndarray) -> bool:
        """批量插入或更新向量点"""
        if not self.connect():
            return False
        
        if len(faqs) != len(embeddings):
            logger.error("FAQs and embeddings length mismatch")
            return False
        
        try:
            points_to_upload = []
            for i, faq in enumerate(faqs):
                embedding_list = embeddings[i].tolist()
                
                points_to_upload.append(
                    PointStruct(
                        id=hash(faq["id"]) % (2**31),  # 使用FAQ ID的哈希作为Qdrant点ID
                        vector=embedding_list,
                        payload={
                            "faq_id": faq["id"],
                            "question": faq["question"],
                            "answer": faq["answer"]
                        }
                    )
                )
            
            # 分批上传
            batch_size = 100
            total_batches = (len(points_to_upload) + batch_size - 1) // batch_size
            
            for i in range(0, len(points_to_upload), batch_size):
                batch = points_to_upload[i:i + batch_size]
                batch_num = i // batch_size + 1
                
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=batch,
                    wait=True
                )
                logger.info(f"Upserted batch {batch_num}/{total_batches}")
            
            logger.info(f"Successfully upserted {len(points_to_upload)} points")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting points: {e}")
            return False
    
    def upsert_single_point(self, faq: Dict, embedding: np.ndarray) -> bool:
        """插入或更新单个向量点"""
        if not self.connect():
            return False
        
        try:
            point = PointStruct(
                id=hash(faq["id"]) % (2**31),
                vector=embedding.tolist(),
                payload={
                    "faq_id": faq["id"],
                    "question": faq["question"],
                    "answer": faq["answer"]
                }
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point],
                wait=True
            )
            
            logger.info(f"Successfully upserted point for FAQ ID: {faq['id']}")
            return True
            
        except Exception as e:
            logger.error(f"Error upserting single point: {e}")
            return False
    
    def search_similar(self, query_vector: np.ndarray, limit: int = 5, score_threshold: float = 0.0) -> List[Dict]:
        """搜索相似向量"""
        if not self.connect():
            return []
        
        try:
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector.tolist(),
                limit=limit,
                score_threshold=score_threshold
            )
            
            results = []
            for scored_point in search_result:
                results.append({
                    "faq_id": scored_point.payload.get("faq_id"),
                    "question": scored_point.payload.get("question"),
                    "answer": scored_point.payload.get("answer"),
                    "score": scored_point.score
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Error searching similar vectors: {e}")
            return []
    
    def get_all_points(self) -> List[Dict]:
        """获取所有向量点"""
        if not self.connect():
            return []
        
        try:
            all_points = []
            offset = None
            
            while True:
                scroll_result = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=None,
                    limit=100,
                    offset=offset,
                    with_payload=True,
                    with_vectors=False
                )
                
                points, next_offset = scroll_result
                
                for point in points:
                    all_points.append({
                        "id": point.id,
                        "faq_id": point.payload.get("faq_id"),
                        "question": point.payload.get("question"),
                        "answer": point.payload.get("answer")
                    })
                
                if next_offset is None:
                    break
                offset = next_offset
            
            logger.info(f"Retrieved {len(all_points)} points from collection")
            return all_points
            
        except Exception as e:
            logger.error(f"Error getting all points: {e}")
            return []
    
    def get_collection_info(self) -> Optional[Dict]:
        """获取集合信息"""
        if not self.connect():
            return None
        
        try:
            collection_info = self.client.get_collection(collection_name=self.collection_name)
            return {
                "name": self.collection_name,
                "vectors_count": collection_info.vectors_count,
                "points_count": collection_info.points_count,
                "status": collection_info.status,
                "optimizer_status": collection_info.optimizer_status
            }
        except Exception as e:
            logger.error(f"Error getting collection info: {e}")
            return None
