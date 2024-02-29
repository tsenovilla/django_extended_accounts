from django.urls import path, reverse_lazy
from django.contrib.auth import views as auth_views
from django.conf import settings
from extended_accounts.views import (
    NewAccountView,
    AccountConfirmationView,
    DetailAccountView,
    UpdateAccountView,
    DeleteAccountView,
    RedirectAccountView,
    ListAccountView,
    DeleteProfileImageView,
)

app_name = "extended_accounts"
urlpatterns = [
    path("new_account/", NewAccountView.as_view(), name="new_account"),
    path(
        "account_confirmation/<str:username>/<token>/",
        AccountConfirmationView.as_view(),
        name="account_confirmation",
    ),
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="extended_accounts/login.html"),
        name="login",
    ),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path(
        "detail_account/<str:username>/",
        DetailAccountView.as_view(),
        name="detail_account",
    ),
    path("list_account/", ListAccountView.as_view(), name="list_account"),
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(
            success_url=reverse_lazy("extended_accounts:redirect_account"),
            template_name="extended_accounts/password_change_form.html",
        ),
        name="password_change",
    ),
    path(
        "reset_password_request/",
        auth_views.PasswordResetView.as_view(
            success_url=reverse_lazy("extended_accounts:reset_password_request_done"),
            template_name="extended_accounts/password_reset_form.html",
            email_template_name="extended_accounts/password_reset_email.html",
            subject_template_name="extended_accounts/password_reset_subject.html",
            from_email=settings.DEFAULT_FROM_EMAIL,
        ),
        name="reset_password_request",
    ),
    path(
        "reset_password_request_done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="extended_accounts/password_reset_done.html"
        ),
        name="reset_password_request_done",
    ),
    path(
        "reset_password/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            success_url=reverse_lazy("extended_accounts:redirect_account"),
            post_reset_login=True,
            template_name="extended_accounts/password_reset_confirm.html",
        ),
        name="reset_password",
    ),
    path(
        "update_account/<str:username>",
        UpdateAccountView.as_view(),
        name="update_account",
    ),
    path(
        "delete_account/<str:username>/",
        DeleteAccountView.as_view(),
        name="delete_account",
    ),
    path(
        "delete_profile_image/<str:username>/",
        DeleteProfileImageView.as_view(),
        name="delete_profile_image",
    ),
    path("redirect_account/", RedirectAccountView.as_view(), name="redirect_account"),
]
