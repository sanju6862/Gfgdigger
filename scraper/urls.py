from django.urls import path
from . import views

urlpatterns = [
    path('search/', views.search_and_save_links, name='search'),
    path('handle_link_action/', views.handle_link_action, name='handle_link_action'),
    path('community/dashboard/', views.community_dashboard, name='community_dashboard'),
    path('rate/<int:link_id>/', views.rate_link, name='rate_link'),
    path('add/<int:link_id>/', views.add_to_dashboard, name='add_to_dashboard'),
    path('add_note_to_link/<int:link_id>/', views.add_note_to_link, name='add_note_to_link'),

]
