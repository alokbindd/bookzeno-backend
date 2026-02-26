from rest_framework.pagination import CursorPagination

class OrderCursorPagination(CursorPagination):
    page_size = 10
    ordering = ('-created_at','id')