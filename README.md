# DoubleKiss Billiards Bot

Telegram бот для бильярдной DoubleKiss с функциями записи на занятия и управления расписанием.

## Запуск через Docker

### Быстрый старт

1. Убедитесь, что Docker и Docker Compose установлены
2. Настройте `.env` файл с вашими данными
3. Запустите бота:

```bash
docker-compose up -d
```

### Команды Docker

Запуск бота:
```bash
docker-compose up -d
```

Остановка бота:
```bash
docker-compose down
```

Просмотр логов:
```bash
docker-compose logs -f
```

Перезапуск бота:
```bash
docker-compose restart
```

Пересборка после изменений:
```bash
docker-compose up -d --build
```

## Запуск без Docker

Установка зависимостей:
```bash
pip install -r requirements.txt
```

Запуск бота:
```bash
python bot.py
```

## Настройка

Создайте файл `.env` со следующими параметрами:

```
BOT_TOKEN=your_bot_token_here
ADMIN_ID=your_telegram_id
```

## Функции

- Регистрация пользователей
- Запись на занятия
- Просмотр своих записей
- Админ-панель для управления занятиями
- Рассылка сообщений пользователям
- Управление пользователями
