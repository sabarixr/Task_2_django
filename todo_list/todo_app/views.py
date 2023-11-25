from django.shortcuts import redirect
from .models import ToDoList, ToDoItem
from django.views.generic import (ListView, CreateView, UpdateView, DeleteView, FormView)
from django.urls import reverse, reverse_lazy
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login


class PageLoginView(LoginView):
    template_name = 'todo_app/login.html'
    fields = '__all__'

    def get_success_url(self):
        return reverse_lazy("index")


class SignUpView(FormView):
    template_name = 'todo_app/signup.html'
    form_class = UserCreationForm
    success_url = reverse_lazy("index")

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return super(SignUpView, self).form_valid(form)


'''    def get(self, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('index')'''


# i made it correct but idk what happened when i was editing css its too late sorry

class ListListView(LoginRequiredMixin, ListView):
    model = ToDoList
    template_name = "todo_app/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # print(ToDoList.objects.all())

        user_specific_lists = ToDoList.objects.filter(user=self.request.user)
        # print(user_specific_lists)

        context['object_list'] = user_specific_lists

        return context


class ItemListView(LoginRequiredMixin, ListView):
    model = ToDoItem
    template_name = "todo_app/todo_list.html"

    def get_queryset(self):
        return ToDoItem.objects.filter(todo_list_id=self.kwargs["list_id"])

    def get_context_data(self):
        context = super().get_context_data()
        context["todo_list"] = ToDoList.objects.get(id=self.kwargs["list_id"])
        return context


class ListCreate(LoginRequiredMixin, CreateView):
    model = ToDoList
    fields = ["title"]

    def form_valid(self, form):
        form.instance.user = self.request.user

        # print(f"Form instance user: {form.instance.user}")
        result = super().form_valid(form)
        # print(f"Created ToDoList user: {self.object.user}")
        return result


class ItemCreate(LoginRequiredMixin, CreateView):
    model = ToDoItem
    fields = [
        "todo_list",
        "title",
        "description",
        "due_date",
    ]

    def get_initial(self):
        initial_data = super(ItemCreate, self).get_initial()
        todo_list = ToDoList.objects.get(id=self.kwargs["list_id"])
        initial_data["todo_list"] = todo_list
        return initial_data

    def get_context_data(self):
        context = super(ItemCreate, self).get_context_data()
        todo_list = ToDoList.objects.get(id=self.kwargs["list_id"])
        context["todo_list"] = todo_list
        context["title"] = "Create a new item"
        return context

    def get_success_url(self):
        return reverse("list", args=[self.object.todo_list_id])


class ItemUpdate(LoginRequiredMixin, UpdateView):
    model = ToDoItem
    fields = [
        "todo_list",
        "title",
        "description",
        "due_date",
        "completed"
    ]

    def get_context_data(self):
        context = super(ItemUpdate, self).get_context_data()
        context["todo_list"] = self.object.todo_list
        context["title"] = "Edit item"
        return context

    def get_success_url(self):
        return reverse("list", args=[self.object.todo_list_id])


class ListDelete(LoginRequiredMixin, DeleteView):
    model = ToDoList
    success_url = reverse_lazy("index")


class ItemDelete(LoginRequiredMixin, DeleteView):
    model = ToDoItem

    def get_success_url(self):
        return reverse_lazy("list", args=[self.kwargs["list_id"]])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["todo_list"] = self.object.todo_list
        return context