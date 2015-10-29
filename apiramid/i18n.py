""" Internationalization
"""


import pyramid


MODULE_NAME = __name__

L10N_DOMAIN = MODULE_NAME


_ = pyramid.i18n.TranslationStringFactory(L10N_DOMAIN)


def gettext(msg_id):
    """ Intentionally returns the unaltered input for deferred translation.
        https://docs.python.org/3.4/library/gettext.html#deferred-translations
        'gettext' is a known extractor keyword.
    """
    return msg_id


# EOF
