## CentOS 7 简单部署指南

### 前提条件
- CentOS 7 系统
- Python 3.8+（按照附件文档安装）
- MySQL 数据库运行正常
- Qdrant 服务运行正常

### 部署步骤

#### 1. 上传代码并创建目录

只需要将以下内容上传到服务器即可：

```
--.cache
--scripts
--src
--tests
requirements.txt
run.py
setup.py
```

```bash
# 创建部署目录
sudo mkdir -p /opt/faq-service
cd /opt/faq-service

# 上传并解压项目代码（假设代码在 /tmp/anarkh-faq-py3.tar.gz）
sudo tar -xzf /tmp/anarkh-faq-py3.tar.gz
sudo mv anarkh-faq-py3 ./
```

#### 2. 安装依赖
```bash
cd /opt/faq-service/anarkh-faq-py3

# 安装系统依赖
sudo yum install -y mysql-devel gcc gcc-c++

# 创建虚拟环境
python3.8 -m venv venv
source venv/bin/activate

# 最好先设置一下国内镜像源（我用的阿里云镜像）
# 1.阿里云镜像
pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/
pip config set global.trusted-host mirrors.aliyun.com
# 2.清华大学镜像
pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
pip config set global.trusted-host pypi.tuna.tsinghua.edu.cn
# 3. 豆瓣镜像
pip config set global.index-url https://pypi.douban.com/simple/
pip config set global.trusted-host pypi.douban.com
# 4. 中科大镜像
pip config set global.index-url https://pypi.mirrors.ustc.edu.cn/simple/
pip config set global.trusted-host pypi.mirrors.ustc.edu.cn


# 安装Python依赖
pip install --upgrade pip
pip install -r requirements.txt
# 如果是需要代理的话，使用下面语句安装Python依赖
pip install --proxy http://li.ba:lll111...@dl-proxy.neusoft.com:8080 --upgrade pip
pip install --proxy http://li.ba:lll111...@dl-proxy.neusoft.com:8080 -r requirements.txt
```

正常来说，这种方式依赖就可以安装成功，但是使用公司的网络需要代理，有一些网络被屏蔽了，需要下面方式：

##### 2.1 分步安装

如果安装步骤2安装依赖安装后，使用python run.py启动报如下的错误：

```bash
/opt/faq-service/anarkh-faq-py3/venv/lib/python3.8/site-packages/transformers/utils/hub.py:128: FutureWarning: Using TRANSFORMERS_CACHE is deprecated and will be removed in v5 of Transformers. Use HF_HOME instead.
warnings.warn(
You are offline and the cache for model files in Transformers v4.22.0 has been updated while your local cache seems to be the one of a previous version. It is very likely that all your calls to any from_pretrained() method will fail. Remove the offline mode and enable internet connection to have your cache be updated automatically, then you can go back to offline mode.
0it [00:00, ?it/s]
✅ Found local model at: /opt/faq-service/anarkh-faq-py3/.cache/huggingface/models--shibing624--text2vec-base-chinese/snapshots/183bb99aa7af74355fb58d16edf8c13ae7c5433e
Traceback (most recent call last):
File "run.py", line 13, in <module>
from faq_retrieval.app import main
File "/opt/faq-service/anarkh-faq-py3/src/faq_retrieval/app.py", line 15, in <module>
from faq_retrieval.api.routes import api_bp, legacy_bp
File "/opt/faq-service/anarkh-faq-py3/src/faq_retrieval/api/routes.py", line 6, in <module>
from faq_retrieval.services.faq_service import FAQService
File "/opt/faq-service/anarkh-faq-py3/src/faq_retrieval/services/init.py", line 7, in <module>
from .qdrant_service import QdrantService
File "/opt/faq-service/anarkh-faq-py3/src/faq_retrieval/services/qdrant_service.py", line 7, in <module>
from qdrant_client import QdrantClient, models
File "/opt/faq-service/anarkh-faq-py3/venv/lib/python3.8/site-packages/qdrant_client/init.py", line 1, in <module>
from .async_qdrant_client import AsyncQdrantClient as AsyncQdrantClient
File "/opt/faq-service/anarkh-faq-py3/venv/lib/python3.8/site-packages/qdrant_client/async_qdrant_client.py", line 31, in <module>
from qdrant_client.local.async_qdrant_local import AsyncQdrantLocal
File "/opt/faq-service/anarkh-faq-py3/venv/lib/python3.8/site-packages/qdrant_client/local/async_qdrant_local.py", line 42, in <module>
from qdrant_client.local.local_collection import (
File "/opt/faq-service/anarkh-faq-py3/venv/lib/python3.8/site-packages/qdrant_client/local/local_collection.py", line 59, in <module>
from qdrant_client.local.persistence import CollectionPersistence
File "/opt/faq-service/anarkh-faq-py3/venv/lib/python3.8/site-packages/qdrant_client/local/persistence.py", line 5, in <module>
import sqlite3
File "/usr/local/lib/python3.8/sqlite3/init.py", line 23, in <module>
from sqlite3.dbapi2 import *
File "/usr/local/lib/python3.8/sqlite3/dbapi2.py", line 27, in <module>
from _sqlite3 import *
ModuleNotFoundError: No module named '_sqlite3'
```

