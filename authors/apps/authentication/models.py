import jwt

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.models import (
    AbstractBaseUser, BaseUserManager, PermissionsMixin
)
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.db import models
from rest_framework.response import Response
from django.urls import reverse


class UserManager(BaseUserManager):

    """
    Django requires that custom users define their own Manager class. By
    inheriting from `BaseUserManager`, we get a lot of the same code used by
    Django to create a `User` for free.

    All we have to do is override the `create_user` function which we will use
    to create `User` objects.
    """

    def create_user(self, username, email, password=None):
        """Create and return a `User` with an email, username and password."""
        if username is None:
            raise TypeError('Users must have a username.')

        if email is None:
            raise TypeError('Users must have an email address.')

        user = self.model(username=username, email=self.normalize_email(email))
        user.set_password(password)
        user.save()

        return user


    def send_confirmation_email(self, email, token, request):
        protocol = 'https://' if request.is_secure() else 'http://'
        current_site = get_current_site(request)
        activate_url = protocol + current_site.domain + reverse('authentication:activate', kwargs={'token': token})
        message = "Please click <a href='" + activate_url + "'>this</a> link to activate your account. If the link doesn't work copy this to your browser:" + activate_url
        send_mail("Activate Authors'Haven Account", message, settings.COMPANY_EMAIL, [email], fail_silently=False,  html_message=message)
        return True

    def reset_password_email(self, email, token, request):
        protocol = 'https://' if request.is_secure() else 'http://'
        current_site = get_current_site(request)
        reset_url = protocol + current_site.domain + reverse('authentication:updateuser', kwargs={'token': token})
        message = "Please click  <a href='" + reset_url + "'>this</a> link to reset your password. If the link doesn't work copy this to your browser:" + reset_url
        send_mail("Reset Authors'Haven Password", message, settings.COMPANY_EMAIL, [email], fail_silently=False,  html_message=message)
        return True


    def create_superuser(self, username, email, password):
      """
      Create and return a `User` with superuser powers.

      Superuser powers means that this use is an admin that can do anything
      they want.
      """
      if password is None:
          raise TypeError('Superusers must have a password.')

      user = self.create_user(username, email, password)
      user.is_superuser = True
      user.is_staff = True
      user.is_actived = False
      user.save()

      return user



class User(AbstractBaseUser, PermissionsMixin):
    # Each `User` needs a human-readable unique identifier that we can use to
    # represent the `User` in the UI. We want to index this column in the
    # database to improve lookup performance.
    username = models.CharField(db_index=True, max_length=255, unique=True)

    # We also need a way to contact the user and a way for the user to identify
    # themselves when logging in. Since we need an email address for contacting
    # the user anyways, we will also use the email for logging in because it is
    # the most common form of login credential at the time of writing.
    email = models.EmailField(db_index=True, unique=True)

    # When a user no longer wishes to use our platform, they may try to delete
    # there account. That's a problem for us because the data we collect is
    # valuable to us and we don't want to delete it. To solve this problem, we
    # will simply offer users a way to deactivate their account instead of
    # letting them delete it. That way they won't show up on the site anymore,
    # but we can still analyze the data.
    is_active = models.BooleanField(default=True)


    is_activated = models.BooleanField(default=False)
    # The `is_staff` flag is expected by Django to determine who can and cannot
    # log into the Django admin site. For most users, this flag will always be
    # falsed.
    is_staff = models.BooleanField(default=False)

    # A timestamp representing when this object was created.
    created_at = models.DateTimeField(auto_now_add=True)

    # A timestamp reprensenting when this object was last updated.
    updated_at = models.DateTimeField(auto_now=True)

    # More fields required by Django when specifying a custom user model.

    # The `USERNAME_FIELD` property tells us which field we will use to log in.
    # In this case, we want that to be the email field.
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    # Tells Django that the UserManager class defined above should manage
    # objects of this type.
    objects = UserManager()

    def __str__(self):
        """
        Returns a string representation of this `User`.

        This string is used when a `User` is printed in the console.
        """
        return self.email


    @property
    def get_full_name(self):
      """
      This method is required by Django for things like handling emails.
      Typically, this would be the user's first and last name. Since we do
      not store the user's real name, we return their username instead.
      """
      return self.username

    def get_short_name(self):
        """
        This method is required by Django for things like handling emails.
        Typically, this would be the user's first name. Since we do not store
        the user's real name, we return their username instead.
        """
        return self.username
        

    @property
    def token(self):
        """
        Generates the token and allows the token to be claaed by `user.token`
        : return string
        """
        token = jwt.encode(
            {
                "id": self.pk,
                "username": self.get_full_name,
                "email": self.email,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(minutes=60)
            },
            settings.SECRET_KEY, algorithm='HS256').decode()
        return token


    @property
    def token(self):
        """
        Generates the token and allows the token to be claaed by `user.token`
        : return string
        """
        token = jwt.encode(
            {
                "id": self.pk,
                "username": self.get_full_name,
                "email": self.email,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(minutes=60)
            },
            settings.SECRET_KEY, algorithm='HS256').decode()
        return token
