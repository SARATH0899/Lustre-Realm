# Lustre Realm : Ornaments E-Commerce Website

## Project Description

This is a complete e-commerce website built with Django for selling ornaments such as bangles, anklets, bracelets, earrings, necklaces, and rings. It includes features like user accounts (registration, login, profile management), product catalog, shopping cart, order processing, and static pages for about, contact, privacy, services, shipping, and terms.

The project is structured with Django apps:
- **accounts**: Handles user authentication and profiles.
- **cart**: Manages shopping cart functionality.
- **core**: Core features including static pages.
- **orders**: Order management and checkout.
- **products**: Product listings and details.

It uses SQLite as the default database (configurable in settings) and includes templates for frontend rendering. Images and static files are served from the `static` directory.

## Prerequisites

- Python 3.11 or higher
- pip (Python package installer)
- Virtual environment tool (recommended: venv or virtualenv)
- Git (for cloning the repository)

## Setup Instructions

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/ornaments-ecommerce.git
   cd ornaments-ecommerce
   ```
2. **Create a Virtual Environment** (recommended to isolate dependencies):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. **Activate the Virtual Environment**:
   - On Windows: `venv\Scripts\activate`
   - On macOS/Linux: `source venv/bin/activate`

4. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
5. **Apply Database Migrations**:
   ```bash
   python manage.py migrate
   ```
6. **Create a Superuser**:
   ```bash
   python manage.py createsuperuser
   ```
   Follow the prompts to create a superuser account.
   
7. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```
   - The website will be available at `http://127.0.0.1:8000/` or `http://localhost:8000/`
   - The admin interface will be available at `http://127.0.0.1:8000/admin/` or `http://localhost:8000/admin/`
   - The admin username and password are the ones you created during setup.

## Project Structure

- accounts : User authentication and profile management.
- cart : Shopping cart functionality.
- core : Static pages like about, contact, privacy, services, shipping, and terms.
- orders : Order processing and checkout.
- products : Product catalog and details.
- static : Static files (CSS, JavaScript, images) for the website.
- templates : HTML templates for rendering pages.
- manage.py : Django management script.
- requirements.txt : Project dependencies.

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

This project is licensed under the MIT License. See the `LICENSE` file for more details.

## Contact

For any questions or feedback, please contact:

- **Email**: [sarathmr@gmail.com](mailto:sarathmr@gmail.com)
- **GitHub**: [SARATH0899](https://github.com/SARATH0899)
- **Portfolio**: [Sarath M R](https://sarathmr.netlify.app)


