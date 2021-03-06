# Generated by Django 2.0.6 on 2019-04-16 09:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('C_num', models.IntegerField(verbose_name='编号')),
                ('C_name', models.CharField(max_length=255, verbose_name='名称')),
            ],
        ),
        migrations.CreateModel(
            name='Score',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('S_score', models.IntegerField(verbose_name='成绩')),
                ('S_course', models.ForeignKey(on_delete=True, to='app.Course', verbose_name='课程')),
            ],
        ),
        migrations.CreateModel(
            name='Student',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('S_num', models.IntegerField(verbose_name='学号')),
                ('S_name', models.CharField(max_length=255, verbose_name='姓名')),
                ('S_age', models.IntegerField(verbose_name='年龄')),
                ('S_sex', models.CharField(max_length=255, verbose_name='性别')),
            ],
        ),
        migrations.CreateModel(
            name='Teacher',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('T_num', models.IntegerField(verbose_name='编号')),
                ('T_name', models.CharField(max_length=255, verbose_name='姓名')),
            ],
        ),
        migrations.AddField(
            model_name='score',
            name='S_student',
            field=models.ForeignKey(on_delete=True, to='app.Student', verbose_name='学生'),
        ),
        migrations.AddField(
            model_name='course',
            name='C_teacher',
            field=models.ForeignKey(on_delete=True, to='app.Teacher', verbose_name='教师'),
        ),
    ]
