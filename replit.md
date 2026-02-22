# Overview

This is a cyberpunk-themed authentication client application that acts as a frontend for interacting with an external Python authentication server. The app allows users to scan QR codes or manually enter challenge IDs to authenticate and logout against the external server, while logging all authentication attempts to its own internal PostgreSQL database.

The app has a single-page interface with a dark cyberpunk visual theme, featuring QR code scanning, configurable server URLs, and an activity log.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Frontend
- **Framework**: React 18 with TypeScript, bundled by Vite
- **Routing**: Wouter (lightweight React router) — single page at `/`, plus a 404 fallback
- **State Management**: TanStack React Query for server state (data fetching, caching, mutations)
- **UI Components**: shadcn/ui component library (new-york style) built on Radix UI primitives, styled with Tailwind CSS
- **Styling**: Tailwind CSS with CSS variables for theming. Dark cyberpunk color scheme using custom fonts (Share Tech Mono, Rajdhani). Custom components (`CyberButton`, `CyberInput`) extend the design system
- **Animations**: Framer Motion for page transitions and UI effects
- **QR Scanning**: `@yudiel/react-qr-scanner` for camera-based QR code input
- **Path Aliases**: `@/` maps to `client/src/`, `@shared/` maps to `shared/`

### Backend
- **Framework**: Express.js running on Node.js with TypeScript (executed via `tsx`)
- **API Pattern**: RESTful JSON API under `/api/` prefix
- **Routes**: Only two endpoints defined:
  - `GET /api/logs` — list all authentication logs
  - `POST /api/logs` — create a new authentication log entry
- **Validation**: Zod schemas for request validation, with drizzle-zod generating schemas from database tables
- **Shared Contract**: `shared/routes.ts` defines the API contract (paths, methods, input/output schemas) used by both client and server

### Data Storage
- **Database**: PostgreSQL via `DATABASE_URL` environment variable
- **ORM**: Drizzle ORM with `drizzle-kit` for schema management (`db:push` command)
- **Schema**: Single table `auth_logs` with fields: `id` (serial), `challenge_id` (text), `action` (text: 'authenticate' or 'logout'), `timestamp` (auto-set)
- **Storage Layer**: `server/storage.ts` implements a `DatabaseStorage` class behind an `IStorage` interface for clean abstraction

### Build System
- **Development**: Vite dev server with HMR, proxied through Express middleware (`server/vite.ts`)
- **Production Build**: Two-step process via `script/build.ts` — Vite builds the client to `dist/public/`, esbuild bundles the server to `dist/index.cjs`. Frequently-used server dependencies are bundled (not externalized) to reduce cold start times
- **Static Serving**: In production, Express serves the built client files from `dist/public/` with SPA fallback to `index.html`

### Key Design Decisions
- **External auth server separation**: The actual authentication logic lives in a separate Python server (default `http://localhost:8000`). This app is just the UI client and log keeper. The server URL is configurable through the Settings dialog
- **Shared schema pattern**: Database schema and API route definitions live in `shared/` directory, imported by both client and server to ensure type safety across the stack
- **No built-in authentication**: The app itself has no user auth — it's a tool that sends requests to an external auth server

## External Dependencies

- **PostgreSQL Database**: Required, configured via `DATABASE_URL` environment variable. Used for storing authentication attempt logs
- **External Python Authentication Server**: Expected at `http://localhost:8000` by default (configurable in the UI). Endpoints called:
  - `POST /authenticate` — sends `challengeId` and `userId`
  - `POST /logout` — sends `challengeId` and `userId`
- **Google Fonts**: Loaded externally for Share Tech Mono, Rajdhani, DM Sans, Fira Code, Geist Mono, and Architects Daughter typefaces
- **Replit Plugins** (dev only): `@replit/vite-plugin-runtime-error-modal`, `@replit/vite-plugin-cartographer`, `@replit/vite-plugin-dev-banner` — active only in development on Replit