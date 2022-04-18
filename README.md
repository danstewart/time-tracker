# Time Tracker

Basic time tracker tool.  

## Setup

#### Running with docker

Start on http://localhost:4000/ via docker
```bash
docker-compose up -d --build app
```

#### Install dependencies locally

We use [hermit](https://cashapp.github.io/hermit/usage/get-started/) to manage the python version

```bash
# Install Hermit
curl -fsSL https://github.com/cashapp/hermit/releases/download/stable/install.sh | /bin/bash

# Active Hermit
source bin/activate-hermit

# Install poetry
curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python3 -

# Install deps with poetry
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
