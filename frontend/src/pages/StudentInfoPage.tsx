import React, { useState } from 'react';
import { motion } from 'framer-motion';
import { useNavigate } from 'react-router-dom';
import { User, GraduationCap, Phone, Mail, Briefcase, ArrowRight, Plus, X, Camera } from 'lucide-react';
import Layout from '../components/Layout';
import { StudentInfo } from '../types';
import { useCamera } from '../hooks/useCamera';

const StudentInfoPage: React.FC = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState<StudentInfo>({
    name: '',
    email: '',
    phone: '',
    education: '',
    major: '',
    graduationYear: '',
    experience: '',
    skills: []
  });
  const [currentSkill, setCurrentSkill] = useState('');
  const [showCamera, setShowCamera] = useState(false);
  
  const {
    isActive,
    capturedPhoto,
    isCapturing,
    videoRef,
    canvasRef,
    startCamera,
    stopCamera,
    capturePhoto,
    retakePhoto
  } = useCamera();

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }));
  };

  const addSkill = () => {
    if (currentSkill.trim() && !formData.skills.includes(currentSkill.trim())) {
      setFormData(prev => ({
        ...prev,
        skills: [...prev.skills, currentSkill.trim()]
      }));
      setCurrentSkill('');
    }
  };

  const removeSkill = (skill: string) => {
    setFormData(prev => ({
      ...prev,
      skills: prev.skills.filter(s => s !== skill)
    }));
  };

  const handleCameraToggle = () => {
    if (showCamera && isActive) {
      stopCamera();
    }
    setShowCamera(!showCamera);
  };

  const handleTakePhoto = async () => {
    if (!isActive) {
      await startCamera();
    } else {
      capturePhoto();
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const dataToSave = {
      ...formData,
      profilePhoto: capturedPhoto || undefined
    };
    localStorage.setItem('studentInfo', JSON.stringify(dataToSave));
    navigate('/job-description');
  };

  const isFormValid = formData.name && formData.email && formData.education && formData.major;

  return (
    <Layout>
      <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8 text-center"
        >
          <h1 className="text-4xl font-bold text-white mb-2 neon-text">Tell Us About Yourself</h1>
          <p className="text-gray-300">Help us personalize your AI interview experience</p>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="glass rounded-3xl p-8 border border-white/10 shadow-2xl"
        >
          <form onSubmit={handleSubmit} className="space-y-8">
            
            {/* Profile Photo Section */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.3 }}
            >
              <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
                <Camera className="h-5 w-5 mr-2 text-cyber-blue" />
                Profile Photo (Optional)
              </h2>
              
              <div className="flex flex-col lg:flex-row gap-6 items-start">
                {/* Photo Preview */}
                <div className="flex-shrink-0">
                  {capturedPhoto ? (
                    <div className="relative">
                      <img
                        src={capturedPhoto}
                        alt="Profile"
                        className="w-32 h-32 rounded-2xl object-cover border-2 border-cyber-blue glow-blue"
                      />
                      <button
                        type="button"
                        onClick={retakePhoto}
                        className="absolute -top-2 -right-2 bg-red-500 text-white rounded-full p-1 hover:bg-red-600 transition-colors"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  ) : (
                    <div className="w-32 h-32 rounded-2xl bg-dark-200/50 border-2 border-dashed border-gray-600 flex items-center justify-center">
                      <Camera className="h-8 w-8 text-gray-400" />
                    </div>
                  )}
                </div>

                {/* Camera Controls */}
                <div className="flex-1">
                  <div className="flex gap-3 mb-4">
                    <motion.button
                      type="button"
                      onClick={handleCameraToggle}
                      className="btn-futuristic bg-gradient-to-r from-cyber-blue to-purple-600 text-white px-4 py-2 rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-200 flex items-center space-x-2"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Camera className="h-4 w-4" />
                      <span>{showCamera ? 'Hide Camera' : 'Open Camera'}</span>
                    </motion.button>

                    {isActive && (
                      <motion.button
                        type="button"
                        onClick={handleTakePhoto}
                        disabled={isCapturing}
                        className="btn-futuristic bg-gradient-to-r from-green-500 to-emerald-600 text-white px-4 py-2 rounded-xl hover:from-green-600 hover:to-emerald-700 transition-all duration-200 flex items-center space-x-2 disabled:opacity-50"
                        whileHover={{ scale: 1.05 }}
                        whileTap={{ scale: 0.95 }}
                        initial={{ opacity: 0, scale: 0.8 }}
                        animate={{ opacity: 1, scale: 1 }}
                      >
                        <span>{isCapturing ? 'Capturing...' : 'Take Photo'}</span>
                      </motion.button>
                    )}
                  </div>

                  {/* Camera Preview */}
                  {showCamera && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      exit={{ opacity: 0, height: 0 }}
                      className="relative"
                    >
                      <video
                        ref={videoRef}
                        autoPlay
                        muted
                        className="w-full max-w-md h-48 object-cover rounded-xl border border-white/10"
                      />
                      <canvas ref={canvasRef} className="hidden" />
                    </motion.div>
                  )}
                </div>
              </div>
            </motion.div>

            {/* Personal Information */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
            >
              <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
                <User className="h-5 w-5 mr-2 text-cyber-blue" />
                Personal Information
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-300 mb-2">
                    Full Name *
                  </label>
                  <input
                    id="name"
                    name="name"
                    type="text"
                    value={formData.name}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-dark-200/50 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-cyber-blue focus:border-cyber-blue transition-all duration-200"
                    placeholder="Enter your full name"
                    required
                  />
                </div>

                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                    Email Address *
                  </label>
                  <div className="relative">
                    <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      id="email"
                      name="email"
                      type="email"
                      value={formData.email}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-3 bg-dark-200/50 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-cyber-blue focus:border-cyber-blue transition-all duration-200"
                      placeholder="your.email@example.com"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label htmlFor="phone" className="block text-sm font-medium text-gray-300 mb-2">
                    Phone Number
                  </label>
                  <div className="relative">
                    <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      id="phone"
                      name="phone"
                      type="tel"
                      value={formData.phone}
                      onChange={handleInputChange}
                      className="w-full pl-10 pr-4 py-3 bg-dark-200/50 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-cyber-blue focus:border-cyber-blue transition-all duration-200"
                      placeholder="+1 (555) 123-4567"
                    />
                  </div>
                </div>
              </div>
            </motion.div>

            {/* Education */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.5 }}
            >
              <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
                <GraduationCap className="h-5 w-5 mr-2 text-purple-400" />
                Education
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <label htmlFor="education" className="block text-sm font-medium text-gray-300 mb-2">
                    Education Level *
                  </label>
                  <select
                    id="education"
                    name="education"
                    value={formData.education}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-dark-200/50 border border-white/10 rounded-xl text-white focus:ring-2 focus:ring-cyber-blue focus:border-cyber-blue transition-all duration-200"
                    required
                  >
                    <option value="">Select education level</option>
                    <option value="high-school">High School</option>
                    <option value="associate">Associate's Degree</option>
                    <option value="bachelor">Bachelor's Degree</option>
                    <option value="master">Master's Degree</option>
                    <option value="phd">PhD</option>
                  </select>
                </div>

                <div>
                  <label htmlFor="major" className="block text-sm font-medium text-gray-300 mb-2">
                    Major/Field of Study *
                  </label>
                  <input
                    id="major"
                    name="major"
                    type="text"
                    value={formData.major}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-dark-200/50 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-cyber-blue focus:border-cyber-blue transition-all duration-200"
                    placeholder="Computer Science, Business, etc."
                    required
                  />
                </div>

                <div>
                  <label htmlFor="graduationYear" className="block text-sm font-medium text-gray-300 mb-2">
                    Graduation Year
                  </label>
                  <input
                    id="graduationYear"
                    name="graduationYear"
                    type="text"
                    value={formData.graduationYear}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-dark-200/50 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-cyber-blue focus:border-cyber-blue transition-all duration-200"
                    placeholder="2024"
                  />
                </div>
              </div>
            </motion.div>

            {/* Experience & Skills */}
            <motion.div
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.6 }}
            >
              <h2 className="text-xl font-semibold text-white mb-6 flex items-center">
                <Briefcase className="h-5 w-5 mr-2 text-green-400" />
                Experience & Skills
              </h2>
              
              <div className="space-y-6">
                <div>
                  <label htmlFor="experience" className="block text-sm font-medium text-gray-300 mb-2">
                    Work Experience
                  </label>
                  <textarea
                    id="experience"
                    name="experience"
                    rows={4}
                    value={formData.experience}
                    onChange={handleInputChange}
                    className="w-full px-4 py-3 bg-dark-200/50 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-cyber-blue focus:border-cyber-blue transition-all duration-200"
                    placeholder="Describe your relevant work experience, internships, or projects..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Skills & Technologies
                  </label>
                  <div className="flex space-x-2 mb-3">
                    <input
                      type="text"
                      value={currentSkill}
                      onChange={(e) => setCurrentSkill(e.target.value)}
                      onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
                      className="flex-1 px-4 py-2 bg-dark-200/50 border border-white/10 rounded-xl text-white placeholder-gray-400 focus:ring-2 focus:ring-cyber-blue focus:border-cyber-blue transition-all duration-200"
                      placeholder="Add a skill (e.g., JavaScript, Python, Communication)"
                    />
                    <motion.button
                      type="button"
                      onClick={addSkill}
                      className="px-4 py-2 bg-gradient-to-r from-cyber-blue to-purple-600 text-white rounded-xl hover:from-blue-600 hover:to-purple-700 transition-all duration-200 flex items-center"
                      whileHover={{ scale: 1.05 }}
                      whileTap={{ scale: 0.95 }}
                    >
                      <Plus className="h-4 w-4" />
                    </motion.button>
                  </div>
                  
                  {formData.skills.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {formData.skills.map((skill, index) => (
                        <motion.span
                          key={index}
                          initial={{ opacity: 0, scale: 0.8 }}
                          animate={{ opacity: 1, scale: 1 }}
                          className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-gradient-to-r from-cyber-blue/20 to-purple-600/20 text-cyber-blue border border-cyber-blue/30"
                        >
                          {skill}
                          <button
                            type="button"
                            onClick={() => removeSkill(skill)}
                            className="ml-2 text-cyber-blue hover:text-white transition-colors"
                          >
                            <X className="h-3 w-3" />
                          </button>
                        </motion.span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            </motion.div>

            {/* Submit Button */}
            <motion.div
              className="pt-6 border-t border-white/10"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.7 }}
            >
              <motion.button
                type="submit"
                disabled={!isFormValid}
                className="w-full bg-gradient-to-r from-cyber-blue to-purple-600 text-white py-4 px-6 rounded-xl font-medium hover:from-blue-600 hover:to-purple-700 focus:outline-none focus:ring-2 focus:ring-cyber-blue focus:ring-offset-2 focus:ring-offset-dark-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 btn-futuristic flex items-center justify-center space-x-2 glow-blue"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <span>Continue to Job Description</span>
                <ArrowRight className="h-5 w-5" />
              </motion.button>
            </motion.div>
          </form>
        </motion.div>
      </div>
    </Layout>
  );
};

export default StudentInfoPage;