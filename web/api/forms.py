from web.foi_requests.forms import MessageForm


class ApiMessageForm(MessageForm):
    class Meta(MessageForm.Meta):
        fields = MessageForm.Meta.fields + ["attached_file"]
