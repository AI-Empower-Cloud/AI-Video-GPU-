'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { 
  CheckIcon,
  XMarkIcon,
  StarIcon,
  RocketLaunchIcon,
  BuildingOfficeIcon,
  UserIcon
} from '@heroicons/react/24/outline';

const plans = [
  {
    name: 'Starter',
    icon: UserIcon,
    price: '$29',
    period: '/month',
    description: 'Perfect for individual creators and small projects',
    features: [
      '10 video generations per month',
      'Basic AI models',
      'HD video output',
      'Email support',
      'Basic templates',
      '5GB cloud storage'
    ],
    notIncluded: [
      'Voice cloning',
      '4K output',
      'Priority support',
      'Custom models'
    ],
    cta: 'Start Free Trial',
    popular: false
  },
  {
    name: 'Professional',
    icon: StarIcon,
    price: '$99',
    period: '/month',
    description: 'Ideal for professional creators and growing teams',
    features: [
      '100 video generations per month',
      'Advanced AI models',
      '4K video output',
      'Voice cloning (5 voices)',
      'Lip sync technology',
      'Priority support',
      'Custom templates',
      '50GB cloud storage',
      'API access',
      'Batch processing'
    ],
    notIncluded: [
      'Unlimited generations',
      'White-label solution',
      'Dedicated support'
    ],
    cta: 'Start Free Trial',
    popular: true
  },
  {
    name: 'Enterprise',
    icon: BuildingOfficeIcon,
    price: 'Custom',
    period: 'pricing',
    description: 'For large teams and organizations with custom needs',
    features: [
      'Unlimited video generations',
      'All AI models included',
      '8K video output',
      'Unlimited voice cloning',
      'Advanced 3D rendering',
      'Dedicated support manager',
      'White-label solution',
      'Unlimited cloud storage',
      'Full API access',
      'Custom integrations',
      'SLA guarantee',
      'On-premise deployment'
    ],
    notIncluded: [],
    cta: 'Contact Sales',
    popular: false
  }
];

const features = [
  { name: 'Video Generations', starter: '10/month', pro: '100/month', enterprise: 'Unlimited' },
  { name: 'AI Models', starter: 'Basic', pro: 'Advanced', enterprise: 'All Models' },
  { name: 'Video Quality', starter: 'HD', pro: '4K', enterprise: '8K' },
  { name: 'Voice Cloning', starter: '❌', pro: '5 voices', enterprise: 'Unlimited' },
  { name: 'Lip Sync', starter: '❌', pro: '✅', enterprise: '✅' },
  { name: '3D Rendering', starter: '❌', pro: 'Basic', enterprise: 'Advanced' },
  { name: 'Cloud Storage', starter: '5GB', pro: '50GB', enterprise: 'Unlimited' },
  { name: 'API Access', starter: '❌', pro: '✅', enterprise: 'Full Access' },
  { name: 'Support', starter: 'Email', pro: 'Priority', enterprise: 'Dedicated' },
  { name: 'Custom Models', starter: '❌', pro: '❌', enterprise: '✅' }
];

