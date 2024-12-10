from django.contrib.auth.decorators import login_required
from utils.auth_crawler import AuthCrawler
from django.contrib import messages
from django.shortcuts import redirect

@login_required
def iniciar_crawler(request):
    if request.method == 'POST':
        try:
            url_login = request.POST.get('url_login')
            usuario = request.POST.get('usuario')
            senha = request.POST.get('senha')
            
            crawler = AuthCrawler(debug=True)
            sucesso = crawler.fazer_login(url_login, usuario, senha)
            
            if sucesso:
                messages.success(request, 'Crawler iniciado com sucesso!')
            else:
                messages.error(request, 'Falha ao iniciar o crawler')
                
            crawler.fechar()
            
        except Exception as e:
            messages.error(request, f'Erro: {str(e)}')
            
    return redirect('responder_questoes')
