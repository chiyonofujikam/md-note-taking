from rest_framework import serializers
from .models import NoteModel

class NoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteModel
        fields = '__all__'
        read_only_fields = ('id', 'created_at')

class NoteUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteModel
        fields = ['filename', 'document']
