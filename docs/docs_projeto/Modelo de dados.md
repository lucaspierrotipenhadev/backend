Modelagem do Banco de Dados
Diagrama Conceitual
                 +----------------+
                 |     User       |
                 +----------------+
                 | id             |
                 | username       |
                 | email          |
                 | password       |
                 +----------------+
                        |
                 OneToOne
                        |
                        |
                 +----------------+
                 |    Profile     |
                 +----------------+
                 | id             |
                 | user           |
                 | display_name   |
                 | bio            |
                 | avatar         |
                 | birth_date     |
                 | created_at     |
                 | updated_at     |
                 +----------------+

                        ▲
                        │
                 created by
                        │
                +----------------+
                |      Post      |
                +----------------+
                | id             |
                | author         |
                | text           |
                | created_at     |
                | updated_at     |
                | edited         |
                +----------------+
                    │      │
          ┌─────────┘      └──────────────┐
          │                               │
      has many                      has many
          │                               │
          ▼                               ▼

 +------------------+          +----------------+
 |   PostMedia      |          |    Comment     |
 +------------------+          +----------------+
 | id               |          | id             |
 | post             |          | author         |
 | image            |          | post           |
 | created_at       |          | parent         |
 +------------------+          | text           |
                               | created_at     |
                               | updated_at     |
                               +----------------+
                                      │
                              replies │
                                      ▼
                                Comment

Agora adicionando as interações.

Likes
User
 │
 │
 ▼
PostLike
 │
 ▼
Post
+----------------+
|   PostLike     |
+----------------+
| id             |
| user           |
| post           |
| created_at     |
+----------------+

Um usuário pode curtir vários posts.

Um post pode possuir milhares de curtidas.

Comentários seguem exatamente a mesma ideia.

User
 │
 ▼
CommentLike
 │
 ▼
Comment
+------------------+
|  CommentLike     |
+------------------+
| id               |
| user             |
| comment          |
| created_at       |
+------------------+
Seguir usuários

Ao invés de amizade, teremos seguidores.

User
 │
 │ follows
 ▼
FollowUser
 │
 │
 ▼
User

Tabela

+--------------------+
|   FollowUser       |
+--------------------+
| id                 |
| follower           |
| following          |
| created_at         |
+--------------------+

Exemplo

Lucas segue João

follower = Lucas

following = João
Reposts
User
 │
 ▼
PostRepost
 │
 ▼
Post

Tabela

+------------------+
|   PostRepost     |
+------------------+
| id               |
| user             |
| post             |
| created_at       |
+------------------+
Compartilhamentos
User
 │
 ▼
PostShare
 │
 ▼
User
              │
              ▼
            Post

Tabela

+------------------+
|   PostShare      |
+------------------+
| id               |
| sender           |
| receiver         |
| post             |
| created_at       |
+------------------+

Isso representa o envio de um post para outro usuário.

No futuro poderemos criar um Chat utilizando essa estrutura.

Mídias

Cada post pode possuir várias mídias.

Post

 │

 ▼

PostMedia
+----------------+
|   PostMedia    |
+----------------+
| id             |
| post           |
| file           |
| media_type     |
| created_at     |
+----------------+

Observe que eu trocaria image por file.

Assim o sistema poderá aceitar:

imagens
vídeos
GIFs
PDFs (caso queira futuramente)

E teremos

media_type

IMAGE

VIDEO

GIF

Isso deixa o sistema muito mais flexível.

Comentários

Aqui existe uma característica interessante.

Post

 │

 ▼

Comment

 │

 ▼

Comment

 │

 ▼

Comment

O próprio comentário aponta para outro comentário.

No banco fica assim.

+----------------------+
|      Comment         |
+----------------------+
| id                   |
| author               |
| post                 |
| parent               |
| text                 |
| created_at           |
| updated_at           |
+----------------------+

Quando

parent = NULL

é um comentário principal.

Quando

parent = Comentário 15

é uma resposta ao comentário.

Isso permite infinitos níveis de respostas.

Visão Geral
User
 │
 ├───────────────► Profile
 │
 ├───────────────► Post
 │                     │
 │                     ├────────► PostMedia
 │                     │
 │                     ├────────► Comment
 │                     │              │
 │                     │              └──────► Comment
 │                     │
 │                     ├────────► PostLike
 │                     │
 │                     └────────► PostRepost
 │
 │
 ├───────────────► FollowUser
 │
 └───────────────► PostShare
Quantidade de relacionamentos
Entidade	Relacionamentos
User	1:1 com Profile
User	1:N com Post
User	N:N com User através de FollowUser
User	N:N com Post através de PostLike
User	N:N com Comment através de CommentLike
User	N:N com Post através de PostRepost
User	N:N com Post através de PostShare
Post	1:N com Comment
Post	1:N com PostMedia
Comment	1:N com Comment (Self Relationship)