from fastapi import FastAPI, HTTPException
from typing import Optional, List
import mysql.connector
from mysql.connector import pooling
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Database connection details from environment variables
DB_HOST_PORT = os.getenv("MYSQL_HOST", "db:3306") # Default to 'db:3306' if not set
DB_USER = os.getenv("MYSQL_USER", "username")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
DB_NAME = os.getenv("MYSQL_DATABASE", "database")

# Parse host and port
db_host, db_port = DB_HOST_PORT.split(":")

DB_CONFIG = {
    "host": db_host,
    "port": int(db_port),
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME
}

# Create a connection pool
cnxpool = pooling.MySQLConnectionPool(pool_name="mypool",
                                      pool_size=5,
                                      **DB_CONFIG)

@app.get("/search_drops")
async def search_drops(query: Optional[str] = None):
    if not query:
        logger.warning("Query parameter 'query' is required.")
        raise HTTPException(status_code=400, detail="Query parameter 'query' is required.")

    cnx = None
    cursor = None
    try:
        # Get a connection from the pool
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True)

        # Try to convert query to int for id searches
        try:
            query_int = int(query)
            sql_query = "SELECT * FROM drop_data WHERE dropperid = %s OR itemid = %s"
            logger.info(f"Executing SQL: {sql_query} with params: ({query_int}, {query_int})")
            cursor.execute(sql_query, (query_int, query_int))
        except ValueError:
            logger.warning(f"Query '{query}' is not a valid integer.")
            raise HTTPException(status_code=400, detail="Query must be a valid integer for dropperid or itemid.")

        results = cursor.fetchall()

        # Convert 'id' to string for frontend compatibility
        for row in results:
            if 'id' in row:
                row['id'] = str(row['id'])

        logger.info(f"Found {len(results)} results for query: {query}")
        return results

    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")
    finally:
        if cursor:
            cursor.close()
        if cnx and cnx.is_connected():
            cnx.close() # Return the connection to the pool
