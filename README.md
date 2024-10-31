<h1>Атом чат с использованием FastAPI</h1>
Этот проект представляет собой API атом чата в реальном времени, который позволяет пользователям общаться в приватных каналах.
<h2>Основные функции</h2>
<ol>
  <li><b>Управление пользователями:</b> Пользователи могут регистрироваться, входить в систему и смотреть информацию о своем аккаунте в профиле. Доступные роли: moderator, user. Так же модератор может заблокировать выбранного пользователя.</li>
  <li><b>Управление каналами:</b> Авторизированные пользователи могут создавать каналы, просматривать какие каналы существуют в атом чате и так же посмотреть детальную информацию об определенном канале. Участники канала могут смотреть в каких каналах они состоят, а модераторы и владельцы каналов могут изменять информацию о канале и удалить его.</li>
  <li><b>Управление заявками:</b> Авторизированные пользователи могут отправить заявку на вступление в нужный им канал и посмотреть детальную информацию о заявке. Модераторы и владельцы каналов могут посмотреть входящие заявки канала, которые находятся в ожидании, а так же принимать их, либо отклонять(accept или decline).</li>
  <li><b>Управление членством в канале:</b> Модераторы или владельцы каналов могут добавлять пользователей в канал и удалять их.</li>
  <li><b>Управление сообщениями:</b> Участники канала и модератор могут общаться в каналах в реальном времени, а так же просматривать историю сообщений.</li>
</ol>
<h3>Чат в реальном времени</h3>
Протестировать чат в реальном времени можно с помощью Postman. Для этого в параметрах пути необходимо указать ID канала, а в заголовке авторизации — токен нужного пользователя.
<img src="https://github.com/morozov831/fastapi_atomchat/blob/master/image.png">
<h2>Используемые технологии</h2>
<ol>
  <li><b>FastAPI</b>: Современный, быстрый веб-фреймворк для разработки API на Python 3.7+, основанный на стандартных подсказках типов Python.</li>
  <li><b>WebSocket Chat</b>: Функция чата в реальном времени с использованием WebSockets для мгновенного обновления сообщений.</li>
  <li><b>PostgreSQL</b>: Мощная, открытая и свободная система управления реляционными базами данных.</li>
  <li><b>JWT-аутентификация</b>: Реализация аутентификации на основе JSON Web Tokens для безопасной аутентификации пользователей.</li>
  <li><b>Pydantic</b>: Библиотека для валидации данных и управления настройками в Python, часто используемая вместе с FastAPI.</li>
  <li><b>Uvicorn</b>: Легковесный ASGI-сервер, используемый для запуска приложений FastAPI.</li>
  <li><b>Gunicorn</b>: Высокопроизводительный WSGI-сервер, используемый для связи с Uvicorn.</li>
  <li><b>UnitTests</b></li>
  <li><b>Docker и Docker Compose</b>: Технологии для создания и управления контейнерами, используемые для упаковки и развертывания всего проекта.</li>
</ol>
<h2>База данных</h2>
<h3>Таблицы:</h3>
<ol>
  <li><b>Пользователи (users)</b>: Содержит информацию о пользователях системы, включая их идентификаторы, юзернеймы, пароли, роли(по умолчанию user) и статусы активности.</li>
  <li><b>Каналы (channels)</b>: Содержит информацию о каналах, включая название, слаг, описание, статус активности, количество участников.</li>
  <li><b>Заявки (channel_join_requests)</b>: Содержит информацию о заявках отправленных пользователями, включая ID канала и пользователя, статус заявки(pending, accepted, rejected), дату создания.</li>
  <li><b>Участники канала (channel_members)</b>: Содержит информацию об участниках каналов.</li>
  <li><b>Сообщения (messages)</b>: Содержит информацию о сообщениях отправленных пользователями.</li>
</ol>
<h2>Установка и запуск</h2>
<h3>Установка:</h3>

1. Склонируйте репозиторий проекта из GitHub:
   ```bash
   git clone https://github.com/morozov831/fastapi_ecommerce.git
   ```

2. Перейдите в каталог проекта:
   ```bash
   cd fastapi_ecommerce
   ```
3. Создайте и активируйте виртуальное окружение:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Установите необходимые пакеты:
   ```bash
   pip install -r requirements.txt
   ```
4. Переименуйте файл `.env.example` в `.env`:
   ```bash
   mv .env.example .env
   ```
5. Для настройки вашего приложения откройте файл `.env` в текстовом редакторе и
   заполните
   соответствующие значения для каждой переменной в зависимости от вашей среды.
   Обязательно
   предоставьте cекретный ключ, используемый для аутентификации
  JWT (JSON Web Token).
   После настройки эти переменные будут
   загружены в
   окружение вашего приложения во время его выполнения.
   <p>Вы можете установить свой собственный или сгенерировать случайный секретный ключ на сайте https://www.grc.com/passwords.htm</p>
<h4>Настройки базы данных:</h4>
  - <b>POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD:</b> Конфигурация для
    базы данных PostgreSQL (должна совпадать с DB_NAME, DB_USER и
    DB_PASSWORD соответственно).
<h3>Запуск:</h3>
1. Убедитесь, что Docker и Docker Compose установлены на вашей системе.

2. Запустите следующую команду для сборки образов, создадия и запуска контейнеров:
   ```bash
   docker compose -f docker-compose.prod.yml up -d --build
   ```
2. После запуска контейнеров примените миграции:
   ```bash
   docker compose -f docker-compose.prod.yml exec web alembic upgrade head
   ```

3. Далее перейдите к документации Swagger
   по адресу http://127.0.0.1/docs, чтобы
   взаимодействовать с
   API.

Для остановки проекта:

1. Нажмите `Ctrl + C` в терминале, чтобы остановить запущенные контейнеры
   Docker.

2. Запустите следующую команду, чтобы остановить контейнеры Docker и удалить их:
   ```bash
   docker compose -f docker-compose.prod.yml down -v
   ```
<h2>Лицензия</h2>
Данный проект лицензирован по <a href="https://github.com/morozov831/fastapi_ecommerce/blob/master/MIT-LICENSE.txt">MIT license</a>.
<h2>Обратная связь</h2>

Если у вас есть какие-либо отзывы, вопросы или предложения относительно этого
проекта, пишите мне в <a href="https://t.me/morozov_831">Telegram</a>. Буду рад помочь Вам!
