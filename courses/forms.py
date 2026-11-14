from django import forms

from .models import Course, Lesson, Question


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ("title", "description", "price")
        widgets = {"description": forms.Textarea(attrs={"rows": 6})}


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ("title", "order", "content", "video_url")
        widgets = {"content": forms.Textarea(attrs={"rows": 10})}


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ("text",)
        labels = {"text": "Your question"}
        widgets = {"text": forms.Textarea(attrs={"rows": 3})}


class AnswerForm(forms.Form):
    answer = forms.CharField(widget=forms.Textarea(attrs={"rows": 3}), label="Your answer")
