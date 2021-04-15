from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render
from django.urls import reverse_lazy

from django.views import View
from django.views.generic import FormView

from .forms import CustomerCreateForm, OrderSearchForm
from .models import Order

from .repositories.customer import load_customer
from .repositories.order import load_orders

from .services.utils import export_csv
from .services.parser import CustomerParser, OrderParser


class UserLoginView(LoginView):
    redirect_authenticated_user = True


class UserLogoutView(LogoutView):
    next_page = 'main_url'


class MainView(LoginRequiredMixin, FormView):
    form_class = OrderSearchForm
    template_name = 'main.html'
    success_url = reverse_lazy('main_url')

    def form_valid(self, form, **kwargs):
        orders = OrderParser(search_params=form.cleaned_data, save=False).parse()
        self.extra_context = {'orders': orders}
        return render(self.request, 'main.html', self.get_context_data())


class CustomerView(LoginRequiredMixin, FormView):
    form_class = CustomerCreateForm
    template_name = 'customer-list.html'
    success_url = reverse_lazy('customer_url')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customers'] = load_customer()
        return context

    def form_valid(self, form, **kwargs):
        CustomerParser().parse(int(form.cleaned_data['inn']))
        return super().form_valid(form)


class CustomerDetailView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        form = OrderSearchForm
        customer = load_customer(inn=kwargs['inn'])
        orders = load_orders(customer_inn=customer.inn)
        return render(request, 'customer-detail.html', {'customer': customer, 'form': form, 'orders': orders})

    def post(self, request, *args, **kwargs):
        form = OrderSearchForm(request.POST)
        customer = load_customer(inn=kwargs['inn'])
        if form.is_valid():
            orders = OrderParser(search_params=form.cleaned_data, save=True).parse()
            return render(request, 'customer-detail.html', {'customer': customer, 'form': form, 'orders': orders})

    # model = Customer
    # template_name = 'customer-detail.html'
    # form_class = OrderSearchForm
    # success_url = reverse_lazy('customer_detail_url')
    # queryset = load_customer('4909112044')
    #
    # def post(self, request, *args, **kwargs):
    #     form = OrderSearchForm(request.POST)
    #     customer = load_customer(inn=kwargs['inn'])
    #     if form.is_valid():
    #         orders = OrderParser(search_params=form.cleaned_data, save=True).parse()
    #     return render(request, 'customer-detail.html', {'customer': customer, 'form': form, 'content': orders})
    #
    # def get_object(self, queryset=None):
    #     return get_object_or_404(Customer, inn=self.kwargs['inn'])
    #
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['orders'] = load_orders(customer_inn=self.kwargs['inn'])
    #     return context
    #
    # def form_valid(self, form, **kwargs):
    #     orders = OrderParser(search_params=form.cleaned_data, save=True).parse()
    #     customer = load_customer(self.kwargs['inn'])
    #     self.extra_context = {'content': orders, 'object': customer}
    #     return render(self.request, 'customer-detail.html', self.get_context_data())


class TestView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        item = Order.objects.filter(parser_status=0).values_list('reg_number').last()
        return render(request, 'test.html', {'test': item[0]})


def export(request, *args, **kwargs):
    return export_csv(customer_inn=kwargs['inn'])

# rss контракты закупщика
# https://zakupki.gov.ru/epz/contract/search/rss?customerInn=3664122837
