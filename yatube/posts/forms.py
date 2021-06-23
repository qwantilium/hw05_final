from .models import Post, Comment
from django.forms import ModelForm, Textarea
from django.utils.translation import gettext_lazy as _


class PostForm(ModelForm):
    class Meta:
        model = Post
        fields = ['text', 'group', 'image']
        labels = {
            'text': _('Какой-то текст'),
            'group': _('Выбери группу'),
            'image': _('Вставьте картинку')
        }
        help_texts = {
            'text': _('Есть идеи? Пиши'),
            'group': _('Кто ты?'),
            'image': _('Выберите картинку')
        }
        widgets = {
            'text': Textarea(attrs={'class': 'form-control',
                                    'placeholder': 'Введите текст'}),
        }
        error_massages = {'text': {'required': _('Заполните поле')}}


class CommentForm(ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        labels = {
            'comment': _('Какой-то текст к посту'),

        }
        help_texts = {
            'comment': _('О, интересный пост? Пиши'),

        }
        widgets = {
            'comment': Textarea(attrs={'cols': 80,
                                       'row': 5}),
        }
