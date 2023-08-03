# views.py
from django.db.models import F
import json
import time
import concurrent.futures
import re
from django.shortcuts import get_object_or_404, render, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .forms import KeywordForm
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .models import Keyword, Link,MyLink

@csrf_exempt
def search_and_save_links(request):
    print("start")
    if request.method == 'POST':
        user = request.user
        form = KeywordForm(request.POST)
        if form.is_valid():
            keywords = form.cleaned_data['keywords']
            duration = int(form.cleaned_data['duration'])  # Get the duration in minutes
            end_time = time.time() + duration * 60  # Calculate the end time
            
            options = webdriver.ChromeOptions()
            options.add_argument('--headless')
            driver = webdriver.Chrome(options=options)  # Use the appropriate executable_path if needed

            # Create a queue to hold links to be scraped
            queue = ['https://www.geeksforgeeks.org/']
            visited = set()
            keyword_obj, created = Keyword.objects.get_or_create(keyword=keywords)

            while True:
                while queue and time.time() <= end_time:
                    link_url = queue.pop(0)
                    visited.add(link_url)

                    driver.get(link_url)
                    search_results = driver.find_elements_by_css_selector('a')

                    for result in search_results:
                        next_link_url = result.get_attribute('href')
                        if next_link_url is not None:  # Check if next_link_url is not None
                            link_title = result.text

                            # Extract title and set is_problem flag if the link contains "/problems/"
                            is_problem = False
                            title_start = next_link_url.find("/problems/")
                            if title_start != -1:
                                title_end = next_link_url.find("/", title_start + len("/problems/") + 1)
                                if title_end != -1:
                                    title = next_link_url[title_start + len("/problems/") + 1:title_end]
                                    is_problem = True
                                else:
                                    title = next_link_url[title_start + len("/problems/") + 1:]
                            else:
                                # Use regex to extract title using the keyword
                                match = re.search(r'/(.*' + keywords + r'.*)/', next_link_url)
                                if match:
                                    title = match.group(1)
                                else:
                                    title = link_title

                            if next_link_url and title and keywords and (keywords.lower() in title.lower() or keywords.lower() in next_link_url.lower()) and next_link_url not in visited:
                                # Check if the link is already saved in the database to avoid duplicates
                                if not Link.objects.filter(url=next_link_url).exists():
                                    # Save the link to the database
                                    print(next_link_url)
                                    queue.append(next_link_url)
                                    link_object = Link(keyword=keyword_obj, url=next_link_url, title=title, is_problem=is_problem, average_rating=0.0)
                                    link_object.save()
                                    mylink = MyLink(user=user, link=link_object, keyword=keyword_obj, revisit=False, done=False)
                                    mylink.save()

                if time.time() > end_time:
                    break

            driver.quit()

            # Data to be displayed
            user = request.user
            keywords = Keyword.objects.all()
            links_by_keyword = {}

            for keyword in keywords:
                mylinks = MyLink.objects.filter(keyword=keyword, user=user).annotate(
                    avg_rating=F('link__average_rating')
                ).order_by('-avg_rating')
                
                # Check if the mylinks list is not empty
                if mylinks.exists():
                    links_by_keyword[keyword] = mylinks

            return render(request, 'users/home.html', {'links_by_keyword': links_by_keyword, 'user': user})


    else:
        form = KeywordForm()

    context = {
        'form': form,
    }
    return render(request, 'scraper/search.html', context)

from django.shortcuts import render, redirect
from .models import Link

def handle_link_action(request):
    action = request.POST.get('action')
    link_id = request.POST.get('link_id')

    try:
        mylink = MyLink.objects.get(pk=link_id)
    except MyLink.DoesNotExist:
        # Handle the case where the MyLink object does not exist
        # You can display an error message or redirect to a different page
        return HttpResponse("MyLink with the provided ID does not exist.")

    if action == 'revisit':
        # Perform the "Revisit" action for the link with the given link_id
        mylink = MyLink.objects.get(pk=link_id)
        mylink.revisit = True
        mylink.done = False
        mylink.save()
    elif action == 'done':
        # Perform the "Done" action for the link with the given link_id
        mylink = MyLink.objects.get(pk=link_id)
        mylink.revisit = False
        mylink.done = True
        mylink.save()
    elif action == 'delete':
        # Perform the "Delete" action for the link with the given link_id
        mylink = MyLink.objects.get(pk=link_id)
        mylink.delete()

