from rest_framework import status
from django.db.models import Q
from rest_framework.response import Response
from rest_framework.generics import ListAPIView, GenericAPIView, CreateAPIView
from rest_framework.mixins import ListModelMixin
from rest_framework.throttling import ScopedRateThrottle

from custom_auth.serializers import UserSerializer
from .serializers import ConnectionRequestSerializer
from .models import ConnectionRequestModel
from .constants import REQUEST_REJECTED, REQUEST_ACCEPTED, REQUEST_PENDING
from custom_auth.models import User

class SearchUsersView(ListAPIView):
    serializer_class = UserSerializer
    
    def get_queryset(self):
        search_term = self.request.query_params.get('key')
        if search_term is None:
            queryset = User.objects.order_by('first_name')
        else:
            queryset = User.objects.filter(first_name__istartswith=search_term).order_by('first_name')
            if not queryset.exists():
                queryset = User.objects.filter(email=search_term).order_by('email')
        return queryset.exclude(id=self.request.user.id)
    
class CreateConnectionRequestView(GenericAPIView):
    serializer_class = ConnectionRequestSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = 'connection_request'
    
    def post(self, request, *args, **kwargs):
        payload = request.data
        if type(request.data) is not dict:
            payload = request.data.dict()
        payload['sender'] = request.user.id
        serializer = ConnectionRequestSerializer(data=payload)
        valid = serializer.is_valid()
        if not valid:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        instance = serializer.save()
        response = ConnectionRequestSerializer(instance).data
        return Response(response, status=status.HTTP_201_CREATED)

class ConnectionRequestView(GenericAPIView, ListModelMixin):
    serializer_class = ConnectionRequestSerializer

    def patch(self, request, connection_id, *args, **kwargs):
        payload = request.data
        try:
            instance = ConnectionRequestModel.objects.get(id=connection_id, request_to__id=self.request.user.id)
        except:
            return Response({"error": "connection request does not exist"}, status=status.HTTP_403_FORBIDDEN)
        if payload.get('status') == REQUEST_REJECTED:
            instance.delete()
            return Response({"id": instance.id}, status=status.HTTP_200_OK)
        connection_request = self.get_serializer(instance, data=payload, partial=True)
        if not connection_request.is_valid():
            return Response(connection_request.errors, status=status.HTTP_400_BAD_REQUEST)
        instance = connection_request.save()
        response = self.get_serializer(instance).data
        return Response(response, status=status.HTTP_200_OK)

    def get_queryset(self):
        status = self.request.query_params.get('status')
        if status == REQUEST_PENDING:
            queryset = ConnectionRequestModel.objects.filter(request_to__id=self.request.user.id, status=REQUEST_PENDING)
        else:
            queryset = ConnectionRequestModel.objects.filter(Q(request_to__id=self.request.user.id) | Q(sender__id=self.request.user.id), status=REQUEST_ACCEPTED)
        return queryset.order_by('-updated_at')
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
