'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { 
  RocketLaunchIcon,
  EyeIcon,
  HeartIcon,
  StarIcon,
  UserGroupIcon,
  GlobeAltIcon,
  CpuChipIcon,
  LightBulbIcon
} from '@heroicons/react/24/outline';

const values = [
  {
    icon: RocketLaunchIcon,
    title: 'Innovation',
    description: 'We push the boundaries of what\'s possible with AI and video technology'
  },
  {
    icon: UserGroupIcon,
    title: 'Community',
    description: 'We believe in empowering creators and building a supportive ecosystem'
  },
  {
    icon: EyeIcon,
    title: 'Transparency',
    description: 'We\'re open about our technology, pricing, and business practices'
  },
  {
    icon: HeartIcon,
    title: 'Quality',
    description: 'We\'re committed to delivering exceptional results and user experiences'
  }
];

const team = [
  {
    name: 'Alex Chen',
    role: 'CEO & Co-founder',
    bio: 'Former Google AI researcher with 10+ years in machine learning and computer vision',
    image: '👨‍💼'
  },
  {
    name: 'Sarah Rodriguez',
    role: 'CTO & Co-founder',
    bio: 'Ex-NVIDIA engineer specializing in GPU acceleration and real-time graphics',
    image: '👩‍💻'
  },
  {
    name: 'Marcus Kim',
    role: 'Head of AI Research',
    bio: 'PhD in Computer Vision from MIT, published 50+ papers on generative models',
    image: '👨‍🔬'
  },
  {
    name: 'Emily Watson',
    role: 'VP of Product',
    bio: 'Former Adobe product manager with expertise in creative tools and user experience',
    image: '👩‍🎨'
  },
  {
    name: 'James Park',
    role: 'Head of Engineering',
    bio: 'Previously at Tesla, specialized in distributed systems and cloud architecture',
    image: '👨‍⚡'
  },
  {
    name: 'Lisa Zhang',
    role: 'VP of Marketing',
    bio: 'Growth marketing expert who scaled multiple B2B SaaS companies from startup to IPO',
    image: '👩‍📈'
  }
];

const milestones = [
  {
    year: '2022',
    title: 'Company Founded',
    description: 'Started with a vision to democratize AI video generation'
  },
  {
    year: '2023',
    title: 'Series A Funding',
    description: 'Raised $15M to accelerate product development and team growth'
  },
  {
    year: '2023',
    title: 'First 1000 Customers',
    description: 'Reached our first major milestone with creators worldwide'
  },
  {
    year: '2024',
    title: 'Enterprise Launch',
    description: 'Launched enterprise platform with advanced features and security'
  },
  {
    year: '2024',
    title: 'Global Expansion',
    description: 'Expanded to 50+ countries with multi-language support'
  },
  {
    year: '2024',
    title: '10M Videos Generated',
    description: 'Celebrated generating 10 million videos for our community'
  }
];

