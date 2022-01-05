from django.shortcuts import render
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponseNotFound, HttpResponse
from django.template import loader
from django import forms
from django.contrib.auth.decorators import login_required

from . import util

import markdown, secrets

class EntryForm(forms.Form):
    title = forms.CharField(label="Название статьи", widget=forms.TextInput(attrs={'class':'form-control col-md-8 col-lg-8', 'required': True}))
    content = forms.CharField(label="Текст статьи", widget=forms.Textarea(attrs={'class':'form-control col-md-8 col-lg-8', 'rows': 10, 'required': True}))
    edit = forms.BooleanField(initial=False, widget=forms.HiddenInput(), required=False)

# список статей
def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

# ссылки на статью
def entry(request, entry):
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/error.html", {
            "entryTitle": entry
        })
    else:
        return render(request, "encyclopedia/entry.html",{
            "entryTitle": entry,
            "entry": markdown.markdown(entryPage)
        })
# поиск
def search(request):
    if request.method == "POST":
        query = request.POST['q']

        content = util.get_entry(query)
        if content:
            return HttpResponseRedirect(reverse('entry', args=[query]))
        else:
            searchList = []
            for entry in util.list_entries():
                if query.upper() in entry.upper():
                    searchList.append(entry)
            if not searchList:
                return render(request, "encyclopedia/error.html", {
                    "entryTitle": query
                })
            
            return render(request, "encyclopedia/index.html", {
                "entries": searchList,
                "search": True,
                "query": query
            })

# создание статьи
def create(request):
    if request.method == "POST":
        form = EntryForm(request.POST)
        if form.is_valid():

            title = form.cleaned_data["title"]
            content = form.cleaned_data["content"]
            if(util.get_entry(title) is None or form.cleaned_data["edit"] is True):
                util.save_entry(title,content)
                return HttpResponseRedirect(reverse('entry', args=[title]))
            else:
                return render(request, "encyclopedia/create.html", {
                    "form": form,
                    "exist": True,
                    "entry": title
                })
        else:
            return render(request, "encyclopedia/create.html", {
                    "form": form,
                    "exist": False
            })
    else:
        return render(request, "encyclopedia/create.html", {
                    "form": EntryForm(),
                    "exist": False
            })
# редактирование статьи
def edit(request, entry):
    entryPage = util.get_entry(entry)
    if entryPage is None:
        return render(request, "encyclopedia/error.html", {
            "entryTitle": entry
        })
    else:
        form = EntryForm()
        form.fields["title"].initial = entry
        form.fields["title"].widget = forms.HiddenInput()
        form.fields["content"].initial = entryPage
        form.fields["edit"].initial = True
        return render(request, "encyclopedia/create.html", {
            "form": form,
            "edit": form.fields["edit"].initial,
            "entryTitle": form.fields["title"].initial
        })

# случайная статья
def random(request):
    entries = util.list_entries()
    randomEntry = secrets.choice(entries)
    return HttpResponseRedirect(reverse('entry', args=[randomEntry]))


    