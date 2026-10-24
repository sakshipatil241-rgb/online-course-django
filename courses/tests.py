from django.test import TestCase

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
