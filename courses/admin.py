from django.contrib import admin

from .models import Course, Lesson, Instructor, Learner, Question, Choice, Submission
from .models import Enrollment


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2


@admin.register(Instructor)
class InstructorAdmin(admin.ModelAdmin):
    list_display = ('name', 'title')
    search_fields = ('name', 'title')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'level', 'price', 'featured', 'published')
    list_filter = ('category', 'level', 'featured', 'published')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'short_description')
    inlines = (QuestionInline,)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('course', 'title', 'order')
    search_fields = ('title', 'course__title')


@admin.register(Learner)
class LearnerAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'user__email')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'course', 'enrolled_at', 'completed')
    list_filter = ('completed',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('question_text', 'course', 'grade')
    list_filter = ('course',)
    search_fields = ('question_text',)
    inlines = (ChoiceInline,)


@admin.register(Choice)
class ChoiceAdmin(admin.ModelAdmin):
    list_display = ('choice_text', 'question', 'is_correct')
    list_filter = ('is_correct',)
    search_fields = ('choice_text', 'question__question_text')


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ('enrollment', 'submitted_at')
    list_filter = ('enrollment__course',)
