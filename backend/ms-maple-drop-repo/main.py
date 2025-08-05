from fastapi import FastAPI, HTTPException, Request, Depends, Query, Path
from typing import Optional
import mysql.connector
from mysql.connector import pooling, cursor
import logging
import os
from models import DropUpdate, DropCreate
from typing import Literal

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

# --- Dependencies for DB Operations ---
def get_db_cursor(request: Request) -> cursor.MySQLCursorDict:
    cnx = None
    cursor = None
    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor(dictionary=True)
        yield cursor
    except mysql.connector.Error as err:
        logger.error(f"Database error: {err}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor: cursor.close()
        if cnx and cnx.is_connected(): cnx.close()

def get_db_writer_cursor(request: Request) -> cursor.MySQLCursor:
    cnx = None
    cursor = None
    try:
        cnx = cnxpool.get_connection()
        cursor = cnx.cursor()
        yield cursor
        cnx.commit()
    except mysql.connector.Error as err:
        logger.error(f"Database error on write: {err}", exc_info=True)
        if cnx: cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if cursor: cursor.close()
        if cnx and cnx.is_connected(): cnx.close()

# --- API Endpoints ---
@app.get("/api/search_drops")
async def search_drops(
    request: Request,
    query: int = Query(..., description="Must be an integer"),
    query_type: Literal["item", "mob"] = Query(..., description="Choose either 'item' or 'mob'"),
    cursor: cursor.MySQLCursorDict = Depends(get_db_cursor)
):
    
    field = {
        "item": "itemid",
        "mob": "dropperid"
    }.get(query_type)

    sql_query = f"SELECT * FROM drop_data WHERE {field} = %s"
    cursor.execute(sql_query, (query,))
    results = cursor.fetchall()
    for row in results:
        if 'id' in row:
            row['id'] = str(row['id'])
    
    logger.info(f"Found {len(results)} results for query: {query}")
    return results

@app.get("/get_drop/{id}")
async def get_drop(id: int = Path(..., description="Must be an integer"), cursor: cursor.MySQLCursorDict = Depends(get_db_cursor)):
    sql_query = "SELECT * FROM drop_data WHERE id = %s"
    cursor.execute(sql_query, (id,))
    result = cursor.fetchone()
    
    if not result:
        raise HTTPException(status_code=404, detail="Drop record not found")
    
    if 'id' in result:
        result['id'] = str(result['id'])
    
    logger.info(f"Found drop record with id: {id}")
    return result

@app.put("/update_drop/{id}")
async def update_drop(id: int, drop: DropUpdate, request: Request, cursor: cursor.MySQLCursor = Depends(get_db_writer_cursor)):
    sql_update_query = """
        UPDATE drop_data 
        SET dropperid=%s, itemid=%s, minimum_quantity=%s, maximum_quantity=%s, questid=%s, chance=%s 
        WHERE id=%s
    """
    values = (drop.dropperid, drop.itemid, drop.minimum_quantity, drop.maximum_quantity, drop.questid, drop.chance, id)
    cursor.execute(sql_update_query, values)
    logger.info(f"Successfully updated drop record with id: {id}")
    return {"message": "Drop data updated successfully", "id": id}

@app.post("/add_drop")
async def add_drop(drop: DropCreate, request: Request, cursor: cursor.MySQLCursor = Depends(get_db_writer_cursor)):
    sql_insert_query = """
        INSERT INTO drop_data 
        (dropperid, itemid, minimum_quantity, maximum_quantity, questid, chance) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (drop.dropperid, drop.itemid, drop.minimum_quantity, drop.maximum_quantity, drop.questid, drop.chance)
    cursor.execute(sql_insert_query, values)
    new_id = cursor.lastrowid
    logger.info(f"Successfully added new drop record with id: {new_id}")
    return {"message": "Drop data added successfully", "id": new_id}

@app.delete("/delete_drop/{id}")
async def delete_drop(id: int, request: Request, cursor: cursor.MySQLCursor = Depends(get_db_writer_cursor)):
    sql_delete_query = "DELETE FROM drop_data WHERE id = %s"
    cursor.execute(sql_delete_query, (id,))
    
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Drop record not found")

    logger.info(f"Successfully deleted drop record with id: {id}")
    return {"message": "Drop data deleted successfully", "id": id}
