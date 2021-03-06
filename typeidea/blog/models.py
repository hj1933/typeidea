# -*- coding: utf-8 -*-

from django.contrib.auth.models import User
from django.db import models


class Category(models.Model):
    STATUS_NOMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NOMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )
    name = models.CharField(max_length=50, verbose_name='名称')
    status = models.PositiveIntegerField(default=STATUS_NOMAL, choices=STATUS_ITEMS, verbose_name='状态')
    is_nav = models.BooleanField(default=False, verbose_name='是否为导航')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.DO_NOTHING)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = verbose_name_plural = '分类'

    def __str__(self):
        return self.name


    @classmethod
    def get_navs(cls):
        """获取分类信息"""
        categoties = Category.objects.filter(status=Category.STATUS_NOMAL)
        nav_category = []       # 导航分类
        normal_category = []
        for cate in categoties:
            # 一次查询，一次判断，检查 IO 操作
            if cate.is_nav:
                nav_category.append(cate)
            else:
                normal_category.append(cate)
        return {
            'navs': nav_category,
            'categories': normal_category
        }


class Tag(models.Model):
    STATUS_NOMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NOMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )
    name = models.CharField(max_length=50, verbose_name='名称')
    status = models.PositiveIntegerField(default=STATUS_NOMAL, choices=STATUS_ITEMS, verbose_name='状态')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.DO_NOTHING)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = verbose_name_plural = '标签'

    def __str__(self):
        return self.name


class Post(models.Model):
    STATUS_NOMAL = 1
    STATUS_DELETE = 0
    STATUS_DRAFT = 2
    STATUS_ITEMS = (
        (STATUS_NOMAL, '正常'),
        (STATUS_DELETE, '删除'),
        (STATUS_DRAFT, '草稿'),
    )
    title = models.CharField(max_length=255, verbose_name='标题')
    desc = models.CharField(max_length=1024, verbose_name='摘要', blank=True)
    content = models.TextField(verbose_name='正文', help_text='文章内容必须为 markdown格式')
    status = models.PositiveIntegerField(default=STATUS_NOMAL, choices=STATUS_ITEMS, verbose_name='状态')

    category = models.ForeignKey(Category, verbose_name='分类', on_delete=models.CASCADE)
    tag = models.ManyToManyField(Tag, verbose_name='标签')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    pv = models.PositiveIntegerField(default=1)     # 统计访问量
    uv = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = verbose_name_plural = '文章'
        ordering = ['-id']  # 根据 ID 降序排序

    def __str__(self):
        return self.title

    @staticmethod
    def get_by_tag(tag_id):
        """获取标签数据"""
        try:
            tag = Tag.objects.get(id=tag_id)
        except Tag.DoesNotExist:
            tag = None
            post_list = []
        else:
            # selecte_related 解决 N + 1 问题
            post_list = Post.objects.filter(status=Post.STATUS_NOMAL).select_related('category', 'owner')
        return post_list, tag

    @staticmethod
    def get_by_categoty(category_id):
        """获取分类数据"""
        try:
            category = Category.objects.filter(id=category_id)
        except Category.DoesNotExist:
            category = None
            post_list = []
        else:
            post_list = Post.objects.filter(status=Post.STATUS_NOMAL).select_related('category', 'owner')

        return post_list, category

    @classmethod
    def latest_posts(cls):
        """获取最新数据"""
        queryset = cls.objects.filter(status=cls.STATUS_NOMAL)

        return queryset

    @classmethod
    def host_posts(cls):
        """获取最热文章"""
        return cls.objects.filter(status=cls.STATUS_NOMAL).order_by('-pv')
