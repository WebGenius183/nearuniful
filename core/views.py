import uuid
import requests
from datetime import timedelta
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.conf.urls import handler404

from .models import Apartment, ApartmentImage, Agent, Payment
from .forms import AgentRegisterForm, ProfileForm, ApartmentForm, ApartmentImageForm, ContactForm

def custom_404(request, exception):
    return render(request, '404.html', status=404)

handler404 = custom_404

# ---------------------------
# Decorators
# ---------------------------
def agent_required(view_func):
    """Protect views to only verified agents."""
    def wrapper(request, *args, **kwargs):
        if not hasattr(request.user, 'agent'):
            return redirect('home')
        if not request.user.agent.verified:
            messages.warning(request, "Your account is awaiting approval.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


# ---------------------------
# Public Pages
# ---------------------------
def home(request):
    apartments = Apartment.objects.filter(
        is_approved=True,
        is_featured=True,
        is_available=True
    ).select_related('university', 'agent').prefetch_related('images').order_by('-is_featured')

    for apt in apartments:
        if apt.featured_until and apt.featured_until < timezone.now():
            apt.is_featured = False
            apt.featured_until = None
            apt.save()

        if apt.boost_until and apt.boost_until < timezone.now():
            apt.boost_until = None
            apt.save()

    return render(request, 'index.html', {'apartments': apartments})


def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']

            full_message = f"""
                New Contact Message from NearUni

                Name: {name}
                Email: {email}
                Subject: {subject}

                Message:
                {message}
                """

            send_mail(
                subject=subject,
                message=full_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=['nearunioff@gmail.com'],
            )

            messages.success(request, "Your message has been sent successfully!")
            return redirect('contact')
    else:
        form = ContactForm()

    return render(request, 'contact.html', {'form': form})


# ---------------------------
# Apartment Pages
# ---------------------------
def apartment_list(request):
    qs = Apartment.objects.filter(is_approved=True, is_available=True).select_related('university', 'agent').prefetch_related('images')

    q = request.GET.get('q')
    apartment_type = request.GET.get('apartment_type')
    featured = request.GET.get('featured')

    if q:
        qs = qs.filter(university__name__icontains=q)
    if apartment_type:
        qs = qs.filter(apartment_type__icontains=apartment_type)
    if featured == '1':
        qs = qs.filter(is_featured=True)

    qs = qs.order_by('-is_featured', '-boost_until', '-created_at')
    return render(request, 'apartment.html', {'apartments': qs})


def apartment_detail(request, slug):
    """Apartment detail page, only approved and available apartments."""
    apartment = get_object_or_404(
        Apartment,
        slug=slug,
        is_approved=True,
        is_available=True
    )

    related_apartments = Apartment.objects.filter(
        university=apartment.university,
        is_approved=True,
        is_available=True
    ).exclude(id=apartment.id)[:4]

    return render(request, "apartment_detail.html", {
        "apartment": apartment,
        "related_apartments": related_apartments
    })


def search(request):
    """Redirect search queries to apartment_list with GET params."""
    query = request.GET.get('q', '')
    return redirect(f"{reverse('apartment_list')}?q={query}")


def agent_profile(request, id):
    agent = get_object_or_404(Agent, id=id)
    apartments = Apartment.objects.filter(agent=agent, is_approved=True, is_available=True)

    context = {
        "agent": agent,
        "apartments": apartments,
        "total_listings": apartments.count()
    }
    return render(request, "apartments/agent_profile.html", context)


# ---------------------------
# Authentication & Agent Pages
# ---------------------------
def RegisterPage(request):
    if request.method == 'POST':
        form = AgentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            # Send welcome email
            send_mail(
                subject="Welcome to NearUni!",
                message=f"Hi {user.username},\n\nYour account has been created successfully. You can now login and start adding apartments.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
            )
            messages.success(request, 'Account created successfully. A confirmation email has been sent.')
            return redirect('home')
    else:
        form = AgentRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})


