# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
import bcrypt, re

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

# Create your models here.
class UserManager(models.Manager):
    def register_validator(self, postData):
        errors = {}
        if len(postData['first_name']) < 1 or not postData['first_name'].isalpha():
            errors['first_name'] = "Enter a name"
        if len(postData['last_name']) < 1 or not postData['last_name'].isalpha():
            errors['last_name'] = "Enter your last name"
        if len(User.objects.filter(username=postData['username'])) > 0 or len(postData['username']) < 3:
            errors['username'] = "Username not valid or is taken"
        if len(postData['password']) < 8:
            errors['password'] = "Password must be at least 8 characters"
        if not postData['password'] == postData['confirm_pw']:
            errors['confirm_pw'] = "Passwords do not much"
        return errors

    def login_validator(self, postData):
        login_errors = {}
        hash1 = bcrypt.hashpw(postData['pw_login'].encode(), bcrypt.gensalt())
        if len(User.objects.filter(username=postData['username'])) == 0 or not bcrypt.checkpw(postData['pw_login'].encode(), hash1.encode()):
            login_errors['login'] = "Incorrect username or password. Try again"
        return login_errors

class ReviewManager(models.Manager):
    def review_validator(self, postData):
        review_errors = {}
        if len(postData['description']) < 1:
            review_errors['description'] = "Review is blank!"
        return review_errors

class User(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

class Place(models.Model):
    name = models.CharField(max_length=255)
    users = models.ManyToManyField(User, related_name="places")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Review(models.Model):
    description = models.TextField()
    rating = models.IntegerField()
    user = models.ForeignKey(User, related_name="reviews")
    place = models.ForeignKey(Place, related_name="reviews")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ReviewManager()