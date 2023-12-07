from django.shortcuts import render, redirect
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

# Imports for Reordering Feature
from django.views import View
from django.shortcuts import redirect
from django.db import transaction

from .models import Task
from .forms import PositionForm
import joblib
from datetime import datetime
from .forms import*

from django.shortcuts import render 

class CustomLoginView(LoginView):
    template_name = 'base/login.html'
    fields = '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('home')


class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')

def home(request):
    biogas_data = {
        'biogas_generated': 500,  # Example data, replace with your own
        'other_info': 'Other relevant information',
    }
    return render(request, 'base/home.html', {'biogas_data': biogas_data})


    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)

from django.shortcuts import render
from django.http import HttpResponse
import joblib

def load_ridge_model():
    model_path = os.path.join('ml_models', 'ridge_logistic_model.pkl')
    with open(model_path, 'rb') as file:
        loaded_model = pickle.load(file)
    return loaded_model

from django.shortcuts import render

from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import pickle
import os
from sklearn.linear_model import LinearRegression
from django.views.decorators.csrf import csrf_exempt
import json

def prediction(request):
    return render(request, 'base/prediciton.html')


def biogas_prediction(request):
    linear_model_path = "C:\\Users\\DELL\\Downloads\\todo_List (1)\\todo_List\\base\ml_models\\linear_regression_model.pkl"
    model_path = "C:\\Users\\DELL\\Downloads\\todo_List (1)\\todo_List\\base\\ml_models\\ridge_logistic_model.pkl"

    if os.path.exists(linear_model_path) and os.path.exists(model_path):
        with open(linear_model_path, 'rb') as file:
            linear_model = pickle.load(file)

        with open(model_path, 'rb') as file:
            model = pickle.load(file)
    else:
        return HttpResponse("Model files not found. Make sure the path is correct.")

    if request.method == 'POST':
        wet_waste = float(request.POST.get('wet_waste', 0.0))
        biogas_generated = float(request.POST.get('biogas_generated', 0.0))
        biogas_generated_litter = biogas_generated/1000
        expected_electricity = biogas_generated * 2  # 1 m³ biogas = 2 kWh

        prediction = model.predict([[wet_waste, biogas_generated, expected_electricity]])

        if prediction[0] == 1:
            prediction_text = "Electricity is Sufficient"
            extra_info = None
        else:
            prediction_text = "Electricity is Not Sufficient"
            current_electricity_needed = 40 
            additional_electricity_needed = current_electricity_needed - expected_electricity
            elec_kwh = additional_electricity_needed * 0.001
            biogas_cubic =elec_kwh/2
            biogas_liters = biogas_cubic*1000


            wet_waste_prediction = linear_model.predict([[biogas_liters]])

            extra_info = {
                "additional_wet_waste_needed_liters": biogas_liters,
                "wet_waste_prediction": wet_waste_prediction[0][0]
            }

        return render(request, 'base/result.html', {
            "prediction_text": prediction_text,
            "extra_info": extra_info,
            "wet_waste": wet_waste,
            "biogas_generated": biogas_generated
        })

    return render(request, 'base/biogas_prediction.html')



def arima_prediction(request):
    arima_model_path = "C:\\Users\\DELL\\Downloads\\todo_List (1)\\todo_List\\base\ml_models\\arima_model.pkl"

    if os.path.exists(arima_model_path):
        with open(arima_model_path, 'rb') as file:
            arima_model = pickle.load(file)
    else:
        return HttpResponse("ARIMA Model file not found. Make sure the path is correct.")

    if request.method == 'POST':
        try:
            weeks_to_predict = int(request.POST.get('weeks_to_predict', 4))  # Default: 4 weeks if not specified
            future_weeks = pd.date_range(start=pd.Timestamp.now(), periods=weeks_to_predict, freq='W')
            future_predictions = arima_model.predict(n_periods=weeks_to_predict * 3)  # Predictions for 3 categories

            water_bottles_predictions = future_predictions[::3]  # Extract predictions for water bottles
            aluminum_predictions = future_predictions[1::3]     # Extract predictions for aluminum
            milk_pouches_predictions = future_predictions[2::3]  # Extract predictions for milk pouches

            future_predictions_data = list(zip(
                future_weeks.strftime("%b. %d, %Y"),  # Format date without time
                water_bottles_predictions,
                aluminum_predictions,
                milk_pouches_predictions
            ))

            return render(request, 'base/arima_result.html', {
                "future_predictions": future_predictions_data,
            })
        except ValueError:
            return HttpResponse("Invalid input for weeks to predict.")

    return render(request, 'base/arima_prediction.html')

