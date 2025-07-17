import React from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../hooks/useAuth';
import { LogOut, User, Bot } from 'lucide-react';
import ParticleBackground from './ParticleBackground';

interface LayoutProps {
  children: React.ReactNode;
  showHeader?: boolean;
  className?: string;
}

const Layout: React.FC<LayoutProps> = ({ children, showHeader = true, className = '' }) => {
  const { user, logout } = useAuth();

  return (
    <div className={`min-h-screen animated-bg relative ${className}`}>
      <ParticleBackground />
      
      {showHeader && user && (
        <motion.header
          initial={{ y: -100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          className="glass border-b border-white/10 sticky top-0 z-40"
        >
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <motion.div 
                className="flex items-center space-x-3"
                whileHover={{ scale: 1.05 }}
                transition={{ type: "spring", stiffness: 400, damping: 10 }}
              >
                <div className="bg-gradient-to-r from-cyber-blue to-purple-600 p-2 rounded-xl glow-blue">
                  <Bot className="h-6 w-6 text-white" />
                </div>
                <div>
                  <h1 className="text-xl font-bold text-white neon-text">AI Interviewer Pro</h1>
                  <p className="text-sm text-gray-300 font-mono">Next-Gen Interview Platform</p>
                </div>
              </motion.div>
              
              <div className="flex items-center space-x-4">
                <motion.div 
                  className="flex items-center space-x-2 text-sm text-gray-300"
                  whileHover={{ scale: 1.05 }}
                >
                  <div className="w-8 h-8 rounded-full bg-gradient-to-r from-cyber-blue to-purple-600 flex items-center justify-center">
                    <User className="h-4 w-4 text-white" />
                  </div>
                  <span className="font-medium">{user.name}</span>
                </motion.div>
                
                <motion.button
                  onClick={logout}
                  className="flex items-center space-x-2 text-sm text-gray-400 hover:text-white transition-colors duration-200 btn-futuristic px-3 py-2 rounded-lg"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  <LogOut className="h-4 w-4" />
                  <span>Logout</span>
                </motion.button>
              </div>
            </div>
          </div>
        </motion.header>
      )}
      
      <main className="relative z-10">
        {children}
      </main>
    </div>
  );
};

export default Layout;