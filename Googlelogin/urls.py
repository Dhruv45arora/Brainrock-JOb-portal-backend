from django.urls import path
from .views import GoogleLoginView,CustomUserView,Getview,LoginView,UpdateView,DeltePostByUserView
from .views import (PostedJobListCreateView, PostedJobDetailView,JobTitleSuggestionView,SavedPostsByUserView,Savedpost,PlanListCreateView, PlanDetailView,
    SubscriptionListCreateView, SubscriptionDetailView)
urlpatterns = [
    path('Savedpost/<str:user_id>/',SavedPostsByUserView.as_view(), name='Saved-post-By-user'),
    path('Savedpost/<str:job_id>/',DeltePostByUserView.as_view(), name='Saved-post-By-user'),
    path('Saved-post/',Savedpost.as_view(), name='Saved-post'),
    path('poste-job/',PostedJobListCreateView.as_view(), name='posted-jobs-list-create'),
    path('posted-jobs/<int:pk>/',PostedJobDetailView.as_view(), name='posted-job-detail'),
    path('google-login/',GoogleLoginView.as_view(), name='google-login'),
    path('Registerpost/',CustomUserView.as_view(), name='Registration-post'),
    path('Userdata/<int:pk>/',Getview.as_view(), name='get-object'),
    path('login/', LoginView.as_view(), name='get-object'),
    path('update/<int:pk>/',UpdateView.as_view(), name='get-object'),
    path('jobs/suggestions/',JobTitleSuggestionView.as_view(), name='job-title-suggestions'),
    path('plans/', PlanListCreateView.as_view(), name='plan-list-create'),
    path('plans/<str:plan_id>/', PlanDetailView.as_view(), name='plan-detail'), 
    path('subscriptions/', SubscriptionListCreateView.as_view(), name='sub-list-create'),
    path('subscriptions/<str:employee_id>/', SubscriptionDetailView.as_view(), name='sub-detail'),
]


    

