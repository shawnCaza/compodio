# compodio

Work in progress, currently online at [https://www.compodio.com](https://www.compodio.com).

Some community radio stations post audio recordings of their shows online, but do not provide a podcast feed. This project provides RRS feeds for radio shows along side a UI with search and categorization features.

## Development

### Prerequisites

Using docker is recommended to simplify development setup.

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [docker-compose](https://docs.docker.com/compose/install/) (if not included with Docker Desktop)

### Quick Start

1. Set up your .env file

   - Duplicate .env.example to .env
   - In most cases, the default values are all you need.

2. **Start all services:**

   ```bash
   docker-compose up -d --build
   ```

3. **Access the services:**
   - **Frontend:** [http://localhost:3000](http://localhost:3000)
   - **API:** [http://localhost:8000](http://localhost:8000)
   - **Database:** MySQL is available on the port specified in your `.env` file (default 3307)

4. **Stopping services:**

   ```bash
   docker-compose down
   ```

### Notes

- All SQL files in the `db` folder will be executed on database startup. This seeds the database with sample data.
- For development, code changes in the `frontend`, `api`, and `scraper` folders will be reflected in the running containers due to volume mounts.
- If you encounter issues with environment variables, try restarting your terminal and running `docker-compose down` before `docker-compose up`.
