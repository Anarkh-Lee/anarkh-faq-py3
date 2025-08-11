# 基于Qdrant实现FAQ智能检索系统

## 系统概述

FAQ智能检索系统基于向量相似度搜索技术，将传统的关键词匹配升级为语义理解匹配。系统通过将FAQ问题转换为高维向量表示，实现了更加精准和智能的问答检索。

### 核心技术原理

1. **语义向量化**: 使用`shibing624/text2vec-base-chinese`模型将问题文本转换为768维向量
2. **相似度计算**: 采用余弦相似度算法计算查询向量与FAQ向量的相似程度
3. **高效检索**: 利用Qdrant向量数据库的近似最近邻(ANN)算法实现毫秒级检索
4. **实时同步**: MySQL数据库作为数据源，与Qdrant向量库保持实时同步

### 系统架构图

```
用户查询 → 文本向量化 → Qdrant检索 → 相似度排序 → 返回结果
    ↓           ↓           ↓           ↓           ↓
  "电脑故障"  → [0.1,0.2...] → 向量匹配 → 按分数排序 → FAQ答案
```

### 数据流向

```mermaid
graph TD
    A[MySQL FAQ表] -->|数据初始化| B[向量化处理]
    B --> C[Qdrant向量库]
    D[用户查询] --> E[查询向量化]
    E --> F[Qdrant相似度检索]
    C --> F
    F --> G[结果排序与过滤]
    G --> H[返回FAQ答案]
``` ## 服务部署与启动

### 生产环境部署流程

#### 1. 环境准备
确保以下服务已正确安装并运行：
- **Python 3.8+**: 运行环境
- **MySQL 5.7+**: 数据存储
- **Qdrant**: 向量数据库服务
- **系统内存**: 建议4GB以上

#### 2. 一键自动化部署 (推荐)

**Linux生产环境**
```bash
# 自动化部署脚本 - 包含环境检查、依赖安装、服务配置
sudo bash scripts/deploy.sh

# 交互式配置数据库连接信息
bash scripts/config_helper.sh

# 启动系统服务
systemctl start faq-service
systemctl enable faq-service

# 验证服务状态
curl http://localhost:5000/health
```

**Windows开发环境**
```batch
# 一键启动脚本
scripts\start_service.bat

# 选择操作模式：
# 1. 初始化数据
# 2. 启动服务
# 3. 完整流程 (推荐)
```

#### 3. 手动部署流程 (高级用户)

**步骤1: 安装Python依赖**
```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖包
pip install -r requirements.txt
```

**步骤2: 配置系统参数**
```bash
# 编辑配置文件
vim src/faq_retrieval/config.py

# 主要配置项：
# - MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD
# - QDRANT_HOST, QDRANT_PORT
# - MODEL_NAME (嵌入模型)
```

**步骤3: 初始化向量数据**
```bash
# 从MySQL加载FAQ数据并生成向量
curl -X POST http://localhost:5000/api/v1/faqs/initialize \
  -H "Content-Type: application/json" \
  -d '{"recreate_collection": true}'
```

**步骤4: 启动API服务**
```bash
# 直接启动
python run.py

# 或使用gunicorn生产服务器
gunicorn -w 4 -b 0.0.0.0:5000 "src.faq_retrieval.app:create_app()"
```

### 4. 数据验证与测试

**验证向量数据初始化**
```bash
# 检查Qdrant集合状态
curl http://localhost:6333/collections/faq_sm06

# 预期返回：
{
  "result": {
    "status": "green",
    "vectors_count": 1000,  # 实际FAQ数量
    "points_count": 1000
  }
}
```

**测试API接口**
```bash
# 1. 健康检查
curl http://localhost:5000/health

# 2. 智能检索测试
curl -X POST http://localhost:5000/api/v1/faqs/search \
  -H "Content-Type: application/json" \
  -d '{
    "text": "如何维修电脑？",
    "similarity": 0.15,
    "limit": 5
  }'

# 预期返回格式：
{
  "results": [
    {
      "faq_id": "faq_001",
      "question": "电脑坏了怎么办？",
      "answer": "找售后人员进行维修",
      "score": 0.8525
    }
  ]
}
```

