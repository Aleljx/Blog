from django.shortcuts import render, get_object_or_404, redirect
from .models import Article, Category, Comment, Grade
from .forms import CommentForm, UserRegisterForm, GradeForm
from django.contrib import messages
from django.db.models import Avg, Q
from django.contrib import messages
from .forms import CategoryForm


def index(request):
    category_id = request.GET.get('category')

    # 1. Складна фільтрація:
    # (Статус 'опубліковано') АБО (Автор — це ви)
    if request.user.is_authenticated:
        filters = Q(status='published') | Q(author=request.user)
    else:
        filters = Q(status='published')

    # 2. Застосовуємо фільтри та рахуємо рейтинг
    articles = Article.objects.filter(filters).annotate(
        avg_rating=Avg('grades__stars')
    )

    # 3. Фільтрація за категорією
    if category_id:
        articles = articles.filter(category_id=category_id)

    # 4. Сортування
    articles = articles.order_by('-created_at')

    categories = Category.objects.all()

    return render(request, 'main/index.html', {
        'articles': articles,
        'categories': categories,
        'selected_category': category_id
    })

# Сторінка конкретної статті (якої зараз не вистачає)
def article_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    comments = article.comments.all()

    # Розрахунок середнього рейтингу
    grades = article.grades.all()
    avg_rating = sum([g.stars for g in grades]) / grades.count() if grades.exists() else 0

    # Створюємо обидві форми
    comment_form = CommentForm()
    grade_form = GradeForm()

    if request.method == 'POST' and request.user.is_authenticated:
        # Перевіряємо, яка саме форма була відправлена
        if 'submit_comment' in request.POST:
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.article = article
                comment.author = request.user
                comment.save()
                return redirect('article_detail', pk=pk)


        elif 'submit_grade' in request.POST:
            # Спочатку створюємо форму з даними з запиту
            grade_form = GradeForm(request.POST)
            if grade_form.is_valid():
                # Використовуємо update_or_create: якщо оцінка є — оновимо, якщо немає — створимо
                Grade.objects.update_or_create(
                    article=article,
                    user=request.user,
                    defaults={'stars': grade_form.cleaned_data['stars']}
                )
                return redirect('article_detail', pk=pk)

    return render(request, 'main/article_detail.html', {
        'article': article,
        'comments': comments,
        'comment_form': comment_form,
        'grade_form': grade_form,
        'avg_rating': round(avg_rating, 1)
    })


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Акаунт створено для {username}!')
            return redirect('login')
    else:
        form = UserRegisterForm()

    return render(request, 'main/register.html', {'form': form})


from .forms import ArticleForm
from django.contrib.auth.decorators import login_required


@login_required  # Тільки авторизовані користувачі можуть створювати пости
def article_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES)  # request.FILES потрібен для завантаження картинок
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user  # Автоматично призначаємо автора
            article.save()
            return redirect('index')
    else:
        form = ArticleForm()

    return render(request, 'main/article_form.html', {'form': form})


def article_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)

    # ПЕРЕВІРКА ПРАВ: якщо ти не автор І не адмін — доступ заборонено
    if article.author != request.user and not request.user.is_staff:
        messages.error(request, "Ви можете редагувати лише власні статті!")
        return redirect('article_detail', pk=pk)

    if request.method == 'POST':
        form = ArticleForm(request.POST, request.FILES, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, "Статтю успішно оновлено!")
            return redirect('article_detail', pk=pk)
    else:
        form = ArticleForm(instance=article)

    return render(request, 'main/article_form.html', {
        'form': form,
        'edit_mode': True,
        'article': article
    })


def article_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)

    # Перевірка прав (як і для редагування)
    if article.author != request.user and not request.user.is_staff:
        messages.error(request, "Ви не можете видалити цю статтю!")
        return redirect('article_detail', pk=pk)

    if request.method == 'POST':
        article.delete()
        messages.success(request, "Статтю успішно видалено!")
        return redirect('index')

    return render(request, 'main/article_confirm_delete.html', {'article': article})

@login_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Категорію успішно додано!")
            return redirect('article_create') # Повертаємо на створення поста
    else:
        form = CategoryForm()
    return render(request, 'main/category_form.html', {'form': form})


@login_required
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)

    # Разрешаем удаление только персоналу (админам)
    if not request.user.is_staff:
        messages.error(request, "Только администратор может удалять категории!")
        return redirect('index')

    if request.method == 'POST':
        category.delete()
        messages.success(request, "Категория успешно удалена!")
        return redirect('index')

    return render(request, 'main/category_confirm_delete.html', {'category': category})