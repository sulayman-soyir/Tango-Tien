from django.contrib import admin
from rango.models import Category,Page
from rango.models import UserProfile



class CategoryAdmin(admin.ModelAdmin):
    #value是元组
    prepopulated_fields = {'slug':('name',)}




# Register your models here.
admin.site.register(Category,CategoryAdmin)
admin.site.register(Page)
admin.site.register(UserProfile)
