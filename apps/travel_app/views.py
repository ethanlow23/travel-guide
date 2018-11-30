# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count, Avg
from models import User, Place, Review
import json, requests
import bcrypt

# Create your views here.
def index(request):
    if request.session.get('id', False):
        return redirect('/main')
    else:
        return render(request, 'travel_app/index.html')

def register(request):
    if request.method == "POST":
        errors = User.objects.register_validator(request.POST)
        if len(errors):
            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags=tag)
            return redirect('/')
        else:
            hash1 = bcrypt.hashpw(request.POST['password'].encode(), bcrypt.gensalt())
            user = User.objects.create(first_name=request.POST['first_name'], last_name=request.POST['last_name'], username=request.POST['username'], password=hash1)
            request.session['id'] = user.id
            request.session['username'] = user.username
            request.session['first_name'] = user.first_name
            request.session['last_name'] = user.last_name
        return redirect('/main')

def login(request):
    if request.method == "POST":
        login_errors = User.objects.login_validator(request.POST)
        if len(login_errors):
            for tag, error in login_errors.iteritems():
                messages.error(request, error, extra_tags=tag)
            return redirect('/')
        else:
            user = User.objects.get(username=request.POST['username'])
            request.session['id'] = user.id
            request.session['username'] = user.username
            request.session['first_name'] = user.first_name
            request.session['last_name'] = user.last_name
            return redirect('/main')

def logout(request):
    request.session.clear()
    return redirect('/')

def main(request):
    if request.GET.get('location', False):
        request.session['location'] = request.GET['location']
        location = request.session['location']
        request.session['category'] = 'topPicks'
    elif request.session.get('location', False):
        location = request.session['location']
    else:
        location = 'San Francisco'
    if request.GET.get('category', False):
        request.session['category'] = request.GET['category']
        section = request.session['category']
    elif request.session.get('category', False):
        section = request.session['category']
    else:
        section = 'topPicks'
    if request.GET.get('page_number', False):
        page = int(request.GET['page_number'])
    else:
        page = 1
    if request.GET.get('location', False) or request.GET.get('category', False) or request.GET.get('page_number', False):
        url = 'https://api.foursquare.com/v2/venues/explore'
        params = dict(
            client_id='CLIENT_ID',
            client_secret='CLIENT_SECRET',
            v='20180323',
            near=location,
            section=section,
            limit=10,
            offset=(page - 1) * 10
        )
        res = requests.get(url=url, params=params)
        data = json.loads(res.text)
    else:
        url = 'https://api.foursquare.com/v2/venues/explore'
        params = dict(
            client_id='CLIENT_ID',
            client_secret='CLIENT_SECRET',
            v='20180323',
            near=location,
            section='topPicks',
            limit=10,
            offset=(page - 1) * 10
        )
        res = requests.get(url=url, params=params)
        data = json.loads(res.text)
    top = Place.objects.annotate(avg_rating=Avg('reviews__rating')).order_by('-avg_rating')
    popular = Place.objects.annotate(num_reviews=Count('reviews')).order_by('-num_reviews')
    return render(request, 'travel_app/main.html', {'data': data, 'page': page, 'top': top, 'popular': popular})

def profile(request, id):
    user = User.objects.get(id=id)
    places = User.objects.get(id=id).places.all()
    reviews = User.objects.get(id=id).reviews.all()
    return render(request, 'travel_app/profile.html', {'user': user, 'places': places, 'reviews': reviews})

def place(request, id):
    url = 'https://api.foursquare.com/v2/venues/' + id
    params = dict(
        client_id='CLIENT_ID',
        client_secret='CLIENT_SECRET',
        v='20180323'
    )
    res = requests.get(url=url, params=params)
    data = json.loads(res.text)
    if request.session.get('id', False):
        if User.objects.get(id=request.session['id']).places.filter(name=data['response']['venue']['name']).first():
            user_place = User.objects.get(id=request.session['id']).places.get(name=data['response']['venue']['name'])
            reviews = Place.objects.get(name=data['response']['venue']['name']).reviews.all()
            place = Place.objects.annotate(avg_rating=Avg('reviews__rating')).get(name=data['response']['venue']['name'])
            return render(request, 'travel_app/place.html', {'data': data, 'user_place': user_place, 'reviews': reviews, 'place': place})
    else:
        if Place.objects.filter(name=data['response']['venue']['name']).first():
            reviews = Place.objects.get(name=data['response']['venue']['name']).reviews.all()
            place = Place.objects.annotate(avg_rating=Avg('reviews__rating')).get(name=data['response']['venue']['name'])
            return render(request, 'travel_app/place.html', {'data': data, 'reviews': reviews, 'place': place})
        else:
            return render(request, 'travel_app/place.html', {'data': data})

def visited(request, id):
    this_user = User.objects.get(id=request.session['id'])
    if Place.objects.filter(name=request.POST['place']).first():
        this_place = Place.objects.get(name=request.POST['place'])
    else:
        this_place = Place.objects.create(name=request.POST['place'])
    this_user.places.add(this_place)
    return redirect('/place/' + id)

def review(request, id):
    if request.method == "POST":
        review_errors = Review.objects.review_validator(request.POST)
        if len(review_errors):
            for tag, error in review_errors.iteritems():
                messages.error(request, error, extra_tags=tag)
        else:
            User.objects.get(id=request.session['id']).reviews.create(description=request.POST['description'], rating=request.POST['rating'], place=Place.objects.filter(name=request.POST['place']).first())
        return redirect('/place/' + id)