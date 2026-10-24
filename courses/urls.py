from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('exam/', views.mock_exam, name='mock_exam'),
    path('exam/submit/', views.submit, name='submit'),
    path('exam/result/', views.show_exam_result, name='show_exam_result'),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('courses/<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
]
