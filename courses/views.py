from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .exam_data import EXAM_QUESTIONS
from .forms import ContactForm, MockExamForm
from .models import Course, Enrollment


def mock_exam(request):
    return render(request, 'courses/mock_exam.html', {
        'form': MockExamForm(),
        'question_count': len(EXAM_QUESTIONS),
    })


def submit(request):
    if request.method != 'POST':
        return redirect('mock_exam')

    form = MockExamForm(request.POST)
    if not form.is_valid():
        return render(request, 'courses/mock_exam.html', {
            'form': form,
            'question_count': len(EXAM_QUESTIONS),
        })

    results = []
    score = 0
    for question in EXAM_QUESTIONS:
        selected = form.cleaned_data[question['id']]
        correct = selected == question['answer']
        score += int(correct)
        results.append({
            'question': question['question'],
            'selected': question['options'][selected],
            'correct_answer': question['options'][question['answer']],
            'is_correct': correct,
        })

    request.session['mock_exam_result'] = {
        'score': score,
        'total': len(EXAM_QUESTIONS),
        'answers': results,
    }
    return redirect('show_exam_result')


def show_exam_result(request):
    result = request.session.get('mock_exam_result')
    if result is None:
        messages.info(request, 'Take the mock exam to see your results.')
        return redirect('mock_exam')

    context = {
        **result,
        'passed': result['score'] >= (result['total'] * 0.6),
    }
    return render(request, 'courses/show_exam_result.html', context)


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
