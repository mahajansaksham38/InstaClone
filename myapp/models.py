# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
import uuid

#UserModel stores user's details
class UserModel(models.Model):
  email = models.EmailField( null=False ,blank=False)
  name = models.CharField(unique=True,max_length=120,null=False)
  username = models.CharField(max_length=120, null=False ,blank=False)
  password = models.CharField(max_length=255)
  created_on = models.DateTimeField(auto_now_add=True)
  updated_on = models.DateTimeField(auto_now=True)

#SessionToken generates a random session token and has fields for storing it with foreign key to UserModel
class SessionToken(models.Model):
    user = models.ForeignKey(UserModel)
    session_token = models.CharField(max_length=255)
    last_request_on = models.DateTimeField(auto_now=True)
    created_on = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=True)

    def create_token(self):
        self.session_token = uuid.uuid4()

#PostModel stores posts urls and captions with foreign key reference to UserModel
class PostModel(models.Model):
  user = models.ForeignKey(UserModel)
  image = models.FileField(upload_to='user_images')
  image_url = models.CharField(max_length=255)
  caption = models.CharField(max_length=240)
  created_on = models.DateTimeField(auto_now_add=True)
  updated_on = models.DateTimeField(auto_now=True)

  @property
  def like_count(self):
      return len(LikeModel.objects.filter(post=self))

  @property
  def comments(self):
      return CommentModel.objects.filter(post=self).order_by('-created_on')

  @property
  def classifications(self):
      return swachh_bharat.objects.filter(post=self)

#LikeModel stores foreign keys to UserModel and PostModel
class LikeModel(models.Model):
    user = models.ForeignKey(UserModel)
    post = models.ForeignKey(PostModel)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

#CommentModel stors comment_text with Foreign keys to UserModel and PostModel
class CommentModel(models.Model):
  user = models.ForeignKey(UserModel)
  post = models.ForeignKey(PostModel)
  comment_text = models.CharField(max_length=555)
  created_on = models.DateTimeField(auto_now_add=True)
  updated_on = models.DateTimeField(auto_now=True)

  @property
  def comments(self):
      return CommentModel.objects.filter(post=self).order_by('created_on')

class swachh_bharat(models.Model):
    post=models.ForeignKey(PostModel)
    text=models.CharField(max_length=555)
