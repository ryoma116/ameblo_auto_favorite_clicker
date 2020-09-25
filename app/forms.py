from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator


class IndexForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control' # bootstrapを使用するため
            field.widget.attrs['placeholder'] = field.label

    username = forms.CharField(label='ユーザー名')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput(), min_length=8)


class SetupForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            field.widget.attrs['placeholder'] = field.label

    url = forms.CharField(label='属性が近いユーザのURL')

    max_like_count = forms.IntegerField(label='いいねする数', validators=[MinValueValidator(1)])
