# Django reCaptcha v3 [![Build Status](https://travis-ci.org/kbytesys/django-recaptcha3.svg?branch=master)](https://travis-ci.org/kbytesys/django-recaptcha2)
----

This integration app implements a recaptcha field for <a href="https://developers.google.com/recaptcha/intro">Google reCaptcha v3</a>.

**Warning:** this package is **not** compatible with django-recaptcha2

----

## How to install

Install the required package from pip (or take the source and install it by yourself):

```bash
pip install django-recaptcha3
```

Then add django-recaptcha3 to your installed apps:

```python
INSTALLED_APPS = (
    ...
    'snowpenguin.django.recaptcha3',
    ...
)
```

And add your reCaptcha private and public key to your django settings.py and the default action name, recaptcha score threshold:

```python
RECAPTCHA_PRIVATE_KEY = 'your private key'
RECAPTCHA_PUBLIC_KEY = 'your public key'
RECAPTCHA_DEFAULT_ACTION = 'generic'
RECAPTCHA_SCORE_THRESHOLD = 0.5
# If you require reCaptcha to be loaded from somewhere other than https://google.com
# (e.g. to bypass firewall restrictions), you can specify what proxy to use.
# RECAPTCHA_FRONTEND_PROXY_HOST = 'https://recaptcha.net'

```

If you have to create the apikey for the domains managed by your django project, you can visit this <a href="https://www.google.com/recaptcha/admin">website</a>.

## Usage
### Form and Widget
You can simply create a reCaptcha enabled form with the field provided by this app:

```python
from snowpenguin.django.recaptcha3.fields import ReCaptchaField

class ExampleForm(forms.Form):
    [...]
    captcha = ReCaptchaField()
    [...]
```

Form validation of the ReCaptchaField causes us to verify the token returned from the client against the ReCaptcha servers and populates a dictionary containing the `score`, `action`, `hostname`, and `challenge_ts` fields as the form fields `cleaned_data`:

```python
    def formview(request):
        if request.method == "POST":
            form = ExampleForm(request.POST)
            if form.is_valid():
              captcha_score = form.cleaned_data['captcha'].get('score')
```

If a communication problem occurs, the token supplied by the client is invalid or has expired then a ValidationError is raised.

## Automatic Enforcement

If you want low scores to cause a ValidationError, pass an appropriate `score_threshold` to the `ReCaptchaField`, or set the configuration variable settings.RECAPTCHA_SCORE_THRESHOLD.

The default value for the threshold is 0.0, which allows all successful capture responses through for you to later check the value of `score`.

```python
from snowpenguin.django.recaptcha3.fields import ReCaptchaField

class ExampleForm(forms.Form):
    [...]
    captcha = ReCaptchaField(score_threshold=0.5)
    [...]
```

You can also set the private key on the "private_key" argument of the ReCaptchaField contructor if you want to override the one inside your configuration.

### Templating
You can use some template tags to simplify the reCaptcha adoption:

* recaptcha_init: add the script tag for reCaptcha api. You have to put this tag somewhere in your "head" element
* recaptcha_ready: call the execute function when the api script is loaded
* recaptcha_execute: start the reCaptcha check and set the token from the api in your django forms. Token is valid for 120s, after this time it is automatically regenerated.
* recaptcha_key: if you want to use reCaptcha manually in your template, you will need the sitekey (a.k.a. public api key).
  This tag returns a string with the configured public key.

You can use the form as usual.

### Samples
#### Simple

Just create a form with the reCaptcha field and follow this template example:

```django
{% load recaptcha3 %}
<html>
  <head>
      {% recaptcha_init %}
      {% recaptcha_ready action_name='homepage' %}
  </head>
  <body>
    <form action="?" method="POST">
      {% csrf_token %}
      {{ form }}
      <input type="submit" value="Submit">
    </form>
  </body>
</html>
```

#### Custom callback

The callback can be used to allow to use the token received from the api in ajax calls or whatever

```django
{% load recaptcha3 %}
<html>
  <head>
      <script>
          function alertToken(token) {
              alert(token);
          }
      </script>
      {% recaptcha_init %}
      {% recaptcha_ready action_name='homepage' custom_callback='alertToken' %}
  </head>
  <body>
    <form action="?" method="POST">
      {% csrf_token %}
      {{ form }}
      <input type="submit" value="Submit">
    </form>
  </body>
</html>
```

#### Multiple render example

You can render multiple reCaptcha without any extra effort:

```django
{% load recaptcha3 %}
<html>
  <head>
      {% recaptcha_init %}
      {% recaptcha_ready action_name='homepage' %}
  </head>
  <body>
    <form action="?" method="POST">
      {% csrf_token %}
      {{ form1 }}
      <input type="submit" value="Submit">
    </form>
    <form action="?" method="POST">
      {% csrf_token %}
      {{ form2 }}
      <input type="submit" value="Submit">
    </form>
  </body>
</html>
```

#### Bare metal!

You can use the plain javascript, just remember to set the correct value for the hidden field in the form

```django
<html>
  <head>
      <script src="https://www.google.com/recaptcha/api.js?render=reCAPTCHA_site_key"></script>
      <script>
        grecaptcha.ready(function() {
          var grecaptcha_execute = function(){
            grecaptcha.execute('reCAPTCHA_site_key', {action: 'homepage'}).then(function(token) {
              document.querySelectorAll('input.django-recaptcha-hidden-field').forEach(function (value) {
                  value.value = token;
              });
              return token;
            })
          };
          grecaptcha_execute()
          setInterval(grecaptcha_execute, 120000);
        });
      </script>
  </head>
  <body>
    <form action="?" method="POST">
      {% csrf_token %}
      {{ form }}
      <input type="submit" value="Submit">
    </form>
  </body>
</html>
```


## Testing
### Test unit support
You can disable recaptcha field validation in unit tests by setting the RECAPTCHA_DISABLE env variable. This will fake the external call to Recaptca servers and return a fixed score of 0.6.

```python
os.environ['RECAPTCHA_DISABLE'] = 'True'
```

You can simular failure by raising `score_threshold` higher than this.

Warning: you can use any word in place of "True", the clean function will check only if the variable exists.

### Test unit with recaptcha3 disabled
```python
import os
import unittest

from yourpackage.forms import MyForm

class TestCase(unittest.TestCase):
    def setUp(self):
        os.environ['RECAPTCHA_DISABLE'] = 'True'

    def test_myform(self):
        form = MyForm({
            'field1': 'field1_value'
        })
        self.assertTrue(form.is_valid())

    def tearDown(self):
        del os.environ['RECAPTCHA_DISABLE']
```
