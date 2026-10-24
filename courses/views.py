from django.contrib import messages
from django.shortcuts import get_object_or_404, render

from .forms import ContactForm
from .models import Course, Enrollment


def home(request):
    courses = Course.objects.filter(published=True)
    featured = courses.filter(featured=True).first()
    return render(request, 'courses/home.html', {'courses': courses, 'featured': featured})


def about(request):
    return render(request, 'courses/about.html')


def contact(request):
    form = ContactForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        messages.success(request, 'Thanks for reaching out. We will get back to you soon.')
        form = ContactForm()
    return render(request, 'courses/contact.html', {'form': form})


def course_detail(request, slug):
    course = get_object_or_404(Course, slug=slug, published=True)
    lessons = course.lessons.all()
    return render(request, 'courses/course_details_bootstrap.html', {'course': course, 'lessons': lessons})


def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, published=True)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.info(request, 'Please sign in to enroll in this course.')
            return render(request, 'courses/enroll.html', {'course': course})
        Enrollment.objects.get_or_create(user=request.user, course=course)
        messages.success(request, f'You are now enrolled in {course.title}.')
    return render(request, 'courses/enroll.html', {'course': course})
