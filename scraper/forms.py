from django import forms

class KeywordForm(forms.Form):
    keywords = forms.CharField(max_length=100)
    duration = forms.IntegerField(min_value=1, max_value=120, initial=10, help_text='Enter the duration in minutes (1-120)')
