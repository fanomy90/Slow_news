# Задача парсинга
url = 'https://cisoclub.ru/category/news/'

def download_a_news():
    
    headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 OPR/68.0.3618.125'
    }
    href = []
    session = r.Session()
    session.headers = headers
    page = session.get(url)
    soup = BeautifulSoup(page.text, "lxml")
    links = soup.find_all('h3', class_='entry-title')
    posts = []

    for link in links:
        href = link.a.get('href')
        posts.append(href)

    news_data = []
    #Проверка для какой категории новости
    if 'economics' in url:
        cat_id = 6
        category_name = "Экономика"
        category_slug = "economics"
    elif 'politics' in url:
        cat_id = 7
        category_name = "Политика"
        category_slug = "politics"
    elif 'cisoclub.ru' in url:
        cat_id = 1
        category_name = "Безопасность"
        category_slug = "security"
    else:
        cat_id = 999  # Set a default value if the category cannot be determined from the URL
        category_name = "Other"
        category_slug = "other"

    for line in posts:
        page2 = session.get(line)
        soup2 = BeautifulSoup(page2.text, 'lxml')
        allNewsTitle = soup2.find('title').text
        allNewsPreview = soup2.find('div', class_='entry-content').text
        picNews = soup2.find('div', class_='photoandcap').a.get('href')
        linkNews = line

        title = allNewsTitle
        content = allNewsPreview
        photo_url = picNews

        #photo_filename = extract_image_filename(photo_url)
        photo_filename = photo_url.split('/')[-1]

        # Form the slug from the last part of the URL without the file extension
        #slug = linkNews.replace("/", "-")
        slug = linkNews.replace('https://', '').replace('/', '').replace('.', '-')

        woman_data = {
            "title": title,
            "slug": slug,
            "content": content,
            #"photo": f"C:\\test\\{photo_filename}",
            "cat_id": cat_id
        }
        news_data.append(woman_data)

    # Categories data (you can modify this part as needed)
    categories = [
        {"name": category_name, "slug": category_slug}
    ]

    # Combine categories and news data into the final structure
    data = {
        "categories": categories,
        "news": news_data
    }

    # Save the data as a JSON file with UTF-8 encoding
    file_name_news = settings.BASE_DIR / 'SAVE' / 'news.json'

    #with open('/home/skiner/site/puppeteer/news.json', 'w', encoding='utf-8') as json_file:
    with open(file_name_news, 'w', encoding='utf-8') as json_file:

        json.dump(data, json_file, ensure_ascii=False, indent=2)
        now = datetime.datetime.now()
        print(str(now) + ' parse cisoclub complete')
    return True
    #return f"{now} parse cisoclub complete"