export default function PricingPage() {
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
              Simple Pricing
            </h1>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              Choose the perfect plan for your needs. Start free and scale as you grow.
            </p>
          </motion.div>

          {/* Pricing Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-20">
            {plans.map((plan, index) => (
              <motion.div
                key={plan.name}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className={`glass p-8 rounded-2xl relative hover:scale-105 transition-all duration-300 ${
                  plan.popular ? 'ring-2 ring-navy-400 transform scale-105' : ''
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <span className="bg-navy-600 text-white px-4 py-1 rounded-full text-sm font-medium">
                      Most Popular
                    </span>
                  </div>
                )}

                <div className="text-center mb-8">
                  <div className="w-16 h-16 bg-gradient-to-br from-navy-500 to-navy-700 rounded-full flex items-center justify-center mx-auto mb-4">
                    <plan.icon className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-2xl font-bold text-navy-800 mb-2">
                    {plan.name}
                  </h3>
                  <p className="text-navy-600 mb-4">
                    {plan.description}
                  </p>
                  <div className="flex items-end justify-center">
                    <span className="text-4xl font-bold gradient-text">
                      {plan.price}
                    </span>
                    <span className="text-navy-600 ml-1">
                      {plan.period}
                    </span>
                  </div>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center text-navy-700">
                      <CheckIcon className="w-5 h-5 text-green-500 mr-3 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                  {plan.notIncluded.map((feature, featureIndex) => (
                    <li key={featureIndex} className="flex items-center text-navy-400">
                      <XMarkIcon className="w-5 h-5 text-red-400 mr-3 flex-shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>

                <Link
                  href={plan.name === 'Enterprise' ? '/contact' : '/get-started'}
                  className={`w-full py-3 px-6 rounded-lg font-semibold text-center transition-all duration-200 hover:scale-105 block ${
                    plan.popular
                      ? 'bg-navy-600 hover:bg-navy-700 text-white pulse-glow'
                      : 'border border-navy-600 text-navy-700 hover:bg-navy-600 hover:text-white'
                  }`}
                >
                  {plan.cta}
                </Link>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Feature Comparison Table */}
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
              Feature Comparison
            </h2>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              Compare all features across our plans
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            whileInView={{ opacity: 1 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="glass rounded-2xl overflow-hidden"
          >
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/20">
                    <th className="px-6 py-4 text-left text-navy-800 font-semibold">
                      Feature
                    </th>
                    <th className="px-6 py-4 text-center text-navy-800 font-semibold">
                      Starter
                    </th>
                    <th className="px-6 py-4 text-center text-navy-800 font-semibold relative">
                      Professional
                      <span className="absolute -top-2 left-1/2 transform -translate-x-1/2 bg-navy-600 text-white text-xs px-2 py-1 rounded">
                        Popular
                      </span>
                    </th>
                    <th className="px-6 py-4 text-center text-navy-800 font-semibold">
                      Enterprise
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {features.map((feature, index) => (
                    <motion.tr
                      key={feature.name}
                      initial={{ opacity: 0, x: -20 }}
                      whileInView={{ opacity: 1, x: 0 }}
                      transition={{ duration: 0.5, delay: index * 0.05 }}
                      viewport={{ once: true }}
                      className="border-b border-white/10 hover:bg-white/5"
                    >
                      <td className="px-6 py-4 text-navy-700 font-medium">
                        {feature.name}
                      </td>
                      <td className="px-6 py-4 text-center text-navy-600">
                        {feature.starter}
                      </td>
                      <td className="px-6 py-4 text-center text-navy-600">
                        {feature.pro}
                      </td>
                      <td className="px-6 py-4 text-center text-navy-600">
                        {feature.enterprise}
                      </td>
                    </motion.tr>
                  ))}
                </tbody>
              </table>
            </div>
          </motion.div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="text-center mb-16"
          >
            <h2 className="text-4xl md:text-5xl font-bold gradient-text mb-6">
              Frequently Asked Questions
            </h2>
          </motion.div>

          <div className="space-y-6">
            {[
              {
                question: 'Can I change my plan at any time?',
                answer: 'Yes, you can upgrade or downgrade your plan at any time. Changes will be reflected in your next billing cycle.'
              },
              {
                question: 'Is there a free trial?',
                answer: 'Yes, all plans come with a 14-day free trial. No credit card required to get started.'
              },
              {
                question: 'What happens if I exceed my monthly quota?',
                answer: 'If you exceed your monthly quota, you can either upgrade your plan or purchase additional credits at standard rates.'
              },
              {
                question: 'Do you offer refunds?',
                answer: 'We offer a 30-day money-back guarantee for all new subscriptions. Contact support for assistance.'
              },
              {
                question: 'Can I use the API in all plans?',
                answer: 'API access is available in Professional and Enterprise plans. Starter plan includes web interface only.'
              }
            ].map((faq, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="glass p-6 rounded-lg"
              >
                <h3 className="text-lg font-semibold text-navy-800 mb-3">
                  {faq.question}
                </h3>
                <p className="text-navy-600">
                  {faq.answer}
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
              Ready to Start Creating?
            </h2>
            <p className="text-xl text-navy-600 mb-8 max-w-2xl mx-auto">
              Join thousands of creators already using AI Empower Hub
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/get-started"
                className="bg-navy-600 hover:bg-navy-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200 hover:scale-105 pulse-glow flex items-center space-x-2 justify-center"
              >
                <RocketLaunchIcon className="w-5 h-5" />
                <span>Start Free Trial</span>
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
