# Magazine List

Um sistema web em Django para catalogar e visualizar aparições de modelos em revistas.

## 🚀 Funcionalidades

- **Gestão de Dados**: Cadastro de modelos (Women), edições de revistas (Issues) e seções (Sections) via Django Admin.
- **Visualização**:
    - Listagem visual de todas as modelos cadastradas.
    - Página de detalhes de cada modelo com histórico completo de aparições.
- **Interface**: Design moderno com tema escuro (Dark Mode) e responsivo.

## 🛠️ Tecnologias

- Python 3.12+
- Django 6.0
- HTML5 / CSS3 (Grid & Flexbox)
- SQLite

## 📦 Como rodar o projeto

1. **Clone o repositório**
   ```bash
   git clone https://github.com/EBarbara/magazine-list.git
   cd magazine-list
   ```

2. **Crie e ative o ambiente virtual**
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate
   ```

3. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```

4. **Prepare o banco de dados**
   ```bash
   python manage.py migrate
   ```

5. **Crie um superusuário (Opcional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Execute o servidor**
   ```bash
   python manage.py runserver
   ```

Acesse em: `http://127.0.0.1:8000/`

## 🗃️ Estrutura do Projeto

- `core/`: Aplicação principal contendo modelos, views e templates.
- `magazine_list/`: Configurações do projeto Django.
- `static/core/css/`: Folhas de estilo costumizadas.

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.
