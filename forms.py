from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectField, SubmitField
from wtforms.validators import DataRequired

class ProductForm(FlaskForm):
    product_id = StringField('Product ID', validators=[DataRequired()])
    name = StringField('Product Name', validators=[DataRequired()])
    submit = SubmitField('Save')

class LocationForm(FlaskForm):
    location_id = StringField('Location ID', validators=[DataRequired()])
    name = StringField('Location Name', validators=[DataRequired()])
    submit = SubmitField('Save')

class MovementForm(FlaskForm):
    movement_id = StringField('Movement ID', validators=[DataRequired()])
    product_id = SelectField('Product', choices=[], validators=[DataRequired()])
    from_location = SelectField('From Location', choices=[])
    to_location = SelectField('To Location', choices=[])
    qty = IntegerField('Quantity', validators=[DataRequired()])
    submit = SubmitField('Save')
