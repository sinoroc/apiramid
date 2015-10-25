""" Apiramid module
"""


import inspect
import logging
import pyramid
import types
import venusian

from . import api
from . import i18n
from . import util
from . import view


MODULE_NAME = __name__

ENDPOINT_NAME = '{}_{}'.format(MODULE_NAME, 'endpoint')
VENUSIAN_CATEGORY = MODULE_NAME
VENUSIAN_NAME_ENDPOINT = ENDPOINT_NAME


_ = i18n._

LOG = logging.getLogger(__name__)


class EndpointDefaults(object):
    """ Class decorator.
        Set defaults for methods decorated with ``Endpoint`` decorator.
    """

    ATTRIBUTE_NAME = '{}_endpoint_defaults'.format(MODULE_NAME)

    def __init__(self, **kwargs):
        """ Expected arguments: See Endpoint.__init__
        """
        self.endpoint_defaults = kwargs
        return None

    def __call__(self, decoratee):
        setattr(decoratee, self.ATTRIBUTE_NAME, self.endpoint_defaults)
        result = decoratee
        return result


class Endpoint(object):
    """ Decorator for function, method or class callable.
    """

    routes = []

    def __init__(self, **kwargs):
        """ Expected keywords:
            ``method``
            ``path``
        """
        self.endpoint = kwargs
        # utility members
        self.api_util = None
        self.decoratee = None
        self.decoratee_class = None
        self.resource = None  # resource parsed from the API document
        self.venusian_info = None
        return None

    def __call__(self, decoratee):
        self.decoratee = decoratee
        self.venusian_info = venusian.attach(
            decoratee,
            self.callback,
            category=VENUSIAN_CATEGORY,
            name=VENUSIAN_NAME_ENDPOINT,
        )
        return decoratee

    def callback(self, scanner, dummy_name, obj):
        """ Venusian callback.
        """
        if self.venusian_info.scope == 'class':
            self.decoratee_class = obj
        config = scanner.config.with_package(self.venusian_info.module)
        self.set_defaults(getattr(obj, EndpointDefaults.ATTRIBUTE_NAME, {}))
        self.check()
        self.api_util = config.registry.queryUtility(api.IApi)
        resource = self.api_util.find_resource(
            self.endpoint['path'],
            self.endpoint['method'],
        )
        if resource:
            self.dcmnt_resource = resource
            self.add_endpoint(config)
        else:
            LOG.warning(_("Could not find resource."))
        return None

    def set_defaults(self, defaults):
        """ Set defaults from ``EntrypointDefaults`` if any.
            Already set values are not overwritten of course.
        """
        for key, value in defaults.items():
            if key not in self.endpoint:
                self.endpoint[key] = value
        return None

    @property
    def name_route(self):
        """ Name of the route for this endpoint.
        """
        result = '{prefix}_{path}'.format(
            prefix=MODULE_NAME,
            path=self.endpoint['path'],
        )
        return result

    def check(self):
        """ Check the endpoint arguements.
        """
        if 'method' not in self.endpoint:
            comment = _("Endpoint has no method {}").format(self.endpoint)
            raise ValueError(comment)
        if 'path' not in self.endpoint:
            comment = _("Endpoint has no path {}").format(self.endpoint)
            raise ValueError(comment)
        return None

    def add_endpoint(self, config):
        """ Set an endpoint: add route if not available yet and add view.
        """
        self.add_route(config)
        self.add_view(config)
        return None

    def add_route(self, config):
        """ Add a Pyramid route if not added yet.
        """
        name = self.name_route
        if name not in self.routes:
            self.routes.append(name)
            path = '{base_path}{rel_path}'.format(
                base_path=self.api_util.base_path,
                rel_path=self.endpoint['path'],
            )
            config.add_route(name, path)
        return None

    def add_view(self, config):
        """ Add a Pyramid view.
        """
        config.add_view(
            view=self.view_wrapper,
            route_name=self.name_route,
            request_method=self.endpoint['method'],
        )
        return None

    def view_wrapper(self, *args, **kwargs):
        """ The view callable.
        """
        request = args[1]
        attr_name = self.api_util.request_endpoint_attribute
        setattr(request, attr_name, self)
        view.checkin(*args, **kwargs)
        request.response = self.run_view_callback(*args, **kwargs)
        view.checkout(*args, **kwargs)
        result = view.render(*args, **kwargs)
        LOG.error("Endpoint.view_wrapper {}".format(result))
        return result

    def run_view_callback(self, *args, **kwargs):
        """ Run the view callback decorated in the user application.
        """
        result = None
        if self.venusian_info.scope == 'class':
            # decoratee is a method
            view_callable = self.decoratee_class(*args, **kwargs)
            result = self.decoratee(view_callable)
        elif inspect.isclass(self.decoratee):
            # decoratee is a class callable
            view_callable = self.decoratee(*args, **kwargs)
            result = view_callable()
        elif inspect.isfunction(self.decoratee):
            # decoratee is a function
            result = self.decoratee(*args, **kwargs)
        else:
            raise Exception(_("Could not identify view callable."))
        return result


def get_endpoint(request):
    """ Get the ``Endpoint`` instance attached to the request.
    """
    api_util = request.registry.queryUtility(api.IApi)
    attr_name = api_util.request_endpoint_attribute
    result = getattr(request, attr_name, None)
    if result is None:
        raise Exception(_("Endpoint has not been attached to request yet."))
    return result


def includeme(config):
    """ Include the module in the Pyramid application.
    """
    document_path = config.registry.settings['{}.document'.format(MODULE_NAME)]

    attr_name = config.registry.settings.get(
        '{}.request_endpoint_attribute'.format(MODULE_NAME),
        '{}_endpoint'.format(MODULE_NAME),
    )

    definition = api.Api(document_path, attr_name)
    config.registry.registerUtility(definition, api.IApi)

    config.add_request_method(get_endpoint, attr_name, reify=True)

    config.add_view(
        util.exception_view,
        context=Exception,
        renderer='json',
    )
    config.add_view(
        util.http_exception_view,
        context=pyramid.httpexceptions.HTTPException,
        renderer='json',
    )

    return None


# EOF
