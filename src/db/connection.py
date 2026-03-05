"""Database connection management with connection pooling"""

import mysql.connector
from mysql.connector import Error, pooling
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# Global connection pool
_connection_pool = None

def init_connection_pool(db_config):
    """Initialize the database connection pool"""
    global _connection_pool
    
    try:
        _connection_pool = pooling.MySQLConnectionPool(
            pool_name=db_config.get('pool_name', 'asset_pool'),
            pool_size=db_config.get('pool_size', 10),
            pool_reset_session=db_config.get('pool_reset_session', True),
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            port=db_config.get('port', 3306),
            charset=db_config.get('charset', 'utf8mb4'),
            collation=db_config.get('collation', 'utf8mb4_unicode_ci'),
            use_pure=db_config.get('use_pure', False),
            autocommit=db_config.get('autocommit', False)
        )
        logger.info(f"Database connection pool initialized: {db_config.get('pool_name')}")
        return True
    except Error as e:
        logger.error(f"Failed to create connection pool: {e}")
        return False

def get_connection():
    """Get a connection from the pool"""
    global _connection_pool
    
    if _connection_pool is None:
        raise Exception("Connection pool not initialized. Call init_connection_pool() first.")
    
    try:
        connection = _connection_pool.get_connection()
        return connection
    except Error as e:
        logger.error(f"Failed to get connection from pool: {e}")
        raise

@contextmanager
def get_db_cursor(dictionary=False, buffered=True):
    """Context manager for database operations with automatic connection management"""
    connection = None
    cursor = None
    
    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=dictionary, buffered=buffered)
        yield cursor
        connection.commit()
    except Error as e:
        if connection:
            connection.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()

def create_connection(host_name, user_name, user_password, db_name, port=3306):
    """Create a single database connection (legacy support)"""
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            password=user_password,
            database=db_name,
            port=port,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        logger.info("Connection to MySQL DB successful")
    except Error as e:
        logger.error(f"Connection error: {e}")
        raise
    
    return connection

def close_connection(connection):
    """Close a database connection"""
    if connection:
        try:
            connection.close()
            logger.debug("Connection to MySQL DB closed")
        except Error as e:
            logger.error(f"Error closing connection: {e}")

def test_connection(db_config):
    """Test database connection with provided config"""
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password'],
            database=db_config['database'],
            port=db_config.get('port', 3306)
        )
        conn.close()
        return True
    except Error as e:
        logger.error(f"Connection test failed: {e}")
        return False