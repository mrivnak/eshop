from rest_framework.response import Response
from rest_framework.views import APIView


class StatusCheck(APIView):
    @staticmethod
    def get(request):
        return Response('OK')
