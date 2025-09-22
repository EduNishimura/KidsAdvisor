# scraper_clubinho.py

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

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


def scrape_category(driver, category: str):
    url = BASE_URL + category.replace(" ", "%20")
    driver.get(url)

    events = []
    try:
        # 1. SELETOR CORRIGIDO: Agora busca pela tag 'a' com a classe 'product-thumb', que corresponde a cada card.
        cards_xpath = "//a[@class='product-thumb']"

        # 2. ESPERA EXPLÍCITA: Aguarda até 10 segundos para que os cards apareçam na página. É mais eficiente que time.sleep().
        WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, cards_xpath))
        )

        cards = driver.find_elements(By.XPATH, cards_xpath)

    except TimeoutException:
        print(
            f"Nenhum evento encontrado para a categoria '{category}' ou a página não carregou a tempo.")
        return []

    for card in cards:
        # A extração de dados já estava quase perfeita.
        # Como o 'card' agora é o elemento 'a', ajustamos a busca do link.
        try:
            name = card.find_element(
                By.CLASS_NAME, "product-thumb__title").text
        except:
            name = None

        try:
            # O link é o atributo 'href' do próprio card.
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

        event_doc = {
            # "id" e "reference_id" serão gerados pelo seu banco de dados ou outra lógica
            "name": name,
            # Detalhes podem ser obtidos acessando a 'url' de cada evento (passo extra)
            "detail": None,
            "start_date": None,  # Datas precisariam de tratamento a partir do campo 'days'
            "end_date": None,
            "private_event": 0,
            "published": 1,
            "cancelled": 0,
            "image": image,
            "url": link,
            "address": venue,  # Simplificado para string, conforme modelo do FastAPI
            "host": None,
            "category_prim": category,
            "category_sec": None,
            # "organizer_id" deve ser preenchido na rota da API com o ID do admin logado
            "created_at": datetime.utcnow(),
            "raw_days": days  # Campo extra para processar as datas posteriormente
        }

        events.append(event_doc)
        print(events)

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
