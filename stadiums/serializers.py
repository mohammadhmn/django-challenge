from drf_yasg import openapi
from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from stadiums.models import Stadium


class StadiumSerializer(serializers.ModelSerializer):
    """
    Serializer for the Stadium model.

    ---
    # Fields
    - `id`: The unique identifier for the stadium.
    - `name`: The name of the stadium.
    - `location`: The location of the stadium.

    # Validations
    - A stadium with the same name and location should not already exist.
    """

    class Meta:
        model = Stadium
        fields = ["id", "name", "location"]

    def validate(self, data):
        """
        Validate that a stadium with the same name and location does not already exist.

        :param data: The data to be validated.
        :type data: dict
        :raises serializers.ValidationError: If validation fails.
        :return: The validated data.
        :rtype: dict
        """
        name = data.get("name")
        location = data.get("location")

        if name and Stadium.objects.filter(name=name, location=location).exists():
            raise serializers.ValidationError(
                "A stadium with the same name and location already exists."
            )

        return data
