import itertools
from datetime import datetime
import json
import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.views import View


def get_news():
    with open(settings.NEWS_JSON_PATH, 'r', encoding='utf-8') as json_file:
        news_json = json.load(json_file)

    return news_json


def update_news(new_news):
    with open(settings.NEWS_JSON_PATH, 'w', encoding='utf-8') as json_file:
        json.dump(new_news, json_file)


def simple_date_fun(date):
    return datetime.strptime(date, "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%d")


class ComingSoon(View):
    def get(self, request, *args, **kwargs):
        return redirect('/news/')


class NewsIndexView(View):
    def get(self, request, *args, **kwargs):

        search_query = request.GET.get('q')

        data_from_json = get_news()

        if search_query:
            data_from_json = [new for new in data_from_json if search_query in new["title"].split(" ")]

        data_from_json.sort(key=lambda x: datetime.strptime(x['created'], "%Y-%m-%d %H:%M:%S"), reverse=True)

        all_news = [{'date': date, 'values': list(news)} for date, news in
                    itertools.groupby(data_from_json, lambda x: simple_date_fun(x['created']))]

        return render(request, 'news/index.html', context={"all_news": all_news})


class News(View):
    def get(self, request, news_id, *args, **kwargs):

        news_json = get_news()
        context = {"new": news_json[news_id - 1]}

        return render(request, 'news/readnew.html', context=context)


class CreateNews(View):

    def get(self, request, *args, **kwargs):
        return render(request, 'news/create.html')

    def post(self, request, *args, **kwargs):

        news_json = get_news()
        db_last_id = news_json[-1]['link']

        news_title = request.POST.get('title')
        news_text = request.POST.get('text')
        news_created_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        news_id = db_last_id + 1

        new = {"created": news_created_time,
               "text": news_text,
               "title": news_title,
               "link": news_id}

        news_json.append(new)

        update_news(news_json)

        return redirect("/news/")
