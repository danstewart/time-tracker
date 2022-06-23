# Log My Time

Basic time logging tool.  

## Demo

![file](https://user-images.githubusercontent.com/10670565/168468584-cb9182ad-d82e-4fe5-aa96-c937a826611c.gif)


---


## Setup

#### Running with docker

Start on http://localhost:4000/ via docker
```bash
# Dev mode
docker-compose up -d --build app

# Prod mode
docker compose -f docker-compose.yml up -d --build
```

#### Install dependencies locally

We use [hermit](https://cashapp.github.io/hermit/usage/get-started/) to manage the python version

```bash
# Install Hermit
curl -fsSL https://github.com/cashapp/hermit/releases/download/stable/install.sh | /bin/bash

# Active Hermit
source bin/activate-hermit

# Install poetry
curl -sSL https://install.python-poetry.org | python3 - --version 1.2.0b1

# Install deps with poetry
poetry config virtualenvs.in-project true
poetry install

# Start a poetry shell
poetry shell
```

#### Connecting to the database
```bash
./scripts/sql.sh
```

#### Running the tests
```bash
./scripts/run_tests.sh
```

---

### Built with

- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [SQLite](https://sqlite.org/index.html)
- [Pony ORM](https://ponyorm.org/)
- [Arrow](https://arrow.readthedocs.io/en/latest/)
- [Bootstrap 5](https://getbootstrap.com/)
- [Spacetime](https://spacetime.how/)
