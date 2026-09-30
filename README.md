# UniRoute Russia

Персональный навигатор поступления в российские университеты для иностранных абитуриентов. Сейчас приложение работает как FastAPI API и бот MAX: собирает профиль, подбирает программы, показывает источники, сравнивает варианты и создаёт личный маршрут с чек-листом документов и напоминаниями.

## Локальный запуск

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
uvicorn app.main:app --reload
```

Swagger доступен по адресу <http://localhost:8000/docs>. Для локальной разработки задайте параметры в `.env`; не публикуйте этот файл и не добавляйте реальные токены в репозиторий. Для тестирования MAX без токена исходящие сообщения выводятся в лог.

Для разработки и запуска проверок установите `requirements-dev.txt`. Инструкции по проверкам перед публикацией находятся в [SECURITY.md](SECURITY.md).

В `docker-compose.yml` настроена локальная связка приложения и PostgreSQL. Порты приложения и БД доступны только с локального компьютера. Перед запуском через Docker замените локальный пароль БД на случайный. Приложение применяет миграции добавленных полей при старте и заполняет каталог.

Локальную связку можно запустить командой `docker compose up --build`; файл `.env` при таком запуске необязателен. Для работы с реальным ботом MAX задайте его токен и параметры webhook в локальном `.env`.

## Возможности

- Онбординг на русском, английском, французском и испанском с возрастом, образованием, годом выпуска, языками, бюджетом, направлением и интересом к квоте.
- Подбор с фильтрами по уровню, языку, направлению, бюджету и общежитию; если на выбранном языке нет вариантов, бот объясняет причину и предлагает сменить язык только по согласию пользователя.
- Поиск направления простым текстом, карточки программ со ссылками и сравнением до трёх вариантов.
- Профильные маршруты поступления, статусы документов, отметки шагов и ежедневные напоминания при наличии подтверждённого срока.
- Ответы на вопросы по каталогу с источниками. Внешняя LLM подключается опционально; без неё бот сообщает, когда не может подтвердить ответ.
- REST API для вузов, программ, профиля, рекомендаций, сравнения, маршрутов и вопросов.

## Каталог и достоверность

Каталог содержит 30 вузов, из них 7 с 29 программами, подготовленными для рекомендаций; остальные записи обзорные. Программы охватывают МФТИ, ВШЭ, МАИ, Сеченовский университет, МГУ, НИЯУ МИФИ и МТУСИ. При запуске каталог сверяет уровни вузов и не понижает университет с программами до обзорной записи.

Данные программ привязаны к официальным страницам вузов. Подтверждённые цены предыдущего цикла показываются только как историческая справка. В каталоге пока нет подтверждённых дедлайнов на цикл 2027/28, поэтому напоминания о сроках для этого цикла не отправляются. Они появятся только после добавления подтверждённых дат и источников. Для МИФИ официальная страница бакалавриата подтверждает направление «Информационная безопасность» и русский язык обучения; набор 2027/28 и его условия пока не подтверждены. Общежитие считается подтверждённым только при наличии явного источника. Проверьте актуальность каждой страницы перед подачей.

Маршрут и статусы документов — личный план абитуриента. Приложение не загружает документы, не проверяет их юридическую корректность и не отправляет заявку в вуз. Это остаётся за официальными кабинетами и приёмными комиссиями.

## Настройки

Скопируйте `.env.example` в локальный `.env` и задайте в нём нужные параметры. Шаблон не содержит действующих секретов. Основные параметры:

- `DATABASE_URL` — PostgreSQL для развёртывания или SQLite для локальной разработки.
- `MAX_BOT_TOKEN`, `MAX_WEBHOOK_SECRET`, `WEBHOOK_PUBLIC_URL` — интеграция с MAX.
- `API_KEY` — ключ для служебного API в production; он не предназначен для пользовательского клиента. Production-режим не запустится без PostgreSQL, HTTPS webhook и обязательных секретов.
- `DATA_CONTROLLER_NAME`, `PRIVACY_CONTACT` — реальное имя оператора персональных данных и рабочий контакт; обязательны в production, примерные значения из `.env.example` нужно заменить.
- `LLM_API_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL` — необязательная OpenAI-совместимая модель для ответов по каталогу.
- `REMINDER_DAYS` — дни до дедлайна, когда отправляются напоминания (по умолчанию 30, 7 и 1).

Для MAX создайте бота, задайте токен, настройте публичный HTTPS webhook и вызовите `POST /max/subscribe`. Long Polling (`py -m app.max_poll`) предназначен для локальной разработки; MAX не позволяет одновременно использовать его и webhook. В production используйте webhook.

## Перед публикацией

Production-развёртывание уже настроено на сервере через GitHub Actions, Docker и HTTPS reverse proxy. Для обновления production укажите фактические `DATA_CONTROLLER_NAME` и `PRIVACY_CONTACT` в серверном `.env`; запуск намеренно остановится, если поля пусты или содержат шаблон. Отдельно задайте `REVIEWER_API_KEY`, если жюри будет проверять read-only API. Не помещайте эти значения в репозиторий, презентацию или публичные логи. Резервное копирование PostgreSQL и юридическая проверка политики обработки данных остаются обязательными перед широким публичным запуском.

Логотип: [assets/uniroute-russia-logo.png](assets/uniroute-russia-logo.png).

## Основной сценарий для проверки

1. Откройте бота в MAX и отправьте `/start`. Выберите язык интерфейса.
2. Заполните профиль: страна, возраст, образование, направление, язык обучения, год поступления, бюджет и потребность в общежитии.
3. Откройте предложенную программу и проверьте ссылку на источник, требования, список документов и статус цены и дедлайна.
4. Нажмите «Хочу поступать», откройте маршрут, отметьте документ готовым и подтвердите выполненный шаг.
5. Через меню можно вернуться к рекомендациям и разделу «Мои поступления». Команда `/reset` позволяет повторить сценарий.

Перед созданием профиля бот показывает уведомление на русском, английском, французском и испанском и просит добровольное согласие. Команда `/privacy` открывает уведомление, `/delete_data` удаляет профиль, маршруты, статусы документов, журналы напоминаний и связанные технические записи. Неактивные профили удаляются автоматически после 365 дней. Это техническая реализация выбранного срока хранения, а не заключение о юридическом соответствии: перед публичным запуском укажите фактического оператора/контакт и проверьте правовые обязанности.

Проверять работу бота следует в MAX. Локальный режим без токена выводит ответы в консоль и пригоден только для разработки.

## Состав решения

`app/main.py` содержит FastAPI, webhook MAX и пользовательский сценарий. `app/max_client.py` отправляет сообщения, `app/services.py` подбирает программы и создаёт маршруты, `app/seed.py` наполняет каталог, `app/models.py` описывает данные, `app/reminders.py` отвечает за напоминания, `app/qa.py` — за ответы по каталогу. SQLAlchemy работает с SQLite локально и PostgreSQL в Docker. Внешние сервисы: API MAX и, при настройке, совместимая LLM.

Данные каталога добавлены из опубликованных страниц университетов; в карточках сохранены ссылки на источники и даты проверки. Для будущего набора неизвестные условия не подставляются из прошлых лет. Контрольная проверка данных проводится по официальным страницам вузов.

## Воспроизведение и проверки

Для запуска через Docker создайте локальный `.env` с параметрами MAX, если нужен реальный бот, затем выполните:

```powershell
docker compose up --build
```

Проверка API локально: <http://localhost:8000/health> и <http://localhost:8000/docs>. В режиме `development` бот без токена работает в режиме имитации. Для остановки используйте `docker compose down`; данные PostgreSQL остаются в томе `postgres_data`.

### Сетевые порты

| Сервис | Порт | Доступ |
| --- | ---: | --- |
| Caddy HTTPS/HTTP на production-хосте | 443 / 80 | публичный вход; HTTP перенаправляется на HTTPS |
| FastAPI в Docker | 8000/tcp | привязан к `127.0.0.1`, доступен через Caddy и локально на сервере |
| PostgreSQL в Docker | 5432/tcp | привязан к `127.0.0.1`, не опубликован в интернет |
| MAX API и настроенная LLM | исходящие HTTPS/443 | исходящие соединения приложения |

Проверки API для жюри: [OpenAPI 3.1 JSON](openapi.json), [DATA-API.yaml](DATA-API.yaml), [синтетические тестовые данные](data/api-test-data.json). `/health` доступен без ключа. Для GET-запросов каталога можно настроить отдельный `REVIEWER_API_KEY` (read-only); остальные служебные маршруты требуют `X-API-Key`, а MAX webhook — `X-Max-Bot-Api-Secret`. Передавайте ключ жюри только по закрытому каналу, не включайте его в слайд или репозиторий. Swagger в production остаётся закрытым; спецификация приложена отдельно.

```powershell
pip install -r requirements-dev.txt
py -m pytest -q
py -m pip_audit -r requirements-dev.txt --progress-spinner off
py -m bandit -r app -lll -q
```

Автоматические проверки также настроены в GitHub Actions. Для настоящей доставки событий нужен постоянно доступный HTTPS webhook; его URL передаётся в `WEBHOOK_PUBLIC_URL`, после чего вызывается `POST /max/subscribe` с ключом `X-API-Key` в production. Локальный Long Polling пригоден для отладки, но не для публичной демонстрации с выключенным компьютером.

## GitHub auto-deploy

After the CI checks pass, pushes to `main` deploy through a restricted SSH account. The account accepts only a source archive and runs the deployment script. The server `.env` and PostgreSQL volume remain outside the uploaded archive.

In repository **Settings > Secrets and variables > Actions**, add these secrets:

- `DEPLOY_HOST` - the server IP or hostname.
- `DEPLOY_SSH_PRIVATE_KEY` - the private key at `%USERPROFILE%\.ssh\uniroute_github_deploy`.

The server public host key is pinned in `.github/deploy_known_hosts`. To copy the private key for the GitHub secret field, run `Get-Content "$env:USERPROFILE\.ssh\uniroute_github_deploy" -Raw | Set-Clipboard` in PowerShell. Never commit the private key. Run **Actions > Tests and security > Run workflow** on `main` to deploy immediately, or push a commit to `main`.


## Official university catalogue monitoring

The programme catalogue is manually curated and links to university sources. A weekly GitHub Actions workflow parses the official MTUCI and MEPhI programme pages and checks all 16 unique programme/admissions source URLs currently referenced by the seven detailed universities. It creates a downloadable JSON report with page titles, relevant text snippets, source fingerprints and fetch failures so moderators can review changes. The workflow is read-only: it never changes the application database or publishes programmes to users. It does not fully import or certify new catalogue facts. A person must confirm language for international applicants, degree, admission conditions, and cycle before adding a programme. Unknown prices and dates remain unconfirmed. Run it from Actions > Official catalogue monitor > Run workflow.

```powershell
python -m scripts.monitor_official_catalog
```

The application route shows university-specific submission, contract, and in-person contact instructions, and can export them in a UTF-8 text checklist. Guidance is localized into Russian, English, French, and Spanish. The checklist includes step/document statuses, applicant notes, and official source links. It is a personal preparation file, not an official form or submitted application. Uploaded scans and other sensitive files are not included. Intake dates and contract terms can change, so users are directed to confirm the current cycle with the university.

To moderate a catalogue discovery, open the latest **Official catalogue monitor** workflow run, download the `official-catalog-review` artifact, and verify each candidate on its linked official pages. Update `app/seed.py` only after confirming the programme, language, admission conditions and cycle; the workflow never publishes candidate data directly.
