class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Log the request headers
        print(request.headers)
        return self.get_response(request)
