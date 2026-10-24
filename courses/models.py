from django.conf import settings
from django.db import models
from django.urls import reverse


class Instructor(models.Model):
    name = models.CharField(max_length=120)
    title = models.CharField(max_length=120)
    bio = models.TextField(blank=True)
    image_url = models.URLField(blank=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    CATEGORY_CHOICES = [
        ('Web Development', 'Web Development'),
        ('Data Science', 'Data Science'),
        ('Design', 'Design'),
        ('Business', 'Business'),
        ('Marketing', 'Marketing'),
    ]
    LEVEL_CHOICES = [
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    short_description = models.CharField(max_length=255)
    description = models.TextField()
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default='Web Development')
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES, default='Beginner')
    duration = models.CharField(max_length=40, default='4 weeks')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    featured = models.BooleanField(default=False)
    published = models.BooleanField(default=True)
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='courses')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-featured', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('course_detail', kwargs={'slug': self.slug})


class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=1)
    duration = models.CharField(max_length=40, default='10 min')
    content = models.TextField()

    class Meta:
        ordering = ['order']
        unique_together = ('course', 'order')

    def __str__(self):
        return f'{self.course.title} - {self.title}'


class Enrollment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-enrolled_at']

    def __str__(self):
        return f'{self.user} enrolled in {self.course}'


class Question(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='questions')
    question_text = models.TextField()
    grade = models.IntegerField(default=1)

    def __str__(self):
        return self.question_text

    def is_get_score(self):
        return self.grade if self.choices.filter(is_correct=True).exists() else 0


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
    choice_text = models.CharField(max_length=100)
    is_correct = models.BooleanField(default=False)

    def __str__(self):
        return self.choice_text


class Submission(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='submissions')
    choices = models.ManyToManyField(Choice, related_name='submissions')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.enrollment.user} - {self.enrollment.course}'

    def get_score(self):
        score = 0
        questions = self.enrollment.course.questions.prefetch_related('choices')
        for question in questions:
            correct_choices = set(question.choices.filter(is_correct=True).values_list('pk', flat=True))
            selected_choices = set(
                self.choices.filter(question=question).values_list('pk', flat=True)
            )
            if correct_choices and selected_choices == correct_choices:
                score += question.is_get_score()
        return score
