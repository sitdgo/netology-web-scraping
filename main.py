import time
import requests
from bs4 import BeautifulSoup

# Определяем список ключевых слов:
KEYWORDS = ['дизайн', 'фото', 'web', 'python']

# Добавляем заголовки, чтобы сервер думал, что мы обычный браузер
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36'
}


def get_habr_articles():
    url = 'https://habr.com/ru/articles/'

    # Отправляем запрос на главную страницу
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()  # Проверка, что сайт ответил успешно (код 200)

    # Парсим HTML-код страницы
    soup = BeautifulSoup(response.text, 'html.parser')

    # Находим все карточки статей (на Хабре они лежат в тегах <article>)
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

        # Хабр использует относительные ссылки, поэтому приклеиваем домен, если нужно
        link = f"https://habr.com{href}" if href.startswith('/') else href

        # 2. Извлекаем дату (лежит в теге <time>)
        time_element = article.find('time')
        # Берем красивую дату из атрибута datetime
        date = time_element.get('datetime') if time_element else 'Дата не указана'

        # 3. Дополнительное задание: парсим полный текст статьи
        # Делаем запрос по ссылке конкретной статьи
        article_response = requests.get(link, headers=HEADERS)
        article_soup = BeautifulSoup(article_response.text, 'html.parser')

        # Получаем весь текст страницы и переводим в нижний регистр
        full_text = article_soup.text.lower()

        # Проверяем, есть ли хотя бы одно ключевое слово в тексте
        is_match = False
        for keyword in KEYWORDS:
            # Искомое слово тоже переводим в нижний регистр на всякий случай
            if keyword.lower() in full_text:
                is_match = True
                break  # Нашли совпадение - дальше слова можно не проверять

        # Если статья подошла, печатаем результат
        if is_match:
            print(f"{date} – {title} – {link}")

        # Небольшая пауза, чтобы не спамить запросами (хороший тон в скрапинге)
        time.sleep(0.3)


if __name__ == '__main__':
    print("Начинаю парсинг статей с Хабра. Это может занять пару секунд...")
    get_habr_articles()
    print("Парсинг завершен!")