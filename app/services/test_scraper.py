from scraper_clubinho import scrape_all

if __name__ == "__main__":
    events = scrape_all()
    print(f"Total coletados: {len(events)}")
    for ev in events[:5]:
        print(ev)
