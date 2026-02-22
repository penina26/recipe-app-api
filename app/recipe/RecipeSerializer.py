"""
Serializers for recipe APIs.
"""
from rest_framework import serializers

from core.models import Recipe


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    class Meta:
        model = Recipe
        fields = [
            'id', 'title', 'time_minutes', 'price', 'link'
        ]
        # We make the ID read-only so users can't accidentally (or maliciously) 
        # try to overwrite the primary key of a recipe in the database.
        read_only_fields = ['id']