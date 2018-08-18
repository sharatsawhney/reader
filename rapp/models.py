from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User
from datetime import datetime, timezone


class Authors(models.Model):
    name = models.CharField(max_length=255, unique=True)
    publisher_name = models.ForeignKey('Publishers',on_delete=models.DO_NOTHING,default='')

    def __str__(self):
        return self.name


class Publishers(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    cat = models.CharField(max_length=255)

    def __str__(self):
        return self.cat


class Ebooks(models.Model):
    name = models.CharField(max_length=255, unique=True)
    author = models.ForeignKey('Authors',on_delete=models.DO_NOTHING)
    publisher = models.ForeignKey('Publishers',on_delete=models.DO_NOTHING)
    price = models.FloatField()
    pages = models.IntegerField()
    content = models.FileField(upload_to='media/',default='',blank=True)
    link = models.URLField(default='',blank=True)
    category = models.ForeignKey('Category',on_delete=models.DO_NOTHING,default=1)
    img = models.ImageField(upload_to='images/',default='')
    CHOICES = (
        ('3 days','3 days'),
        ('7 days','7 days'),
        ('14 days','14 days'),
        ('21 days','21 days'),
        ('1 month','1 month'),
        ('1.5 months','1.5 months'),
        ('2 months','2 months'),
        ('3 months','3 months'),
        ('4 months','4 months'),
        ('5 months','5 months'),
        ('6 months','6 months'),
        ('12 months','12 months'),
        ('18 months','18 months'),
        ('24 months','24 months'),
    )
    dayopt = MultiSelectField(choices=CHOICES,default='3 days,7 days,14 days,21 days,1 month,1.5 months,2 months,3 months,4 months,5 months,6 months')
    LANG_CHOICES = (
        ('English','English'),
        ('Hindi','Hindi'),
    )
    language = models.CharField(max_length=30,choices= LANG_CHOICES,default='English')
    description = models.TextField(default="",blank=True)
    PRI_CHOICES = (
        (1,1),
        (2,2),
        (3,3),
        (4,4),
        (5,5),
        (6,6),
        (7,7),
        (8,8),
        (9,9),
        (10,10),
    )
    priority = models.IntegerField(choices= PRI_CHOICES,default=5)
    ACTIVE_CHOICES = (
        ('bookActive','bookActive'),
        ('bookInactive','bookInactive'),
    )
    bookActive = models.CharField(max_length=20,choices= ACTIVE_CHOICES,default='bookActive')
    isbn = models.CharField(max_length=14,default='')

    def __str__(self):
        return self.name


class UserP(models.Model):
    user = models.OneToOneField(User,on_delete=models.DO_NOTHING)
    pub = models.BooleanField(default=False)
    publisher = models.ForeignKey('Publishers',on_delete=models.DO_NOTHING,default='')

    def __str__(self):
        return self.user.username


class Subscribers(models.Model):
    subemail = models.EmailField()

    def __str__(self):
        return self.subemail


class Usercart(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    ebook = models.ForeignKey('Ebooks',on_delete=models.DO_NOTHING)
    CHOICES = (
        ('3 days', '3 days'),
        ('7 days', '7 days'),
        ('14 days', '14 days'),
        ('21 days', '21 days'),
        ('1 month', '1 month'),
        ('1.5 months', '1.5 months'),
        ('2 months', '2 months'),
        ('3 months', '3 months'),
        ('4 months', '4 months'),
        ('5 months', '5 months'),
        ('6 months', '6 months'),
        ('12 months', '12 months'),
        ('18 months', '18 months'),
        ('24 months', '24 months'),
    )
    duration = models.CharField(max_length=255, choices=CHOICES)
    nprice = models.FloatField(default=0)
    BUY_CHOICES = (
        ('Buy','Buy'),
        ('Rent','Rent'),
    )
    buyrent = models.CharField(max_length=10,choices= BUY_CHOICES,default='Rent')

    def __str__(self):
        strebook = str(self.ebook)
        return strebook


class Wishlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    ebook = models.ForeignKey('Ebooks',on_delete=models.DO_NOTHING)

    def __str__(self):
        strebook = str(self.ebook)
        return strebook


class Dashboard(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING,default='')
    ebook = models.ForeignKey('Ebooks', on_delete=models.DO_NOTHING,default='')
    CHOICES = (
        ('3 days', '3 days'),
        ('7 days', '7 days'),
        ('14 days', '14 days'),
        ('21 days', '21 days'),
        ('1 month', '1 month'),
        ('1.5 months', '1.5 months'),
        ('2 months', '2 months'),
        ('3 months', '3 months'),
        ('4 months', '4 months'),
        ('5 months', '5 months'),
        ('6 months', '6 months'),
        ('12 months', '12 months'),
        ('18 months', '18 months'),
        ('24 months', '24 months'),
        ('Buy','Buy'),
    )
    duration = models.CharField(max_length=255, choices=CHOICES,default='1 month')
    nprice = models.FloatField(default=0)
    itime = models.DateTimeField(default=datetime.now)
    active = models.BooleanField()

    def __str__(self):
        return str(self.itime)


class Transactions(models.Model):
    txnid = models.CharField(max_length=32)

    def __str__(self):
        return self.txnid


class Notes(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    title = models.CharField(max_length=255)
    text = models.TextField()

    def __str__(self):
        return self.title


class Lastpage(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    ebook = models.ForeignKey('Ebooks',on_delete=models.DO_NOTHING)
    page = models.IntegerField()
    time = models.DateTimeField(default=datetime.now)

    def __str__(self):
        return str(self.page)


class Uploaded(models.Model):
    publisher = models.ForeignKey('Publishers',on_delete=models.DO_NOTHING)
    file = models.FileField(upload_to='media/')
    handled = models.BooleanField(default=False)

    def __str__(self):
        return str(self.file)