# Function to load the linear regression model
def load_linear_regression_model(model_path):
    if os.path.exists(model_path):
        with open(model_path, 'rb') as file:
            model = pickle.load(file)
        return model
    else:
        return None
        
def monthly_income_prediction(request):
    # Path to your linear regression model
    linear_model2_path = "C:\\Users\\DELL\\Downloads\\todo_List (1)\\todo_List\\base\\ml_models\\Income_generation.pkl"

    # Load the linear regression model
    model2 = load_linear_regression_model(linear_model2_path)

    if model2 is None:
        return HttpResponse("Linear Regression Model file not found. Make sure the path is correct.")

    if request.method == 'POST':
        # Fetching user inputs for month and year
        month_str = request.POST.get('month')
        year_str = request.POST.get('year')

        try:
            # Try to convert the input values to integers
            month = int(month_str)
            year = int(year_str)

            # Ensure that month and year are within valid ranges
            if not (1 <= month <= 12 and (year > 2023 or (year == 2023 and month >= 7))):
                raise ValueError("Invalid month or year")


            # Predict the income using the loaded model
            prediction = model2.predict([[month, year]])[0]

            return render(request, 'base/income_result.html', {'prediction': prediction})

        except ValueError as e:
            # Handle the case where conversion to integers fails or input is invalid
            return HttpResponse(f"Invalid input. {str(e)}")

    return render(request, 'base/monthly_income_prediction.html')



    
      # Replace with your dashboard template
class TaskList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()

        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['tasks'] = context['tasks'].filter(
                title__contains=search_input)

        context['search_input'] = search_input

        return context


class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    context_object_name = 'task'
    template_name = 'base/task.html'


class TaskCreate(LoginRequiredMixin, ListView):
    model = Task
    fields = ['title', 'description', 'complete']
    template_name = 'base/task_form.html'
    success_url = reverse_lazy('tasks')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')


