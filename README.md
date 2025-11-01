# EU ForecastHUB

**Forecast the Future, Together**

Build and share transparent forecasts — empower policy with open foresight.

## 🌟 Overview

EU ForecastHUB is an open-source forecasting platform designed to democratize access to sophisticated forecasting tools and models. The platform enables researchers, policymakers, and citizens to create, publish, and collaborate on forecasts across multiple domains including climate, economy, society, policy, and technology.

## 🎯 Key Features

### 1. **Forecast Builder**
An interactive tool for configuring forecast scenarios:
- **Kill Chain Configuration**: Advanced scenario planning with configurable stages
- **Stage Management**: Set domain weights, natural language rules, and importance levels
- **Interactive Interface**: Clean, intuitive UI for configuring forecast parameters
- **Message Input**: Describe forecasts and ask questions to get started

### 2. **Forecast Publishing**
Publish and share forecasts with:
- Project name and description
- Publisher information
- Keywords for discoverability
- Full project documentation

### 3. **Collaboration Platform**
Connect researchers and enable collaboration through:
- Project opportunity listings
- Contact information sharing
- File attachments for proposals
- Search and discovery tools

### 4. **Kill Chain Stages**
Advanced scenario planning with configurable stages:
- Reconnaissance
- Weaponization
- Delivery
- Exploitation
- Installation
- Command & Control (C2)
- Actions on Objectives

Each stage supports:
- **Domain Weight Distribution**: Configure weights for Environment, Economy, Society, Policy, and Technology domains
- **Natural Language Rules**: Define specific sub-scenarios using natural language input
- **Importance Scoring**: Set importance levels (0-1) to prioritize different stages

## 🏗️ Technology Stack

### Frontend
- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool and dev server
- **React Router** - Client-side routing
- **TanStack Query** - Data fetching and caching
- **Tailwind CSS** - Styling
- **Radix UI** - Accessible component primitives
- **Lucide React** - Icons
- **Shadcn/ui** - UI components

### Development Tools
- **ESLint** - Code linting
- **TypeScript** - Static type checking
- **PostCSS** - CSS processing
- **Autoprefixer** - CSS vendor prefixing

## 🚀 Getting Started

### Prerequisites
- Node.js 18+ or Bun
- npm, yarn, or bun package manager

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-org/the-euforecast-hub.git
cd the-euforecast-hub
```

2. **Install dependencies**
```bash
npm install
# or
yarn install
# or
bun install
```

3. **Start the development server**
```bash
npm run dev
# or
yarn dev
# or
bun dev
```

4. **Open your browser**
Navigate to `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## 📁 Project Structure

```
src/
├── components/
│   ├── ui/              # Reusable UI components (shadcn)
│   ├── layout/          # Layout components
│   └── features/        # Feature-specific components
├── pages/
│   ├── Index.tsx        # Landing page
│   ├── Builder.tsx      # Forecast builder interface
│   ├── Forecasts.tsx    # Forecast listing and search
│   ├── Collaborations.tsx # Collaboration opportunities
│   └── NotFound.tsx     # 404 page
├── hooks/               # Custom React hooks
├── lib/                 # Utility functions
├── App.tsx              # Main app component
├── main.tsx             # App entry point
└── index.css            # Global styles
```

## 🔌 Backend API Integration

This frontend application is designed to work with a backend API. Below are the required API endpoints and specifications.

### Base Configuration

```
Base URL: http://localhost:8000/api/v1
Content-Type: application/json
```

### Authentication

**No authentication required** - All endpoints are publicly accessible.

### Required Endpoints

#### 1. Forecast Management

##### GET /forecasts
Get list of published forecasts with optional search/filtering.

**Query Parameters:**
- `search` (string, optional): Search term for name, publisher, keywords, or description
- `page` (number, optional, default: 1): Page number for pagination
- `limit` (number, optional, default: 20): Items per page
- `sortBy` (string, optional): Field to sort by (createdAt, name, publisher)
- `order` (string, optional): Sort order (asc, desc)