## 技术实现细节

### 向量化处理流程

1. **文本预处理**
   - 去除特殊字符和多余空格
   - 统一文本编码格式
   - 长度限制处理 (最大512字符)

2. **模型推理**
   - 使用`shibing624/text2vec-base-chinese`模型
   - 批量处理优化 (批次大小: 32)
   - 生成768维稠密向量

3. **向量存储**
   - Qdrant使用余弦距离算法
   - 自动索引优化
   - 支持增量更新

### 检索算法优化

**相似度计算**
```python
# 余弦相似度公式
similarity = dot(query_vector, faq_vector) / 
             (norm(query_vector) * norm(faq_vector))

# 分数范围: [-1, 1]，值越大越相似
```

**搜索策略**
- **阈值过滤**: 可配置最低相似度阈值 (默认0.0)
- **结果排序**: 按相似度分数降序排列
- **数量限制**: 可配置返回结果数量 (最大50条)

### 性能优化策略

1. **模型单例模式**: 全局共享模型实例，避免重复加载
2. **连接池管理**: 数据库连接复用，减少连接开销
3. **批量处理**: 初始化时使用批量向量化和插入
4. **缓存机制**: 模型文件本地缓存，支持离线运行
5. **异步处理**: 支持并发请求处理

## 运维监控

### 服务管理

**systemd服务配置**
```bash
# 查看服务状态
systemctl status faq-service

# 服务日志监控
journalctl -u faq-service -f --since "1 hour ago"

# 性能监控
top -p $(pgrep -f "faq_retrieval")
```

**运维管理工具**
```bash
# 交互式管理界面
bash scripts/service_manager.sh

# 功能菜单:
# 1. 服务状态检查
# 2. 启动/停止/重启服务
# 3. 查看系统日志
# 4. 数据初始化
# 5. 系统监控
```

### 监控指标

**关键性能指标 (KPI)**
- **响应时间**: API接口平均响应时间 < 100ms
- **检索精度**: Top-5准确率 > 85%
- **服务可用性**: 99.9%正常运行时间
- **并发处理**: 支持100+并发请求

**健康检查指标**
```json
{
  "database": {
    "connected": true,
    "faq_count": 1000,
    "response_time_ms": 15
  },
  "qdrant": {
    "connected": true,
    "vectors_count": 1000,
    "index_status": "green"
  },
  "model": {
    "is_loaded": true,
    "memory_usage_mb": 1024,
    "device": "cpu"
  }
}
```

## 故障排查指南

### 常见问题解决

**问题1: 模型下载失败**
```bash
# 症状: 首次启动时模型下载超时
# 解决: 手动下载模型文件
wget https://huggingface.co/shibing624/text2vec-base-chinese/resolve/main/pytorch_model.bin
# 放置到: .cache/huggingface/models--shibing624--text2vec-base-chinese/
```

**问题2: Qdrant连接失败**
```bash
# 症状: "Failed to connect to Qdrant"
# 检查: Qdrant服务状态
systemctl status qdrant
# 解决: 启动Qdrant服务
systemctl start qdrant
```

**问题3: 检索结果为空**
```bash
# 症状: 搜索返回空结果
# 检查: 数据是否正确初始化
curl http://localhost:6333/collections/faq_sm06/points/scroll
# 解决: 重新初始化数据
curl -X POST http://localhost:5000/api/v1/faqs/initialize
```

**问题4: 内存占用过高**
```bash
# 症状: 系统内存不足
# 解决: 调整模型设备配置
export CUDA_VISIBLE_DEVICES=""  # 强制使用CPU
# 或增加系统内存/使用GPU
```

---

**系统维护建议**: 
- 定期备份MySQL数据库
- 监控Qdrant向量库大小
- 定期清理日志文件
- 监控服务器资源使用情况