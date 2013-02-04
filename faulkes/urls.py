from django.conf.urls.defaults import *


urlpatterns = patterns('faulkes.views',

	(r'^search','search'),

	(r'^recent','view_group',{'mode' : 'recent'}),
	(r'^popular','view_group',{'mode' : 'popular'}),
	(r'^trending','view_group',{'mode' : 'trending'}),

	(r'^user/(?P<userid>\d+)','view_user'),
	(r'^user/(?P<username>[a-zA-Z\.]+)','view_username'),
	(r'^user','index'),
	(r'^u/(?P<userid>\d+)','view_user'),
	(r'^u/(?P<username>[a-zA-Z\.]+)','view_username'),

	(r'^object/(?P<object>[a-zA-Z \+\-\.0-9]+)','view_object'),
	(r'^object','index'),
	(r'^o/(?P<object>[a-zA-Z \+\-\.0-9]+)','view_object'),

	(r'^category/(?P<avm>[0-9\.]+)','view_avm'),
	(r'^category/(?P<category>\w+)','view_category'),
	(r'^category','view_category_list'),
	(r'^c/(?P<avm>[0-9\.]+)','view_avm'),
	(r'^c/(?P<category>\w+)','view_category'),

	(r'^map','view_map'),

	(r'^(?P<code>\w\w\w)/(?P<tel>\w+)/(?P<obs>\d+)','view_observation'),
	(r'^(?P<code>\w\w\w)/show','view_site'),
	(r'^(?P<code>\w\w\w)/(?P<tel>\w+)','view_telescope'),
	(r'^(?P<code>\w\w\w)','view_site'),

	(r'^$','index'),
#	(r'','unknown'),
)
