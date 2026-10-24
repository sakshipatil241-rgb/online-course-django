EXAM_QUESTIONS = [
    {
        'id': 'question_1',
        'question': 'Which Django file is commonly used to map URL patterns to views?',
        'options': {
            'urls_py': 'urls.py',
            'models_py': 'models.py',
            'admin_py': 'admin.py',
            'tests_py': 'tests.py',
        },
        'answer': 'urls_py',
    },
    {
        'id': 'question_2',
        'question': 'Which Django shortcut retrieves an object or returns a 404 response?',
        'options': {
            'render': 'render()',
            'get_object_or_404': 'get_object_or_404()',
            'redirect': 'redirect()',
            'reverse': 'reverse()',
        },
        'answer': 'get_object_or_404',
    },
    {
        'id': 'question_3',
        'question': 'What is the Django template tag for looping over a collection?',
        'options': {
            'if_tag': '{% if %}',
            'url_tag': '{% url %}',
            'for_tag': '{% for item in items %}',
            'csrf_tag': '{% csrf_token %}',
        },
        'answer': 'for_tag',
    },
    {
        'id': 'question_4',
        'question': 'Which command applies database migrations?',
        'options': {
            'runserver': 'python manage.py runserver',
            'makemigrations': 'python manage.py makemigrations',
            'migrate': 'python manage.py migrate',
            'startapp': 'python manage.py startapp',
        },
        'answer': 'migrate',
    },
    {
        'id': 'question_5',
        'question': 'Which Django feature helps protect POST forms against cross-site request forgery?',
        'options': {
            'csrf_token': '{% csrf_token %}',
            'static_tag': '{% static %}',
            'extends_tag': '{% extends %}',
            'url_tag': '{% url %}',
        },
        'answer': 'csrf_token',
    },
]
