import os
import mock

from django.forms import Form
from django.test import TestCase

from snowpenguin.django.recaptcha3.fields import ReCaptchaField
from snowpenguin.django.recaptcha3.widgets import ReCaptchaHiddenInput


class RecaptchaTestForm(Form):
    recaptcha = ReCaptchaField(widget=ReCaptchaHiddenInput())


class TestRecaptchaForm(TestCase):
    def test_dummy_validation(self):
        os.environ['RECAPTCHA_DISABLE'] = 'True'
        form = RecaptchaTestForm({})
        self.assertTrue(form.is_valid())
        del os.environ['RECAPTCHA_DISABLE']

    @mock.patch('requests.post')
    def test_validate_error_invalid_token(self, requests_post):

        recaptcha_response = {'success': False}
        requests_post.return_value.json = lambda: recaptcha_response

        form = RecaptchaTestForm({"g-recaptcha-response": "dummy token"})
        self.assertFalse(form.is_valid())

    @mock.patch('requests.post')
    def test_validate_error_lower_score(self, requests_post):

        recaptcha_response = {
            'success': True,
            'score': 0.5
        }
        requests_post.return_value.json = lambda: recaptcha_response

        class RecaptchaTestForm(Form):
            recaptcha = ReCaptchaField(score_threshold=0.7)
        form = RecaptchaTestForm({"g-recaptcha-response": "dummy token"})
        self.assertFalse(form.is_valid())

    @mock.patch('requests.post')
    def test_validate_success_highter_score(self, requests_post):

        recaptcha_response = {
            'success': True,
            'score': 0.7
        }
        requests_post.return_value.json = lambda: recaptcha_response

        class RecaptchaTestForm(Form):
            recaptcha = ReCaptchaField(score_threshold=0.4)
        form = RecaptchaTestForm({"g-recaptcha-response": "dummy token"})
        self.assertTrue(form.is_valid())

    @mock.patch('requests.post')
    def test_validate_success(self, requests_post):

        recaptcha_response = {
            'success': True,
            'score': 0.5
        }
        requests_post.return_value.json = lambda: recaptcha_response

        form = RecaptchaTestForm({"g-recaptcha-response": "dummy token"})
        self.assertTrue(form.is_valid())
