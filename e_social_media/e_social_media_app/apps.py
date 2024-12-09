from django.apps import AppConfig


class ESocialMediaAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'e_social_media_app'

    def ready(self):
        import e_social_media_app.signals