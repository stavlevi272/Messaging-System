from django.urls import path
from message import views

# URLConf
urlpatterns = [
    path('write_message/', views.write_message, name='write_message'),
    path('messages/all', views.get_all_messages, name='get_all_messages'),
    path('messages/<int:message_id>', views.get_message_by_id, name='get_message_by_id'),
    path('messages/<int:message_id>/delete', views.mark_message_as_deleted_by_id, name='mark_message_as_deleted_by_id'),
    path('messages/unread', views.get_all_unread_messages, name='get_all_unread_messages'),
]