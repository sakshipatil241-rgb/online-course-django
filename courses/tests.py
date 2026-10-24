from django.contrib.auth import get_user_model
from django.contrib import admin
from django.test import TestCase
from django.urls import reverse

from . import admin as course_admin
from .exam_data import EXAM_QUESTIONS
from .models import Choice, Course, Enrollment, Instructor, Learner, Lesson, Question, Submission


class CourseModelTests(TestCase):
    def setUp(self):
        instructor = Instructor.objects.create(
            name='Test Instructor',
            title='Python Mentor',
            bio='Helps developers grow in confidence and skill.',
        )
        self.course = Course.objects.create(
            title='Test Course',
            slug='test-course',
            short_description='A short description.',
            description='A longer description for the course.',
            category='Web Development',
            level='Beginner',
            duration='4 weeks',
            price=29.99,
            instructor=instructor,
            published=True,
        )
        Lesson.objects.create(course=self.course, title='Intro', order=1, content='Welcome to the course.')

    def test_course_slug_url(self):
        self.assertEqual(self.course.get_absolute_url(), '/courses/test-course/')

    def test_course_has_lesson(self):
        self.assertEqual(self.course.lessons.count(), 1)

    def test_course_detail_displays_course_and_all_lessons(self):
        Lesson.objects.create(
            course=self.course,
            title='Next steps',
            order=2,
            content='Build your first project.',
        )

        response = self.client.get(self.course.get_absolute_url())

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/course_details_bootstrap.html')
        self.assertContains(response, 'Test Course')
        self.assertContains(response, 'Intro')
        self.assertContains(response, 'Next steps')
        self.assertContains(response, 'bootstrap@5.3.3')


class ExamModelTests(TestCase):
    def setUp(self):
        instructor = Instructor.objects.create(name='Exam Instructor', title='Teacher')
        self.course = Course.objects.create(
            title='Exam Course',
            slug='exam-course',
            short_description='Exam course.',
            description='Course for question and submission tests.',
            instructor=instructor,
        )
        self.user = get_user_model().objects.create_user(username='exam_student', password='test-password')
        self.enrollment = Enrollment.objects.create(user=self.user, course=self.course)
        self.question = Question.objects.create(
            course=self.course,
            question_text='Which answer is correct?',
            grade=3,
        )
        self.correct_choice = Choice.objects.create(
            question=self.question,
            choice_text='Correct answer',
            is_correct=True,
        )
        self.incorrect_choice = Choice.objects.create(
            question=self.question,
            choice_text='Incorrect answer',
        )

    def test_question_returns_its_grade_when_it_has_a_correct_choice(self):
        self.assertEqual(self.question.is_get_score(), 3)

    def test_question_without_a_correct_choice_has_no_score(self):
        self.correct_choice.delete()
        self.assertEqual(self.question.is_get_score(), 0)

    def test_submission_scores_exact_correct_answers(self):
        submission = Submission.objects.create(enrollment=self.enrollment)
        submission.choices.add(self.correct_choice)

        self.assertEqual(submission.get_score(), 3)

    def test_submission_does_not_score_incorrect_or_incomplete_answers(self):
        submission = Submission.objects.create(enrollment=self.enrollment)
        submission.choices.add(self.incorrect_choice)

        self.assertEqual(submission.get_score(), 0)

    def test_submission_string_representation(self):
        submission = Submission.objects.create(enrollment=self.enrollment)

        self.assertEqual(str(submission), 'exam_student - Exam Course')

    def test_learner_string_representation(self):
        learner = Learner.objects.create(user=self.user)

        self.assertEqual(str(learner), 'exam_student')


