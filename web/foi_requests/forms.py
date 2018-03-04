from django.forms import ModelForm, Textarea, CharField
from .models import Message


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = [
            'receiver',
            'title',
            'body',
        ]
        # TODO: clean this up once we have widget_tweaks
        classes = 'db border-box hover-black w-100'
        classes += ' measure ba b--black-20 pa2 br2 mb2'
        widgets = {
            'body': Textarea(attrs={'class': classes}),
        }

    # TODO https://github.com/jazzband/django-widget-tweaks
    # install above dependency to ease the class adding process
    title = CharField()
