from flask.ext.wtf import Form
from wtforms.fields import (
    StringField,
    TextAreaField)
from wtforms.validators import Required


class NoteForm(Form):
    tags = StringField('tags')
    content = TextAreaField('Content', validators=[Required()])

    def init_from_note(self, note):
        self.content.data = note.entry.content
        self.tags.data = ', '.join(tag.name for tag in note.tags)
