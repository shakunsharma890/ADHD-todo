from django.urls import path
from . views import *

urlpatterns = [
    path('dashboard/', dashboard, name='dashboard'),
    path('tasks/', tasks, name='tasks'),
    path('focus_timer/', focus_timer, name='focus_timer'),
    path('stats/', stats, name='stats'),
    path("dashboard-filter/",dashboard_filter,name="dashboard_filter"),
    path('complete-task/<int:task_id>/',complete_task,name='complete_task'),
    path('delete-task/<int:task_id>/',delete_task,name='delete_task'),
    path('edit-task/<int:task_id>/', edit_task, name='edit_task'),
    path('save-focus-session/', save_focus_session, name='save_focus_session'),
    path('settings/', settings_view, name='settings'),
    path('about/', about, name='about'),
    path('summary/',summary, name='summary'),
    path("change-password/",change_password,name="change_password"),
]