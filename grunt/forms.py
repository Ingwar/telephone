from django import forms

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from .models import Message, Game, Chain


class ResponseForm(forms.ModelForm):
    """ Save the message received from the player. """
    class Meta:
        model = Message
        fields = ('parent', 'audio')

    def save(self, **kwargs):
        """ Create a new message and populate fields from parent. """
        message = super(ResponseForm, self).save(**kwargs)
        message.chain = message.parent.chain
        message.generation = message.parent.generation + 1
        message.save()
        return message


class NewGameForm(forms.ModelForm):
    """ Creates a new game.

    num_chains is used by the view to render the correct number
    of new chain forms on the following page.
    """
    num_chains = forms.IntegerField(initial=1, min_value=1)

    class Meta:
        model = Game
        fields = ('name', )

    def __init__(self, *args, **kwargs):
        """ Crispy form """
        super(NewGameForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create'))


class NewChainForm(forms.ModelForm):
    seed = forms.FileField()

    class Meta:
        model = Chain
        fields = ('game', 'name')

    def save(self, **kwargs):
        """ Create a new chain and then create a seed message for it. """
        chain = super(NewChainForm, self).save(**kwargs)
        chain.messages.create(audio=self.cleaned_data['seed'])
        return chain


class NewChainFormSet(forms.models.BaseModelFormSet):
    pass


class NewChainFormSetHelper(FormHelper):
    """ Styling specific to pages rendering multiple new chain forms """
    def __init__(self, *args, **kwargs):
        super(NewChainFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.add_input(Submit('submit', 'Create'))
