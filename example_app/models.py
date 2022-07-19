from django.db import models


class PersonManager(models.Manager):
    def get_by_natural_key(self, first_name, last_name):
        return self.get(first_name=first_name, last_name=last_name)


class Person(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    # Override the default manager with our custom manager to include get_by_natural_key method.
    objects = PersonManager()

    class Meta:
        # This is a unique constraint.
        unique_together = [['first_name', 'last_name']]

    def natural_key(self):
        # This is the key that will be used to look up the Person in the database.
        return (self.first_name, self.last_name)


class Book(models.Model):
    name = models.CharField(max_length=100)
    author = models.ForeignKey(Person, on_delete=models.CASCADE)
