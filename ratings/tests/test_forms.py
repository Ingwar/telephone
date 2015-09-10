from unipath import Path

from django.conf import settings
from django.test import TestCase, override_settings

from model_mommy import mommy

from grunt.models import Message
from ratings.models import Survey, Question, Choice
from ratings.forms import SurveyForm

TEST_MEDIA_ROOT = Path(settings.MEDIA_ROOT + '-test')


@override_settings(MEDIA_ROOT = TEST_MEDIA_ROOT)
class SurveyTest(TestCase):
    def tearDown(self):
        super(SurveyTest, self).tearDown()
        TEST_MEDIA_ROOT.rmtree()

    def test_make_new_survey(self):
        num_questions = 10
        questions = mommy.make(Message, _quantity=num_questions)
        questions_str = ','.join([str(message.id) for message in questions])

        choices = mommy.make(Message, _quantity=4)
        choices_str = ','.join([str(message.id) for message in choices])

        survey_form = SurveyForm({'questions': questions_str,
                                  'choices': choices_str})
        self.assertTrue(survey_form.is_valid())
        survey = survey_form.save()  # should not raise
        self.assertEquals(Survey.objects.count(), 1)

        self.assertEquals(survey.questions.count(), num_questions)

    def test_questions_must_be_actual_messages(self):
        questions_str = '1,2,3'
        choices_str = '4,5,6'
        survey_form = SurveyForm({'questions': questions_str,
                                  'choices': choices_str})
        self.assertFalse(survey_form.is_valid())

    def test_questions_must_be_csv_ints(self):
        questions_str = 'a,b,c'
        choices_str = 'd,e,f'
        survey_form = SurveyForm({'questions': questions_str,
                                  'choices': choices_str})
        self.assertFalse(survey_form.is_valid())

    def test_questions_can_contain_spaces(self):
        questions = mommy.make(Message, _quantity=10)
        questions_str = ', '.join([str(message.id) for message in questions])

        choices = mommy.make(Message, _quantity=4)
        choices_str = ',  '.join([str(message.id) for message in choices])

        survey_form = SurveyForm({'questions': questions_str,
                                  'choices': choices_str})
        self.assertTrue(survey_form.is_valid())
