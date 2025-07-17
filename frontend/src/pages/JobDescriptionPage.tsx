import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { Building, FileText, ArrowRight, Briefcase, Target, Users, Zap } from 'lucide-react';
import Layout from '../components/Layout';
import { JobDescription } from '../types';

const JobDescriptionPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<JobDescription>({
    title: '',
    company: '',
    description: '',
    requirements: '',
    level: 'entry',
    type: 'hr'
  });

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    localStorage.setItem('jobDescription', JSON.stringify(formData));
    navigate('/interview');
  };

  const isFormValid = formData.title && formData.company && formData.description;

  return (
    <Layout>
      <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 text-center"
        >
          <h1 className="text-4xl font-bold text-white mb-2 neon-text">Job Description</h1>
          <p className="text-gray-300">Tell us about the position you're interviewing for</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass rounded-3xl p-8 border border-white/10 shadow-2xl"
        >
          <form onSubmit={handleSubmit} className="space-y-8">
            
            {/* Job Details */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
            >
              <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
                <Briefcase className="h-5 w-5 mr-2 text-cyber-blue" />
                Position Details
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="title" className="block text-sm font-medium text-gray-300 mb-2">
                    Job Title *
                  </label>
                  <input
                    id="title"
                    name="title"
                    type="text"
                    value={formData.title}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-dark-200/50 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-cyber-blue focus:border-cyber-blue transition-all duration-200"
                    placeholder="e.g., Software Engineer, Marketing Manager"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="company" className="block text-sm font-medium text-gray-300 mb-2">
                    Company Name *
                  </label>
                  <div className="relative">
                    <Building className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      id="company"
                      name="company"
                      type="text"
                      value={formData.company}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-3 bg-dark-200/50 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-cyber-blue focus:border-cyber-blue transition-all duration-200"
                      placeholder="e.g., Google, Microsoft, Startup Inc."
                      required
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="level" className="block text-sm font-medium text-gray-300 mb-2">
                    Experience Level
                  </label>
                  <select
                    id="level"
                    name="level"
                    value={formData.level}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-dark-200/50 border border-white/10 rounded-xl text-white focus:ring-2 focus:ring-cyber-blue focus:border-cyber-blue transition-all duration-200"
                  >
                    <option value="entry">Entry Level (0-2 years)</option>
                    <option value="mid">Mid Level (2-5 years)</option>
                    <option value="senior">Senior Level (5+ years)</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="type" className="block text-sm font-medium text-gray-300 mb-2">
                    Interview Type
                  </label>
                  <select
                    id="type"
                    name="type"
                    value={formData.type}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-dark-200/50 border border-white/10 rounded-xl text-white focus:ring-2 focus:ring-cyber-blue focus:border-cyber-blue transition-all duration-200"
                  >
                    <option value="hr">HR/General Interview</option>
                    <option value="technical">Technical Interview</option>
                    <option value="behavioral">Behavioral Interview</option>
                  </select>
                </div>
              </div>
            </motion.div>

            {/* Job Description */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
            >
              <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
                <FileText className="h-5 w-5 mr-2 text-purple-400" />
                Job Information
              </h2>
              
              <div className="space-y-6">
                <div>
                  <label htmlFor="description" className="block text-sm font-medium text-gray-300 mb-2">
                    Job Description *
                  </label>
                  <textarea
                    id="description"
                    name="description"
                    rows={6}
                    value={formData.description}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-dark-200/50 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-cyber-blue focus:border-cyber-blue transition-all duration-200"
                    placeholder="Paste the job description here or describe the role responsibilities, what the company does, and what you'll be working on..."
                    required
                  />
                </div>

                <div>
                  <label htmlFor="requirements" className="block text-sm font-medium text-gray-300 mb-2">
                    Requirements & Qualifications
                  </label>
                  <textarea
                    id="requirements"
                    name="requirements"
                    rows={4}
                    value={formData.requirements}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-dark-200/50 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-cyber-blue focus:border-cyber-blue transition-all duration-200"
                    placeholder="List the key requirements, skills, and qualifications mentioned in the job posting..."
                  />
                </div>
              </div>
            </motion.div>

            {/* Interview Focus Areas */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
              className="glass rounded-2xl p-6 border border-white/10 holographic"
            >
              <h3 className="text-lg font-semibold text-white mb-4 flex items-center">
                <Target className="h-5 w-5 mr-2 text-cyber-blue" />
                What to Expect in Your AI Interview
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {[
                  {
                    icon: Users,
                    title: 'Behavioral Questions',
                    desc: 'Tell me about yourself, strengths/weaknesses',
                    color: 'text-cyber-blue'
                  },
                  {
                    icon: Building,
                    title: 'Company-Specific',
                    desc: 'Why this company, role-specific scenarios',
                    color: 'text-purple-400'
                  },
                  {
                    icon: Zap,
                    title: 'Situational',
                    desc: 'Problem-solving, teamwork scenarios',
                    color: 'text-green-400'
                  }
                ].map((item, index) => (
                  <motion.div
                    key={item.title}
                    className="bg-dark-200/30 rounded-xl p-4 border border-white/5"
                    whileHover={{ scale: 1.05, y: -5 }}
                    transition={{ type: "spring", stiffness: 300, damping: 20 }}
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={{ animationDelay: `${index * 0.1}s` }}
                  >
                    <item.icon className={`h-6 w-6 ${item.color} mb-2`} />
                    <h4 className="font-medium text-white mb-1">{item.title}</h4>
                    <p className="text-sm text-gray-400">{item.desc}</p>
                  </motion.div>
                ))}
              </div>
            </motion.div>

            {/* Submit Button */}
            <motion.div
              className="pt-6 border-t border-white/10"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.6 }}
            >
              <motion.button
                type="submit"
                disabled={!isFormValid}
                className="w-full bg-gradient-to-r from-cyber-blue to-purple-600 text-white py-4 px-6 rounded-xl font-medium hover:from-blue-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-cyber-blue focus:ring-offset-2 focus:ring-offset-dark-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 btn-futuristic flex items-center justify-center space-x-2 glow-blue"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <span>Start AI Interview</span>
                <ArrowRight className="h-5 w-5" />
              </motion.button>
            </motion.div>
          </form>
        </motion.div>
      </div>
    </Layout>
  );
};

export default JobDescriptionPage;