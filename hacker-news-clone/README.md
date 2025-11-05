# Hacker News Clone

A full-featured Hacker News clone built with modern web technologies, demonstrating a production-ready application with real-time features, authentication, and a comprehensive ranking algorithm.

## Features

### Core Functionality
- **Story Submission**: Submit links or text posts with duplicate URL detection
- **Nested Comments**: Unlimited comment threading with materialized path storage (max depth: 10)
- **Voting System**: Weighted voting based on user karma
- **Ranking Algorithm**: Hacker News-style ranking with time decay and penalties
- **User Profiles**: Karma system, user submissions, and comment history
- **Real-time Updates**: WebSocket support for live vote counts and new comments
- **Authentication**: JWT-based auth with refresh tokens and account lockout

### Advanced Features
- **Multiple Story Types**: story, ask, show, job, poll
- **Different Sorting**: top (ranked), new (chronological), best (Wilson score)
- **Saved Items**: Save stories and comments for later
- **Edit Window**: 2-hour edit window for posts and comments
- **Rate Limiting**: Prevents spam and abuse
- **Redis Caching**: Performance optimization with cache invalidation
- **Responsive Design**: Mobile-first design with Tailwind CSS
- **TypeScript**: Full type safety across the application

## Tech Stack

### Backend
- **Runtime**: Node.js 18+
- **Framework**: Express.js
- **Database**: PostgreSQL 14
- **Cache**: Redis 7
- **Authentication**: JWT (jsonwebtoken)
- **Real-time**: Socket.IO
- **Security**: Helmet, bcrypt, sanitize-html, express-rate-limit

### Frontend
- **Framework**: Next.js 15 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **HTTP Client**: Axios
- **Real-time**: Socket.IO Client
- **Utilities**: date-fns, DOMPurify, marked

## Project Structure

```
hacker-news-clone/
├── backend/
│   ├── src/
│   │   ├── config/          # Database and Redis configuration
│   │   ├── controllers/     # Request handlers
│   │   ├── middleware/      # Auth, rate limiting, etc.
│   │   ├── models/          # Data models
│   │   ├── routes/          # API routes
│   │   ├── services/        # Business logic (WebSocket, etc.)
│   │   ├── utils/           # Utilities and helpers
│   │   └── server.js        # Express app entry point
│   ├── migrations/          # Database migrations
│   ├── tests/               # Unit and integration tests
│   └── package.json
├── frontend/
│   ├── app/                 # Next.js app directory
│   │   ├── (pages)/         # Route pages
│   │   ├── layout.tsx       # Root layout
│   │   └── globals.css      # Global styles
│   ├── components/          # React components
│   │   ├── common/          # Reusable components
│   │   ├── comments/        # Comment components
│   │   ├── layout/          # Layout components
│   │   ├── providers/       # Context providers
│   │   └── stories/         # Story components
│   ├── lib/                 # Libraries and utilities
│   │   ├── api/             # API client
│   │   ├── store/           # Zustand stores
│   │   └── utils/           # Helper functions
│   ├── types/               # TypeScript types
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Database Schema

### Users
- Authentication with password hashing (bcrypt)
- Karma tracking
- Account lockout after failed login attempts
- Email verification support
- Moderator and shadowban flags

### Stories
- Support for URL or text content (not both)
- Auto-domain extraction
- Soft delete
- Comment count tracking
- Story type classification

### Comments
- Hierarchical structure with materialized path
- Depth tracking (max 10 levels)
- Parent-child relationships
- Soft delete (preserves thread structure)

### Votes
- Weighted voting based on karma
- Unique constraint (one vote per user per item)
- Separate tracking for stories and comments

### Saved Items
- Bookmark stories and comments
- User-specific

## API Endpoints

### Authentication
```
POST   /api/auth/register      - Register new user
POST   /api/auth/login         - Login
POST   /api/auth/logout        - Logout
POST   /api/auth/refresh       - Refresh token
GET    /api/auth/me            - Get current user
```

### Stories
```
GET    /api/stories                    - List stories (with filters)
GET    /api/stories/:id                - Get story details
POST   /api/stories                    - Create story
PUT    /api/stories/:id                - Update story
DELETE /api/stories/:id                - Delete story
POST   /api/stories/:id/vote           - Vote on story
DELETE /api/stories/:id/vote           - Unvote story
POST   /api/stories/:id/save           - Toggle save story
```

### Comments
```
GET    /api/stories/:storyId/comments  - Get all comments for story
POST   /api/stories/:storyId/comments  - Create comment
PUT    /api/comments/:id               - Update comment
DELETE /api/comments/:id               - Delete comment
GET    /api/comments/:id/thread        - Get comment thread
POST   /api/comments/:id/vote          - Vote on comment
DELETE /api/comments/:id/vote          - Unvote comment
POST   /api/comments/:id/save          - Toggle save comment
```

### Users
```
GET    /api/users/:username            - Get user profile
PUT    /api/users/:username            - Update profile
GET    /api/users/:username/saved      - Get saved items
GET    /api/users/:username/submissions - Get user submissions
GET    /api/users/:username/comments   - Get user comments
```

## Setup and Installation

### Prerequisites
- Node.js 18+ and npm
- PostgreSQL 14+
- Redis 7+
- Docker and Docker Compose (optional)

### Option 1: Docker Compose (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd hacker-news-clone
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

3. **Start all services**
   ```bash
   docker-compose up -d
   ```

4. **Initialize the database**
   ```bash
   docker-compose exec backend npm run migrate
   ```

5. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:3000
   - Health Check: http://localhost:3000/health

### Option 2: Manual Setup

1. **Set up PostgreSQL**
   ```bash
   createdb hn_clone
   psql hn_clone < backend/migrations/init.sql
   ```

2. **Set up Redis**
   ```bash
   redis-server
   ```

3. **Install backend dependencies**
   ```bash
   cd backend
   npm install
   cp ../.env.example .env
   # Edit .env with your configuration
   npm run dev
   ```

4. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

## Environment Variables

See `.env.example` for all configuration options. Key variables:

```bash
# Backend
DATABASE_URL=postgresql://user:pass@localhost:5432/hn_clone
REDIS_URL=redis://localhost:6379
JWT_SECRET=your-secret-key
PORT=3000

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:3000
NEXT_PUBLIC_WS_URL=ws://localhost:3000
```

## Development

### Backend Development
```bash
cd backend
npm run dev          # Start with nodemon
npm run test         # Run tests
npm run test:unit    # Run unit tests only
npm run lint         # Run ESLint
```

### Frontend Development
```bash
cd frontend
npm run dev          # Start Next.js dev server
npm run build        # Build for production
npm run lint         # Run ESLint
```

## Testing

### Backend Tests
```bash
cd backend
npm run test         # Run all tests with coverage
npm run test:unit    # Unit tests only
npm run test:integration  # Integration tests only
```

### Frontend Tests
```bash
cd frontend
npm test             # Run Jest tests
```

## Algorithms

### Ranking Algorithm (Hacker News Style)
```
Score = (P - 1)^0.8 / (T + 2)^1.8 × Penalties

