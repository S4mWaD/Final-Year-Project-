# RiskAvant
 
**Vendor Risk Management Made Simple and Automated**
 
RiskAvant is a web-based application designed to streamline vendor risk management for organizations. It automates the generation of vendor-specific questionnaires, conducts risk assessments, provides real-time scoring, and generates comprehensive risk reports. Built using Django, PostgreSQL, and containerized with Docker, RiskAvant simplifies third-party risk management while maintaining security and compliance standards.
 
---
 
## Features
 
- **Dynamic Vendor Onboarding**: Add vendors and automatically classify them based on service type.

- **Automated Questionnaire Generation**: Vendor-specific compliance and security questionnaires generated dynamically.

- **Real-Time Risk Scoring**: Automatic scoring based on vendor responses with clear risk categorizations.

- **Dashboard and Data Visualization**: Interactive dashboard for monitoring vendor status, risk scores, and compliance posture.

- **Risk Report Generation**: Downloadable PDF reports summarizing vendor risk assessments.

- **Secure User Authentication**: Role-based access control for internal users and external vendors.

- **Containerized Deployment**: Dockerized setup for easy deployment across environments.
 
---
 
## Tech Stack
 
- **Backend**: Django (Python)

- **Frontend**: HTML5, CSS3, JavaScript (with Chart.js for graphs)

- **Database**: PostgreSQL

- **Containerization**: Docker, Docker-Compose

- **Version Control**: GitHub
 
---
 
## Getting Started
 
### Prerequisites

- Python 3.10+

- Docker & Docker-Compose installed

- Git installed
 
### Installation Steps
 
1. **Clone the Repository**

```bash

git clone https://github.com/yourusername/RiskAvant.git

cd RiskAvant

```
 
2. **Configure Environment Variables**

Create a `.env` file in the root directory:

```bash

# .env file example

DJANGO_SECRET_KEY=your_secret_key

POSTGRES_DB=riskavant

POSTGRES_USER=your_db_user

POSTGRES_PASSWORD=your_db_password

POSTGRES_HOST=db

POSTGRES_PORT=5432

```
 
3. **Build and Run using Docker Compose**

```bash

docker-compose up --build

```
 
4. **Access the Application**

- Navigate to `http://localhost:8000/` in your browser.

- Log in as an internal user or vendor.
 
### Running Locally without Docker (Optional)

1. Set up a virtual environment.

2. Install dependencies:

```bash

pip install -r requirements.txt

```

3. Configure local `settings.py` database settings.

4. Run Django server:

```bash

python manage.py runserver

```
 
---
 
## Usage
 
- **Internal Users** can onboard vendors, view risk assessments, and download reports.

- **Vendors** can complete questionnaires and review their submitted assessments.

- **Admins** can manage users, view dashboard analytics, and oversee system operations.
 
---
 

## Future Improvements

- Integration with real-time vendor monitoring services

- Support for additional compliance frameworks (e.g., HIPAA, PCI-DSS)

- Mobile responsiveness

- Multi-tenancy support for large organizations
 
---
 
## Contributing

Pull requests are welcome! For significant changes, please open an issue first to discuss what you would like to change.
 
---
 
## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
 
---
 
## Acknowledgments


- Developed as a part of Final Year Project by **Samwad Basnet**
 
---
 
**RiskAvant** - Simplifying vendor risk management for a safer business ecosystem.
 
---
 
> "Securing your vendors secures your organization."

 
