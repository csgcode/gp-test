from django.urls import path
from apps.accounts.api.views import FacebookLoginView, PagesListView, PageUpdateView

app_name = 'accounts'

urlpatterns = [
    path('fb-login/', FacebookLoginView.as_view(), name='fb-login'),
    path('fb-pages-list/', PagesListView.as_view(), name='fb-list'),
    path('fb-page-update/', PageUpdateView.as_view(), name='fb-update'),

]