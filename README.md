AI Entity Analyst
Українська версія
Привіт! Це проєкт для розпізнавання сутностей (людей, організацій) у тексті та пошуку відповідей за допомогою RAG-архітектури. Усередині все зв'язано через FastMCP як шар інструментів, а користуватися системою можна або через Telegram-бота, або через веб-інтерфейс.

Що тут є і як це працює
Виділення сутностей (NER): Система шукає в тексті персон (PER), організації (ORG) та локації (LOC) для української та англійської мов на базі моделей BERT.

Пошук контексту (RAG): Використовує FAISS та LangChain для швидкого пошуку по векторній базі знань.

Веб-інтерфейс: Лаконічний чат на React із темною темою для швидкої роботи прямо з браузера.

Telegram-бот: Бот, який підключений до того самого MCP-сервера і відповідає на промпти в месенджері.

Технології
Бекенд: Python, FastMCP, LangChain, FAISS, Transformers (BERT), python-telegram-bot.

Фронтенд: React, Vite, Tailwind CSS, Lucide React.

Інфраструктура: Docker, Docker Compose.

Як запустити проєкт
Скопіюйте проєкт та створіть файл .env у кореневій папці зі своїми ключами:

Plaintext
TELEGRAM_BOT_TOKEN=ваш_токен_телеграм
OPENAI_API_KEY=ваш_ключ_openai
Запустіть бекенд та бота через Docker Compose:

Bash
docker compose up -d --build
Запустіть веб-інтерфейс:

Bash
cd react_project/frontend
npm install
npm run dev

English Version
Hey! This project is built for extracting named entities (people, organizations) from raw text and answering context-aware queries using a RAG pipeline. Everything is hooked up through FastMCP as a middleware tool layer, and you can interact with it either via a Telegram bot or a clean React web interface.

What it does
Named Entity Recognition (NER): Extracts PER, ORG, and LOC entities from Ukrainian and English text using BERT-based models.

Context Retrieval (RAG): Uses FAISS and LangChain to store vectors and retrieve relevant knowledge fast.

Web Dashboard: A dark-themed React chat interface for testing and analyzing texts in the browser.

Telegram Integration: A bot linked to the same MCP tool layer for quick access on mobile or desktop.

Tech Stack
Backend: Python, FastMCP, LangChain, FAISS, Transformers (BERT), python-telegram-bot.

Frontend: React, Vite, Tailwind CSS, Lucide React.

Infrastructure: Docker, Docker Compose.

How to Run
Clone the repository and place your API keys in a .env file in the root directory:

Plaintext
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
Start the backend services and Telegram bot with Docker:

Bash
docker compose up -d --build
Launch the frontend development server:

Bash
cd react_project/frontend
npm install
npm run dev