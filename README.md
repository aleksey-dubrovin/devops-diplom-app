
# Тестовое приложение дипломного проекта и CI/CD для его сборки и деплоя.

Репозиторий содержит статический сайт на nginx, Dockerfile, workflows
GitHub Actions и пояснительную записку к дипломной работе.

## Связанные репозитории

- [devops-diplom-infra](https://github.com/aleksey-dubrovin/devops-diplom-infra) — инфраструктура (Terraform)
- [devops-diplom-k8s](https://github.com/aleksey-dubrovin/devops-diplom-k8s) — Kubernetes манифесты и Helm

## Работающие сервисы

- Приложение: [https://app.dubrovins.ru](https://app.dubrovins.ru)
- Пояснительная записка: [https://app.dubrovins.ru/docs.html](https://app.dubrovins.ru/docs.html)
- Grafana: [https://monitoring.dubrovins.ru](https://monitoring.dubrovins.ru)

## Структура

```
devops-diplom-app/
├── app/
│   ├── Dockerfile              # nginx:alpine + index.html
│   ├── index.html              # главная страница
│   ├── docs.html               # страница рендера документации
│   └── docs/                   # пояснительная записка в markdown
│       ├── README.md
│       ├── 01-intro.md
│       ├── ...
│       └── images/             # скриншоты
├── .github/workflows/
│   ├── build.yml               # сборка образа при push в main
│   └── release.yml             # сборка + деплой при создании тега
└── README.md
```

## Приложение

Статический сайт на `nginx:alpine` с минимальным Dockerfile:

```dockerfile
FROM nginx:alpine

COPY index.html /usr/share/nginx/html/index.html
COPY docs.html /usr/share/nginx/html/docs.html
COPY docs/ /usr/share/nginx/html/docs/

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1
```

Кроме главной страницы, в образ включена пояснительная записка —
markdown-файлы рендерятся в браузере через `marked.js` и
`highlight.js` на странице `/docs.html`.

## Локальная сборка

```bash
cd app
docker build -t diplom-app:local .
docker run --rm -p 8080:80 diplom-app:local
```

Откройте:

- [http://localhost:8080](http://localhost:8080) — главная.
- [http://localhost:8080/docs.html](http://localhost:8080/docs.html) — документация.

## CI/CD

### build.yml

Триггер: push в main.

1. Собирает Docker-образ.
2. Пушит в Yandex Container Registry с тегами `latest` и `sha-<commit>`.
3. Кэширует слои для ускорения последующих сборок.

**Особенность:** параметры `provenance: false` и `sbom: false`
обязательны для совместимости с Yandex Registry. Без них buildx
добавляет attestation-манифесты, которые Yandex Registry не читает.

### release.yml

Триггер: создание тега `v*`.

1. Собирает образ с тегом версии (например, `v1.0.0`) и `latest`.
2. Пушит в реестр.
3. Отправляет `repository_dispatch` в `devops-diplom-k8s`
   с указанием версии.

Это запускает автоматический деплой приложения в кластер.

## GitHub Secrets

Для работы workflow нужны:

| Secret | Назначение |
|--------|-----------|
| `YC_SERVICE_ACCOUNT_KEY_B64` | JSON-ключ сервисного аккаунта в base64 |
| `REGISTRY_URL` | `cr.yandex/crph52se6qjtjg937i7h` |
| `K8S_REPO_PAT` | PAT для отправки события в k8s-репозиторий |

## Сквозной сценарий

1. Коммит в feature-ветку, PR, ревью, мерж в main.
2. Автоматически запускается `build.yml` — образ в реестре.
3. Создание тега:

```bash
git checkout main
git pull
git tag -a v0.2.0 -m "Описание изменений"
git push origin v0.2.0
```

4. Запускается `release.yml` — образ с тегом и триггер деплоя.
5. В `devops-diplom-k8s` запускается `deploy.yml` — обновление
   Deployment в кластере.
6. Через 5 минут обновлённое приложение доступно по адресу
   `https://app.dubrovins.ru`.

## Документация

Пояснительная записка доступна в двух форматах:

- **Markdown:** файлы в `app/docs/`.
- **HTML:** страница `https://app.dubrovins.ru/docs.html`.

Структура записки:

| Файл | Содержание |
|------|-----------|
| `01-intro.md` | Введение, цели, задачи |
| `02-infrastructure.md` | Инфраструктура Terraform |
| `03-kubernetes.md` | Kubernetes кластер |
| `04-application.md` | Приложение и Dockerfile |
| `05-monitoring.md` | Мониторинг и алертинг |
| `06-cicd.md` | CI/CD |
| `07-operations.md` | Эксплуатация и обслуживание |
| `08-conclusion.md` | Заключение |
| `09-references.md` | Список литературы |
| `10-appendix.md` | Приложения со скриншотами |

## Обновление документации

При изменении markdown-файлов в `app/docs/`:

1. Собрать образ локально и проверить:
   ```bash
   docker build -t diplom-app:docs ./app
   docker run --rm -p 8080:80 diplom-app:docs
   ```
2. Закоммитить в feature-ветку, создать PR.
3. После мержа — создать тег для деплоя.

## Полезные ссылки

- [Yandex Cloud. Container Registry](https://yandex.cloud/ru/docs/container-registry)
- [GitHub Actions. Documentation](https://docs.github.com/en/actions)
- [Docker Build Push Action](https://github.com/docker/build-push-action)
- [repository-dispatch](https://github.com/peter-evans/repository-dispatch)

## Лицензия

Проект создан в рамках дипломной работы курса
«DevOps для опытных инженеров» в Netology.
