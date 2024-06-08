from django.contrib.admin.widgets import FilteredSelectMultiple
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django import forms
from django_select2.forms import Select2MultipleWidget

from .models import CustomUser, Section, ArticleText, AuthorInfo, ArticleInfo, ArticleThesis, Consent, TechnicalWork, CommentAttachment


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ("email",)


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ("email",)


class ArticleTextForm(forms.ModelForm):
    class Meta:
        model = ArticleText
        fields = ("article", "file")
        widgets = {
            "file": forms.FileInput(attrs={"accept": ".doc,.docx"})
        }


class ArticleThesisForm(forms.ModelForm):
    class Meta:
        model = ArticleThesis
        fields = ("article", "file")
        widgets = {
            "file": forms.FileInput(attrs={"accept": ".doc,.docx"})
        }


class ConsentForm(forms.ModelForm):
    class Meta:
        model = Consent
        fields = ("user", "file")
        widgets = {
            "file": forms.FileInput(attrs={"accept": ".pdf"})
        }


class TechnicalWorkForm(forms.ModelForm):
    class Meta:
        model = TechnicalWork
        fields = ("start", "end")
        widgets = {
            "start": forms.DateTimeField(input_formats=["%d.%m.%Y %H:%M", "%d-%m-%Y"]),
            "end": forms.DateTimeField(input_formats=["%d.%m.%Y %H:%M", "%d-%m-%Y"])
        }


class AuthorInfoForm(forms.Form):
    """Форма для добавления доп. информации об авторе."""
    class Meta:
        model = AuthorInfo
        fields = ("user", "first_name_translation", "last_name_translation",
                  "country", "city", "institution", "department", "department_group",
                  "major", "level", "course", "education_group"
                  )
        widgets = {
            "first_name_translation": forms.CharField(max_length=64, label="Имя на английском языке", label_suffix=":", required=False),
            "last_name_translation": forms.CharField(max_length=64, label="Фамилия на английском языке", label_suffix=":", required=False),
            "country": forms.CharField(max_length=64, label="Страна проживания", initial="Россия", label_suffix=":", required=False),
            "city": forms.CharField(max_length=64, label="Город", initial="Владивосток", label_suffix=":", required=False),
            "institution": forms.CharField(label="Учебное заведение", initial="ДВФУ", label_suffix=":", required=False),
            "department": forms.CharField(label="Подразделение", initial="ШИГН", label_suffix=":", required=False),
            "department_group": forms.CharField(label="Департамент", label_suffix=":", required=False),
            "major": forms.CharField(label="Направление / факультет", label_suffix=":", required=False),
            "level": forms.CharField(max_length=24, label="Уровень образования", initial="Бакалавр", label_suffix=":", required=False),
            "course": forms.IntegerField(min_value=1, label="Курс", label_suffix=":", required=False),
            "education_group": forms.CharField(label="Учебная группа", label_suffix=":", required=False),
        }


