from django.urls import path
from .views import TaskList, TaskDetail, TaskCreate, TaskUpdate, DeleteView, CustomLoginView, RegisterPage, TaskReorder
from django.contrib.auth.views import LogoutView
from base.views import home
from base.views import prediction
from base.views import monthly_income_prediction
from base.views import arima_prediction
from base.views import dashboard
from base.views import register
from base.views import user_login
from base.views import biogas_prediction
from base.views import logout_view
urlpatterns = [
    path('home/', home, name='home'),
    path('biogas_prediction/',biogas_prediction, name='biogas_prediction'),
    path('prediction/', prediction, name='prediction'),
    path('arima/', arima_prediction, name='arima_prediction'),
    path('monthly_income/', monthly_income_prediction, name='monthly_income_prediction'),
    path('dashboard/', dashboard, name='dashboard'),
    path('logout/', logout_view, name='logout'),
    path('register/', register, name='register'),
    path('', user_login, name='login'),
]
