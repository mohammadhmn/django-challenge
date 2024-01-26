from rest_framework import serializers

from stadiums.models import Stadium


class StadiumSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stadium
        fields = ["id", "name", "location"]

    def validate(self, data):
        data = super().validate(data)

        name = data.get("name")
        location = data.get("location")

        if name:
            existing_stadium = Stadium.objects.filter(
                name=name,
                location=location,
            ).first()

            if existing_stadium:
                raise serializers.ValidationError(
                    "A stadium with the same name and location already exists."
                )

        return data
