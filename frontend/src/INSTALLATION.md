# Installation Guide

## Prerequisites

- Node.js 20.x or later
- npm or yarn package manager
- Docker (optional, for containerized deployment)

## Local Development Setup

### 1. Install Dependencies

Run the following command to install all required packages:

```bash
npm install
```

This will install:

**Core Dependencies:**
- React 18.2.0 and React DOM
- TypeScript 5.0.0

**UI Component Libraries:**
- All Radix UI primitives (accordion, alert-dialog, avatar, checkbox, dialog, dropdown-menu, etc.)
- Lucide React (icons)
- Recharts (charts and graphs)
- Sonner (toast notifications)

**Utility Libraries:**
- class-variance-authority (CVA for component variants)
- clsx & tailwind-merge (class name utilities)
- date-fns (date utilities)
- vaul (drawer component)
- cmdk (command palette)
- react-day-picker (calendar)
- react-hook-form (forms)
- react-resizable-panels (resizable layouts)
- embla-carousel-react (carousel)
- input-otp (OTP inputs)

**Styling:**
- Tailwind CSS 4.0
- @tailwindcss/vite plugin

### 2. Start Development Server

```bash
npm run dev
```

The application will be available at `http://localhost:5173`

### 3. Build for Production

```bash
npm run build
```

This creates an optimized production build in the `dist` folder.

### 4. Preview Production Build

```bash
npm run preview
```

## Docker Deployment

### Build the Docker Image

```bash
docker build -t document-management-app .
```

### Run the Container

```bash
docker run -p 3000:3000 document-management-app
```

The application will be available at `http://localhost:3000`

### Using Docker Compose

If you have a `docker-compose.yml` file:

```bash
docker-compose up
```

## Troubleshooting

### Issue: Styles not loading

**Solution:** Make sure Tailwind CSS is installed and the Vite plugin is configured in `vite.config.ts`:

```typescript
import tailwindcss from '@tailwindcss/vite';

export default defineConfig({
  plugins: [react(), tailwindcss()],
  // ...
});
```

### Issue: Module not found errors

**Solution:** Delete `node_modules` and reinstall:

```bash
rm -rf node_modules package-lock.json
npm install
```

### Issue: Radix UI components not rendering

**Solution:** Ensure all @radix-ui packages are installed. Check the package.json dependencies section.

### Issue: TypeScript errors

**Solution:** Make sure TypeScript is installed and tsconfig.json is properly configured.

## Component Library Overview

The application uses shadcn/ui components located in `/components/ui`:

- **Accordion** - Expandable content sections
- **Alert Dialog** - Modal confirmations
- **Avatar** - User profile images
- **Button** - Interactive buttons with variants
- **Calendar** - Date picker
- **Card** - Content containers
- **Carousel** - Image/content sliders
- **Chart** - Data visualizations using Recharts
- **Checkbox** - Form checkboxes
- **Dialog** - Modal dialogs
- **Dropdown Menu** - Context menus
- **Form** - Form components with validation
- **Input** - Text input fields
- **Select** - Dropdown selects
- **Table** - Data tables
- **Tabs** - Tabbed interfaces
- **Textarea** - Multi-line text inputs
- **Toast (Sonner)** - Notification messages
- **Tooltip** - Hover tooltips
- And many more...

## Application Structure

```
/
├── App.tsx                 # Main application component
├── main.tsx               # Application entry point
├── components/
│   ├── ui/               # Shadcn UI components
│   ├── AdminDashboard.tsx
│   ├── Dashboard.tsx
│   ├── DocumentChat.tsx
│   ├── DocumentCompare.tsx
│   ├── DocumentList.tsx
│   ├── DocumentUpload.tsx
│   ├── Login.tsx
│   └── Navbar.tsx
├── context/
│   ├── AuthContext.tsx
│   └── DocumentContext.tsx
├── styles/
│   └── globals.css        # Global styles and Tailwind config
└── vite.config.ts         # Vite configuration
```

## Environment Variables

Currently, the application uses mock data and doesn't require environment variables. If you want to add real API integrations, create a `.env` file:

```env
VITE_API_URL=your_api_url_here
VITE_SUPABASE_URL=your_supabase_url
VITE_SUPABASE_ANON_KEY=your_supabase_key
```

## Features

- **Authentication System** - Login with admin/user role support
- **Document Upload** - Upload and manage PDF, DOCX, TXT files
- **AI Chat** - Chat with uploaded documents
- **Document Comparison** - Compare multiple documents
- **Document Summarization** - Generate summaries
- **Admin Dashboard** - User management and analytics (admin only)
- **Responsive Design** - Works on desktop and mobile devices

## Support

For issues or questions, please check the documentation or create an issue in the repository.