这个错误是因为Python 3.8缺少sqlite3模块，这通常是在编译安装Python时没有正确配置sqlite3依赖导致的。

我们需要安装sqlite3：

1. 安装sqlite3开发库

   ```bash
   sudo yum install -y sqlite-devel
   ```

2. 重新编译Python 3.8

   ```bash
   cd /usr/src/Python-3.8.18
   
   # 清理之前的编译
   sudo make clean
   
   # 重新配置，添加sqlite3支持
   sudo env PATH=$PATH ./configure --enable-optimizations --enable-loadable-sqlite-extensions
   
   # 重新编译安装
   sudo env PATH=$PATH make altinstall
   ```

3. 验证sqlite3支持

   ```bash
   python3.8 -c "import sqlite3; print('✅ sqlite3 available')"
   ```

   显示下面，证明成功：

   ```bash
   ✅ sqlite3 available
   ```

4. 重新创建虚拟环境

   ```bash
   cd /opt/faq-service/anarkh-faq-py3
   
   # 删除旧的虚拟环境
   rm -rf venv
   
   # 创建新的虚拟环境
   python3.8 -m venv venv
   source venv/bin/activate
   ```

5. 重新安装依赖

   ```bash
   # 设置代理
   export http_proxy=http://li.ba:lll111...@dl-proxy.neusoft.com:8080
   export https_proxy=http://li.ba:lll111...@dl-proxy.neusoft.com:8080
   
   # 配置pip
   pip config set global.trusted-host "pypi.tuna.tsinghua.edu.cn mirrors.aliyun.com"
   pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple/
   
   # 按顺序安装依赖（兼容CentOS 7）
   pip install "urllib3>=1.26.0,<2.0"
   pip install flask>=2.3.0
   pip install pymysql>=1.1.0
   pip install numpy>=1.21.0
   pip install scipy>=1.7.0
   pip install scikit-learn>=1.0.0
   pip install qdrant-client>=1.6.0
   pip install torch>=1.13.0
   pip install sentence-transformers>=2.2.0
   ```

   我是直接使用下面的命令：

   ```bash
   pip install --proxy http://li.ba:lll111...@dl-proxy.neusoft.com:8080 "urllib3>=1.26.0,<2.0"
   
   pip install --proxy http://li.ba:lll111...@dl-proxy.neusoft.com:8080 flask>=2.3.0
   
   
   pip install --proxy http://li.ba:lll111...@dl-proxy.neusoft.com:8080 pymysql>=1.1.0
   
   
   pip install --proxy http://li.ba:lll111...@dl-proxy.neusoft.com:8080 numpy>=1.21.0
   
   
   pip install --proxy http://li.ba:lll111...@dl-proxy.neusoft.com:8080 scipy>=1.7.0
   
   
   pip install --proxy http://li.ba:lll111...@dl-proxy.neusoft.com:8080 scikit-learn>=1.0.0
   
   
   pip install --proxy http://li.ba:lll111...@dl-proxy.neusoft.com:8080 qdrant-client>=1.6.0
   
   
   pip install --proxy http://li.ba:lll111...@dl-proxy.neusoft.com:8080 torch>=1.13.0
   # 这个不好用，用下面这个
   pip install --proxy http://li.ba:lll111...@dl-proxy.neusoft.com:8080 \
       --trusted-host pypi.tuna.tsinghua.edu.cn \
       --trusted-host mirrors.aliyun.com \
       -i https://pypi.tuna.tsinghua.edu.cn/simple/ \
       torch>=1.13.0
   
   pip install --proxy http://li.ba:lll111...@dl-proxy.neusoft.com:8080 sentence-transformers>=2.2.0
   ```

###### 2.1.1 问题1：SSL证书在企业代理中验证错误

pip install --proxy http://li.ba:lll111...@dl-proxy.neusoft.com:8080 torch>=1.13.0这个命令报错：

