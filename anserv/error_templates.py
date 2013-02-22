from django.http import HttpResponseNotFound, HttpResponseServerError

def render_404(request):
    return HttpResponseNotFound(render_to_string('templates/404.html', {}))


def render_500(request):
    return HttpResponseServerError(render_to_string('templates/server-error.html', {}))
