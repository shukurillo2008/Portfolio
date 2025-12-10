from django.db import models
from django.contrib.auth.models import User
from django.core.validators import URLValidator, MinValueValidator, MaxValueValidator
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _


class TimeStampedModel(models.Model):
    """Abstract base model with created and updated timestamps"""
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(TimeStampedModel):
    """Main profile information for the portfolio owner"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='portfolio_profile')
    
    # Basic Information
    full_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200, help_text="e.g., Django Backend Developer")
    bio = models.TextField(help_text="Brief introduction about yourself")
    tagline = models.CharField(max_length=300, help_text="Main tagline displayed on hero section")
    
    # Profile Images
    profile_image = models.ImageField(upload_to='profile/', blank=True, null=True)
    hero_image = models.ImageField(upload_to='profile/hero/', blank=True, null=True)
    
    # Status
    is_available = models.BooleanField(default=True, help_text="Open to opportunities")
    status_text = models.CharField(max_length=100, default="Open to Opportunities")
    
    # Experience
    years_experience = models.PositiveIntegerField(default=0)
    
    # Contact Information
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=200, blank=True)
    
    # Resume
    resume_file = models.FileField(upload_to='resumes/', blank=True, null=True)
    
    # SEO
    meta_description = models.TextField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    # Display Settings
    show_stats = models.BooleanField(default=True)
    show_tech_stack = models.BooleanField(default=True)
    
    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
    
    def __str__(self):
        return self.full_name


class SocialLink(TimeStampedModel):
    """Social media and external links"""
    PLATFORM_CHOICES = [
        ('github', 'GitHub'),
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter'),
        ('email', 'Email'),
        ('website', 'Website'),
        ('stackoverflow', 'Stack Overflow'),
        ('medium', 'Medium'),
        ('dev', 'Dev.to'),
        ('other', 'Other'),
    ]
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='social_links')
    platform = models.CharField(max_length=50, choices=PLATFORM_CHOICES)
    url = models.URLField(validators=[URLValidator()])
    username = models.CharField(max_length=100, blank=True)
    icon_class = models.CharField(max_length=100, blank=True, help_text="CSS class for icon")
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'platform']
        verbose_name = _('Social Link')
        verbose_name_plural = _('Social Links')
    
    def __str__(self):
        return f"{self.profile.full_name} - {self.get_platform_display()}"


class Skill(TimeStampedModel):
    """Skills and technologies"""
    CATEGORY_CHOICES = [
        ('backend', 'Backend'),
        ('frontend', 'Frontend'),
        ('database', 'Database'),
        ('devops', 'DevOps'),
        ('tools', 'Tools'),
        ('other', 'Other'),
    ]
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='skills')
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    proficiency = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Proficiency level (0-100)"
    )
    icon = models.CharField(max_length=100, blank=True, help_text="Icon identifier or SVG path")
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['category', 'order', 'name']
        verbose_name = _('Skill')
        verbose_name_plural = _('Skills')
        unique_together = ['profile', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"


class ExpertiseArea(TimeStampedModel):
    """Areas of expertise displayed in About section"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='expertise_areas')
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100, blank=True)
    technologies = models.CharField(max_length=500, help_text="Comma-separated list of technologies")
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'title']
        verbose_name = _('Expertise Area')
        verbose_name_plural = _('Expertise Areas')
    
    def __str__(self):
        return self.title
    
    def get_technologies_list(self):
        """Returns technologies as a list"""
        return [tech.strip() for tech in self.technologies.split(',') if tech.strip()]


class Statistic(TimeStampedModel):
    """Portfolio statistics (uptime, response time, etc.)"""
    METRIC_CHOICES = [
        ('uptime', 'System Uptime'),
        ('response_time', 'Response Time'),
        ('api_calls', 'API Calls'),
        ('projects', 'Projects'),
        ('clients', 'Clients'),
        ('custom', 'Custom Metric'),
    ]
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='statistics')
    metric_type = models.CharField(max_length=50, choices=METRIC_CHOICES)
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=50, help_text="e.g., 99.9%, 50ms, 1M+")
    description = models.CharField(max_length=200)
    icon = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['order', 'metric_type']
        verbose_name = _('Statistic')
        verbose_name_plural = _('Statistics')
    
    def __str__(self):
        return f"{self.label}: {self.value}"


class ProjectCategory(TimeStampedModel):
    """Categories for organizing projects"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = _('Project Category')
        verbose_name_plural = _('Project Categories')
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Project(TimeStampedModel):
    """Portfolio projects"""
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('planned', 'Planned'),
        ('archived', 'Archived'),
    ]
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='projects')
    
    # Basic Information
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    subtitle = models.CharField(max_length=300, blank=True)
    short_description = models.TextField(max_length=500)
    full_description = models.TextField()
    
    # Images
    thumbnail = models.ImageField(upload_to='projects/thumbnails/')
    featured_image = models.ImageField(upload_to='projects/featured/', blank=True, null=True)
    
    # Classification
    category = models.ForeignKey(ProjectCategory, on_delete=models.SET_NULL, null=True, related_name='projects')
    tags = models.CharField(max_length=500, help_text="Comma-separated tags")
    
    # Status and Dates
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='completed')
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    duration = models.CharField(max_length=50, blank=True, help_text="e.g., 3 months")
    
    # Project Details
    team_size = models.PositiveIntegerField(default=1)
    role = models.CharField(max_length=200, blank=True)
    client = models.CharField(max_length=200, blank=True)
    user_count = models.CharField(max_length=50, blank=True, help_text="e.g., 10,000+")
    
    # Links
    github_url = models.URLField(blank=True, validators=[URLValidator()])
    live_url = models.URLField(blank=True, validators=[URLValidator()])
    documentation_url = models.URLField(blank=True, validators=[URLValidator()])
    
    # Display Settings
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    # SEO
    meta_description = models.TextField(max_length=160, blank=True)
    
    class Meta:
        ordering = ['-is_featured', 'order', '-created_at']
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def get_tags_list(self):
        """Returns tags as a list"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]


