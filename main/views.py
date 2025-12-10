from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView, CreateView
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json

from .models import (
    Profile, SocialLink, Skill, ExpertiseArea, Statistic,
    Project, ProjectCategory, ProjectImage, ProjectTechnology,
    ProjectFeature, TechnicalDetail, ContactMessage, Testimonial,
    BlogPost, SiteSettings
)
from .forms import ContactForm


# ==================== Home/Index View ====================
class HomeView(TemplateView):
    """Main landing page with all sections"""
    template_name = 'portfolio/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the main profile (assuming single user portfolio)
        try:
            profile = Profile.objects.select_related('user').prefetch_related(
                'social_links',
                'skills',
                'expertise_areas',
                'statistics'
            ).first()
            
            if not profile:
                # Create a default profile if none exists
                from django.contrib.auth.models import User
                user = User.objects.first() or User.objects.create_user('admin')
                profile = Profile.objects.create(
                    user=user,
                    full_name="John Doe",
                    title="Django Backend Developer",
                    bio="Backend developer specializing in Django",
                    email="contact@example.com"
                )
        except Exception as e:
            profile = None
        
        # Get featured projects
        featured_projects = Project.objects.filter(
            is_published=True,
            is_featured=True
        ).prefetch_related('technologies')[:2]
        
        # Get skills organized by category
        skills_by_category = {}
        if profile:
            skills = profile.skills.filter(is_featured=True)
            for skill in skills:
                category = skill.get_category_display()
                if category not in skills_by_category:
                    skills_by_category[category] = []
                skills_by_category[category].append(skill)
        
        # Get statistics
        statistics = Statistic.objects.filter(
            profile=profile,
            is_active=True
        ).order_by('order')[:4] if profile else []
        
        # Get social links
        social_links = SocialLink.objects.filter(
            profile=profile,
            is_active=True
        ).order_by('order') if profile else []
        
        # Get expertise areas
        expertise_areas = ExpertiseArea.objects.filter(
            profile=profile
        ).order_by('order')[:3] if profile else []
        
        # Get testimonials
        testimonials = Testimonial.objects.filter(
            profile=profile,
            is_published=True
        ).order_by('-is_featured', 'order')[:3] if profile else []
        
        # Get site settings
        site_settings = SiteSettings.load()
        
        context.update({
            'profile': profile,
            'featured_projects': featured_projects,
            'skills_by_category': skills_by_category,
            'statistics': statistics,
            'social_links': social_links,
            'expertise_areas': expertise_areas,
            'testimonials': testimonials,
            'site_settings': site_settings,
            'contact_form': ContactForm(),
        })
        
        return context


# ==================== Projects Views ====================
class ProjectListView(ListView):
    """List all projects with filtering and pagination"""
    model = Project
    template_name = 'portfolio/projects-list.html'
    context_object_name = 'projects'
    paginate_by = 9
    
    def get_queryset(self):
        queryset = Project.objects.filter(
            is_published=True
        ).select_related('category').prefetch_related('technologies')
        
        # Filter by category
        category_slug = self.request.GET.get('category')
        if category_slug:
            queryset = queryset.filter(category__slug=category_slug)
        
        # Filter by tag
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__icontains=tag)
        
        # Filter by status
        status = self.request.GET.get('status')
        if status and status in dict(Project.STATUS_CHOICES).keys():
            queryset = queryset.filter(status=status)
        
        # Search functionality
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(short_description__icontains=search_query) |
                Q(tags__icontains=search_query)
            )
        
        return queryset.order_by('-is_featured', 'order', '-created_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get profile
        profile = Profile.objects.first()
        
        # Get all categories with project count
        categories = ProjectCategory.objects.annotate(
            project_count=Count('projects', filter=Q(projects__is_published=True))
        ).order_by('order')
        
        # Get project counts by status
        project_counts = {
            'total': Project.objects.filter(is_published=True).count(),
            'completed': Project.objects.filter(is_published=True, status='completed').count(),
            'in_progress': Project.objects.filter(is_published=True, status='in_progress').count(),
            'open_source': Project.objects.filter(
                is_published=True
            ).exclude(github_url='').count(),
        }
        
        # Get all unique tags
        all_projects = Project.objects.filter(is_published=True)
        all_tags = set()
        for project in all_projects:
            all_tags.update(project.get_tags_list())
        
        context.update({
            'profile': profile,
            'categories': categories,
            'project_counts': project_counts,
            'all_tags': sorted(all_tags),
            'current_category': self.request.GET.get('category', ''),
            'current_tag': self.request.GET.get('tag', ''),
            'search_query': self.request.GET.get('search', ''),
            'site_settings': SiteSettings.load(),
        })
        
        return context


class ProjectDetailView(DetailView):
    """Detailed view of a single project"""
    model = Project
    template_name = 'portfolio/project-detail.html'
    context_object_name = 'project'
    slug_field = 'slug'
    
    def get_queryset(self):
        return Project.objects.filter(
            is_published=True
        ).select_related('category', 'profile').prefetch_related(
            'images',
            'technologies',
            'features',
            'technical_details',
            'testimonials'
        )
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        project = self.object
        
        # Get related projects (same category or similar tags)
        related_projects = Project.objects.filter(
            is_published=True
        ).exclude(id=project.id).filter(
            Q(category=project.category) |
            Q(tags__in=project.get_tags_list())
        ).distinct()[:3]
        
        # Get profile
        profile = Profile.objects.first()
        
        context.update({
            'related_projects': related_projects,
            'profile': profile,
            'site_settings': SiteSettings.load(),
        })
        
        return context


# ==================== About/Profile Views ====================
class AboutView(TemplateView):
    """About page with detailed profile information"""
    template_name = 'portfolio/about.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        profile = Profile.objects.select_related('user').prefetch_related(
            'skills',
            'expertise_areas',
            'social_links'
        ).first()
        
        # Get all skills organized by category
        skills_by_category = {}
        if profile:
            skills = profile.skills.all()
            for skill in skills:
                category = skill.get_category_display()
                if category not in skills_by_category:
                    skills_by_category[category] = []
                skills_by_category[category].append(skill)
        
        # Get expertise areas
        expertise_areas = ExpertiseArea.objects.filter(
            profile=profile
        ).order_by('order') if profile else []
        
        # Get project count
        project_count = Project.objects.filter(
            profile=profile,
            is_published=True
        ).count() if profile else 0
        
        # Get client count (unique clients from projects)
        client_count = Project.objects.filter(
            profile=profile,
            is_published=True
        ).exclude(client='').values('client').distinct().count() if profile else 0
        
        context.update({
            'profile': profile,
            'skills_by_category': skills_by_category,
            'expertise_areas': expertise_areas,
            'project_count': project_count,
            'client_count': client_count,
            'site_settings': SiteSettings.load(),
        })
        
        return context