# Redirect back to the home page after handling the action
    user = request.user
    keywords = Keyword.objects.all()
    links_by_keyword = {}

    for keyword in keywords:
        mylinks = MyLink.objects.filter(keyword=keyword, user=user).annotate(
                    avg_rating=F('link__average_rating')
                ).order_by('-avg_rating')
                
        
        # Check if the mylinks list is not empty
        if mylinks:
            links_by_keyword[keyword] = mylinks
    return render(request, 'users/home.html',{'links_by_keyword': links_by_keyword, 'user': user})
# def user_links(request):
#     user = request.user
#     keywords = Keyword.objects.filter(user=user)
#     links_by_keyword = {}

#     for keyword in keywords:
#         links = Link.objects.filter(keyword=keyword).order_by('-average_rating')
#         links_by_keyword[keyword] = links

#     return render(request, 'users/user_links.html', {'links_by_keyword': links_by_keyword, 'user': user})

def community_dashboard(request):
    keywords = Keyword.objects.all()
    links_by_keyword = {}
    user = request.user
    for keyword in keywords:
        mylinks = Link.objects.filter(keyword=keyword).order_by('-average_rating')
                
        
        # Check if the mylinks list is not empty
        if mylinks:
            links_by_keyword[keyword] = mylinks
    return render(request, 'scraper/comunity_dashboard.html',{'links_by_keyword': links_by_keyword,'user' : user})

def rate_link(request, link_id):
    if request.method == 'POST':
        link = get_object_or_404(Link, pk=link_id)
        rating = int(request.POST.get('rating'))
        # Update the link's average rating and rated status
        total_ratings = link.total_ratings + 1
        total_score = link.total_score + rating
        average_rating = total_score / total_ratings
        link.total_ratings = total_ratings
        link.total_score = total_score
        link.average_rating = average_rating
        link.rated = True
        link.save()
        print(link.average_rating)
    keywords = Keyword.objects.all()
    links_by_keyword = {}
    user = request.user
    for keyword in keywords:
        mylinks = Link.objects.filter(keyword=keyword).order_by('-average_rating')
                
        
        # Check if the mylinks list is not empty
        if mylinks:
            links_by_keyword[keyword] = mylinks
    return render(request, 'scraper/comunity_dashboard.html',{'links_by_keyword': links_by_keyword,'user' : user})

def add_to_dashboard(request, link_id):
    if request.method == 'POST':
        user = request.user
        link = Link.objects.get(pk=link_id)
        if not MyLink.objects.filter(keyword=link.keyword, user=user, link=link).exists():
            MyLink.objects.create(keyword=link.keyword, user=user, link=link)
    keywords = Keyword.objects.all()
    links_by_keyword = {}
    user = request.user
    for keyword in keywords:
        mylinks = Link.objects.filter(keyword=keyword).order_by('-average_rating')
        if mylinks:
            links_by_keyword[keyword] = mylinks
    return render(request, 'scraper/comunity_dashboard.html',{'links_by_keyword': links_by_keyword,'user' : user})


def add_note_to_link(request, link_id):
    if request.method == 'POST':
        user = request.user
        link = MyLink.objects.get(pk=link_id, user=user)
        note = request.POST.get('note', '')
        link.note = note
        link.save()
        keywords = Keyword.objects.all()
        links_by_keyword = {}

        for keyword in keywords:
            mylinks = MyLink.objects.filter(keyword=keyword, user=user).annotate(
                    avg_rating=F('link__average_rating')
                ).order_by('-avg_rating')
                
            # Check if the mylinks list is not empty
            if mylinks:
                links_by_keyword[keyword] = mylinks
        return render(request, 'users/home.html',{'links_by_keyword': links_by_keyword, 'user': user})
