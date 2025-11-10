import io
import os
import shutil

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import NoteModel
from .serializers import NoteSerializer, NoteUploadSerializer

import markdown as md
import language_tool_python
from django.db import connection, transaction

tool = language_tool_python.LanguageTool('en-US')


class NoteAPIView(APIView):
    """
        Unified Note API handler.

        Supports:
        - GET /api/notes/ → list all notes
        - GET /api/notes/<int:pk>/ → retrieve one note
        - POST /api/notes/ → upload a markdown note (multipart/form-data)
        - DELETE /api/notes/<int:pk>/ → delete a single note
        - DELETE /api/notes/ → delete all notes and media files
    """
    serializer_class = NoteUploadSerializer

    def get(self, request, pk=None, *args, **kwargs):
        """Retrieve all notes or a single note by ID."""
        if pk:
            try:
                note = NoteModel.objects.get(pk=pk)
                serializer = NoteSerializer(note)
                return Response(serializer.data, status=status.HTTP_200_OK)
            except NoteModel.DoesNotExist:
                return Response({"error": f"Note with ID {pk} does not exist."}, status=status.HTTP_404_NOT_FOUND)

        notes = NoteModel.objects.all().order_by('-created_at')
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
            Upload a markdown file (multipart/form-data).
            Expects 'document' file and optional 'filename'.
        """
        uploaded_file = request.FILES.get('document')
        if not uploaded_file:
            return Response({"error": "No file provided. Expecting field 'document'."}, status=status.HTTP_400_BAD_REQUEST)

        content_bytes = uploaded_file.read()
        try:
            text = content_bytes.decode('utf-8')
        except UnicodeDecodeError:
            text = content_bytes.decode('latin-1')

        note = NoteModel.objects.create(
            filename= uploaded_file.name,
            document=uploaded_file,
            markdown_text=text,
            report_issues=['No issues reported.']
        )
        note.save()
        serializer = NoteSerializer(note)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, pk=None, *args, **kwargs):
        """Delete a specific note or all notes (and their files)."""
        if pk:
            return self._delete_single(pk)
        return self._delete_all()

    def _delete_single(self, pk):
        """Helper to delete one note and its associated file."""
        try:
            note = NoteModel.objects.get(pk=pk)
        except NoteModel.DoesNotExist:
            return Response({"error": f"Note with ID {pk} does not exist."}, status=status.HTTP_404_NOT_FOUND)

        # Delete associated file
        if note.document and os.path.isfile(note.document.path):
            os.remove(note.document.path)

        note.delete()
        return Response({"message": f"Note with ID {pk} deleted successfully."}, status=status.HTTP_204_NO_CONTENT)

    @transaction.atomic
    def _delete_all(self):
        """Helper to delete all notes, reset autoincrement, and clear files."""
        notes = NoteModel.objects.all()
        count = notes.count()

        # Delete all files on disk
        for note in notes:
            if note.document and os.path.isfile(note.document.path):
                os.remove(note.document.path)

        # Clear database and reset primary key sequence
        notes.delete()
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM sqlite_sequence WHERE name='notes_notemodel';")

        # Remove documents folder
        documents_dir = os.path.join(os.getcwd(), 'media', 'Documents')
        if os.path.isdir(documents_dir):
            shutil.rmtree(documents_dir, ignore_errors=True)

        return Response({"message": f"Successfully deleted all ({count}) notes and cleared media files."}, status=status.HTTP_204_NO_CONTENT)

class RenderNoteAPIView(APIView):
    """
        Render the note (markdown_text or file content) to HTML and return it.
    """
    def get(self, request, pk, format=None):
        note = NoteModel.objects.get(pk=pk)
        text = note.markdown_text
        if not text and note.document:
            try:
                with note.document.open('r') as f:
                    text = f.read()
            except Exception as err:
                return Response({"detail": "No text provided for grammar check.", "error": err}, status=status.HTTP_404_NOT_FOUND)

        # render markdown to html
        html = md.markdown(text or '', extensions=['fenced_code', 'tables'])
        return Response({'html': html}, status=status.HTTP_200_OK)

class GrammarCheckAPIView(APIView):
    """
        Check grammar for a note (by id) or for raw text passed in body.
            POST /api/notes/{id}/grammar/  OR
            POST /api/grammar/check/ with JSON {'text': '...'}
    """
    def post(self, request, pk=None, format=None):
        if pk is not None:
            error = 'No exception occurred.'
            note = NoteModel.objects.get(pk=pk)
            content = note.markdown_text
            if not content and note.document:
                try:
                    with note.document.open('r') as f:
                        content = f.read()
                except Exception as err:
                    error = err
                    content = ''

        if not content:
            return Response({"detail": "No text provided for grammar check.", "error": error}, status=status.HTTP_400_BAD_REQUEST)

        issues = []
        for m in tool.check(content):
            issues.append({
                'message': m.message,
                'context': m.context,
                'offset': m.offset,
                'length': m.errorLength if hasattr(m, 'errorLength') else m.length if hasattr(m, 'length') else None,
                'replacements': m.replacements
            })

        if pk is not None:
            note.report_issues = issues
            note.save()

        return Response({'issues': issues, 'count': len(issues)}, status=status.HTTP_200_OK)
