<h1>Атом чат на FastAPI</h1>
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
  <li><b>Unit-тесты</b> Автоматизированные проверки, которые позволяют убедиться в правильной работоспособности программы.</li>
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
   git clone https://github.com/morozov831/fastapi_atomchat.git
   ```

2. Перейдите в каталог проекта:
   ```bash
   cd fastapi_atomchat
   ```
3. Создайте и активируйте виртуальное окружение, если оно не создано автоматически интерпретатором:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Установите необходимые пакеты:
   ```bash
   pip install -r requirements.txt
   ```

<h3>Запуск приложения:</h3>
<ol>
    <li>Убедитесь, что Docker и Docker Compose установлены на вашей системе.</li>
    <li>Запустите следующую команду для сборки образов, создания и запуска контейнеров:
        <pre><code>docker compose -f docker-compose.yaml up -d --build</code></pre>
    </li>
    <li>После запуска контейнеров автоматически выполняются миграции и скрипт для создания тестовых данных <code>seed.py</code>. Этот процесс включает в себя следующее:</li>
</ol>
Созданные пользователи:
<ul>
    <li>Модератор: moderator (ID: 1)</li>
    <li>Создатель канала для программистов: programmer_creator (ID: 2)</li>
    <li>Создатель канала для дизайнеров: designer_creator (ID: 3)</li>
    <li>Пользователь, который вступил в канал для программистов: user_program (ID: 4)</li>
    <li>Пользователь, который вступил в канал для дизайнеров: user_design (ID: 5)</li>
    <li>Пользователь: user1 (ID: 6)</li>
    <li>Пользователь: user2 (ID: 7)</li>
</ul>
Созданные каналы:
<ul>
    <li>Канал для программистов: Программисты (ID: 1)</li>
    <li>Канал для дизайнеров: Дизайнеры (ID: 2)</li>
</ul>
Заявка на присоединение:
<ul>
    <li>ID заявки: 1</li>
    <li>Пользователь: user1</li>
    <li>Канал: Программисты</li>
    <li>Статус заявки: pending (ожидание обработки)</li>
</ul>

<h4>Переход к документации Swagger:</h4>
<p>Для взаимодействия с API перейдите по следующему адресу: 
    <a href="http://localhost:8000/docs">http://localhost:8000/docs</a>
</p>

<h3>Остановка проекта:</h3>
<p>Чтобы остановить контейнеры Docker и удалить их, запустите следующую команду:</p>
<pre><code>docker compose -f docker-compose.yaml down -v</code></pre>

<h3>Запуск тестов:</h3>
<ol>
    <li>Запустите следующую команду для сборки образов, создания и запуска контейнеров:
        <pre><code>docker compose -f docker-compose.tests.yaml up --build</code></pre>
    </li>
</ol>
<h3>Описание тестов:</h3>
<ul>
    <li>Проверка успешной регистрации нового пользователя.</li>
    <li>Проверка уникальности имени пользователя при регистрации.</li>
    <li>Проверка возможности входа в систему с корректными учетными данными.</li>
    <li>Проверка возможности блокировки пользователя модератором.</li>
    <li>Проверка, что обычные пользователи не могут блокировать других пользователей.</li>
    <li>Проверка успешного обновления канала владельцем.</li>
    <li>Проверка обработки случая, когда канал для обновления не найден.</li>
    <li>Проверка успешного удаления канала владельцем.</li>
    <li>Проверка, что нельзя повторно отправить запрос на присоединение к каналу с уже существующей заявкой.</li>
    <li>Проверка получения списка ожидающих запросов на присоединение к каналу.</li>
    <li>Проверка успешного добавления пользователя в канал.</li>
    <li>Проверка успешного удаления пользователя из канала.</li>
    <li>Проверка, что нельзя добавить пользователя, который уже является членом канала.</li>
</ul>
<h3>Для остановки тестов:</h3>
<ol>
    <li>Нажмите <strong>Ctrl + C</strong> в терминале, чтобы остановить запущенные контейнеры Docker.</li>
    <li>Запустите следующую команду, чтобы остановить контейнеры Docker и удалить их:
        <pre><code>docker compose -f docker-compose.tests.yaml down -v</code></pre>
    </li>
</ol>
<h2>Лицензия</h2>
Данный проект лицензирован по <a href="https://github.com/morozov831/fastapi_atomchat/blob/master/LICENSE">MIT license</a>.
<h2>Обратная связь</h2>

Если у вас есть какие-либо отзывы, вопросы или предложения относительно этого
проекта, пишите мне в <a href="https://t.me/morozov_831">Telegram</a>. 
