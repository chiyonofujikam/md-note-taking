from django.urls import path
from .views import (
    RenderNoteAPIView,
    GrammarCheckAPIView,
    NoteAPIView
)

urlpatterns = [
    path('notes/', NoteAPIView.as_view(), name='notes'),
    path('notes/<int:pk>/', NoteAPIView.as_view(), name='note-detail'),

    path('notes/<int:pk>/render/', RenderNoteAPIView.as_view(), name='note-render'),
    path('notes/<int:pk>/grammar/', GrammarCheckAPIView.as_view(), name='note-grammar')
]
