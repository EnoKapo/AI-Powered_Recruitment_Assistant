from django.urls import path
from . import views

urlpatterns = [
    path('', views.index),

    path('api/', views.chat_with_ai),

    path('sessions/', views.get_sessions),
    path('messages/<int:session_id>/', views.get_messages),
    path('delete/<int:session_id>/', views.delete_session),

    # files
    path('session/<int:session_id>/files/', views.get_session_files),
    path('session/file/<int:file_id>/delete/', views.delete_session_file),

    # memory
    path('session/<int:session_id>/memory/', views.get_session_memory),
    path('session/<int:session_id>/memory/save/', views.save_session_memory),
]