from rest_framework import status
from rest_framework.response import Response


def success_response(data=None, message="Success", status=status.HTTP_200_OK):
    return Response({
        "success": True,
        "message": message,
        "data": data
    }, status=status)

def error_response(errors=None, message="Error", status=status.HTTP_400_BAD_REQUEST):
    return Response({
        "success": False,
        "message": message,
        "errors": errors
    }, status=status)