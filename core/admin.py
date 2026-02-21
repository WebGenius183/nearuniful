from django.contrib import admin
from .models import University, Apartment, Agent, ApartmentImage, Amenity, Distance, State, Period, ApartmentType

class ApartmentImageInline(admin.TabularInline):
    model = ApartmentImage
    extra = 1

class ApartmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'university', 'agent', 'price', 'is_available', 'is_approved', 'is_featured')
    list_filter = ('is_available', 'is_approved', 'is_featured', 'university', 'apartment_type')
    search_fields = ('title', 'description', 'address', 'agent__user__username', 'university__name')
    inlines = [ApartmentImageInline]
    ordering = ('-is_featured', '-created_at')

class AgentAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'whatsapp_number', 'verified')
    search_fields = ('user__username', 'user__email', 'phone_number', 'whatsapp_number')
    list_filter = ('verified',)

admin.site.register(Agent, AgentAdmin)
admin.site.register(University)
admin.site.register(Apartment, ApartmentAdmin)
admin.site.register(Period)
admin.site.register(ApartmentType)
admin.site.register(State)
admin.site.register(Amenity)
admin.site.register(Distance)