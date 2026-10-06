from django.shortcuts import render, redirect
from main.models import Contact, Listing, Comment, Notification
from django.core.mail import send_mail
import os
from django.contrib import messages
from django.contrib.auth.models import User as AuthUser
import re
from django.contrib.auth.models import User as AuthUser
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

# Landing page
def home(request):
    category_choices = Listing.CATEGORY_CHOICES
    latest_listings = Listing.objects.order_by('-created_at')[:6]

    context = {
        'category_choices':category_choices,
        'latest_listings':latest_listings,
    }
    return render(request, 'home.html', context)

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')

        Contact.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )

        messages.success(request, "Your message has been received. Thank you for contacting Bazaar Online!")

        send_mail(
            subject=f'New Contact message from {name}',
            message=f'''
Name: {name}
Email: {email}
Phone: {phone}
Message:
{message}
''',
            from_email={email},
            recipient_list=['mail4rms@gmail.com'],
        )

    return render(request, 'contact.html')

@login_required
def listing(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        description = request.POST.get('description')
        category = request.POST.get('category')
        price = request.POST.get('price')
        image = request.FILES.get('image')
        location = request.POST.get('location')
        created_at = request.POST.get('created_at')
        expires_at = request.POST.get('expires_at')

        Listing.objects.create(
            user=request.user,
            title=title,
            description=description,
            category=category,
            price=price,
            image=image,
            location=location,
            created_at=created_at,
            expires_at=expires_at
        )

        messages.success(request, f"Your Listing for {title} has been posted.")
    #listings = Listing.objects.filter(user=request.user)
    return render(request, 'listing.html')

def category_listings(request,category):
    listings = Listing.objects.filter(category = category).order_by('-created_at')
    category_name = dict(Listing.CATEGORY_CHOICES).get(category, 'Listings')
    context = {
        'listings':listings,
        'category_name':category_name
    }
    return render(request, 'category_listings.html', context)

def signup(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        email=request.POST.get('email')
        password=request.POST.get('password')

        if AuthUser.objects.filter(username=username).exists():
            messages.error(request, "username {usernmae} already exists.")
            return render(request, 'signup.html')

        if AuthUser.objects.filter(email=email).exists():
            messages.error(request, "email {email} is already registered.")
            return render(request, 'signup.html')

        user = AuthUser.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, "Your account has been created. You can now log in.")
        return redirect('login')

    return render(request, 'signup.html')

def user_login(request):
    if request.method == 'POST':
        username=request.POST.get('username')
        password=request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')

def user_logout(request):
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('home')

@login_required
def my_listings(request):
    listings = Listing.objects.filter(
        user=request.user
    ).order_by('-created_at')

    return render(request, 'my_listings.html', {'listings':listings})

@login_required
def delete_listing(request, id):
    listing = Listing.objects.get(id=id)
    
    if request.method == 'POST':
        listing.delete()
        messages.success(request, "Your listing has been deleted successfully.")

    return redirect("my_listings")

@login_required
def edit_listing(request, id):
    listing = Listing.objects.get(id=id)
    
    if request.method == 'POST':
        listing.title = request.POST.get('title')
        listing.description = request.POST.get('description')
        listing.category = request.POST.get('category')
        listing.price = request.POST.get('price')
        listing.location = request.POST.get('location')

        if request.FILES.get('image'):
            listing.image = request.FILES.get('image')

        listing.save()
        messages.success(request, "Your listing has been updated successfully")

        return redirect('my_listings')

    return render(request, 'edit_listing.html', {'listing':listing})

def categories(request):
    category_icons = {
        'mobiles': 'bi-phone',
        'computers': 'bi-laptop',
        'electronics': 'bi-cpu',
        'vehicles': 'bi-car-front',
        'property': 'bi-house',
        'fashion': 'bi-bag',
        'furniture': 'bi-lamp',
        'musical_instruments': 'bi-music-note-beamed',
        'sports': 'bi-trophy',
        'books': 'bi-book',
        'toys': 'bi-controller',
        'pets': 'bi-heart',
        'jobs': 'bi-briefcase',
        'services': 'bi-tools',
        'other': 'bi-three-dots',
    }

    categories = []

    for value, label in Listing.CATEGORY_CHOICES:
        categories.append({
            'value':value,
            'label':label,
            'icon':category_icons.get(value, 'bi-grid')
        })

    context = {
        'categories':categories,
    }

    return render(request, 'categories.html', context)


def search(request):
    query = request.GET.get('q', '')
    listings = Listing.objects.none()

    if query:
        listings = Listing.objects.filter(
            title__icontains = query
        )

    context = {
        'listings': listings,
        'query': query,
    }
    return render(request, 'search.html', context)

def listing_detail(request, id):
    listing = Listing.objects.get(id=id)
    comments = listing.comments.select_related('user').order_by('-created_at')

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to post a comment")
            return redirect('login')

        text = request.POST.get("text", '').strip()

        if text:
            comment = Comment.objects.create(
                listing=listing,
                user=request.user,
                text=text
            )

            # Create notification for the seller
            if request.user != listing.user:
                Notification.objects.create(
                    user=listing.user,
                    comment=comment
                )

            messages.success(request, "Your comment has been posted.")
        else:
            messages.error(request, "Comment cannot be empty.")

        return redirect('listing_detail', id=listing.id)

    context = {
        'listing': listing,
        'comments': comments,
    }

    return render(request, 'listing_detail.html', context)

@login_required
def notifications(request):
    notifications = request.user.notifications.select_related(
        'comment',
        'comment__listing',
        'comment__user'
    ).order_by('-created_at')

    # Mark all notifications as read when the page is opened
    request.user.notifications.filter(is_read=False).update(is_read=True)

    return render(
        request,
        'notifications.html',
        {'notifications': notifications}
    )

@login_required
def edit_profile(request):
    user = request.user

    if request.method == 'POST':
        user.username = request.POST.get('username')
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        user.email = request.POST.get('email')

        user.save()

        messages.success(request, "Your profile has been updated successfully.")

        return redirect('home')
    
    return render(request, 'edit_profile.html')