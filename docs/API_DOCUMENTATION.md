# FAQ智能检索服务 API 接口文档

[![API Version](https://img.shields.io/badge/API%20Version-v1.0-blue.svg)](/)
[![Status](https://img.shields.io/badge/Status-Stable-green.svg)](/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](/)

## 概述

FAQ智能检索服务提供企业级的智能问答API接口，基于深度学习的语义理解技术，支持高精度的FAQ检索、数据管理和系统监控功能。

### 核心功能
- 🔍 **智能语义检索**: 基于向量相似度的FAQ智能匹配
- 📊 **数据管理**: 支持FAQ数据的增删改查操作
- 🔄 **实时同步**: MySQL数据库与向量数据库实时同步
- 📈 **系统监控**: 完整的健康检查和性能监控
- 🚀 **高性能**: 毫秒级响应时间，支持高并发访问

## 基础信息

| 配置项 | 值 | 说明 |
|--------|----|----|
| **服务地址** | `http://localhost:5000` | 默认本地服务地址 |
| **API版本** | `v1` | 当前API版本 |
| **请求格式** | `application/json` | 请求Content-Type |
| **响应格式** | `JSON` | 统一JSON响应格式 |
| **字符编码** | `UTF-8` | 统一字符编码 |
| **超时时间** | `30秒` | 默认请求超时时间 |

## API 接口清单

### 🔍 核心检索接口

| 接口名称 | HTTP方法 | 路径 | 功能描述 |
|---------|---------|------|---------|
| [健康检查](#1-健康检查) | `GET` | `/health` | 检查服务运行状态 |
| [智能搜索](#4-搜索faq) | `POST` | `/api/v1/faqs/search` | 基于语义的FAQ检索 |
| [获取全部FAQ](#5-获取所有faq) | `GET` | `/api/v1/faqs` | 获取所有FAQ数据 |

### 🛠️ 数据管理接口

| 接口名称 | HTTP方法 | 路径 | 功能描述 |
|---------|---------|------|---------|
| [全量数据初始化](#2-全量数据初始化) | `POST` | `/api/v1/faqs/initialize` | 从MySQL初始化向量数据 |
| [添加单条FAQ](#3-添加单条faq) | `POST` | `/api/v1/faqs` | 新增FAQ条目 |

### 📊 系统监控接口

| 接口名称 | HTTP方法 | 路径 | 功能描述 |
|---------|---------|------|---------|
| [模型信息](#6-获取模型信息) | `GET` | `/api/v1/model/info` | 获取嵌入模型状态 |

### 🔄 兼容性接口

| 接口名称 | HTTP方法 | 路径 | 对应新接口 |
|---------|---------|------|----------|
| 搜索(兼容) | `POST` | `/search` | `/api/v1/faqs/search` |
| 列表(兼容) | `GET` | `/list-all` | `/api/v1/faqs` |

---

## 详细接口说明

### 1. 健康检查
> **用途**: 检查服务运行状态和各组件连接情况，用于负载均衡健康检查和系统监控

```http
GET /health
```

**请求示例**:
```bash
curl -X GET http://localhost:5000/health
```

**响应示例**:
```json
{
    "success": true,
    "timestamp": "2025-08-08T12:30:45Z",
    "version": "1.0.0",
    "uptime_seconds": 3600,
    "database": {
        "connected": true,
        "faq_count": 1000,
        "response_time_ms": 15,
        "last_sync": "2025-08-08T12:00:00Z"
    },
    "qdrant": {
        "connected": true,
        "collection_info": {
            "name": "faq_sm06",
            "vectors_count": 1000,
            "points_count": 1000,
            "status": "green",
            "optimizer_status": "ok"
        },
        "response_time_ms": 8
    },
    "model": {
        "model_name": "shibing624/text2vec-base-chinese",
        "device": "cpu",
        "is_loaded": true,
        "memory_usage_mb": 1024,
        "load_time_seconds": 12.5
    }
}
```

**状态码**:
- `200`: 服务正常
- `503`: 服务异常，检查具体错误信息

---

### 2. 全量数据初始化
> **用途**: 从MySQL数据库加载所有FAQ数据，生成向量并存储到Qdrant数据库，用于系统初始化或数据重建

```http
POST /api/v1/faqs/initialize
```

**请求参数**:
```json
{
    "recreate_collection": true  // 可选，是否重新创建集合，默认true
}
```

**参数说明**:
- `recreate_collection` (布尔值，可选): 
  - `true`: 删除现有集合并重新创建 (默认)
  - `false`: 在现有集合基础上追加数据

**请求示例**:
```bash
curl -X POST http://localhost:5000/api/v1/faqs/initialize \
  -H "Content-Type: application/json" \
  -d '{"recreate_collection": true}'
```

**响应示例**:
```json
{
    "success": true,
    "message": "Successfully initialized 1000 FAQs",
    "processed_count": 1000,
    "total_count": 1000,
    "execution_time": 45.23,
    "collection_recreated": true,
    "model_info": {
        "model_name": "shibing624/text2vec-base-chinese",
        "is_loaded": true,
        "device": "cpu",
        "vector_dimension": 768
    },
    "performance_stats": {
        "vectorization_time": 30.5,
        "database_sync_time": 12.8,
        "qdrant_upsert_time": 1.93
    }
}
```

**错误响应示例**:
```json
{
    "success": false,
    "message": "Failed to load embedding model",
    "processed_count": 0,
    "total_count": 1000,
    "execution_time": 5.2,
    "error_code": "MODEL_LOAD_ERROR"
}
```

**状态码**:
- `200`: 初始化成功
- `500`: 初始化失败

---

### 3. 添加单条FAQ
> **用途**: 添加新的FAQ数据到系统，自动进行向量化处理并同步到向量数据库

```http
POST /api/v1/faqs
```

**请求参数**:
```json
{
    "id": "faq_001",              // 必需，FAQ唯一标识，建议使用有意义的编码
    "question": "如何重置密码？",    // 必需，问题内容，建议长度不超过500字符
    "answer": "请联系管理员重置密码"  // 必需，答案内容，支持富文本和链接
}
```

**参数验证规则**:
- `id`: 字符串，1-50字符，必须唯一
- `question`: 字符串，1-1000字符，不能为空
- `answer`: 字符串，1-5000字符，不能为空

**请求示例**:
```bash
curl -X POST http://localhost:5000/api/v1/faqs \
  -H "Content-Type: application/json" \
  -d '{
    "id": "faq_password_reset",
    "question": "忘记密码怎么办？",
    "answer": "请点击登录页面的忘记密码链接，或联系系统管理员协助重置"
  }'
```

**成功响应示例**:
```json
{
    "success": true,
    "message": "Successfully added FAQ: faq_password_reset",
    "faq_id": "faq_password_reset",
    "execution_time": 1.25,
    "operations": {
        "database_insert": true,
        "vector_generated": true,
        "qdrant_upsert": true
    },
    "model_info": {
        "model_name": "shibing624/text2vec-base-chinese",
        "is_loaded": true,
        "device": "cpu",
        "vector_dimension": 768
    }
}
```

**错误响应示例**:
```json
{
    "success": false,
    "message": "FAQ ID already exists",
    "faq_id": "faq_password_reset",
    "execution_time": 0.15,
    "error_code": "DUPLICATE_ID"
}
```

**状态码**:
- `201`: 创建成功
- `400`: 请求参数错误
- `409`: FAQ ID已存在
- `500`: 服务器内部错误

---
### 4. 搜索FAQ
> **用途**: 基于语义相似度搜索相关FAQ，支持自然语言查询和精确度控制

```http
POST /api/v1/faqs/search
```

**请求参数**:
```json
{
    "text": "如何维修电脑？",      // 必需，查询文本，支持自然语言
    "limit": 5,               // 可选，返回结果数量，默认5，范围1-50
    "similarity": 0.15        // 可选，相似度阈值，默认0.0，范围0.0-1.0
}
```

**参数说明**:
- `text`: 查询文本，支持中文、英文、标点符号
- `limit`: 返回结果数量限制，建议不超过20以保证响应速度
- `similarity`: 相似度阈值，只返回相似度高于此值的结果

**请求示例**:
```bash
curl -X POST http://localhost:5000/api/v1/faqs/search \
  -H "Content-Type: application/json" \
  -d '{
    "text": "电脑出现蓝屏怎么处理",
    "limit": 3,
    "similarity": 0.2
  }'
```

**成功响应示例**:
```json
{
    "results": [
        {
            "faq_id": "faq_computer_repair",
            "question": "电脑坏了怎么办？",
            "answer": "1. 检查电源连接是否正常\n2. 重启电脑尝试解决\n3. 如无法解决请联系技术支持",
            "score": 0.8525,
            "similarity_level": "high"
        },
        {
            "faq_id": "faq_system_crash", 
            "question": "系统崩溃如何处理？",
            "answer": "建议重启系统，如问题持续请备份数据后重装系统",
            "score": 0.7234,
            "similarity_level": "medium"
        },
        {
            "faq_id": "faq_hardware_issue",
            "question": "硬件故障怎么排查？",
            "answer": "可以通过设备管理器检查硬件状态，或使用硬件检测工具",
            "score": 0.6890,
            "similarity_level": "medium"
        }
    ],
    "query_info": {
        "original_text": "电脑出现蓝屏怎么处理",
        "results_count": 3,
        "max_score": 0.8525,
        "min_score": 0.6890,
        "search_time_ms": 45
    }
}
```

**空结果响应示例**:
```json
{
    "results": [],
    "query_info": {
        "original_text": "完全不相关的查询",
        "results_count": 0,
        "message": "No FAQs found matching the similarity threshold",
        "search_time_ms": 12
    }
}
```

**状态码**:
- `200`: 搜索成功 (包括空结果)
- `400`: 请求参数错误
- `500`: 搜索失败

---

### 5. 获取所有FAQ
> **用途**: 获取向量数据库中的所有FAQ数据，支持分页和排序

```http
GET /api/v1/faqs
```

**查询参数** (可选):
```
?page=1&limit=100&sort=id
```

**参数说明**:
- `page`: 页码，默认1
- `limit`: 每页数量，默认100，最大1000
- `sort`: 排序字段，支持id、question

**请求示例**:
```bash
# 获取所有FAQ
curl -X GET http://localhost:5000/api/v1/faqs

# 分页获取
curl -X GET "http://localhost:5000/api/v1/faqs?page=1&limit=50"
```

**响应示例**:
```json
{
    "total_points": 1000,
    "current_page": 1,
    "items_per_page": 100,
    "total_pages": 10,
    "points": [
        {
            "id": 123456789,
            "faq_id": "faq_001",
            "question": "如何重置密码？",
            "answer": "请联系管理员重置密码",
            "created_at": "2025-08-08T10:30:00Z",
            "vector_score": null
        },
        {
            "id": 123456790,
            "faq_id": "faq_002",
            "question": "忘记用户名怎么办？",
            "answer": "可以通过邮箱找回用户名",
            "created_at": "2025-08-08T10:35:00Z",
            "vector_score": null
        }
    ],
    "meta": {
        "collection_name": "faq_sm06",
        "last_updated": "2025-08-08T12:00:00Z",
        "vector_dimension": 768
    }
}
```

**状态码**:
- `200`: 获取成功
- `500`: 获取失败

---

### 6. 获取模型信息
> **用途**: 获取当前加载的embedding模型详细信息和运行状态

```http
GET /api/v1/model/info
```

**请求示例**:
```bash
curl -X GET http://localhost:5000/api/v1/model/info
```

**响应示例**:
```json
{
    "success": true,
    "model_info": {
        "model_name": "shibing624/text2vec-base-chinese",
        "local_model_path": "/path/to/cache/models--shibing624--text2vec-base-chinese",
        "device": "cpu",
        "is_loaded": true,
        "model_type": "SentenceTransformer",
        "vector_dimension": 768,
        "max_sequence_length": 512,
        "load_time_seconds": 12.5,
        "memory_usage": {
            "model_size_mb": 383,
            "total_memory_mb": 1024
        },
        "performance_stats": {
            "avg_inference_time_ms": 25,
            "total_inferences": 1500,
            "last_inference": "2025-08-08T12:30:00Z"
        }
    },
    "hardware_info": {
        "gpu_available": false,
        "cpu_cores": 8,
        "total_memory_gb": 16
    }
}
```

**状态码**:
- `200`: 获取成功
- `500`: 获取失败

---

## 错误处理机制

### 统一错误响应格式
所有API接口在发生错误时都返回统一格式的错误响应：

```json
{
    "success": false,
    "message": "具体错误描述",
    "error_code": "ERROR_TYPE",
    "timestamp": "2025-08-08T12:30:45Z",
    "request_id": "uuid-string",
    "details": {
        "field": "具体错误字段",
        "value": "错误值"
    }
}
```

### HTTP状态码说明

| 状态码 | 说明 | 使用场景 |
|--------|------|----------|
| `200` | 成功 | 请求成功处理 |
| `201` | 创建成功 | 资源创建成功 |
| `400` | 请求错误 | 参数格式错误、参数缺失、参数超出范围 |
| `401` | 未认证 | 需要认证访问 (未启用) |
| `403` | 禁止访问 | 权限不足 (未启用) |
| `404` | 资源不存在 | 请求的API端点不存在 |
| `409` | 冲突 | 资源已存在 (如重复的FAQ ID) |
| `429` | 请求过多 | 触发限流 (可配置) |
| `500` | 服务器错误 | 内部处理异常 |
| `503` | 服务不可用 | 依赖服务异常 (数据库、Qdrant等) |

### 常见错误类型

#### 1. 参数验证错误 (400)
```json
{
    "success": false,
    "message": "Request validation failed",
    "error_code": "VALIDATION_ERROR",
    "details": {
        "field": "limit",
        "message": "limit must be between 1 and 50",
        "received_value": 100
    }
}
```

#### 2. 服务依赖错误 (503)
```json
{
    "success": false,
    "message": "Failed to connect to Qdrant service",
    "error_code": "QDRANT_CONNECTION_ERROR",
    "details": {
        "service": "qdrant",
        "host": "localhost:6333",
        "timeout_seconds": 30
    }
}
```

#### 3. 模型加载错误 (500)
```json
{
    "success": false,
    "message": "Failed to load embedding model",
    "error_code": "MODEL_LOAD_ERROR",
    "details": {
        "model_name": "shibing624/text2vec-base-chinese",
        "error_type": "memory_insufficient"
    }
}
```

---

## 使用示例和最佳实践

### 完整业务流程示例

#### 1. 系统初始化流程
```bash
#!/bin/bash
# 生产环境部署完整流程

echo "1. 检查服务健康状态..."
health_check=$(curl -s http://localhost:5000/health)
echo $health_check | jq .

echo "2. 全量初始化FAQ数据..."
init_response=$(curl -s -X POST http://localhost:5000/api/v1/faqs/initialize \
  -H "Content-Type: application/json" \
  -d '{"recreate_collection": true}')
echo $init_response | jq .

echo "3. 验证数据初始化结果..."
list_response=$(curl -s http://localhost:5000/api/v1/faqs)
total_count=$(echo $list_response | jq '.total_points')
echo "总计FAQ数量: $total_count"

echo "4. 测试搜索功能..."
search_response=$(curl -s -X POST http://localhost:5000/api/v1/faqs/search \
  -H "Content-Type: application/json" \
  -d '{"text": "测试查询", "limit": 3}')
echo $search_response | jq .
```

#### 2. 动态添加FAQ示例
```python
import requests
import json

def add_faq_batch(faqs):
    """批量添加FAQ"""
    base_url = "http://localhost:5000"
    success_count = 0
    
    for faq in faqs:
        try:
            response = requests.post(
                f"{base_url}/api/v1/faqs",
                json=faq,
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            if response.status_code == 201:
                success_count += 1
                print(f"✅ 成功添加FAQ: {faq['id']}")
            else:
                print(f"❌ 添加失败 {faq['id']}: {response.text}")
                
        except Exception as e:
            print(f"❌ 网络错误 {faq['id']}: {e}")
    
    print(f"批量添加完成，成功: {success_count}/{len(faqs)}")

# 示例FAQ数据
new_faqs = [
    {
        "id": "faq_network_001",
        "question": "网络连接不稳定怎么办？",
        "answer": "1. 检查网线连接\n2. 重启路由器\n3. 联系网络管理员"
    },
    {
        "id": "faq_printer_001", 
        "question": "打印机无法正常工作？",
        "answer": "1. 检查电源\n2. 确认驱动安装\n3. 检查墨盒或硒鼓"
    }
]

add_faq_batch(new_faqs)
```

#### 3. 智能搜索优化示例
```javascript
// 前端搜索优化示例
class FAQSearchClient {
    constructor(baseUrl = 'http://localhost:5000') {
        this.baseUrl = baseUrl;
        this.cache = new Map();
        this.debounceTimer = null;
    }
    
    // 防抖搜索
    debounceSearch(query, callback, delay = 300) {
        clearTimeout(this.debounceTimer);
        this.debounceTimer = setTimeout(() => {
            this.search(query).then(callback);
        }, delay);
    }
    
    // 智能搜索
    async search(query, options = {}) {
        const params = {
            text: query,
            limit: options.limit || 5,
            similarity: options.similarity || 0.1
        };
        
        // 缓存检查
        const cacheKey = JSON.stringify(params);
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }
        
        try {
            const response = await fetch(`${this.baseUrl}/api/v1/faqs/search`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(params)
            });
            
            const result = await response.json();
            
            // 结果增强
            result.results = result.results.map(item => ({
                ...item,
                highlighted_question: this.highlightText(item.question, query),
                confidence_level: this.getConfidenceLevel(item.score)
            }));
            
            // 缓存结果
            this.cache.set(cacheKey, result);
            return result;
            
        } catch (error) {
            console.error('搜索失败:', error);
            throw error;
        }
    }
    
    highlightText(text, query) {
        // 简单高亮实现
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    getConfidenceLevel(score) {
        if (score > 0.8) return 'high';
        if (score > 0.6) return 'medium';
        return 'low';
    }
}

// 使用示例
const faqClient = new FAQSearchClient();

// 实时搜索
document.getElementById('searchInput').addEventListener('input', (e) => {
    const query = e.target.value.trim();
    if (query.length > 2) {
        faqClient.debounceSearch(query, (results) => {
            displaySearchResults(results);
        });
    }
});
```

### 性能优化建议

#### 1. 搜索参数优化
```bash
# 高精度搜索 (推荐用于精确匹配)
curl -X POST http://localhost:5000/api/v1/faqs/search \
  -d '{"text": "密码重置", "similarity": 0.7, "limit": 3}'

# 模糊搜索 (推荐用于兜底搜索)
curl -X POST http://localhost:5000/api/v1/faqs/search \
  -d '{"text": "用户问题", "similarity": 0.2, "limit": 10}'

# 快速搜索 (推荐用于实时提示)
curl -X POST http://localhost:5000/api/v1/faqs/search \
  -d '{"text": "查询关键词", "similarity": 0.5, "limit": 5}'
```

#### 2. 监控和告警
```bash
#!/bin/bash
# 服务监控脚本

monitor_faq_service() {
    # 健康检查
    health=$(curl -s http://localhost:5000/health)
    success=$(echo $health | jq -r '.success')
    
    if [ "$success" != "true" ]; then
        echo "⚠️  FAQ服务异常"
        echo $health | jq .
        # 发送告警通知
        send_alert "FAQ服务健康检查失败"
    fi
    
    # 性能检查
    response_time=$(curl -o /dev/null -s -w '%{time_total}' http://localhost:5000/health)
    if (( $(echo "$response_time > 1.0" | bc -l) )); then
        echo "⚠️  FAQ服务响应缓慢: ${response_time}s"
        send_alert "FAQ服务响应时间超过1秒"
    fi
    
    # 内存检查
    memory_usage=$(ps -p $(pgrep -f faq_retrieval) -o rss= | awk '{sum+=$1} END {print sum/1024}')
    if (( $(echo "$memory_usage > 2048" | bc -l) )); then
        echo "⚠️  FAQ服务内存使用过高: ${memory_usage}MB"
        send_alert "FAQ服务内存使用超过2GB"
    fi
}

send_alert() {
    # 实现告警逻辑 (邮件、webhook等)
    echo "ALERT: $1" >> /var/log/faq-service-alerts.log
}

# 每分钟执行一次监控
while true; do
    monitor_faq_service
    sleep 60
done
```

---

## 性能优化

1. **模型单例**: 整个应用程序共享一个模型实例，避免重复加载
2. **连接池**: 数据库连接使用上下文管理器，自动管理连接生命周期
3. **批量处理**: 全量初始化时使用批量插入，提高性能
4. **缓存机制**: 本地模型文件缓存，离线运行
5. **异步支持**: 支持多线程处理请求

---

## API版本兼容性

### 向后兼容接口
为保持与旧版本的兼容性，系统提供以下兼容接口：

| 旧接口 | 新接口 | 状态 | 建议 |
|--------|--------|------|------|
| `POST /search` | `POST /api/v1/faqs/search` | ✅ 兼容 | 建议迁移到新接口 |
| `GET /list-all` | `GET /api/v1/faqs` | ✅ 兼容 | 建议迁移到新接口 |
| `GET /health` | `GET /health` | ✅ 保持 | 推荐使用 |

### 接口变更说明

#### v1.0.0 更新内容
- ✨ 新增统一的`/api/v1`前缀
- ✨ 新增详细的错误响应格式
- ✨ 新增模型信息接口
- ✨ 新增FAQ添加接口
- ✨ 增强搜索结果格式
- ✨ 新增系统监控指标

#### 迁移指南
```bash
# 旧版本搜索
curl -X POST http://localhost:5000/search -d '{"text": "查询"}'

# 新版本搜索 (推荐)
curl -X POST http://localhost:5000/api/v1/faqs/search -d '{"text": "查询"}'
```

---

## 性能基准

### 响应时间基准 (单线程)
| 接口 | 平均响应时间 | 95%分位数 | 99%分位数 |
|------|-------------|-----------|-----------|
| 健康检查 | 5ms | 10ms | 20ms |
| 搜索FAQ | 45ms | 80ms | 150ms |
| 添加FAQ | 200ms | 350ms | 500ms |
| 获取全部FAQ | 15ms | 30ms | 60ms |
| 模型信息 | 8ms | 15ms | 25ms |

### 吞吐量基准 (4核CPU)
- **搜索并发**: 100 RPS
- **添加FAQ**: 20 RPS
- **查询FAQ**: 200 RPS

### 系统资源消耗
- **内存使用**: 1-2GB (包含模型)
- **CPU使用**: 10-30% (搜索时)
- **磁盘I/O**: 低 (主要是日志写入)

---

## 注意事项和限制

### 系统限制
1. **单次搜索结果**: 最多50条
2. **FAQ内容长度**: 问题1000字符，答案5000字符
3. **并发连接**: 建议不超过200
4. **模型支持**: 仅支持中文embedding模型

### 最佳实践
1. **生产部署**: 建议使用Gunicorn + Nginx
2. **监控**: 配置健康检查和日志监控
3. **备份**: 定期备份MySQL数据和Qdrant集合
4. **缓存**: 前端建议实现搜索结果缓存

### 已知问题
1. 首次启动模型加载时间较长 (10-30秒)
2. 大量数据初始化时内存消耗较高
3. Qdrant连接异常时需要手动重连

---

## 技术支持

### 联系方式
- **文档**: [项目Wiki](https://github.com/yourusername/faq-retrieval-service/wiki)
- **问题反馈**: [GitHub Issues](https://github.com/yourusername/faq-retrieval-service/issues)
- **技术支持**: support@example.com

### 更新日志
查看 [CHANGELOG.md](../CHANGELOG.md) 获取详细更新记录。

---

**文档版本**: v1.0.0  
**最后更新**: 2025年8月8日  
**维护人员**: FAQ检索服务开发团队
