## Screenshots

### Main Page Example

![Main Page Example](./images/demo.jpg)

### System Design

![System Design](./images/system_design.jpg)

# MapleStory Drop Data Microservice Monorepo

This project is a monorepo designed to manage and display MapleStory drop data, leveraging a microservice architecture for scalability and maintainability. It includes a Next.js frontend and several Python FastAPI backend services.

## Features

- **Drop Data Management:** CRUD operations for MapleStory drop records.
- **Image Retrieval:** Dynamic retrieval and display of mob and item images.
- **Name Resolution:** Resolving IDs to names and names to IDs for game entities.
- **Aggregated Search:** Comprehensive search functionality for drop data.
- **User Authentication:** (Implied by `useAuth` context, but not fully implemented in provided code).
- **Containerized Development:** Easy local setup using Docker Compose.
- **CI/CD Pipeline:** Automated build and release process with GitLab CI.

## Architecture Overview

The project follows a microservice architecture, orchestrated by Docker Compose for local development. API calls from the Next.js frontend are handled through a mix of Next.js App Router API routes and direct rewrites configured in `next.config.ts`.

### Services:

- **`ms-nextjs-template` (Frontend):** A Next.js application serving the user interface.
- **`ms-maple-drop-repo` (Backend):** Manages MapleStory drop data in a MySQL database.
- **`ms-name-resolver` (Backend):** Resolves game entity names and IDs using MongoDB.
- **`ms-search-aggregator` (Backend):** Aggregates search results by orchestrating calls to other microservices.
- **`ms-image-retriever` (Backend):** Retrieves images from a MinIO object storage.

## Technology Stack

- **Frontend:**
  - Next.js (React Framework)
  - React
  - TypeScript
  - Tailwind CSS
  - React Icons
- **Backend (Python Microservices):**
  - FastAPI
  - Uvicorn (ASGI server)
  - `mysql-connector-python` (for MySQL)
  - `pymongo` (for MongoDB)
  - `minio` (for MinIO object storage)
  - `httpx` (HTTP client for inter-service communication)
- **Database/Storage:**
  - MySQL
  - MongoDB
  - MinIO Object Storage
- **Containerization:**
  - Docker
  - Docker Compose
- **CI/CD:**
  - GitLab CI

## Setup and Local Development

### Prerequisites

- Docker Desktop (or Docker Engine and Docker Compose)
- Git

### Cloning the Repository

```bash
git clone <repository-url>
cd microservice_template
```

### Environment Variables

Create a `.env` file in the project root with the following environment variables. These are used by `docker-compose.yml` to configure the backend services.

```dotenv
# Example .env content
ITEM_DATA_DB_PASSWORD=your_mysql_password
MINIO_ROOT_PASSWORD=your_minio_password
MONGO_URI=mongodb://host.docker.internal:30370/?directConnection=true # Adjust port if needed
```

### Running Services with Docker Compose

Navigate to the project root directory and run:

```bash
docker-compose up --build
```

This command will:
- Build Docker images for all services (if not already built).
- Start all microservices and the Next.js frontend.
- Create a shared Docker network for inter-service communication.

### Accessing the Frontend

The Next.js frontend will be accessible at `http://localhost:30102` (as configured in `docker-compose.yml`).

## API Endpoints Overview

This section provides a brief overview of the main API endpoints exposed by the backend microservices.

- **Drop Repository Service (`ms-maple-drop-repo`)**
  - `GET /get_drop/{id}`: Retrieve a drop record.
  - `POST /add_drop`: Add a new drop record.
  - `PUT /update_drop/{id}`: Update a drop record.
  - `DELETE /delete_drop/{id}`: Delete a drop record.
  - _Note: The `/api/search_drops` endpoint is handled by the Next.js App Router API route, which then calls `ms-search-aggregator`._

- **Name Resolver Service (`ms-name-resolver`)**
  - `POST /api/id-names/resolve`: Resolve IDs to names.
  - `POST /api/names-id/resolve`: Resolve names to IDs.

- **Search Aggregator Service (`ms-search-aggregator`)**
  - `GET /api/search/drops-augmented?name=<query>`: Aggregates and augments drop search results.

- **Image Retriever Service (`ms-image-retriever`)**
  - `GET /images/{type}/{id}`: Retrieve images (e.g., mob, item).

## Frontend API Routing (next.config.ts rewrites)

The `frontend/next.config.ts` file defines rewrite rules to proxy certain API calls directly to the backend microservices, bypassing Next.js App Router API routes for those specific paths.

```typescript
// Excerpt from next.config.ts
async rewrites() {
  return [
    {
      source: '/api/images/:path*',
      destination: 'http://ms-image-retriever:8000/images/:path*',
    },
    {
      source: '/api/get_drop/:path*',
      destination: 'http://ms-maple-drop-repo:8000/get_drop/:path*',
    },
    {
      source: '/api/add_drop',
      destination: 'http://ms-maple-drop-repo:8000/add_drop',
    },
    {
      source: '/api/delete_drop/:path*',
      destination: 'http://ms-maple-drop-repo:8000/delete_drop/:path*',
    },
    // Note: /api/search_drops is handled by a Next.js App Router API route (src/app/api/search_drops/route.ts)
    // and then calls ms-search-aggregator.
  ];
},
```

## CI/CD and Deployment

This project uses GitLab CI for its Continuous Integration and Continuous Deployment pipeline.

- **Build Stage:** Docker images for the frontend and most backend microservices are built and pushed to Docker Hub on every commit to the `dev` branch.
  - _Note: `ms-image-retriever` currently lacks a dedicated build job in `.gitlab-ci.yml`._
- **Release Stage:** On commits to the `dev` branch, a Merge Request is automatically created to update image tags in `deployment.yaml` files and push them to the `main` branch.

