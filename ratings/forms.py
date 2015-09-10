from django import forms
from django.core.exceptions import ValidationError

from grunt.models import Message
from ratings.models import Survey, Question


class MessageIdField(forms.Field):
    def to_python(self, value):
        try:
            return map(int, value.split(','))
        except AttributeError:
            # value is already a list of ints
            return map(int, value)
        except ValueError:
            raise ValidationError('Messages must be given as ints')

    def validate(self, value):
        all_message_ids = Message.objects.values_list('id', flat=True)
        for message_id in value:
            if message_id not in all_message_ids:
                raise ValidationError('Message not found')


class SurveyForm(forms.ModelForm):
    questions = MessageIdField()
    choices = MessageIdField()

    class Meta:
        model = Survey
        fields = ('questions', 'choices')

    def save(self):
        """ Create a survey and then create questions for that survey """
        survey = super(SurveyForm, self).save()

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
