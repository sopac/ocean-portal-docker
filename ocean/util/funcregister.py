#
# (c) 2012 Commonwealth of Australia
#     Australian Bureau of Meteorology, COSPPac COMP
#     All Rights Reserved
#
# Authors: Danielle Madeley <d.madeley@bom.gov.au>

from functools import wraps
from ocean.core import ReportableException

class ParameteriseError(ReportableException):
    pass

class Parameterise(object):
    """
    apply_to is a decorator which makes it possible to implement
    multiple versions of a method, based on the passed parameters, for instance:

    class MyClass(object):
        p = Parameterise()

        @p.apply_to(variable='anom', period='monthly')
        def get_title(self, *args, params={}):
            ...

    Would only apply in the case where params included variable and period
    with their respective values.

    The method is then called something like:
        dataset.get_title(params={...})

    If a method matches too many versions, or is otherwise ambiguous,
    AttributeError is raised. Similarly if there are no available matches.
    """

    def __init__(self, supercls=object):
        self._registry = {}
        self._supercls = supercls

    def registry(self, name):
        try:
            funcs = self._registry[name]
        except KeyError:
            funcs = self._registry[name] = []
#            raise ParameteriseError

        return funcs

    def __call__(self, **methodparams):
        """
        This is the decorator.
        """

        def outer(func):
            name = func.__name__

            self.registry(name).append(func)
            func._methodparams = methodparams

            def matches(params, ignores):
                def inner(func):
                    for k, v in func._methodparams.items():
                        if k in ignores:
                            return False

                        if k not in params or params[k] != v:
                            return False

                    return True

                return inner

            @wraps(func)
            def inner(*args, **kwargs):
                __tracebackhide__ = True

                params = kwargs['params']

                try:
                    ignore = kwargs['_ignore']
                    del kwargs['_ignore']
                except KeyError:
                    ignore = []
#                    raise ParameteriseError
#                    raise Exception('inner')

                def find_registry(cls):
                    try:
                        for v in cls.__dict__.values():
                            if isinstance(v, Parameterise):
                                return v
                    except AttributeError:
#                        raise ParameteriseError
                        raise Exception('find')
                        pass

                    return None

                def walk_back(funcs, supercls):
                    pp = find_registry(supercls)

                    if pp is not None:
                        funcs = walk_back(funcs, pp._supercls) + \
                                pp.registry(name)

                    return funcs

                funcs = walk_back(self.registry(name), self._supercls)
                from ocean import util, logger
                logger.log('funcs')
                logger.log(str(funcs))

                candidates = filter(matches(params, ignore), funcs)
                logger.log('candidates')
                logger.log(str(candidates))
                candidates.sort(key=lambda f: len(f._methodparams),
                                reverse=True)

                if len(candidates) == 1:
                    return candidates[0](*args, **kwargs)
                elif len(candidates) > 1:
                    if len(candidates[0]._methodparams) == \
                       len(candidates[1]._methodparams):
                        logger.log('too many candidates')
                        raise AttributeError("Ambiguous. Too many matches")
                    else:
                        logger.log('return the first candidate')
                        return candidates[0](*args, **kwargs)
                else:
                    for f in funcs:
                        logger.log(name, f._methodparams)
                    raise AttributeError("No function matches parameters")

            return inner

        return outer
