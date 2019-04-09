from django import forms


class ProblemListSearchForm(forms.Form):
    search = forms.CharField(label="搜索", widget=forms.TextInput)
