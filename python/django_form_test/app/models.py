from django.db import models

# Create your models here.

class Student(models.Model):
    S_num = models.IntegerField(verbose_name="学号")
    S_name = models.CharField(verbose_name="姓名", max_length=255)
    S_age = models.IntegerField(verbose_name="年龄")
    S_sex = models.CharField(verbose_name="性别", max_length=255)


class Course(models.Model):
    C_num = models.IntegerField(verbose_name="编号")
    C_name = models.CharField(verbose_name="名称", max_length=255)
    C_teacher = models.ForeignKey("Teacher", verbose_name="教师", on_delete=True)


class Score(models.Model):
    S_student = models.ForeignKey("Student", verbose_name="学生", on_delete=True)
    S_course = models.ForeignKey("Course", verbose_name="课程", on_delete=True)
    S_score = models.IntegerField(verbose_name="成绩")


class Teacher(models.Model):
    T_num = models.IntegerField(verbose_name="编号")
    T_name = models.CharField(verbose_name="姓名", max_length=255)