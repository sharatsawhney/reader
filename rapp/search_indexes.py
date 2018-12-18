from haystack import indexes
from rapp.models import Ebooks,Tag

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
	priority= indexes.IntegerField(model_attr='priority')
	bookActive = indexes.CharField(model_attr='bookActive')
	isbn = indexes.CharField(model_attr='isbn')
	tags = indexes.MultiValueField()
	rating = indexes.FloatField(model_attr='rating')
	ebookid = indexes.IntegerField(model_attr='id')
	img = indexes.CharField(model_attr='img')
	suggestions = indexes.FacetCharField()
	name_auto = indexes.EdgeNgramField(model_attr='name')
	author_auto = indexes.EdgeNgramField(model_attr='author')
	publisher_auto = indexes.EdgeNgramField(model_attr='publisher')
	category_auto = indexes.EdgeNgramField(model_attr='category')
	isbn_auto = indexes.EdgeNgramField(model_attr='isbn')

	def get_model(self):
		return Ebooks

	def prepare_tags(self, object):
		return [tag.name for tag in object.tags.all()]

	def prepare(self, obj):
		prepared_data = super(EbooksIndex, self).prepare(obj)
		prepared_data['suggestions'] = prepared_data['text']
		return prepared_data

	def index_queryset(self,using=None):
		return self.get_model().objects.all()


class TagIndex(indexes.SearchIndex, indexes.Indexable):
	text = indexes.CharField(document=True)
	tags = indexes.CharField(model_attr='name')
	tags_auto = indexes.EdgeNgramField(model_attr='name')

	def get_model(self):
		return Tag

	def index_queryset(self,using=None):
		return self.get_model().objects.all()




