from django.db import models
from django.contrib.auth.models import User
from multiselectfield import MultiSelectField
from django.contrib.auth.models import User
from datetime import datetime, timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class Authors(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Publishers(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    cat = models.CharField(max_length=255)
    CHOICES = (
        ('3month', '3month'),
        ('12month', '12month'),
    )
    catmodel = models.CharField(max_length=20, choices=CHOICES, default='3month')

    def __str__(self):
        return self.cat


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Ebooks(models.Model):
    name = models.CharField(max_length=255, unique=True)
    author = models.ForeignKey('Authors',on_delete=models.DO_NOTHING)
    publisher = models.ForeignKey('Publishers',on_delete=models.DO_NOTHING,null=True,default='')
    publishdate = models.DateField(blank=True,null=True)
    price = models.FloatField()
    pages = models.IntegerField()
    content = models.CharField(max_length=255,default='')
    category = models.ForeignKey('Category',on_delete=models.DO_NOTHING,default=1)
    img = models.CharField(max_length=255,default='')
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
    description = models.TextField(default="",blank=True,null=True)
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
    isbn = models.CharField(max_length=14,default='',null=True)
    tags = models.ManyToManyField(Tag,blank=True)
    rating = models.FloatField(default=0)
    ratedusers = models.IntegerField(default=0)

    def __str__(self):
        return self.name


class UserP(models.Model):
    user = models.OneToOneField(User,on_delete=models.DO_NOTHING)
    pub = models.BooleanField(default=False)
    publisher = models.ForeignKey('Publishers',on_delete=models.DO_NOTHING,default='')
    benname = models.CharField(max_length=255,blank=True)
    account = models.CharField(max_length=255,blank=True)
    ifsc = models.CharField(max_length=255,blank=True)
    number = models.CharField(max_length=255,blank=True)

    def __str__(self):
        return self.user.username


class Adminacc(models.Model):
    user = models.OneToOneField(User,on_delete=models.DO_NOTHING)

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
    epubcfi = models.TextField(default='')
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.epubcfi)


class Uploaded(models.Model):
    publisher = models.ForeignKey('Publishers',on_delete=models.DO_NOTHING)
    file = models.CharField(max_length=255)
    handled = models.BooleanField(default=False)

    def __str__(self):
        return str(self.file)


class Gmailid(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING,default='')

    def __str__(self):
        return self.user.username


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, default='')
    ebook = models.ForeignKey('Ebooks',on_delete=models.DO_NOTHING)
    location = models.IntegerField()
    data = models.TextField(default='')

    def __str__(self):
        return self.ebook.name


class Musicgenre(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='musicgenre/',null=True)

    def __str__(self):
        return self.name


