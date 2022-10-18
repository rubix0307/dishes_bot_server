from db.functions import sql


for id in range(1,50000):

        photos = sql(f'SELECT url, local_photo FROM photos WHERE dish_id = {id}')

        numbers_by_dish = []
        for photo in photos:
            try:
                numbers = photo['url'].split('s1.eda.ru/StaticContent/Photos')[1]
                
                
                if numbers in numbers_by_dish:
            
                    sql(f'DELETE FROM `photos` WHERE dish_id = {id} AND url LIKE "%{numbers}%"', commit=True)
                    new_url = f'https://eda.ru/img/eda/900x-/s1.eda.ru/StaticContent/Photos{numbers}'
                    sql(f'INSERT INTO `photos`(`dish_id`, `url`, `local_photo`) VALUES ({id},"{new_url}","{photo["local_photo"]}")', commit=True)
                    print(id)
                else:
                    numbers_by_dish.append(numbers)
            except:
                pass

            