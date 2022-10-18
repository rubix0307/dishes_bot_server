import random
import threading
import time as t_time

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

from db import functions


def get_cooking_time(c_time: str):

    if 'сутки' in c_time:
        time = int(c_time.split()[0])
        cooking_time = f'{24 * time}:00:00'

    elif 'час' in c_time:
        times = c_time.split()
        time = []
        for i in times:
            try:
                time.append(int(i))
            except:
                continue

        if len(time) == 1:
            cooking_time = f'{f"0{time[0]}" if time[0] < 10 else time[0]}:00:00'
        if len(time) == 2:
            cooking_time = f'{f"0{time[0]}" if time[0] < 10 else time[0]}:{f"0{time[1]}" if time[1] < 10 else time[1]}:00'

    elif 'минут' in c_time:
        time = int(c_time.split()[0])
        cooking_time = f'00:{f"0{time}" if time < 10 else time}:00'

    return cooking_time

def get_driver():

    caps = DesiredCapabilities().CHROME
    caps["pageLoadStrategy"] = "eager"
    options = webdriver.ChromeOptions()
    options.headless = True
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument(f"user-agent=Mozilla/5.{random.randint(1,9999)} (Windows NT 10.0; Win64; x647) AppleWebKit/537.{random.randint(1,9999)} (KHTML, like Gecko) Chrome/98.0.4788.{random.randint(1,9999)} Safari/557.36")
    driver = webdriver.Chrome(executable_path="chromedriver.exe", 
                            options=options,
                            desired_capabilities=caps,
                            )
    return driver

def light_element(driver, element):
    return
    # try:
    #     action = ActionChains(driver)
    #     action.move_to_element(element).perform()
    #     # driver.execute_script("arguments[0].style.border = \"5px solid red\"",element)
    #     driver.execute_script("arguments[0].style.border = \"2px solid green\"",element)
    # except:
    #     pass



def get_id_ing(title):
    for i in range(2):
        id = functions.sql(f'SELECT id FROM ingredients WHERE title = "{title}"', database='bot', fetchall=True)
        if not id:
            functions.sql(f'INSERT INTO `ingredients`(`title`) VALUES ("{title}")', database='bot', fetchall=True)
        else:
            return id[0]['id']
def add_data(data):

    recipe = '\n'.join(data['recipe'])

    dishes = f'''INSERT INTO `dishes`(`id`, `title`, `original_link`, `serving`, `cooking_time`, `kilocalories`, `protein`, `fats`, `carbohydrates`, `recipe`, `likes`) VALUES ({data['id']},"{data['title']}","{data['original_link']}",{data['serving']},"{data['cooking_time']}",{data['enegry']['kilocalories']},{data['enegry']['protein']},{data['enegry']['fats']},{data['enegry']['carbohydrates']},"{recipe}", {data['likes']});'''


    dishes_categories_data = ','.join([f'({data["id"]}, {cat})' for cat in data['categories']])
    dishes_categories = f'''INSERT INTO `dishes_categories`(`dish_id`, `category_id`) VALUES {dishes_categories_data};'''

    dishes_ingredients_data = ','.join(
        [f'({data["id"]}, {get_id_ing(ing["title"])}, "{ing["value"]}")'
        for ing in data['ingredients']]
        )
    dishes_ingredients = f'''INSERT INTO `dishes_ingredients`(`dish_id`, `ingredient_id`, `value`) VALUES {dishes_ingredients_data};'''

    photos_data = ','.join([f'({data["id"]}, "{img}")' for img in data['images']])
    photos = f'''INSERT INTO `photos` (`dish_id`, `url`) VALUES {photos_data};'''
    
    is_dishes = functions.sql(dishes, database='bot')
    is_dishes_categories = functions.sql(dishes_categories, database='bot')
    is_dishes_ingredients = functions.sql(dishes_ingredients, database='bot')
    is_photos = functions.sql(photos, database='bot')

    answer = [is_dishes, is_dishes_categories, is_dishes_ingredients, is_photos]

    for a in answer:
        if not a:
            open('scrap.txt', 'a').write(f'''{data['original_link']}\n''')
            break
    return

