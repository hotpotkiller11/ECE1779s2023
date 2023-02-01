from FrontEnd import db_connect

def get_all_keys():# -> list[str]:
    ''' Return all keys stored in the database
        If the table is currently empty, an empty list will be returned.
    '''
    db = db_connect.get_db()
    query = 'SELECT `key` FROM `key_picture` ORDER BY `key`' # instantiate query statement
    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    result_list = []
    for s in result:
        result_list.append(s[0])
    # db.close()
    return result_list

def get_keys_page(page: int, item: int):# -> list[str]:
    ''' Return keys stored in the data base in page.
        Note that page start from 0
    '''
    db = db_connect.get_db()
    query = 'SELECT `key` FROM `key_picture` ORDER BY `key` LIMIT %d OFFSET %d' % (item, page * item) # instantiate query statement
    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    result_list = []
    for s in result:
        result_list.append(s[0])
    # db.close()
    return result_list

def get_path_by_key(key: str) -> str:
    ''' Return the path of the indexed key from the database.
        If no valid term match, return None.
    '''
    db = db_connect.get_db()
    query = 'SELECT `path` FROM `key_picture` WHERE `key` = "%s"' % key # instantiate query statement
    cursor = db.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    cursor.close()
    if len(result) == 0:
        return None
    # db.close()
    return result[0][0]

def add_key_and_path(key: str, path: str) -> bool:
    ''' Record the key and path into the database.
        Return if the key and path stored successfully.
    '''
    db = db_connect.get_db()
    query = 'INSERT INTO `key_picture` (`key`, `path`) VALUES ("%s", "%s");' % (key, path) # instantiate query statement
    cursor = db.cursor()
    try:
        cursor.execute(query)
        db.commit() # Try to commit (confirm) the insertion
        cursor.close()
        # db.close()
    except:
        db.rollback() # Try to rollback in case of error
        cursor.close()
        # db.close()
        return False
    return True

def delete_term_by_key(key: str) -> bool:
    ''' Delete a term with a specified key in the database.
        Return true if the deletion succeed.
    '''
    db = db_connect.get_db()
    query = 'DELETE FROM `key_picture` WHERE `key` = "%s"' % (key) # instantiate query statement
    cursor = db.cursor()
    try:
        cursor.execute(query)
        db.commit() # Try to commit (confirm) the insertion
        cursor.close()
        # db.close()
    except:
        db.rollback() # Try to rollback in case of error
        cursor.close()
        # db.close()
        return False
    return True

def delete_all_key_path_term() -> bool:
    ''' Delete all terms in the key_picture table.
        Return true if the deletion succeed. 
        (If the table was initially empty, true will also returned)
    '''
    db = db_connect.get_db()
    query = 'DELETE FROM `key_picture`' # instantiate query statement
    cursor = db.cursor()
    try:
        cursor.execute(query)
        db.commit() # Try to commit (confirm) the insertion
        cursor.close()
    except:
        db.rollback() # Try to rollback in case of error
        cursor.close()
        # db.close()
        return False
    return True