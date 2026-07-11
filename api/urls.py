from django.urls import path
from . import views

urlpatterns = [
    # Ommaviy endpointlar
    path('api/partners/', views.PartnerPublicList.as_view()),
    path('api/news/', views.NewsPublicList.as_view()),
    path('api/news/<str:slug>', views.NewsPublicDetail.as_view()),
    path('api/banners/', views.BannerPublicList.as_view()),

    # Admin endpointlar
    path('api/partners/admin', views.PartnerAdminListCreate.as_view()),
    path('api/partners/<int:pk>', views.PartnerAdminDetail.as_view()),
    path('api/news/admin', views.NewsAdminListCreate.as_view()),
    path('api/news/<int:pk>', views.NewsAdminDetail.as_view()),
    path('api/banners/admin', views.BannerAdminListCreate.as_view()),
    path('api/banners/<int:pk>', views.BannerAdminDetail.as_view()),
]