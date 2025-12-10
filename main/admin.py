from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Profile, SocialLink, Skill, ExpertiseArea, Statistic,
    Project, ProjectCategory, ProjectImage, ProjectTechnology,
    ProjectFeature, TechnicalDetail, ContactMessage, Testimonial,
    BlogPost, SiteSettings
)

# --- Inlines ---

class SocialLinkInline(admin.TabularInline):
    model = SocialLink
    extra = 1

class SkillInline(admin.TabularInline):
    model = Skill
    extra = 1
    classes = ['collapse']

class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1

class ProjectTechnologyInline(admin.TabularInline):
    model = ProjectTechnology
    extra = 1

class ProjectFeatureInline(admin.StackedInline):
    model = ProjectFeature
    extra = 0
    classes = ['collapse']

class TechnicalDetailInline(admin.StackedInline):
    model = TechnicalDetail
    extra = 0
    classes = ['collapse']

# --- Model Admins ---

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'title', 'is_available', 'email')
    list_editable = ('is_available',)
    inlines = [SocialLinkInline, SkillInline]
    fieldsets = (
        ('Basic Info', {'fields': ('user', 'full_name', 'title', 'bio', 'tagline')}),
        ('Images', {'fields': ('profile_image', 'hero_image')}),
        ('Status', {'fields': ('is_available', 'status_text', 'years_experience')}),
        ('Contact', {'fields': ('email', 'phone', 'location', 'resume_file')}),
        ('Settings', {'fields': ('show_stats', 'show_tech_stack')}),
    )

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'is_featured', 'is_published', 'order')
    list_filter = ('status', 'is_featured', 'is_published', 'category')
    search_fields = ('title', 'short_description')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectTechnologyInline, ProjectFeatureInline, TechnicalDetailInline, ProjectImageInline]
    list_editable = ('order', 'is_featured', 'is_published')

@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'status', 'created_at', 'is_read')
    list_filter = ('status', 'is_read', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at', 'ip_address', 'user_agent')

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'published_at', 'view_count')
    list_filter = ('status', 'category')
    prepopulated_fields = {'slug': ('title',)}

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        # Prevent creating more than one settings object
        if self.model.objects.exists():
            return False
        return True

# Register remaining models simply
admin.site.register(ExpertiseArea)
admin.site.register(Statistic)
admin.site.register(Testimonial)