# This module provides tests for periodic tasks using core.decorators.cron

from edinsights.core.decorators import view, mq_force_retrieve, NotInCacheError
from edinsights.periodic.tasks import big_computation, big_computation_withfm

@view()
def big_computation_visualizer():
    return "<html>%s</html>" % mq_force_retrieve(big_computation)()


@view()
def big_computation_visualizer_withfm():
    try:
        # returns instantly, does not perform computation if results are not
        # in cache
        result = mq_force_retrieve(big_computation_withfm)()
    except NotInCacheError:
        result = "The big computation has not been performed yet"
        # alternatively you can display a "please wait" message
        # and run  big_computation_withfm() without force_retrieve
    return "<html>%s</html>" % result
