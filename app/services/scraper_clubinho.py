# scraper_clubinho.py

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import re

BASE_URL = "https://clubinhodeofertas.com.br/sao-paulo/busca?genres="

CATEGORIES = [
    "Teatro Infantil", "Parques", "Musical Infantil", "Teatro adulto",
    "Teatro Sabesp Frei Caneca", "Restaurante", "Stand-up comedy",
    "Parque Indoor", "Show", "Vassoura quebrada", "K-pop", "Show Musical",
    "Circo", "Parque Aquático", "Recreação", "Stand Up",
    "Teatro para bebês", "day use", "Afrika Park", "Bailinho de Halloween"
]


def start_driver():
    options = Options()
    options.add_argument("--headless")  # Roda sem abrir a janela do navegador
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    return webdriver.Chrome(options=options)


def parse_days(days_text: str):
    """Extrai start_date e end_date a partir do campo days_text."""
    if not days_text:
        now = datetime.utcnow()
        return now, now

    # Remove o prefixo "Dias"
    clean_text = days_text.replace("Dias", "").strip()

    # Extrai pedaços como "27", "04/10", "11/10" etc
    parts = re.findall(r"\d{1,2}(?:/\d{1,2})?", clean_text)

    dates = []
    current_year = datetime.utcnow().year
    current_month = datetime.utcnow().month

    for part in parts:
        if "/" in part:  # formato dd/mm
            try:
                dt = datetime.strptime(f"{part}/{current_year}", "%d/%m/%Y")
                dates.append(dt)
            except:
                continue
        else:  # só o dia (ex: "27")
            try:
                dt = datetime(current_year, current_month, int(part))
                dates.append(dt)
            except:
                continue

    if not dates:
        now = datetime.utcnow()
        return now, now

    return min(dates), max(dates)


def scrape_category(driver, category: str):
    url = BASE_URL + category.replace(" ", "%20")
    driver.get(url)

    events = []
    try:
        cards_xpath = "//a[@class='product-thumb']"
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, cards_xpath))
        )
        cards = driver.find_elements(By.XPATH, cards_xpath)

    except TimeoutException:
        print(f"Nenhum evento encontrado para a categoria '{category}'")
        return []

    for card in cards:
        try:
            name = card.find_element(
                By.CLASS_NAME, "product-thumb__title").text
        except:
            name = None

        try:
            link = card.get_attribute("href")
        except:
            link = None

        try:
            image = card.find_element(By.TAG_NAME, "img").get_attribute("src")
        except:
            image = None

        try:
            venue = card.find_element(
                By.CLASS_NAME, "product-thumb__venue").text
        except:
            venue = None

        try:
            days = card.find_element(By.CLASS_NAME, "product-thumb__days").text
        except:
            days = None

        start_date, end_date = parse_days(days)

        event_doc = {
            "name": name,
            "detail": None,
            "start_date": start_date,
            "end_date": end_date,
            "private_event": 0,
            "published": 1,
            "cancelled": 0,
            "image": image,
            "url": link,
            "address": {
                "name": venue,
                "address": None,
                "address_num": None,
                "address_alt": None,
                "neighborhood": None,
                "city": None,
                "state": None,
                "zip_code": None,
                "country": None,
                "lon": None,
                "lat": None,
            },
            "host": {"name": None, "description": None},
            "category_prim": {"name": category},
            "category_sec": None,
            "organizer_id": None,  # preenchido pela API
            "created_at": datetime.utcnow(),
            "raw_days": days
        }

        events.append(event_doc)

    return events


def scrape_all():
    driver = start_driver()
    all_events = []
    try:
        for cat in CATEGORIES:
            events_from_category = scrape_category(driver, cat)
            print(
                f"Categoria '{cat}' → {len(events_from_category)} eventos coletados")
            all_events.extend(events_from_category)
    finally:
        driver.quit()

    # Remove duplicatas baseadas na URL do evento
    unique_events = {event['url']: event for event in all_events}.values()
    print(f"\nTotal de eventos únicos coletados: {len(unique_events)}")

    return list(unique_events)


if __name__ == '__main__':
    # Para testar o scraper de forma independente
    scraped_data = scrape_all()
    # print(scraped_data)
