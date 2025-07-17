from django.urls import path
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

from . import views


urlpatterns = [
    # path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("secondary", views.register_secondary, name="secondary"),
    path("third", views.register_third, name="third"),
    path("staff", views.register_staff, name="staff"),

    path("profile", views.profile, name="profile"),
    path("article/<int:article_id>", views.article, name="article"),
    path("article/<int:article_id>/<str:need_check>", views.article, name="article"),
    path("library", views.library, name="library"),
    path("join", views.join_view, name="join"),
    path("comment/<int:article_id>", views.comment, name="comment"),

    path("download_text/<int:article_id>", views.download_article_text, name="download_text"),
    path("download_thesis/<int:article_id>", views.download_article_thesis, name="download_thesis"),
    path("download_consent/<int:user_id>", views.download_consent, name="download_consent"),
    path("download_attachment/<int:attachment_id>", views.download_attachment, name="download_attachment"),
    path("delete_text/<int:article_id>", views.delete_article_text, name="delete_text"),
    path("delete_thesis/<int:article_id>", views.delete_article_thesis, name="delete_thesis"),
    path("delete_consent/<int:user_id>", views.delete_consent, name="delete_consent"),
    path("add_thesis/<int:article_id>", views.add_article_thesis, name="add_thesis"),

    path("add_consent/<int:user_id>", views.add_consent, name="add_consent"),
    path("participation", views.confirm_participation, name="confirm_participation"),

    path("add_source/<int:article_id>", views.add_source, name="add_source"),
    path("delete_source/<int:source_id>", views.delete_source, name="delete_source"),
    path("edit_authorship/<int:article_id>", views.edit_authorship, name="edit_authorship"),

    # API Routes
    path('find_user', views.find_user, name="find_user"),
    path('get_text/<int:article_id>', views.get_text, name="get_text"),
    path("edit_general_info", views.edit_general_info, name="edit_general_info"),
    path("edit_secondary_info", views.edit_secondary_info, name="edit_secondary_info"),
    path("edit_section_info", views.edit_section_info, name="edit_section_info"),
    path("edit_article_info", views.edit_article_info, name="edit_article_info"),

    path('check_article_exists', views.check_article_exists, name="check_article_exists"),
    path("register_article", views.register_article, name="register_article"),
    path('join_article', views.join_article, name="join_article"),
    path("approve/<int:article_id>", views.approve_article, name="approve_article"),
    path("reject/<int:article_id>", views.reject_or_restore_article, name="reject_article"),

    path("degree", views.degree, name="degree"),
    path("sections", views.sections, name="sections"),
    path("section/<int:section_id>", views.section, name="section"),
    path("user_articles", views.user_articles, name="user_articles"),
    path("check_technical_work", views.check_technical_work, name="check_technical_work"),
    path("search_articles", views.search_articles, name="search_articles"),

    # Autocomplete API Routes
    path("search_title", views.search_title, name="search_title"),
    path("search_title_translation", views.search_title_translation, name="search_title_translation"),

    # Email Routes
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='conference/password_reset/password_reset_done.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='conference/password_reset/password_reset_confirm.html'),name='password_reset_confirm'),
    path('password-reset-complete/', PasswordResetCompleteView.as_view(template_name='conference/password_reset/password_reset_complete.html'),name='password_reset_complete'),
    path('password-reset/', PasswordResetView.as_view(template_name='conference/password_reset/password_reset.html',
                                                      html_email_template_name='conference/password_reset/password_reset_email.html',
                                                      subject_template_name='conference/password_reset/password_reset_sebject.txt'), name='password_reset'),
    path("resend_email", views.resend_email, name="resend_email"),
    path("email_change", views.email_change, name="email_change"),

    path("accept_join/<int:user_id>/<int:article_id>/<token>", views.accept_join, name="accept_join"),
    path("accept_invitation/<int:sender_id>/<int:recipient_id>/<int:article_id>/<token>", views.accept_invitation, name="accept_invitation"),
    path("confirm_staff/<int:user_id>/<token>", views.confirm_staff, name="confirm_staff"),

    # Instructions Routes
    path("how-to-register", views.register_instruction, name="register_instruction"),
    path("thesis-requirements", views.thesis_instruction, name="thesis_instruction"),
    path("article-requirements", views.article_instruction, name="article_instruction"),
    path("staff-instruction", views.staff_instruction, name="staff_instruction"),
    path("upload-instruction-thesis", views.upload_thesis_instruction, name="upload_thesis_instruction"),
]
