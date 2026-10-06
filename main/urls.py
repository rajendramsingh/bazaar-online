from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/', views.contact, name='contact'),
    path('listing/', views.listing, name='listing'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('my_listings/', views.my_listings, name="my_listings"),
    path('delete_listing/<int:id>/', views.delete_listing, name="delete_listing"),
    path('edit_listing/<int:id>/', views.edit_listing, name='edit_listing'),
    path('category/<str:category>/', views.category_listings, name='category_listings'),
    path('categories/', views.categories, name='categories'),
    path('search/', views.search, name='search'),
    path('listing/<int:id>/', views.listing_detail, name='listing_detail'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('notifications/', views.notifications, name='notifications'),
]