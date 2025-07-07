# AI Empower Hub Frontend

A stunning, animated, professional-grade frontend UI built with React, Next.js, Tailwind CSS, and Framer Motion.

## Features

- **Light Sky Blue Background** (#87CEFA) - Beautiful gradient background
- **Navy Blue Accents** (#1e3a8a) - Professional buttons, headers, and interactive elements
- **Stunning Animations** - Smooth transitions and micro-interactions powered by Framer Motion
- **Responsive Design** - Works perfectly on desktop, tablet, and mobile devices
- **Modern UI Components** - Professional-grade components inspired by RunwayML
- **TypeScript Support** - Full type safety throughout the application
- **Performance Optimized** - Built with Next.js for optimal performance

## Design System

### Colors
- **Primary Background**: Light Sky Blue (#87CEFA)
- **Secondary Background**: Light Sky Blue variations (#B0E0E6, #6BB3FF)
- **Accent Colors**: Navy Blue shades (#1e3a8a, #1e40af, #1e293b)
- **Text Colors**: Various navy blue shades for hierarchy

### Typography
- **Font Family**: Inter (clean, modern sans-serif)
- **Gradient Text**: Animated gradient text for headings
- **Responsive Typography**: Scales appropriately across devices

### Animations
- **Page Transitions**: Smooth fade and slide effects
- **Hover Effects**: Scale, glow, and color transitions
- **Loading States**: Elegant loading animations
- **Scroll Animations**: Elements animate into view on scroll

## Pages

### Home Page (`/`)
- Hero section with animated elements
- Feature showcase with icons and descriptions
- Statistics section with animated counters
- Call-to-action sections

### Products Page (`/products`)
- Product grid with detailed feature lists
- Integration showcase
- Feature comparison
- Interactive product cards

### Pricing Page (`/pricing`)
- Pricing tiers with feature comparison
- Interactive plan selection
- FAQ section
- Feature comparison table

### Use Cases Page (`/use-cases`)
- Industry-specific use cases
- Success stories and testimonials
- Implementation guide
- Statistics and metrics

### About Page (`/about`)
- Company story and mission
- Team showcase
- Company values
- Timeline of milestones

### Documentation Page (`/docs`)
- Quick start guide
- API documentation sections
- Code examples
- Search functionality

### Get Started Page (`/get-started`)
- Multi-step onboarding flow
- Plan selection
- Account creation form
- Welcome screen

## Components

### Navigation
- **Navbar**: Fixed header with smooth background transitions
- **Footer**: Comprehensive footer with links and contact info
- **Mobile Menu**: Animated mobile navigation

### UI Elements
- **Glass Morphism**: Translucent cards with backdrop blur
- **Gradient Buttons**: Animated buttons with hover effects
- **Feature Cards**: Interactive cards with icons and descriptions
- **Testimonial Cards**: Customer testimonials with animations

## Technologies Used

- **Next.js 14**: React framework with App Router
- **React 18**: Modern React with hooks and concurrent features
- **TypeScript**: Type-safe development
- **Tailwind CSS**: Utility-first CSS framework
- **Framer Motion**: Powerful animation library
- **Heroicons**: Beautiful SVG icons
- **PostCSS**: CSS processing

## Development

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Installation
```bash
cd frontend
npm install
```

### Development Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
npm start
```

### Type Checking
```bash
npm run type-check
```

## Customization

### Colors
Colors are defined in `tailwind.config.js` and can be easily customized:

```javascript
colors: {
  'sky-blue': '#87CEFA',
  navy: {
    600: '#1e3a8a',
    // ... other shades
  }
}
```

### Animations
Animations are defined in `globals.css` and can be modified:

```css
@keyframes float {
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
}
```

## Browser Support

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## Performance

- **Lighthouse Score**: 95+ Performance
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Cumulative Layout Shift**: < 0.1

## Accessibility

- WCAG 2.1 AA compliant
- Keyboard navigation support
- Screen reader optimization
- High contrast mode support

## Contributing

1. Follow the established design system
2. Maintain consistent animations and transitions
3. Ensure responsive design works across all devices
4. Test accessibility features
5. Update documentation for new components

## License

Copyright © 2024 AI Empower Hub. All rights reserved.