class DeleteView(LoginRequiredMixin, DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')
    def get_queryset(self):
        owner = self.request.user
        return self.model.objects.filter(user=owner)

class TaskReorder(View):
    def post(self, request):
        form = PositionForm(request.POST)

        if form.is_valid():
            positionList = form.cleaned_data["position"].split(',')

            with transaction.atomic():
                self.request.user.set_task_order(positionList)

        return redirect(reverse_lazy('tasks'))


def some_view(request):
    ridge_prediction = ridge_model.predict(some_data)
    arima_forecast = arima_model.forecast(steps=4)
    linear_regression_prediction = linear_regression_model.predict(some_data)
  

def dashboard(request):
    context = {}  # Initialize an empty context dictionary

    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            # Read data from the uploaded file
            uploaded_file = request.FILES['file']
            df = pd.read_csv(uploaded_file)

            # Extract categories and corresponding count for events
            waste_columns = [
                'White Paper Collected', 'Color Paper Collected', 'water bottle collected',
                'Cbox Paper Collected', 'damage collected', 'milk pouches collected',
                'magazine collected', 'aluminium collected', 'plastic collected',
                'road waste collected', 'compost collected', 'wet-waste collected',
                'biogas generated'
            ]
            values = [
                df['White Paper Collected'].sum(),
                df['Color Paper Collected'].sum(),
                df['water bottle collected'].sum(),
                df['Cbox Paper Collected'].sum(),
                df['damage collected'].sum(),
                df['milk pouches collected'].sum(),
                df['magazine collected'].sum(),
                df['aluminium collected'].sum(),
                df['plastic collected'].sum(),
                df['road waste collected'].sum(),
                df['compost collected'].sum(),
                df['wet-waste collected'].sum(),
                df['biogas generated'].sum()
            ]

            # Get unique months in the correct order
            Month = df['Months'].unique().tolist()
            
             # Group by 'Months' and sum the values for each waste category
            values_1 = df.groupby('Months')['White Paper Sale'].sum().reset_index()
            values_2 = df.groupby('Months')['aluminium sale'].sum().reset_index()
            values_3 = df.groupby('Months')['Color Paper Sale'].sum().reset_index()
            values_4 = df.groupby('Months')['Cbox Paper Sale'].sum().reset_index()
            values_5 = df.groupby('Months')['damage sale'].sum().reset_index()
            values_6 = df.groupby('Months')['milk pouch sale'].sum().reset_index()
            values_7 = df.groupby('Months')['magazine sale'].sum().reset_index()
            values_8 = df.groupby('Months')['plastic sale'].sum().reset_index()
            values_9 = df.groupby('Months')['road waste sale'].sum().reset_index()

            Events = df['Events'].unique().tolist()
            
            bar_values_1 = df.groupby('Events')['White Paper Collected'].sum().reset_index()
            bar_values_2 = df.groupby('Events')['aluminium collected'].sum().reset_index()
            bar_values_3 = df.groupby('Events')['Color Paper Collected'].sum().reset_index()
            bar_values_4 = df.groupby('Events')['Cbox Paper Collected'].sum().reset_index()
            bar_values_5 = df.groupby('Events')['damage collected'].sum().reset_index()
            bar_values_6 = df.groupby('Events')['milk pouches collected'].sum().reset_index()
            bar_values_7 = df.groupby('Events')['magazine collected'].sum().reset_index()
            bar_values_8 = df.groupby('Events')['plastic collected'].sum().reset_index()
            bar_values_9 = df.groupby('Events')['road waste collected'].sum().reset_index()
            bar_values_10 = df.groupby('Events')['compost collected'].sum().reset_index()
            bar_values_11 = df.groupby('Events')['wet-waste collected'].sum().reset_index()
            bar_values_12 = df.groupby('Events')['biogas generated'].sum().reset_index()

            sum_sales =['White Paper Sale','aluminium sale','Color Paper Sale','Cbox Paper Sale','damage sale','milk pouch sale','magazine sale','plastic sale','road waste sale']
            # Sum the values for each event
            df['Total Sale'] = df[sum_sales].sum(axis=1)

            # Group by Events and sum the total sale for each event
            total_sale_by_event = df.groupby('Events')['Total Sale'].sum().reset_index()
            table_content = df.to_html(index=None, classes='table table-striped')
            total_sale_by_event['Percentage'] = (total_sale_by_event['Total Sale'] / total_sale_by_event['Total Sale'].sum()) * 100
            Pie_chart = total_sale_by_event[['Events','Percentage']]

            # Prepare context for rendering the template
            context = {
                "categories": waste_columns,
                'values': values,
                "line_categories": Month,
                "line_values_1": values_1['White Paper Sale'].tolist(),
                "line_values_2" : values_2['aluminium sale'].tolist(),
                "line_values_3": values_3['Color Paper Sale'].tolist(),
                "line_values_4": values_4['Cbox Paper Sale'].tolist(),
                "line_values_5": values_5['damage sale'].tolist(),
                "line_values_6": values_6['milk pouch sale'].tolist(),
                "line_values_7": values_7['magazine sale'].tolist(),
                "line_values_8": values_8['plastic sale'].tolist(),
                "line_values_9": values_9['road waste sale'].tolist(),
                "bar_values_1": bar_values_1['White Paper Collected'].tolist(),
                "bar_values_2": bar_values_2['aluminium collected'].tolist(),
               "bar_values_3": bar_values_3['Color Paper Collected'].tolist(),
            "bar_values_4": bar_values_4['Cbox Paper Collected'].tolist(),
            "bar_values_5": bar_values_5['damage collected'].tolist(),
          "bar_values_6": bar_values_6['milk pouches collected'].tolist(),
    "bar_values_7": bar_values_7['magazine collected'].tolist(),
    "bar_values_8": bar_values_8['plastic collected'].tolist(),
    "bar_values_9": bar_values_9['road waste collected'].tolist(),
    "bar_values_10": bar_values_10['compost collected'].tolist(),
    "bar_values_11": bar_values_11['wet-waste collected'].tolist(),
    "bar_values_12": bar_values_12['biogas generated'].tolist(),
    "bar_categories" : Events,
    "pie_value":  total_sale_by_event,
    'table_data': Pie_chart }
            return render(request, 'base/index.html',context)

    else:
        form = UploadFileForm()

    context['form'] = form  # Add the form to the context
    return render(request, 'base/dashboard.html',context)


from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login as auth_login
from django.shortcuts import render, redirect

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)  # Log the user in after registration
            return redirect('login')  # Redirect to the login view after registration
    else:
        form = UserCreationForm()
    return render(request, 'base/register.html', {'form': form})


def user_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)  # Log the user in after login
            return redirect('home')  # Redirect to the home page after login
    else:
        form = AuthenticationForm()
    return render(request, 'base/login.html', {'form': form})

from django.contrib.auth import logout
from django.shortcuts import redirect

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout



