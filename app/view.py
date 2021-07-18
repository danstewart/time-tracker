import arrow
from flask import Blueprint, render_template, redirect, request, current_app as app
from app.controller import Time
from app.controller import Settings
from app.lib.logger import get_logger
from app.lib.database import pony

v = Blueprint('default', __name__)
logger = get_logger('view.py')


@app.context_processor
@pony.db_session
def inject_settings():
    return dict(settings=Settings().get())


@v.get('/')
def home():
    time_entries = Time().get_all()
    return render_template('home.html.j2', time_entries=time_entries, tz=Time().tz, arrow=arrow)


@v.route('/settings', methods=['GET', 'POST'])
def settings():
    settings = Settings()

    if request.form:
        settings.update(**request.form)

    return render_template('settings.html.j2', settings=settings.settings)


@v.post('/time/add')
def add_time():
    if request.form:
        values = dict(request.form)
        clock = values.pop('clock')

        if clock == 'manual':
            Time().create(**values)
        elif clock == 'in':
            Time().create(start=values['time'])
        else:
            Time().clock_out(end=values['time'])

    return redirect('/')


@v.delete('/time/delete/<row_id>')
def delete_time(row_id):
    Time().delete(row_id)
    return 'OK', 200
