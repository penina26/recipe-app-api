"""
Views for the recipe APIs.
"""
from rest_framework import viewsets 
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe

# explicitly name the file (module) and the class inside it
from recipe.RecipeSerializer import RecipeSerializer 


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    
    # We assign the class directly now!
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve recipes for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)