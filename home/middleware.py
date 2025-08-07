from .models import SiteVisit

class TrackSiteVisitMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Ignore admin or static/media paths
        if request.path.startswith('/theboss') or request.path.startswith('/admin') or request.path.startswith('/static'):
            return response

        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        page_visited = request.path

        SiteVisit.objects.create(
            ip_address=ip_address,
            user_agent=user_agent,
            page_visited=page_visited
        )

        return response

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
