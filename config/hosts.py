from django_hosts import patterns, host

host_patterns = patterns(
    '',
    host(r'www', 'config.urls', name='www'),
    host(r'api', 'api_app.urls', name='api'),
    host(r'team', 'team.urls', name='team'),
)