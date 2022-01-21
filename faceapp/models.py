from datetime import date
from django.db import models

dept_list=(
    ('CS','CS'), ('IS','IS'), ('EC','EC'),
    ('EE','EE'), ('EI','EI'), ('ET','ET'),
    ('ME','ME'), ('CV','CV'), ('BT','BT'),
    ('IM','IM'), ('AS','AS'), ('CH','CH'),
)

class Section(models.Model):
    dept_code=models.CharField(max_length=5,choices=dept_list)
    batch=models.PositiveSmallIntegerField()

    class Meta:
        unique_together=(('dept_code','batch'),)

    def __str__(self):
        return f"{self.dept_code}-{self.batch}"

class Student(models.Model):
    usn=models.CharField(max_length=10,primary_key=True)
    name=models.CharField(max_length=60)
    photo=models.ImageField()
    json_encoding=models.TextField()
    section=models.ForeignKey(Section,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usn}-{self.name}"

class Class(models.Model):
    section=models.ForeignKey(Section,on_delete=models.CASCADE)
    course_code=models.CharField(max_length=10)
    faculty=models.CharField(max_length=40)

    class Meta:
        unique_together=(('section','course_code'),)

    def __str__(self):
        return f"{self.faculty}-{self.course_code}"

class CurrentSession(models.Model):
    classdetails=models.ForeignKey(Class,on_delete=models.CASCADE)
    date=models.DateField(default=date.today)
    countage=models.PositiveSmallIntegerField(default=1)
    # is_active=models.BooleanField(default=False,null=True)

    class Meta:
        unique_together=(('classdetails','date'),)

    def __str__(self):
        return f"{self.classdetails.faculty}-{self.date}"

class Present(models.Model):
    session=models.ForeignKey(CurrentSession,on_delete=models.CASCADE)
    student=models.ForeignKey(Student,on_delete=models.CASCADE)
    timestamp=models.DateTimeField(auto_now_add=True,null=True)