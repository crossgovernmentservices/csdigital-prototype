from flask.ext.wtf import Form
from wtforms.fields import (
    StringField,
    TextAreaField)
from wtforms.validators import Required

from application.models import create_log_entry


class NoteForm(Form):
    title = StringField('Title')
    tags = StringField('tags')
    content = TextAreaField('Details', validators=[Required()])

    def update(self, note):
        note.entry.update(
            title=self.title.data,
            content=self.content.data)

        self.add_tags(note, self.tags.data)

    def create(self):
        note = create_log_entry(
            'log',
            title=self.title.data,
            content=self.content.data)

        self.add_tags(note, self.tags.data)

        return note

    def add_tags(self, note, tags):
        for tag in self.tags.data.split(','):
            note.add_tag(tag)
