from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "EduHelp administration"
admin.site.site_title = "EduHelp admin"
admin.site.index_title = "Courses, users and approvals"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("", include("courses.urls")),
]
