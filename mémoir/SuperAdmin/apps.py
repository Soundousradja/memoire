from django.apps import AppConfig


class SuperadminConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'SuperAdmin'
class SuperAdminConfig(AppConfig):
    name = 'SuperAdmin'

    def ready(self):
        import SuperAdmin.models