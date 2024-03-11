from django.urls import path


from .views import *
from candyApp import candy

app_name = "home"
urlpatterns = [
  *candy.path("", home, name="home"),
    *candy.path('blog-detail/<slug>', blog_detail, name="blog_detail"),

     *candy.path("transfer/", transfers, name="transfers"),
    *candy.path('blog-details/<slug>', blog_details, name="blog_details"),


    path("login/", login_view, name="login_view"),
    path("register/", register_view, name="register_view"),
    path("add-blog/", add_blog, name="add_blog"),
    path("see-blog/", see_blog, name="see_blog"),
    path("blog-delete/<id>", blog_delete, name="blog_delete"),
    path("blog-update/<slug>/", blog_update, name="blog_update"),
    path("logout-view/", logout_view, name="logout_view"),
    path("verify/<token>/", verify, name="verify")
]
