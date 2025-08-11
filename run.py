#!/usr/bin/env python3
"""
FAQ检索服务启动脚本
"""
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from faq_retrieval.app import main

if __name__ == "__main__":
    main()