**Response:**
```json
{
  "success": true,
  "data": {
    "forecasts": [
      {
        "id": "string",
        "name": "string",
        "publisherName": "string",
        "projectKeywords": "string",
        "projectDescription": "string",
        "status": "active" | "archived" | "draft",
        "category": "string",
        "createdAt": "ISO 8601 date",
        "updatedAt": "ISO 8601 date"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 100,
      "totalPages": 5
    }
  }
}
```

##### GET /forecasts/:id
Get detailed information about a specific forecast.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "name": "string",
    "publisherName": "string",
    "projectKeywords": "string",
    "projectDescription": "string",
    "status": "string",
    "category": "string",
    "metadata": {
      "modelConfig": {},
      "dataSources": [],
      "methodology": "string"
    },
    "createdAt": "ISO 8601 date",
    "updatedAt": "ISO 8601 date"
  }
}
```

##### POST /forecasts
Publish a new forecast.

**Request Body:**
```json
{
  "name": "string (required)",
  "publisherName": "string (required)",
  "projectKeywords": "string (required)",
  "projectDescription": "string (required)",
  "metadata": {
    "modelConfig": {},
    "dataSources": [],
    "methodology": "string"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "message": "Forecast published successfully"
  }
}
```

#### 2. Collaboration Management

##### GET /collaborations
Get list of collaboration opportunities.

**Query Parameters:**
- `search` (string, optional): Search term
- `page` (number, optional): Page number
- `limit` (number, optional): Items per page

**Response:**
```json
{
  "success": true,
  "data": {
    "collaborations": [
      {
        "id": "string",
        "name": "string",
        "email": "string",
        "projectDescription": "string",
        "uploadedFileName": "string (optional)",
        "uploadType": "pdf" | "image" | "document",
        "status": "active" | "closed",
        "createdAt": "ISO 8601 date"
      }
    ],
    "pagination": {
      "page": 1,
      "limit": 20,
      "total": 50,
      "totalPages": 3
    }
  }
}
```

##### GET /collaborations/:id
Get detailed collaboration information.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "name": "string",
    "email": "string",
    "projectDescription": "string",
    "uploadedFileName": "string",
    "uploadType": "string",
    "status": "string",
    "createdAt": "ISO 8601 date"
  }
}
```

##### POST /collaborations
Submit a collaboration opportunity.

**Request Body:**
```json
{
  "name": "string (required)",
  "email": "string (required, valid email)",
  "projectDescription": "string (required)",
  "uploadedFile": "File (multipart/form-data, optional)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "message": "Collaboration opportunity submitted successfully"
  }
}
```

##### POST /collaborations/:id/contact
Contact a collaborator (creates a contact request/notification).

**Request Body:**
```json
{
  "requesterName": "string (required)",
  "requesterEmail": "string (required)",
  "message": "string (required)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "message": "Contact request sent successfully"
  }
}
```

#### 3. File Upload Endpoints

##### POST /uploads
Handle file uploads for collaborations or forecasts.

**Request:**
- `multipart/form-data`
- Field: `file`

**Response:**
```json
{
  "success": true,
  "data": {
    "url": "string",
    "fileName": "string",
    "fileType": "string",
    "fileSize": "number"
  }
}
```

##### GET /uploads/:filename
Retrieve uploaded file.

**Response:**
- Binary file content
- Appropriate Content-Type header

#### 4. Forecast Builder Management

##### POST /builder/projects
Save a forecast project configuration from the builder.

**Request Body:**
```json
{
  "name": "string (required)",
  "stageConfigurations": {
    "Reconnaissance": {
      "domainWeights": {
        "environment": 20,
        "economy": 20,
        "society": 20,
        "policy": 20,
        "technology": 20
      },
      "nlRuleInput": "string",
      "importance": 0.5
    },
    "Weaponization": { ... },
    "Delivery": { ... },
    "Exploitation": { ... },
    "Installation": { ... },
    "Command & Control (C2)": { ... },
    "Actions on Objectives": { ... }
  },
  "messageHistory": [
    {
      "timestamp": "ISO 8601 date",
      "message": "string",
      "type": "user" | "system"
    }
  ]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "projectId": "string",
    "message": "Project saved successfully"
  }
}
```

