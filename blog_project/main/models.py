from django.db import models
from django.contrib.auth.models import User

# Категорії для статей
class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Назва категорії")
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name="Зображення")

    class Meta:
        verbose_name = "Категорія"
        verbose_name_plural = "Категорії"

        def __str__(self):
            return self.name

# Теги
class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name="Тег")

    class Meta:
            verbose_name = "Тег"
            verbose_name_plural = "Теги"

            def __str__(self):
                return self.name

#Основна модель Статті
class Article(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Чернетка'),
        ('published', 'Опублікована'),
    ]

    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Категорія")
    tags = models.ManyToManyField(Tag, blank=True, verbose_name="Теги")

    title = models.CharField(max_length=200, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст статті")
    image = models.ImageField(upload_to='articles/', blank=True, null=True, verbose_name="Головне фото")
    video = models.FileField(upload_to='videos/', blank=True, null=True, verbose_name="Відео (необов'язково)")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft', verbose_name="Статус")

    class Meta:
        verbose_name = "Стаття"
        verbose_name_plural = "Статті"
        ordering = ['-created_at'] #Створення: нові зверху

    def __str__(self):
        return self.title

#Коментарі
class Comment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments', verbose_name="Стаття")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор коментаря")
    text = models.TextField(verbose_name="Текст")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата")

    class Meta:
        verbose_name = "Коментар"
        verbose_name_plural = "Коментарі"

    def __str__(self):
        return f"Коментарі від {self.author.username} до {self.article.title}"

#Оголошення (Notification з діаграми)
class Announcement(models.Model):
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    text = models.TextField(verbose_name="Текст оголошення")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True, verbose_name="Активна")

    class Meta:
        verbose_name = "Оголошення"
        verbose_name_plural = "Оголошення"