class ProjectImage(TimeStampedModel):
    """Additional images for project gallery"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='projects/gallery/')
    caption = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(max_length=200)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = _('Project Image')
        verbose_name_plural = _('Project Images')
    
    def __str__(self):
        return f"{self.project.title} - Image {self.order}"


class ProjectTechnology(TimeStampedModel):
    """Technologies used in a project"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='technologies')
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=50, blank=True)
    icon = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name = _('Project Technology')
        verbose_name_plural = _('Project Technologies')
        unique_together = ['project', 'name']
    
    def __str__(self):
        return f"{self.project.title} - {self.name}"


class ProjectFeature(TimeStampedModel):
    """Key features of a project"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='features')
    title = models.CharField(max_length=200)
    description = models.TextField()
    icon = models.CharField(max_length=100, blank=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = _('Project Feature')
        verbose_name_plural = _('Project Features')
    
    def __str__(self):
        return f"{self.project.title} - {self.title}"


class TechnicalDetail(TimeStampedModel):
    """Technical architecture details for a project"""
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='technical_details')
    title = models.CharField(max_length=200)
    content = models.TextField()
    code_snippet = models.TextField(blank=True)
    language = models.CharField(max_length=50, blank=True, help_text="Programming language for syntax highlighting")
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
        verbose_name = _('Technical Detail')
        verbose_name_plural = _('Technical Details')
    
    def __str__(self):
        return f"{self.project.title} - {self.title}"


class ContactMessage(TimeStampedModel):
    """Messages received through contact form"""
    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    ]
    
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300, blank=True)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    is_read = models.BooleanField(default=False)
    replied_at = models.DateTimeField(blank=True, null=True)
    notes = models.TextField(blank=True, help_text="Internal notes")
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = _('Contact Message')
        verbose_name_plural = _('Contact Messages')
    
    def __str__(self):
        return f"{self.name} - {self.created_at.strftime('%Y-%m-%d')}"


class Testimonial(TimeStampedModel):
    """Client testimonials and reviews"""
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='testimonials')
    
    # Client Information
    client_name = models.CharField(max_length=200)
    client_title = models.CharField(max_length=200)
    client_company = models.CharField(max_length=200, blank=True)
    client_image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    
    # Testimonial Content
    content = models.TextField()
    rating = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating out of 5"
    )
    
    # Associated Project
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True, blank=True, related_name='testimonials')
    
    # Display Settings
    is_featured = models.BooleanField(default=False)
    is_published = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['-is_featured', 'order', '-created_at']
        verbose_name = _('Testimonial')
        verbose_name_plural = _('Testimonials')
    
    def __str__(self):
        return f"{self.client_name} - {self.client_company}"


class BlogPost(TimeStampedModel):
    """Blog posts and articles"""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='blog_posts')
    
    # Content
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    excerpt = models.TextField(max_length=500)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='blog/')
    
    # Classification
    category = models.CharField(max_length=100)
    tags = models.CharField(max_length=500, help_text="Comma-separated tags")
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(blank=True, null=True)
    
    # Engagement
    view_count = models.PositiveIntegerField(default=0)
    read_time = models.PositiveIntegerField(help_text="Estimated read time in minutes")
    
    # SEO
    meta_description = models.TextField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    
    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = _('Blog Post')
        verbose_name_plural = _('Blog Posts')
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)


class SiteSettings(TimeStampedModel):
    """Global site settings (singleton model)"""
    site_name = models.CharField(max_length=200, default="Portfolio")
    site_tagline = models.CharField(max_length=300)
    footer_text = models.CharField(max_length=300)
    copyright_text = models.CharField(max_length=200)
    
    # Analytics
    google_analytics_id = models.CharField(max_length=100, blank=True)
    google_tag_manager_id = models.CharField(max_length=100, blank=True)
    
    # Email Settings
    contact_email = models.EmailField()
    notification_email = models.EmailField(blank=True)
    
    # Features
    enable_blog = models.BooleanField(default=False)
    enable_contact_form = models.BooleanField(default=True)
    enable_testimonials = models.BooleanField(default=True)
    
    # Maintenance
    maintenance_mode = models.BooleanField(default=False)
    maintenance_message = models.TextField(blank=True)
    
    class Meta:
        verbose_name = _('Site Settings')
        verbose_name_plural = _('Site Settings')
    
    def __str__(self):
        return self.site_name
    
    def save(self, *args, **kwargs):
        # Ensure only one instance exists
        self.pk = 1
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        pass
    
    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj