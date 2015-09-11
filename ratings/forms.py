from django import forms
from django.core.exceptions import ValidationError

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from grunt.models import Message
from ratings.models import Survey, Question


class MessageIdField(forms.Field):
    def to_python(self, value):
        try:
            return map(int, value.split(','))
        except AttributeError:
            # value is already a list, so just make sure they are ints
            return map(int, value)
        except ValueError:
            raise ValidationError('Messages must be given as ints')

    def validate(self, value):
        all_message_ids = Message.objects.values_list('id', flat=True)
        for message_id in value:
            if message_id not in all_message_ids:
                raise ValidationError('Message not found')


class NewSurveyForm(forms.ModelForm):
    questions = MessageIdField()
    choices = MessageIdField()

    class Meta:
        model = Survey
        fields = ('name', 'questions', 'choices')

    def __init__(self, *args, **kwargs):
        super(NewSurveyForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Create'))

    def save(self):
        """ Create a survey and then create questions for that survey """
        survey = super(NewSurveyForm, self).save()

        choices = self.cleaned_data['choices']
        for message_id in self.cleaned_data.get('questions'):
            question_data = {
                'survey': survey.id,
                'given': message_id,
                'choices': choices,
            }
            question_form = CreateQuestionForm(question_data)
            if question_form.is_valid():
                question_form.save()

        return survey


class CreateQuestionForm(forms.ModelForm):
    choices = MessageIdField()

    class Meta:
        model = Question
        fields = ('survey', 'given', 'choices')

    def save(self):
        question = super(CreateQuestionForm, self).save()
        messages = Message.objects.filter(id__in=self.cleaned_data['choices'])
        question.choices.add(*messages)

        given_chain = question.given.chain
        possible_answers = given_chain.message_set.all()
        for choice in messages:
            if choice in possible_answers:
                question.answer = choice
                question.save()
                break

        if not question.answer:
            raise ValidationError('No descendant was found in choices')

        return question