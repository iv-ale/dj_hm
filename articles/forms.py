from django import forms

from .models import Article, Feedback


def add_bootstrap(form: forms.BaseForm) -> None:
    """Добавляет классы Bootstrap ко всем полям формы (урок 50, челлендж)."""

    for field in form.fields.values():
        # В Bootstrap 5 у <select> класс form-select, у остальных — form-control.
        default = (
            'form-select'
            if isinstance(field.widget, forms.Select)
            else 'form-control'
        )
        field.widget.attrs.setdefault('class', default)


class ArticleForm(forms.ModelForm):
    """Форма создания и редактирования статьи (урок 50, уровень 2)."""

    class Meta:
        model = Article
        fields = ['title', 'text', 'category']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap(self)

    def clean_title(self):
        """Заголовок не короче 5 символов — ошибки выводятся под полем."""
        title = self.cleaned_data['title']
        if len(title) < 5:
            raise forms.ValidationError(
                'Заголовок должен быть не короче 5 символов.'
            )
        return title


class FeedbackForm(forms.Form):
    """Обычная форма обратной связи: имя, email, сообщение."""

    name = forms.CharField(label='Имя', max_length=100)
    email = forms.EmailField(label='Email')
    message = forms.CharField(
        label='Сообщение',
        widget=forms.Textarea(attrs={'rows': 5}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        add_bootstrap(self)

    def save(self) -> Feedback:
        """Сохраняет сообщение в модель Feedback."""
        return Feedback.objects.create(**self.cleaned_data)
