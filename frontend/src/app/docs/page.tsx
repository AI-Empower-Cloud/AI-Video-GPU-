'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { 
  DocumentTextIcon,
  CodeBracketIcon,
  CpuChipIcon,
  CloudIcon,
  PlayIcon,
  CogIcon,
  ShieldCheckIcon,
  QuestionMarkCircleIcon,
  BookOpenIcon,
  RocketLaunchIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

const documentationSections = [
  {
    icon: RocketLaunchIcon,
    title: 'Getting Started',
    description: 'Quick start guide to begin creating AI videos',
    items: [
      'Installation & Setup',
      'First Video Generation',
      'Basic Configuration',
      'Authentication'
    ],
    link: '/docs/getting-started'
  },
  {
    icon: CodeBracketIcon,
    title: 'API Reference',
    description: 'Complete API documentation with examples',
    items: [
      'REST API Endpoints',
      'Authentication',
      'Rate Limiting',
      'Error Handling'
    ],
    link: '/docs/api'
  },
  {
    icon: CpuChipIcon,
    title: 'AI Models',
    description: 'Available AI models and their capabilities',
    items: [
      'Text-to-Video Models',
      'Image-to-Video Models',
      'Voice Cloning Models',
      'Model Performance'
    ],
    link: '/docs/models'
  },
  {
    icon: CloudIcon,
    title: 'Cloud Integration',
    description: 'Cloud deployment and scaling guides',
    items: [
      'Docker Deployment',
      'Kubernetes Setup',
      'Wasabi S3 Integration',
      'Auto-scaling'
    ],
    link: '/docs/cloud'
  },
  {
    icon: CogIcon,
    title: 'Configuration',
    description: 'System configuration and customization',
    items: [
      'Environment Variables',
      'GPU Configuration',
      'Performance Tuning',
      'Custom Models'
    ],
    link: '/docs/configuration'
  },
  {
    icon: ShieldCheckIcon,
    title: 'Security',
    description: 'Security best practices and guidelines',
    items: [
      'Authentication Methods',
      'Data Encryption',
      'Access Control',
      'Compliance'
    ],
    link: '/docs/security'
  }
];

const quickLinks = [
  { title: 'API Keys', description: 'Manage your API credentials', link: '/docs/api-keys' },
  { title: 'Rate Limits', description: 'Understanding API limits', link: '/docs/rate-limits' },
  { title: 'Webhooks', description: 'Real-time event notifications', link: '/docs/webhooks' },
  { title: 'SDKs', description: 'Official client libraries', link: '/docs/sdks' },
  { title: 'Examples', description: 'Code examples and tutorials', link: '/docs/examples' },
  { title: 'Troubleshooting', description: 'Common issues and solutions', link: '/docs/troubleshooting' }
];

const codeExample = `import { AIVideoGPU } from '@aivideogpu/sdk';

const client = new AIVideoGPU({
  apiKey: 'your-api-key-here'
});

// Generate a video from text
const video = await client.generateVideo({
  prompt: 'A beautiful sunset over the ocean',
  model: 'text-to-video-v1',
  duration: 10,
  resolution: '1920x1080'
});

console.log('Video URL:', video.url);`;

