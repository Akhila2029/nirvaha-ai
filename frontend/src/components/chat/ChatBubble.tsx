import React from 'react';
import { motion } from 'framer-motion';
import { cn } from '../../lib/utils';

interface ChatBubbleProps {
  role: 'user' | 'assistant';
  content: string;
}

const ChatBubble: React.FC<ChatBubbleProps> = ({ role, content }) => {
  const isAssistant = role === 'assistant';

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      className={cn(
        "flex w-full mb-4",
        isAssistant ? "justify-start" : "justify-end"
      )}
    >
      <div
        className={cn(
          "max-w-[80%] px-6 py-4 rounded-[1.5rem] shadow-sm",
          isAssistant 
            ? "glass rounded-tl-none text-foreground border border-slate-200" 
            : "bg-primary text-white rounded-tr-none"
        )}
      >
        <p className="text-sm md:text-base leading-relaxed whitespace-pre-wrap">{content}</p>
      </div>
    </motion.div>
  );
};

export default ChatBubble;
