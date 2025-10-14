from django.contrib import admin
from .models import *

admin.site.site_header = "MSE Admin"
admin.site.site_title = "MSE Admin Portal"
admin.site.index_title = "Welcome to MSE Admin Portal"

admin.site.register(Profile)
admin.site.register(Career)
admin.site.register(CareerApplication)
admin.site.register(PressRelease)
admin.site.register(TeamMember)