##### GET /builder/projects/:id
Retrieve a saved forecast project configuration.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "string",
    "name": "string",
    "stageConfigurations": {},
    "messageHistory": [],
    "createdAt": "ISO 8601 date",
    "updatedAt": "ISO 8601 date"
  }
}
```

##### POST /builder/run
Execute forecast scenario based on kill chain configuration.

**Request Body:**
```json
{
  "projectId": "string (optional)",
  "stageConfigurations": {},
  "dataFile": "file (optional, multipart/form-data)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "forecastId": "string",
    "scenarioResults": {},
    "metadata": {
      "stagesAnalyzed": ["Reconnaissance", "Weaponization", ...],
      "domainWeightsApplied": {},
      "timestamp": "ISO 8601 date"
    },
    "createdAt": "ISO 8601 date"
  }
}
```

##### POST /builder/message
Process a message input from the builder interface along with all stage configurations.

**Request Body:**
```json
{
  "message": "string (required)",
  "stageConfigurations": {
    "Reconnaissance": {
      "domainWeights": {
        "environment": 20,
        "economy": 20,
        "society": 20,
        "policy": 20,
        "technology": 20
      },
      "nlRuleInput": "string",
      "importance": 0.5
    },
    "Weaponization": { ... },
    "Delivery": { ... },
    "Exploitation": { ... },
    "Installation": { ... },
    "Command & Control (C2)": { ... },
    "Actions on Objectives": { ... }
  },
  "projectId": "string (optional)",
  "sessionId": "string (optional)"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "response": "string",
    "suggestions": ["string"],
    "sessionId": "string"
  }
}
```

### Error Response Format

All endpoints should return consistent error responses:

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

**Common HTTP Status Codes:**
- `200 OK` - Success
- `201 Created` - Resource created successfully
- `400 Bad Request` - Invalid input
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Validation error
- `500 Internal Server Error` - Server error

### Data Validation

**Forecast Submission:**
- `name`: 3-200 characters
- `publisherName`: 2-100 characters
- `projectKeywords`: 1-500 characters
- `projectDescription`: 10-5000 characters

**Collaboration Submission:**
- `name`: 2-100 characters
- `email`: Valid email format
- `projectDescription`: 10-5000 characters
- `uploadedFile`: Max 10MB, allowed types: PDF, images (PNG, JPG, SVG)

**Builder Project Submission:**
- `name`: 3-200 characters
- `stageConfigurations`: Object with up to 7 kill chain stages, each containing:
  - `domainWeights`: Object with 5 domains (environment, economy, society, policy, technology) each 0-100, sum should be 100
  - `nlRuleInput`: Max 2000 characters
  - `importance`: 0-1 (float)
- `messageHistory`: Array of message objects (optional)
- Data files: Max 50MB, allowed types: CSV, Excel (.xlsx, .xls), JSON

### Real-time Features (Optional)

Consider implementing WebSocket endpoints for:
- Real-time forecast updates
- Live collaboration notifications
- Chat/messaging system

### CORS Configuration

Backend must allow CORS from:
- `http://localhost:5173` (development)
- `https://your-production-domain.com` (production)

## 🧪 Development

### Code Style
- ESLint configuration included
- Follow TypeScript best practices
- Use functional components with hooks

### Testing
```bash
npm run lint
```

### Environment Variables

Create a `.env` file:
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME=EU ForecastHUB
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎯 Roadmap

- [ ] Real-time collaboration features
- [ ] Advanced data visualization
- [ ] Export forecasts to various formats
- [ ] API rate limiting and quotas
- [ ] Community features (comments, ratings, discussions)
- [ ] Machine learning model integration
- [ ] Multi-language support
- [ ] Mobile responsive improvements
- [ ] Accessibility enhancements

## 📞 Support

For questions, issues, or contributions:
- GitHub Issues: [https://github.com/your-org/the-euforecast-hub/issues](https://github.com/your-org/the-euforecast-hub/issues)
- Email: support@euforecasthub.eu

## 🙏 Acknowledgments


- UI components from [shadcn/ui](https://ui.shadcn.com)
- Icons from [Lucide](https://lucide.dev)

---

**EU ForecastHUB** - Empowering evidence-based policy through open foresight.

