from django.urls import path
from .views import UploadDatasetView, DatasetListView, DatasetDetailView
from .views import dataset_shape_view, dataset_dtypes_view, dataset_nulls_view, dataset_duplicates_view, dataset_unique_values_view, dataset_describe_view
from .views import dataset_histograms_view, dataset_boxplots_view, DashboardView

urlpatterns = [
    path('upload/', UploadDatasetView.as_view(), name='upload-dataset'),
    path('datasets/', DatasetListView.as_view(), name='dataset-list'),
    path('datasets/<int:pk>/', DatasetDetailView.as_view(), name='dataset-detail'),
    path('analyze/<int:id>/shape/', dataset_shape_view, name='dataset-shape'),
    path('analyze/<int:id>/dtypes/', dataset_dtypes_view, name='dataset-dtypes'),
    path('analyze/<int:id>/nulls/', dataset_nulls_view, name='dataset-nulls'),
    path('analyze/<int:id>/duplicates/', dataset_duplicates_view, name='dataset-duplicates'),
    path('analyze/<int:id>/unique/', dataset_unique_values_view, name='dataset-unique-values'),
    path('analyze/<int:id>/describe/', dataset_describe_view, name='dataset-describe'),
    path('analyze/<int:id>/histograms/', dataset_histograms_view, name='dataset-histograms'),
    path('analyze/<int:id>/boxplots/', dataset_boxplots_view, name='dataset-boxplots'),
     path('dashboard/', DashboardView.as_view(), name='dashboard'),
]