class Musictag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Music(models.Model):
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255,blank=True,null=True)
    image = models.ImageField(upload_to='musicimages/')
    duration = models.IntegerField()
    media = models.FileField(upload_to='music/')
    genre = models.ForeignKey('Musicgenre',on_delete=models.DO_NOTHING)
    tag = models.ManyToManyField(Musictag,blank=True)
    listennum = models.IntegerField(default=0)
    PRI_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (9, 9),
        (10, 10),
    )
    priority = models.IntegerField(choices= PRI_CHOICES,default=5)
    publishdate = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Musiclis(models.Model):
    music = models.ForeignKey('Music',on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    time = models.DateTimeField(auto_now_add=True)
    queue = models.BooleanField(default=True)

    def __str__(self):
        return self.music.name


class Playlist(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    music = models.ManyToManyField(Music,blank=True)

    def __str__(self):
        return self.name


class Highlight(models.Model):
    cfirange = models.TextField()
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    ebook = models.ForeignKey('Ebooks',on_delete=models.DO_NOTHING)
    CHOICES = (
        ('rgb(255, 237, 165)', 'rgb(255, 237, 165)'),
        ('rgb(219, 255, 183)', 'rgb(219, 255, 183)'),
        ('rgb(255, 219, 219)', 'rgb(255, 219, 219)'),
        ('rgb(201, 237, 237)', 'rgb(201, 237, 237)'),
    )
    color = models.CharField(max_length=255, choices=CHOICES,default='rgb(255, 237, 165)')
    note = models.BooleanField(default=False)
    text = models.TextField(blank=True,null=True)
    selectedtext = models.TextField(default='')
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cfirange


class Notefile(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    ebook = models.ForeignKey(Ebooks,on_delete=models.DO_NOTHING)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.name


class Notefileitem(models.Model):
    notefile = models.ForeignKey(Notefile,on_delete=models.DO_NOTHING)
    note = models.TextField()
    text = models.TextField()

    def __str__(self):
        return self.notefile.name


class Uploadadmin(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.user.username


class Keyvalue(models.Model):
    key = models.CharField(max_length=255)
    value = models.IntegerField(default=0)

    def __str__(self):
        return self.key


class Offer(models.Model):
    name1 = models.CharField(max_length=255)
    name2 = models.CharField(max_length=255)
    ebooks = models.ManyToManyField(Ebooks)
    percentbool = models.BooleanField(default=True)
    trueoffer = models.BooleanField(default=False)
    offerlowlimit = models.IntegerField(null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])
    offerhighlimit = models.IntegerField(null=True, validators=[MinValueValidator(0), MaxValueValidator(100)])

    def __str__(self):
        return str(str(self.name1) + str(self.name2))


class Bestseller(models.Model):
    name = models.CharField(max_length=255)
    ebooks = models.ManyToManyField(Ebooks)

    def __str__(self):
        return self.name


class Detailview(models.Model):
    ebook = models.ForeignKey(Ebooks,on_delete=models.DO_NOTHING)
    user =models.ForeignKey(User,on_delete=models.DO_NOTHING)
    time = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField()
    profilevector = models.TextField(default='')
    
    def __str__(self):
        return self.ebook.name
    
    
class Readview(models.Model):
    ebook = models.ForeignKey(Ebooks,on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    time = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField()
    profilevector = models.TextField(default='')
    
    def __str__(self):
        return self.ebook.name


class Sampleview(models.Model):
    ebook = models.ForeignKey(Ebooks, on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    time = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField()
    profilevector = models.TextField(default='')

    def __str__(self):
        return self.ebook.name


class Genreview(models.Model):
    genre = models.ForeignKey(Category,on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    time = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField()
    profilevector = models.TextField(default='')

    def __str__(self):
        return self.genre.cat


class Newreleaseview(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    time = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField()

    def __str__(self):
        return self.user.username


class Bestsellerview(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    time = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField()

    def __str__(self):
        return self.user.username


class Searchview(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    time = models.DateTimeField(auto_now_add=True)
    duration = models.IntegerField()
    profilevector = models.TextField('')

    def __str__(self):
        return self.user.username


class Rateduser(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    ebook = models.ForeignKey(Ebooks,on_delete=models.DO_NOTHING)
    rating = models.IntegerField()

    def __str__(self):
        return self.user.username


class Percentageread(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    ebook = models.ForeignKey('Ebooks',on_delete=models.DO_NOTHING)
    percent = models.FloatField(null=True)

    def __str__(self):
        return str(self.percent)


class Readlocation(models.Model):
    readmodel = models.ForeignKey(Percentageread,on_delete=models.DO_NOTHING)
    location = models.IntegerField()
    PHASE_CHOICES = (
        ('full', 'full'),
        ('left', 'left'),
        ('right', 'right'),
    )
    phase = models.CharField(max_length=10, choices=PHASE_CHOICES, default='full')

    def __str__(self):
        return self.phase


class ConnectionHistory(models.Model):
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    publicip = models.CharField(max_length=100)
    localip = models.CharField(max_length=100)
    status = models.IntegerField(default=0)
    echo = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.localip


class Payment(models.Model):
    paymentid = models.CharField(max_length=40)
    amount = models.FloatField()
    ebook = models.ForeignKey(Ebooks,on_delete=models.DO_NOTHING)
    user = models.ForeignKey(User,on_delete=models.DO_NOTHING)
    time = models.DateTimeField(auto_now_add=True)
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
        ('Buy', 'Buy'),
    )
    duration = models.CharField(max_length=255, choices=CHOICES, default='21 days')

    def __str__(self):
        return self.paymentid


class Publisherpayment(models.Model):
    paymentid = models.CharField(max_length=40)
    publisher = models.ForeignKey(Publishers,on_delete=models.DO_NOTHING)
    amount = models.FloatField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.paymentid
