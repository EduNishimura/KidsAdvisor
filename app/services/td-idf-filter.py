# arquivo: gerar_tfidf.py
import joblib
import nltk
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
from pymongo import MongoClient
from bs4 import BeautifulSoup
import string
from database import db

# Stopwords em português para filtros de texto
stopwords_pt = {
    "a", "ao", "aos", "aquela", "aquelas", "aquele", "aqueles", "aquilo", "as", "até", "com", "como", "da", "das", "do", "dos", "e", "ela", "elas", "ele", "eles", "em", "entre", "era", "eram", "essa", "essas", "esse", "esses", "esta", "estamos", "estas", "estava", "estavam", "este", "esteja", "estejam", "estejamos", "estes", "esteve", "estive", "estivemos", "estiver", "estivera", "estiveram", "estiverem", "estivermos", "estivesse", "estivessem", "estivéramos", "estivéssemos", "estou", "está", "estão", "eu", "foi", "fomos", "for", "fora", "foram", "forem", "formos", "fosse", "fossem", "fui", "fôramos", "fôssemos", "haja", "hajam", "hajamos", "havemos", "havia", "hei", "houve", "houvemos", "houver", "houvera", "houveram", "houverei", "houverem", "houveremos", "houveria", "houveriam", "houveríamos", "houverão", "houverá", "houveríamos", "houvesse", "houvessem", "houvéramos", "houvéssemos", "há", "hão", "isso", "isto", "já", "lhe", "lhes", "mais", "mas", "me", "mesmo", "meu", "meus", "minha", "minhas", "muito", "na", "nas", "nem", "no", "nos", "nossa", "nossas", "nosso", "nossos", "num", "numa", "não", "nós", "o", "os", "ou", "para", "pela", "pelas", "pelo", "pelos", "por", "qual", "quando", "que", "quem", "se", "seja", "sejam", "sejamos", "sem", "ser", "será", "serão", "seria", "seriam", "será", "serão", "seria", "seriam", "seu", "seus", "só", "sua", "suas", "são", "só", "também", "te", "tem", "temos", "tenha", "tenham", "tenhamos", "tenho", "ter", "terá", "terão", "teria", "teriam", "teve", "tinha", "tinham", "tive", "tivemos", "tiver", "tivera", "tiveram", "tiverem", "tivermos", "tivesse", "tivessem", "tivéramos", "tivéssemos", "tu", "tua", "tuas", "tém", "tínhamos", "um", "uma", "você", "vocês", "vos", "à", "às", "éramos", "é", "são", "está", "estão", "foi", "foram", "será", "serão", "seria", "seriam", "estava", "estavam", "estivera", "estiveram", "esteja", "estejam", "estivesse", "estivessem", "estiver", "estiverem", "hei", "há", "houve", "houverá", "houveria", "houveriam", "houver", "houverem", "houvera", "houveram", "haja", "hajam", "houvesse", "houvessem", "houvéramos", "houvéssemos", "tenho", "tem", "temos", "tém", "tinha", "tinham", "tínhamos", "tive", "tivemos", "teve", "terá", "terão", "teria", "teriam", "ter", "terem", "tera", "teram", "tenha", "tenham", "tenhamos", "tivesse", "tivessem", "tivéramos", "tivéssemos", "tiver", "tiverem", "tivera", "tiveram", "sou", "somos", "era", "éramos", "fui", "fomos", "será", "serão", "seria", "seriam", "seja", "sejam", "sejamos", "fosse", "fossem", "fôramos", "fôssemos", "for", "forem", "formos", "fora", "foram", "sou", "somos", "era", "éramos", "fui", "fomos", "será", "serão", "seria", "seriam", "seja", "sejam", "sejamos", "fosse", "fossem", "fôramos", "fôssemos", "for", "forem", "formos", "fora", "foram"
}

def clean_text(text):
    # Sua função de limpeza (pode reusar a do meu exemplo anterior)
    # Tira HTML (importante para o campo 'detail'!), pontuação, stopwords.
    text = BeautifulSoup(text, "html.parser").get_text()
    text = text.lower()
    text = ''.join([char for char in text if char not in string.punctuation])
    tokens = [word for word in text.split() if word not in stopwords_pt]
    return ' '.join(tokens)

def build_and_save_tfidf():
    print("Buscando todos os eventos...")
    # Usei o find síncrono aqui, já que é um script de background
    # Se quiser usar async, terá que rodar com asyncio.run()
    events = list(db.events.find({"published": 1}))
    
    corpus = []
    event_id_map = {} # Mapeia índice (0, 1, 2...) para ObjectId

    print(f"Processando {len(events)} eventos...")
    for i, e in enumerate(events):
        event_id_map[i] = str(e["_id"])
        
        # --- Lógica exata do seu endpoint ---
        text_parts = []
        text_parts.extend(e.get("tags", []))
        if e.get("community_tags_count"):
            text_parts.extend(list(e["community_tags_count"].keys()))
        if e.get("category_prim"):
            text_parts.append(e["category_prim"].get("name", ""))
        if e.get("category_sec"):
            text_parts.append(e["category_sec"].get("name", ""))
        
        # Limpar o HTML do 'detail' é crucial!
        if e.get("detail"):
            text_parts.append(clean_text(e["detail"]))
        else:
            text_parts.append(e.get("name", "")) # Adiciona o nome se não houver detail

        text = " ".join(text_parts)
        corpus.append(text)
        # --- Fim da lógica ---

    print("Treinando o TF-IDF Vectorizer...")
    # NOTA: Remova a limpeza de stopwords daqui, pois já fizemos manualmente
    vectorizer = TfidfVectorizer() 
    
    # 1. Treina o TF-IDF com o corpus dos eventos
    tfidf_matrix = vectorizer.fit_transform(corpus)
    
    print("Salvando artefatos...")
    # 2. Salva os artefatos
    joblib.dump(vectorizer, 'tfidf_vectorizer.pkl')
    joblib.dump(tfidf_matrix, 'tfidf_matrix.pkl')
    joblib.dump(event_id_map, 'event_id_map.pkl')
    
    print("Processo concluído.")

if __name__ == "__main__":
    build_and_save_tfidf()