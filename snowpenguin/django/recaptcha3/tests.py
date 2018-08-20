import os

from django.forms import Form
from django.test import TestCase

from snowpenguin.django.recaptcha3.fields import ReCaptchaField
from snowpenguin.django.recaptcha3.widgets import ReCaptchaHiddenInput


class RecaptchaTestForm(Form):
    recaptcha = ReCaptchaField(widget=ReCaptchaHiddenInput())


class TestRecaptchaForm(TestCase):
    def setUp(self):
        os.environ['RECAPTCHA_DISABLE'] = 'True'

    def test_dummy_validation(self):
        form = RecaptchaTestForm({})
        self.assertTrue(form.is_valid())

    def test_dummy_error(self):
        del os.environ['RECAPTCHA_DISABLE']
        form = RecaptchaTestForm({})
        self.assertFalse(form.is_valid())

    def tearDown(self):
        if 'RECAPTCHA_DISABLE' in os.environ.keys():
            del os.environ['RECAPTCHA_DISABLE']