def get_recipe(driver):
    global all_times
    global confirmed_urls
    global all_url
    start_time = t_time.time()


    try:
        for i in all_url:
            if not i['link'] in confirmed_urls:
                confirmed_urls.append(i['link'])
                data_url = i
                # print(i['link'])
                break

        driver.get(data_url['link'])


        title_xpath = '//*[@id="__next"]/main/div/div/div/div/div[1]/div[2]/div[2]/span/h1'

        error = 0
        while True:
            try:
                title = driver.find_element(By.XPATH, title_xpath)
                break
            except:
                t_time.sleep(0.5)
                error += 1
                if error == 30:
                    driver.refresh()

        light_element(driver, title)
        title = title.text.capitalize()

        categories = []
        categories_text = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/div/div/div/div[1]/div[2]/div[1]/div/div')
        light_element(driver, categories_text)

        for i in categories_text.text.lower().split('\n'):
            category_id = functions.sql(f'SELECT `id` FROM `categories` WHERE title = "{i.capitalize()}"', database='bot', fetchall=True)
            
            if len(category_id):
                category_id = category_id[0]['id']
                categories.append(category_id)


        serving = driver.find_element(By.XPATH, '//*[@id="__next"]/main/div/div/div/div/div[1]/div[2]/div[3]/div[1]/span[1]/span[2]/span')
        light_element(driver, serving)
        serving = int(serving.text)

        cooking_time_xpath = '//*[@id="__next"]/main/div/div/div/div/div[1]/div[2]/div[3]/div[1]/span[2]/div[1]'
        cooking_time = driver.find_element(By.XPATH, cooking_time_xpath)
        light_element(driver, cooking_time)
        cooking_time = get_cooking_time(cooking_time.text.lower())

        likes_xapth = '//*[@id="__next"]/main/div/div/div/div/div[1]/div[2]/div[3]/span/div/div'
        likes = driver.find_element(By.XPATH, likes_xapth)
        light_element(driver, likes)
        likes = int(likes.text.split('\n')[0])

        images = []
        try:
            image_xpath = '//*[@id="__next"]/main/div/div/div/div/div[2]/div[1]/div[1]/button/div/img'
            image = driver.find_element(By.XPATH, image_xpath)
            light_element(driver, image)
            images.append(image.get_attribute('src'))
        except:
            pass

        for image_num in range(1,5):
            try:
                image_xpath = f'//*[@id="__next"]/main/div/div/div/div/div[2]/div[1]/div[1]/div[2]/button[{image_num}]/div/img'
                image = driver.find_element(By.XPATH, image_xpath)
                light_element(driver, image)
                images.append(image.get_attribute('src'))
            except:
                try:
                    image_xpath = f'//*[@id="__next"]/main/div/div/div/div/div[2]/div[1]/div[1]/div/button[{image_num}]/div/img'
                    image = driver.find_element(By.XPATH, image_xpath)
                    light_element(driver, image)
                    images.append(image.get_attribute('src'))
                except:
                    continue

        enegry_xpath = '//*[@id="__next"]/main/div/div/div/div/div[2]/div[1]/div[2]/span/div'
        enegry_data = driver.find_element(By.XPATH, enegry_xpath)
        light_element(driver, enegry_data)
        enegry_data = enegry_data.text.lower().split('\n')
        enegry = {
            'kilocalories': int(enegry_data[0]),
            'protein': int(enegry_data[1]),
            'fats': int(enegry_data[2]),
            'carbohydrates': int(enegry_data[3]),
        }

        ingredients = []
        for i in range(2,100):
            try:
                ingredients_xpath = f'//*[@id="__next"]/main/div/div/div/div/div[2]/div[1]/div[3]/div/div[{i}]'
                ingredients_data = driver.find_element(By.XPATH, ingredients_xpath)
                light_element(driver, ingredients_data)
                name, value = ingredients_data.text.lower().split('\n')
                ingredients.append(
                    {
                        'title': name.capitalize(),
                        'value': value,
                    }
                )
            except:
                continue

        recipe = []
        errors = 0
        for i in range(2, 100):
            try:
                recipe_xpath = f'//*[@id="__next"]/main/div/div/div/div/div[3]/div/div[1]/div[{i}]/div/div/div[2]/div/div[1]'
                step_recipe = driver.find_element(By.XPATH, recipe_xpath + '/span[1]')
                instr_recipe = driver.find_element(By.XPATH, recipe_xpath + '/span[2]')
                light_element(driver, step_recipe)
                light_element(driver, instr_recipe)
                if step_recipe:
                    text = step_recipe.text
                    recipe.append(f'{step_recipe.text} - {instr_recipe.text}')
                else:
                    continue
            except:
                try:
                    recipe_xpath = f'//*[@id="__next"]/main/div/div/div/div/div[3]/div/div[1]/div[{i}]/div/div/div/div/div[1]'
                    step_recipe = driver.find_element(By.XPATH, recipe_xpath + '/span[1]')
                    instr_recipe = driver.find_element(By.XPATH, recipe_xpath + '/span[2]')
                    light_element(driver, step_recipe)
                    light_element(driver, instr_recipe)
                    if step_recipe:
                        text = step_recipe.text
                        recipe.append(f'{step_recipe.text} - {instr_recipe.text}')

                except:
                    errors += 1
                    if errors > 10:
                        break
                    continue

        data = {
            'id': data_url['id'],
            'title': title,
            'original_link': data_url['link'],
            'categories': categories,
            'serving': serving,
            'cooking_time': cooking_time,
            'likes': likes,
            'images': images,
            'enegry': enegry,
            'ingredients': ingredients,
            'recipe': recipe,
        }
        add_data(data)
        all_times.append(t_time.time() - start_time)
        print(f'''{data_url['id']} | {sum(all_times)/len(all_times)}''')

    except Exception as ex:
        pass
    finally:
        return get_recipe(driver)
      







all_times = []

all_url = functions.sql('SELECT id,link FROM dish', fetchall=True)
confirmed_urls = [i['original_link'] for i in functions.sql('SELECT id, original_link FROM dishes', fetchall=True, database='bot')]

for i in range(7):
    threading.Thread(target = get_recipe, args = (get_driver(),)).start()

    





















