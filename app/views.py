from django.shortcuts import render
from django.views.generic import TemplateView
from .forms import IndexForm, SetupForm
from .like.like import AutoLiker


class IndexView(TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = IndexForm()
        return context


class SetupView(TemplateView):
    template_name = 'setup.html'

    def get(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SetupForm()

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = SetupForm()

        form = IndexForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            request.session['username'] = d.get('username')
            request.session['password'] = d.get('password')

        return self.render_to_response(context)


class ResultView(TemplateView):
    template_name = 'result.html'

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        form = SetupForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            request.session['url'] = d.get('url')

            # 自動いいね

            autoliker = AutoLiker()
            autoliker.set_account(username=request.session.get('username'), password=request.session.get('password'))
            autoliker.set_url(url=d.get('url'), max_like_count=d.get('max_like_count'))

            # 結果を返す
            context['result'] = autoliker.start()

        return self.render_to_response(context)
