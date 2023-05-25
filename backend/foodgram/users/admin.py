from django.contrib import admin
from django.contrib.auth.hashers import make_password

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'username',
        'first_name',
        'last_name',
        'email',
        'password',
        'is_blocked'
    ]
    ordering = ('id',)
    list_editable = ('password', )
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')
    list_display_links = ('username', 'id',)

    def save_model(self, request, obj, form, change):
        if 'password' in form.changed_data:
            obj.password = make_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author')
    list_editable = ('user', 'author')
