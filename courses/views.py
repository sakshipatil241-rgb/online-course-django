from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render

from .exam_data import EXAM_QUESTIONS
from .forms import ContactForm, CourseExamForm, MockExamForm
from .models import Course, Enrollment, Submission


def mock_exam(request):
    return render(request, 'courses/mock_exam.html', {
        'form': MockExamForm(),
        'question_count': len(EXAM_QUESTIONS),
    })


def course_exam(request, course_id):
    course = get_object_or_404(Course, pk=course_id, published=True)
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in and enroll to take this course exam.')
        return redirect('course_detail', slug=course.slug)

    enrollment = Enrollment.objects.filter(user=request.user, course=course).first()
    if enrollment is None:
        messages.info(request, 'Enroll in this course before taking its exam.')
        return redirect('course_detail', slug=course.slug)

    questions = course.questions.prefetch_related('choices')
    form = CourseExamForm(request.POST or None, questions=questions)
    if not questions.exists():
        messages.info(request, 'This course does not have an exam yet.')
        return redirect('course_detail', slug=course.slug)

    return render(request, 'courses/course_exam.html', {
        'course': course,
        'form': form,
        'question_count': questions.count(),
    })


def submit(request, course_id):
    if request.method != 'POST':
        return redirect('course_exam', course_id=course_id)

    course = get_object_or_404(Course, pk=course_id, published=True)
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in and enroll to submit this exam.')
        return redirect('course_detail', slug=course.slug)
    enrollment = get_object_or_404(Enrollment, user=request.user, course=course)
    questions = list(course.questions.prefetch_related('choices'))
    if not questions:
        messages.info(request, 'This course does not have an exam yet.')
        return redirect('course_detail', slug=course.slug)

    form = CourseExamForm(request.POST, questions=questions)
    if not form.is_valid():
        return render(request, 'courses/course_exam.html', {
            'course': course,
            'form': form,
            'question_count': len(questions),
        })

    submission = Submission.objects.create(enrollment=enrollment)
    for question in questions:
        submission.choices.add(*form.cleaned_data[f'question_{question.pk}'])
    return redirect(
        'show_exam_result',
        course_id=course.pk,
        submission_id=submission.pk,
    )


def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    if not request.user.is_authenticated:
        messages.info(request, 'Please sign in to view your exam result.')
        return redirect('course_detail', slug=course.slug)

    submission = get_object_or_404(
        Submission.objects.prefetch_related('choices', 'enrollment__course__questions__choices'),
        pk=submission_id,
        enrollment__course=course,
        enrollment__user=request.user,
    )
    questions = course.questions.prefetch_related('choices')
    answers = []
    total = 0
    for question in questions:
        correct_choices = set(question.choices.filter(is_correct=True).values_list('pk', flat=True))
        selected_choices = set(
            submission.choices.filter(question=question).values_list('pk', flat=True)
        )
        is_correct = bool(correct_choices) and selected_choices == correct_choices
        total += question.grade
        answers.append({
            'question': question.question_text,
            'selected': list(
                submission.choices.filter(question=question).values_list('choice_text', flat=True)
            ),
            'correct_answer': list(
                question.choices.filter(is_correct=True).values_list('choice_text', flat=True)
            ),
            'is_correct': is_correct,
        })
    score = submission.get_score()
    context = {
        'course': course,
        'score': score,
        'total': total,
        'answers': answers,
        'passed': total > 0 and score >= total * 0.6,
    }
    return render(request, 'courses/show_exam_result.html', context)


def submit_mock_exam(request):
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
    return redirect('mock_exam_result')


def show_mock_exam_result(request):
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
    is_enrolled = (
        request.user.is_authenticated
        and Enrollment.objects.filter(user=request.user, course=course).exists()
    )
    return render(request, 'courses/course_details_bootstrap.html', {
        'course': course,
        'lessons': lessons,
        'is_enrolled': is_enrolled,
    })


def enroll_course(request, slug):
    course = get_object_or_404(Course, slug=slug, published=True)
    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.info(request, 'Please sign in to enroll in this course.')
            return render(request, 'courses/enroll.html', {'course': course})
        Enrollment.objects.get_or_create(user=request.user, course=course)
        messages.success(request, f'You are now enrolled in {course.title}.')
    return render(request, 'courses/enroll.html', {'course': course})
