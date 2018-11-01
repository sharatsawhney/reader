from django.conf.urls import url
from django.conf.urls.static import static
from rapp import views
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from rapp.views import MySearchView
from rapp.views import FacetedSearchView

urlpatterns = [
    url(r'^$',views.index, name='index'),
    url(r'^register/$',views.register,name='register'),
    url(r'^login/$', views.user_login, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^about/$',views.about,name='about'),
    url(r'^contact/$',views.contact,name='contact'),
    url(r'^subscribe/$',views.subscribe,name='subscribe'),
    url(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.activate, name='activate'),
    url(r'^check_login/$',views.check_login,name='check_login'),
    url(r'^password_reset/$', views.password_reset, name='password_reset'),
    url(r'^password_reset/done/$',views.password_reset_done, name='password_reset_done'),
    url(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
        views.password_reset_confirm, name='password_reset_confirm'),
    url(r'^reset/done/$', views.password_reset_complete, name='password_reset_complete'),
    url(r'^detail/(?P<id>\d+)/$',views.detail,name='detail'),
    url(r'^cart/$',views.cart,name='cart'),
    url(r'^add_cart/$',views.add_cart,name='add_cart'),
    url(r'^change_duration/',views.change_duration,name='change_duration'),
    url(r'^change_buy/',views.change_buy,name='change_buy'),
    url(r'^delete_cart/',views.delete_cart,name='delete_cart'),
    url(r'^wishlist/$',views.wishlist,name='wishlist'),
    url(r'^delete_wishlist/',views.delete_wishlist,name='delete_wishlist'),
    url(r'^mtc/',views.mtc,name='mtc'),
    url(r'^mtw/',views.mtw,name='mtw'),
    url(r'^atw/',views.atw,name='atw'),
    url(r'^payment/$',views.payment,name='payment'),
    url(r'^payment/success/(?P<transid>[0-9a-z]{32})/$', views.payment_success, name="payment_success"),
    url(r'^payment/failure$', views.payment_failure, name="payment_failure"),
    url(r'^dashboard/$',views.dashboard,name='dashboard'),
    url(r'^reader/(?P<id>\d+)/index.html',views.reader,name='reader'),
    url(r'^change/',RedirectView.as_view(url='/home/sharatsawhney/pdf/theeffort/',permanent=True)),
    url(r'^read/(?P<id>\d+)/$',views.read,name='read'),
    url(r'^sample/(?P<id>\d+)/$',views.sample,name='sample'),
    url(r'^add_notes/$',views.add_notes,name='add_notes'),
    url(r'^save_page/$',views.save_page,name='save_page'),
    url(r'^searchi/$',views.searchi,name='searchi'),
    url(r'^search/', MySearchView.as_view(), name='search_view'),
    url(r'^publisher',views.publisher,name='publisher'),
    url(r'^secure/',views.secure,name='secure'),
    url(r'^bookrequest/',views.bookrequest,name='bookrequest'),
    url(r'^feedback/',views.feedback,name='feedback'),
    url(r'^allower/',views.allower,name='allower'),
    url(r'^pubactivate/(?P<email>.*)/(?P<password>.*)/',views.pubactivate,name='pubactivate'),
    url(r'^pubactivate/$',views.pubactivate,name='pubactivate'),
    url(r'^googlesignin/$',views.googlesignin,name='googlesignin'),
    url(r'^addbookmark/$',views.addbookmark,name='addbookmark'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG is True:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

