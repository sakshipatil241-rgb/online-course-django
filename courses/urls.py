from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('exam/', views.mock_exam, name='mock_exam'),
    path('exam/submit/', views.submit_mock_exam, name='mock_submit'),
    path('exam/result/', views.show_mock_exam_result, name='mock_exam_result'),
    path('courses/<int:course_id>/exam/', views.course_exam, name='course_exam'),
    path('courses/<int:course_id>/submit/', views.submit, name='submit'),
    path(
        'course/<int:course_id>/submission/<int:submission_id>/result/',
        views.show_exam_result,
        name='show_exam_result',
    ),
    path('courses/<slug:slug>/', views.course_detail, name='course_detail'),
    path('courses/<slug:slug>/enroll/', views.enroll_course, name='enroll_course'),
]
