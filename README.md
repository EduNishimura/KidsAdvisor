# 🎮 KidsAdvisor API

API do **KidsAdvisor**, um aplicativo gamificado para recomendação de atividades infantis.  
Construído em **FastAPI + MongoDB + JWT Auth**, com motor de recomendação baseado em **TF-IDF + Similaridade do Cosseno**.

---

## 🚀 Stack
- [FastAPI](https://fastapi.tiangolo.com/) – API web
- [MongoDB Atlas](https://www.mongodb.com/) – banco de dados não relacional
- [scikit-learn](https://scikit-learn.org/) – motor de recomendação (TF-IDF + cosine)
- [Python-Jose](https://python-jose.readthedocs.io/) – JWT
- [Passlib](https://passlib.readthedocs.io/) – hash de senhas

---

## 📂 Estrutura

app/
core/ # Config, DB e segurança
models/ # Schemas (Pydantic)
routes/ # Endpoints (users, activities, auth, feedback, recommend)
services/ # Recomendador
main.py # Ponto de entrada FastAPI

---

## 🔑 Autenticação e Roles
- `user` → cria perfis de filhos, recebe recomendações, envia feedback
- `admin` → cria e gerencia atividades

Login retorna um **JWT** que deve ser enviado em cada request protegido:

---

## 🛠️ Como rodar localmente

1. Clone o repo:
```bash
git clone https://github.com/seuusuario/kidsadvisor-api.git
cd kidsadvisor-api

