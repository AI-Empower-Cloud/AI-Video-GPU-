'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { 
  FilmIcon,
  MegaphoneIcon,
  AcademicCapIcon,
  BuildingStorefrontIcon,
  PlayIcon,
  UserGroupIcon,
  DocumentTextIcon,
  GlobeAltIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline';

const useCases = [
  {
    icon: FilmIcon,
    title: 'Content Creation',
    description: 'Create engaging videos for social media, YouTube, and marketing campaigns',
    benefits: [
      'Automated video generation from scripts',
      'Brand-consistent visual style',
      'Multiple format outputs',
      'Batch content creation'
    ],
    industry: 'Media & Entertainment',
    testimonial: '"AI Empower Hub helped us scale our content production by 500% while maintaining quality."',
    author: 'Sarah Chen, Creative Director'
  },
  {
    icon: MegaphoneIcon,
    title: 'Marketing & Advertising',
    description: 'Generate personalized video ads and marketing content at scale',
    benefits: [
      'Personalized video campaigns',
      'A/B testing multiple variants',
      'Voice-over in multiple languages',
      'Real-time campaign optimization'
    ],
    industry: 'Marketing & Advertising',
    testimonial: '"Our conversion rates increased by 40% using personalized AI-generated video ads."',
    author: 'Marcus Rodriguez, CMO'
  },
  {
    icon: AcademicCapIcon,
    title: 'Education & Training',
    description: 'Create interactive educational content and training materials',
    benefits: [
      'Personalized learning experiences',
      'Multi-language support',
      'Interactive demonstrations',
      'Scalable training content'
    ],
    industry: 'Education',
    testimonial: '"Students are 60% more engaged with AI-generated educational videos."',
    author: 'Dr. Emily Watson, University Professor'
  },
  {
    icon: BuildingStorefrontIcon,
    title: 'E-commerce',
    description: 'Generate product demonstrations and shopping experiences',
    benefits: [
      'Automated product videos',
      'Virtual try-on experiences',
      'Personalized recommendations',
      'Multi-platform optimization'
    ],
    industry: 'Retail & E-commerce',
    testimonial: '"Product videos increased our conversion rates by 35% and reduced returns by 20%."',
    author: 'Lisa Park, E-commerce Manager'
  },
  {
    icon: UserGroupIcon,
    title: 'Corporate Communications',
    description: 'Internal communications, announcements, and training videos',
    benefits: [
      'Executive message delivery',
      'Company-wide announcements',
      'HR training materials',
      'Multi-language support'
    ],
    industry: 'Corporate',
    testimonial: '"Our employee engagement scores improved significantly with video communications."',
    author: 'James Wilson, Head of Internal Comms'
  },
  {
    icon: GlobeAltIcon,
    title: 'Gaming & Virtual Worlds',
    description: 'Create immersive gaming content and virtual experiences',
    benefits: [
      'NPC character generation',
      'Cinematic cutscenes',
      'Virtual world creation',
      'Real-time avatar animation'
    ],
    industry: 'Gaming & VR',
    testimonial: '"AI Empower Hub revolutionized our game development pipeline and cut costs by 50%."',
    author: 'Alex Kim, Game Director'
  }
];

const industries = [
  { name: 'Media & Entertainment', count: '2.5K+', icon: '🎬' },
  { name: 'Marketing & Advertising', count: '3.8K+', icon: '📢' },
  { name: 'Education', count: '1.9K+', icon: '🎓' },
  { name: 'E-commerce', count: '4.2K+', icon: '🛍️' },
  { name: 'Gaming', count: '1.3K+', icon: '🎮' },
  { name: 'Healthcare', count: '850+', icon: '🏥' },
  { name: 'Real Estate', count: '2.1K+', icon: '🏢' },
  { name: 'Finance', count: '1.7K+', icon: '💰' }
];

