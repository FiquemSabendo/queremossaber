from django.forms import ModelForm, CharField

from .models import Message, Esic, PublicBody


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = [
            'receiver',
            'summary',
            'body',
        ]

    summary = CharField()


class EsicForm(ModelForm):
    class Meta:
        model = Esic
        fields = [
            'url',
        ]


class PublicBodyForm(ModelForm):
    class Meta:
        model = PublicBody
        fields = [
            'name',
            'municipality',
            'uf',
        ]
