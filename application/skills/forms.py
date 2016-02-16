from flask.ext.wtf import Form
from wtforms.fields import IntegerField
from wtforms.validators import NumberRange, Required
from wtforms.widgets import Input


class RangeWidget(Input):

    def __init__(self):
        self.input_type = 'range'

    def __call__(self, field, **kwargs):
        kwargs.setdefault('step', '1')

        for validator in field.validators:
            if isinstance(validator, NumberRange):
                if validator.min is not None:
                    kwargs['min'] = str(validator.min)
                if validator.max is not None:
                    kwargs['max'] = str(validator.max)

        return super(RangeWidget, self).__call__(field, **kwargs)


class AuditForm(Form):
    commercial = IntegerField('Commercial', [
        Required(),
        NumberRange(min=0, max=100)], widget=RangeWidget(), default=1)
    digital = IntegerField('Digital', [
        Required(),
        NumberRange(min=0, max=100)], widget=RangeWidget(), default=1)
    delivery = IntegerField('Project delivery', [
        Required(),
        NumberRange(min=0, max=100)], widget=RangeWidget(), default=1)
    leadership = IntegerField('Change leadership', [
        Required(),
        NumberRange(min=0, max=100)], widget=RangeWidget(), default=1)
