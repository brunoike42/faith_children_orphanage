from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from causes.models import Cause
from events.models import Event
from blog.models import Post
from .models import HeroImage

admin.site.register(HeroImage)

schema_view = get_schema_view(
    openapi.Info(
        title="Mercy Works API",
        default_version='v1',
        description="RESTful API for Mercy Works Charity Organization — Uganda",
        contact=openapi.Contact(email="admin@mercyworks.org.ug"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

def home(request):
    causes = Cause.objects.filter(is_active=True, is_featured=True)[:3]
    if causes.count() < 3:
        causes = Cause.objects.filter(is_active=True)[:3]

    events = Event.objects.filter(is_active=True).order_by('-start_date', '-start_time')[:3]
    posts = Post.objects.filter(is_published=True)[:3]

    hero_images = HeroImage.objects.filter(is_active=True)

    return render(request, 'home.html', {
        'causes': causes,
        'events': events,
        'posts': posts,
        'hero_images': hero_images,
    })
    
def about(request):
    return render(request, 'about.html')

def services(request):
    services_default = [
        
        ('heart-pulse','Medical Outreach','Free medical camps and healthcare services to rural communities'),
        ('book','Education Support','Scholarships and school supply programs for underprivileged children'),
        ('basket','Food Relief','Feeding programs and nutritional support for vulnerable families'),
        ('house-heart','Shelter Program','Building and renovating homes for the homeless and displaced'),
        ('droplet','Clean Water','Borehole drilling and water sanitation projects'),
        ('people','Community Development','Skills training and economic empowerment programs'),
    ]
    
    return render(request, 'services.html', {'services_default': services_default})


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('about/', about, name='about'),
    path('services/', services, name='services'),
    path('contact/', include('donations.urls')),  # Contact is handled by donations app
    path('accounts/', include('accounts.urls')),
    path('causes/', include('causes.urls')),
    path('events/', include('events.urls')),
    path('blog/', include('blog.urls')),
    path('donations/', include('donations.urls')),
    path('volunteers/', include('volunteers.urls')),
    # REST API
    path('api/', include('causes.api_urls')),
    path('api/', include('donations.api_urls')),
    path('api/', include('volunteers.api_urls')),
    path('api/', include('blog.api_urls')),
    path('api/', include('accounts.api_urls')),
    # Swagger
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='redoc'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
