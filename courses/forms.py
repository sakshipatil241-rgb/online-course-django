from django import forms

from .exam_data import EXAM_QUESTIONS


class ContactForm(forms.Form):
    name = forms.CharField(max_length=120, widget=forms.TextInput(attrs={'placeholder': 'Your name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'you@example.com'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'placeholder': 'How can we help you?'}))


class MockExamForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for question in EXAM_QUESTIONS:
            self.fields[question['id']] = forms.ChoiceField(
                label=question['question'],
                choices=[(key, label) for key, label in question['options'].items()],
                widget=forms.RadioSelect,
                required=True,
            )
