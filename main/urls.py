from django.urls import path
from . import views

# Optional: Add an app_name for namespacing URLs (e.g., 'portfolio:home')
# app_name = 'portfolio'

urlpatterns = [
    # --- Main Pages ---
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.AboutView.as_view(), name='about'),
    path('contact/', views.ContactView.as_view(), name='contact'),

    # --- Functional Actions ---
    path('contact/submit/', views.contact_submit, name='contact_submit'),
    path('resume/download/', views.download_resume, name='download_resume'),

    # --- Projects ---
    path('projects/', views.ProjectListView.as_view(), name='projects_list'),
    path('projects/<slug:slug>/', views.ProjectDetailView.as_view(), name='project_detail'),

    # --- Blog ---
    path('blog/', views.BlogListView.as_view(), name='blog_list'),
    path('blog/<slug:slug>/', views.BlogDetailView.as_view(), name='blog_detail'),

    # --- API Endpoints ---
    path('api/profile/', views.api_profile, name='api_profile'),
    path('api/projects/', views.api_projects, name='api_projects'),
    path('api/projects/<slug:slug>/', views.api_project_detail, name='api_project_detail'),
    path('api/stats/', views.api_statistics, name='api_statistics'),
]