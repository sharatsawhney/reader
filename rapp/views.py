from django.shortcuts import render, redirect,resolve_url,render_to_response
from easy_pdf.views import PDFTemplateView
from django.conf import settings
from rapp.forms import UserForm,UploadForm,PriceRangeSearchForm
from django.contrib.auth import authenticate, login,logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from rapp.models import Authors,Publishers,Category,Ebooks,Subscribers,Usercart,Wishlist,Transactions,Dashboard,Notes,Lastpage,Uploaded,UserP,Adminacc,Gmailid,Bookmark,Tag,Musicgenre,Musictag,Music,Musiclis,Playlist,Highlight,Notefile,Notefileitem,Uploadadmin,Keyvalue,Offer,Bestseller,Detailview,Readview,Sampleview,Genreview,Newreleaseview,Bestsellerview,Searchview,Rateduser,Percentageread,Readlocation,ConnectionHistory,Payment,Publisherpayment
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.template.loader import render_to_string
from rapp.tokens import account_activation_token
from django.core.mail import EmailMessage
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.urls import reverse
from django.views.decorators.csrf import csrf_protect,csrf_exempt
from django.contrib.auth.tokens import default_token_generator
from django.template.response import TemplateResponse
from django.views.decorators.cache import never_cache
from django.views.decorators.debug import sensitive_post_parameters
from django.contrib.auth.forms import (
    AuthenticationForm, PasswordChangeForm, PasswordResetForm, SetPasswordForm,
)
import warnings
from django.utils.deprecation import RemovedInDjango21Warning
from django.contrib.auth import get_user_model
import json
import hashlib
from django.template import RequestContext
import requests
from django.contrib import messages
import logging, traceback
import rapp.constants as constants
import rapp.config as config
from random import randint
import requests as req
from datetime import datetime, timezone, timedelta
from haystack.generic_views import SearchView
from haystack.forms import FacetedSearchForm
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery, Exact, Clean
from google.oauth2 import id_token
from google.auth.transport import requests
import boto.s3
from boto.s3.key import Key
from nltk.corpus import stopwords
import razorpay
from django.core.files.storage import FileSystemStorage
import paypalrestsdk
import logging

UserModel = get_user_model()


def index(request):
    ebooks = Ebooks.objects.all()
    return render(request,'rapp/index.html', {'ebooks':ebooks})


def register(request):
    if request.method == 'POST':
        email = request.POST['email']
        username = request.POST['username']
        password = request.POST['password']
        if email!='' and username!='' and password!='':
            if len(User.objects.filter(email=email)) == 0:
                user = User.objects.create_user(username,email,password)
                user.is_active = False
                user.save()
                text_content = "Account Activation Email"
                subject = "Email Activation"
                template_name = "rapp/acc_active_email.html"
                from_email = 'contact@readerearth.com'
                recipients = [email,]
                kwargs = {
                    "uidb64": urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                    "token": account_activation_token.make_token(user)
                }
                activation_url = reverse("activate", kwargs=kwargs)

                activate_url = "{0}://{1}{2}".format(request.scheme, request.get_host(), activation_url)
                context = {
                    'user': user,
                    'activate_url': activate_url
                }
                html_content = render_to_string(template_name,context)
                email = EmailMultiAlternatives(subject, text_content, from_email, recipients)
                email.attach_alternative(html_content, "text/html")
                email.send()
                return HttpResponse('Please confirm your email address to complete the registration')
            else:
                return HttpResponse('This Email id has already been taken!')

def user_login(request):
    if request.method == 'POST':
        email = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(email=email, password=password)

        if user:
            login(request, user)
            return HttpResponseRedirect('/')
        else:
            print("Invalid Credentials")
            return HttpResponse("Invalid login details supplied.")
    else:
        return render(request,'rapp/login.html', {})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/')


def about(request):
    return render(request,'rapp/about.html',{})


def contact(request):
    if request.method == 'POST':
        if 'submit1' in request.POST:
            message = request.POST['message']
            name = request.POST['name']
            email = request.POST['email']
            number = request.POST['number']
            html_content = '<br>Name: ' + name + '<br>Message: ' + message + '<br>Number: ' + number + '<br>Email: ' + email
            msg = EmailMultiAlternatives(
                'General Contact - Reader Earth',
                'Details:',
                to=['contact@readerearth.com',]
            )
            msg.attach_alternative(html_content,"text/html")
            msg.send()
            return render(request,'rapp/contact.html', {'alert':True})



    return render(request,'rapp/contact.html', {'alert':False})


def subscribe(request):
    if request.method == 'POST':
        subemail = request.POST['subemail']

        if subemail:
            sub = Subscribers.objects.get_or_create(subemail=subemail)

    return HttpResponse(sub)


