import pymysql.cursors
from config import DB_USER, DB_PASSWORD, DEBUG

def get_connect(database='bot'):
    return pymysql.connect(host='localhost',
                             user=DB_USER,
                             password=DB_PASSWORD,
                             database=database,
                             cursorclass=pymysql.cursors.DictCursor,
                            )


def sql(query:str, database='bot', commit=False):
    try:
        with get_connect(database) as con:
            cursor = con.cursor()
            cursor.execute(query)

            if commit:
                con.commit()
                return True
            else:
                return cursor.fetchall()
                
    except Exception as ex:
        return False




def get_fav_dish_by_user(user_id, is_get_fav_ids = False):
    fav_data = sql(f'SELECT `dish_id` AS id FROM `fav_dish_user` WHERE user_id = {user_id}')
    if not is_get_fav_ids:
        return fav_data

    else:
        try:
            fav_ids = [data_id['id'] for data_id in fav_data]
        except:
            fav_ids = []
        finally:
            return fav_ids
















