export default function AboutPage() {
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
              About AI Empower Hub
            </h1>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              We're on a mission to democratize AI video generation and empower creators worldwide 
              with cutting-edge technology.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8, delay: 0.2 }}
            className="glass p-12 rounded-2xl text-center mb-20"
          >
            <h2 className="text-3xl font-bold gradient-text mb-6">
              Our Story
            </h2>
            <p className="text-lg text-navy-600 max-w-4xl mx-auto leading-relaxed">
              Founded in 2022 by a team of AI researchers and engineers from Google, NVIDIA, and Adobe, 
              AI Empower Hub was born from the frustration of seeing incredible AI research locked away 
              in academic papers while creators struggled with expensive, time-consuming video production. 
              We believed that powerful AI video generation should be accessible to everyone - from 
              individual creators to large enterprises.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Mission & Vision */}
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
              <div className="w-16 h-16 bg-gradient-to-br from-navy-500 to-navy-700 rounded-full flex items-center justify-center mb-6">
                <RocketLaunchIcon className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-3xl font-bold gradient-text mb-6">
                Our Mission
              </h3>
              <p className="text-navy-600 text-lg leading-relaxed">
                To democratize AI video generation by making cutting-edge technology accessible, 
                affordable, and easy to use for creators of all skill levels. We believe that 
                everyone should have the power to bring their ideas to life through video.
              </p>
            </motion.div>

            <motion.div
              initial={{ opacity: 0, x: 30 }}
              whileInView={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              viewport={{ once: true }}
              className="glass p-8 rounded-xl"
            >
              <div className="w-16 h-16 bg-gradient-to-br from-navy-500 to-navy-700 rounded-full flex items-center justify-center mb-6">
                <EyeIcon className="w-8 h-8 text-white" />
              </div>
              <h3 className="text-3xl font-bold gradient-text mb-6">
                Our Vision
              </h3>
              <p className="text-navy-600 text-lg leading-relaxed">
                A world where creative expression is limitless, where anyone can create 
                professional-quality videos without technical barriers, and where AI enhances 
                human creativity rather than replacing it.
              </p>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Values */}
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
              Our Values
            </h2>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              The principles that guide everything we do
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {values.map((value, index) => (
              <motion.div
                key={value.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="glass p-6 rounded-lg text-center hover:scale-105 transition-all duration-300"
              >
                <div className="w-12 h-12 bg-gradient-to-br from-navy-500 to-navy-700 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <value.icon className="w-6 h-6 text-white" />
                </div>
                <h3 className="text-xl font-bold text-navy-800 mb-3">
                  {value.title}
                </h3>
                <p className="text-navy-600">
                  {value.description}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Team */}
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
              Meet Our Team
            </h2>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              World-class team of researchers, engineers, and creators
            </p>
          </motion.div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {team.map((member, index) => (
              <motion.div
                key={member.name}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="glass p-6 rounded-lg text-center hover:scale-105 transition-all duration-300"
              >
                <div className="text-6xl mb-4">{member.image}</div>
                <h3 className="text-xl font-bold text-navy-800 mb-2">
                  {member.name}
                </h3>
                <p className="text-navy-500 font-medium mb-3">
                  {member.role}
                </p>
                <p className="text-navy-600 text-sm">
                  {member.bio}
                </p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Timeline */}
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
              Our Journey
            </h2>
            <p className="text-xl text-navy-600 max-w-3xl mx-auto">
              Key milestones in our mission to democratize AI video
            </p>
          </motion.div>

          <div className="relative">
            <div className="absolute left-1/2 transform -translate-x-1/2 w-1 h-full bg-gradient-to-b from-navy-300 to-navy-600"></div>
            
            <div className="space-y-12">
              {milestones.map((milestone, index) => (
                <motion.div
                  key={milestone.year}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.6, delay: index * 0.1 }}
                  viewport={{ once: true }}
                  className={`flex items-center ${
                    index % 2 === 0 ? 'flex-row' : 'flex-row-reverse'
                  }`}
                >
                  <div className={`w-5/12 ${index % 2 === 0 ? 'text-right pr-8' : 'text-left pl-8'}`}>
                    <div className="glass p-6 rounded-lg">
                      <div className="text-2xl font-bold gradient-text mb-2">
                        {milestone.year}
                      </div>
                      <h3 className="text-xl font-bold text-navy-800 mb-3">
                        {milestone.title}
                      </h3>
                      <p className="text-navy-600">
                        {milestone.description}
                      </p>
                    </div>
                  </div>
                  
                  <div className="w-2/12 flex justify-center">
                    <div className="w-6 h-6 bg-navy-600 rounded-full border-4 border-white shadow-lg"></div>
                  </div>
                  
                  <div className="w-5/12"></div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {[
              { value: '10M+', label: 'Videos Generated' },
              { value: '50+', label: 'Countries' },
              { value: '5K+', label: 'Active Users' },
              { value: '99.9%', label: 'Uptime' }
            ].map((stat, index) => (
              <motion.div
                key={stat.label}
                initial={{ opacity: 0, scale: 0.5 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="glass p-8 rounded-lg text-center"
              >
                <div className="text-4xl md:text-5xl font-bold gradient-text mb-3">
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
              Join Our Mission
            </h2>
            <p className="text-xl text-navy-600 mb-8 max-w-2xl mx-auto">
              Be part of the AI video revolution and help us democratize creative technology
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/get-started"
                className="bg-navy-600 hover:bg-navy-700 text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200 hover:scale-105 pulse-glow"
              >
                Start Creating
              </Link>
              <Link
                href="/careers"
                className="border border-navy-600 text-navy-700 hover:bg-navy-600 hover:text-white px-8 py-4 rounded-lg font-semibold text-lg transition-all duration-200"
              >
                Join Our Team
              </Link>
            </div>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
