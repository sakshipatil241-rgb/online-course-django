from django.test import TestCase
from django.urls import reverse

from .exam_data import EXAM_QUESTIONS
from .models import Course, Instructor, Lesson


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


class MockExamTests(TestCase):
    def test_exam_urls_are_registered(self):
        self.assertEqual(reverse('submit'), '/exam/submit/')
        self.assertEqual(reverse('show_exam_result'), '/exam/result/')
        response = self.client.get(reverse('mock_exam'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Answer all 5 questions')
        self.assertEqual(self.client.get(reverse('submit')).status_code, 302)
        self.assertEqual(self.client.get(reverse('show_exam_result')).status_code, 302)

    def test_successful_submission_shows_score_and_all_answers(self):
        answers = {
            question['id']: question['answer']
            for question in EXAM_QUESTIONS
        }

        response = self.client.post(reverse('submit'), answers, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/show_exam_result.html')
        self.assertContains(response, 'Congratulations!')
        self.assertContains(response, f'{len(EXAM_QUESTIONS)} / {len(EXAM_QUESTIONS)}')
        self.assertContains(response, 'Exam results')
        for question in EXAM_QUESTIONS:
            self.assertContains(response, question['question'])

    def test_incomplete_exam_is_not_scored(self):
        response = self.client.post(reverse('submit'), {}, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'courses/mock_exam.html')
        self.assertNotIn('mock_exam_result', self.client.session)
