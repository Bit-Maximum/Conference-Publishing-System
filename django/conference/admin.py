from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, AuthorInfo, Section, SectionEditor, ArticleInfo, ArticleText, Comment, ArticleThesis, \
    TechnicalWork, CommentAttachment


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser

    list_display = ("email", "is_staff", "is_winner", "is_participation_confirmed", "is_verified", "first_name", "last_name", "middle_name", "is_active")
    list_display_links = ("email", "first_name", "last_name", "middle_name")
    list_filter = ("is_staff", "is_winner", "is_active", "is_verified", "is_participation_confirmed")
    list_editable = ("is_staff", "is_winner", "is_active", "is_verified")
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("is_staff", "is_active", "is_winner", "groups", "user_permissions")}),
        ("Full name", {"fields": ("first_name", "middle_name", "last_name")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email", "password1", "password2", "is_staff",
                "is_active", "groups", "user_permissions"
            )}
         ),
    )
    search_fields = ("email", "last_name")
    ordering = ("email",)


class AuthorInfoAdmin(admin.ModelAdmin):
    list_display = ("first_name_translation", "last_name_translation",
                    "country", "city", "institution", "department", "major", "level", "course")
    list_display_links = ("last_name_translation", "first_name_translation")
    list_filter = ("country", "city", "level", "course")
    search_fields = ("last_name_translation", "first_name_translation")


class SectionAdmin(admin.ModelAdmin):
    list_display = ("open", "content")
    list_display_links = ("content",)
    list_filter = ("open",)
    search_fields = ("content",)
    list_editable = ("open",)


class SectionEditorAdmin(admin.ModelAdmin):
    list_display = ("section_id", "confirmed")
    list_filter = ("confirmed",)
    list_editable = ("confirmed",)


class ArticleInfoAdmin(admin.ModelAdmin):
    list_display = ("title", "is_winner", "title_translation", "abstract", "abstract_translation",
                    "keywords", "keywords_translation", "grant", "section_id",
                    "adviser_first_name", "adviser_middle_name", "adviser_last_name",
                    "adviser_first_name_translation", "adviser_last_name_translation",
                    "adviser_degree", "adviser_job"
                    )
    list_display_links = ("title", "title_translation")
    list_filter = ("is_winner",)
    search_fields = ("title", "is_winner", "adviser_last_name")
    list_editable = ("is_winner",)


class ArticleTextAdmin(admin.ModelAdmin):
    list_display = ("article", "file")


class ArticleThesisAdmin(admin.ModelAdmin):
    list_display = ("article", "file")


class ConsentAdmin(admin.ModelAdmin):
    list_display = ("user", "file", "creation_date")
    list_filter = ("creation_date", "user")


class CommentAdmin(admin.ModelAdmin):
    list_display = ("content", "creation_date",
                    "article_id", "editor_id")
    list_display_links = ("creation_date", "content")
    list_filter = ("creation_date", "editor_id")
    search_fields = ("editor_id",)


class CommentAttachmentAdmin(admin.ModelAdmin):
    list_display = ("comment", "file")
    list_display_links = ("comment",)
    list_filter = ("comment",)
    search_fields = ("comment",)


class TechnicalWorkAdmin(admin.ModelAdmin):
    list_display = ("start", "end", "creation_date")
    list_filter = ("start", "end", "creation_date")
    list_display_links = ("start", "end")


# Register your models here.
admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(AuthorInfo, AuthorInfoAdmin)
admin.site.register(Section, SectionAdmin)
admin.site.register(SectionEditor, SectionEditorAdmin)
admin.site.register(ArticleInfo, ArticleInfoAdmin)
admin.site.register(ArticleText, ArticleTextAdmin)
admin.site.register(ArticleThesis, ArticleThesisAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(CommentAttachment, CommentAttachmentAdmin)
admin.site.register(TechnicalWork, TechnicalWorkAdmin)
