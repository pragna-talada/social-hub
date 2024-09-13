"""
URL configuration for social_hub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

import default.views


urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/1/sign-up/", default.views.SignupView.as_view(), name="sign-up"),
    path("api/1/login/", default.views.LoginView.as_view(), name="login"),
    path("api/1/logout/", default.views.LogoutView.as_view(), name="logout"),
    path("api/1/search-users/", default.views.UserSearchView.as_view(), name="search-users"),

    path("api/1/friend-request/send/", default.views.SendFriendRequestView.as_view(), name='send_friend_request'),
    path("api/1/friend-request/<int:id>/action/", default.views.AcceptRejectFriendRequestView.as_view(), name='accept_reject_friend_request'),
    path("api/1/friends/", default.views.ListFriendsView.as_view(), name='list_friends'),
    path("api/1/friend-requests/pending/", default.views.PendingFriendRequestsView.as_view(), name='pending_friend_requests'),

    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),

]