export default function DocsPage() {
  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h1 className="text-5xl md:text-6xl font-bold gradient-text mb-6">
              Documentation
            </h1>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              Everything you need to integrate and use AI Empower Hub in your projects
            </p>
          </motion.div>

          {/* Search Bar */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="max-w-2xl mx-auto mb-16"
          >
            <div className="relative">
              <input
                type="text"
                placeholder="Search documentation..."
                className="w-full px-6 py-4 glass rounded-lg border border-navy-300 focus:border-navy-500 focus:outline-none text-navy-700 placeholder-navy-400"
              />
              <button className="absolute right-4 top-1/2 transform -translate-y-1/2">
                <svg className="w-5 h-5 text-navy-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
            </div>
          </motion.div>
        </div>
      </section>

      {/* Quick Start */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold gradient-text mb-6">
              Quick Start
            </h2>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              Get up and running in minutes with our simple API
            </p>
          </motion.div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="glass p-8 rounded-xl"
            >
              <h3 className="text-2xl font-bold text-navy-800 mb-6">
                Installation
              </h3>
              <div className="bg-navy-900 rounded-lg p-4 mb-6">
                <code className="text-green-400 font-mono text-sm">
                  npm install @aivideogpu/sdk
                </code>
              </div>
              <div className="bg-navy-900 rounded-lg p-4">
                <code className="text-green-400 font-mono text-sm">
                  pip install aivideogpu
                </code>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
              className="glass p-8 rounded-xl"
            >
              <h3 className="text-2xl font-bold text-navy-800 mb-6">
                Example Code
              </h3>
              <div className="bg-navy-900 rounded-lg p-4 overflow-x-auto">
                <pre className="text-green-400 font-mono text-sm whitespace-pre-wrap">
                  {codeExample}
                </pre>
              </div>
            </motion.div>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            viewport={{ once: true }}
            className="text-center"
          >
            <Link
              href="/docs/getting-started"
              className="bg-navy-600 hover:bg-navy-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200 hover:scale-105 pulse-glow inline-flex items-center space-x-2"
            >
              <BookOpenIcon className="w-5 h-5" />
              <span>View Full Tutorial</span>
              <ArrowRightIcon className="w-4 h-4" />
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Documentation Sections */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold gradient-text mb-6">
              Documentation Sections
            </h2>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              Comprehensive guides for every aspect of AI Empower Hub
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {documentationSections.map((section, index) => (
              <motion.div
                key={section.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="glass p-6 rounded-lg hover:scale-105 transition-all duration-300 group cursor-pointer"
              >
                <Link href={section.link} className="block">
                  <div className="w-12 h-12 bg-gradient-to-br from-navy-500 to-navy-700 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                    <section.icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-navy-800 mb-3">
                    {section.title}
                  </h3>
                  <p className="text-navy-600 mb-4">
                    {section.description}
                  </p>
                  <ul className="space-y-2">
                    {section.items.map((item, itemIndex) => (
                      <li key={itemIndex} className="flex items-center text-navy-500 text-sm">
                        <div className="w-1.5 h-1.5 bg-navy-400 rounded-full mr-2"></div>
                        {item}
                      </li>
                    ))}
                  </ul>
                  <div className="flex items-center text-navy-600 mt-4 group-hover:text-navy-800 transition-colors">
                    <span className="text-sm font-medium">Read more</span>
                    <ArrowRightIcon className="w-4 h-4 ml-1" />
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Quick Links */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold gradient-text mb-6">
              Quick Links
            </h2>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              Frequently accessed documentation pages
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {quickLinks.map((link, index) => (
              <motion.div
                key={link.title}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.05 }}
                viewport={{ once: true }}
              >
                <Link
                  href={link.link}
                  className="glass p-4 rounded-lg hover:scale-105 transition-all duration-300 block group"
                >
                  <h3 className="text-lg font-semibold text-navy-800 mb-2 group-hover:text-navy-900">
                    {link.title}
                  </h3>
                  <p className="text-navy-600 text-sm">
                    {link.description}
                  </p>
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Support Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="glass p-8 rounded-xl"
            >
              <QuestionMarkCircleIcon className="w-12 h-12 text-navy-600 mb-4" />
              <h3 className="text-3xl font-bold gradient-text mb-6">
                Need Help?
              </h3>
              <p className="text-navy-600 text-lg mb-6">
                Can't find what you're looking for? Our support team is here to help.
              </p>
              <div className="space-y-4">
                <Link
                  href="/help"
                  className="block w-full bg-navy-600 hover:bg-navy-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 text-center"
                >
                  Visit Help Center
                </Link>
                <Link
                  href="/contact"
                  className="block w-full border border-navy-600 text-navy-700 hover:bg-navy-600 hover:text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 text-center"
                >
                  Contact Support
                </Link>
              </div>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
              className="glass p-8 rounded-xl"
            >
              <BookOpenIcon className="w-12 h-12 text-navy-600 mb-4" />
              <h3 className="text-3xl font-bold gradient-text mb-6">
                Community
              </h3>
              <p className="text-navy-600 text-lg mb-6">
                Join our community of developers and creators sharing knowledge and best practices.
              </p>
              <div className="space-y-4">
                <Link
                  href="/community"
                  className="block w-full bg-navy-600 hover:bg-navy-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 text-center"
                >
                  Join Community
                </Link>
                <Link
                  href="/blog"
                  className="block w-full border border-navy-600 text-navy-700 hover:bg-navy-600 hover:text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 text-center"
                >
                  Read Blog
                </Link>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            whileInView={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="glass p-12 rounded-2xl text-center"
          >
            <h2 className="text-4xl md:text-5xl font-bold gradient-text mb-6">
              Ready to Build?
            </h2>
            <p className="text-xl text-navy-600 mb-8 max-w-2xl mx-auto">
              Start integrating AI Empower Hub into your applications today
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/get-started"
                className="bg-navy-600 hover:bg-navy-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200 hover:scale-105 pulse-glow flex items-center space-x-2 justify-center"
              >
                <PlayIcon className="w-5 h-5" />
                <span>Get API Keys</span>
              </Link>
              <Link
                href="/docs/examples"
                className="border border-navy-600 text-navy-700 hover:bg-navy-600 hover:text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200"
              >
                View Examples
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
