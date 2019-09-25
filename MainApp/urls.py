from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home, name="home_page"),
    path('register/', views.Register, name="register_page"),
    path('login/', views.Login, name="login_page"),
    path('verify/<str:username>/<str:chars>', views.Verify, name="verify_page"),
    path('account/', views.Account, name="account_page"),
    path('logout/', views.Logout, name="logout_page"),
    path('forgetpassword/', views.Forget_password, name="forget_pass_page"),
    path("changepassword/<str:username>/<str:chars>", views.ChangePassword, name="change_pass_page"),
    path("editprofile/", views.EditProfile, name="edit_profile_page"),
    path("upload/", views.Upload, name="upload_page"),
    path("addquestion/", views.AddQuestion, name="add_question_page"),
    path("<str:question_url>/", views.Question_Answers, name="question_answers_page"),
    path("answer/<str:question_url>/", views.Answers, name="answer_page"),
    path("comment/<str:answer_id>/", views.Comments, name="comment_page"),
    path("profile/<str:username>", views.Profile, name="profile_page"),
    path("editquestion/<str:question_url>", views.EditQuestion, name="edit_question_page"),
    path("deletequestion/<str:question_url>", views.DeleteQuestion, name="delete_question_page"),
    path("<str:question_url>/editanswer/<str:answer_id>", views.EditAnswer, name="edit_answer_page"),
    path("<str:question_url>/deleteanswer/<str:answer_id>", views.DeleteAnswer, name="edit_answer_page"),
    path("<str:question_url>/editcomment/<str:comment_id>", views.EditComment, name="edit_comment_page"),
    path("<str:question_url>/deletecomment/<str:comment_id>", views.DeleteComment, name="delete_comment_page"),
    path("search/query/", views.Search, name="search"),
    path("deleteaccount/<int:user_id>", views.DeleteAccount, name="delete_account_page")
]