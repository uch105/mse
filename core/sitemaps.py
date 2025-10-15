from django.contrib.sitemaps import Sitemap
from django.urls import reverse

class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = "weekly"

    def items(self):
        return ['index', 'about', 'materials', 'resources', 'blogs', 'pricing', 'api-docs', 'privacy', 'terms', 'presses', 'careers']

    def location(self, item):
        return reverse(item)