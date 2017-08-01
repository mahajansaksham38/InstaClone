from django import forms
from models import UserModel,PostModel,LikeModel,CommentModel

#SignUpForm accepts entries for UserModel from User
class SignUpForm(forms.ModelForm):
  class Meta:
    model = UserModel
    fields=['email','username','name','password']

#LoginForm accepts username and password for login
class LoginForm(forms.ModelForm):
    class Meta:
        model = UserModel
        fields = ['username', 'password']
#PostForm accepts image path, caption and url for PostModel
class PostForm(forms.ModelForm):
    class Meta:
        model=PostModel
        fields=['image','caption']

#LikeForm accepts post to be liked for LikeModel
class LikeForm(forms.ModelForm):
    class Meta:
        model = LikeModel
        fields = ['post']

#CommentForm accepts comment text and post to be commented on for CommentModel
class CommentForm(forms.ModelForm):
  class Meta:
    model = CommentModel
    fields = ['comment_text', 'post']
