from django.shortcuts import render, redirect, HttpResponseRedirect
from django.http import HttpResponse

# send email package
from django.core.mail import EmailMultiAlternatives

# package for password hex
from passlib.hash import pbkdf2_sha256

# package for upload files
from django.core.files.storage import FileSystemStorage

# pagination package
from django.core.paginator import Paginator

# package for multiple query at one time
from django.db.models import Q

# package for display informative messages to users
from django.contrib import messages

# models
from .models import Users, Question, Answer, Comment

# other modules
import string
import random
import requests
import os
import json

# config.json File
with open("config.json", 'r') as json_file:
    params = json.load(json_file)["PARAMS"]
    # admin_login = json.load(json_file)["ADMIN_LOGIN"]


# Important variable
DOMAIN = params["DOMAIN_URL"]



# Home Page

def Home(request):

    # iterate all questions from the database, order by views & date_posted
    question_obj = Question.objects.all().order_by('-date_posted').order_by('-views')

    # pagination to all questions objects
    paginator = Paginator(question_obj, params["NO_OF_POSTS_PER_PAGE"])
    page = request.GET.get('page')
    questions = paginator.get_page(page)

    # declare some variables
    login = False
    user = ""

    # if user logged in - assign the login varaible is True
    # & assign user = user object from its email session varaible
    if request.session.get('email'):
        user = Users.objects.get(email=request.session.get('email'))
        login = True

    # render all the info to the template and display to the users
    return render(request, 'MainApp/home.html', ({
        "title": "Discus Question",
        "page": "home",
        "login": login,
        "user": user,
        "question_obj": questions,
    }))


# Register Page

