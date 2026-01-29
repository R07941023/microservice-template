"""Maple drop repository microservice for MySQL drop data operations."""

import logging
import os
from typing import Literal

import mysql.connector
from fastapi import FastAPI, HTTPException, Request, Depends, Query, Path
from mysql.connector import pooling, cursor

from models import DropUpdate, DropCreate, ExistenceCheckRequest, ExistenceCheckResponse
from services.existence_checker import check_existence
from utils.auth import User, get_current_user
from utils.health import router as health_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
app.include_router(health_router)

# Database Configuration
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


def get_db_cursor(request: Request) -> cursor.MySQLCursorDict:
    """Get database cursor for read operations."""
    cnx = None
    db_cursor = None
    try:
        cnx = cnxpool.get_connection()
        db_cursor = cnx.cursor(dictionary=True)
        yield db_cursor
    except mysql.connector.Error as err:
        logger.error("Database error: %s", err, exc_info=True)
        raise HTTPException(status_code=500, detail=f"Database error: {err}") from err
    finally:
        if db_cursor:
            db_cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()


def get_db_writer_cursor(request: Request) -> cursor.MySQLCursor:
    """Get database cursor for write operations."""
    cnx = None
    db_cursor = None
    try:
        cnx = cnxpool.get_connection()
        db_cursor = cnx.cursor()
        yield db_cursor
        cnx.commit()
    except mysql.connector.Error as err:
        logger.error("Database error on write: %s", err, exc_info=True)
        if cnx:
            cnx.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {err}") from err
    finally:
        if db_cursor:
            db_cursor.close()
        if cnx and cnx.is_connected():
            cnx.close()


@app.get("/api/search_drops")
async def search_drops(
    request: Request,
    query: int = Query(..., description="Must be an integer"),
    query_type: Literal["item", "mob"] = Query(..., description="Choose either 'item' or 'mob'"),
    db_cursor: cursor.MySQLCursorDict = Depends(get_db_cursor),
    user: User = Depends(get_current_user),
):
    """
    Search drops by item or mob ID.

    Args:
        request: FastAPI request object.
        query: ID to search for.
        query_type: Type of query (item or mob).
        db_cursor: Database cursor.
        user: Current authenticated user.

    Returns:
        List of matching drop records.
    """
    logger.info("User %s searching drops: query=%d, type=%s", user.name, query, query_type)

    field = {
        "item": "itemid",
        "mob": "dropperid"
    }.get(query_type)

    sql_query = f"SELECT * FROM drop_data WHERE {field} = %s"
    db_cursor.execute(sql_query, (query,))
    results = db_cursor.fetchall()
    for row in results:
        if 'id' in row:
            row['id'] = str(row['id'])

    logger.info("Found %d results for user %s", len(results), user.name)
    return results


@app.get("/get_drop/{id}")
async def get_drop(
    id: int = Path(..., description="Must be an integer"),
    db_cursor: cursor.MySQLCursorDict = Depends(get_db_cursor),
    user: User = Depends(get_current_user),
):
    """
    Get a single drop record by ID.

    Args:
        id: Drop record ID.
        db_cursor: Database cursor.
        user: Current authenticated user.

    Returns:
        Drop record.

    Raises:
        HTTPException: 404 if not found.
    """
    logger.info("User %s getting drop: id=%d", user.name, id)

    sql_query = "SELECT * FROM drop_data WHERE id = %s"
    db_cursor.execute(sql_query, (id,))
    result = db_cursor.fetchone()

    if not result:
        raise HTTPException(status_code=404, detail="Drop record not found")

    if 'id' in result:
        result['id'] = str(result['id'])

    return result


