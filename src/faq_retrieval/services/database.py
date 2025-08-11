"""
数据访问层 - 处理MySQL数据库操作
"""
import pymysql
import logging
from typing import List, Dict, Optional
from contextlib import contextmanager
from ..config import config

logger = logging.getLogger(__name__)

class MySQLConnection:
    """MySQL连接管理器"""
    
    def __init__(self):
        self.host = config.MYSQL_HOST
        self.port = config.MYSQL_PORT
        self.user = config.MYSQL_USER
        self.password = config.MYSQL_PASSWORD
        self.database = config.MYSQL_DATABASE
        self.charset = config.MYSQL_CHARSET
    
    @contextmanager
    def get_connection(self):
        """获取数据库连接的上下文管理器"""
        connection = None
        try:
            connection = pymysql.connect(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                charset=self.charset,
                autocommit=True
            )
            yield connection
        except Exception as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if connection:
                connection.close()
    
    def test_connection(self) -> bool:
        """测试数据库连接"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

class FAQRepository:
    """FAQ数据仓库"""
    
    def __init__(self):
        self.db = MySQLConnection()
    
    def get_all_faqs(self) -> List[Dict[str, str]]:
        """获取所有FAQ数据"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, question, answer 
                    FROM faq 
                    WHERE question IS NOT NULL 
                    AND answer IS NOT NULL 
                    AND question != '' 
                    AND answer != ''
                    ORDER BY id
                """)
                
                faqs = []
                for row in cursor.fetchall():
                    faqs.append({
                        "id": row[0],
                        "question": row[1],
                        "answer": row[2]
                    })
                
                logger.info(f"Retrieved {len(faqs)} FAQs from database")
                return faqs
                
        except Exception as e:
            logger.error(f"Error retrieving FAQs: {e}")
            raise
    
    def get_faq_by_id(self, faq_id: str) -> Optional[Dict[str, str]]:
        """根据ID获取单个FAQ"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, question, answer 
                    FROM faq 
                    WHERE id = %s
                """, (faq_id,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        "id": row[0],
                        "question": row[1],
                        "answer": row[2]
                    }
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving FAQ by ID {faq_id}: {e}")
            raise
    
    def add_faq(self, faq_id: str, question: str, answer: str) -> bool:
        """添加新的FAQ"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO faq (id, question, answer) 
                    VALUES (%s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                    question = VALUES(question), 
                    answer = VALUES(answer)
                """, (faq_id, question, answer))
                
                logger.info(f"Added/Updated FAQ with ID: {faq_id}")
                return True
                
        except Exception as e:
            logger.error(f"Error adding FAQ: {e}")
            raise
    
    def get_faq_count(self) -> int:
        """获取FAQ总数"""
        try:
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM faq WHERE question IS NOT NULL AND answer IS NOT NULL")
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting FAQ count: {e}")
            raise
