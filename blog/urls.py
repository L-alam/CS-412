from django.urls import path
from .views import * #ShowAllView, ArticleView, RandomArticleView

urlpatterns = [
    # map the URL (empty string) to the view
    path('', ShowAllView.as_view(), name='show_all'), # generic class-based view
    path('article/<int:pk>', ArticleView.as_view(), name='article'), # show one article ### NEW
    path('article/create', CreateArticleView.as_view(), name="create_article"),
    path('article/<int:pk>/create_comment', CreateCommentView.as_view(), name='create_comment'), ### NEW
]