from flask import (
    Blueprint,
    render_template,
    flash,
    redirect,
    url_for,
    abort
)

from flask.ext.security import login_required
from flask.ext.login import current_user

from application.models import LogEntry
from application.mylog.forms import LogEntryForm

mylog = Blueprint('mylog', __name__, template_folder='templates')


@mylog.route('/my-log')
@login_required
def view_mylog():
    log_entries = LogEntry.objects.filter(owner=current_user._get_current_object()).all()
    return render_template('mylog/log.html', log_entries=log_entries)


@mylog.route('/my-log/entry', methods=['GET', 'POST'])
def add_log_entry():
    form = LogEntryForm()
    if form.validate_on_submit():
        entry = LogEntry(content=form.content.data)
        entry.owner = current_user._get_current_object()
        entry.save()
        flash('Entry saved')
        return redirect(url_for('mylog.view_mylog'))
    return render_template('mylog/add-entry.html', form=form)


@mylog.route('/my-log/entry/<id>')
def view_log_entry(id):
    entry = LogEntry.objects(id=id)
    if not entry:
        abort(404)
    return render_template('mylog/entry.html', entry=entry.get())