@app.put("/update_drop/{id}")
async def update_drop(
    id: int,
    drop: DropUpdate,
    request: Request,
    db_cursor: cursor.MySQLCursor = Depends(get_db_writer_cursor),
    user: User = Depends(get_current_user),
):
    """
    Update a drop record.

    Args:
        id: Drop record ID to update.
        drop: New drop data.
        request: FastAPI request object.
        db_cursor: Database cursor.
        user: Current authenticated user.

    Returns:
        Success message with ID.
    """
    logger.info("User %s updating drop: id=%d", user.name, id)

    sql_update_query = """
        UPDATE drop_data 
        SET dropperid=%s, itemid=%s, minimum_quantity=%s, maximum_quantity=%s, questid=%s, chance=%s 
        WHERE id=%s
    """
    values = (drop.dropperid, drop.itemid, drop.minimum_quantity, drop.maximum_quantity, drop.questid, drop.chance, id)
    db_cursor.execute(sql_update_query, values)

    logger.info("User %s successfully updated drop record: id=%d", user.name, id)
    return {"message": "Drop data updated successfully", "id": id}


@app.post("/add_drop")
async def add_drop(
    drop: DropCreate,
    request: Request,
    db_cursor: cursor.MySQLCursor = Depends(get_db_writer_cursor),
    user: User = Depends(get_current_user),
):
    """
    Add a new drop record.

    Args:
        drop: Drop data to create.
        request: FastAPI request object.
        db_cursor: Database cursor.
        user: Current authenticated user.

    Returns:
        Success message with new ID.
    """
    logger.info("User %s adding new drop", user.name)

    sql_insert_query = """
        INSERT INTO drop_data 
        (dropperid, itemid, minimum_quantity, maximum_quantity, questid, chance) 
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    values = (drop.dropperid, drop.itemid, drop.minimum_quantity, drop.maximum_quantity, drop.questid, drop.chance)
    db_cursor.execute(sql_insert_query, values)
    new_id = db_cursor.lastrowid

    logger.info("User %s successfully added drop record: id=%d", user.name, new_id)
    return {"message": "Drop data added successfully", "id": new_id}


@app.delete("/delete_drop/{id}")
async def delete_drop(
    id: int,
    request: Request,
    db_cursor: cursor.MySQLCursor = Depends(get_db_writer_cursor),
    user: User = Depends(get_current_user),
):
    """
    Delete a drop record.

    Args:
        id: Drop record ID to delete.
        request: FastAPI request object.
        db_cursor: Database cursor.
        user: Current authenticated user.

    Returns:
        Success message with ID.

    Raises:
        HTTPException: 404 if not found.
    """
    logger.info("User %s deleting drop: id=%d", user.name, id)

    sql_delete_query = "DELETE FROM drop_data WHERE id = %s"
    db_cursor.execute(sql_delete_query, (id,))

    if db_cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Drop record not found")

    logger.info("User %s successfully deleted drop record: id=%d", user.name, id)
    return {"message": "Drop data deleted successfully", "id": id}


@app.post("/api/drops/exist", response_model=ExistenceCheckResponse)
async def check_drops_exist(
    request: ExistenceCheckRequest,
    db_cursor: cursor.MySQLCursorDict = Depends(get_db_cursor),
    user: User = Depends(get_current_user),
) -> ExistenceCheckResponse:
    """
    Check if drops exist in the database.

    Args:
        request: Request containing items to check.
        db_cursor: Database cursor.
        user: Current authenticated user.

    Returns:
        Response with existence check results.
    """
    logger.info("User %s checking existence of %d items", user.name, len(request.items))

    final_results = check_existence(db_cursor, request.items)
    return ExistenceCheckResponse(results=final_results)


@app.get("/health/ready")
async def readiness() -> dict:
    """
    Readiness probe endpoint.

    Checks if MySQL dependency is available.

    Returns:
        Status dict with dependency states.

    Raises:
        HTTPException: 503 if MySQL is unavailable.
    """
    cnx = None
    try:
        cnx = cnxpool.get_connection()
        cnx.ping(reconnect=True)
    except mysql.connector.Error as e:
        logger.error("MySQL health check failed: %s", e)
        raise HTTPException(status_code=503, detail="MySQL unavailable") from e
    finally:
        if cnx and cnx.is_connected():
            cnx.close()

    return {
        "status": "ready",
        "mysql": "connected",
    }
