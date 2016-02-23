from flask.ext.wtf import Form
from wtforms.fields import (
    StringField,
    TextAreaField)
from wtforms.validators import Required

from application.models import create_log_entry


class NoteForm(Form):
    title = StringField('Title')
    tags = StringField('tags')
    content = TextAreaField('Content', validators=[Required()])

    def update(self, note):
        note.entry.update(
            title=self.title.data,
            content=self.content.data)

        for tag in self.tags.data.split(','):
            note.add_tag(tag)

    def create(self):
        note = create_log_entry(
            'log',
            title=self.title.data,
            content=self.content.data)

        for tag in self.tags.data.split(','):
            note.add_tag(tag)

        return note