# ==================== Contact Views ====================
class ContactView(TemplateView):
    """Contact page with form"""
    template_name = 'portfolio/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = Profile.objects.first()
        
        context.update({
            'profile': profile,
            'contact_form': ContactForm(),
            'site_settings': SiteSettings.load(),
        })
        
        return context


@require_http_methods(["POST"])
def contact_submit(request):
    """Handle contact form submission"""
    form = ContactForm(request.POST)
    
    if form.is_valid():
        # Create contact message
        contact_message = ContactMessage.objects.create(
            name=form.cleaned_data['name'],
            email=form.cleaned_data['email'],
            subject=form.cleaned_data.get('subject', ''),
            message=form.cleaned_data['message'],
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        )
        
        # Send email notification
        try:
            site_settings = SiteSettings.load()
            notification_email = site_settings.notification_email or site_settings.contact_email
            
            send_mail(
                subject=f'New Contact Form Submission: {contact_message.subject or "No Subject"}',
                message=f"""
                New message from portfolio contact form:
                
                Name: {contact_message.name}
                Email: {contact_message.email}
                Subject: {contact_message.subject}
                
                Message:
                {contact_message.message}
                
                Sent at: {contact_message.created_at}
                IP: {contact_message.ip_address}
                """,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[notification_email],
                fail_silently=True,
            )
        except Exception as e:
            # Log error but don't fail the request
            print(f"Error sending notification email: {e}")
        
        # AJAX response
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your message! I will get back to you soon.'
            })
        
        # Regular response
        messages.success(request, 'Thank you for your message! I will get back to you soon.')
        return redirect('contact')
    
    # Handle form errors
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': False,
            'errors': form.errors
        }, status=400)
    
    messages.error(request, 'Please correct the errors in the form.')
    return redirect('contact')


# ==================== Blog Views ====================
class BlogListView(ListView):
    """List all blog posts"""
    model = BlogPost
    template_name = 'portfolio/blog-list.html'
    context_object_name = 'posts'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('profile')
        
        # Filter by category
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category__iexact=category)
        
        # Filter by tag
        tag = self.request.GET.get('tag')
        if tag:
            queryset = queryset.filter(tags__icontains=tag)
        
        # Search
        search_query = self.request.GET.get('search')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(excerpt__icontains=search_query) |
                Q(content__icontains=search_query)
            )
        
        return queryset.order_by('-published_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if blog is enabled
        site_settings = SiteSettings.load()
        if not site_settings.enable_blog:
            raise Http404("Blog is not enabled")
        
        profile = Profile.objects.first()
        
        # Get all categories
        all_posts = BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        )
        categories = all_posts.values_list('category', flat=True).distinct()
        
        # Get all tags
        all_tags = set()
        for post in all_posts:
            all_tags.update([tag.strip() for tag in post.tags.split(',') if tag.strip()])
        
        context.update({
            'profile': profile,
            'categories': sorted(categories),
            'all_tags': sorted(all_tags),
            'current_category': self.request.GET.get('category', ''),
            'current_tag': self.request.GET.get('tag', ''),
            'search_query': self.request.GET.get('search', ''),
            'site_settings': site_settings,
        })
        
        return context


