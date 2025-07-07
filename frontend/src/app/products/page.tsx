'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { 
  PlayIcon, 
  CubeIcon, 
  CloudIcon, 
  CpuChipIcon,
  SparklesIcon,
  RocketLaunchIcon,
  EyeIcon,
  MicrophoneIcon,
  FilmIcon,
  ArrowRightIcon,
  CheckIcon
} from '@heroicons/react/24/outline';

const products = [
  {
    icon: PlayIcon,
    title: 'AI Video Studio',
    description: 'Complete video generation suite with AI models, editing tools, and rendering pipeline',
    features: [
      'Text-to-video generation',
      'Image-to-video conversion',
      'Style transfer',
      'Video upscaling',
      'Batch processing'
    ],
    pricing: 'Starting at $99/month',
    popular: true
  },
  {
    icon: MicrophoneIcon,
    title: 'Voice Clone Pro',
    description: 'Advanced voice cloning and synthesis with lip-sync technology',
    features: [
      'High-fidelity voice cloning',
      'Multi-language support',
      'Real-time voice conversion',
      'Lip-sync generation',
      'Custom voice models'
    ],
    pricing: 'Starting at $149/month',
    popular: false
  },
  {
    icon: CubeIcon,
    title: '3D Render Engine',
    description: 'Professional 3D rendering and animation with GPU acceleration',
    features: [
      '3D scene generation',
      'Character animation',
      'Physics simulation',
      'Ray tracing',
      'VR/AR support'
    ],
    pricing: 'Starting at $199/month',
    popular: false
  },
  {
    icon: CloudIcon,
    title: 'Cloud Platform',
    description: 'Scalable cloud infrastructure for enterprise video processing',
    features: [
      'Auto-scaling compute',
      'Global CDN',
      'API management',
      'Real-time monitoring',
      'Enterprise security'
    ],
    pricing: 'Custom pricing',
    popular: false
  }
];

const integrations = [
  { name: 'Adobe Creative Suite', logo: '🎨' },
  { name: 'Blender', logo: '🎭' },
  { name: 'Unity', logo: '🎮' },
  { name: 'Unreal Engine', logo: '🚀' },
  { name: 'DaVinci Resolve', logo: '🎬' },
  { name: 'After Effects', logo: '✨' },
  { name: 'Premiere Pro', logo: '📹' },
  { name: 'Cinema 4D', logo: '🎪' }
];

export default function ProductsPage() {
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
              Our Products
            </h1>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              Comprehensive AI video tools designed for creators, developers, and enterprises
            </p>
          </motion.div>

          {/* Products Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-20">
            {products.map((product, index) => (
              <motion.div
                key={product.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className={`glass p-8 rounded-2xl hover:scale-105 transition-all duration-300 relative ${
                  product.popular ? 'ring-2 ring-navy-400' : ''
                }`}
              >
                {product.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <span className="bg-navy-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}
                
                <div className="flex items-center mb-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-navy-500 to-navy-700 rounded-lg flex items-center justify-center mr-4">
                    <product.icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-navy-800">
                      {product.title}
                    </h3>
                    <p className="text-navy-600 font-semibold">
                      {product.pricing}
                    </p>
                  </div>
                </div>

                <p className="text-navy-600 mb-6">
                  {product.description}
                </p>

                <ul className="space-y-3 mb-8">
                  {product.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center text-navy-700">
                      <CheckIcon className="w-5 h-5 text-navy-500 mr-3 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>

                <div className="flex space-x-4">
                  <Link
                    href="/get-started"
                    className="bg-navy-600 hover:bg-navy-700 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 hover:scale-105 flex items-center space-x-2 flex-1 justify-center"
                  >
                    <span>Get Started</span>
                    <ArrowRightIcon className="w-4 h-4" />
                  </Link>
                  <Link
                    href="/demo"
                    className="border border-navy-600 text-navy-700 hover:bg-navy-600 hover:text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center space-x-2"
                  >
                    <PlayIcon className="w-4 h-4" />
                    <span>Demo</span>
                  </Link>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Integrations Section */}
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
              Seamless Integrations
            </h2>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              Works with your favorite creative tools and workflows
            </p>
          </motion.div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {integrations.map((integration, index) => (
              <motion.div
                key={integration.name}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="glass p-6 rounded-lg text-center hover:scale-105 transition-all duration-300 cursor-pointer"
              >
                <div className="text-4xl mb-3">{integration.logo}</div>
                <h3 className="text-navy-700 font-medium">{integration.name}</h3>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Comparison */}
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
              Why Choose AI Empower Hub?
            </h2>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              Advanced features that set us apart from the competition
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <motion.div
              initial={{ opacity: 0, x: -30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6 }}
              viewport={{ once: true }}
              className="glass p-8 rounded-xl"
            >
              <CpuChipIcon className="w-12 h-12 text-navy-600 mb-4" />
              <h3 className="text-2xl font-bold text-navy-800 mb-4">
                GPU Acceleration
              </h3>
              <p className="text-navy-600">
                CUDA-optimized processing delivers 10x faster rendering compared to CPU-only solutions
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
              className="glass p-8 rounded-xl"
            >
              <SparklesIcon className="w-12 h-12 text-navy-600 mb-4" />
              <h3 className="text-2xl font-bold text-navy-800 mb-4">
                Real-time Processing
              </h3>
              <p className="text-navy-600">
                Live video generation and streaming capabilities for interactive applications
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
              viewport={{ once: true }}
              className="glass p-8 rounded-xl"
            >
              <CloudIcon className="w-12 h-12 text-navy-600 mb-4" />
              <h3 className="text-2xl font-bold text-navy-800 mb-4">
                Cloud Native
              </h3>
              <p className="text-navy-600">
                Built for cloud with auto-scaling, monitoring, and global deployment capabilities
              </p>
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
              Ready to Get Started?
            </h2>
            <p className="text-xl text-navy-600 mb-8 max-w-2xl mx-auto">
              Choose the perfect product for your needs and start creating amazing content today
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/get-started"
                className="bg-navy-600 hover:bg-navy-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200 hover:scale-105 pulse-glow"
              >
                Start Free Trial
              </Link>
              <Link
                href="/contact"
                className="border border-navy-600 text-navy-700 hover:bg-navy-600 hover:text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200"
              >
                Contact Sales
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
