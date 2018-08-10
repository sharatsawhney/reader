from django import forms
from django.contrib.auth.models import User
from rapp.models import Authors,Publishers,Ebooks,Uploaded
from haystack.forms import SearchForm

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username','email','password')


class UploadForm(forms.ModelForm):
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple':True}))
    
    class Meta:
        model = Uploaded
        fields = ('file_field',)


class PriceRangeSearchForm(SearchForm):
    low_price = forms.FloatField(required=False)
    high_price = forms.FloatField(required=False)
    low_pages = forms.IntegerField(required=False)
    high_pages = forms.IntegerField(required=False)

    def search(self):
        # First, store the SearchQuerySet received from other processing.
        sqs = super(PriceRangeSearchForm, self).search()

        if not self.is_valid():
            return self.no_query_found()
        
        
        # Check to see if a start_date was chosen.
        if self.cleaned_data['low_price']:
            sqs = sqs.filter(price__gte=self.cleaned_data['low_price'])

        # Check to see if an end_date was chosen.
        if self.cleaned_data['high_price']:
            sqs = sqs.filter(price__lte=self.cleaned_data['high_price'])

        if self.cleaned_data['low_pages']:
            sqs = sqs.filter(pages__gte=self.cleaned_data['low_pages'])

        if self.cleaned_data['high_pages']:
            sqs = sqs.filter(pages__lte=self.cleaned_data['high_pages'])
        return sqs