```bash
WARNING: Retrying (Retry(total=4, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1131)'))': /whl/cpu/torch/
WARNING: Retrying (Retry(total=3, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1131)'))': /whl/cpu/torch/
WARNING: Retrying (Retry(total=2, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1131)'))': /whl/cpu/torch/
WARNING: Retrying (Retry(total=1, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1131)'))': /whl/cpu/torch/
WARNING: Retrying (Retry(total=0, connect=None, read=None, redirect=None, status=None)) after connection broken by 'SSLError(SSLCertVerificationError(1, '[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: unable to get local issuer certificate (_ssl.c:1131)'))': /whl/cpu/torch/
ERROR: Could not find a version that satisfies the requirement torch (from versions: none)
ERROR: No matching distribution found for torch
```

**解决：**

这个SSL证书验证错误在企业代理环境中很常见。给出几个肯定可行的解决方案：

**跳过SSL验证（最直接）**

```bash
cd /opt/faq-service/anarkh-faq-py3
source venv/bin/activate

# 设置代理
export http_proxy=http://li.ba:lll111...@dl-proxy.neusoft.com:8080
export https_proxy=http://li.ba:lll111...@dl-proxy.neusoft.com:8080

# 跳过SSL验证安装PyTorch
pip install --proxy http://li.ba:lll111...@dl-proxy.neusoft.com:8080 \
    --trusted-host pypi.tuna.tsinghua.edu.cn \
    --trusted-host mirrors.aliyun.com \
    -i https://pypi.tuna.tsinghua.edu.cn/simple/ \
    torch>=1.13.0
```

**验证安装成功：**

```bash
# 验证PyTorch
python -c "
import torch
print('✅ PyTorch安装成功!')
print(f'版本: {torch.__version__}')
print(f'CUDA可用: {torch.cuda.is_available()}')
print(f'测试张量: {torch.tensor([1, 2, 3]).sum()}')
"
```



#### 3. 配置数据库连接（这一步最好直接在windows中修改好，这里就不用修改了）

编辑配置文件：
```bash
vim src/faq_retrieval/config.py
```

修改以下配置：
```python
# MySQL数据库配置
MYSQL_HOST = "localhost"        # 您的MySQL地址
MYSQL_PORT = 3306
MYSQL_USER = "root"             # 您的MySQL用户名
MYSQL_PASSWORD = "your_password" # 您的MySQL密码
MYSQL_DATABASE = "anarkh"       # 您的数据库名

# Qdrant配置
QDRANT_HOST = "localhost"       # 您的Qdrant地址
QDRANT_PORT = 6333
```

#### 4. 测试连接
```bash
# 激活虚拟环境
source venv/bin/activate

# 测试MySQL连接
python tests/test_mysql.py

# 如果连接成功，会看到类似输出：
# ✅ MySQL连接成功！
# ✅ 数据库 'anarkh' 创建成功！
# ✅ faq表创建成功，插入了 5 条示例数据！
```

#### 5. 启动服务
```bash
# 在虚拟环境中启动
source venv/bin/activate
python run.py
```

服务启动后会显示：
```
Starting FAQ retrieval API service...
Model: shibing624/text2vec-base-chinese
Database: localhost:3306/anarkh
Qdrant: localhost:6333
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
 * Running on http://[your-ip]:5000
```

##### 5.1 启动报错

###### 5.1.1 OpenSSL版本太旧

报如下错误：

