import pymysql.cursors
from config import db_user, db_password
from markups import br

def get_connect(database='bot'):
    return pymysql.connect(host='localhost',
                             user=db_user,
                             password=db_password,
                             database=database,
                             cursorclass=pymysql.cursors.DictCursor,
                            )


def sql(sql:str, database='bot', commit=False):
    try:
        with get_connect(database) as con:
            cursor = con.cursor()
            cursor.execute(sql)

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

def get_ingredients_data_from_id(id: int):

    query = f'''SELECT ingredients.title, dishes_ingredients.value FROM dishes_ingredients 
        JOIN ingredients ON ingredients.id = dishes_ingredients.ingredient_id
        WHERE dishes_ingredients.dish_id = {id}'''.replace(br, '')

    return br.join([f'{i["title"]}: {i["value"]}' for i in sql(query)])

def get_categories_data_from_id(id: int):

    query = f'''SELECT categories.title FROM `dishes_categories`
        JOIN categories ON category_id = id
        WHERE dish_id = {id}'''.replace(br, '')

    return ', '.join([f'{i["title"]}' for i in sql(query)]).capitalize()

def get_photos_data_from_id(id: int):
            
    query = f'''SELECT `url` FROM `photos` WHERE dish_id = {id}'''

    return [i['url'].replace('c88x88', '900x-') for i in sql(query)]



