class FilterArticleForm(forms.Form):
    """Форма для страницы продвинутого поиска."""
    title = forms.CharField(
        label="Тема",
        label_suffix=":",
        required=False
    )
    keywords__icontains = forms.CharField(label="Ключевые слова", label_suffix=":", required=False)

    title_translation = forms.CharField(label="Тема на английском языке", label_suffix=":", required=False)
    keywords_translation__icontains = forms.CharField(label="Ключевые слова на английском языке", label_suffix=":", required=False)

    section__in = forms.ModelMultipleChoiceField(
        queryset=Section.objects.all(),
        widget=FilteredSelectMultiple("Секция", is_stacked=False),
        required=False,
        label="Секция"
    )

    is_complete = forms.ChoiceField(choices=((None, "Все"), (True, "Да"), (False, "Нет")),
                                 initial=(None, "Все"), label="Принята к публикации", label_suffix=":", required=False)

    is_participation_confirmed = forms.ChoiceField(choices=((None, "Все"), (True, "Да"), (False, "Нет")),
                                  initial=(None, "Все"), label="Участие подтверждено", label_suffix=":", required=False)
    is_winner = forms.ChoiceField(choices=((None, "Все"), (True, "Да"), (False, "Нет")),
                               initial=(None, "Все"), label="Призёр", label_suffix=":", required=False)

    authors__in = forms.ModelMultipleChoiceField(
        queryset=CustomUser.objects.filter(is_staff=False),
        required=False,
        label="Авторы"
    )

    city__icontains = forms.CharField(label="Город", label_suffix=":", max_length=64, required=False)
    institution__icontains = forms.CharField(label="Учебное заведение", label_suffix=":", required=False)
    department__icontains = forms.CharField(label="Подразделение", label_suffix=":", required=False)

    major__icontains = forms.CharField(label="Направление / факультет", label_suffix=":", required=False)
    level__icontains = forms.CharField(label="Уровень образования", label_suffix=":", max_length=24, required=False)
    course = forms.IntegerField(label="Курс", label_suffix=":", min_value=1, required=False)

    adviser_first_name = forms.CharField(label="Имя научного руководителя", label_suffix=":", max_length=64, required=False)
    adviser_middle_name = forms.CharField(label="Отчество научного руководителя", label_suffix=":", max_length=64, required=False)
    adviser_last_name = forms.CharField(label="Фамилия научного руководителя", label_suffix=":", max_length=64, required=False)
    adviser_first_name_translation = forms.CharField(label="Имя научного руководителя на английском языке", label_suffix=":", max_length=64, required=False)
    adviser_last_name_translation = forms.CharField(label="Фамилия научного руководителя на английском языке", label_suffix=":", max_length=64, required=False)
    adviser_degree__icontains = forms.CharField(label="Учёная степень научного руководителя", label_suffix=":", max_length=64, required=False)


class SectionSelect2Form(forms.ModelForm):
    section = forms.ModelChoiceField(
        queryset=Section.objects.all()
    )

    class Meta:
        model = ArticleInfo
        fields = ("section", "authors")


class EmailChangeForm(forms.Form):
    error_messages = {
        'email_mismatch': "Введённые адреса электронной почты не совпадают.",
        'not_changed': "Указан такой же адрес электронной почты, как у вас сейчас."
    }

    new_email1 = forms.EmailField(
        label="Новый адрес электронной почты",
        widget=forms.EmailInput,
    )

    new_email2 = forms.EmailField(
        label="Подтверждение нового адреса электронной почты",
        widget=forms.EmailInput,
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EmailChangeForm, self).__init__(*args, **kwargs)

    def clean_new_email1(self):
        old_email = self.user.email
        new_email1 = self.cleaned_data.get('new_email1')
        if new_email1 and old_email:
            if new_email1 == old_email:
                raise forms.ValidationError(
                    self.error_messages['not_changed'],
                    code='not_changed',
                )
        return new_email1

    def clean_new_email2(self):
        new_email1 = self.cleaned_data.get('new_email1')
        new_email2 = self.cleaned_data.get('new_email2')
        if new_email1 and new_email2:
            if new_email1 != new_email2:
                raise forms.ValidationError(
                    self.error_messages['email_mismatch'],
                    code='email_mismatch',
                )
        return new_email2

    def save(self, commit=True):
        email = self.cleaned_data["new_email1"]
        self.user.email = email
        if commit:
            self.user.save()
        return self.user


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class LimitedMultipleFileInput(forms.FileField):
    def __init__(self, max_files=5, *args, **kwargs):
        self.max_files = max_files
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            if len(data) > self.max_files:
                raise forms.ValidationError(f"Можно прикрепить до {self.max_files} вложений.")
            result = [single_file_clean(item, initial) for item in data]
        else:
            result = single_file_clean(data, initial)
        return result


# class CommentAttachmentForm(forms.ModelForm):
#     class Meta:
#         model = CommentAttachment
#         fields = ('file', )

class CommentAttachmentForm(forms.Form):
    """Форма для отправки комментария авторам доклада с возможностью прикрепить вложения."""
    text = forms.CharField(
        widget=forms.Textarea(attrs={"rows": "5"}),
        label="Комментарий",
        label_suffix=":",
        required=True
    )

    files = LimitedMultipleFileInput(
        label="При желании вы можете прикрепить к комментарию до 5 файлов",
        label_suffix=":",
        required=False
    )
