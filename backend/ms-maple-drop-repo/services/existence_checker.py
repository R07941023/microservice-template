from typing import List
from mysql.connector import cursor
from models import ExistenceInfo, ExistenceResult

def check_existence(
    cursor: cursor.MySQLCursorDict, 
    items: List[ExistenceInfo]
) -> List[ExistenceResult]:
    
    mob_ids_to_check = [item.id for item in items if item.type == 'mob']
    item_ids_to_check = [item.id for item in items if item.type == 'item']

    existing_mob_ids = set()
    existing_item_ids = set()

    sql_parts = []
    params = []

    if mob_ids_to_check:
        mob_placeholders = ','.join(['%s'] * len(mob_ids_to_check))
        sql_parts.append(f"SELECT 'mob' as type, dropperid as id FROM drop_data WHERE dropperid IN ({mob_placeholders})")
        params.extend(mob_ids_to_check)

    if item_ids_to_check:
        item_placeholders = ','.join(['%s'] * len(item_ids_to_check))
        sql_parts.append(f"SELECT 'item' as type, itemid as id FROM drop_data WHERE itemid IN ({item_placeholders})")
        params.extend(item_ids_to_check)

    if sql_parts:
        full_query = " UNION ALL ".join(sql_parts)
        cursor.execute(full_query, tuple(params))
        db_results = cursor.fetchall()

        for row in db_results:
            if row['type'] == 'mob':
                existing_mob_ids.add(row['id'])
            elif row['type'] == 'item':
                existing_item_ids.add(row['id'])
        
    final_results = []
    for item in items:
        exists = False
        if item.type == 'mob':
            exists = item.id in existing_mob_ids
        elif item.type == 'item':
            exists = item.id in existing_item_ids
        
        final_results.append(ExistenceResult(type=item.type, id=item.id, drop_exist=exists))

    return final_results
