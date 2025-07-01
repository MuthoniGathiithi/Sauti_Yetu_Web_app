from django.utils.deprecation import MiddlewareMixin

class NoAnonymousSessionMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        if not request.user.is_authenticated:
            if hasattr(request, 'session'):
                request.session.flush()
        return response
