from rest_framework.pagination import PageNumberPagination
from collections import OrderedDict
from rest_framework.response import Response

class KgPagination():

    def get_page_size(limit):
        paginator = PageNumberPagination()
        if limit and int(limit) >= 1:
            return limit
        else:
            return paginator.page_size
    
    def get_response(limit,items,request,Serializer):
        paginator = PageNumberPagination()

        paginator.page_size = int(limit) if limit and int(
            limit) >= 1 else paginator.page_size
        result_page = paginator.paginate_queryset(items, request)
        serializer = Serializer(result_page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    def get_response_praticien(limit, items, request, Serializer,data=None):
        paginator = PageNumberPagination()
        paginator.page_size = int(limit) if limit and int(limit) >= 1 else paginator.page_size
        result_page = paginator.paginate_queryset(items, request)
        serializer = Serializer(result_page, many=True)
        
        # Create an OrderedDict for the paginated response
        paginated_response = OrderedDict()
        paginated_response['count'] = paginator.page.paginator.count
        paginated_response['next'] = paginator.get_next_link()
        paginated_response['previous'] = paginator.get_previous_link()
        paginated_response['documents'] = serializer.data
        paginated_response['categories'] = data
        return Response(paginated_response)
    

    def get_response_messages_recus(limit, items, request, Serializer,data=None):
        paginator = PageNumberPagination()
        paginator.page_size = int(limit) if limit and int(limit) >= 1 else paginator.page_size
        result_page = paginator.paginate_queryset(items, request)
        serializer = Serializer(result_page, many=True,context={'request': request})
        
        # Create an OrderedDict for the paginated response
        paginated_response = OrderedDict()
        paginated_response['count'] = paginator.page.paginator.count
        paginated_response['next'] = paginator.get_next_link()
        paginated_response['previous'] = paginator.get_previous_link()
        paginated_response['documents'] = serializer.data
        paginated_response['messages_non_lues'] = data
        return Response(paginated_response)
    
    def get_response_messages_envoyes(limit, items, request, Serializer,data=None):
        paginator = PageNumberPagination()
        paginator.page_size = int(limit) if limit and int(limit) >= 1 else paginator.page_size
        result_page = paginator.paginate_queryset(items, request)
        serializer = Serializer(result_page, many=True)
        
        # Create an OrderedDict for the paginated response
        paginated_response = OrderedDict()
        paginated_response['count'] = paginator.page.paginator.count
        paginated_response['next'] = paginator.get_next_link()
        paginated_response['previous'] = paginator.get_previous_link()
        paginated_response['documents'] = serializer.data
        paginated_response['messages_non_lues'] = data
        return Response(paginated_response)