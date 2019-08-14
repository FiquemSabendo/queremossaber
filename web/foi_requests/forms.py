from django.forms import ModelForm, CharField, Textarea

from .models import Message, Esic, PublicBody, FOIRequest


class MessageForm(ModelForm):
    class Meta:
        model = Message
        fields = [
            'receiver',
            'summary',
            'body',
        ]

    summary = CharField()
    body = CharField(min_length=55, widget=Textarea)

    def __init__(self, *args, **kwargs):
        super(MessageForm, self).__init__(*args, **kwargs)
        self.fields['receiver'].required = True


class FOIRequestForm(ModelForm):
    class Meta:
        model = FOIRequest
        fields = [
            'can_publish',
            'previous_protocol',
        ]


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
            'level',
        ]