export default function UseCasesPage() {
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
              Use Cases
            </h1>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              Discover how AI Empower Hub is transforming industries and empowering creators worldwide
            </p>
          </motion.div>

          {/* Industries Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-20">
            {industries.map((industry, index) => (
              <motion.div
                key={industry.name}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="glass p-4 rounded-lg text-center hover:scale-105 transition-all duration-300"
              >
                <div className="text-2xl mb-2">{industry.icon}</div>
                <div className="text-2xl font-bold gradient-text mb-1">
                  {industry.count}
                </div>
                <div className="text-sm text-navy-600">
                  {industry.name}
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Use Cases Grid */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-12">
            {useCases.map((useCase, index) => (
              <motion.div
                key={useCase.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="glass p-8 rounded-2xl hover:scale-105 transition-all duration-300"
              >
                <div className="flex items-center mb-6">
                  <div className="w-12 h-12 bg-gradient-to-br from-navy-500 to-navy-700 rounded-lg flex items-center justify-center mr-4">
                    <useCase.icon className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h3 className="text-2xl font-bold text-navy-800">
                      {useCase.title}
                    </h3>
                    <span className="text-sm text-navy-500 bg-navy-100 px-3 py-1 rounded-full">
                      {useCase.industry}
                    </span>
                  </div>
                </div>

                <p className="text-navy-600 mb-6">
                  {useCase.description}
                </p>

                <div className="mb-6">
                  <h4 className="text-lg font-semibold text-navy-800 mb-3">
                    Key Benefits:
                  </h4>
                  <ul className="space-y-2">
                    {useCase.benefits.map((benefit, benefitIndex) => (
                      <li key={benefitIndex} className="flex items-center text-navy-700">
                        <div className="w-2 h-2 bg-navy-500 rounded-full mr-3"></div>
                        {benefit}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="border-t border-white/20 pt-6 mb-6">
                  <blockquote className="text-navy-600 italic mb-3">
                    {useCase.testimonial}
                  </blockquote>
                  <cite className="text-navy-500 font-medium">
                    — {useCase.author}
                  </cite>
                </div>

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

      {/* Success Stories */}
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
              Success Stories
            </h2>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              Real results from companies using AI Empower Hub
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[
              {
                metric: '500%',
                description: 'Increase in content production',
                company: 'TechStart Media'
              },
              {
                metric: '40%',
                description: 'Higher conversion rates',
                company: 'MarketPro Agency'
              },
              {
                metric: '60%',
                description: 'Improved student engagement',
                company: 'EduTech University'
              }
            ].map((story, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="glass p-8 rounded-xl text-center"
              >
                <div className="text-4xl font-bold gradient-text mb-3">
                  {story.metric}
                </div>
                <p className="text-navy-700 font-medium mb-2">
                  {story.description}
                </p>
                <p className="text-navy-500">
                  {story.company}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Implementation Guide */}
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
              Getting Started
            </h2>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              Simple steps to implement AI Empower Hub in your workflow
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              {
                step: '1',
                title: 'Sign Up',
                description: 'Create your account and choose the right plan for your needs'
              },
              {
                step: '2',
                title: 'Configure',
                description: 'Set up your brand guidelines, templates, and preferences'
              },
              {
                step: '3',
                title: 'Generate',
                description: 'Start creating videos using our AI models and tools'
              },
              {
                step: '4',
                title: 'Scale',
                description: 'Integrate with your existing workflow and scale production'
              }
            ].map((step, index) => (
              <motion.div
                key={step.step}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <div className="w-16 h-16 bg-gradient-to-br from-navy-500 to-navy-700 rounded-full flex items-center justify-center mx-auto mb-4">
                  <span className="text-2xl font-bold text-white">
                    {step.step}
                  </span>
                </div>
                <h3 className="text-xl font-bold text-navy-800 mb-3">
                  {step.title}
                </h3>
                <p className="text-navy-600">
                  {step.description}
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
              Ready to Transform Your Workflow?
            </h2>
            <p className="text-xl text-navy-600 mb-8 max-w-2xl mx-auto">
              Join thousands of creators and businesses already using AI Empower Hub
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
                Schedule Demo
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
