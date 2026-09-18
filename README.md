# Musicarte Web
Sistema web do Projeto Musicarte — IFPR Campus Paranavaí.

## Como abrir no VS Code e rodar
1. Extraia o ZIP e abra a pasta `musicarte_web` no VS Code.
2. Abra o terminal nessa pasta.
3. Crie o ambiente virtual: `python -m venv venv`
4. No Windows PowerShell, ative com: `venv\Scripts\Activate.ps1`
   - Se o PowerShell bloquear, use o Prompt de Comando: `venv\Scripts\activate.bat`
5. Instale: `python -m pip install -r requirements.txt`
6. Prepare o banco: `python manage.py migrate`
7. Crie seu usuário administrador: `python manage.py createsuperuser`
8. Rode: `python manage.py runserver`
9. Abra no navegador: `http://127.0.0.1:8000/`

## O que já está pronto
- Site público responsivo: Início, Sobre, Oficinas, Eventos, Galeria e Equipe.
- Login e painel de gestão.
- CRUD de alunos, instrutores, oficinas, matrículas, aulas e eventos.
- Controle de frequência por aula.
- Galeria gerenciável pelo Django Admin.
- Upload de fotos de oficinas, instrutores, eventos e galeria.
- Busca e paginação nas telas principais de cadastro.
- SQLite.

## Onde colocar as informações reais depois
Você não precisa alterar código para cadastrar nomes, telefones, horários e fotos. Entre no painel/admin e cadastre os dados. As imagens enviadas pelo formulário ficam na pasta `media/` automaticamente.

## Observação
O projeto não inclui fotos reais do Musicarte ainda. Onde faltam imagens, o layout usa placeholders discretos que desaparecem assim que as fotos forem cadastradas.
