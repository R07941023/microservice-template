from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import mysql.connector
from mysql.connector import pooling
import logging
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# --- Database Configuration ---
DB_HOST_PORT = os.getenv("MYSQL_HOST", "db:3306")
DB_USER = os.getenv("MYSQL_USER", "username")
DB_PASSWORD = os.getenv("MYSQL_PASSWORD", "password")
DB_NAME = os.getenv("MYSQL_DATABASE", "database")
db_host, db_port = DB_HOST_PORT.split(":")
DB_CONFIG = {
    "host": db_host,
    "port": int(db_port),
    "user": DB_USER,
    "password": DB_PASSWORD,
    "database": DB_NAME
}
cnxpool = pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **DB_CONFIG)

# --- Pydantic Models ---
class DropUpdate(BaseModel):
    dropperid: int
    itemid: int
    minimum_quantity: int
    maximum_quantity: int
    questid: int
    chance: int

class DropCreate(BaseModel):
    dropperid: int
    itemid: int
    minimum_quantity: int
    maximum_quantity: int
    questid: int
    chance: int

# --- API Endpoints ---
@app.get("/search_drops")
async def search_drops(query: Optional[str] = None):
    if not query:
        logger.warning("Query parameter 'query' is required.")
        raise HTTPException(status_code=400, detail="Query parameter 'query' is required.")

    cnx = None
    cursor = None
    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        try:
            query_int = int(query)
            sql_query = "SELECT * FROM drop_data WHERE dropperid = %s OR itemid = %s"
            cursor.execute(sql_query, (query_int, query_int))
        except ValueError:
            logger.warning(f"Query '{query}' is not a valid integer.")
            raise HTTPException(status_code=400, detail="Query must be a valid integer for dropperid or itemid.")
        
        results = cursor.fetchall()
        for row in results:
            if 'id' in row:
                row['id'] = str(row['id'])
        
        logger.info(f"Found {len(results)} results for query: {query}")
        return results

    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor: cursor.close()
        if cnx and cnx.is_connected(): cnx.close()

@app.get("/get_drop/{id}")
async def get_drop(id: int):
    cnx = None
    cursor = None
    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        
        sql_query = "SELECT * FROM drop_data WHERE id = %s"
        cursor.execute(sql_query, (id,))
        
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(status_code=404, detail="Drop record not found")
        
        if 'id' in result:
            result['id'] = str(result['id'])
        
        logger.info(f"Found drop record with id: {id}")
        return result

    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor: cursor.close()
        if cnx and cnx.is_connected(): cnx.close()

@app.put("/update_drop/{id}")
async def update_drop(id: int, drop: DropUpdate):
    cnx = None
    cursor = None
    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()
        
        sql_update_query = """
            UPDATE drop_data 
            SET dropperid=%s, itemid=%s, minimum_quantity=%s, maximum_quantity=%s, questid=%s, chance=%s 
            WHERE id=%s
        """
        values = (
            drop.dropperid,
            drop.itemid,
            drop.minimum_quantity,
            drop.maximum_quantity,
            drop.questid,
            drop.chance,
            id
        )
        
        cursor.execute(sql_update_query, values)
        cnx.commit()
        
        logger.info(f"Successfully updated drop record with id: {id}")
        return {"message": "Drop data updated successfully", "id": id}

    except mysql.connector.Error as err:
        logger.error(f"Database error on update: {err}", exc_info=True)
        if cnx: cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor: cursor.close()
        if cnx and cnx.is_connected(): cnx.close()

        if cnx and cnx.is_connected(): cnx.close()

@app.post("/add_drop")
async def add_drop(drop: DropCreate):
    cnx = None
    cursor = None
    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()
        
        sql_insert_query = """
            INSERT INTO drop_data 
            (dropperid, itemid, minimum_quantity, maximum_quantity, questid, chance) 
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            drop.dropperid,
            drop.itemid,
            drop.minimum_quantity,
            drop.maximum_quantity,
            drop.questid,
            drop.chance,
        )
        
        cursor.execute(sql_insert_query, values)
        cnx.commit()
        
        new_id = cursor.lastrowid
        logger.info(f"Successfully added new drop record with id: {new_id}")
        return {"message": "Drop data added successfully", "id": new_id}

    except mysql.connector.Error as err:
        logger.error(f"Database error on add: {err}", exc_info=True)
        if cnx: cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor: cursor.close()
        if cnx and cnx.is_connected(): cnx.close()

@app.delete("/delete_drop/{id}")
async def delete_drop(id: int):
    cnx = None
    cursor = None
    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()
        
        sql_delete_query = "DELETE FROM drop_data WHERE id = %s"
        
        cursor.execute(sql_delete_query, (id,))
        cnx.commit()
        
        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="Drop record not found")

        logger.info(f"Successfully deleted drop record with id: {id}")
        return {"message": "Drop data deleted successfully", "id": id}

    except mysql.connector.Error as err:
        logger.error(f"Database error on delete: {err}", exc_info=True)
        if cnx: cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor: cursor.close()
        if cnx and cnx.is_connected(): cnx.close()
