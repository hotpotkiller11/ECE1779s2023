from flask import Flask

webapp = Flask(__name__)

from MemCache import main

# init?
main.filesize = 0
main.total_miss = 0
main.total_hit = 0
main.reqs = 0


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
    query = '''INSERT INTO `backend_config` (`capacity`, `policy`) VALUES (1024000, "random")'''
    cursor = cnx.cursor()
    cursor.execute(query)
    cnx.commit() # Try to commit (confirm) the insertion
    cursor.close()
    main.Config = {'capacity': 1024000, 'policy': "random"} # Default value: 1000KB

# Clear stat from last run
query = '''DELETE FROM `backend_statistic`'''
cursor = cnx.cursor()
cursor.execute(query)
cnx.commit()
cursor.close()
cnx.close()

cnx.close()

# main.Config = {'capacity': 400, 'policy': "random"}
