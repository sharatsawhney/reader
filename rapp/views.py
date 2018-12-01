from django.shortcuts import render, redirect,resolve_url,render_to_response
from easy_pdf.views import PDFTemplateView
from django.conf import settings
from rapp.forms import UserForm,UploadForm,PriceRangeSearchForm
from django.contrib.auth import authenticate, login,logout
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from rapp.models import Authors,Publishers,Category,Ebooks,Subscribers,Usercart,Wishlist,Transactions,Dashboard,Notes,Lastpage,Uploaded,UserP,Adminacc,Gmailid,Bookmark,Tag,Musicgenre,Musictag,Music,Musiclis,Playlist,Highlight,Notefile,Notefileitem,Uploadadmin,Keyvalue
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
from datetime import datetime, timezone
from haystack.generic_views import SearchView
from haystack.forms import FacetedSearchForm
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from haystack.query import SearchQuerySet
from haystack.inputs import AutoQuery, Exact, Clean
from google.oauth2 import id_token
from google.auth.transport import requests
import boto.s3
from boto.s3.key import Key


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



    return render(request,'rapp/contact.html', {})


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
    try:
        Wishlist.objects.filter(user=request.user,ebook=ebook)[0]
        heart = True
    except:
        heart = False

    return render(request,'rapp/detail.html',{'ebook':ebook,'heart':heart})


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
        oprice = ebook.price
        if ebook.category.cat == ('Engineering' or 'Medical'):
            def getprice(argument):
                switcher = {
                    '3 days': 0.05*oprice,
                    '7 days': 0.08*oprice,
                    '14 days': 0.13*oprice,
                    '21 days': 0.17*oprice,
                    '1 month': 0.20*oprice,
                    '1.5 months': 0.26*oprice,
                    '2 months': 0.30*oprice,
                    '3 months': 0.35*oprice,
                    '4 months': 0.40*oprice,
                    '5 months': 0.45*oprice,
                    '6 months': 0.50*oprice,
                    '12 months': 0.65*oprice
                }
                return switcher.get(argument,"nothing")
            price = getprice('1 month')
        else:
            def getprice(argument):
                switcher = {
                    '3 days': 0.08*oprice,
                    '7 days': 0.15*oprice,
                    '14 days': 0.25*oprice,
                    '21 days': 0.32*oprice,
                    '1 month': 0.40*oprice,
                    '1.5 months': 0.50*oprice,
                    '2 months': 0.60*oprice
                }
                return switcher.get(argument,"nothing")
            price = getprice('1 month')
        check = Usercart.objects.filter(user=request.user,ebook=ebook)
        if check.count() == 0:
            usercart = Usercart.objects.get_or_create(user=request.user,ebook=ebook,duration='1 month',nprice=price)
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
        ebookid = request.POST['ebookid']
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        wishlist = Wishlist.objects.filter(user=request.user,ebook=ebook)[0]
        wishlist.delete()
        return HttpResponse('Success')


@login_required
def mtc(request):
    if request.method == 'POST':
        ebookid = request.POST['ebookid']
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        wishlist = Wishlist.objects.filter(user=request.user,ebook=ebook)[0]
        wishlist.delete()
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

            nprice = getprice('1 month')
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

            nprice = getprice('1 month')
        usercart = Usercart.objects.get_or_create(user=request.user, ebook=ebook,duration='1 month',nprice=nprice)
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
        ebookid = request.POST['ebooknumber']
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        check = Wishlist.objects.filter(user=request.user,ebook=ebook)
        if check.count() == 0:
            wish = Wishlist.objects.get_or_create(user=request.user,ebook=ebook)
            if wish:
                return HttpResponse('Added to wishlist successfully!')
            else:
                return HttpResponse('Please try again later!')
        else:
            return HttpResponse('This e-book is already in your Wishlist!')

@login_required
def payment(request):

    return render(request, "rapp/payment.html", {})


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
    remain = []
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
        if effective > transformer(dash.duration):
            dash.active = False
        else:
            remain.append(round(transformer(dash.duration)-effective,1))
    bdashes = Dashboard.objects.filter(user=request.user,duration='Buy')

    return render(request,'rapp/dashboard.html',{'dashes':dashes,'remain':remain,'bdashes':bdashes})


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
    musdict = recommender(request.user)
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
        elif int(id) == 4:
            check = True
        else:
            check = False
    elif int(id) == 4:
        check = True
    else:
        check = False

    return render(request,'rapp/read.html',{'pages':pages,'id':id,'check':check,'bookmarkarr':bookmarkarr,'musicp':musicp,'musicr':musicrr,'musicgenre':musicgenre,'musiclis':new_lis2,'musiclislen':len(musiclis),'playlist':playlist,'esource':str(esource),'ename':ename,'eauthor':eauthor,'highlightarr':highlightarr,'highlightcolorarr':highlightcolorarr,'highlighttextarr':highlighttextarr,'elang':elang,'bookmarkdataarr':bookmarkdataarr,'notetextarr':notetextarr,'noteselectedtextarr':noteselectedtextarr,'notecfiarr':notecfiarr,'notefilearr':notefilearr})


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
        ebookid = request.POST['ebookid']
        page = request.POST['page']
        ebook = Ebooks.objects.filter(id=ebookid)[0]
        if request.user.is_authenticated:
            delete = Lastpage.objects.filter(user=request.user,ebook=ebook).delete()
            addpage = Lastpage.objects.get_or_create(user=request.user,ebook=ebook,page=page)
        return HttpResponse('Success')


def searchi(request):
    return render(request,'rapp/search.html',{})



class MySearchView(SearchView):
    """My custom search view."""
    template_name = 'rapp/searchshop.html'
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
        context.update({'lprice':lprice,'hprice':hprice,'lpages':lpages,'hpages':hpages,'pubs':pubs,'books':items,'page':page,'totalBooks':totalBooks})
        # do something
        return context



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
        form = UploadForm(request.POST,request.FILES)
        files = request.FILES.getlist('file_field')
        pub = Publishers.objects.filter(name=request.POST['publisher'])[0]
        if form.is_valid():
            for f in files:
                upload = Uploaded()
                upload.publisher = pub
                upload.file = f
                upload.save()
            return redirect('publisher/?upload=success')
    else:
        form = UploadForm()

    if len(UserP.objects.filter(user=request.user)) ==1:
        allow = True
        publisherName = UserP.objects.filter(user=request.user)[0].publisher.name
        numBooks = len(Ebooks.objects.filter(publisher=Publishers.objects.filter(name=publisherName)[0]))
        return render(request,'rapp/publisher.html',{'form':form,'allow':allow,'publisherName':publisherName,'numBooks':numBooks})
    else:
        allow = False
        return render(request,'rapp/publisher.html',{'form':form,'allow':allow})


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
        file = Notefile.objects.create(name=notefilename,user=request.user,ebook=ebook)

        for i in range(len(notearr)):
            Notefileitem.objects.create(notefile=file,note=notearr[i],text=textarr[i])

        return HttpResponse('success')


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