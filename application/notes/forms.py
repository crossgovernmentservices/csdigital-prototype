from flask.ext.login import current_user
from flask.ext.wtf import Form
from wtforms.fields import (
    StringField,
    TextAreaField)
from wtforms.validators import Required

from application.models import Entry, LogEntry


class NoteForm(Form):
    title = StringField('Title')
    tags = StringField('tags')
    content = TextAreaField('Content', validators=[Required()])

    def update(self, note):
        note.entry.update(
            title=self.title.data,
            content=self.content.data)
        note.entry.save()

        for tag in self.tags.data.split(','):
            note.add_tag(tag)

    def create(self):
        entry = Entry(
            title=self.title.data,
            content=self.content.data)
        entry.save()

        note = LogEntry(
            entry_type='log',
            owner=current_user._get_current_object(),
            entry=entry)
        note.save()

        for tag in self.tags.data.split(','):
            note.add_tag(tag)

        return note
