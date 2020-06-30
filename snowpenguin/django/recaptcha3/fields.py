import logging
import os

from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

import requests

from snowpenguin.django.recaptcha3.widgets import ReCaptchaHiddenInput

logger = logging.getLogger(__name__)


class ReCaptchaField(forms.CharField):
    def __init__(self, attrs=None, *args, **kwargs):
        if os.environ.get('RECAPTCHA_DISABLE', None) is None:
            self._private_key = kwargs.pop('private_key', settings.RECAPTCHA_PRIVATE_KEY)
            self._score_threshold = kwargs.pop('score_threshold', settings.RECAPTCHA_SCORE_THRESHOLD)

        if 'widget' not in kwargs:
            kwargs['widget'] = ReCaptchaHiddenInput()

        super(ReCaptchaField, self).__init__(*args, **kwargs)

    def clean(self, values):

        # Disable the check if we run a test unit
        if os.environ.get('RECAPTCHA_DISABLE', None) is not None:
            return values[0]

        super(ReCaptchaField, self).clean(values[0])
        response_token = values[0]

        try:
            r = requests.post(
                'https://www.google.com/recaptcha/api/siteverify',
                {
                    'secret': self._private_key,
                    'response': response_token
                },
                timeout=5
            )
            r.raise_for_status()
        except requests.RequestException as e:
            logger.exception(e)
            raise ValidationError(
                _('Connection to reCaptcha server failed'),
                code='connection_failed'
            )

        json_response = r.json()

        logger.debug("Recieved response from reCaptcha server: %s", json_response)
        if bool(json_response['success']):
            if self._score_threshold is not None and self._score_threshold > json_response['score']:
                raise ValidationError(
                    _('reCaptcha score is too low. score: %(score)s'),
                    code='score',
                    params={'score': json_response['score']},
                )
            return values[0]
        else:
            if 'error-codes' in json_response:
                if 'missing-input-secret' in json_response['error-codes'] or \
                        'invalid-input-secret' in json_response['error-codes']:

                    logger.exception('Invalid reCaptcha secret key detected')
                    raise ValidationError(
                        _('Connection to reCaptcha server failed'),
                        code='invalid_secret',
                    )
                else:
                    raise ValidationError(
                        _('reCaptcha invalid or expired, try again'),
                        code='expired',
                    )
            else:
                logger.exception('No error-codes received from Google reCaptcha server')
                raise ValidationError(
                    _('reCaptcha response from Google not valid, try again'),
                    code='invalid_response',
                )