def LoginPage(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('agent_dashboard' if hasattr(user, 'agent') else 'home')
        else:
            messages.error(request, 'Username or password incorrect')
    return render(request, 'accounts/login.html')


@login_required
def LogoutPage(request):
    logout(request)
    return redirect('login')


# ---------------------------
# Agent Dashboard / Apartment Management
# ---------------------------
@login_required
@agent_required
def agent_dashboard(request):
    apartments = request.user.agent.apartments.select_related('university').prefetch_related('images').all()
    now = timezone.now()

    # Clear expired featured/boost flags
    for apt in apartments:
        updated = False
        if apt.featured_until and apt.featured_until < now:
            apt.is_featured = False
            apt.featured_until = None
            updated = True
        if apt.boost_until and apt.boost_until < now:
            apt.boost_until = None
            updated = True
        if updated:
            apt.save()

    # Compute counts
    total_listings = apartments.count()
    pending_listings = apartments.filter(is_approved=False).count()
    featured_listings = apartments.filter(is_featured=True).count()
    boosted_listings = apartments.filter(boost_until__gte=now).count()

    return render(request, 'agent/dashboard.html', {
        'apartments': apartments,
        'total_listings': total_listings,
        'pending_listings': pending_listings,
        'featured_listings': featured_listings,
        'boosted_listings': boosted_listings,
    })
@login_required
@agent_required
def my_listings(request):
    apartments = request.user.agent.apartments.all()
    return render(request, 'agent/my_listings.html', {'apartments': apartments})

@login_required
@agent_required
def add_apartment(request):
    if request.method == 'POST':
        form = ApartmentForm(request.POST, request.FILES) 

        if form.is_valid():
            apartment = form.save(commit=False)
            apartment.agent = request.user.agent
            apartment.save()
            form.save_m2m()

            
            images = request.FILES.getlist("images")

            if images: 
                for image in images:
                    ApartmentImage.objects.create(
                        apartment=apartment,
                        image=image
                    )

            messages.success(request, 'Apartment and images added successfully!')
            return redirect('my_listings')

    else:
        form = ApartmentForm()

    return render(request, 'agent/add_apartment.html', {'form': form})


@login_required
@agent_required
def edit_apartment(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id, agent=request.user.agent)
    if request.method == 'POST':
        form = ApartmentForm(request.POST, instance=apartment)
        images_form = ApartmentImageForm(request.POST, request.FILES)
        if form.is_valid() and images_form.is_valid():
            form.save()
            images = request.FILES.getlist('image')
            for img in images:
                ApartmentImage.objects.create(apartment=apartment, image=img)
            messages.success(request, 'Apartment updated successfully!')
            return redirect('my_listings')
    else:
        form = ApartmentForm(instance=apartment)
        images_form = ApartmentImageForm()
    current_images = apartment.images.all()
    return render(request, 'agent/edit_apartment.html', {
        'form': form,
        'images_form': images_form,
        'apartment': apartment,
        'current_images': current_images
    })


@login_required
@agent_required
def delete_apartment(request, apartment_id):
    apartment = get_object_or_404(Apartment, id=apartment_id, agent=request.user.agent)
    if request.method == 'POST':
        apartment.delete()
        messages.success(request, 'Apartment deleted successfully!')
        return redirect('my_listings')
    return render(request, 'agent/delete_apartment.html', {'apartment': apartment})


@login_required
@agent_required
def delete_apartment_image(request, image_id):
    image = get_object_or_404(ApartmentImage, id=image_id, apartment__agent=request.user.agent)
    apartment_id = image.apartment.id
    if request.method == 'POST':
        image.delete()
        messages.success(request, 'Image deleted successfully!')
        return redirect('edit_apartment', apartment_id=apartment_id)
    return render(request, 'agent/delete_image_confirm.html', {'image': image})


@login_required
@agent_required
def profile(request):
    agent = request.user.agent
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=agent)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=agent)
    return render(request, 'agent/profile.html', {'form': form})

@login_required
@agent_required
def request_boost_payment(request, apartment_id):
    apartment = get_object_or_404(
        Apartment,
        id=apartment_id,
        agent=request.user.agent
    )

    # Prevent double boost
    if apartment.boost_until and apartment.boost_until > timezone.now():
        messages.warning(request, "This apartment is already boosted.")
        return redirect('my_listings')

    reference = str(uuid.uuid4())
    amount = 2000  # ₦2000

    # Create payment first
    payment = Payment.objects.create(
        agent=request.user.agent,
        apartment=apartment,
        payment_type='boost',
        amount=amount,
        reference=reference
    )

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "email": request.user.email,
        "amount": int(amount * 100),  # convert to kobo
        "reference": reference,
        "callback_url": request.build_absolute_uri(
            reverse('payment_success', args=[payment.id])
        ),
    }

    response = requests.post(
        settings.PAYSTACK_INITIALIZE_URL,
        json=data,
        headers=headers
    )

    res_data = response.json()

    if res_data.get("status"):
        return redirect(res_data["data"]["authorization_url"])

    payment.delete()
    messages.error(request, "Payment initialization failed.")
    return redirect('my_listings')


@login_required
@agent_required
def payment_success(request, payment_id):
    payment = get_object_or_404(
        Payment,
        id=payment_id,
        agent=request.user.agent
    )

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
    }

    url = f"{settings.PAYSTACK_VERIFY_URL}{payment.reference}"
    response = requests.get(url, headers=headers)
    res_data = response.json()

    if res_data.get("status") and res_data["data"]["status"] == "success":

        if not payment.is_successful:
            payment.mark_as_paid()

            apartment = payment.apartment

            if payment.payment_type == "boost":
                apartment.boost_until = timezone.now() + timedelta(days=7)

            elif payment.payment_type == "feature":
                apartment.is_featured = True
                apartment.featured_until = timezone.now() + timedelta(days=30)

            apartment.save()

        messages.success(request, "Payment successful! Apartment boosted 🚀")

    else:
        messages.error(request, "Payment verification failed.")

    return redirect('my_listings')

@login_required
@agent_required
def request_feature_payment(request, apartment_id):
    apartment = get_object_or_404(
        Apartment,
        id=apartment_id,
        agent=request.user.agent
    )

    # Prevent double feature
    if apartment.is_featured and apartment.featured_until and apartment.featured_until > timezone.now():
        messages.warning(request, "This apartment is already featured.")
        return redirect('my_listings')

    reference = str(uuid.uuid4())
    amount = 5000  # ₦5000 for 30 days feature

    payment = Payment.objects.create(
        agent=request.user.agent,
        apartment=apartment,
        payment_type='feature',
        amount=amount,
        reference=reference
    )

    headers = {
        "Authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}",
        "Content-Type": "application/json",
    }

    data = {
        "email": request.user.email,
        "amount": int(amount * 100),
        "reference": reference,
        "callback_url": request.build_absolute_uri(
            reverse('payment_success', args=[payment.id])
        ),
    }

    response = requests.post(
        settings.PAYSTACK_INITIALIZE_URL,
        json=data,
        headers=headers
    )

    res_data = response.json()

    if res_data.get("status"):
        return redirect(res_data["data"]["authorization_url"])

    payment.delete()
    messages.error(request, "Payment initialization failed.")
    return redirect('my_listings')