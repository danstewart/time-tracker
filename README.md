# Time Tracker

Basic time tracker tool.  

### Setup

Start on http://localhost:4000/:
```bash
docker-compose up -d --build app
```

Installing dependencies locally:
```bash
pyenv local 3.10.0
pyenv exec poetry config virtualenvs.create true --local
pyenv exec poetry install
pyenv exec poetry shell
```

Database:
```bash
./scripts/sql.sh
```

Test:
```bash
./scripts/run_tests.sh
```

### Built with

- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [SQLite](https://sqlite.org/index.html)
- [Pony ORM](https://ponyorm.org/)
- [Arrow](https://arrow.readthedocs.io/en/latest/)
- [Bootstrap 5](https://getbootstrap.com/)
- [Spacetime](https://spacetime.how/)
