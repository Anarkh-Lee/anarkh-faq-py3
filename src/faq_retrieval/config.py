"""
配置文件 - 统一管理项目配置
支持Windows和Linux环境
"""
import os
import platform
from pathlib import Path

class Config:
    def __init__(self):
        # 获取项目根目录 (从src/faq_retrieval/ 回到项目根目录)
        self.PROJECT_ROOT = Path(__file__).parent.parent.parent
        
        # 检测操作系统
        self.OS_TYPE = platform.system().lower()
        
        # 设置缓存目录
        self._setup_cache_dirs()
        
        # 设置环境变量
        self._setup_environment_variables()
    
    def _setup_cache_dirs(self):
        """设置缓存目录"""
        cache_base = self.PROJECT_ROOT / ".cache"
        
        self.HF_CACHE_DIR = cache_base / "huggingface"
        self.TRANSFORMERS_CACHE_DIR = cache_base / "transformers"
        
        # 创建缓存目录（如果不存在）
        self.HF_CACHE_DIR.mkdir(parents=True, exist_ok=True)
        self.TRANSFORMERS_CACHE_DIR.mkdir(parents=True, exist_ok=True)
    
    def _setup_environment_variables(self):
        """设置环境变量"""
        # 设置HuggingFace缓存路径
        os.environ['HF_HUB_CACHE'] = str(self.HF_CACHE_DIR)
        os.environ['TRANSFORMERS_CACHE'] = str(self.TRANSFORMERS_CACHE_DIR)
        
        # 设置HuggingFace离线模式（启用以使用本地模型）
        os.environ['HF_HUB_OFFLINE'] = '1'
        os.environ['TRANSFORMERS_OFFLINE'] = '1'
        os.environ['HF_DATASETS_OFFLINE'] = '1'
        
        # 设置PyTorch设备
        if 'CUDA_VISIBLE_DEVICES' not in os.environ:
            os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # 默认使用第一块GPU
    
    def get_local_model_path(self):
        """获取本地模型路径"""
        # 对于sentence-transformers，模型通常存储在HuggingFace缓存中
        model_cache_path = self.HF_CACHE_DIR / "models--shibing624--text2vec-base-chinese"
        if model_cache_path.exists():
            # 查找最新的快照目录
            snapshots_dir = model_cache_path / "snapshots"
            if snapshots_dir.exists():
                # 获取第一个（通常是最新的）快照目录
                snapshot_dirs = list(snapshots_dir.iterdir())
                if snapshot_dirs:
                    snapshot_path = snapshot_dirs[0]
                    # 检查sentence-transformers必需的文件是否存在
                    required_files = ['modules.json', 'sentence_bert_config.json', 'config.json']
                    if all((snapshot_path / file).exists() for file in required_files):
                        print(f"✅ Found local model at: {snapshot_path}")
                        return str(snapshot_path)
        
        # 如果本地缓存不完整，仍然返回缓存路径供模型管理器处理
        print(f"⚠️ Local model cache incomplete, returning cache path: {model_cache_path}")
        return str(model_cache_path)
    
    # Qdrant配置
    QDRANT_HOST = "10.4.118.159"
    QDRANT_PORT = 6333
    COLLECTION_NAME = "faq_sm06"
    
    # 模型配置
    MODEL_NAME = 'shibing624/text2vec-base-chinese'
    
    # MySQL数据库配置
    MYSQL_HOST = "10.4.118.159"
    MYSQL_PORT = 3306
    MYSQL_USER = "root"
    MYSQL_PASSWORD = "123456"
    MYSQL_DATABASE = "anarkh"  # 请根据实际数据库名称修改
    MYSQL_CHARSET = "utf8mb4"
    
    def get_flask_config(self):
        """获取Flask应用配置"""
        return {
            'DEBUG': False,
            'HOST': '0.0.0.0',
            'PORT': 5000,
            'THREADED': True
        }

# 创建全局配置实例
config = Config()
