# Zasol Analog — Telegram Bot

Легальный аналог @Zasol_Bot: reverse phone lookup + credit score tracker.

## Стек
- Python 3.11+
- aiogram 3.x
- PostgreSQL (Railway)
- Redis (Railway, optional)
- aiohttp + BeautifulSoup (скрепинг fallback)
- Whitepages Pro API (рекомендуется для продакшена)

## Структура
```
zasol-analog/
├── bot/
│   ├── config.py         # Конфиг
│   ├── main.py           # Точка входа
│   ├── handlers/         # Хендлеры
│   ├── keyboards/        # Inline кнопки
│   ├── services/         # API клиенты + скрепинг
│   ├── models/           # SQLAlchemy модели
│   └── utils/            # Хелперы
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

## Деплой на Railway
1. Fork на GitHub
2. Railway → New Project → Deploy from GitHub
3. Добавь Variables (см. .env.example)
4. Добавь PostgreSQL плагин в Railway
5. Готово

## Env переменные
```bash
BOT_TOKEN=your_telegram_bot_token
ADMIN_IDS=123456789,987654321
DATABASE_URL=postgresql://...  # Railway выдаст автоматически
WHITEPAGES_API_KEY=optional    # Платный API для reverse phone
NUMVERIFY_API_KEY=optional     # Бесплатный базовый lookup
USE_SCRAPING=true              # Fallback скрепинг
REDIS_URL=optional             # Railway Redis
```

## Команды бота
- `/start` — главное меню
- `/phone` — reverse phone lookup
- `/batch` — batch phone lookup
- `/credit` — credit score модуль
- `/profile` — профиль пользователя
- `/admin` — админ-панель
