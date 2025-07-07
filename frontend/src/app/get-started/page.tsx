'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { 
  RocketLaunchIcon,
  UserIcon,
  EnvelopeIcon,
  LockClosedIcon,
  BuildingOfficeIcon,
  CheckIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/react/24/outline';

const plans = [
  {
    name: 'Starter',
    price: '$29',
    period: '/month',
    description: 'Perfect for individual creators',
    features: [
      '10 video generations per month',
      'Basic AI models',
      'HD video output',
      'Email support'
    ],
    recommended: false
  },
  {
    name: 'Professional',
    price: '$99',
    period: '/month',
    description: 'Ideal for growing teams',
    features: [
      '100 video generations per month',
      'Advanced AI models',
      '4K video output',
      'Voice cloning',
      'Priority support'
    ],
    recommended: true
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: 'pricing',
    description: 'For large organizations',
    features: [
      'Unlimited video generations',
      'All AI models',
      '8K video output',
      'Dedicated support',
      'Custom integrations'
    ],
    recommended: false
  }
];

export default function GetStartedPage() {
  const [currentStep, setCurrentStep] = useState(1);
  const [selectedPlan, setSelectedPlan] = useState('Professional');
  const [showPassword, setShowPassword] = useState(false);
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    company: '',
    useCase: ''
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const nextStep = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
    }
  };

  const prevStep = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  return (
    <div className="min-h-screen pt-20">
      {/* Hero Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center mb-16"
          >
            <h1 className="text-5xl md:text-6xl font-bold gradient-text mb-6">
              Get Started
            </h1>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              Start your AI video journey in just a few simple steps
            </p>
          </motion.div>

          {/* Progress Bar */}
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="mb-12"
          >
            <div className="flex items-center justify-center space-x-8">
              {[1, 2, 3].map((step) => (
                <div key={step} className="flex items-center">
                  <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all duration-300 ${
                    currentStep >= step 
                      ? 'bg-navy-600 text-white' 
                      : 'bg-gray-200 text-gray-500'
                  }`}>
                    {currentStep > step ? (
                      <CheckIcon className="w-5 h-5" />
                    ) : (
                      step
                    )}
                  </div>
                  {step < 3 && (
                    <div className={`w-16 h-1 mx-4 transition-all duration-300 ${
                      currentStep > step ? 'bg-navy-600' : 'bg-gray-200'
                    }`}></div>
                  )}
                </div>
              ))}
            </div>
            <div className="flex justify-center space-x-20 mt-4">
              <span className={`text-sm font-medium ${currentStep >= 1 ? 'text-navy-600' : 'text-gray-400'}`}>
                Choose Plan
              </span>
              <span className={`text-sm font-medium ${currentStep >= 2 ? 'text-navy-600' : 'text-gray-400'}`}>
                Account Info
              </span>
              <span className={`text-sm font-medium ${currentStep >= 3 ? 'text-navy-600' : 'text-gray-400'}`}>
                Complete
              </span>
            </div>
          </motion.div>

          {/* Step Content */}
          <motion.div
            key={currentStep}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.5 }}
            className="glass p-8 rounded-2xl"
          >
            {/* Step 1: Choose Plan */}
            {currentStep === 1 && (
              <div>
                <h2 className="text-3xl font-bold text-navy-800 mb-6 text-center">
                  Choose Your Plan
                </h2>
                <p className="text-navy-600 text-center mb-8">
                  Select the plan that best fits your needs. You can upgrade or downgrade at any time.
                </p>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  {plans.map((plan) => (
                    <div
                      key={plan.name}
                      className={`border-2 rounded-lg p-6 cursor-pointer transition-all duration-300 relative ${
                        selectedPlan === plan.name
                          ? 'border-navy-500 bg-navy-50'
                          : 'border-gray-200 hover:border-navy-300'
                      }`}
                      onClick={() => setSelectedPlan(plan.name)}
                    >
                      {plan.recommended && (
                        <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                          <span className="bg-navy-600 text-white px-3 py-1 rounded-full text-sm font-medium">
                            Recommended
                          </span>
                        </div>
                      )}
                      
                      <div className="text-center mb-4">
                        <h3 className="text-xl font-bold text-navy-800 mb-2">
                          {plan.name}
                        </h3>
                        <div className="flex items-end justify-center mb-2">
                          <span className="text-3xl font-bold text-navy-600">
                            {plan.price}
                          </span>
                          <span className="text-navy-400 ml-1">
                            {plan.period}
                          </span>
                        </div>
                        <p className="text-navy-500 text-sm">
                          {plan.description}
                        </p>
                      </div>
                      
                      <ul className="space-y-2">
                        {plan.features.map((feature, index) => (
                          <li key={index} className="flex items-center text-navy-600 text-sm">
                            <CheckIcon className="w-4 h-4 text-green-500 mr-2 flex-shrink-0" />
                            {feature}
                          </li>
                        ))}
                      </ul>
                    </div>
                  ))}
                </div>

                <div className="text-center">
                  <button
                    onClick={nextStep}
                    className="bg-navy-600 hover:bg-navy-700 text-white px-8 py-3 rounded-lg font-semibold transition-all duration-200 hover:scale-105"
                  >
                    Continue with {selectedPlan}
                  </button>
                </div>
              </div>
            )}

            {/* Step 2: Account Information */}
            {currentStep === 2 && (
              <div>
                <h2 className="text-3xl font-bold text-navy-800 mb-6 text-center">
                  Create Your Account
                </h2>
                <p className="text-navy-600 text-center mb-8">
                  Fill in your details to create your AI Empower Hub account
                </p>

                <form className="space-y-6 max-w-md mx-auto">
                  <div>
                    <label className="block text-navy-700 font-medium mb-2">
                      Full Name
                    </label>
                    <div className="relative">
                      <UserIcon className="w-5 h-5 text-navy-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                      <input
                        type="text"
                        name="fullName"
                        value={formData.fullName}
                        onChange={handleInputChange}
                        className="w-full pl-10 pr-4 py-3 border border-navy-300 rounded-lg focus:border-navy-500 focus:outline-none"
                        placeholder="Enter your full name"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-navy-700 font-medium mb-2">
                      Email Address
                    </label>
                    <div className="relative">
                      <EnvelopeIcon className="w-5 h-5 text-navy-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                      <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleInputChange}
                        className="w-full pl-10 pr-4 py-3 border border-navy-300 rounded-lg focus:border-navy-500 focus:outline-none"
                        placeholder="Enter your email"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-navy-700 font-medium mb-2">
                      Password
                    </label>
                    <div className="relative">
                      <LockClosedIcon className="w-5 h-5 text-navy-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                      <input
                        type={showPassword ? 'text' : 'password'}
                        name="password"
                        value={formData.password}
                        onChange={handleInputChange}
                        className="w-full pl-10 pr-12 py-3 border border-navy-300 rounded-lg focus:border-navy-500 focus:outline-none"
                        placeholder="Create a password"
                        required
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-1/2 transform -translate-y-1/2 text-navy-400 hover:text-navy-600"
                      >
                        {showPassword ? (
                          <EyeSlashIcon className="w-5 h-5" />
                        ) : (
                          <EyeIcon className="w-5 h-5" />
                        )}
                      </button>
                    </div>
                  </div>

                  <div>
                    <label className="block text-navy-700 font-medium mb-2">
                      Company (Optional)
                    </label>
                    <div className="relative">
                      <BuildingOfficeIcon className="w-5 h-5 text-navy-400 absolute left-3 top-1/2 transform -translate-y-1/2" />
                      <input
                        type="text"
                        name="company"
                        value={formData.company}
                        onChange={handleInputChange}
                        className="w-full pl-10 pr-4 py-3 border border-navy-300 rounded-lg focus:border-navy-500 focus:outline-none"
                        placeholder="Your company name"
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-navy-700 font-medium mb-2">
                      Primary Use Case
                    </label>
                    <select
                      name="useCase"
                      value={formData.useCase}
                      onChange={handleInputChange}
                      className="w-full px-4 py-3 border border-navy-300 rounded-lg focus:border-navy-500 focus:outline-none"
                      required
                    >
                      <option value="">Select your use case</option>
                      <option value="content-creation">Content Creation</option>
                      <option value="marketing">Marketing & Advertising</option>
                      <option value="education">Education & Training</option>
                      <option value="ecommerce">E-commerce</option>
                      <option value="entertainment">Entertainment</option>
                      <option value="other">Other</option>
                    </select>
                  </div>
                </form>

                <div className="flex space-x-4 justify-center mt-8">
                  <button
                    onClick={prevStep}
                    className="border border-navy-600 text-navy-700 px-6 py-3 rounded-lg font-semibold transition-all duration-200 hover:bg-navy-600 hover:text-white"
                  >
                    Back
                  </button>
                  <button
                    onClick={nextStep}
                    className="bg-navy-600 hover:bg-navy-700 text-white px-8 py-3 rounded-lg font-semibold transition-all duration-200 hover:scale-105"
                  >
                    Create Account
                  </button>
                </div>
              </div>
            )}

            {/* Step 3: Complete */}
            {currentStep === 3 && (
              <div className="text-center">
                <div className="w-20 h-20 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  <CheckIcon className="w-10 h-10 text-green-600" />
                </div>
                
                <h2 className="text-3xl font-bold text-navy-800 mb-6">
                  Welcome to AI Empower Hub!
                </h2>
                <p className="text-navy-600 mb-8 max-w-md mx-auto">
                  Your account has been created successfully. You're now ready to start creating amazing AI-generated videos.
                </p>

                <div className="glass p-6 rounded-lg mb-8 max-w-sm mx-auto">
                  <h3 className="font-semibold text-navy-800 mb-3">
                    What's Next?
                  </h3>
                  <ul className="text-left space-y-2 text-navy-600">
                    <li className="flex items-center">
                      <div className="w-2 h-2 bg-navy-400 rounded-full mr-3"></div>
                      Explore the dashboard
                    </li>
                    <li className="flex items-center">
                      <div className="w-2 h-2 bg-navy-400 rounded-full mr-3"></div>
                      Generate your first video
                    </li>
                    <li className="flex items-center">
                      <div className="w-2 h-2 bg-navy-400 rounded-full mr-3"></div>
                      Read the documentation
                    </li>
                  </ul>
                </div>

                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Link
                    href="/dashboard"
                    className="bg-navy-600 hover:bg-navy-700 text-white px-8 py-3 rounded-lg font-semibold transition-all duration-200 hover:scale-105 pulse-glow flex items-center justify-center space-x-2"
                  >
                    <RocketLaunchIcon className="w-5 h-5" />
                    <span>Go to Dashboard</span>
                  </Link>
                  <Link
                    href="/docs"
                    className="border border-navy-600 text-navy-700 hover:bg-navy-600 hover:text-white px-8 py-3 rounded-lg font-semibold transition-all duration-200"
                  >
                    View Documentation
                  </Link>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      </section>

      {/* Features Preview */}
      {currentStep === 1 && (
        <section className="py-20">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
              viewport={{ once: true }}
              className="text-center mb-16"
            >
              <h2 className="text-4xl font-bold gradient-text mb-6">
                What You'll Get Access To
              </h2>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  title: 'AI Video Generation',
                  description: 'Create stunning videos from text prompts using state-of-the-art AI models',
                  icon: '🎬'
                },
                {
                  title: 'Voice Cloning',
                  description: 'Clone voices with high fidelity and perfect lip-sync technology',
                  icon: '🎤'
                },
                {
                  title: 'Cloud Integration',
                  description: 'Seamless cloud storage and processing with enterprise-grade security',
                  icon: '☁️'
                }
              ].map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 30 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className="glass p-6 rounded-lg text-center"
                >
                  <div className="text-4xl mb-4">{feature.icon}</div>
                  <h3 className="text-xl font-bold text-navy-800 mb-3">
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
      )}

      {/* Support Section */}
      <section className="py-20">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            whileInView={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            viewport={{ once: true }}
            className="glass p-8 rounded-xl"
          >
            <h3 className="text-2xl font-bold gradient-text mb-4">
              Need Help Getting Started?
            </h3>
            <p className="text-navy-600 mb-6">
              Our support team is here to help you every step of the way
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/docs"
                className="border border-navy-600 text-navy-700 hover:bg-navy-600 hover:text-white px-6 py-3 rounded-lg font-medium transition-all duration-200"
              >
                View Documentation
              </Link>
              <Link
                href="/contact"
                className="border border-navy-600 text-navy-700 hover:bg-navy-600 hover:text-white px-6 py-3 rounded-lg font-medium transition-all duration-200"
              >
                Contact Support
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
