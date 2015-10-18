from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from server import views

urlpatterns = format_suffix_patterns([
    url(r'payment/', views.PaymentList.as_view()),
    url(r'twisponse/', views.Twisponse.as_view()),
    url(r'labourer-list/', views.LabourerList.as_view()),
    url(r'labourer-detail/', views.LabourerDetail.as_view()),
    url(r'contractor-list/', views.ContractorList.as_view()), 
    url(r'contractor-detail/', views.ContractorDetail.as_view()),
    url(r'labourer-search/', views.LabourerSearch.as_view()),
])

