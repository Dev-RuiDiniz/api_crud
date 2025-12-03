# 📦 API CRUD de Pedidos (Orders)

## 📝 Descrição do Projeto

Esta é uma API CRUD assíncrona desenvolvida em Python para gerenciar o ciclo de vida de pedidos (Orders).
O projeto implementa boas práticas de desenvolvimento, como:

- Validação de dados com Pydantic v2
- Persistência assíncrona com MongoDB
- Proteção de rotas com JWT (JSON Web Tokens)
- Cálculo automático do valor total (total_value) antes de salvar no banco

---

## ⚙️ Tecnologias Utilizadas

| **Tecnologia** | **Descrição** |
| **Python** | Linguagem de programação principal. |
| **FastAPI** | Framework moderno e rápido para construção da API assíncrona. |
| **Pydantic v2** | Validação de dados e definição de schemas. |
| **MongoDB** | Banco NoSQL usado para persistência dos dados. |
| **Motor** | Driver assíncrono para integração do FastAPI com o MongoDB. |
| **python-jose** | Biblioteca para manipulação e validação de tokens JWT. |

---

## 🚀 Setup e Instalação

Siga os passos abaixo para rodar o projeto localmente.

### 🔧 Pré-requisitos

- Python 3.10+
- MongoDB Server rodando localmente (porta 27017) ou configurado em src/config/db.py.

1. 📥 Clonar o Repositório

```
git clone https://github.com/RUI FRANCISCO/api_crud.git
cd api_crud
```

2. 🧪 Criar e Ativar Ambiente Virtual

```
# Criar ambiente virtual
python -m venv venv

# Ativar no Windows (PowerShell)
.\venv\Scripts\Activate

# Ativar no Linux/macOS/Git Bash
source venv/bin/activate
```

3. 📦 Instalar Dependências

Inclui uvicorn, python-jose, motor, fastapi, pydantic e outros:

```
pip install uvicorn python-jose[cryptography] passlib motor pydantic fastapi
```

4. ▶️ Rodar a API

```
uvicorn src.main:app --reload
```
A API estará disponível em:
👉 http://127.0.0.1:8000

---

## 📖 Instruções de Uso da API

O FastAPI fornece documentação interativa para testar a API:

| **Documentação** | **Link** |
| **Swagger UI** | http://127.0.0.1:8000/docs |
| **ReDoc** | http://127.0.0.1:8000/redoc |

---

## 🔑 Autenticação (JWT)

As rotas POST e PATCH exigem autenticação JWT (Bearer Token).

Para Testar:
- Gere um token de teste usando a função create_access_token em src/security.py (o projeto simula um usuário com ID "101").
- No Swagger UI, clique em Authorize e insira:

```
Bearer <SEU_TOKEN_AQUI>
```

---

## 📚 Endpoints Principais (CRUD)

| **Método** | **Endpoint** | **Descrição** | **Status Code** | Protegido (JWT) |
| **POST** | /orders/ | Cria um novo pedido | 201 Created | ✔️ |
| **GET** | /orders/ | Lista pedidos com paginação (skip, limit) | 200 OK | ❌ |
| **GET** | /orders/{id} | Busca pedido por ID | 200 OK / 404 |	❌ |
| **PATCH** | /orders/{id} | Atualiza campos específicos | 200 OK / 404 | ✔️ |
| **DELETE** | /orders/{id} | Exclui um pedido | 204 No Content / 404 |	❌ |

---

## 🔗 Link do Repositório

[Repositorio] (https://github.com/Dev-RuiDiniz/api_crud)