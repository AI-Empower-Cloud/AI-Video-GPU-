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
  FilmIcon
} from '@heroicons/react/24/outline';

const features = [
  {
    icon: PlayIcon,
    title: 'AI Video Generation',
    description: 'Create stunning videos using cutting-edge AI models with GPU acceleration'
  },
  {
    icon: MicrophoneIcon,
    title: 'Voice Cloning',
    description: 'Clone voices with high fidelity for personalized video content'
  },
  {
    icon: EyeIcon,
    title: 'Lip Sync Technology',
    description: 'Perfect lip synchronization with advanced facial recognition'
  },
  {
    icon: FilmIcon,
    title: 'Video Composition',
    description: 'Professional video editing and composition tools'
  },
  {
    icon: CubeIcon,
    title: '3D Rendering',
    description: 'Advanced 3D graphics and rendering capabilities'
  },
  {
    icon: CloudIcon,
    title: 'Cloud Integration',
    description: 'Seamless cloud storage and processing with Wasabi S3'
  },
  {
    icon: CpuChipIcon,
    title: 'GPU Acceleration',
    description: 'Optimized for CUDA and high-performance computing'
  },
  {
    icon: SparklesIcon,
    title: 'Real-time Processing',
    description: 'Live video processing and streaming capabilities'
  }
];

const stats = [
  { value: '10x', label: 'Faster Processing' },
  { value: '99.9%', label: 'Uptime' },
  { value: '50+', label: 'AI Models' },
  { value: '1M+', label: 'Videos Generated' }
];

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative pt-32 pb-20 overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <motion.h1
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              className="text-5xl md:text-7xl font-bold gradient-text mb-8"
            >
              AI Empower Hub
            </motion.h1>
            
            <motion.p
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.2 }}
              className="text-xl md:text-2xl text-navy-700 mb-12 max-w-4xl mx-auto leading-relaxed"
            >
              Production-ready AI video generation platform with GPU acceleration, 
              voice cloning, lip sync, 3D rendering, and cloud integration
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8, delay: 0.4 }}
              className="flex flex-col sm:flex-row gap-4 justify-center items-center"
            >
              <Link
                href="/get-started"
                className="bg-navy-600 hover:bg-navy-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200 hover:scale-105 pulse-glow flex items-center space-x-2"
              >
                <RocketLaunchIcon className="w-5 h-5" />
                <span>Get Started Free</span>
              </Link>
              <Link
                href="/demo"
                className="glass border border-navy-300 text-navy-700 hover:text-navy-900 px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200 hover:scale-105 flex items-center space-x-2"
              >
                <PlayIcon className="w-5 h-5" />
                <span>Watch Demo</span>
              </Link>
            </motion.div>
          </div>

          {/* Floating Animation Elements */}
          <div className="absolute top-20 left-10 w-20 h-20 bg-navy-200 rounded-full opacity-30 float-animation"></div>
          <div className="absolute top-40 right-20 w-16 h-16 bg-navy-300 rounded-full opacity-40 float-animation" style={{ animationDelay: '2s' }}></div>
          <div className="absolute bottom-20 left-1/4 w-12 h-12 bg-navy-400 rounded-full opacity-50 float-animation" style={{ animationDelay: '4s' }}></div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.5 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center glass p-6 rounded-lg"
              >
                <div className="text-3xl md:text-4xl font-bold gradient-text mb-2">
                  {stat.value}
                </div>
                <div className="text-navy-600 font-medium">
                  {stat.label}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
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
              Powerful Features
            </h2>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              Everything you need to create, process, and deploy AI-generated videos at scale
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => (
              <motion.div
                key={feature.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="glass p-6 rounded-lg hover:scale-105 transition-all duration-300 cursor-pointer group"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-navy-500 to-navy-700 rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform duration-300">
                  <feature.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-navy-800 mb-3">
                  {feature.title}
                </h3>
                <p className="text-navy-600">
                  {feature.description}
                </p>
              </motion.div>
            ))}
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
              Ready to Create?
            </h2>
            <p className="text-xl text-navy-600 mb-8 max-w-2xl mx-auto">
              Join thousands of creators using AI Empower Hub to generate stunning content
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/get-started"
                className="bg-navy-600 hover:bg-navy-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200 hover:scale-105 pulse-glow"
              >
                Start Creating Now
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
