from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import *
from .forms import *
#класс позволяет создать форму связанную с моделью
class AddPostForm(forms.ModelForm):
    # конструктор формы позволит вызвать конструктор базового класса ModelForm
    # для поля cat выставим отображение пустого поля
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['cat'].empty_label = "Категория не выбрана"
#для взаимодействия с данными модели используем класс Meta
    class Meta:
        #связь формы с моделью
        model = News
        #указываем поля которые будем использовать в форме (кроме автоматических)
        fields = ['title', 'slug', 'content', 'is_published', 'cat']
        #виджет позволяет использовать свои стили для отдельных полей
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input'}),
            'content': forms.Textarea(attrs={'cols': 60, 'rows': 10})
        }
    #валидация введенных данных пользовательским валидатором clean_проверяемое поле
    def clean_title(self):
        title = self.cleaned_data['title']
        if len(title) > 200:
            raise ValidationError('Длина превышает 200 символов')
        return title

#форма для регистрации пользователя на основе базового класса UserCreationForm
class RegisterUserForm(UserCreationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    email = forms.EmailField(label='Email', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    password2 = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput(attrs={'class': 'form-input'}))
    class Meta:
        #используем стандартную модель user
        model = User
        fields = ('username', 'email', 'password1', 'password2')

#форма для логирования
class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label='Логин', widget=forms.TextInput(attrs={'class': 'form-input'}))
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput(attrs={'class': 'form-input'}))

#форма обратной связи
class ContactForm(forms.Form):
    name = forms.CharField(label='Имя', max_length=255)
    email = forms.EmailField(label='Email')
    content = forms.CharField(
        label='Отзыв',  # Используйте label для задания текста метки
        widget=forms.Textarea(attrs={'cols': 21, 'rows': 10})
    )