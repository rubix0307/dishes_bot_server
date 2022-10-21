import time
from db.functions import sql
import pymorphy2



morph = pymorphy2.MorphAnalyzer()
def get_normal_form(text: str):
    
    text = text.replace('(', '').replace(')', '').replace('\'', '')


    prelogs = [' без ', ' безо ', ' близ ', ' в ',  ' во ', ' вместо ', ' вне ', ' для ', ' до ', ' за ', ' из ', ' изо ', ' и ', ' к ',  ' ко ', ' кроме ', ' между ', ' меж ', ' на ', ' над ', ' надо ', ' о ',  ' об ', ' обо ', ' от ', ' ото ', ' перед ', ' передо ', ' предо ', ' пo ', ' под ', ' при ', ' про ', ' ради ', ' с ',  ' со ', ' сквозь ', ' среди ', ' через ', ' чрез ']
    for sumb in prelogs:
        text = text.replace(sumb, ' ')

    normal_form = [morph.parse(i)[0].normal_form for i in text.split()]

    return ' '.join(normal_form)






if __name__ == '__main__':

    all_titles = sql('SELECT id, title FROM categories')
    start = time.time()
    for data in all_titles:
        id = data['id']
        title = data['title']
        norm_title = get_normal_form(title)

        sql(f'''UPDATE `categories` SET norm_title='{norm_title}' WHERE id = {id}''', commit=True)

    print(f'edit {len(all_titles)} titles  by {time.time() - start}s')