def Register(request):

    # if user logged in redirect to the home page
    if request.session.get('email'):
        messages.add_message(request, messages.INFO,
                             f'You are already logged in.')
        return redirect('home_page')

    # if user not logged in & submit the register form
    if request.method == 'POST':

        # get the form data from all input fields
        name = request.POST.get('name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        # check username is unique or not
        checkUsername = Users.objects.filter(username=username)

        # if username already exists - user stay on register page & display info to user
        if checkUsername:
            messages.add_message(request, messages.WARNING,
                                 f'This Username is already taken!')
            return redirect('register_page')

        # if username is unique, check email is unique or not
        else:
            checkemail = Users.objects.filter(email=email)

            # if email is already exists - user stay on register page & display info to user
            if checkemail:
                messages.add_message(request, messages.WARNING,
                                     'This Email is already Exists!')
                return redirect('register_page')

            # if both username and email is unique
            # user account created
            else:

                # random verify string
                lst = [random.choice(string.ascii_letters + string.digits)
                       for n in range(50)]
                verifyStr = "".join(lst)

                # send mail to the user email address
                subject, from_email, to = 'Verify your Email Address', 'goshouters@gmail.com', email
                text_content = 'This is an important message.'
                html_content = f'''
                    <h1 style="font-family: 'Lexend Deca', sans-serif; font-weight: bold; font-size: 30px; color: #8B78E6; text-align: center;"> Discus Question </h1>
                    <p style="font-family: 'Roboto', sans-serif; font-size: 18px; padding: 0 200px; margin: 13px 0; margin-bottom: 20px;">
                        We need to verify your email address. We have sent an email to {email} to verify your address. Please click the link below to verify your email address.
                    </p>
                    <div style="text-align: center; font-family: 'Roboto', sans-serif;">
                        <a href="{DOMAIN}/verify/{username}/{verifyStr}" style="text-decoration: none; background: #8B78E6; color: #fff; border: none; padding: 10px 20px; padding-bottom: 20px; font-size: 17px;">Verify your Email</a>
                    </div>
                '''
                msg = EmailMultiAlternatives(
                    subject, text_content, from_email, [to])
                msg.attach_alternative(html_content, "text/html")
                msg.send()


                # random change password string
                s = [random.choice(string.ascii_letters + string.digits)
                     for n in range(80)]
                change_pass_str = "".join(s)


                # encrypt password
                enc_password = pbkdf2_sha256.encrypt(
                    password, rounds=12000, salt_size=32)

                # find user location
                r = requests.get('https://api.ipdata.co?api-key=' + params["IPDATA_API_KEY"]).json()
                location = r['country_name']

                # sava data to the database and the user account created
                newUser = Users(name=name, username=username,
                                email=email, password=enc_password, verify=verifyStr, location=location, change_pass_str=change_pass_str)
                newUser.save()

                # After creating user account, redirect to the home page
                messages.add_message(request, messages.SUCCESS,
                                     'Your Accound has been created successfully. Now you can login to your account after verifying email.')
                return redirect('home_page')

    # if user not logged in simply render register.html page
    else:
        return render(request, 'MainApp/register.html', ({
            "title": "Register",
            "page": "register"
        }))


# Login Page

def Login(request):

    # if user already logged in, redirect to home page and display info
    if request.session.get('email'):
        messages.add_message(request, messages.INFO,
                             f'You are already logged in.')
        return redirect('home_page')

    # if user not logged in and user submit the login form
    if request.method == 'POST':

        # get the form data from all input fields
        email = request.POST.get('email')
        password = request.POST.get('password')

        # check email address is exists or not
        checkemail = Users.objects.filter(email=email).count()

        # if email exists
        if checkemail == 1:

            # get that email object
            getEmail = Users.objects.get(email=email)

            # if password is right
            if (pbkdf2_sha256.verify(password, getEmail.password)):

                # check the user email address is verified or not - if verified
                if (getEmail.verify == 'True'):

                    # user successfully logged in
                    request.session['email'] = email
                    messages.add_message(request, messages.SUCCESS,
                                         'You are successfully logged in.')
                    return redirect('home_page')

                # if user email address is not verified
                else:
                    messages.add_message(request, messages.WARNING,
                                         'Please verify your Email Address.')
                    return redirect('login_page')

            # if password is wrong
            else:
                messages.add_message(request, messages.WARNING,
                                     'Incorrect password! Please check it perfectly')
                return redirect('login_page')

        # if email does not exists
        else:
            messages.add_message(request, messages.WARNING,
                                 'Wrong Email Address! Please check it perfectly')
            return redirect('login_page')

    # if user does not logged in
    else:
        return render(request, 'MainApp/login.html', ({
            "title": "Login",
            "page": "login"
        }))


# user Email Verification page

def Verify(request, username, chars):

    # Here two parameters, username gives the username of user,
    # and chars gives that random verify string of user account

    # get the user object
    uname = Users.objects.get(username=username)

    # if username exists
    if uname:

        # check random verify string of the user object from chars parameter
        # if random verify string of the user object is equal to the chars parameter
        # then user email is verified --

        if (uname.verify == chars):

            # update verify row of the use to True & redirect user to login page and display info
            Users.objects.filter(username=username).update(verify=True)

            messages.add_message(request, messages.SUCCESS,
                                 'Thanks for verifying your Email Address. Now you can login to your account.')
            return redirect('login_page')

        # if random verify string of the user object is not equal to the chars parameter
        else:
            return redirect('home_page')

    # if username does not exixts
    else:
        return redirect('home_page')


# user Account Page

def Account(request):

    # if user logged in
    if request.session.get('email'):

        # get the user object from the email sessaion variable
        user_obj = Users.objects.get(email=request.session['email'])

        # get all the question objects of the logged in user
        question_obj = Question.objects.filter(user=user_obj).order_by('-date_posted')

        # render all the info to the template
        return render(request, 'MainApp/account.html', ({
            "title": "Account",
            "page": "account",
            "login": True,
            "data": user_obj,
            "questions": question_obj,
            "ques_length": question_obj.count(),
            "user": user_obj
        }))

    # if user not logged in, redirect to home page
    else:
        messages.add_message(request, messages.INFO,
                             'First you have to login to your account.')
        return redirect('home_page')


# Logout Page

def Logout(request):

    # if user logged in
    if request.session['email']:

        # delete session variable
        del request.session['email']

        messages.add_message(request, messages.INFO,
                             'Good to see you, You are successfully Logged out!')
        return redirect('home_page')

    # if user does not logged in
    else:
        return redirect('home_page')


# Forget Password page
# send mail to user for changing password

def Forget_password(request):

    # if user submit the forget_password form
    if request.method == "POST":

        # get the data from input field
        email = request.POST.get('email')

        # if input field email is blank
        # display a info to user and redirect to same page

        if email == "":
            messages.add_message(request, messages.WARNING,
                                 'Please Enter your Email Address.')
            return redirect('forget_pass_page')

        # if email field is not blank
        # query the user email is exists or not

        checkemail = Users.objects.filter(email=email).count()

        # if user email is exists
        if checkemail == 1:

            # get the user object from the user email
            data = Users.objects.get(email=email)

            # send mail to the user email address
            subject, from_email, to = 'Choose a new password', 'goshouters@gmail.com', email
            text_content = ''
            html_content = f'''
                    <h1 style="font-family: 'Lexend Deca', sans-serif; font-weight: bold; font-size: 30px; color: #8B78E6; text-align: center;"> Discus Question </h1>
                    <p style="font-family: 'Roboto', sans-serif; font-size: 16px; padding: 0 200px; margin: 13px 0; margin-bottom: 20px;">
                        There was a request to change your password. <br>
                        If you did not make this request, just ignore this email. Otherwise, please click the button below to change your password.
                    </p>
                    <div style="text-align: center; font-family: 'Roboto', sans-serif;">
                        <a href="{DOMAIN}/changepassword/{data.username}/{data.change_pass_str}" style="text-decoration: none; background: #8B78E6; color: #fff; border: none; padding: 10px 20px; padding-bottom: 20px; font-size: 17px;">Change password</a>
                    </div>
                '''
            msg = EmailMultiAlternatives(
                subject, text_content, from_email, [to])
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            # display info to user and redirect user to home Page
            messages.add_message(request, messages.INFO,
                                 'Mail successfully sent to your email address.Open your mailbox, There is Instructions to chnage password.')
            return redirect('home_page')

        # if user email does not exists
        else:
            messages.add_message(request, messages.WARNING,
                                 'Wrong Email Address! Please check it perfectly.')
            return redirect('forget_pass_page')

    # if user does not submit the forget_password form
    else:
        return render(request, 'MainApp/forget_password.html', ({
            "title": "Forget Password",
            "page": "forget"
        }))


# Change Password Page
# open the link from mail which send from forget passwrod Page
# for set new password to user

def ChangePassword(request, username, chars):

    # Here two parameters, username gives the username of user,
    # and chars gives that random change password string of user account

    # if user submit the change password form
    if request.method == "POST":

        # get the data of input field
        password = request.POST.get('password')
        con_password = request.POST.get('confirm_password')

        # length of password, user submitted
        pass_length = len(password)

        # if password is blank, redirect user to same page
        if password == "":
            messages.add_message(
                request, messages.WARNING, 'Please Enter your new password')
            return redirect(f'{DOMAIN}/changepassword/{username}/{chars}')

        # if password length is less than 8 or greater than 25
        # redirect user to same page

        elif (pass_length < 8 or pass_length > 25):
            messages.add_message(
                request, messages.WARNING, 'Password must be between 8 to 25 characters.')
            return redirect(f'{DOMAIN}/changepassword/{username}/{chars}')

        # if password field value not equal to confirm password field
        elif password != con_password:
            messages.add_message(
                request, messages.WARNING, 'Password do not match')
            return redirect(f'{DOMAIN}/changepassword/{username}/{chars}')

        # if password field value is valid
        else:

            # encrypt password
            enc_password = pbkdf2_sha256.encrypt(
                password, rounds=12000, salt_size=32)

            # update password
            userpass = Users.objects.filter(
                username=username).update(password=enc_password)

            # generate random change password string of user
            s = [random.choice(string.ascii_letters + string.digits)
                 for n in range(80)]
            change_pass_str = "".join(s)

            # update change password string of user
            user_pass_str = Users.objects.filter(
                username=username).update(change_pass_str=change_pass_str)

            # display info to user and redirect to login page
            messages.add_message(request, messages.SUCCESS,
                                 'Your Password succesfully changed.')
            return redirect('login_page')

    # if user does not submit the change password form
    else:

        # query the user object from username of user
        checkusername = Users.objects.filter(username=username)

        # if username exists
        if checkusername:

            # get the user object from username of user
            user = Users.objects.get(username=username)

            # if change password string of user object is equal to chars parameters
            # render change password file

            if user.change_pass_str == chars:
                return render(request, 'MainApp/change_password.html', ({
                    "title": "Change Password",
                    "page": "change_password"
                }))

            # if change password string of user object is not equal to chars parameters
            else:
                return redirect('home_page')

        # if username doen not exists
        else:
            return redirect('home_page')


# Edit Profile Page

def EditProfile(request):

    # if user submit eidt profile form
    if request.method == "POST":

        # get the data of input fields
        name = request.POST.get('name')
        desc = request.POST.get('about-user')
        location = request.POST.get('location')
        show_email = request.POST.get('show_email')

        # declare a variable
        showEmailSwitch = False

        # if show email switch is on
        if show_email == "on":
            showEmailSwitch = True

        # update the user object
        update = Users.objects.filter(email=request.session['email']).update(
            name=name, description=desc, location=location, show_email=showEmailSwitch)
        return redirect('account_page')

# User profiel Image Upload Page

def Upload (request):

    # if user upload profile picture
    if request.method == "POST":

        # get the user uploaded file
        user_avatar = request.FILES['img']

        # get the extension of file
        ext = os.path.splitext(user_avatar.name)[1]

        # if user uploaded file is not image
        if (ext.lower() not in ['.png', '.jpg', '.jpeg']):
            messages.add_message(request, messages.WARNING,
                                 'Please choose image file')
            return redirect('account_page')

        # if user uploaded file is image but size is greater than 1mb
        elif (user_avatar.size > 1000000):
            messages.add_message(request, messages.WARNING,
                                 'Please choose image size less than 1 MB')
            return redirect('account_page')

        # if user uploaded file is image and size is less than 1mb
        else:

            # randomize user uploaded image name
            random_str = [random.choice(string.ascii_letters + string.digits)for n in range(50)]
            image_name = "".join(random_str) + ext

            # package from which image can be delete or save
            fs = FileSystemStorage()

            # get the user object from email session variable
            user = Users.objects.get(email=request.session['email'])

            # if user present profile picture is not same to the user default profile image
            # delete the present profile picture of user

            if (user.user_img.name != "user_profile/user_default.png"):
                fs.delete(f"{user.user_img.name}")

            # update the new uploaded profile image of user
            fs.save(f"user_profile/{image_name}", user_avatar)

            # update the image url of user
            update = Users.objects.filter(email=request.session['email']).update(user_img=f"user_profile/{image_name}")

            # redirect to account page
            return redirect('account_page')

    # if user does not upload profile picture
    # redirect to home page

    else:
        return redirect('home_page')

# Add Question Page

def AddQuestion (request):

    # if user submit addquestion form
    if request.method == "POST":

        # get the data of input fields
        title = request.POST.get('title')
        description = request.POST.get('desc')
        category = request.POST.get('category')
        tags = request.POST.get('tags')
        url = request.POST.get('url')

        # query the question url already exists or not
        question_obj = Question.objects.filter(url=url)

        # if question url exists
        if (question_obj):
            messages.add_message(
                request, messages.WARNING, 'This Question is already asked! Please ask another question.')
            return redirect("account_page")

        # if question url does not exists
        else:

            # get the user object from email session varaible
            user_obj = Users.objects.get(email=request.session['email'])

            # add new question to database
            newQuestion = Question(title=title, description=description, category=category, tags=tags, user=user_obj, url=url)
            newQuestion.save()

            # display info to user and redirect to account page
            messages.add_message(
                    request, messages.SUCCESS, 'Question added successfully. I hope you got the solution of your question soon.')
            return redirect("account_page")

    # if user does not submit addquestion form
    else:
        return redirect("home_page")


# Question, Answers, comments Page

def Question_Answers (request, question_url):

    # Here question_url parameter contain url of question

    # query question object from question_url parameter
    data = Question.objects.filter(url=question_url)

    # query answer objects from question_url parameter
    answer_data = Answer.objects.filter(question_url=question_url).order_by('-date_posted')

    # declare varaible
    user = ""

    # if user logged in
    if request.session.get('email'):

        # get the user object from email session variable
        user = Users.objects.get(email=request.session.get('email'))

        # declare login variable to True
        login = True

    # if user does not logged in
    else:

        # declare user variable to blank
        user = ""

        # declare login variable to Falsw
        login = False

    # if question object is exists from question_url parameter
    if data:

        # get the question object from question url parameter
        data = Question.objects.get(url=question_url)

        # increment the views of question
        views = data.views
        views += 1
        Question.objects.filter(url=question_url).update(views=views)

        # get the comment objects from question url parameter
        comments = Comment.objects.filter(question_url=question_url)

        # render user to question_answers page
        return render(request, "MainApp/question_answers.html", ({
            "title": data.title,
            "page": "question_answers",
            "data": data,
            "login": login,
            "user_login": user,
            "answer_data": answer_data,
            "answer_len": answer_data.count(),
            "user": user,
            "comments": comments
        }))

    # if question object doen not exists from question_url parameter
    else:
        return redirect("home_page")

# Answers page

def Answers (request, question_url):

    # Here question_url parameter contains url of question

    # if user submit answer
    if request.method == "GET":

        # if user logged in
        if request.session.get('email'):

            # get the data from input field
            answer = request.GET.get('answer')

            # if answer input field value is blank
            if answer == "":
                messages.add_message(
                    request, messages.WARNING, 'Please Enter your answer.')
                return redirect(f"{DOMAIN}/{question_url}")

            # if answer input field value is greater than 700 characters
            elif len(answer) > 700:
                messages.add_message(
                    request, messages.WARNING, 'Please Enter your answer less than 700 characters.')
                return redirect(f"{DOMAIN}/{question_url}")

            # if answer input field value is valid
            else:

                # get the answer obbject from question_url parameter and order by date_posted
                answer_data = Answer.objects.filter(question_url=question_url).order_by('-date_posted')

                # get the user object from email session variable
                user = Users.objects.get(email=request.session.get('email'))

                # create new answer object
                Answer.objects.create(
                    answer=answer,
                    user=user,
                    question_url=question_url
                )

                # update the lenght of answer of Question object
                Question.objects.filter(url=question_url).update(answer_length=answer_data.count())

                # display info and redirect to same page
                messages.add_message(
                    request, messages.SUCCESS, 'Your answer is succesfully submited.')
                return redirect(f"{DOMAIN}/{question_url}")

        # if user does not logged in
        else:
            messages.add_message(
                    request, messages.INFO, 'First you have to login to your account.')
            return redirect("login_page")

    # if user does not submit answer
    else:
        return redirect("home_page")

# Comment Page

def Comments (request, answer_id):

    # Here answer_id parameter contains id answer

    # if user submit comment form
    if request.method == "GET":

        # if user logged in
        if request.session.get('email'):

            # get the data of input field
            comment = request.GET.get("comment")

            # if comment input field value is blank
            if comment == "":
                pass

            # if comment input field value length is greater than 200 characters
            elif len(comment) > 200:
                pass

            # if comment input field value if valid
            else:

                # get the answer object from answer_id parameter
                ans = Answer.objects.get(id=answer_id)

                # get the userobject from email session variable
                user = Users.objects.get(email=request.session.get('email'))

                # create new comment object
                Comment.objects.create(
                    comment=comment,
                    user=user,
                    answer_id=answer_id,
                    question_url=ans.question_url
                )

                # display message and redirect user. to same page
                messages.add_message(
                    request, messages.INFO, 'Your comment successfully submited.')
                return redirect(f"{DOMAIN}/{ans.question_url}")

        # if user does not logged in
        else:
            messages.add_message(
                    request, messages.INFO, 'First you have to login to your account.')
            return redirect("login_page")

    # if user does not submit comment form
    else:
        return redirect("home_page")

# Profile Page

def Profile (request, username):

    # Here username parameter contain username of user

    # get the user object from username parameter
    data = Users.objects.get(username=username)

    # query question object from user object
    question = Question.objects.filter(user=data).order_by('-date_posted')

    # declare variable
    login = False

    # if user logged in
    if request.session.get('email'):

        # declsre login variable to True
        login = True

        # get user object from email session variable
        login_user = Users.objects.get(email=request.session.get('email'))

        # if username parameter is equal to username of user objects
        if login_user.username == username:
            return redirect('account_page')

    # if user does not logged in
    else:
        login_user = ""

    # render profile page
    return render(request, 'MainApp/profile.html', ({
       "title": "Profile",
       "data": data,
       "user": login_user,
       "questions": question,
       "login": login,
       "ques_length": question.count(),
    }))


# Edit Question Page

def EditQuestion (request, question_url):

    # Here question url parameter contain url of question

    # if user submit edit question form
    if request.method == "POST":

        # get the data from input fields
        title = request.POST.get("title")
        description = request.POST.get("desc")

        # query question object from question_url parameter
        question_obj = Question.objects.filter(url=question_url).update(title=title, description=description)

        messages.add_message(
                    request, messages.SUCCESS, 'Your Question is succesfully updated.')
        return redirect("account_page")

    # if user does not submit edit question form
    else:
        return redirect("account_page")


# Delete Question Page

def DeleteQuestion (request, question_url):

    # Here question url parameter contain url of question

    # if user submit delete question form
    if request.method == "POST":

        # get the question object from question_url parameter
        question = Question.objects.get(url=question_url)

        # delete question object
        question.delete()

        messages.add_message(
                    request, messages.SUCCESS, 'Your Question is succesfully Deleted.')
        return redirect("account_page")

    # if user does not submit question form
    else:
        return redirect("account_page")

# Edit Answer Page

def EditAnswer (request, question_url, answer_id):

    # Here question_url & answer_id parameters
    # question_url parameter contain url of question and answer_id contain id of answer

    # if user submit edit answer form
    if request.method == "POST":

        # get the data from input field
        answer = request.POST.get("answer")

        # query the answer object from answer_id parameter
        Answer.objects.filter(id=answer_id).update(answer=answer)

        messages.add_message(
                    request, messages.SUCCESS, 'Your Answer is succesfully Edited.')
        return redirect(f"{DOMAIN}/{question_url}")

    # if user doen not submit edit answer form
    else:
        return redirect("home_page")

# Delete Answer Page

def DeleteAnswer (request, question_url, answer_id):

    # Here question_url & answer_id parameters
    # question_url parameter contain url of question and answer_id contain id of answer

    # if user submit delete answer form
    if request.method == "POST":

        # get the answer object from answer_id parameter
        answer = Answer.objects.get(id=answer_id)

        # delete answer object
        answer.delete()

        messages.add_message(
                    request, messages.SUCCESS, 'Your Answer is succesfully Deleted.')
        return redirect(f"{DOMAIN}/{question_url}")

    # if user does not submit delete answer form
    else:
        return redirect("home_page")

# Edit Comment Page

def EditComment (request, question_url, comment_id):

    # Here question_url & comment_id parameters
    # question_url parameter contain url of question and comment_id contain id of comment

    # if user submit edit comment form
    if request.method == "POST":

        # get the data of input filed
        Commentval = request.POST.get("comment")

        # update the comment object from comment_id
        comment = Comment.objects.filter(id=comment_id).update(comment=Commentval)

        messages.add_message(
                    request, messages.SUCCESS, 'Your Comment is successfully Edited.')
        return redirect(f"{DOMAIN}/{question_url}")

    # if user does not submit edit comment form
    else:
        return redirect("home_page")

# Delete Comment Page

def DeleteComment (request, question_url, comment_id):

    # Here question_url & comment_id parameters
    # question_url parameter contain url of question and comment_id contain id of comment

    # if user submit delete comment form
    if request.method == "POST":

        # get the comment object from comment_id parameter
        comment = Comment.objects.get(id=comment_id)

        # delete comment object
        comment.delete()

        messages.add_message(
                    request, messages.SUCCESS, 'Your Comment is successfully Deleted.')
        return redirect(f"{DOMAIN}/{question_url}")

    # if user does not submit delete comment form
    else:
        return redirect("home_page")

# Search Page

def Search (request):

    # if user submit search form
    if request.method == "GET":

        # get the data from input field
        searchTxt = request.GET.get("search")

        # query question object to its titlt, description and tags with order by views & data_posted
        query = Question.objects.filter(
                    Q(title__icontains=searchTxt) |
                    Q(description__icontains=searchTxt) |
                    Q(tags__icontains=searchTxt)
                ).order_by('-date_posted').order_by('-views')

        # declare varaibles
        login = False
        user = ""

        # if user logged in
        if request.session.get('email'):
            user = Users.objects.get(email=request.session.get('email'))
            login = True

        # if query has at least one filtered question object
        if query:

            # paginate all the questions objects
            paginator = Paginator(query, params["NO_OF_POSTS_PER_PAGE"])
            page = request.GET.get('page')
            questions = paginator.get_page(page)

            # render home page
            return render(request, 'MainApp/home.html', ({
                "title": "Discus Question",
                "page": "search",
                "login": login,
                "user": user,
                "found": True,
                "question_obj": questions,
            }))

        # if query has no filtered question object
        else:
            return render(request, 'MainApp/home.html', ({
                "title": "Discus Question",
                "page": "search",
                "login": login,
                "user": user,
                "found": False,
                "question_obj": ""
            }))

    # if user does not submit search form
    else:
        return redirect('home_page')

# Delete Account Page

def DeleteAccount (request, user_id):

    # Here user_id parameter contain id of user

    # if user submit deleteaccount form
    if request.method == "POST":

        # get the data from input field
        password = request.POST.get("password")

        # get the user object from email session varaible
        user = Users.objects.get(email=request.session.get('email'))

        # if password of user object is matched to the password input field
        if (pbkdf2_sha256.verify(password, user.password)):

            # delete user object
            user.delete()

            # delete session varaible
            del request.session['email']

            messages.add_message(request, messages.INFO,
                                'Good to see you, Your account successfully deleted.')
            return redirect('home_page')

        # if password of user object is not matched to the password input field
        else:
            messages.add_message(request, messages.WARNING,
                                'Wrong Password! Please check it perfectly.')
            return redirect(f"{DOMAIN}/deleteaccount/{user.id}")

    # if user logged in
    if request.session.get('email'):

        # get the user object from email session varaible
        user = Users.objects.get(email=request.session.get('email'))

        # if id of user object matched to user_id parameter
        if user.id == user_id:

            # render deleteaccount page
            return render(request, 'MainApp/deleteaccount.html', ({
                "title": "Delete",
                "page": "deleteAccount"
            }))

        # if id of user object does not matched to user_id parameter
        else:
            return redirect("home_page")

    # if user does not logged in
    else:
        return redirect('home_page')

