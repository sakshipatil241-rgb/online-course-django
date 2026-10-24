from django.core.management.base import BaseCommand

from courses.models import Course, Instructor, Lesson


class Command(BaseCommand):
    help = 'Populate the database with sample online course content.'

    def handle(self, *args, **options):
        instructor, _ = Instructor.objects.get_or_create(
            name='Ariana Wells',
            defaults={
                'title': 'Senior Product Instructor',
                'bio': 'Designs practical learning paths for modern digital careers.',
            },
        )

        course, created = Course.objects.get_or_create(
            slug='django-for-beginners',
            defaults={
                'title': 'Django for Beginners',
                'short_description': 'Learn to build and deploy full-stack web apps with Django.',
                'description': 'Create professional web projects using Django models, templates, routing, and deployment best practices.',
                'category': 'Web Development',
                'level': 'Beginner',
                'duration': '6 weeks',
                'price': 49.00,
                'featured': True,
                'instructor': instructor,
                'published': True,
            },
        )

        if created:
            Lesson.objects.get_or_create(course=course, title='Project setup', order=1, defaults={'content': 'Install Django, create your project, and configure the settings for your first application.'})
            Lesson.objects.get_or_create(course=course, title='Building models', order=2, defaults={'content': 'Define your app models, database tables, and validation rules.'})
            Lesson.objects.get_or_create(course=course, title='Templates and views', order=3, defaults={'content': 'Connect your views to templates and build dynamic pages for students.'})
            Lesson.objects.get_or_create(course=course, title='Deploying your app', order=4, defaults={'content': 'Prepare the app for production with secure settings and deployment checks.'})

        self.stdout.write(self.style.SUCCESS('Course data seed complete.'))
