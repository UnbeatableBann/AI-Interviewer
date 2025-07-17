import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { useAuth } from '../hooks/useAuth';
import { useNavigate } from 'react-router-dom';
import { 
  BarChart3, 
  Users, 
  TrendingUp, 
  Clock, 
  Award, 
  Download, 
  Filter,
  Search,
  Calendar,
  Star,
  Eye,
  LogOut,
  Bot,
  RefreshCw
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts';
import ThreeDBackground from '../components/3DBackground';
import { HRDashboardStats, InterviewSession } from '../types';

const HRDashboard: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<HRDashboardStats | null>(null);
  const [selectedTimeframe, setSelectedTimeframe] = useState('week');
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    if (!user || user.role !== 'hr') {
      navigate('/auth?role=hr');
      return;
    }
    loadDashboardData();
  }, [user, navigate]);

  const loadDashboardData = () => {
    // Load interviews from localStorage (mock database)
    const interviews = JSON.parse(localStorage.getItem('interviews') || '[]');
    
    // Generate mock stats
    const mockStats: HRDashboardStats = {
      totalInterviews: interviews.length + Math.floor(Math.random() * 100) + 50,
      todayInterviews: Math.floor(Math.random() * 10) + 5,
      averageScore: Math.floor(Math.random() * 20) + 75,
      completionRate: Math.floor(Math.random() * 15) + 85,
      topSkills: ['JavaScript', 'React', 'Python', 'Communication', 'Leadership'],
      recentInterviews: interviews.slice(-10)
    };
    
    setStats(mockStats);
  };

  const chartData = [
    { name: 'Mon', interviews: 12, avgScore: 78 },
    { name: 'Tue', interviews: 19, avgScore: 82 },
    { name: 'Wed', interviews: 15, avgScore: 75 },
    { name: 'Thu', interviews: 22, avgScore: 88 },
    { name: 'Fri', interviews: 18, avgScore: 85 },
    { name: 'Sat', interviews: 8, avgScore: 79 },
    { name: 'Sun', interviews: 5, avgScore: 81 }
  ];

  const skillsData = [
    { name: 'Technical', value: 35, color: '#00d4ff' },
    { name: 'Communication', value: 25, color: '#9333ea' },
    { name: 'Leadership', value: 20, color: '#22c55e' },
    { name: 'Problem Solving', value: 20, color: '#f97316' }
  ];

  if (!stats) {
    return (
      <div className="min-h-screen animated-bg flex items-center justify-center">
        <div className="text-center">
          <Bot className="h-16 w-16 text-cyber-blue mx-auto mb-4 animate-spin" />
          <h2 className="text-2xl font-bold text-white mb-2">Loading Dashboard...</h2>
          <p className="text-gray-400">Analyzing interview data</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen animated-bg relative">
      <ThreeDBackground />
      
      {/* Header */}
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
            >
              <div className="bg-gradient-to-r from-green-500 to-emerald-600 p-2 rounded-xl glow-green">
                <BarChart3 className="h-6 w-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white font-orbitron">HR DASHBOARD</h1>
                <p className="text-sm text-gray-300 font-mono">{user?.company || 'Interview Analytics'}</p>
              </div>
            </motion.div>
            
            <div className="flex items-center space-x-4">
              <motion.button
                onClick={loadDashboardData}
                className="p-2 rounded-lg bg-white/10 text-white hover:bg-white/20 transition-colors"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              >
                <RefreshCw className="h-4 w-4" />
              </motion.button>
              
              <div className="flex items-center space-x-2 text-sm text-gray-300">
                <div className="w-8 h-8 rounded-full bg-gradient-to-r from-green-500 to-emerald-600 flex items-center justify-center">
                  <Users className="h-4 w-4 text-white" />
                </div>
                <span className="font-medium">{user?.name}</span>
              </div>
              
              <motion.button
                onClick={logout}
                className="flex items-center space-x-2 text-sm text-gray-400 hover:text-white transition-colors btn-futuristic px-3 py-2 rounded-lg"
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

      <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8 relative z-10">
        
        {/* Welcome Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-8"
        >
          <h2 className="text-3xl font-bold text-white mb-2 font-orbitron">
            Welcome back, {user?.name}! 👋
          </h2>
          <p className="text-gray-300">Here's what's happening with your interviews today.</p>
        </motion.div>

        {/* Stats Cards */}
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8"
        >
          {[
            {
              title: 'Total Interviews',
              value: stats.totalInterviews,
              icon: Users,
              color: 'from-cyber-blue to-blue-600',
              change: '+12%'
            },
            {
              title: 'Today\'s Interviews',
              value: stats.todayInterviews,
              icon: Clock,
              color: 'from-green-500 to-emerald-600',
              change: '+5%'
            },
            {
              title: 'Average Score',
              value: `${stats.averageScore}%`,
              icon: Award,
              color: 'from-purple-500 to-pink-600',
              change: '+3%'
            },
            {
              title: 'Completion Rate',
              value: `${stats.completionRate}%`,
              icon: TrendingUp,
              color: 'from-orange-500 to-red-600',
              change: '+8%'
            }
          ].map((stat, index) => (
            <motion.div
              key={stat.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 + index * 0.1 }}
              className="glass rounded-2xl p-6 border border-white/10 holographic"
              whileHover={{ scale: 1.02, y: -5 }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`p-3 rounded-xl bg-gradient-to-r ${stat.color}`}>
                  <stat.icon className="h-6 w-6 text-white" />
                </div>
                <span className="text-green-400 text-sm font-medium">{stat.change}</span>
              </div>
              <h3 className="text-2xl font-bold text-white mb-1 font-orbitron">{stat.value}</h3>
              <p className="text-gray-400 text-sm">{stat.title}</p>
            </motion.div>
          ))}
        </motion.div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          
          {/* Interview Trends */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="glass rounded-3xl p-6 border border-white/10"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold text-white font-orbitron">Interview Trends</h3>
              <select
                value={selectedTimeframe}
                onChange={(e) => setSelectedTimeframe(e.target.value)}
                className="bg-dark-200/50 border border-white/10 rounded-lg px-3 py-1 text-white text-sm"
              >
                <option value="week">This Week</option>
                <option value="month">This Month</option>
                <option value="quarter">This Quarter</option>
              </select>
            </div>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                <XAxis dataKey="name" stroke="#9CA3AF" />
                <YAxis stroke="#9CA3AF" />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#1F2937', 
                    border: '1px solid #374151',
                    borderRadius: '8px'
                  }}
                />
                <Bar dataKey="interviews" fill="#00d4ff" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </motion.div>

          {/* Skills Distribution */}
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
            className="glass rounded-3xl p-6 border border-white/10"
          >
            <h3 className="text-xl font-semibold text-white mb-6 font-orbitron">Skills Assessment</h3>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={skillsData}
                  cx="50%"
                  cy="50%"
                  outerRadius={100}
                  dataKey="value"
                  label={({ name, value }) => `${name}: ${value}%`}
                >
                  {skillsData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </motion.div>
        </div>

        {/* Recent Interviews */}
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="glass rounded-3xl p-6 border border-white/10"
        >
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-semibold text-white font-orbitron">Recent Interviews</h3>
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search candidates..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10 pr-4 py-2 bg-dark-200/50 border border-white/10 rounded-lg text-white text-sm placeholder-gray-400 focus:ring-2 focus:ring-cyber-blue focus:border-cyber-blue"
                />
              </div>
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="bg-dark-200/50 border border-white/10 rounded-lg px-3 py-2 text-white text-sm"
              >
                <option value="all">All Status</option>
                <option value="completed">Completed</option>
                <option value="in-progress">In Progress</option>
                <option value="stopped">Stopped</option>
              </select>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-white/10">
                  <th className="text-left py-3 px-4 text-gray-300 font-medium">Candidate</th>
                  <th className="text-left py-3 px-4 text-gray-300 font-medium">Position</th>
                  <th className="text-left py-3 px-4 text-gray-300 font-medium">Score</th>
                  <th className="text-left py-3 px-4 text-gray-300 font-medium">Status</th>
                  <th className="text-left py-3 px-4 text-gray-300 font-medium">Date</th>
                  <th className="text-left py-3 px-4 text-gray-300 font-medium">Actions</th>
                </tr>
              </thead>
              <tbody>
                {stats.recentInterviews.length > 0 ? (
                  stats.recentInterviews.map((interview, index) => (
                    <motion.tr
                      key={interview.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: 0.6 + index * 0.1 }}
                      className="border-b border-white/5 hover:bg-white/5 transition-colors"
                    >
                      <td className="py-4 px-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-8 h-8 rounded-full bg-gradient-to-r from-cyber-blue to-purple-600 flex items-center justify-center">
                            <span className="text-white text-sm font-medium">
                              {interview.studentInfo.name.charAt(0)}
                            </span>
                          </div>
                          <div>
                            <div className="text-white font-medium">{interview.studentInfo.name}</div>
                            <div className="text-gray-400 text-sm">{interview.studentInfo.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="text-white">{interview.jobDescription.title}</div>
                        <div className="text-gray-400 text-sm">{interview.jobDescription.company}</div>
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center space-x-2">
                          <div className={`text-lg font-bold ${
                            interview.result && interview.result.overallScore >= 80 ? 'text-green-400' :
                            interview.result && interview.result.overallScore >= 60 ? 'text-yellow-400' :
                            'text-red-400'
                          }`}>
                            {interview.result ? `${interview.result.overallScore}%` : 'N/A'}
                          </div>
                          {interview.result && interview.result.overallScore >= 80 && (
                            <Star className="h-4 w-4 text-yellow-400" />
                          )}
                        </div>
                      </td>
                      <td className="py-4 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          interview.status === 'completed' ? 'bg-green-500/20 text-green-400 border border-green-500/30' :
                          interview.status === 'in-progress' ? 'bg-blue-500/20 text-blue-400 border border-blue-500/30' :
                          interview.status === 'stopped' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                          'bg-gray-500/20 text-gray-400 border border-gray-500/30'
                        }`}>
                          {interview.status}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-gray-300">
                        {new Date(interview.createdAt).toLocaleDateString()}
                      </td>
                      <td className="py-4 px-4">
                        <div className="flex items-center space-x-2">
                          <motion.button
                            className="p-2 rounded-lg bg-cyber-blue/20 text-cyber-blue hover:bg-cyber-blue/30 transition-colors"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                          >
                            <Eye className="h-4 w-4" />
                          </motion.button>
                          <motion.button
                            className="p-2 rounded-lg bg-green-500/20 text-green-400 hover:bg-green-500/30 transition-colors"
                            whileHover={{ scale: 1.1 }}
                            whileTap={{ scale: 0.9 }}
                          >
                            <Download className="h-4 w-4" />
                          </motion.button>
                        </div>
                      </td>
                    </motion.tr>
                  ))
                ) : (
                  <tr>
                    <td colSpan={6} className="py-8 text-center text-gray-400">
                      No interviews found. Candidates will appear here after completing interviews.
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default HRDashboard;