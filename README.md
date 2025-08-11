# FAQ智能检索服务

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-orange.svg)](https://github.com/yourusername/faq-retrieval-service)

## 项目概述

FAQ智能检索服务是一个基于深度学习的企业级智能问答系统，提供高性能的语义检索和FAQ管理功能。系统采用微服务架构，支持大规模数据处理和高并发访问。

### 核心特性

- 🚀 **高性能语义检索**: 基于`shibing624/text2vec-base-chinese`模型，提供毫秒级检索响应
- 🔄 **实时数据同步**: 支持MySQL数据库与向量数据库的实时同步
- 🌐 **RESTful API**: 完整的API接口，支持前后端分离架构
- 🛡️ **高可用部署**: 支持生产环境部署，包含健康检查和监控
- 📊 **智能相似度匹配**: 可配置相似度阈值，精确控制检索结果
- 🔧 **跨平台支持**: 支持Windows、Linux多平台部署

## 技术架构

### 技术栈
- **应用框架**: Python 3.8+ + Flask
- **向量数据库**: Qdrant (分布式向量搜索引擎)
- **关系数据库**: MySQL 5.7+ (数据持久化)
- **NLP模型**: sentence-transformers (shibing624/text2vec-base-chinese)
- **部署方案**: Docker / systemd (Linux) / 批处理脚本 (Windows)
- **监控**: 内置健康检查接口

### 系统架构
```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   前端应用      │───▶│   Flask API     │───▶│   MySQL数据库   │
│   (Web/Mobile)  │    │   (业务逻辑)    │    │   (数据存储)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │  Sentence       │───▶│   Qdrant向量库  │
                       │  Transformers   │    │   (语义检索)    │
                       │  (向量化模型)   │    │                 │
                       └─────────────────┘    └─────────────────┘
```

## 快速开始

### 环境要求
- **Python**: 3.8 或更高版本
- **内存**: 建议 4GB 以上 (模型加载需要)
- **存储**: 建议 10GB 以上可用空间
- **网络**: 首次运行需要网络下载模型

### 一键部署 (推荐)

#### Linux 生产环境部署
```bash
# 1. 克隆项目
git clone <repository-url>
cd anarkh-faq-py3

# 2. 一键部署脚本
sudo bash scripts/deploy.sh

# 3. 配置数据库连接
bash scripts/config_helper.sh

# 4. 启动服务
systemctl start faq-service
systemctl enable faq-service

# 5. 验证服务状态
curl http://localhost:5000/health

# 6. 初始化数据
curl -X POST http://localhost:5000/api/v1/faqs/initialize
```

#### Windows 开发环境
```batch
# 1. 双击运行启动脚本
scripts\start_service.bat

# 2. 根据菜单选择操作：
#    选择 "1" - 仅初始化数据
#    选择 "2" - 仅启动API服务  
#    选择 "3" - 完整流程（推荐）
```

#### Linux 开发环境
```bash
# 1. 赋予执行权限并运行
chmod +x scripts/start_service.sh
./scripts/start_service.sh

# 2. 根据交互式菜单选择操作
```

### Docker 部署 (推荐生产环境)
```bash
# 1. 构建镜像
docker build -t faq-retrieval-service .

# 2. 运行服务
docker run -d \
  --name faq-service \
  -p 5000:5000 \
  -e MYSQL_HOST=your_mysql_host \
  -e MYSQL_USER=your_mysql_user \
  -e MYSQL_PASSWORD=your_mysql_password \
  -e QDRANT_HOST=your_qdrant_host \
  faq-retrieval-service

# 3. 查看服务状态
docker logs faq-service
```

## 配置说明

### 核心配置文件

#### 1. 数据库配置 (`src/faq_retrieval/config.py`)
```python
# MySQL 数据库配置
MYSQL_HOST = "localhost"        # 数据库主机
MYSQL_PORT = 3306              # 数据库端口
MYSQL_USER = "root"            # 数据库用户名
MYSQL_PASSWORD = "password"    # 数据库密码
MYSQL_DATABASE = "anarkh"      # 数据库名称

# Qdrant 向量数据库配置
QDRANT_HOST = "localhost"      # Qdrant主机
QDRANT_PORT = 6333            # Qdrant端口
COLLECTION_NAME = "faq_sm06"   # 集合名称
```

#### 2. 模型配置
```python
# 嵌入模型配置
MODEL_NAME = 'shibing624/text2vec-base-chinese'

# 模型缓存目录 (自动创建)
HF_CACHE_DIR = ".cache/huggingface"
TRANSFORMERS_CACHE_DIR = ".cache/transformers"
```

#### 3. 服务配置
```python
# Flask 服务配置
FLASK_HOST = "0.0.0.0"    # 监听地址
FLASK_PORT = 5000         # 监听端口
FLASK_DEBUG = False       # 调试模式
```

### 环境变量配置
支持通过环境变量覆盖配置文件设置：
```bash
export MYSQL_HOST=your_database_host
export MYSQL_PASSWORD=your_secure_password
export QDRANT_HOST=your_qdrant_host
export FLASK_PORT=8080
```

### 数据库表结构
系统需要以下MySQL表结构：
```sql
CREATE TABLE `faq` (
  `id` varchar(50) NOT NULL PRIMARY KEY,
  `question` text NOT NULL,
  `answer` text NOT NULL,
  `created_at` timestamp DEFAULT CURRENT_TIMESTAMP,
  `updated_at` timestamp DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY `idx_question` (`question`(255))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## API 接口概览

### RESTful API 设计
所有API遵循RESTful设计原则，统一返回JSON格式数据。

#### 基础信息
- **服务地址**: `http://localhost:5000`
- **API版本**: v1
- **认证方式**: 暂无（可扩展JWT等认证机制）
- **限流策略**: 可配置（建议生产环境启用）

#### 核心接口

| 接口 | 方法 | 路径 | 功能 |
|------|------|------|------|
| 健康检查 | GET | `/health` | 检查服务状态 |
| 初始化数据 | POST | `/api/v1/faqs/initialize` | 全量数据初始化 |
| 添加FAQ | POST | `/api/v1/faqs` | 添加单条FAQ |
| 搜索FAQ | POST | `/api/v1/faqs/search` | 智能检索FAQ |
| 获取全部FAQ | GET | `/api/v1/faqs` | 获取所有FAQ数据 |
| 模型信息 | GET | `/api/v1/model/info` | 获取模型状态 |

#### 快速测试
```bash
# 1. 健康检查
curl -X GET http://localhost:5000/health

# 2. 智能搜索
curl -X POST http://localhost:5000/api/v1/faqs/search \
  -H "Content-Type: application/json" \
  -d '{"text": "如何维修电脑？", "limit": 5}'

# 3. 获取所有FAQ
curl -X GET http://localhost:5000/api/v1/faqs
```

### 兼容性API
为保持向后兼容，系统同时支持旧版本API：
- `GET /list-all` → `GET /api/v1/faqs`
- `POST /search` → `POST /api/v1/faqs/search`

详细API文档请参考：[API接口文档](docs/API_DOCUMENTATION.md)

## 项目结构

```
anarkh-faq-py3/
├── 📁 src/                          # 源代码目录
│   └── faq_retrieval/              # 主应用包
│       ├── __init__.py             # 包初始化
│       ├── app.py                  # Flask应用入口
│       ├── config.py               # 配置管理
│       ├── 📁 api/                 # API路由层
│       │   ├── __init__.py
│       │   └── routes.py           # RESTful API定义
│       ├── 📁 services/            # 业务逻辑层
│       │   ├── __init__.py
│       │   ├── database.py         # 数据访问层
│       │   ├── faq_service.py      # FAQ业务服务
│       │   ├── model_manager.py    # 模型管理服务
│       │   └── qdrant_service.py   # 向量数据库服务
│       └── 📁 models/              # 数据模型(待扩展)
├── 📁 scripts/                     # 部署和管理脚本
│   ├── deploy.sh                   # Linux生产环境部署
│   ├── config_helper.sh            # 配置助手
│   ├── service_manager.sh          # 服务管理工具
│   ├── start_service.sh            # Linux启动脚本
│   ├── start_service.bat           # Windows启动脚本
│   └── check_python_env.sh         # 环境检查
├── 📁 docs/                        # 项目文档
│   ├── API_DOCUMENTATION.md        # API接口文档
│   ├── 基于Qdrant实现常用问题检索功能.md
│   ├── CentOS 7 简单部署指南.md
│   └── Centos7安装Python3.8.md
├── 📁 tests/                       # 测试用例
│   ├── __init__.py
│   └── test_mysql.py
├── 📄 requirements.txt             # Python依赖列表
├── 📄 setup.py                     # 安装配置
├── 📄 run.py                       # 服务启动入口
└── 📄 README.md                    # 项目说明文档
```

### 代码架构说明

#### 分层架构
- **API层** (`api/`): 处理HTTP请求，参数验证，响应格式化
- **服务层** (`services/`): 核心业务逻辑，事务处理，数据转换
- **数据层** (`services/database.py`): 数据持久化，数据库操作封装
- **配置层** (`config.py`): 统一配置管理，环境变量处理

#### 核心组件
- **FAQService**: FAQ业务逻辑处理
- **ModelManager**: 嵌入模型生命周期管理
- **QdrantService**: 向量数据库操作封装
- **MySQLConnection**: 关系数据库连接管理

## 运维管理

### 服务管理命令

#### systemd 服务管理 (Linux生产环境)
```bash
# 启动服务
sudo systemctl start faq-service

# 停止服务
sudo systemctl stop faq-service

# 重启服务
sudo systemctl restart faq-service

# 查看服务状态
sudo systemctl status faq-service

# 查看服务日志
sudo journalctl -u faq-service -f

# 设置开机自启
sudo systemctl enable faq-service
```

#### 运维管理工具
使用集成的管理工具进行服务管理：
```bash
bash scripts/service_manager.sh
```

功能包括：
- 🔍 服务状态检查
- 🚀 服务启动/停止/重启
- 📊 系统资源监控
- 🔄 数据初始化
- 📋 日志查看
- ⚙️ 配置管理

### 监控和健康检查

#### 健康检查端点
```bash
# 基础健康检查
curl http://localhost:5000/health

# 返回示例
{
  "success": true,
  "database": {"connected": true, "faq_count": 1000},
  "qdrant": {"connected": true, "vectors_count": 1000},
  "model": {"is_loaded": true, "device": "cpu"}
}
```

#### 日志管理
- **应用日志**: 自动记录API请求、错误信息、性能指标
- **日志级别**: INFO, WARNING, ERROR
- **日志轮转**: 建议配置logrotate进行日志轮转

#### 性能监控
- **响应时间**: API接口响应时间监控
- **内存使用**: 模型加载后内存占用监控
- **并发处理**: 支持多线程并发请求处理

### 故障排查

#### 常见问题及解决方案

1. **模型加载失败**
   ```bash
   # 检查模型缓存目录
   ls -la .cache/huggingface/
   
   # 清理缓存重新下载
   rm -rf .cache/huggingface/
   python run.py
   ```

2. **数据库连接失败**
   ```bash
   # 检查数据库配置
   python -c "from src.faq_retrieval.config import config; print(config.MYSQL_HOST)"
   
   # 测试数据库连接
   mysql -h localhost -u root -p anarkh
   ```

3. **Qdrant连接失败**
   ```bash
   # 检查Qdrant服务状态
   curl http://localhost:6333/health
   
   # 查看集合信息
   curl http://localhost:6333/collections
   ```

4. **服务启动失败**
   ```bash
   # 检查端口占用
   netstat -tulpn | grep 5000
   
   # 查看详细错误日志
   python run.py
   ```

## 开发指南

### 本地开发环境搭建

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd anarkh-faq-py3
   ```

2. **创建虚拟环境**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # 或
   venv\Scripts\activate     # Windows
   ```

3. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

4. **配置开发环境**
   ```bash
   # 复制配置文件并修改
   cp src/faq_retrieval/config.py src/faq_retrieval/config_dev.py
   # 修改数据库连接信息
   ```

5. **启动开发服务器**
   ```bash
   python run.py
   ```

### 代码贡献指南

#### 代码规范
- **Python**: 遵循PEP 8标准
- **命名**: 使用有意义的变量和函数名
- **注释**: 关键业务逻辑必须添加注释
- **类型提示**: 新代码建议添加类型注解

#### 测试要求
```bash
# 运行单元测试
python -m pytest tests/

# 运行API测试
python tests/test_api.py

# 代码覆盖率检查
python -m pytest --cov=src/faq_retrieval tests/
```

#### 提交规范
```bash
# 提交消息格式
git commit -m "type(scope): description"

# 示例
git commit -m "feat(api): add FAQ batch import interface"
git commit -m "fix(database): handle connection timeout"
git commit -m "docs(readme): update deployment guide"
```

### 扩展开发

#### 添加新的API接口
1. 在 `src/faq_retrieval/api/routes.py` 中添加路由
2. 在 `src/faq_retrieval/services/` 中实现业务逻辑
3. 添加相应的测试用例
4. 更新API文档

#### 集成新的嵌入模型
1. 修改 `src/faq_retrieval/services/model_manager.py`
2. 更新配置文件中的模型参数
3. 测试模型兼容性

#### 添加新的数据源
1. 在 `src/faq_retrieval/services/` 中创建新的数据访问类
2. 实现统一的数据接口
3. 更新FAQ服务层以支持新数据源

## 许可证

本项目采用 MIT 许可证。详细信息请查看 [LICENSE](LICENSE) 文件。

## 联系方式

- **项目维护者**: [Your Name](mailto:your.email@example.com)
- **技术支持**: [Support Email](mailto:support@example.com)
- **问题反馈**: [GitHub Issues](https://github.com/yourusername/faq-retrieval-service/issues)

## 更新日志

### v1.0.0 (2025-08-08)
- ✨ 初始版本发布
- 🚀 基础FAQ检索功能
- 📚 完整的API接口
- 🛠️ 自动化部署脚本
- 📖 详细的文档说明

---

**感谢使用FAQ智能检索服务！** 如果您觉得这个项目对您有帮助，请给我们一个 ⭐ Star！