class BlogDetailView(DetailView):
    """Detailed view of a single blog post"""
    model = BlogPost
    template_name = 'portfolio/blog-detail.html'
    context_object_name = 'post'
    slug_field = 'slug'
    
    def get_queryset(self):
        return BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).select_related('profile')
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        
        # Increment view count
        obj.view_count += 1
        obj.save(update_fields=['view_count'])
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Check if blog is enabled
        site_settings = SiteSettings.load()
        if not site_settings.enable_blog:
            raise Http404("Blog is not enabled")
        
        post = self.object
        profile = Profile.objects.first()
        
        # Get related posts
        related_posts = BlogPost.objects.filter(
            status='published',
            published_at__lte=timezone.now()
        ).exclude(id=post.id).filter(
            Q(category=post.category) |
            Q(tags__in=post.tags)
        ).distinct()[:3]
        
        context.update({
            'profile': profile,
            'related_posts': related_posts,
            'site_settings': site_settings,
        })
        
        return context


# ==================== API Endpoints (JSON) ====================
def api_profile(request):
    """API endpoint to get profile data"""
    profile = Profile.objects.select_related('user').prefetch_related(
        'social_links',
        'skills',
        'expertise_areas',
        'statistics'
    ).first()
    
    if not profile:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    data = {
        'full_name': profile.full_name,
        'title': profile.title,
        'bio': profile.bio,
        'tagline': profile.tagline,
        'email': profile.email,
        'location': profile.location,
        'years_experience': profile.years_experience,
        'is_available': profile.is_available,
        'status_text': profile.status_text,
        'social_links': [
            {
                'platform': link.get_platform_display(),
                'url': link.url,
                'username': link.username,
            }
            for link in profile.social_links.filter(is_active=True)
        ],
        'skills': [
            {
                'name': skill.name,
                'category': skill.get_category_display(),
                'proficiency': skill.proficiency,
            }
            for skill in profile.skills.all()
        ],
    }
    
    return JsonResponse(data)


def api_projects(request):
    """API endpoint to get all projects"""
    projects = Project.objects.filter(
        is_published=True
    ).select_related('category').prefetch_related('technologies')
    
    # Filter by category
    category = request.GET.get('category')
    if category:
        projects = projects.filter(category__slug=category)
    
    data = [
        {
            'id': project.id,
            'title': project.title,
            'slug': project.slug,
            'short_description': project.short_description,
            'category': project.category.name if project.category else None,
            'status': project.get_status_display(),
            'tags': project.get_tags_list(),
            'technologies': [tech.name for tech in project.technologies.all()],
            'github_url': project.github_url,
            'live_url': project.live_url,
            'is_featured': project.is_featured,
        }
        for project in projects
    ]
    
    return JsonResponse({'projects': data})


def api_project_detail(request, slug):
    """API endpoint to get single project details"""
    project = get_object_or_404(
        Project.objects.filter(is_published=True).prefetch_related(
            'technologies', 'features', 'images'
        ),
        slug=slug
    )
    
    data = {
        'id': project.id,
        'title': project.title,
        'slug': project.slug,
        'short_description': project.short_description,
        'full_description': project.full_description,
        'status': project.get_status_display(),
        'tags': project.get_tags_list(),
        'team_size': project.team_size,
        'duration': project.duration,
        'role': project.role,
        'client': project.client,
        'user_count': project.user_count,
        'github_url': project.github_url,
        'live_url': project.live_url,
        'documentation_url': project.documentation_url,
        'technologies': [
            {
                'name': tech.name,
                'version': tech.version,
            }
            for tech in project.technologies.all()
        ],
        'features': [
            {
                'title': feature.title,
                'description': feature.description,
            }
            for feature in project.features.all()
        ],
        'images': [
            {
                'url': request.build_absolute_uri(img.image.url) if img.image else None,
                'caption': img.caption,
                'alt_text': img.alt_text,
            }
            for img in project.images.all()
        ],
    }
    
    return JsonResponse(data)


def api_statistics(request):
    """API endpoint to get portfolio statistics"""
    profile = Profile.objects.first()
    
    if not profile:
        return JsonResponse({'error': 'Profile not found'}, status=404)
    
    statistics = Statistic.objects.filter(
        profile=profile,
        is_active=True
    ).order_by('order')
    
    data = [
        {
            'metric_type': stat.get_metric_type_display(),
            'label': stat.label,
            'value': stat.value,
            'description': stat.description,
        }
        for stat in statistics
    ]
    
    return JsonResponse({'statistics': data})


# ==================== Resume Download ====================
def download_resume(request):
    """Download resume file"""
    profile = Profile.objects.first()
    
    if not profile or not profile.resume_file:
        messages.error(request, 'Resume not available.')
        return redirect('home')
    
    response = HttpResponse(profile.resume_file, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{profile.full_name}_Resume.pdf"'
    
    return response


# ==================== Helper Functions ====================
def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# ==================== Error Views ====================
def handler404(request, exception):
    """Custom 404 error page"""
    profile = Profile.objects.first()
    return render(request, 'portfolio/404.html', {
        'profile': profile,
        'site_settings': SiteSettings.load(),
    }, status=404)


def handler500(request):
    """Custom 500 error page"""
    profile = Profile.objects.first()
    return render(request, 'portfolio/500.html', {
        'profile': profile,
        'site_settings': SiteSettings.load(),
    }, status=500)