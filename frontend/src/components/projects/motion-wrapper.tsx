'use client';

import { motion, Variants } from 'framer-motion';

export const containerVariants: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.2,
    },
  },
};

export const itemVariants: Variants = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: 'spring', stiffness: 50, damping: 15 } },
};

export function MotionContainer({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <motion.div variants={containerVariants} initial="hidden" animate="show" className={className}>
      {children}
    </motion.div>
  );
}

export function MotionItem({
  children,
  className,
}: {
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <motion.div variants={itemVariants} className={className}>
      {children}
    </motion.div>
  );
}

export function GlassCard({
  children,
  className,
  hoverEffect = true,
}: {
  children: React.ReactNode;
  className?: string;
  hoverEffect?: boolean;
}) {
  return (
    <motion.div
      whileHover={
        hoverEffect ? { scale: 1.01, boxShadow: '0 20px 40px -10px rgba(0,0,0,0.5)' } : {}
      }
      className={`
                relative backdrop-blur-2xl rounded-[24px] border border-white/[0.08] 
                bg-gradient-to-b from-white/[0.08] to-transparent 
                shadow-[0_8px_32px_0_rgba(0,0,0,0.37)] 
                overflow-hidden transition-colors duration-500
                ${className}
            `}
    >
      {/* Glossy Reflection Gradient */}
      <div className="absolute inset-0 bg-gradient-to-tr from-white/[0.03] via-transparent to-transparent pointer-events-none" />

      {/* Content */}
      <div className="relative z-10">{children}</div>
    </motion.div>
  );
}

export function MotionDiv({ children, ...props }: any) {
  return <motion.div {...props}>{children}</motion.div>;
}
