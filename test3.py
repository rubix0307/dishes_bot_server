import webbrowser

all_url = open('current_urls.txt', 'r').read().split('\n')


for url in all_url:
    if url:
        webbrowser.open(url)