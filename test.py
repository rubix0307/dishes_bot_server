
from db.functions import sql







with open('cats.txt', 'a', encoding="UTF-8") as txt:
        for i in range(82, 95):
            cat_title = sql(f'''SELECT title FROM categories WHERE id = {i}''')[0]['title']
            ing_in_category = sql(f'''SELECT i.title, ingredient_id, COUNT(*) as `count` FROM `dishes_ingredients` as di
INNER JOIN ingredients as i ON i.id = di.ingredient_id
WHERE dish_id in (SELECT dish_id FROM `dishes_categories` WHERE category_id = {i})
GROUP BY ingredient_id  
ORDER BY `count`  DESC''')
            top8 =','.join([f'''"{n['title'].lower()}"''' for n in ing_in_category[:5]])

            text = f'''
ingredients: [{top8}],
categories: ['{cat_title}'],'''

            wr_text = '{' + text + '\n},\n'
            txt.write(wr_text)