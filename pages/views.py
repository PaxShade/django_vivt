from django.shortcuts import render

def index(request):
    context = {'title': 'Главная страница'}
    return render(request, 'pages/index.html', context)

def about(request):
    context = {'title': 'О компании'}
    return render(request, 'pages/about.html', context)

def rules(request):
    context = {
        'title': 'Правила',
        'rules_list': [
            'Будьте вежливы и уважайте других участников сообщества.',
            'Используйте только проверенные зависимости и не ломайте системный интерпретатор.',
            'Регулярно делайте миграции базы данных перед запуском сервера.'
        ]
    }
    return render(request, 'pages/rules.html', context)

def custom_page_not_found(request, exception):
    # Пытаемся достать текст из аргументов исключения (кастомный текст)
    if exception and hasattr(exception, 'args') and exception.args:
        error_message = exception.args[0]
    # Если текст передан как обычная строка (или приведен к ней)
    elif str(exception):
        error_message = str(exception)
    # Если зашли на случайную несуществующую страницу
    else:
        error_message = "Возможно, она была удалена, переименована или никогда не существовала."
    
    context = {
        'error_message': error_message,
        'title': 'Страница не найдена'
    }
    
    return render(request, '404.html', context, status=404)