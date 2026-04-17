import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../lib/api';
import { motion } from 'framer-motion';

const SignupPage = () => {
  const [email, setEmail] = useState('');
  const [fullName, setFullName] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    try {
      console.log('Attempting signup to 127.0.0.1:8000...');
      const response = await api.post('/signup', { email, full_name: fullName, password });
      login(response.data.access_token);
    } catch (err: any) {
      console.error('Signup error detail:', err);
      setError(err.response?.data?.detail || 'Signup failed. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-6 bg-gradient-to-br from-background via-secondary/20 to-primary/10">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="glass p-8 rounded-[2rem] w-full max-w-md shadow-2xl"
      >
        <div className="text-center mb-8">
          <Link to="/" className="inline-block w-12 h-12 bg-primary rounded-xl text-white font-bold text-2xl pt-2 mb-4">N</Link>
          <h1 className="text-3xl font-bold">Begin Your Journey</h1>
          <p className="text-muted-foreground mt-2">Join Nirvaha and start prioritized mental wellness.</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1 pl-1">Full Name</label>
            <input
              type="text"
              required
              className="w-full px-5 py-3 rounded-2xl border border-slate-200 bg-white/50 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
              placeholder="Jay Smith"
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 pl-1">Email Address</label>
            <input
              type="email"
              required
              className="w-full px-5 py-3 rounded-2xl border border-slate-200 bg-white/50 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
              placeholder="jay@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 pl-1">Password</label>
            <input
              type="password"
              required
              className="w-full px-5 py-3 rounded-2xl border border-slate-200 bg-white/50 focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          {error && <p className="text-rose-500 text-sm pl-1">{error}</p>}

          <button
            type="submit"
            disabled={loading}
            className="w-full py-4 bg-primary text-white font-bold rounded-2xl hover:shadow-xl hover:shadow-primary/20 disabled:opacity-70 transition-all active:scale-[0.98] mt-4"
          >
            {loading ? 'Creating Account...' : 'Create Account'}
          </button>
        </form>

        <p className="text-center mt-8 text-sm text-muted-foreground">
          Already have an account? <Link to="/login" className="text-primary font-bold hover:underline">Log in</Link>
        </p>
      </motion.div>
    </div>
  );
};

export default SignupPage;
