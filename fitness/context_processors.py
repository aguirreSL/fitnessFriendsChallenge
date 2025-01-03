from .utils import get_latest_version

def version_processor(request):
    version = get_latest_version()
    return {'app_version': version}
