from django.urls import path
from message import views

# URLConf
urlpatterns = [
    path('write_message/', views.write_message, name='write_message'),
    # #path('create_message_view/', views.create_message_view, name='create_message_view'),
    # path('messages/<str:user>', views.all_messages, name='all_messages'),
    # path('messages/<str:user>/<str:message_id>', views.all_messages, name='all_messages'),
    # #path('all_messages/<str:user>', views.all_messages, name='all_messages'),
    # path('all_unread_messages/<str:user>', views.all_unread_messages, name='all_unread_messages'),
    # #path('read_message/<str:user>/<str:message_id>', views.read_message, name='read_message'),
    # path('delete_message/<str:user>/<str:message_id>', views.delete_message, name='all_unread_messages'),
    path('messages/all', views.get_all_messages, name='get_all_messages'),
    path('messages/<int:message_id>', views.get_message_by_id, name='get_message_by_id'),
    path('messages/<int:message_id>/delete', views.mark_message_as_deleted_by_id, name='mark_message_as_deleted_by_id'),
    path('messages/unread', views.get_all_unread_messages, name='get_all_unread_messages'),
]