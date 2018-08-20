from django.forms.widgets import Input


class ReCaptchaHiddenInput(Input):
    input_type = 'hidden'
    template_name = 'snowpenguin/recaptcha/recaptcha_hidden_input.html'

    def value_from_datadict(self, data, files, name):
        return [data.get('g-recaptcha-response', None)]
