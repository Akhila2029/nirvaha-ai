import React from 'react';
import { motion } from 'framer-motion';
import { Link } from 'react-router-dom';
import { Sparkles, Shield, Heart, ArrowRight } from 'lucide-react';

const LandingPage = () => {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Navbar */}
      <nav className="p-6 flex justify-between items-center glass sticky top-0 z-50">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-lg">N</div>
          <span className="text-2xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-primary to-primary/60">Nirvaha</span>
        </div>
        <div className="flex gap-4">
          <Link to="/chat" className="px-5 py-2 bg-primary text-white rounded-full hover:shadow-xl transition-all hover:-translate-y-1 text-sm font-medium">Get Started</Link>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="flex-1">
        <section className="relative pt-20 pb-32 px-6 overflow-hidden">
          {/* Background Blobs */}
          <div className="absolute top-0 -left-4 w-72 h-72 bg-primary/10 rounded-full blur-3xl" />
          <div className="absolute bottom-0 -right-4 w-96 h-96 bg-slate-100/30 rounded-full blur-3xl" />

          <div className="max-w-6xl mx-auto text-center relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.8 }}
            >
              <h1 className="text-6xl md:text-8xl font-black mb-6 tracking-tight">
                Your AI Companion for <br />
                <span className="text-primary italic">Mental Wellness.</span>
              </h1>
              <p className="text-xl md:text-2xl text-muted-foreground mb-10 max-w-2xl mx-auto leading-relaxed">
                Experience a compassionate, AI-driven sanctuary designed to support your journey towards inner peace and emotional balance.
              </p>
              <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Link to="/chat" className="px-10 py-5 bg-primary text-white text-lg font-bold rounded-2xl hover:shadow-2xl hover:shadow-primary/20 transition-all hover:scale-105 flex items-center gap-2 justify-center">
                  Start Chatting <ArrowRight className="w-5 h-5" />
                </Link>
                <a href="#features" className="px-10 py-5 bg-white border border-slate-200 text-lg font-semibold rounded-2xl hover:bg-slate-100 transition-all">
                  Explore Features
                </a>
              </div>
            </motion.div>
          </div>
        </section>

        {/* Features */}
        <section id="features" className="py-24 px-6 bg-slate-100/30">
          <div className="max-w-6xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl font-bold mb-4">Why Nirvaha?</h2>
              <p className="text-muted-foreground">Modern tools for modern minds.</p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              {[
                {
                  icon: <Heart className="w-8 h-8 text-primary" />,
                  title: "Compassionate AI",
                  desc: "Our AI is trained with empathy first, providing a safe space to express yourself freely."
                },
                {
                  icon: <Shield className="w-8 h-8 text-primary" />,
                  title: "Private & Secure",
                  desc: "Your data is yours alone. We use advanced encryption to ensure your sanctuary remains private."
                },
                {
                  icon: <Sparkles className="w-8 h-8 text-primary" />,
                  title: "Personalized Care",
                  desc: "Using RAG technology, Nirvaha understands your unique context to provide tailored support."
                }
              ].map((f, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.2 }}
                  className="p-8 bg-card rounded-3xl border border-slate-200 shadow-sm hover:shadow-xl transition-shadow group"
                >
                  <div className="mb-6 p-4 bg-primary/5 rounded-2xl w-fit group-hover:scale-110 transition-transform">
                    {f.icon}
                  </div>
                  <h3 className="text-2xl font-bold mb-3">{f.title}</h3>
                  <p className="text-muted-foreground leading-relaxed">{f.desc}</p>
                </motion.div>
              ))}
            </div>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="py-12 px-6 border-t border-slate-200 bg-white">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-white font-bold shadow-md">N</div>
            <span className="text-xl font-bold tracking-tight">Nirvaha</span>
          </div>
          <p className="text-sm text-muted-foreground">© 2026 Nirvaha. Compassionately built for you.</p>
          <div className="flex gap-6 text-sm text-muted-foreground">
            <a href="#" className="hover:text-primary transition-colors">Privacy</a>
            <a href="#" className="hover:text-primary transition-colors">Terms</a>
            <a href="#" className="hover:text-primary transition-colors">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default LandingPage;
