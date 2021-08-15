import json

from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.base import ObjectDoesNotExist
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import authentication, permissions
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.response import Response

from message.models import Message, model_to_dict


@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
# @api_view(http_method_names=['GET'])
def get_all_messages(request):
    #todo replace with real user and inbox sent
    username = request.user.username
    user_all_messages = Message.objects.all() \
        .filter(Q(sender=1, was_deleted_by_sender=False) |
                Q(receiver=1, was_deleted_by_receiver=False))
    if not user_all_messages:
        return JsonResponse({"response": "No messages were found for the current user"})
    return JsonResponse(model_to_dict(user_all_messages))


@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_message_by_id(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
        #todo move to serazlizer
        message_data = {
            'sender': message.sender.username,
            'receiver': message.receiver.username,
            'subject': message.subject,
            'content': message.content,
            'creation date': message.creation_date,
        }
        if message.receiver == 'admin':#todo chnge user
            message.mark_read()
            message.save()

        return JsonResponse(message_data)
    except ObjectDoesNotExist as ex:
        return JsonResponse({"response": "The message doesn't exist"})


@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
def get_all_unread_messages(request):
    user_unread_messages = Message.objects.all() \
        .filter(receiver=2,
                was_read=False,
                was_deleted_by_receiver=False)
    if not user_unread_messages:
        return JsonResponse({"response": "all messages were read"})
    return JsonResponse(model_to_dict(user_unread_messages))


@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@csrf_exempt
# @api_view(http_method_names=['PUT'])
def mark_message_as_deleted_by_id(request, message_id):
    try:
        message = Message.objects.get(id=message_id)
        message.mark_as_deleted(1)
        message.save()
        return JsonResponse({"response": "The message was deleted successfully"})
    except ObjectDoesNotExist as ex:
        return JsonResponse({"response": "The message doesn't exist"})


@authentication_classes([authentication.TokenAuthentication])
@permission_classes([permissions.IsAuthenticated])
@csrf_exempt
def write_message(request):
    sender = User.objects.get(username=json.loads(request.body)["sender"])
    receiver = User.objects.get(username=json.loads(request.body)["receiver"])
    subject = json.loads(request.body.decode("utf-8"))["subject"]
    content = json.loads(request.body.decode("utf-8"))["content"]
    message_instance = Message.objects.create(sender=sender, receiver=receiver, content=content, subject=subject)
    return JsonResponse({"response":"The message was sent successfully"})


# def login_view(request):
#     next = request.GET.get('next')
#     form = UserLoginForm(request.POST or None)
#     if form.is_valid():
#         username = form.cleaned_data.get('username')
#         password = form.cleaned_data.get('password')
#         user = authenticate(username=username, password=password)
#         login(request, user)
#         if next:
#             return redirect(next)
#         return redirect('/')
#
#     context = {
#         'form': form,
#     }
#     return render(request, "login.html", context)


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



















"""
@login_required
@csrf_exempt
def write_message(request):
    template = loader.get_template('message/add_message.html')
    if request.method == "POST":
        sender = request.POST.get('sender')
        receiver = request.POST.get('receiver')
        message = request.POST.get('message')
        subject = request.POST.get('subject')
        #creation_date = datetime.datetime.now()
        #print(sender,receiver,message,subject,creation_date)
        message_instance = Message.objects.create(sender=sender, receiver=receiver, message=message, subject=subject)
    return HttpResponse(template.render({"info":"message sent"}, request))
    #return JsonResponse({"info":"create"})


# @login_required
# @csrf_exempt
# def write_message(request):
#     sender = json.loads(request.body.decode("utf-8"))["sender"]
#     receiver = json.loads(request.body.decode("utf-8"))["receiver"]
#     subject = json.loads(request.body.decode("utf-8"))["subject"]
#     message = json.loads(request.body.decode("utf-8"))["message"]
#     creation_date = datetime.datetime.now()
#     message_instance = Message.objects.create(sender=sender, receiver=receiver, message=message, subject=subject,
#                                               creation_date=creation_date)
#     return JsonResponse({"info":"message sent"})


@login_required
def all_messages(request, user):
    # user = User.get_username()
    user_messages = Message.objects.all().filter(Q(sender=user) | Q(receiver=user))
    send_data = model_to_dict(user_messages)
    if send_data == {}:
        return JsonResponse({"info": "no messages"})
    return JsonResponse(model_to_dict(user_messages))


@login_required
def all_unread_messages(request, user):
    user_unread_messages = Message.objects.all().filter(receiver=user, unread=True)
    send_data = model_to_dict(user_unread_messages)
    if send_data == {}:
        return JsonResponse({"info":"all messages were read"})
    return JsonResponse(send_data)


@login_required
def read_message(request,user, message_id):
    try:
        message = Message.objects.get(id=message_id)
    except Exception as e:
        return JsonResponse({"info": "the message doen't exist" })
    else:
        if message.receiver == user:
            message.mark_read()
            message.save()
        if message.receiver == user or message.sender == user:
            send_data ={
                'from': message.sender,
                'to': message.receiver,
                'body': message.message,
                'subject': message.subject,
                'creation date': message.creation_date,
            }
        else:
            return JsonResponse({"info": "user not allowed"})
        return JsonResponse(send_data)


@login_required
def delete_message(request,user,  message_id):
    try:
        message = Message.objects.get(id=message_id)
    except Exception as e:
        return JsonResponse({"info": "the message doen't exist" })
    else:
        if message.receiver == user or message.sender == user:
            message.move_to_trash()
            message.save()
            return JsonResponse({"info": "message delete"})
        else:
            return JsonResponse({"info": "user not allowed"})

# @csrf_exempt
# def create_message_view(request):
#     try:
#         #sender=request.POST["sender"]
#         sender = json.loads(request.body.decode("utf-8"))["sender"]
#         receiver = json.loads(request.body.decode("utf-8"))["receiver"]
#         subject = json.loads(request.body.decode("utf-8"))["subject"]
#         message = json.loads(request.body.decode("utf-8"))["message"]
#
#         message = Message.objects.create(sender=sender, receiver=receiver, message=message, subject=subject,
#                                                       creation_date=datetime.datetime.now())
#
#         if message == None:
#             send_data = {"info": "message could not be sent"}
#         else:
#             send_data = {"info": "message was sent"}
#
#         return JsonResponse(send_data)
#
#     except Exception as e:
#          send_data = {"info": "error has occurred",
#                       "error": e.args}
#     return JsonResponse(send_data)
"""