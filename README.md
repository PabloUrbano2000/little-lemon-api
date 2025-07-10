# 🍋 Little Lemon API

API REST desarrollada con Django y Django REST Framework para gestionar operaciones internas de la empresa **Little Lemon**, incluyendo:

- Gestión de usuarios y grupos (`Manager`, `Delivery crew`, `Customer`)
- Creación y consulta de órdenes
- Carrito de compras
- Menú y categorías

## 🚀 Tecnologías

- Python 3.x
- Django
- Django REST Framework
- SQLite (por defecto, fácilmente cambiable a PostgreSQL)
- JWT o Token Auth (si aplica)

## 🛠️ Endpoints principales

| Método | Endpoint          | Descripción                        |
| ------ | ----------------- | ---------------------------------- |
| GET    | /menu-items/      | Lista de ítems del menú            |
| POST   | /cart/menu-items/ | Añade ítems al carrito             |
| POST   | /orders/          | Crea una orden desde el carrito    |
| GET    | /orders/<id>/     | Consulta una orden específica      |
| PATCH  | /orders/<id>/     | Actualización (manager o delivery) |
| DELETE | /orders/<id>/     | Elimina una orden (solo manager)   |

## 🔐 Roles y permisos

- **Customer**: puede ver menú, agregar al carrito y crear órdenes.
- **Manager**: puede modificar órdenes, asignar delivery y eliminar.
- **Delivery crew**: solo puede actualizar el estado de sus órdenes asignadas.

## 📦 Instalación local

```bash
git clone https://github.com/PabloUrbano2000/little-lemon-api.git
cd little-lemon-api
python -m venv env
source env/bin/activate  # En Windows: env\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
