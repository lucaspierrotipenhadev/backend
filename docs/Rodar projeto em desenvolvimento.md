Como agora os ambientes estão separados, você precisa indicar qual arquivo de settings utilizar.

-Para rodar em servidores de desenvolvimento:
python manage.py runserver --settings=config.settings.dev

-Para rodar migrações
python manage.py migrate --settings=config.settings.dev

-Para rodar testes
python manage.py test --settings=config.settings.test