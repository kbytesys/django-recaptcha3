import os

from django import template
from django.conf import settings
from django.template.loader import get_template

register = template.Library()


@register.simple_tag
def recaptcha_key():
    return settings.RECAPTCHA_PUBLIC_KEY


def recaptcha_init(public_key=None):

    return {
        'public_key': public_key or settings.RECAPTCHA_PUBLIC_KEY,
        'google_api_host': 'https://www.google.com' if not hasattr(settings, 'RECAPTCHA_FRONTEND_PROXY_HOST')
                           else settings.RECAPTCHA_FRONTEND_PROXY_HOST
    }


def recaptcha_ready(public_key=None, action_name=None, custom_callback=None):
    return {
        'public_key': public_key or settings.RECAPTCHA_PUBLIC_KEY,
        'action_name': action_name or settings.RECAPTCHA_DEFAULT_ACTION,
        'custom_callback': custom_callback
    }


def recaptcha_execute(public_key=None, action_name=None, custom_callback=None):
    return {
        'public_key': public_key or settings.RECAPTCHA_PUBLIC_KEY,
        'action_name': action_name or settings.RECAPTCHA_DEFAULT_ACTION,
        'custom_callback': custom_callback
    }


def return_empty_context(*args, **kwargs):
    return ''


if not os.environ.get('RECAPTCHA_DISABLE', None):
    register.inclusion_tag(get_template('snowpenguin/recaptcha/recaptcha_init.html'))(recaptcha_init)
    register.inclusion_tag(get_template('snowpenguin/recaptcha/recaptcha_ready.html'))(recaptcha_ready)
    register.inclusion_tag(get_template('snowpenguin/recaptcha/recaptcha_execute.html'))(recaptcha_execute)
else:
    register.simple_tag(return_empty_context, name='recaptcha_init')
    register.simple_tag(return_empty_context, name='recaptcha_ready')
    register.simple_tag(return_empty_context, name='recaptcha_execute')
