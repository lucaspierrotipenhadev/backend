Aqui estão os endpoints para usar e testar a api:

- Accoutns

1. register
- Endpoint usado para registrar um usuário no sistema

- URL POST
http://127.0.0.1:8000/api/v1/accounts/register/

- Header
    Nada

- Body (json)
{
    "username": "nome do usuario",
    "email": "usuario@universal.com",
    "password": "UsuarioSenha",
    "password_confirm": "UsuarioSenha",
    "display_name": "usuario_display_name",
    "bio": "Usuario bio",
    "avatar": "usuario img",
    "birth_date": "usuario birth date"
}

2. login
- Endpoint usado para realizar o login do usuário no sistema

- URL POST
http://127.0.0.1:8000/api/v1/accounts/token/

- Header
    Nada

- Body (json)
{
    "username": "username",
    "password": "userpassword"
}

3. update
- Endpoint usada para atualizar o perfil do usuário

- URL UPDATE
http://127.0.0.1:8000/api/v1/accounts/yo/

- Header
    Authorization
    Bearer Token: access_token

- Body (json)
{
    "display_name": "user",
    "bio": "user bio",
    "avatar": "user img",
    "birth_date": "user birth date"
}

- Posts

1. Posts
- Endpoint usada para postar algo na fakesocialmedia

-URL POST
http://127.0.0.1:8000/api/v1/posts/

- Header
    Authorization
    Bearer token: access_token

- Body (json)
{
    "id": post_id,
    "author": {
        "id":user_id,
        "username": "username",
        "email": "user@example.com",
        "profile": {
            "id": profile_id,
            "avatar": user_avatar,
            "birth_date": user_birth_date,
            "created_at": "profile_create_date",
            "updated_at": "profile_update_date"
        }
    },
    "text": "Post text",
    "edited": true,
    "medias": [
        {
            "id": id_post,
            "file": "post/media",
            "media_type": "post_img",
            "created_at": "post_date"
        }
    ],
    "created_at": "post_create_date",
    "updated_at": "post_updated_date"
}