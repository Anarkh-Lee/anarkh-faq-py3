#!/usr/bin/env python3
"""
测试MySQL连接和创建示例FAQ数据
"""
import pymysql
import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))
from faq_retrieval.config import config

def test_mysql_connection():
    """测试MySQL连接"""
    try:
        connection = pymysql.connect(
            host=config.MYSQL_HOST,
            port=config.MYSQL_PORT,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD,
            charset=config.MYSQL_CHARSET
        )
        
        cursor = connection.cursor()
        
        # 创建数据库（如果不存在）
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.MYSQL_DATABASE}")
        cursor.execute(f"USE {config.MYSQL_DATABASE}")
        
        # 创建faq表
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS `faq` (
          `id` varchar(64) NOT NULL COMMENT '主键',
          `question` varchar(3000) DEFAULT NULL COMMENT '问题',
          `answer` varchar(3000) DEFAULT NULL COMMENT '回答',
          PRIMARY KEY (`id`)
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """
        cursor.execute(create_table_sql)
        
        # 插入示例数据
        sample_data = [
            ('1', '如何维修电脑？', '找售后人员进行维修'),
            ('2', '电脑坏了怎么办？', '先检查电源线是否连接，如果还不行请联系技术支持'),
            ('3', '如何重装系统？', '备份重要数据后，使用系统安装盘或恢复分区重装系统'),
            ('4', '忘记密码怎么办？', '联系管理员重置密码，或使用密码找回功能'),
            ('5', '网络连不上怎么办？', '检查网线连接，重启路由器，或联系网络管理员')
        ]
        
        # 先清空表，然后插入新数据
        cursor.execute("DELETE FROM faq")
        
        insert_sql = "INSERT INTO faq (id, question, answer) VALUES (%s, %s, %s)"
        cursor.executemany(insert_sql, sample_data)
        
        connection.commit()
        
        # 验证数据
        cursor.execute("SELECT COUNT(*) FROM faq")
        count = cursor.fetchone()[0]
        
        print(f"✅ MySQL连接成功！")
        print(f"✅ 数据库 '{config.MYSQL_DATABASE}' 创建成功！")
        print(f"✅ faq表创建成功，插入了 {count} 条示例数据！")
        
        # 显示数据
        cursor.execute("SELECT id, question, answer FROM faq LIMIT 3")
        for row in cursor.fetchall():
            print(f"   ID: {row[0]}, 问题: {row[1][:30]}..., 答案: {row[2][:30]}...")
        
        cursor.close()
        connection.close()
        
        return True
        
    except Exception as e:
        print(f"❌ MySQL连接失败: {e}")
        return False

if __name__ == "__main__":
    print("正在测试MySQL连接...")
    test_mysql_connection()
