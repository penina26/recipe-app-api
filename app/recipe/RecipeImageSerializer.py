"""
Serilizer to add an image to a recipe
"""
from rest_framework import serializers
from core.models import Recipe

class RecipeImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Recipe
        fields = ['id', 'image']
        read_only_fields = ['id']
        # We enforce that an image must be provided if they hit this endpoint
        extra_kwargs = {'image': {'required': 'True'}}