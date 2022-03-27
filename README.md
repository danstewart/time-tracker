# Time Tracker

Basic time tracker tool.  

### Setup

Start on http://localhost:4000/:
```bash
docker-compose up -d --build app
```

Database:
```bash
docker exec -it time-tracker sqlite3 ./db/time.db
```

### Built with

- [Flask](https://flask.palletsprojects.com/en/2.0.x/)
- [SQLite](https://sqlite.org/index.html)
- [Pony ORM](https://ponyorm.org/)
- [Arrow](https://arrow.readthedocs.io/en/latest/)
- [Bootstrap 5](https://getbootstrap.com/)
- [Spacetime](https://spacetime.how/)
