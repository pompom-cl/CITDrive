from database import *


conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="052005"
)

cursor = conn.cursor()

# preparing database
drop_database(cursor)
create_database(cursor)
create_tbcatalogue(cursor)
create_tbuser(cursor)
create_tbrenting(cursor)


# dummy data
insert_template_catalogue(cursor)
insert_user(cursor, 'admin', 'admin')
insert_user(cursor, 'clahava', 'clahava')
insert_rent(cursor, 1, 1, "Clara", "087709238755", "Jalan Bahagia", "2025-03-23", 2)
conn.commit()