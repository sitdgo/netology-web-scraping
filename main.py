import time
import requests
import re
from bs4 import BeautifulSoup

# Определяем список ключевых слов
KEYWORDS = ['дизайн', 'фото', 'web', 'python']

# Сразу превращаем список ключей во множество (set) для быстрого поиска
KEYWORDS_SET = set(k.lower() for k in KEYWORDS)

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36'
}

def get_habr_articles():
    url = 'https://habr.com/ru/articles/'

    # Отправляем запрос на главную страницу
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.find_all('article')

    for article in articles:
        # 1. Извлекаем заголовок и ссылку
        title_element = article.find('h2')
        if not title_element:
            continue

        link_element = title_element.find('a')
        if not link_element:
            continue

        title = link_element.text.strip()
        href = link_element.get('href')
        link = f"https://habr.com{href}" if href.startswith('/') else href

        # 2. Извлекаем дату
        time_element = article.find('time')
        date = time_element.get('datetime') if time_element else 'Дата не указана'

        # 3. Парсим полный текст статьи с ОБРАБОТКОЙ ИСКЛЮЧЕНИЙ
        try:
            # Установили таймаут, чтобы не зависнуть навсегда, если сервер тормозит
            article_response = requests.get(link, headers=HEADERS, timeout=10)
            article_response.raise_for_status()
        except requests.exceptions.RequestException as e:
            # Если произошла ошибка (404, таймаут, сбой сети), печатаем ошибку и идем дальше
            print(f"[-] Пропуск статьи {link} из-за ошибки: {e}")
            continue

        article_soup = BeautifulSoup(article_response.text, 'html.parser')

        # ИСПРАВЛЕНИЕ 1: Ищем только блок с самим текстом статьи (без комментариев и меню)
        # На Хабре класс обычно содержит 'article-formatted-body'
        body_element = article_soup.find('div', class_=re.compile('article-formatted-body'))

        # Если тело найдено, берем текст оттуда. Иначе берем весь текст (страховка)
        raw_text = body_element.text.lower() if body_element else article_soup.text.lower()

        # ИСПРАВЛЕНИЕ 3: Оптимизация поиска через множества
        # re.findall(r'\w+', raw_text) разбивает текст на слова, выкидывая запятые, точки и скобки
        text_words_set = set(re.findall(r'\w+', raw_text))

        # Оператор & находит пересечение двух множеств. Если есть совпадения - статья подходит
        if KEYWORDS_SET & text_words_set:
            print(f"{date} – {title} – {link}")

        time.sleep(0.3)


if __name__ == '__main__':
    print("Начинаю парсинг статей с Хабра. Это может занять пару секунд...")
    get_habr_articles()
    print("Парсинг завершен!")