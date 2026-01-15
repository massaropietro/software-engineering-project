from rest_framework import serializers

class BaseModelSerializer(serializers.ModelSerializer):
    def validate(self, attrs):
        if self.instance:
            # For updates, we need to merge existing instance data with the new attrs
            # to check validity of the final state.
            # We can't modify self.instance directly as it would persist side effects if validation fails later
            # (though validate is late stage).
            # A safer way is to create a shadow instance.
            instance_data = {}
            # Copy relevant fields from instance
            for field in self.Meta.model._meta.fields:
                field_name = field.name
                if field_name in attrs:
                    instance_data[field_name] = attrs[field_name]
                else:
                    instance_data[field_name] = getattr(self.instance, field_name)

            # Create a temporary instance for validation
            # Note: This ignores ManyToMany fields for the clean() check, which is usually fine for model.clean()
            # unless it explicitly checks m2m.
            instance = self.Meta.model(**instance_data)
        else:
            # Create
            instance = self.Meta.model(**attrs)

        instance.clean()
        return attrs

