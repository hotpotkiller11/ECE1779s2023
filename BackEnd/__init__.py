from flask import Flask

webapp = Flask(__name__)

from BackEnd import main

# Fetch memcache config upon initialization, default value: 4KB, random replacement

cnx = main.init_db()
query = '''SELECT capacity, policy
                FROM backend_config where id = (
    select max(id) FROM backend_config);'''
cursor = cnx.cursor()
cursor.execute(query)
rows = cursor.fetchall()
if len(rows) > 0:
    main.Config = {'capacity': rows[0][0], 'policy': rows[0][1]}
else:
    query = '''INSERT INTO `backend_config` (`capacity`, `policy`) VALUES (4096, "random")'''
    cursor = cnx.cursor()
    cursor.execute(query)
    cnx.commit() # Try to commit (confirm) the insertion
    cursor.close()
    main.Config = {'capacity': 4096, 'policy': "random"}
cnx.close()

# main.Config = {'capacity': 400, 'policy': "random"}
