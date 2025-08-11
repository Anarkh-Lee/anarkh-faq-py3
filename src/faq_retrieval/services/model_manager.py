"""
模型管理器 - 单例模式管理sentence transformer模型
避免重复加载模型，提高性能
"""
import logging
import os
import torch
from sentence_transformers import SentenceTransformer
from typing import Optional, List
import numpy as np
import threading
from pathlib import Path
from ..config import config

logger = logging.getLogger(__name__)

class ModelManager:
    """
    模型管理器 - 单例模式
    确保整个应用程序中只有一个模型实例，避免重复加载
    """
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(ModelManager, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self.model: Optional[SentenceTransformer] = None
            self.device = None
            self.model_name = config.MODEL_NAME
            self.local_model_path = config.get_local_model_path()
            self._model_lock = threading.Lock()
            self._initialized = True
    
    def load_model(self) -> bool:
        """加载模型 - 强制使用本地模型，不连接在线服务"""
        if self.model is not None:
            logger.info("Model already loaded, skipping...")
            return True
        
        with self._model_lock:
            if self.model is not None:  # 双重检查
                return True
            
            try:
                # 检测设备
                self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
                logger.info(f"Loading model on device: {self.device}")
                
                # 强制使用本地模型路径
                local_model = self.local_model_path
                logger.info(f"Attempting to load model from local path: {local_model}")
                
                # 检查本地模型是否存在
                from pathlib import Path
                if not Path(local_model).exists() and local_model != self.model_name:
                    logger.error(f"Local model path does not exist: {local_model}")
                    logger.error("Please download the model first or check cache directory")
                    return False
                
                # 设置离线模式环境变量（确保不会连接在线）
                import os
                os.environ['HF_HUB_OFFLINE'] = '1'
                os.environ['TRANSFORMERS_OFFLINE'] = '1'
                os.environ['HF_DATASETS_OFFLINE'] = '1'
                
                try:
                    # 尝试加载本地模型
                    logger.info(f"Loading model from local cache: {local_model}")
                    self.model = SentenceTransformer(local_model, device=self.device)
                    logger.info("✅ Model loaded successfully from local cache")
                    return True
                    
                except Exception as local_error:
                    logger.error(f"Failed to load from local path: {local_error}")
                    
                    # 如果本地路径就是模型名称，尝试从缓存目录加载
                    if local_model == self.model_name:
                        # 查找可能的缓存目录
                        cache_paths = [
                            Path(config.HF_CACHE_DIR) / "models--shibing624--text2vec-base-chinese",
                            Path.home() / ".cache" / "huggingface" / "transformers" / "models--shibing624--text2vec-base-chinese",
                            Path(".cache") / "huggingface" / "models--shibing624--text2vec-base-chinese"
                        ]
                        
                        for cache_path in cache_paths:
                            if cache_path.exists():
                                snapshots_dir = cache_path / "snapshots"
                                if snapshots_dir.exists():
                                    snapshot_dirs = list(snapshots_dir.iterdir())
                                    if snapshot_dirs:
                                        snapshot_path = snapshot_dirs[0]
                                        try:
                                            logger.info(f"Trying cache directory: {snapshot_path}")
                                            self.model = SentenceTransformer(str(snapshot_path), device=self.device)
                                            logger.info("✅ Model loaded successfully from cache directory")
                                            return True
                                        except Exception as cache_error:
                                            logger.warning(f"Failed to load from cache {snapshot_path}: {cache_error}")
                                            continue
                    
                    # 如果所有本地加载都失败，报错而不是尝试在线下载
                    logger.error("❌ All local model loading attempts failed")
                    logger.error("Please ensure the model is properly cached or download it manually")
                    logger.error("Model loading failed - refusing to connect to online services")
                    return False
                
            except Exception as e:
                logger.error(f"❌ Failed to load model: {e}")
                self.model = None
                return False
    
    def get_model(self) -> Optional[SentenceTransformer]:
        """获取模型实例"""
        if self.model is None:
            if not self.load_model():
                return None
        return self.model
    
    def is_model_loaded(self) -> bool:
        """检查模型是否已加载"""
        return self.model is not None
    
    def generate_embeddings(self, texts: List[str], batch_size: int = 32) -> Optional[np.ndarray]:
        """生成文本向量"""
        if not texts:
            logger.warning("No texts provided for embedding generation")
            return None
        
        model = self.get_model()
        if model is None:
            logger.error("Model not available for embedding generation")
            return None
        
        try:
            logger.info(f"Generating embeddings for {len(texts)} texts")
            embeddings = model.encode(
                texts, 
                show_progress_bar=True, 
                batch_size=batch_size,
                convert_to_numpy=True
            )
            logger.info(f"Generated embeddings with shape: {embeddings.shape}")
            return embeddings
            
        except Exception as e:
            logger.error(f"Error generating embeddings: {e}")
            return None
    
    def get_model_info(self) -> dict:
        """获取模型信息"""
        return {
            "model_name": self.model_name,
            "local_model_path": self.local_model_path,
            "device": self.device,
            "is_loaded": self.is_model_loaded(),
            "model_type": type(self.model).__name__ if self.model else None
        }

# 全局模型管理器实例
model_manager = ModelManager()
