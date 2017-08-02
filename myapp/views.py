# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
from django.shortcuts import render,redirect
from forms import SignUpForm,LoginForm,PostForm,LikeForm,CommentForm
from models import UserModel,SessionToken,PostModel,LikeModel,CommentModel,swachh_bharat
from django.contrib.auth.hashers import make_password, check_password
from imgurpython import ImgurClient
from InstaClone.settings import BASE_DIR
from django.contrib import messages
from clarifai.rest import ClarifaiApp
import sendgrid
from sendgrid.helpers.mail import *


YOUR_CLIENT_ID="4ca4ee91e7f89bd"
YOUR_CLIENT_SECRET="a140c84ad4e31494f999b787891d429297f952c8"
CLARIFY_KEY='adb39193a68140b7bc43d3e8bb3c9c82'
dirty_list=['garbage','waste','polluttion','junk','trash','litter','disposal']

sg = sendgrid.SendGridAPIClient(apikey='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')

# Create your views here.
def signup_view(request):

    if request.method == "POST":
        form=SignUpForm(request.POST)
        if form.is_valid():
            name=form.cleaned_data['name']
            username=form.cleaned_data['username']
            email=form.cleaned_data['email']
            password=form.cleaned_data['password']
            user = UserModel(name=name, password=make_password(password), email=email, username=username)
            user.save()


            from_email = Email("support@InstaClone.com")
            to_email = Email(email)
            subject = "Signup Confirmation!"
            content = Content("text/plain", "Welcome to InstaClone.Your InstaClone Signup is successful. Login and enjoy!")
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())
            return render(request, 'success.html')

    elif request.method == 'GET':
        form = SignUpForm()
    today=datetime.now()
    return render(request, 'index.html',{'today': today} ,{'form': form})

def login_view(request):
    response_data = {}
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = UserModel.objects.filter(username=username).first()

            if user:
                if check_password(password, user.password):
                    token = SessionToken(user=user)
                    token.create_token()
                    token.save()
                    response = redirect('/feed/')
                    response.set_cookie(key='session_token', value=token.session_token)
                    return response
                else:
                    note = 'Incorrect Password! Please try again!'
                    return render(request, 'login.html', {'note': note})
            else:
                note = 'Incorrect Username! Please try again!'
                return render(request, 'login.html', {'note': note})
    elif request.method == 'GET':
        form = LoginForm()

    response_data['form'] = form
    return render(request, 'login.html', response_data)


def feed_view(request):
    user = check_validation(request)
    if user:
        posts = PostModel.objects.all().order_by('-created_on')
        for post in posts:
            existing_like = LikeModel.objects.filter(post_id=post.id, user=user).first()
            if existing_like:
                post.has_liked = True

        return render(request, 'feed.html', {'posts': posts})
    else:
        return redirect('/login/')


# For validating the session
def check_validation(request):
    if request.COOKIES.get('session_token'):
        session = SessionToken.objects.filter(session_token=request.COOKIES.get('session_token')).first()
        if session:
            return session.user
    else:
        return None

def post_view(request):
    user = check_validation(request)

    if user:
        if request.method == 'GET':
            form = PostForm()
        elif request.method == 'POST':
            form = PostForm(request.POST, request.FILES)
            if form.is_valid():
                image = form.cleaned_data.get('image')
                caption = form.cleaned_data.get('caption')
                post = PostModel(user=user, image=image, caption=caption)
                post.save()
                path = str(BASE_DIR +'\\'+ post.image.url)
                client = ImgurClient(YOUR_CLIENT_ID, YOUR_CLIENT_SECRET)
                post.image_url = client.upload_from_path(path, anon=True)['link']
                variant(post)
                post.save()
        return render(request, 'post.html', {'form': form})
    else:
        return redirect('/login/')

def like_view(request):
  user = check_validation(request)
  if user and request.method == 'POST':
      form = LikeForm(request.POST)
      if form.is_valid():
          post_id = form.cleaned_data.get('post').id

          existing_like = LikeModel.objects.filter(post_id=post_id, user=user).first()

          if not existing_like:
              LikeModel.objects.create(post_id=post_id, user=user)

              postimg = PostModel.objects.filter(id=post_id).first()
              userid = postimg.user_id
              user = UserModel.objects.filter(id=userid).first()
              mail = user.email

              from_email = Email("support@InstaClone.com")
              to_email = Email(mail)
              subject = "Like Notification"
              content = Content("text/plain", "Someone just liked your post!")
              mail = Mail(from_email, subject, to_email, content)
              response = sg.client.mail.send.post(request_body=mail.get())
          else:
              existing_like.delete()

          return redirect('/feed/')

  else:
    return redirect('/login/')

def comment_view(request):
    user = check_validation(request)
    if user and request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            post_id = form.cleaned_data.get('post').id
            comment_text = form.cleaned_data.get('comment_text')
            comment = CommentModel.objects.create(user=user, post_id=post_id, comment_text=comment_text)
            comment.save()

            messages.success(request,'Commment successfully posted')

            postimg=PostModel.objects.filter(id=post_id).first()
            userid=postimg.user_id
            user=UserModel.objects.filter(id=userid).first()
            mail=user.email


            from_email = Email("support@InstaClone.com")
            to_email = Email(mail)
            subject = "Comment Notification"
            content = Content("text/plain", "Someone just commented on your post!")
            mail = Mail(from_email, subject, to_email, content)
            response = sg.client.mail.send.post(request_body=mail.get())

            return redirect('/feed/')
        else:
            return redirect('/feed/')
    else:
        return redirect('/login')


# variant function uses clarify api to store
def variant(post):
    app = ClarifaiApp(api_key=CLARIFY_KEY)
    model = app.models.get('general-v1.3')
    response = model.predict_by_url(url=post.image_url)

    if response["status"]["code"] == 10000:
        if response["outputs"]:
            if response["outputs"][0]["data"]:
                if response["outputs"][0]["data"]["concepts"]:
                    for index in range(0, len(response["outputs"][0]["data"]["concepts"])):
                        if response["outputs"][0]["data"]["concepts"][index]["name"] in dirty_list:
                            category = swachh_bharat(post=post,text=response["outputs"][0]["data"]["concepts"][index]["name"])
                            category.save()
                        else:
                            pass
                else:
                    print "No Concepts List Found"
            else:
                print "No Data List Found"
        else:
            print "No Outputs List Found"
    else:
        print "Response Code Error"
