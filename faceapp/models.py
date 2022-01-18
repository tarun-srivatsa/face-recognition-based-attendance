from django.db import models

dept_list=(
    ('CS','CS'), ('IS','IS'), ('EC','EC'), 
    # ('EE'), ('EI'), ('ET'), ('ME'), ('CV'), ('BT'), ('IM'), ('AS'), ('CH')
)

class Section(models.Model):
    dept_code=models.CharField(max_length=5,choices=dept_list) # CS IS EC EE EI ET ME CV BT IM AS CH
    batch=models.PositiveSmallIntegerField()

    class Meta:
        unique_together=(('dept_code','batch'),)

    def __str__(self):
        return f"{self.dept_code} - {self.batch}"

# class Course(models.Model):
#     code=models.CharField(max_length=10,primary_key=True)
#     scheme=models.PositiveSmallIntegerField(primary_key=True)
#     name=models.CharField(max_length=30)

#     def __str__(self):
#         return f"{self.code}-{self.year}"

class Student(models.Model):
    usn=models.CharField(max_length=10,primary_key=True)
    name=models.CharField(max_length=60)
    photo=models.ImageField()
    section=models.ForeignKey(Section,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.usn} - {self.name}"

class Class(models.Model):
    section=models.ForeignKey(Section,on_delete=models.CASCADE)
    # course=models.ForeignKey(Course,on_delete=models.CASCADE,primary_key=True)
    course_code=models.CharField(max_length=10)
    faculty=models.CharField(max_length=40)

    class Meta:
        unique_together=(('section','course_code'),)

    def __str__(self):
        return f"{self.faculty}-{self.course_code}"

class CurrentSession(models.Model):
    classdetails=models.ForeignKey(Class,on_delete=models.CASCADE)
    date=models.DateField()
    countage=models.PositiveSmallIntegerField(default=1)

    class Meta:
        unique_together=(('classdetails','date'),)

    def __str__(self):
        return f"{self.classdetails.faculty}-{self.date}"

class Present(models.Model):
    session=models.ForeignKey(CurrentSession,on_delete=models.CASCADE)
    student=models.ForeignKey(Student,on_delete=models.CASCADE)