class MockExamTests(TestCase):
    def test_exam_urls_are_registered(self):
        self.assertEqual(reverse('submit', args=[7]), '/courses/7/submit/')
        self.assertEqual(
            reverse('show_exam_result', args=[7, 12]),
            '/course/7/submission/12/result/',
        )
        response = self.client.get(reverse('mock_exam'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Answer all 5 questions')
        self.assertEqual(self.client.get(reverse('mock_submit')).status_code, 302)
        self.assertEqual(self.client.get(reverse('mock_exam_result')).status_code, 302)

    def test_successful_submission_shows_score_and_all_answers(self):
        answers = {
            question['id']: question['answer']
            for question in EXAM_QUESTIONS
        }

        response = self.client.post(reverse('mock_submit'), answers, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/show_exam_result.html')
        self.assertContains(response, 'Congratulations!')
        self.assertContains(response, f'{len(EXAM_QUESTIONS)} / {len(EXAM_QUESTIONS)}')
        self.assertContains(response, 'Exam results')
        for question in EXAM_QUESTIONS:
            self.assertContains(response, question['question'])

    def test_incomplete_exam_is_not_scored(self):
        response = self.client.post(reverse('mock_submit'), {}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/mock_exam.html')
        self.assertNotIn('mock_exam_result', self.client.session)


class CourseExamViewTests(TestCase):
    def setUp(self):
        instructor = Instructor.objects.create(name='Exam Instructor', title='Teacher')
        self.course = Course.objects.create(
            title='Route Exam Course',
            slug='route-exam-course',
            short_description='Exam course.',
            description='Course for route tests.',
            instructor=instructor,
        )
        self.user = get_user_model().objects.create_user(username='route_student', password='test-password')
        self.enrollment = Enrollment.objects.create(user=self.user, course=self.course)
        question = Question.objects.create(
            course=self.course,
            question_text='Select the correct answer.',
            grade=3,
        )
        self.correct_choice = Choice.objects.create(
            question=question,
            choice_text='Correct',
            is_correct=True,
        )
        Choice.objects.create(question=question, choice_text='Incorrect')
        self.client.force_login(self.user)

    def test_course_submit_route_creates_submission_and_redirects_to_result(self):
        submit_url = reverse('submit', args=[self.course.pk])
        response = self.client.post(submit_url, {
            f'question_{self.correct_choice.question_id}': [self.correct_choice.pk],
        })

        submission = Submission.objects.get(enrollment=self.enrollment)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            response.url,
            reverse('show_exam_result', args=[self.course.pk, submission.pk]),
        )
        self.assertEqual(list(submission.choices.all()), [self.correct_choice])

    def test_result_route_displays_score_and_rejects_other_users(self):
        submission = Submission.objects.create(enrollment=self.enrollment)
        submission.choices.add(self.correct_choice)

        response = self.client.get(reverse('show_exam_result', args=[self.course.pk, submission.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '3 / 3')
        self.assertContains(response, 'Select the correct answer.')
        self.assertContains(response, 'Congratulations!')

        other_user = get_user_model().objects.create_user(username='other_student', password='test-password')
        self.client.force_login(other_user)
        self.assertEqual(
            self.client.get(reverse('show_exam_result', args=[self.course.pk, submission.pk])).status_code,
            404,
        )

    def test_course_exam_page_requires_enrollment(self):
        self.assertEqual(self.client.get(reverse('course_exam', args=[self.course.pk])).status_code, 200)

        self.enrollment.delete()
        response = self.client.get(reverse('course_exam', args=[self.course.pk]))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('course_detail', args=[self.course.slug]))


class CourseAdminTests(TestCase):
    def test_question_and_choice_inlines_are_attached_to_admins(self):
        self.assertEqual(course_admin.QuestionInline.model, Question)
        self.assertEqual(course_admin.ChoiceInline.model, Choice)
        self.assertIn(course_admin.QuestionInline, course_admin.CourseAdmin.inlines)
        self.assertIn(course_admin.ChoiceInline, course_admin.QuestionAdmin.inlines)

    def test_required_models_are_registered(self):
        for model in (Course, Lesson, Instructor, Learner, Question, Choice, Submission):
            with self.subTest(model=model.__name__):
                self.assertIn(model, admin.site._registry)

    def test_lesson_admin_lists_lessons_by_course_and_order(self):
        self.assertEqual(course_admin.LessonAdmin.list_display, ('course', 'title', 'order'))
        self.assertEqual(course_admin.LessonAdmin.search_fields, ('title', 'course__title'))
