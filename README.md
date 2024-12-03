# insuranceCalc
### requirements:
- Docker 27.1.0 or above
- Docker Compose 2.29.0 or above
### deployment:
1) clone the repo and go to the repo dir
```bash
   git clone <URL_репозитория>
   cd <repo_dir>
```
2) replase or edit ./app/imports/import_rates.json for import rates
3) build image and run services:
   - without UI:
   ```bash
      docker compose up --build -d
   ```
   - with UI (adminer for postgres and kafka-ui for kafka):
   ```bash
      docker compose --profile optional_ui up --build -d
   ```  
4) wait end of building
5) use http://localhost:8000/docs for open swagger documentation
### to shutdown:
- without UI:
   ```bash
      docker compose down
   ```
- with UI (adminer for postgres and kafka-ui for kafka):
  ```bash
     docker compose --profile optional_ui down
  ```  