Where:
- P = points (upvotes)
- T = time since submission (hours)
- Penalties:
  - Paywall domain: 0.5×
  - New user (karma < 100): 0.8×
  - Controversial (comments >> votes): 0.7×
```

### Vote Weight Calculation
```
Weight = min(1 + log10(karma/100), 3)

Results:
- 0-99 karma: 1.0× weight
- 100 karma: 1.0× weight
- 1000 karma: 1.3× weight
- 10000 karma: 1.6× weight
- 100000+ karma: 3.0× weight (capped)
```

### Best Score (Wilson Score Confidence Interval)
Used for "best" sorting, accounting for both quality and quantity of engagement.

## Security Features

- **Password Hashing**: bcrypt with 10 rounds
- **JWT Authentication**: Secure token-based auth
- **Rate Limiting**: Prevents abuse
  - Stories: 5/hour
  - Comments: 30/hour
  - Votes: 100/hour
  - Auth: 10 attempts/15 minutes
- **Account Lockout**: 5 failed login attempts = 15 min lock
- **Input Sanitization**: HTML sanitization on all user content
- **SQL Injection Prevention**: Parameterized queries
- **XSS Protection**: Content Security Policy headers
- **CSRF Protection**: Token validation

## Performance Optimizations

- **Redis Caching**: Cache stories, comments, user profiles
- **Database Indexing**: Optimized queries with proper indexes
- **Connection Pooling**: PostgreSQL connection pool (max 20)
- **Compression**: gzip compression on responses
- **Pagination**: Limit results to prevent large data transfers
- **Lazy Loading**: Comments and stories loaded on demand

## Deployment

### Production Build
```bash
# Backend
cd backend
npm install --production
npm start

# Frontend
cd frontend
npm run build
npm start
```

### Docker Production
```bash
docker-compose -f docker-compose.prod.yml up -d
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - feel free to use this project for learning or as a foundation for your own applications.

## Acknowledgments

- Inspired by [Hacker News](https://news.ycombinator.com/)
- Ranking algorithm based on HN's public algorithm documentation
- Built as a demonstration of modern web development practices
