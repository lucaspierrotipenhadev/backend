Abra a pasta docs e leia dos documentos md, para entender os processos do sistema.
No diagrama.sql, está a estrutura do projeto.

1. Temos no momento um backend usando python, e um app usando flutter.

1.1. Para saber mais da documentação do backend vá a pasta docs da pasta backend.
1.2 Para saber mais da documentaçãpo do app, vá a pasta docs da pasta app.


2. Básico para rodar o bakcend:

2.1 Para criar o arquivo do python, primeiro crie um venv:
    python -m venv <SuaPasta>/venv

2.2 Depois estão os comandos para operar o sistema:
- Temos 3 ambientes na versão 1.0, um para teste, um para desenvolver e um futuro para produção.
- Como agora os ambientes estão separados, você precisa indicar qual arquivo de settings utilizar.

2.2.1 Para rodar em servidores de desenvolvimento:
- python manage.py runserver --settings=config.settings.dev

2.2.2. Para rodar migrações
- python manage.py migrate --settings=config.settings.dev

2.2.3 Para rodar testes
- python manage.py test --settings=config.settings.test

3. Básico para rodar o app:
- Instale a extensão do flutter novs code;
- Pressione Ctrl+Shift+P, para ir na janela de extensões e escolha Flutter: Select a Device
- Instale ou rescontrua asa dependências digitando *flutter pub get* no console
- Pressione F5 para rodar o sistema ou digite  *flutter run -d windows* no console para rodar.
