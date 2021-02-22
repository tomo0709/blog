from django.urls import path
from . import views

app_name = 'discussion'
urlpatterns = [
    
    # /disc/ -> Discussion List
    path('', views.DiscList.as_view(), name='disc_list'),
    
    # /disc/disc_create/ -> Discussion Create
    path('disc_create/', views.DiscCreate.as_view(), name='disc_create'),
    
    # /disc/disc_update/1/ -> Discussion #1 Update
    path('disc_update/<int:pk>/', views.DiscUpdate.as_view(), name='disc_update'),
    
    # /disc/disc_delete/1/ -> Discussion #1 Delete
    path('disc_delete/<int:pk>/', views.DiscDelete.as_view(), name='disc_delete'),
    
    # /disc/usr_list/1/ -> DiscUser List for Discussion #1
    path('usr_list/<int:disc_id>/', views.UsrList.as_view(), name='usr_list'),
    
    # /disc/usr_update/1/ -> DiscUser #1 Update
    path('usr_update/<int:pk>/', views.UsrUpdate.as_view(), name='usr_update'),
    
    # /disc/usr_delete/1/ -> DiscUser #1 Delete
    path('usr_delete/<int:pk>/', views.UsrDelete.as_view(), name='usr_delete'),

    # /disc/invt_create/1/ -> Invitation Create for Discussion #1
    path('invt_create/<int:disc_id>/', views.InvtCreate.as_view(), name='invt_create'),

    # /disc/invt_delete/1/{usr_list|disc_list}/ -> Invitation #1 Delete
    path('invt_delete/<int:pk>/<str:from>/', views.InvtDelete.as_view(), name='invt_delete'),

    # /disc/disc_join/1/ -> Join to Discussion via Invitation #1
    path('disc_join/<int:invt_id>/', views.DiscJoin.as_view(), name='disc_join'),
]