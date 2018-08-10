from haystack import indexes
from rapp.models import Ebooks

class EbooksIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True, use_template = True,
		template_name='search/ebooks_text.txt')
	name = indexes.CharField(model_attr='name')
	author = indexes.CharField(model_attr='author')
	language = indexes.CharField(model_attr='language')
	publisher = indexes.CharField(model_attr='publisher')
	price = indexes.FloatField(model_attr='price')
	pages = indexes.IntegerField(model_attr='pages')
	category = indexes.CharField(model_attr='category')
	description = indexes.CharField(model_attr='description')
	img= indexes.CharField(model_attr='img')
	priority= indexes.IntegerField(model_attr='priority')
	ebookid = indexes.IntegerField(model_attr='id')
	bookActive = indexes.CharField(model_attr='bookActive')

	def get_model(self):
		return Ebooks

	def index_queryset(self,using=None):
		return self.get_model().objects.all()

