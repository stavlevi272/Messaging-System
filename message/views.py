import json
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.base import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import authentication, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import authentication_classes, permission_classes, api_view
from rest_framework.response import Response
from message.models import Message
from message.serializers import MessageSerializer


@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@api_view(http_method_names=['GET'])
def get_all_messages(request):
    user = request.user
    user_all_messages = Message.objects.all() \
        .filter(Q(sender=user.id, was_deleted_by_sender=False) |
                Q(receiver=user.id, was_deleted_by_receiver=False))
    if not user_all_messages:
        return JsonResponse({"response": "No messages were found for the current user"})
    return JsonResponse(MessageSerializer.serialize_to_json(user_all_messages))


@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@api_view(http_method_names=['GET'])
def get_message_by_id(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
        user = request.user
        if message.receiver.username == user.username or message.sender.username == user.username:
            if message.receiver == user.username:
                message.mark_read()
                message.save()
            return JsonResponse(MessageSerializer.serialize_to_json([message]))
        else:
            return JsonResponse({"response": "You don't have permission to see the message"})
    except ObjectDoesNotExist as ex:
        return JsonResponse({"response": "The message doesn't exist"})


@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@api_view(http_method_names=['GET'])
def get_all_unread_messages(request):
    user = request.user
    user_unread_messages = Message.objects.all() \
        .filter(receiver=user.id,
                was_read=False,
                was_deleted_by_receiver=False)
    if not user_unread_messages:
        return JsonResponse({"response": "all messages were read"})
    return JsonResponse(MessageSerializer.serialize_to_json(user_unread_messages))


@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@csrf_exempt
@api_view(http_method_names=['PUT'])
def mark_message_as_deleted_by_id(request, message_id):
    try:
        user = request.user
        message = Message.objects.get(id=message_id)
        if message.receiver.username == user.username or message.sender.username == user.username:
            message.mark_as_deleted(user.id)
            message.save()
            return JsonResponse({"response": "The message was deleted successfully"})
        else:
            return JsonResponse({"response": "You don't have permission to delete the message"})
    except ObjectDoesNotExist as ex:
        return JsonResponse({"response": "The message doesn't exist"})


@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@csrf_exempt
@api_view(http_method_names=['POST'])
def write_message(request):
    user = request.user
    sender = User.objects.get(username=user.username)
    try:
        receiver = User.objects.get(username=json.loads(request.body)["receiver"])
    except ObjectDoesNotExist as ex:
        return JsonResponse({"response": "The receiver user doesn't exist"})
    subject = json.loads(request.body.decode("utf-8"))["subject"]
    content = json.loads(request.body.decode("utf-8"))["content"]
    Message.objects.create(sender=sender, receiver=receiver, content=content, subject=subject)
    return JsonResponse({"response": "The message was sent successfully"})


class CustomAuthToken(ObtainAuthToken):

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data,
                                           context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email
        })
