from ..forms import MessageForm


class TestMessageForm():
    def test_receiver_is_required(self):
        assert MessageForm().fields['receiver'].required
