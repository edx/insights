# This module provides tests for periodic tasks using core.decorators.cron

from edinsights.core.decorators import view, mq_force_retrieve
from edinsights.periodic.tasks import big_computation, big_computation_withfm

@view()
def big_computation_visualizer():
    return "<html>%s</html>" % mq_force_retrieve(big_computation)()


@view()
def big_computation_visualizer_withfm():
    return "<html>%s</html>" % mq_force_retrieve(big_computation_withfm)()
