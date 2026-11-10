# Discord Bot Dashboard

A sleek, high-tech Discord bot management dashboard with a modern dark theme and real-time data visualization.

## Features

### 🎨 **Beautiful UI**
- Dark mode design with Discord-inspired aesthetics
- Glassmorphism effects and smooth animations
- Responsive design for desktop and mobile
- Custom color palette (Deep Obsidian, Slate Gray, Electric Purple, Neon Cyan)

### ⚡ **Bot Management**
- Real-time bot status monitoring
- Command control panel with search and filters
- User profile inspection and management
- Server statistics and analytics

### 📊 **Analytics**
- Command usage trends with real-time updates
- User growth statistics
- Performance metrics and resource monitoring
- Interactive charts and graphs

### 🛠 **Command Control**
- Interactive command cards with syntax highlighting
- Toggle switch for remote command enable/disable
- Execute command modal for quick testing
- Category-based filtering (Moderation, Utility, Music, Economy, etc.)

### 👤 **User Profiles**
- Discord-style user cards with avatars and badges
- Level and XP progress tracking
- Economy balance and activity logs
- Detailed user information panels

## Technology Stack

- **Framework**: Next.js (App Router) with React 18
- **Styling**: Tailwind CSS v4 with custom design system
- **Animations**: Framer Motion for smooth micro-interactions
- **Icons**: Lucide React for consistent icon set
- **Charts**: Recharts for data visualization
- **HTTP Client**: Express.js for API server (development)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/discord-bot-dashboard.git
cd discord-bot-dashboard
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Open your browser and navigate to:
   `http://localhost:3000`

## Project Structure

```
/discord-bot-dashboard
├── src/
│   ├── app/                    # Next.js App Router pages
│   │   ├── layout.tsx          # Main layout with sidebar
│   │   ├── page.tsx           # Dashboard page
│   │   └── ...                # Other pages
│   ├── components/             # React components
│   │   ├── sidebar.tsx        # Navigation sidebar
│   │   ├── command-control.tsx # Command management interface
│   │   ├── user-profile.tsx    # User profile viewer
│   │   ├── analytics.tsx       # Analytics dashboard
│   │   └── settings.tsx        # Settings page
│   ├── context/                # React contexts
│   │   └── app-context.tsx     # App state management
│   └── lib/                    # Utility functions
│       └── utils.tsx          # Helper utilities
├── public/                     # Static assets
│   └── index.html            # Main HTML entry point
├── package.json              # Project dependencies and scripts
├── package-lock.json         # Dependency lock file
├── tsconfig.json             # TypeScript configuration
└── .gitignore               # Git ignore file
```

## Key Components

### 1. Sidebar Navigation
- Dynamic bot status toggle (Online, Idle, DND, Offline)
- Navigation menu with Dashboard, Commands, Profiles, Analytics, Settings
- User profile preview with logout button

### 2. Command Control Panel
- Search bar with real-time filtering
- Category tabs for easy navigation
- Interactive command cards with toggles
- Execute command modal for testing

### 3. User Profile Viewer
- Discord-style user cards with avatars
- Level and XP progress bars with animations
- Economy balance and activity feeds
- Badge system for user achievements

### 4. Analytics Dashboard
- Command usage trends over time
- User growth statistics
- Performance metrics
- Interactive data visualizations

## Design Features

### Color Palette
- **Deep Obsidian**: `#0B0E14` - Background
- **Slate Gray**: `#161B22` - Cards
- **Electric Purple**: `#8B5CF6` - Accents
- **Neon Cyan**: `#06B6D4` - Highlights

### Typography
- **Inter / Geist**: Modern sans-serif fonts
- Clean, readable hierarchy
- Responsive text sizing

### Animations
- Smooth hover effects (tilt/scale 1.02x)
- Framer Motion page transitions
- Staggered fade-in animations
- Smooth accordions for content

### Glassmorphism
- Semi-transparent backgrounds
- Blur effects for depth
- Subtle border styling

## Development Tips

### Running the Development Server
```bash
# Start the local development server
npm run dev

# Build for production
npm run build

# Start the production server
npm start

# Run linting
npm run lint
```

### Browser Support
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Mobile Support
The dashboard is fully responsive and works on:
- Mobile devices (iOS and Android)
- Tablets
- Desktop computers

## API Integration

The dashboard includes a simple Express.js server for development:

- **GET `/api/bot/status`** - Get current bot status and metrics
- **GET `/api/commands`** - List all available commands
- **GET `/api/users`** - Get user data for profiles

## Customization

### Color Theme
To customize the color theme, modify the Tailwind configuration in `src/app/layout.tsx`:

```javascript
tailwindcss.config = {
    theme: {
        colors: {
            border: "hsl(var(--border))",
            input: "hsl(var(--input))",
            ring: "hsl(var(--ring))",
            background: "hsl(var(--background))",
            // Add your custom colors here
        },
    },
};
```

### Navigation Items
Edit the navigation menu in the sidebar component to add or remove pages.

### Command Categories
The command categories can be modified in the `command-control.tsx` component to add new filters.

## Performance

### Optimization
- Code splitting with Next.js App Router
- Automatic image optimization
- CSS purging with Tailwind
- Lazy loading for components

### Monitoring
- Real-time bot status updates
- Resource usage monitoring
- Command execution tracking

## Future Enhancements

### 🚀 Planned Features
1. **Real-time Updates**: WebSocket integration for live data
2. **Advanced Analytics**: Machine learning for usage patterns
3. **Multi-server Support**: Manage multiple Discord servers
4. **Custom Themes**: User-selectable color schemes
5. **Command Documentation**: Auto-generated command help
6. **API Keys**: Secure API key management
7. **Rate Limiting**: Configurable rate limits
8. **Command Templates**: Save and reuse command templates

## License

This project is licensed under the MIT License. See the `LICENSE` file for more information.

## Contributing

Contributions are welcome! Please follow the existing code style and add appropriate tests.

### Development Workflow
1. Create a new branch for your feature
2. Make your changes
3. Test locally
4. Create a pull request
5. Resolve any requested changes

## Support

For issues, questions, or support, please:
1. Check the documentation
2. Search existing issues
3. Create a new issue with detailed description
4. Provide screenshots if applicable

## Acknowledgements

Special thanks to:
- The open-source community for excellent libraries
- Discord developers for inspiring the UI/UX design
- All contributors who have made this project better

---

Built with ❤️ by your friendly neighborhood Discord bot manager
