# This module provides tests for periodic tasks using core.decorators.cron

from edinsights.core.decorators import view
from edinsights.periodic.tasks import big_computation

@view()
def big_computation_visualizer():
    return "<html>%s</html>" % big_computation()


