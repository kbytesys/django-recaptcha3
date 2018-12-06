from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def recaptcha_key():
    return settings.RECAPTCHA_PUBLIC_KEY


@register.inclusion_tag('snowpenguin/recaptcha/recaptcha_init.html')
def recaptcha_init(public_key=None, hl=None):
    return {'public_key': public_key or settings.RECAPTCHA_PUBLIC_KEY,
            'hl': hl or 'en'
    }


@register.inclusion_tag('snowpenguin/recaptcha/recaptcha_ready.html')
def recaptcha_ready(public_key=None, action_name=None, custom_callback=None):
    return {
        'public_key': public_key or settings.RECAPTCHA_PUBLIC_KEY,
        'action_name': action_name or settings.RECAPTCHA_DEFAULT_ACTION,
        'custom_callback': custom_callback
    }


@register.inclusion_tag('snowpenguin/recaptcha/recaptcha_execute.html')
def recaptcha_execute(public_key=None, action_name=None, custom_callback=None):
    return {
        'public_key': public_key or settings.RECAPTCHA_PUBLIC_KEY,
        'action_name': action_name or settings.RECAPTCHA_DEFAULT_ACTION,
        'custom_callback': custom_callback
    }