def activate(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        # return redirect('home')
        return HttpResponseRedirect('/')
    else:
        return HttpResponse('Activation link is invalid!')


def check_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            return HttpResponse('Login Successful')

        else:
            return HttpResponse("Invalid login details supplied.")


@csrf_protect
def password_reset(request,
                   template_name='registration/password_reset_form.html',
                   email_template_name='registration/password_reset_email.html',
                   subject_template_name='registration/password_reset_subject.txt',
                   password_reset_form=PasswordResetForm,
                   token_generator=default_token_generator,
                   post_reset_redirect=None,
                   from_email=None,
                   extra_context=None,
                   html_email_template_name=None,
                   extra_email_context=None):
    warnings.warn("The password_reset() view is superseded by the "
                  "class-based PasswordResetView().",
                  RemovedInDjango21Warning, stacklevel=2)
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_done')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    if request.method == "POST":
        form = password_reset_form(request.POST)
        if form.is_valid():
            opts = {
                'use_https': request.is_secure(),
                'token_generator': token_generator,
                'from_email': from_email,
                'email_template_name': email_template_name,
                'subject_template_name': subject_template_name,
                'request': request,
                'html_email_template_name': html_email_template_name,
                'extra_email_context': extra_email_context,
            }
            form.save(**opts)
            return HttpResponseRedirect(post_reset_redirect)
    else:
        form = password_reset_form()
    context = {
        'form': form,
        'title':'Password reset',
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def password_reset_done(request,
                        template_name='registration/password_reset_done.html',
                        extra_context=None):
    warnings.warn("The password_reset_done() view is superseded by the "
                  "class-based PasswordResetDoneView().",
                  RemovedInDjango21Warning, stacklevel=2)
    context = {
        'title':'Password reset sent',
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


@sensitive_post_parameters()
@never_cache
def password_reset_confirm(request, uidb64=None, token=None,
                           template_name='registration/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           extra_context=None):
    """
    Check the hash in a password reset link and present a form for entering a
    new password.
    """
    warnings.warn("The password_reset_confirm() view is superseded by the "
                  "class-based PasswordResetConfirmView().",
                  RemovedInDjango21Warning, stacklevel=2)
    assert uidb64 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    try:
        # urlsafe_base64_decode() decodes to bytestring
        uid = urlsafe_base64_decode(uidb64).decode()
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        title = 'Enter new password'
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(user)
    else:
        validlink = False
        form = None
        title = 'Password reset unsuccessful'
    context = {
        'form': form,
        'title': title,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def password_reset_complete(request,
                            template_name='registration/password_reset_complete.html',
                            extra_context=None):
    warnings.warn("The password_reset_complete() view is superseded by the "
                  "class-based PasswordResetCompleteView().",
                  RemovedInDjango21Warning, stacklevel=2)
    context = {
        'login_url': resolve_url(settings.LOGIN_URL),
        'title': 'Password reset complete',
    }
    if extra_context is not None:
        context.update(extra_context)

    return TemplateResponse(request, template_name, context)


def shop(request):
    pubs = Publishers.objects.all();
    if request.method == 'POST':
        if 'Engineering' in request.POST:
            engg = Ebooks.objects.filter(category__cat='Engineering')
            return render(request,'rapp/shop.html',{'ebooks':engg,'pubs':pubs})

        elif 'Medical' in request.POST:
            med = Ebooks.objects.filter(category__cat='Medical')
            return render(request,'rapp/shop.html',{'ebooks':med,'pubs':pubs})

        elif 'Novels' in request.POST:
            nov = Ebooks.objects.filter(category__cat='Novels')
            return render(request,'rapp/shop.html',{'ebooks':nov,'pubs':pubs})

        elif 'Stories' in request.POST:
            stor = Ebooks.objects.filter(category__cat='Stories')
            return render(request,'rapp/shop.html',{'ebooks':stor,'pubs':pubs})

        elif 'Biographies' in request.POST:
            bio = Ebooks.objects.filter(category__cat='Biographies')
            return render(request,'rapp/shop.html',{'ebooks':bio,'pubs':pubs})

        elif 'Self-Development' in request.POST:
            selfd = Ebooks.objects.filter(category__cat='Self-Development')
            return render(request,'rapp/shop.html',{'ebooks':selfd,'pubs':pubs})

    ebooks = Ebooks.objects.all()
    return render(request,'rapp/shop.html',{'ebooks':ebooks,'pubs':pubs})


def detail(request,id):
    ebook = Ebooks.objects.filter(id=id)[0]
    if request.user.is_authenticated:
        profilevector = ''
        profile_author = str(ebook.author.name).replace(" ","").lower()
        profilevector = profilevector + profile_author + ' ' + profile_author + ' ' + profile_author
        profile_publisher = str(ebook.publisher.name).replace(" ","").lower()
        profilevector = profilevector + ' ' + profile_publisher
        profile_category = str(ebook.category.cat).replace(" ","").lower()
        profilevector =  profilevector + ' ' + profile_category + ' ' + profile_category
        for tag in ebook.tags.all():
            tag = str(tag).replace(" ","").lower()
            profilevector = profilevector + ' ' + tag + ' ' + tag + ' ' + tag + ' ' + tag
        Detailview.objects.create(ebook=ebook,user=request.user,duration=0,profilevector=profilevector)
        try:
            rating = Rateduser.objects.filter(user=request.user,ebook=ebook)[0].rating
        except Exception as e:
            rating = 0
    else:
        rating = 0
    ebooks = Ebooks.objects.all()

    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user)
        wisharray = []
        for wish in wishlist:
            wisharray.append(wish.ebook.id)
    else:
        wisharray = []
    sugbooks = Ebooks.objects.filter(author=ebook.author)
    if sugbooks.count() > 1:
        sfbooks = sugbooks.exclude(id=ebook.id).order_by('-rating')
        sftitle = 'Author'
    elif Ebooks.objects.filter(publisher=ebook.publisher).count() > 1 and ebook.publisher.name != 'None':
        sfbooks =  Ebooks.objects.filter(publisher=ebook.publisher).exclude(id=ebook.id).order_by('-rating')
        sftitle = 'Publisher'
    if sfbooks.count() <= 5:
        sfless = True
    else:
        sfless = False

    return render(request,'rapp/detail.html',{'ebook':ebook,'ebooks':ebooks,'rating':rating,'wisharray':wisharray,'sfbooks':sfbooks,'sfless':sfless,'sftitle':sftitle})


@login_required
def cart(request):
    products = Usercart.objects.filter(user=request.user)
    tprice = 0
    for product in products:
        if product.buyrent == 'Rent':
            tprice = tprice + product.nprice
        elif product.buyrent == 'Buy':
            tprice = tprice + product.ebook.price

    if products.count() == 0:
        response = "Your cart is empty!"
    else:
        response = "Success"

    return render(request,'rapp/cart.html',{'products':products,'response':response,'tprice':round(tprice,3)})


@login_required
def add_cart(request):
    if request.method == 'POST':
        ebooknumber = request.POST['ebooknumber']
        ebook = Ebooks.objects.filter(id=ebooknumber)[0]
        nprice = ebook.price
        if ebook.category.catmodel == '12month':
            def getprice(argument):
                switcher = {
                    '3 days': 0.12*nprice,
                    '7 days': 0.18*nprice,
                    '14 days': 0.24*nprice,
                    '21 days': 0.30*nprice,
                    '1 month': 0.35*nprice,
                    '1.5 months': 0.40*nprice,
                    '2 months': 0.45*nprice,
                    '3 months': 0.48*nprice,
                    '4 months': 0.50*nprice,
                    '5 months': 0.53*nprice,
                    '6 months': 0.55*nprice,
                    '12 months': 0.70*nprice
                }
                return switcher.get(argument,"nothing")
            price = getprice('21 days')
        else:
            def getprice(argument):
                switcher = {
                    '3 days': 0.25*nprice,
                    '7 days': 0.35*nprice,
                    '14 days': 0.40*nprice,
                    '21 days': 0.45*nprice,
                    '1 month': 0.50*nprice,
                    '1.5 months': 0.55*nprice,
                    '2 months': 0.65*nprice,
                    '3 months':0.70*nprice
                }
                return switcher.get(argument,"nothing")
            price = getprice('21 days')
        check = Usercart.objects.filter(user=request.user,ebook=ebook)
        if check.count() == 0:
            usercart = Usercart.objects.get_or_create(user=request.user,ebook=ebook,duration='21 days',nprice=price)
            if usercart:
                return HttpResponse('Added to cart successfully!')
            else:
                return HttpResponse('Please try again later!')
        else:
            return HttpResponse('This e-book is already in your cart!')

@login_required
def change_duration(request):
    if request.method == 'POST':
        ebookid = request.POST['ebookid']
        duration = request.POST['duration']
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        trans = Usercart.objects.filter(user=request.user,ebook=ebook)[0]
        trans.duration = duration
        oprice = ebook.price
        if ebook.category.cat == ('Engineering' or 'Medical'):
            def getprice(argument):
                switcher = {
                    '3 days': 0.05 * oprice,
                    '7 days': 0.08 * oprice,
                    '14 days': 0.13 * oprice,
                    '21 days': 0.17 * oprice,
                    '1 month': 0.20 * oprice,
                    '1.5 months': 0.26 * oprice,
                    '2 months': 0.30 * oprice,
                    '3 months': 0.35 * oprice,
                    '4 months': 0.40 * oprice,
                    '5 months': 0.45 * oprice,
                    '6 months': 0.50 * oprice,
                    '12 months': 0.65 * oprice
                }
                return switcher.get(argument, "nothing")

            trans.nprice = getprice(duration)
        else:
            def getprice(argument):
                switcher = {
                    '3 days': 0.08 * oprice,
                    '7 days': 0.15 * oprice,
                    '14 days': 0.25 * oprice,
                    '21 days': 0.32 * oprice,
                    '1 month': 0.40 * oprice,
                    '1.5 months': 0.50 * oprice,
                    '2 months': 0.60 * oprice
                }
                return switcher.get(argument, "nothing")

            trans.nprice = getprice(duration)
        trans.save()
        products = Usercart.objects.filter(user=request.user)
        tprice = 0
        for product in products:
            tprice = tprice + product.nprice
        return HttpResponse(json.dumps({"nprice": round(trans.nprice,3), "tprice": round(tprice,3)}), content_type="application/json")

@login_required
def change_buy(request):
    if request.method == 'POST':
        ebookid = request.POST['ebookid']
        buy = request.POST['buy']
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        trans = Usercart.objects.filter(user=request.user,ebook=ebook)[0]
        trans.buyrent = buy

        trans.save()
        products = Usercart.objects.filter(user=request.user)
        tprice = 0
        for product in products:
            if product.buyrent == 'Rent':
                tprice = tprice + product.nprice
            elif product.buyrent == 'Buy':
                tprice = tprice + product.ebook.price
        if trans.buyrent == 'Buy':
            nprice = trans.ebook.price
        elif trans.buyrent == 'Rent':
            nprice = trans.nprice
        return HttpResponse(json.dumps({"nprice": round(nprice,3), "tprice": round(tprice,3)}), content_type="application/json")

@login_required
def delete_cart(request):
    if request.method == 'POST':
        ebookid = request.POST['ebookid']
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        usercart = Usercart.objects.filter(user=request.user,ebook=ebook)[0]
        usercart.delete()
        return HttpResponse('Success')



@login_required
def wishlist(request):
    list = Wishlist.objects.filter(user=request.user)
    return render(request,'rapp/wishlist.html',{'list':list})


@login_required
def delete_wishlist(request):
    if request.method == 'POST':
        ebookid = int(request.POST['ebookid'])
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        wishlist = Wishlist.objects.filter(user=request.user,ebook=ebook)[0]
        wishlist.delete()
        return HttpResponse('Success')


@login_required
def mtc(request):
    if request.method == 'POST':
        ebookid = request.POST['ebookid']
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        if Usercart.objects.filter(user=request.user,ebook=ebook).exists():
            return HttpResponse('Already in Cart!')
        else:
            wishlist = Wishlist.objects.filter(user=request.user,ebook=ebook)[0]
            wishlist.delete()
            nprice = ebook.price
            if ebook.category.catmodel == '12month':
                def getprice(argument):
                    switcher = {
                        '3 days': 0.12*nprice,
                        '7 days': 0.18*nprice,
                        '14 days': 0.24*nprice,
                        '21 days': 0.30*nprice,
                        '1 month': 0.35*nprice,
                        '1.5 months': 0.40*nprice,
                        '2 months': 0.45*nprice,
                        '3 months': 0.48*nprice,
                        '4 months': 0.50*nprice,
                        '5 months': 0.53*nprice,
                        '6 months': 0.55*nprice,
                        '12 months': 0.70*nprice
                    }
                    return switcher.get(argument,"nothing")
                price = getprice('21 days')
            else:
                def getprice(argument):
                    switcher = {
                        '3 days': 0.25*nprice,
                        '7 days': 0.35*nprice,
                        '14 days': 0.40*nprice,
                        '21 days': 0.45*nprice,
                        '1 month': 0.50*nprice,
                        '1.5 months': 0.55*nprice,
                        '2 months': 0.65*nprice,
                        '3 months':0.70*nprice
                    }
                    return switcher.get(argument,"nothing")
                price = getprice('21 days')
            usercart = Usercart.objects.create(user=request.user, ebook=ebook,duration='21 days',nprice=price)
            return HttpResponse('Success')


@login_required
def mtw(request):
    if request.method == 'POST':
        ebookid = request.POST['ebookid']
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        usercart = Usercart.objects.filter(user=request.user,ebook=ebook)[0]
        usercart.delete()
        wishlist = Wishlist.objects.get_or_create(user=request.user,ebook=ebook)
        return HttpResponse('Success')

@login_required
def atw(request):
    if request.method == 'POST':
        ebookid = int(request.POST['ebooknumber'])
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        check = Wishlist.objects.filter(user=request.user,ebook=ebook)
        if not check.exists():
            wish = Wishlist.objects.create(user=request.user,ebook=ebook)
            if wish:
                return HttpResponse('Added to wishlist successfully!')
            else:
                return HttpResponse('Please try again later!')
        else:
            return HttpResponse('This e-book is already in your Wishlist!')

@login_required
def payment(request):
    try:
        products = Usercart.objects.filter(user=request.user)
        tprice = 0
        for product in products:
            if product.buyrent == 'Rent':
                tprice = tprice + product.nprice
            elif product.buyrent == 'Buy':
                tprice = tprice + product.ebook.price
    except Exception as e:
        tprice = 0

    return render(request, "rapp/payment.html", {'tprice':tprice})


@login_required
def generate_hash(request, txnid):
    try:
        # get keys and SALT from dashboard once account is created.
        # hashSequence = "key|txnid|amount|productinfo|firstname|email|udf1|udf2|udf3|udf4|udf5|udf6|udf7|udf8|udf9|udf10"
        hash_string = get_hash_string(request, txnid)
        generated_hash = hashlib.sha512(hash_string.encode('utf-8')).hexdigest().lower()
        return generated_hash
    except Exception as e:
        # log the error here.
        logging.getLogger("error_logger").error(traceback.format_exc())
        return None


@login_required
def get_hash_string(request, txnid):
    amount = 0.000
    usercart = Usercart.objects.filter(user=request.user)
    for userc in usercart:
        amount = amount + userc.nprice
    hash_string = config.KEY + "|" + txnid + "|" + str(
        float(amount)) + "|" + constants.PAID_FEE_PRODUCT_INFO + "|"
    hash_string += request.user.username + "|" + request.user.email + "|"
    hash_string += "||||||||||" + config.SALT

    return hash_string


@login_required
def get_transaction_id():
    hash_object = hashlib.sha256(str(randint(0, 9999)).encode("utf-8"))
    # take approprite length
    txnid = hash_object.hexdigest().lower()[0:32]
    return txnid


@login_required
@csrf_exempt
def payment_success(request,transid):
    trans = Transactions.objects.all()
    for tran in trans:
        if tran.txnid == transid:
            carts = Usercart.objects.filter(user=request.user)
            for cart in carts:
                active = Dashboard.objects.get_or_create(user=request.user,ebook=cart.ebook,duration=cart.duration,nprice=cart.nprice,active=True)
                cart.delete()
            data = {}
            return render(request, "rapp/success.html", data)

    return render(request,'rapp/failure.html',{})


@login_required()
@csrf_exempt
def payment_failure(request):
    data = {}
    return render(request, "rapp/failure.html", data)


@login_required()
def dashboard(request):
    remaind = []
    remainh = []
    remainm = []
    def transformer(duration):
        switcher = {
            '3 days': 3,
            '7 days': 7,
            '14 days': 14,
            '21 days': 21,
            '1 month': 30,
            '1.5 months': 45,
            '2 months': 60,
            '3 months': 90,
            '4 months': 120,
            '5 months': 150,
            '6 months': 180,
            '12 months': 360
        }
        return switcher.get(duration, "nothing")

    dashes = Dashboard.objects.filter(user=request.user).exclude(duration='Buy')
    for dash in dashes:
        now = datetime.now()
        itime = dash.itime
        yeardif = now.year - itime.year
        monthdif = now.month - itime.month
        daydif = now.day - itime.day
        hourdif = now.hour - itime.hour
        minutedif = now.minute - itime.minute
        seconddif = now.second - itime.second
        if yeardif >0 and monthdif<0:
            yeardif = yeardif - 1
            monthdif = 12 + monthdif
            if daydif < 0:
                monthdif = monthdif -1
                daydif = 30 + daydif
                if hourdif < 0:
                    daydif = daydif -1
                    hourdif = 24 +  hourdif
                    if minutedif < 0:
                        hourdif = hourdif -1
                        minutedif = 60 + minutedif
                        if seconddif < 0:
                            minutedif = minutedif -1
                            seconddif = 60 + seconddif
                    else:
                        if seconddif < 0:
                            minutedif = minutedif -1
                            seconddif = 60 + seconddif
                else:
                    if minutedif < 0:
                        hourdif = hourdif -1
                        minutedif = 60 + minutedif
                        if seconddif < 0:
                            minutedif = minutedif -1
                            seconddif = 60 + seconddif
                    else:
                        if seconddif < 0:
                            minutedif = minutedif -1
                            seconddif = 60 + seconddif
            else:
                if hourdif < 0:
                    daydif = daydif -1
                    hourdif = 24 +  hourdif
                    if minutedif < 0:
                        hourdif = hourdif -1
                        minutedif = 60 + minutedif
                        if seconddif < 0:
                            minutedif = minutedif -1
                            seconddif = 60 + seconddif
                    else:
                        if seconddif < 0:
                            minutedif = minutedif -1
                            seconddif = 60 + seconddif
                else:
                    if minutedif < 0:
                        hourdif = hourdif -1
                        minutedif = 60 + minutedif
                        if seconddif < 0:
                            minutedif = minutedif -1
                            seconddif = 60 + seconddif
                    else:
                        if seconddif < 0:
                            minutedif = minutedif -1
                            seconddif = 60 + seconddif

        else:
            if daydif < 0:
                monthdif = monthdif -1
                daydif = 30 + daydif
                if hourdif < 0:
                    daydif = daydif -1
                    hourdif = 24 +  hourdif
                    if minutedif < 0:
                        hourdif = hourdif -1
                        minutedif = 60 + minutedif
                        if seconddif < 0:
                            minutedif = minutedif -1
                            seconddif = 60 + seconddif
                    else:
                        if seconddif < 0:
                            minutedif = minutedif -1
                            seconddif = 60 + seconddif
                else:
                    if minutedif < 0:
                        hourdif = hourdif -1
                        minutedif = 60 + minutedif
                        if seconddif < 0:
                            minutedif = minutedif -1
                            seconddif = 60 + seconddif
                    else:
                        if seconddif < 0:
                            minutedif = minutedif -1
                            seconddif = 60 + seconddif
            else:
                if hourdif < 0:
                    daydif = daydif -1
                    hourdif = 24 +  hourdif
                    if minutedif < 0:
                        hourdif = hourdif -1
                        minutedif = 60 + minutedif
                        if seconddif < 0:
                            minutedif = minutedif -1
                            seconddif = 60 + seconddif
                    else:
                        if seconddif < 0:
                            minutedif = minutedif -1
                            seconddif = 60 + seconddif
                else:
                    if minutedif < 0:
                        hourdif = hourdif -1
                        minutedif = 60 + minutedif
                        if seconddif < 0:
                            minutedif = minutedif -1
                            seconddif = 60 + seconddif
                    else:
                        if seconddif < 0:
                            minutedif = minutedif -1
                            seconddif = 60 + seconddif

        effective = (yeardif*360) + (monthdif*30) + daydif + (hourdif/24) + (minutedif/1440) + (seconddif/86400)
        dayu = (yeardif*360) + (monthdif*30) + daydif
        houru = hourdif
        minu = minutedif
        if hourdif < 0:
            dayu = dayu -1
            houru = 24 + hourdif
        if minutedif < 0:
            houru = houru - 1
            minu = 60 + minutedif
        rdayu = transformer(dash.duration) - dayu - 1
        rhouru = 24 - houru - 1
        rminu = 60 - minu
        if effective > transformer(dash.duration):
            dash.active = False
        else:
            remaind.append(rdayu)
            remainh.append(rhouru)
            remainm.append(rminu)
    bdashes = Dashboard.objects.filter(user=request.user,duration='Buy')

    return render(request,'rapp/dashboard.html',{'dashes':dashes,'remaind':remaind,'remainh':remainh,'remainm':remainm,'bdashes':bdashes})


@login_required
def reader(request,id):
    return render(request,'interface/the_outsiders_se_hinton/index.html',{})


def recommender(user):
    musiclis = Musiclis.objects.filter(user=user)
    tagdict = {}
    genredict = {}
    for item in musiclis:
        yeardiff = (datetime.now().year - item.time.year)*365
        monthdff = (datetime.now().month - item.time.month)*30
        daydiff = datetime.now().day - item.time.day
        diff = datetime.now(timezone.utc) - item.time
        if diff.days <= 3:
            alpha = 1
        elif 3 < diff.days <= 7:
            alpha = 0.95
        elif 3 < diff.days <= 7:
            alpha = 0.90
        elif 7 < diff.days <= 14:
            alpha = 0.85
        elif 14 < diff.days <= 21:
            alpha = 0.80
        elif 21 < diff.days <= 28:
            alpha = 0.75
        elif 28 < diff.days <= 40:
            alpha = 0.70
        elif 40 < diff.days <= 60:
            alpha = 0.65
        elif 60 < diff.days <= 100:
            alpha = 0.60
        elif diff.days > 100:
            alpha = 0.55
        for tag in item.music.tag.all():
            if tag.name in tagdict:
                tagdict[tag.name] = tagdict[tag.name] +  (1*alpha)
            else:
                tagdict[tag.name] = 1*alpha
        if item.music.genre.name in genredict:
            genredict[item.music.genre.name] = genredict[item.music.genre.name] + 1*alpha
        else:
            genredict[item.music.genre.name] = 1 * alpha
    music = Music.objects.all()
    musdict = {}
    for mus in music:
      if not Musiclis.objects.filter(music=mus, user=user).exists():
        for tag in mus.tag.all():
            if tag.name in tagdict:
                if mus in musdict:
                    musdict[mus] = musdict[mus] + tagdict[tag.name]
                else:
                    musdict[mus] = tagdict[tag.name]
        if mus.genre.name in genredict:
            if mus in musdict:
                musdict[mus] = musdict[mus] + genredict[mus.genre.name]
            else:
                musdict[mus] = genredict[mus.genre.name]

    return musdict


def read(request,id):
    try:
        musdict = recommender(request.user)
    except Exception as e:
        musdict = {}
    book = Ebooks.objects.filter(id=id)[0]
    pages = book.pages
    esource = book.content
    ename = book.name
    eauthor = book.author
    elang = book.language
    musicp = Music.objects.all().order_by('-listennum')
    musicr = Music.objects.all().order_by('-priority')
    def musicsorter(i,musdict):
        if i in musdict:
            p = musdict[i]
        else:
            p = 0
        return p

    musicrr = sorted(musicr, key=lambda i:musicsorter(i,musdict),reverse=True)
    musicgenre = Musicgenre.objects.all()
    existing_lis = []
    new_lis = []
    try:
        musiclis = Musiclis.objects.filter(user=request.user,queue=True)
        for lisi in musiclis:
            if lisi.music in existing_lis:
                thu = {i for i, t in enumerate(new_lis) if t[0] == lisi.music.id}
                new_lis[list(thu)[0]][5] = new_lis[list(thu)[0]][5] + 1
            else:
                existing_lis.append(lisi.music)
                new_lis.append([lisi.music.id,lisi.music.name,lisi.music.artist,lisi.music.duration,lisi.music.media,1,lisi.music.image])
        new_lis2 = sorted(new_lis,key=lambda i:i[5],reverse=True)
        playlist = Playlist.objects.filter(user=request.user)
    except Exception as e:
        new_lis2 = []
        musiclis = ''
        playlist = ''
    if request.user.is_authenticated:
        checklen = len(Dashboard.objects.filter(user=request.user,ebook=book,active=True))
        if checklen >0:
            check = True
            bookmarks = Bookmark.objects.filter(user=request.user,ebook=book)
            bookmarkarr = []
            bookmarkdataarr = []
            for bookmark in bookmarks:
                bookmarkarr.append(bookmark.location)
                bookmarkdataarr.append(bookmark.data)
            highlightarr = []
            highlightcolorarr = []
            highlighttextarr = []
            highlights = Highlight.objects.filter(user=request.user,ebook=book)
            for highlight in highlights:
                highlightarr.append(highlight.cfirange)
                highlightcolorarr.append(highlight.color)
                if highlight.text != None:
                    highlighttextarr.append(highlight.text)
                else:
                    highlighttextarr.append('')
            notes = Highlight.objects.filter(user=request.user,ebook=book,note=True)
            notetextarr = []
            noteselectedtextarr = []
            notecfiarr = []
            for note in notes:
                notetextarr.append(note.text)
                noteselectedtextarr.append(note.selectedtext)
                notecfiarr.append(note.cfirange)
            notefiles = Notefile.objects.filter(user=request.user,ebook=book)
            notefileitems = Notefileitem.objects.filter(notefile__in=notefiles)
            notefilearr = []
            for file in notefiles:
                filenotearr = []
                filetextarr = []
                for item in notefileitems.filter(notefile=file):
                    filenotearr.append(item.note)
                    filetextarr.append(item.text)
                notefilearr.append([file.name,file.date,filenotearr,filetextarr])
        else:
            check = 'No book'
            bookmarkarr = []
            highlightarr = []
            highlightcolorarr = []
            highlighttextarr = []
            bookmarkdataarr = []
            notetextarr = []
            noteselectedtextarr = []
            notecfiarr = []
            notefilearr =[]
    else:
        check = False
        bookmarkarr = []
        highlightarr = []
        highlightcolorarr = []
        highlighttextarr = []
        bookmarkdataarr = []
        notetextarr = []
        noteselectedtextarr = []
        notecfiarr = []
        notefilearr = []
    if request.user.is_authenticated:
        profilevector = ''
        profile_author = str(book.author.name).replace(" ","").lower()
        profilevector = profilevector + profile_author + ' ' + profile_author + ' ' + profile_author
        profile_publisher = str(book.publisher.name).replace(" ","").lower()
        profilevector = profilevector + ' ' + profile_publisher
        profile_category = str(book.category.cat).replace(" ","").lower()
        profilevector =  profilevector + ' ' + profile_category + ' ' + profile_category
        for tag in book.tags.all():
            tag = str(tag).replace(" ","").lower()
            profilevector = profilevector + ' ' + tag + ' ' + tag + ' ' + tag + ' ' + tag
        Readview.objects.create(ebook=book,user=request.user,duration=0,profilevector=profilevector)
        if Lastpage.objects.filter(user=request.user,ebook=book).exists():
            lastcfi = Lastpage.objects.filter(user=request.user,ebook=book)[0].epubcfi
        else:
            lastcfi = ''
        if Rateduser.objects.filter(user=request.user,ebook=book).exists():
            ratingbox = 0
        else:
            ratingbox = 1
        if ConnectionHistory.objects.filter(user=request.user).exists():
            conni = ConnectionHistory.objects.filter(user=request.user,status__gte=1)
            connlen = conni.count()
            for conn in conni:
                timediff = (datetime.now(timezone.utc) - conn.echo)/timedelta(minutes=1)
                if timediff >= 1440:
                    conn.status = 0
                    conn.save()
            if connlen >= 3:
                check = False
    else:
        lastcfi = ''
        ratingbox = 0

    return render(request,'rapp/read.html',{'pages':pages,'id':id,'check':check,'bookmarkarr':bookmarkarr,'musicp':musicp,'musicr':musicrr,'musicgenre':musicgenre,'musiclis':new_lis2,'musiclislen':len(musiclis),'playlist':playlist,'esource':str(esource),'ename':ename,'eauthor':eauthor,'highlightarr':highlightarr,'highlightcolorarr':highlightcolorarr,'highlighttextarr':highlighttextarr,'elang':elang,'bookmarkdataarr':bookmarkdataarr,'notetextarr':notetextarr,'noteselectedtextarr':noteselectedtextarr,'notecfiarr':notecfiarr,'notefilearr':notefilearr,'lastcfi':lastcfi,'ratingbox':ratingbox})


def sample(request,id):
    book = Ebooks.objects.filter(id=id)[0]
    pagesfull = book.pages
    if pagesfull <= 300:
        pages = round(0.08*pagesfull)
    elif 300 < pagesfull <= 600:
        pages = round(0.07*pagesfull)
    elif 600 < pagesfull <= 900:
        pages = round(0.06*pagesfull)
    elif 900 < pagesfull <= 1200:
        pages = round(0.05*pagesfull)
    else:
        pages =round(0.04*pagesfull)
    if request.user.is_authenticated():
        if len(Notes.objects.filter(user=request.user)) >0:
            notes = Notes.objects.filter(user=request.user)
        else:
            notes = False
    else:
        user = User.objects.filter(email='trialuser@gmail.com')[0]
        if len(Notes.objects.filter(user=user)) >0:
            notes = Notes.objects.filter(user=user)
        else:
            notes = False
    if request.user.is_authenticated:
        if len(Lastpage.objects.filter(user=request.user,ebook=book))>0:
            if (datetime.now(timezone.utc) - Lastpage.objects.filter(user=request.user,ebook=book)[0].time).total_seconds() <10:
                lastpage = Lastpage.objects.filter(user=request.user,ebook=book)[0].page
            else:
                lastpage = False
        else:
            lastpage = False
    else:
        lastpage = False

    if request.user.is_authenticated:
        profilevector = ''
        profile_author = str(book.author.name).replace(" ","").lower()
        profilevector = profilevector + profile_author + ' ' + profile_author + ' ' + profile_author
        profile_publisher = str(book.publisher.name).replace(" ","").lower()
        profilevector = profilevector + ' ' + profile_publisher
        profile_category = str(book.category.cat).replace(" ","").lower()
        profilevector =  profilevector + ' ' + profile_category + ' ' + profile_category
        for tag in book.tags.all():
            tag = str(tag).replace(" ","").lower()
            profilevector = profilevector + ' ' + tag + ' ' + tag + ' ' + tag + ' ' + tag
        Sampleview.objects.create(ebook=book,user=request.user,duration=0,profilevector=profilevector)

    return render(request,'rapp/sample.html',{'pages':pagesfull,'id':id,'notes':notes,'lastpage':lastpage,'pagesaccess':pages})


def add_notes(request):
    if request.method == 'POST':
        title = request.POST['title']
        text = request.POST['text']
        if request.user.is_authenticated:
            notes = Notes.objects.filter(user=request.user,title=title)
            if notes.exists():
                obj = notes[0]
                obj.text = text
                obj.save()
            else:
                Notes.objects.create(user=request.user,title=title,text=text)
            allnotes = Notes.objects.filter(user=request.user)
            html = render_to_string('rapp/notestemplate.html',{'notes':allnotes})
        else:
            user = User.objects.filter(email='trialuser@gmail.com')[0]
            notes = Notes.objects.filter(user=user, title=title)
            if notes.exists():
                obj = notes[0]
                obj.text = text
                obj.save()
            else:
                Notes.objects.create(user=user, title=title, text=text)
            allnotes = Notes.objects.filter(user=user)
            html = render_to_string('rapp/notestemplate.html', {'notes': allnotes})
        return HttpResponse(html)


def save_page(request):
    if request.method == 'POST':
        ebookid = int(request.POST['ebookid'])
        epubcfi = request.POST['epubcfi']
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        if request.user.is_authenticated:
            if Lastpage.objects.filter(user=request.user,ebook=ebook).exists():
                last = Lastpage.objects.filter(user=request.user,ebook=ebook)[0]
                last.epubcfi = epubcfi
                last.save()
            else:
                Lastpage.objects.create(user=request.user,ebook=ebook,epubcfi=epubcfi)
        return HttpResponse('Success')


def searchi(request):
    return render(request,'rapp/search.html',{})


def erecommender(user):
    musiclis = Musiclis.objects.filter(user=user)
    tagdict = {}
    genredict = {}
    for item in musiclis:
        yeardiff = (datetime.now().year - item.time.year)*365
        monthdff = (datetime.now().month - item.time.month)*30
        daydiff = datetime.now().day - item.time.day
        diff = datetime.now(timezone.utc) - item.time
        if diff.days <= 3:
            alpha = 1
        elif 3 < diff.days <= 7:
            alpha = 0.95
        elif 3 < diff.days <= 7:
            alpha = 0.90
        elif 7 < diff.days <= 14:
            alpha = 0.85
        elif 14 < diff.days <= 21:
            alpha = 0.80
        elif 21 < diff.days <= 28:
            alpha = 0.75
        elif 28 < diff.days <= 40:
            alpha = 0.70
        elif 40 < diff.days <= 60:
            alpha = 0.65
        elif 60 < diff.days <= 100:
            alpha = 0.60
        elif diff.days > 100:
            alpha = 0.55
        for tag in item.music.tag.all():
            if tag.name in tagdict:
                tagdict[tag.name] = tagdict[tag.name] +  (1*alpha)
            else:
                tagdict[tag.name] = 1*alpha
        if item.music.genre.name in genredict:
            genredict[item.music.genre.name] = genredict[item.music.genre.name] + 1*alpha
        else:
            genredict[item.music.genre.name] = 1 * alpha
    music = Music.objects.all()
    musdict = {}
    for mus in music:
      if not Musiclis.objects.filter(music=mus, user=user).exists():
        for tag in mus.tag.all():
            if tag.name in tagdict:
                if mus in musdict:
                    musdict[mus] = musdict[mus] + tagdict[tag.name]
                else:
                    musdict[mus] = tagdict[tag.name]
        if mus.genre.name in genredict:
            if mus in musdict:
                musdict[mus] = musdict[mus] + genredict[mus.genre.name]
            else:
                musdict[mus] = genredict[mus.genre.name]

    return musdict


class MySearchView(SearchView):
    """My custom search view."""
    template_name = 'search/search.html'
    form_class = PriceRangeSearchForm

    def get_queryset(self):
        queryset = super(MySearchView, self).get_queryset()
        pqueryset = queryset.order_by('-priority')
        # further filter queryset based on some set of criteria
        '''paginator = Paginator(pqueryset, 2)
        page = self.request.GET.get('page')
        if page:
            sqs = SearchQuerySet().filter(content=AutoQuery(page))
            sqs = sqs.filter(product_url=Clean(self.request.GET['page']))
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            items = paginator.page(1)
        except EmptyPage:
            items = paginator.page(paginator.num_pages) 
        #return pqueryset
        return items'''
        #sqs = SearchQuerySet().load_all().auto_query('English').order_by('-priority')[:3]
        return pqueryset

    def get_context_data(self, *args, **kwargs):
        context = super(MySearchView, self).get_context_data(*args, **kwargs)
        print(context)
        res = SearchQuerySet().auto_query('dilk')
        spellres = res.spelling_suggestion()
        print(res)
        print(spellres)
        books = Ebooks.objects.all()
        priceArr =[]
        pagesArr =[]
        for book in books:
            priceArr.append(book.price)
            pagesArr.append(book.pages)
        lprice = min(priceArr)
        hprice = max(priceArr)
        lpages = min(pagesArr)
        hpages = max(pagesArr)
        pubs = Publishers.objects.all();
        totalBooks = Ebooks.objects.all().count()
        books = self.get_queryset();
        paginator = Paginator(books,40)
        page = self.request.GET.get('pag')
        try:
            items = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            items = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            items = paginator.page(paginator.num_pages)
        offermp2 = Offer.objects.all()[0]
        ebooks = Ebooks.objects.all()

        context.update({'lprice':lprice,'hprice':hprice,'lpages':lpages,'hpages':hpages,'pubs':pubs,'books':items,'page':page,'totalBooks':totalBooks,'offermp2':offermp2,'ebooks':ebooks})
        # do something
        return context


def search(request):
    try:
        q = request.GET['q']
        query = True
        sqs = SearchQuerySet().filter(content=AutoQuery(q))
        if request.user.is_authenticated:
            stop = set(stopwords.words('english'))
            tokenarr = [i for i in q.lower().split() if i not in stop]
            for author in Authors.objects.select_related():
                autharr = [i for i in str(author.name).lower().split()]
                if autharr == tokenarr:
                    print('Yes')
            profilevector = str(q).replace(" ","").lower()
            #Searchview.objects.create(user=request.user, duration=0,profilevector=profilevector)
        try:
            hl = request.GET['hl']
            if hl == 'true':
                sqs = sqs.order_by('-price')
            elif hl == 'false':
                sqs = sqs.order_by('price')
        except Exception as e:
            pass
        try:
            page = request.GET['page']
            if page == 'l1':
                sqs = sqs.filter(pages__in=list(range(0,100)))
            elif page == '12':
                sqs = sqs.filter(pages__in=list(range(100,201)))
            elif page == '23':
                sqs = sqs.filter(pages__in=list(range(200,301)))
            elif page == 'm3':
                try:
                  sqs = sqs.filter(pages__in=list(range(301,1000)))
                except Exception as e:
                    sqs = sqs.filter(pages__in=list(range(1000,1700)))
        except Exception as e:
            pass
        try:
            pub = request.GET['pub']
            pubarr = pub[pub.index('[')+1:pub.index(']')].split(',')
            publist = []
            for i in pubarr:
                pubid = int(i)
                publisher = Publishers.objects.filter(id=pubid)[0]
                publist.append(publisher.name)
            sqs = sqs.filter(publisher__in=publist)
        except Exception as e:
            pass
        spellres = sqs.spelling_suggestion()
        searchtitle = q
    except Exception as e:
        try:
            cat = request.GET['cat']
            category = Category.objects.filter(cat=cat)[0]
            sqs = Ebooks.objects.filter(category=category)
            spellres = ''
            query = True
            egeneralquery = True
            if request.user.is_authenticated:
                profilevector = str(cat).replace(" ", "").lower() + ' ' + str(cat).replace(" ", "").lower()
                Genreview.objects.create(genre=category,user=request.user, duration=0, profilevector=profilevector)
            searchtitle = cat
        except Exception as e:
            try:
                nr = request.GET['nr']
                if nr == 'true':
                    datethresh = datetime.now() - timedelta(days=365)
                    sqs = Ebooks.objects.filter(publishdate__gte=datethresh)
                    spellres = ''
                    query = True
                    egeneralquery = True
                    if request.user.is_authenticated:
                        Newreleaseview.objects.create(user=request.user, duration=0)
                    searchtitle = 'New Releases'
                else:
                    sqs = ''
                    spellres = ''
                    query = False
                    egeneralquery = ''
                    searchtitle = ''
            except Exception as e:
                try:
                    bs = request.GET['bs']
                    if bs == 'true':
                        sqs0 = Bestseller.objects.filter(name='Bestsellers')[0]
                        sqs = sqs0.ebooks.all
                        spellres = ''
                        query = True
                        egeneralquery = False
                        if request.user.is_authenticated:
                            Bestsellerview.objects.create(user=request.user, duration=0)
                        searchtitle = 'Bestsellers'
                    else:
                        sqs = ''
                        spellres = ''
                        query = False
                        egeneralquery = ''
                        searchtitle = ''
                except Exception as e:
                    sqs = ''
                    spellres = ''
                    query = False
                    egeneralquery = ''
                    searchtitle = ''

        if egeneralquery == True:
            try:
                hl = request.GET['hl']
                if hl == 'true':
                    sqs = sqs.order_by('-price')
                elif hl == 'false':
                    sqs = sqs.order_by('price')
            except Exception as e:
                pass
            try:
                page = request.GET['page']
                if page == 'l1':
                    sqs = sqs.filter(pages__in=list(range(0,100)))
                elif page == '12':
                    sqs = sqs.filter(pages__in=list(range(100,201)))
                elif page == '23':
                    sqs = sqs.filter(pages__in=list(range(200,301)))
                elif page == 'm3':
                    try:
                      sqs = sqs.filter(pages__in=list(range(301,1000)))
                    except Exception as e:
                        sqs = sqs.filter(pages__in=list(range(1000,1700)))
            except Exception as e:
                pass
            try:
                pub = request.GET['pub']
                pubarr = pub[pub.index('[')+1:pub.index(']')].split(',')
                publist = []
                for i in pubarr:
                    pubid = int(i)
                    publisher = Publishers.objects.filter(id=pubid)[0]
                    publist.append(publisher.name)
                sqs = sqs.filter(publisher__name__in=publist)
            except Exception as e:
                pass
        elif egeneralquery ==False:
            try:
                hl = request.GET['hl']
                if hl == 'true':
                    sqs = sqs0.ebooks.all().order_by('-price')
                elif hl == 'false':
                    sqs = sqs0.ebooks.all().order_by('price')
            except Exception as e:
                pass
            try:
                page = request.GET['page']
                if page == 'l1':
                    sqs = sqs0.ebooks.filter(pages__in=list(range(0,100)))
                elif page == '12':
                    sqs = sqs0.ebooks.filter(pages__in=list(range(100,201)))
                elif page == '23':
                    sqs = sqs0.ebooks.filter(pages__in=list(range(200,301)))
                elif page == 'm3':
                    try:
                      sqs = sqs0.ebooks.filter(pages__in=list(range(301,1000)))
                    except Exception as e:
                        sqs = sqs0.ebooks.filter(pages__in=list(range(1000,1700)))
            except Exception as e:
                pass
            try:
                pub = request.GET['pub']
                pubarr = pub[pub.index('[')+1:pub.index(']')].split(',')
                publist = []
                for i in pubarr:
                    pubid = int(i)
                    publisher = Publishers.objects.filter(id=pubid)[0]
                    publist.append(publisher.name)
                sqs = sqs0.ebooks.filter(publisher__name__in=publist)
            except Exception as e:
                pass

    paginator = Paginator(sqs, 36)
    page = request.GET.get('pag')
    try:
        items = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        items = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        items = paginator.page(paginator.num_pages)

    pubs = Publishers.objects.all()
    offermp2 = Offer.objects.all()[0]
    ebooks = Ebooks.objects.all()
    if request.user.is_authenticated:
        wishlist = Wishlist.objects.filter(user=request.user)
        wisharray = []
        for wish in wishlist:
            wisharray.append(wish.ebook.id)
    else:
        wisharray = []

    return render(request,'rapp/searchshop.html',{'sqs':items,'pubs':pubs,'offermp2':offermp2,'ebooks':ebooks,'spellres':spellres,'query':query,'searchtitle':searchtitle,'wisharray':wisharray})


def autocomplete(request):
    sqs1 = SearchQuerySet().autocomplete(name_auto=request.GET.get('q', ''))
    sqs2 = SearchQuerySet().autocomplete(author_auto=request.GET.get('q', ''))
    sqs3 = SearchQuerySet().autocomplete(publisher_auto=request.GET.get('q', ''))
    sqs4 = SearchQuerySet().autocomplete(category_auto=request.GET.get('q', ''))
    sqs5 = SearchQuerySet().autocomplete(isbn_auto=request.GET.get('q', ''))
    sqs6 = SearchQuerySet().autocomplete(tags_auto=request.GET.get('q', ''))
    suggestions1 = [result.name for result in sqs1]
    suggestions2 = list(set([result.author for result in sqs2]))
    suggestions3 = list(set([result.publisher for result in sqs3]))
    suggestions4 = list(set([result.category for result in sqs4]))
    suggestions5 = list(set([result.isbn for result in sqs5]))
    suggestions6 = list(set([result.tags[2:len(result.tags)-2] for result in sqs6]))
    # Make sure you return a JSON object, not a bare list.
    # Otherwise, you could be vulnerable to an XSS attack.
    data = json.dumps({
        'results1': suggestions1,'results2':suggestions2,'results3': suggestions3,'results4':suggestions4,'results5': suggestions5,'results6':suggestions6
    })
    return HttpResponse(data, content_type='application/json')


class FacetedSearchView(SearchView):
    """My custom search view."""
    template = 'search/search.html'
    form_class = FacetedSearchForm
    facet_fields = ['author']
    def get_queryset(self):
        queryset = super(FacetedSearchView, self).get_queryset()
        # further filter queryset based on some set of criteria
        return queryset.all()

    def get_context_data(self, *args, **kwargs):
        context = super(FacetedSearchView, self).get_context_data(*args, **kwargs)
        # do something
        return context

    def extra_context(self):
        extra = super(FacetedSearchView, self).extra_context()

        if self.results == []:
            extra['facets'] = self.form.search().facet_counts()
        else:
            extra['facets'] = self.results.facet_counts()

        return extra


@login_required
def publisher(request):
    if request.method == 'POST':
        files = request.FILES.getlist('file')
        pub = Publishers.objects.filter(name=request.POST['publisher'])[0]
        for f in files:
            fs = FileSystemStorage(location='media/pubupload')
            file = fs.save(f.name, f)
            Uploaded.objects.create(publisher=pub,file='/media/pubupload/' + fs.url(file)[7:])
        return HttpResponse('Success')
    else:
        pass

    if len(UserP.objects.filter(user=request.user)) ==1:
        allow = True
        publisher = UserP.objects.filter(user=request.user)[0].publisher
        publisherName = publisher.name
        numBooks = len(Ebooks.objects.filter(publisher=Publishers.objects.filter(name=publisherName)[0]))
        monthlabel = []
        weeklabel = []
        daylabel = []

        def monthlabelextractor(month, year):
            yeari = str(year)[2:]

            def switch_month(argument):
                switcher = {
                    1: "Jan",
                    2: "Feb",
                    3: "Mar",
                    4: "Apr",
                    5: "May",
                    6: "Jun",
                    7: "Jul",
                    8: "Aug",
                    9: "Sep",
                    10: "Oct",
                    11: "Nov",
                    12: "Dec"
                }
                return switcher.get(argument, "Invalid month")

            monthi = switch_month(month)
            return monthi + ' ' + yeari

        curmonth = datetime.now().month
        curyear = datetime.now().year
        curweek = datetime.now().isocalendar()[1]
        curdate = datetime.now().day
        for i in range(0, 12):
            if curmonth - i <= 0:
                curyeari = curyear - 1
                curmonthi = curmonth - i + 12
            else:
                curyeari = curyear
                curmonthi = curmonth - i
            monthlabel.append(monthlabelextractor(curmonthi, curyeari))
        monthlabel.reverse()
        for i in range(0, 12):
            weeklabel.append('Week ' + str(curweek-i))
        weeklabel.reverse()
        def switch_month(argument):
            switcher = {
                1: "Jan",
                2: "Feb",
                3: "Mar",
                4: "Apr",
                5: "May",
                6: "Jun",
                7: "Jul",
                8: "Aug",
                9: "Sep",
                10: "Oct",
                11: "Nov",
                12: "Dec"
            }
            return switcher.get(argument, "Invalid month")

        for i in range(0, 12):
            daten = datetime.now() - timedelta(days=i)
            daylabel.append(str(daten.day) + ' ' + switch_month(daten.month))
        daylabel.reverse()
        totalearn = 0
        try:
            earningmonth = Payment.objects.filter(ebook__publisher=publisher)
            for item in earningmonth:
                totalearn = totalearn + item.amount
            earningmonthbuyq = earningmonth.filter(duration='Buy')
            earningmonthrentq = earningmonth.exclude(duration='Buy')
            earningmonthbuy = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            earningmonthrent = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            earningweekbuy = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            earningweekrent = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            earningdaybuy = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            earningdayrent = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            tearnm = 0
            tearnw = 0
            tearnd = 0
            tearny = 0
            tearnmp = 0
            tearnwp = 0
            tearndp = 0
            tearnyp = 0
            for item in earningmonth:
                if item.time.year == curyear:
                    tearny = tearny + item.amount
                    if item.time.month == curmonth:
                        tearnm = tearnm + item.amount
                        if item.time.isocalendar()[1] == curweek:
                            tearnw = tearnw + item.amount
                            if item.time.day == curdate:
                                tearnd = tearnd + item.amount
                            elif item.time.day == curdate -1:
                                tearndp = tearndp + item.amount
                        elif item.time.isocalendar()[1] == curweek - 1:
                            tearnwp = tearnwp + item.amount
                    elif item.time.month == curmonth - 1:
                        tearnmp = tearnmp + item.amount
                elif item.time.year == curyear - 1:
                    tearnyp = tearnyp + item.amount
                    if item.time.month == 12 and curmonth == 1:
                        tearnmp = tearnmp + item.amount
                        if curweek == 1 and (item.time.isocalendar()[1] == 52 or item.time.isocalendar()[1] == 53):
                            tearnwp = tearnwp + item.amount
                            if curdate == 1 and item.time.day == 31:
                                tearndp = tearndp + item.amount
            if tearnmp != 0 :
                tearnmi = str(((tearnm - tearnmp)/tearnmp)*100) + '%'
            else:
                tearnmi = str(tearnm - tearnmp)
            if tearnwp != 0:
                tearnwi = str(((tearnw - tearnwp) / tearnwp) * 100) + '%'
            else:
                tearnwi = str(tearnw - tearnwp)
            if tearndp != 0:
                tearndi = str(((tearnd - tearndp) / tearndp) * 100) + '%'
            else:
                tearndi = str(tearnd - tearndp)
            if tearnyp != 0:
                tearnyi = str(((tearny - tearnyp) / tearnyp) * 100) + '%'
            else:
                tearnyi = str(tearny - tearnyp)
            for item in earningmonthbuyq:
                diffmonth = (curyear - item.time.year)*12 + (curmonth-item.time.month)
                if diffmonth == 11:
                    earningmonthbuy[0] = item.amount
                elif diffmonth == 10:
                    earningmonthbuy[1] = item.amount
                elif diffmonth == 9:
                    earningmonthbuy[2] = item.amount
                elif diffmonth == 8:
                    earningmonthbuy[3] = item.amount
                elif diffmonth == 7:
                    earningmonthbuy[4] = item.amount
                elif diffmonth == 6:
                    earningmonthbuy[5] = item.amount
                elif diffmonth == 5:
                    earningmonthbuy[6] = item.amount
                elif diffmonth == 4:
                    earningmonthbuy[7] = item.amount
                elif diffmonth == 3:
                    earningmonthbuy[8] = item.amount
                elif diffmonth == 2:
                    earningmonthbuy[9] = item.amount
                elif diffmonth == 1:
                    earningmonthbuy[10] = item.amount
                elif diffmonth == 0:
                    earningmonthbuy[11] = item.amount
            for item in earningmonthrentq:
                diffmonth = (curyear - item.time.year) * 12 + (curmonth - item.time.month)
                if diffmonth == 11:
                    earningmonthrent[0] = item.amount
                elif diffmonth == 10:
                    earningmonthrent[1] = item.amount
                elif diffmonth == 9:
                    earningmonthrent[2] = item.amount
                elif diffmonth == 8:
                    earningmonthrent[3] = item.amount
                elif diffmonth == 7:
                    earningmonthrent[4] = item.amount
                elif diffmonth == 6:
                    earningmonthrent[5] = item.amount
                elif diffmonth == 5:
                    earningmonthrent[6] = item.amount
                elif diffmonth == 4:
                    earningmonthrent[7] = item.amount
                elif diffmonth == 3:
                    earningmonthrent[8] = item.amount
                elif diffmonth == 2:
                    earningmonthrent[9] = item.amount
                elif diffmonth == 1:
                    earningmonthrent[10] = item.amount
                elif diffmonth == 0:
                    earningmonthrent[11] = item.amount
            for item in earningmonthbuyq:
                diffweek = datetime.now().isocalendar()[1] - item.time.isocalendar()[1]
                if diffweek == 11:
                    earningweekbuy[0] = item.amount
                elif diffweek == 10:
                    earningweekbuy[1] = item.amount
                elif diffweek == 9:
                    earningweekbuy[2] = item.amount
                elif diffweek == 8:
                    earningweekbuy[3] = item.amount
                elif diffweek == 7:
                    earningweekbuy[4] = item.amount
                elif diffweek == 6:
                    earningweekbuy[5] = item.amount
                elif diffweek == 5:
                    earningweekbuy[6] = item.amount
                elif diffweek == 4:
                    earningweekbuy[7] = item.amount
                elif diffweek == 3:
                    earningweekbuy[8] = item.amount
                elif diffweek == 2:
                    earningweekbuy[9] = item.amount
                elif diffweek == 1:
                    earningweekbuy[10] = item.amount
                elif diffweek == 0:
                    earningweekbuy[11] = item.amount
            for item in earningmonthrentq:
                diffweek = datetime.now().isocalendar()[1] - item.time.isocalendar()[1]
                if diffweek == 11:
                    earningweekrent[0] = item.amount
                elif diffweek == 10:
                    earningweekrent[1] = item.amount
                elif diffweek == 9:
                    earningweekrent[2] = item.amount
                elif diffweek == 8:
                    earningweekrent[3] = item.amount
                elif diffweek == 7:
                    earningweekrent[4] = item.amount
                elif diffweek == 6:
                    earningweekrent[5] = item.amount
                elif diffweek == 5:
                    earningweekrent[6] = item.amount
                elif diffweek == 4:
                    earningweekrent[7] = item.amount
                elif diffweek == 3:
                    earningweekrent[8] = item.amount
                elif diffweek == 2:
                    earningweekrent[9] = item.amount
                elif diffweek == 1:
                    earningweekrent[10] = item.amount
                elif diffweek == 0:
                    earningweekrent[11] = item.amount
            for item in earningmonthbuyq:
                diffday = datetime.now().day - item.time.day
                if diffday == 11:
                    earningdaybuy[0] = item.amount
                elif diffday == 10:
                    earningdaybuy[1] = item.amount
                elif diffday == 9:
                    earningdaybuy[2] = item.amount
                elif diffday == 8:
                    earningdaybuy[3] = item.amount
                elif diffday == 7:
                    earningdaybuy[4] = item.amount
                elif diffday == 6:
                    earningdaybuy[5] = item.amount
                elif diffday == 5:
                    earningdaybuy[6] = item.amount
                elif diffday == 4:
                    earningdaybuy[7] = item.amount
                elif diffday == 3:
                    earningdaybuy[8] = item.amount
                elif diffday == 2:
                    earningdaybuy[9] = item.amount
                elif diffday == 1:
                    earningdaybuy[10] = item.amount
                elif diffday == 0:
                    earningdaybuy[11] = item.amount
            for item in earningmonthrentq:
                diffday = datetime.now().day - item.time.day
                if diffday == 11:
                    earningdayrent[0] = item.amount
                elif diffday == 10:
                    earningdayrent[1] = item.amount
                elif diffday == 9:
                    earningdayrent[2] = item.amount
                elif diffday == 8:
                    earningdayrent[3] = item.amount
                elif diffday == 7:
                    earningdayrent[4] = item.amount
                elif diffday == 6:
                    earningdayrent[5] = item.amount
                elif diffday == 5:
                    earningdayrent[6] = item.amount
                elif diffday == 4:
                    earningdayrent[7] = item.amount
                elif diffday == 3:
                    earningdayrent[8] = item.amount
                elif diffday == 2:
                    earningdayrent[9] = item.amount
                elif diffday == 1:
                    earningdayrent[10] = item.amount
                elif diffday == 0:
                    earningdayrent[11] = item.amount
        except Exception as e:
            earningmonthbuy = [0,0,0,0,0,0,0,0,0,0,0,0]
            earningmonthrent = [0,0,0,0,0,0,0,0,0,0,0,0]
            earningweekbuy = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            earningweekrent = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            earningdaybuy = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            earningdayrent = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
            tearnm = 0
            tearnw = 0
            tearnd = 0
            tearny = 0
            tearnmi = str(0) + '%'
            tearnwi = str(0) + '%'
            tearndi = str(0) + '%'
            tearnyi = str(0) + '%'
        pubpaym = []
        pubpayw = []
        pubpayd = []
        pubpayy = []
        totalpayment = 0
        try:
            pubpay = Publisherpayment.objects.filter(publisher=publisher).order_by('-id')
            for item in pubpay:
                totalpayment = totalpayment + item.amount
                if item.time.year == curyear:
                    pubpayy.append([item.time,item.amount])
                    if item.time.month == curmonth:
                        pubpaym.append([item.time,item.amount])
                        if item.time.isocalendar()[1] == curweek:
                            pubpayw.append([item.time,item.amount])
                            if item.time.day == curdate:
                                pubpayd.append([item.time,item.amount])
            pubpayy = pubpayy[0:4]
            pubpaym = pubpaym[0:4]
            pubpayw = pubpayw[0:4]
            pubpayd = pubpayd[0:4]
        except Exception as e:
            pass
        totalremain = totalearn - totalpayment
        totalremain = "{0:.2f}".format(totalremain)

        try:
            pbooks = Ebooks.objects.filter(publisher=publisher)
            pbookarr = []
            pbooknamearr = []
            payment = Payment.objects.filter(ebook__publisher=publisher)
            for book in pbooks:
                tb = payment.filter(ebook=book,duration='Buy').count()
                tr = payment.filter(ebook=book).exclude(duration='Buy').count()
                te = 0
                for item in payment.filter(ebook=book):
                    te = te + item.amount
                pbookarr.append([book.img,book.name,tb,tr,te])
                pbooknamearr.append(book.name)
            pbookarr = sorted(pbookarr,key=lambda x: float(x[4]),reverse=True)
        except Exception as e:
            pbookarr = []
            pbooknamearr = []

        return render(request,'rapp/publisher.html',{'allow':allow,'publisherName':publisherName,'numBooks':numBooks,'earningmonthbuy':earningmonthbuy,'earningmonthrent':earningmonthrent,'monthlabel':monthlabel,'earningweekbuy':earningweekbuy,'earningweekrent':earningweekrent,'weeklabel':weeklabel,'earningdaybuy':earningdaybuy,'earningdayrent':earningdayrent,'daylabel':daylabel,
                                                     'tearnm':tearnm,'tearnw':tearnw,'tearnd':tearnd,'tearny':tearny,'tearnmi':tearnmi,'tearnwi':tearnwi,'tearndi':tearndi,'tearnyi':tearnyi,'pubpayy':pubpayy,'pubpaym':pubpaym,'pubpayw':pubpayw,'pubpayd':pubpayd,'totalremain':totalremain,'pbookarr':pbookarr,'pbooknamearr':pbooknamearr})
    else:
        allow = False
        return render(request,'rapp/publisher.html',{'allow':allow})


def secure(request):
    user = request.user
    if Uploadadmin.objects.filter(user=user).exists():
        usercheck = True
    else:
        usercheck = False
    if request.method == 'POST':
        name = request.POST['name']
        author = request.POST['author']
        try:
          publisher = request.POST['publisher']
        except Exception as e:
            publisher = 'None'
        publishdate = request.POST['publishdate']
        isbn = request.POST['isbn']
        price = request.POST['price']
        pages = request.POST['pages']
        category = request.POST['category']
        ebookfile = request.FILES['ebookfile']
        image = request.FILES['image']
        language = request.POST['language']
        description = request.POST['description']
        tags = request.POST.getlist('tags[]')
        priority = request.POST['priority']

        AWS_ACCESS_KEY_ID = 'AKIAI3WSXTMIMMG6VWWA'
        AWS_SECRET_ACCESS_KEY = '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'

        END_POINT = 'ap-south-1'  # eg. us-east-1
        S3_HOST = 's3.ap-south-1.amazonaws.com'  # eg. s3.us-east-1.amazonaws.com
        BUCKET_NAME = 'readerearth'
        imagename = image.name
        extension1 = imagename[imagename.rfind('.'):]
        if len(extension1) <=1:
            extension1 = None
        filename = ebookfile.name
        extension2 = filename[filename.rfind('.'):]
        if len(extension2) <= 1:
            extension2 = None
        imagekey = Keyvalue.objects.filter(key='image')[0]
        imkey = imagekey.value
        imagekey.value = imagekey.value + 1
        imagekey.save()
        if extension1 != None:
            UPLOADED_FILENAME = 'media/bookimages/' + str(imkey) + extension1
            imageurl = UPLOADED_FILENAME
        else:
            UPLOADED_FILENAME = 'media/bookimages/' + str(imkey)
            imageurl = UPLOADED_FILENAME
        ebookkey = Keyvalue.objects.filter(key='ebook')[0]
        ekey = ebookkey.value
        ebookkey.value = ebookkey.value + 1
        ebookkey.save()
        if extension2 != None:
            UPLOADED_FILENAME2 = 'media/epubs/' + str(ekey) + extension2
            eurl = UPLOADED_FILENAME2
        else:
            UPLOADED_FILENAME2 = 'media/epubs/' + str(ekey)
            eurl = UPLOADED_FILENAME2
        # include folders in file path. If it doesn't exist, it will be created

        s3 = boto.s3.connect_to_region(END_POINT,
                                       aws_access_key_id=AWS_ACCESS_KEY_ID,
                                       aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                                       host=S3_HOST)

        bucket = s3.get_bucket(BUCKET_NAME)
        k = Key(bucket)
        k.key = UPLOADED_FILENAME
        k.set_contents_from_file(image)
        k = Key(bucket)
        k.key = UPLOADED_FILENAME2
        k.set_contents_from_file(ebookfile)

        cat = Category.objects.filter(cat=category)[0]
        catmodel = cat.catmodel
        if catmodel == '3month':
            dayopt = '3 days,7 days,14 days,21 days,1 month,1.5 months,2 months,3 months'
        else:
            dayopt = '3 days,7 days,14 days,21 days,1 month,1.5 months,2 months,3 months,4 months,5 months,6 months,12 months'

        authorf = Authors.objects.filter(name=author)[0]
        publisherf = Publishers.objects.filter(name=publisher)[0]
        if publishdate == '':
            publishdate = None
        if publisher != '' and description != '<p><br></p>':
            ebook = Ebooks.objects.create(name=name,author=authorf,publisher=publisherf,publishdate=publishdate,price=price,pages=pages,content=eurl,category=cat,
                                  img=imageurl,dayopt=dayopt,language=language,description=description,priority=priority,isbn=isbn)
        elif publisher == '' and description == '<p><br></p>':
            ebook = Ebooks.objects.create(name=name, author=authorf, publishdate=publishdate, price=price,pages=pages, content=eurl, category=cat,
                                  img=imageurl, dayopt=dayopt, language=language,priority=priority, isbn=isbn)
        else:
            if publisher == '':
                ebook = Ebooks.objects.create(name=name, author=authorf, publishdate=publishdate,
                                      price=price, pages=pages, content=eurl, category=cat,
                                      img=imageurl, dayopt=dayopt, language=language, description=description,
                                      priority=priority, isbn=isbn)
            else:
                ebook = Ebooks.objects.create(name=name, author=authorf, publisher=publisherf, publishdate=publishdate,
                                      price=price, pages=pages, content=eurl, category=cat,
                                      img=imageurl, dayopt=dayopt, language=language,
                                      priority=priority, isbn=isbn)
        if len(tags) > 0:
            for tag in tags:
                tagf = Tag.objects.filter(name=tag)[0]
                ebook.tags.add(tagf)
        ebook.save()
    publishers = Publishers.objects.all()
    cats = Category.objects.all()
    tags = Tag.objects.all()
    authors = Authors.objects.all()

    return render(request,'rapp/secure.html',{'usercheck':usercheck,'publishers':publishers,'cats':cats,'tags':tags,'authors':authors})


def bookrequest(request):
    if request.method == 'POST':
        message = request.POST['bookname']
        email = request.POST['email']
        html_content = '<br>Email: ' + email + '<br>Book Name: ' + message
        msg = EmailMultiAlternatives(
            'Book Request - Reader Earth',
            'Details:',
            to=['contact@readerearth.com',]
        )
        msg.attach_alternative(html_content,"text/html")
        msg.send()

        return HttpResponse('You request has been received! We will soon Notify you with the Arrival of E-book!')


def feedback(request):
    if request.method == 'POST':
        message = request.POST['message']
        email = request.POST['email']
        html_content = '<br>Email: ' + email + '<br>Feedback/Comments: ' + message
        msg = EmailMultiAlternatives(
            'Feedback/Comments - Reader Earth',
            'Details:',
            to=['contact@readerearth.com',]
        )
        msg.attach_alternative(html_content,"text/html")
        msg.send()

        return HttpResponse('Thanks for Your Worthy Feedback/Comments! We would love to hear more from you!')


def allower(request):
    if request.method == 'POST':
        email = request.POST['email']
        publisher = request.POST['publisher']
        username = request.POST['publisher']
        password = User.objects.make_random_password()
        if email!='' and username!='':
            if len(User.objects.filter(email=email)) == 0:
                user = User.objects.create_user(username,email,password)
                user.is_active = False
                user.save()
                pub = Publishers.objects.create(name=publisher)
                userp = UserP.objects.create(user=user, pub=False, publisher=pub)
                text_content = "Publisher Account Activation Email"
                subject = "Readerearth Account Activation"
                template_name = "rapp/pub_active_email.html"
                from_email = 'contact@readerearth.com'
                recipients = [email,]
                activate_url = 'https://www.readerearth.com/pubactivate/'+email+'/'+password+'/'
                context = {
                    'user': user,
                    'activate_url': activate_url
                }
                html_content = render_to_string(template_name,context)
                email = EmailMultiAlternatives(subject, text_content, from_email, recipients)
                email.attach_alternative(html_content, "text/html")
                email.send()
                return HttpResponse('Mail Sent!')
            else:
                return HttpResponse('This Email id has already been taken!')
    else:
        if request.user.is_authenticated:
            admin = Adminacc.objects.filter(user=request.user)
            if len(admin) > 0:
                admin = admin[0]
                allow = True
            else:
                allow = False
        else:
            allow = False
        return render(request, 'rapp/allower.html', {'allow':allow})


def pubactivate(request,email='',password=''):
    if request.method == 'POST':
        benname = request.POST['benname']
        account = request.POST['account']
        ifsc = request.POST['ifsc']
        number = request.POST['number']
        passer = request.POST['pass']
        email = request.POST['email']
        user = User.objects.filter(email=email)[0]
        user.set_password(passer)
        user.is_active = True
        user.save()
        userp = UserP.objects.filter(user=user)[0]
        userp.pub = True
        userp.benname = benname
        userp.account = account
        userp.ifsc = ifsc
        userp.number = number
        userp.save()
        return HttpResponse('Success')
    else:
        user = User.objects.filter(email=email)
        if user.exists():
            user = user[0]
            if user.check_password(password) == True:
                if user.is_active == False:
                    allow = True
                else:
                    allow = False
            else:
                allow = False
        else:
            allow = False
        return render(request,'rapp/pubactivate.html',{'allow':allow})


def googlesignin(request):
    if request.method == 'POST':
        token = request.POST['id_token']
        try:
            idinfo = id_token.verify_oauth2_token(token, requests.Request(), '18205974359-scm2ogghtt91dkgfb9id3lpprfnvd3f4.apps.googleusercontent.com')

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            email = idinfo['email']
            name = idinfo['name']
            user = User.objects.filter(email=email)
            if user.exists():
                user = user[0]
                login(request,user)
                return HttpResponse('Success')

            else:
                password = User.objects.make_random_password()
                user = User.objects.create_user(name,email,password)
                Gmailid.objects.create(user=user)
                login(request,user)
                return HttpResponse('Success')
        except ValueError:
            pass


def addbookmark(request):
    if request.method == 'POST':
        ebookid = request.POST['ebookid']
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        bookloc = request.POST['bookloc']
        data = request.POST['data']
        if Bookmark.objects.filter(user=request.user,ebook=ebook,location=bookloc).exists():
            Bookmark.objects.filter(user=request.user, ebook=ebook, location=bookloc).delete()
            return HttpResponse('Deleted')
        else:
            Bookmark.objects.create(user=request.user,ebook=ebook,location = bookloc,data=data)
            return HttpResponse('Added')


def addmusiclis(request):
    if request.method == 'POST':
        musicid = request.POST['musicid']
        music = Music.objects.filter(id=musicid)[0]
        Musiclis.objects.create(music=music,user=request.user)

        return HttpResponse('Success')


def removequeue(request):
    if request.method == 'POST':
        queueid = request.POST['queueid']
        music = Music.objects.filter(id=queueid)
        musiclis = Musiclis.objects.filter(music=music,user=request.user)
        for lis in musiclis:
            lis.queue = False
            lis.save()

        return HttpResponse('Success')


def removeplaylist(request):
    if request.method == 'POST':
        playlistid = int(request.POST['playlistid'])
        musicid = int(request.POST['musicid'])
        playlist = Playlist.objects.filter(id=playlistid,user=request.user)[0]
        for mus in playlist.music.all():
            if mus.id == musicid:
                playlist.music.remove(mus)
        playlist.save()

        return HttpResponse('Success')


def addplaylist(request):
    if request.method == 'POST':
        musicid = int(request.POST['musicid'])
        playlistname = request.POST['playlist']
        playlistid = int(request.POST['playlistid'])
        addi = int(request.POST['add'])
        music = Music.objects.filter(id=musicid)[0]
        if addi == 0:
            playlist = Playlist.objects.filter(id=playlistid, user=request.user)[0]
            playlist.music.add(music)
            playlist.save()
            playlistide = playlistid
        elif addi == 1:
            list = Playlist.objects.create(name=playlistname,user=request.user)
            list.music.add(music)
            list.save()
            playlistide = list.id

        return HttpResponse(playlistide)


def addhighlight(request):
    if request.method == 'POST':
        cfirange = request.POST['cfirange']
        ebookid = request.POST['ebookid']
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        colora = request.POST['colora']
        selected = request.POST['selected']
        Highlight.objects.create(cfirange=cfirange,user=request.user,ebook=ebook,color=colora,note=False,selectedtext=selected)

        return HttpResponse('success')


def removehighlight(request):
    if request.method == 'POST':
        cfirange = request.POST['cfirange']
        ebookid = request.POST['ebookid']
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        Highlight.objects.filter(cfirange=cfirange,user=request.user,ebook=ebook)[0].delete()

        return HttpResponse('success')


def changehighlight(request):
    if request.method == 'POST':
        cfirange = request.POST['cfirange']
        ebookid = request.POST['ebookid']
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        colora = request.POST['color']
        notenote = int(request.POST['notenote'])
        notetext = request.POST['notetext']
        selected = request.POST['selected']
        if notenote == 0:
            if Highlight.objects.filter(cfirange=cfirange, user=request.user, ebook=ebook).exists():
                high = Highlight.objects.filter(cfirange=cfirange, user=request.user, ebook=ebook)[0]
                high.color = colora
                high.note = False
                high.save()
            else:
                Highlight.objects.create(cfirange=cfirange,user=request.user,ebook=ebook,color=colora,note=False,selectedtext=selected)
        elif notenote == 1:
            if Highlight.objects.filter(cfirange=cfirange, user=request.user, ebook=ebook).exists():
                high = Highlight.objects.filter(cfirange=cfirange, user=request.user, ebook=ebook)[0]
                high.color = colora
                high.note = True
                high.text = notetext
                high.save()
            else:
                Highlight.objects.create(cfirange=cfirange, user=request.user, ebook=ebook, color=colora, note=True,text=notetext,selectedtext=selected)

        return HttpResponse('success')



def getdict(request):
    if request.method == 'POST':
        word = request.POST['word']
        if word[-1] == '.' or word[-1] == "'" or word[-1] == " ":
            word = word[0:len(word)-1]
        lang = request.POST['lang']
        if lang == 'English':
            langs = 'en'
        elif lang == 'Hindi':
            langs = 'hi'
        app_id = 'c0ce2857'
        app_key = '94c05bd02a17260ce98991443aec78d4'
        language = langs
        word_id = word
        url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word_id.lower()
        r = req.get(url, headers={'app_id': app_id, 'app_key': app_key})

        if r.status_code == 404 and (word[-1] == 's' or word[-1] == 'd'):
            word = word[0:len(word)-1]
            word_id = word
            url = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word_id.lower()
            r = req.get(url, headers={'app_id': app_id, 'app_key': app_key})
        if r.status_code == 200:
          try:
            list1 = r.json()
            url2 = 'https://od-api.oxforddictionaries.com:443/api/v1/entries/' + language + '/' + word_id.lower() + '/synonyms'
            r2 = req.get(url2, headers={'app_id': app_id, 'app_key': app_key})
            phoneticlist = []
            categorylist = []
            definelist = []
            for item in list1['results'][0]['lexicalEntries']:
                try:
                    phoneticlist.append(item['pronunciations'][0]['phoneticSpelling'])
                except KeyError:
                    phoneticlist.append('')
                categorylist.append(item['lexicalCategory'])
                temparray = []
                if item['lexicalCategory'] == 'Other':
                    for jk in item['entries'][0]['senses']:
                        temparray.append(jk['crossReferenceMarkers'][0])
                    definelist.append(temparray)
                else:
                    for jk in item['entries'][0]['senses']:
                        try:
                            temparray.append(jk['definitions'][0])
                        except KeyError:
                            try:
                                temparray.append(jk['subsenses'][0]['definitions'][0])
                            except KeyError:
                                temparray.append(jk['crossReferenceMarkers'][0])
                    definelist.append(temparray)
            syarray = []
            for cat in categorylist:
                syarray.append([])
            if r2.status_code != 404:
                list2 = r2.json()
                n = 0
                for item in list2['results'][0]['lexicalEntries']:
                    if item['lexicalCategory'] in categorylist:
                        index = categorylist.index(item['lexicalCategory'])
                        tre2array = []
                        for hj in item['entries'][0]['senses']:
                            tre1array = []
                            for kl in hj['synonyms']:
                                tre1array.append(kl['text'])
                            tre2array.append(tre1array)
                        syarray[index] = tre2array
                    n = n + 1
          except JSONDecodeError:
              phoneticlist = []
              categorylist = []
              definelist = []
              syarray = []
        else:
            phoneticlist = []
            categorylist = []
            definelist = []
            syarray = []
        return HttpResponse(json.dumps({"phoneticlist": phoneticlist, "categorylist": categorylist,"definelist":definelist,"syarray":syarray}),
                            content_type="application/json")


def addnotefile(request):
    if request.method == 'POST':
        ebookid = request.POST['ebookid']
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        notefilename = request.POST['notefilename']
        notearr = request.POST.getlist('notearr[]')
        textarr = request.POST.getlist('textarr[]')
        if not Notefile.objects.filter(name=notefilename,user=request.user,ebook=ebook).exists():
            file = Notefile.objects.create(name=notefilename,user=request.user,ebook=ebook)
            for i in range(len(notearr)):
                Notefileitem.objects.create(notefile=file,note=notearr[i],text=textarr[i])
            return HttpResponse('success')
        else:
            return HttpResponse('Exists')


def addauthor(request):
    if request.method == 'POST':
        authorname = request.POST['authorname']
        Authors.objects.create(name=authorname)

        return HttpResponse('success')


def addpublisher(request):
    if request.method == 'POST':
        publishername = request.POST['publishername']
        Publishers.objects.create(name=publishername)

        return HttpResponse('success')


def addtag(request):
    if request.method == 'POST':
        tagname = request.POST['tagname']
        Tag.objects.create(name=tagname)

        return HttpResponse('success')


def addcategory(request):
    if request.method == 'POST':
        categoryname = request.POST['categoryname']
        categorymodel = request.POST['categorymodel']
        Category.objects.create(cat=categoryname,catmodel=categorymodel)

        return HttpResponse('success')


def adddurationview(request):
    if request.method == 'POST':
        view = request.POST['view']
        try:
            ebookid = int(request.POST['ebookid'])
            ebook = Ebooks.objects.filter(id=ebookid)[0]
        except Exception as e:
            pass
        duration = int(request.POST['duration'])
        try:
            genre = request.POST['genre']
            genrer = Category.objects.filter(cat=genre)[0]
        except Exception as e:
            pass
        if view == 'detail':
            dv = Detailview.objects.filter(ebook=ebook,user=request.user).latest('id')
            dv.duration = duration
            dv.save()
        elif view == 'read':
            dv = Readview.objects.filter(ebook=ebook, user=request.user).latest('id')
            dv.duration = duration
            dv.save()
        elif view == 'sample':
            dv = Sampleview.objects.filter(ebook=ebook, user=request.user).latest('id')
            dv.duration = duration
            dv.save()
        elif view == 'cat':
            dv = Genreview.objects.filter(genre=genrer, user=request.user).latest('id')
            dv.duration = duration
            dv.save()
        elif view == 'nr':
            dv = Newreleaseview.objects.filter(user=request.user).latest('id')
            dv.duration = duration
            dv.save()
        elif view == 'bs':
            dv = Bestsellerview.objects.filter(user=request.user).latest('id')
            dv.duration = duration
            dv.save()

        return HttpResponse('success')


def addrating(request):
    if request.method == 'POST':
        ebookid = int(request.POST['ebookid'])
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        rating = int(request.POST['rating'])
        if request.user.is_authenticated:
            if Rateduser.objects.filter(user=request.user,ebook=ebook).exists():
                rateuser = Rateduser.objects.filter(user=request.user,ebook=ebook)[0]
                prevrating = rateuser.rating
                rateuser.rating = rating
                rateuser.save()
                ebook.rating = (ebook.rating*ebook.ratedusers - prevrating + rating)/ebook.ratedusers
                atrating = ebook.rating
                ebook.save()
                return HttpResponse(json.dumps({'age':'old', 'rating':atrating}), content_type="application/json")
            else:
                Rateduser.objects.create(user=request.user,ebook=ebook,rating=rating)
                ebook.rating = ((ebook.rating*ebook.ratedusers) + rating)/(ebook.ratedusers+1)
                atrating = ebook.rating
                ebook.ratedusers = ebook.ratedusers + 1
                atusers = ebook.ratedusers
                ebook.save()
                return HttpResponse(json.dumps({'age':'new','rating':atrating,'users':atusers}), content_type="application/json")
        else:
            return HttpResponse('Please login to Rate the Book')


def save_percent(request):
    if request.method == 'POST':
        ebookid = int(request.POST['ebookid'])
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        loccur1 = int(request.POST['loccur1'])
        loccur2 = int(request.POST['loccur2'])
        loctotal = int(request.POST['loctotal'])
        if request.user.is_authenticated:
            if Percentageread.objects.filter(user=request.user,ebook=ebook).exists():
                last = Percentageread.objects.filter(user=request.user,ebook=ebook)[0]
                for i in range(loccur2-loccur1+1):
                    if i+loccur1 == loccur1:
                        phase = 'left'
                        eff = (0.5/loctotal)*100
                    elif i+loccur1 == loccur2:
                        phase = 'right'
                        eff = (0.5/loctotal)*100
                    else:
                        phase = 'full'
                        eff = (1.0/loctotal)*100
                    if not Readlocation.objects.filter(readmodel=last,location=i+loccur1,phase=phase).exists():
                        Readlocation.objects.create(readmodel=last, location=i+loccur1, phase=phase)
                        last.percent = last.percent + eff
                        last.save()
            else:
                readmodel = Percentageread.objects.create(user=request.user,ebook=ebook)
                readmodel.percent = 0
                for i in range(loccur2-loccur1+1):
                    if i+loccur1 == loccur1:
                        phase = 'left'
                        eff = (0.5/loctotal)*100
                    elif i+loccur1 == loccur2:
                        phase = 'right'
                        eff = (0.5/loctotal)*100
                    else:
                        phase = 'full'
                        eff = (1.0/loctotal)*100
                    Readlocation.objects.create(readmodel=readmodel,location=i+loccur1,phase=phase)
                    readmodel.percent = readmodel.percent + eff
                    readmodel.save()
        return HttpResponse('Success')


def remove_notefile(request):
    if request.method == 'POST':
        filename = request.POST['filename']
        ebookid = int(request.POST['ebookid'])
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        file = Notefile.objects.filter(name=filename,user=request.user,ebook=ebook)[0]
        Notefileitem.objects.filter(notefile=file).delete()
        file.delete()

        return HttpResponse('Success')


def updateconn(request):
    if request.method == 'POST':
        publicip = request.POST['publicip']
        localip = request.POST['localip']
        status = request.POST['status']
        if ConnectionHistory.objects.filter(user=request.user,publicip=publicip,localip=localip).exists():
            conn = ConnectionHistory.objects.filter(user=request.user,publicip=publicip,localip=localip)[0]
            if status == 'online':
                conn.status = conn.status + 1
            elif status == 'offline':
                conn.status = conn.status - 1
            conn.save()
        else:
            ConnectionHistory.objects.create(user=request.user,publicip=publicip,localip=localip,status=1)
        return HttpResponse('Success')


def catchpayment(request):
    if request.method == 'POST':
        paymentid = request.POST['paymentid']
        amount = request.POST['amount']
        amounti = int(amount)/100
        public_key = 'rzp_test_R9MS4y8dG93IWT'
        secret_key = '9YH80tzm0ilqe0LjRuDd0igs'
        client = razorpay.Client(auth=(public_key, secret_key))
        client.payment.capture(paymentid, amount)

        return HttpResponse('Success')


def paypalcreate(request):
    if request.method == 'POST':
        paypalrestsdk.configure({
            "mode": "sandbox",  # sandbox or live
            "client_id": "AYhLyZ9jvCZ7pJaH4C1C0izZXZhui1950yQVUZC0sNnfts4eqM-DQrdJZE5DzvOQhKUO9B3RUlfCXySt",
            "client_secret": "ED3WFoaIvxtc45xDUA0igyp09zH6rtB0vNVROslsW1FIQpGk63O4Uaq3unH7IfS-7hUNFusfCDgnXvDh"})

        payment = paypalrestsdk.Payment({
            "intent": "sale",
            "payer": {
                "payment_method": "paypal"},
            "redirect_urls": {
                "return_url": "http://localhost:8000/payment",
                "cancel_url": "http://localhost:8000/"},
            "transactions": [{
                "item_list": {
                    "items": [{
                        "name": "item",
                        "sku": "item",
                        "price": "5.00",
                        "currency": "USD",
                        "quantity": 1}]},
                "amount": {
                    "total": "5.00",
                    "currency": "USD"},
                "description": "This is the payment transaction description."}]})

        if payment.create():
            return HttpResponse(json.dumps({"id": payment.id}), content_type="application/json")
        else:
            return HttpResponse(payment.error)


def paypalexecute(request):
    if request.method == 'POST':
        print('hiiii')
        paymentID = request.POST['paymentID']
        payerID = request.POST['payerID']
        payment = paypalrestsdk.Payment.find(paymentID)
        if payment.execute({"payer_id": payerID}):
            return HttpResponse('Success')
        else:
            return HttpResponse(payment.error)