```bash
Error importing huggingface_hub.hf_api: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'OpenSSL 1.0.2k-fips 26 Jan 2017'. See: https://github.com/urllib3/urllib3/issues/2168
Traceback (most recent call last):
File "run.py", line 13, in <module>
from faq_retrieval.app import main
File "/opt/faq-service/anarkh-faq-py3/src/faq_retrieval/app.py", line 15, in <module>
from faq_retrieval.api.routes import api_bp, legacy_bp
File "/opt/faq-service/anarkh-faq-py3/src/faq_retrieval/api/routes.py", line 6, in <module>
from faq_retrieval.services.faq_service import FAQService
File "/opt/faq-service/anarkh-faq-py3/src/faq_retrieval/services/init.py", line 6, in <module>
from .model_manager import ModelManager, model_manager
File "/opt/faq-service/anarkh-faq-py3/src/faq_retrieval/services/model_manager.py", line 8, in <module>
from sentence_transformers import SentenceTransformer
File "/opt/faq-service/anarkh-faq-py3/venv/lib/python3.8/site-packages/sentence_transformers/init.py", line 10, in <module>
from sentence_transformers.cross_encoder.CrossEncoder import CrossEncoder
File "/opt/faq-service/anarkh-faq-py3/venv/lib/python3.8/site-packages/sentence_transformers/cross_encoder/init.py", line 3, in <module>
from .CrossEncoder import CrossEncoder
File "/opt/faq-service/anarkh-faq-py3/venv/lib/python3.8/site-packages/sentence_transformers/cross_encoder/CrossEncoder.py", line 14, in <module>
from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer, is_torch_npu_available
File "/opt/faq-service/anarkh-faq-py3/venv/lib/python3.8/site-packages/transformers/init.py", line 26, in <module>
from . import dependency_versions_check
File "/opt/faq-service/anarkh-faq-py3/venv/lib/python3.8/site-packages/transformers/dependency_versions_check.py", line 16, in <module>
from .utils.versions import require_version, require_version_core
File "/opt/faq-service/anarkh-faq-py3/venv/lib/python3.8/site-packages/transformers/utils/init.py", line 21, in <module>
from huggingface_hub import get_full_repo_name # for backward compatibility
File "/opt/faq-service/anarkh-faq-py3/venv/lib/python3.8/site-packages/huggingface_hub/init.py", line 1028, in getattr
submod = importlib.import_module(submod_path)
File "/usr/local/lib/python3.8/importlib/init.py", line 127, in import_module
return _bootstrap._gcd_import(name[level:], package, level)
File "/opt/faq-service/anarkh-faq-py3/venv/lib/python3.8/site-packages/huggingface_hub/hf_api.py", line 51, in <module>
import requests
File "/opt/faq-service/anarkh-faq-py3/venv/lib/python3.8/site-packages/requests/init.py", line 43, in <module>
import urllib3
File "/opt/faq-service/anarkh-faq-py3/venv/lib/python3.8/site-packages/urllib3/init.py", line 42, in <module>
raise ImportError(
ImportError: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'OpenSSL 1.0.2k-fips 26 Jan 2017'. See: https://github.com/urllib3/urllib3/issues/2168
```

这个错误是因为CentOS 7系统自带的OpenSSL版本太旧（1.0.2k），而新版本的urllib3要求OpenSSL 1.1.1+。这是CentOS 7的常见问题。

**解决方案：降级urllib3版本** 

**直接降级urllib3** 

```bash
cd /opt/faq-service/anarkh-faq-py3
source venv/bin/activate

# 设置代理
export http_proxy=http://li.ba:lll111...@dl-proxy.neusoft.com:8080
export https_proxy=http://li.ba:lll111...@dl-proxy.neusoft.com:8080

# 降级urllib3到兼容版本
pip install "urllib3<2.0" --trusted-host pypi.tuna.tsinghua.edu.cn -i https://pypi.tuna.tsinghua.edu.cn/simple/
```

**验证修复** 

```bash
cd /opt/faq-service/anarkh-faq-py3
source venv/bin/activate

# 检查urllib3版本
python -c "import urllib3; print('urllib3 version:', urllib3.__version__)"
```



#### 6. 初始化FAQ数据

在另一个终端中：
```bash
# 初始化数据
curl -X POST http://localhost:5000/api/v1/faqs/initialize \
  -H "Content-Type: application/json"
```

#### 7. 测试服务
```bash
# 健康检查
curl http://localhost:5000/health

# 搜索测试
curl -X POST http://localhost:5000/api/v1/faqs/search \
  -H "Content-Type: application/json" \
  -d '{
    "text": "电脑坏了怎么办",
    "similarity": 0.15,
    "limit": 5
  }'
```

### 后台运行（可选）

如果需要后台运行服务：

#### 方法1：使用nohup
```bash
cd /opt/faq-service/anarkh-faq-py3
source venv/bin/activate
nohup python run.py > logs/service.log 2>&1 &
```

#### 方法2：创建systemd服务
```bash
# 创建服务文件
sudo tee /etc/systemd/system/faq-service.service > /dev/null << 'EOF'
[Unit]
Description=FAQ Retrieval Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/faq-service/anarkh-faq-py3
Environment=PYTHONPATH=/opt/faq-service/anarkh-faq-py3/src
ExecStart=/opt/faq-service/anarkh-faq-py3/venv/bin/python run.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable faq-service
sudo systemctl start faq-service

# 查看状态
sudo systemctl status faq-service
```

### 访问服务
- 健康检查：`http://[服务器IP]:5000/health`
- API文档参考：[`docs/API_DOCUMENTATION.md`](docs/API_DOCUMENTATION.md )

这样就完成了最简单的单机部署，服务会在5000端口提供API接口。