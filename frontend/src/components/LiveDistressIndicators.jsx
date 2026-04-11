import { motion } from "framer-motion";
import { useEffect, useState } from "react";

const indicators = [
  { 
    key: "distress_intensity", 
    label: "DISTRESS INTENSITY", 
    icon: "⚠️",
    color: "#ef4444",
    description: "Overall emotional distress level"
  },
  { 
    key: "cognitive_coherence", 
    label: "COGNITIVE COHERENCE", 
    icon: "🧠",
    color: "#3b82f6",
    description: "Clarity and logical flow of thought"
  },
  { 
    key: "agitation", 
    label: "AGITATION", 
    icon: "⚡",
    color: "#f59e0b",
    description: "Physical/emotional restlessness"
  },
  { 
    key: "dissociation", 
    label: "DISSOCIATION MARKERS", 
    icon: "🌀",
    color: "#a78bfa",
    description: "Detachment from reality indicators"
  },
  { 
    key: "suicidal_ideation", 
    label: "SUICIDAL IDEATION", 
    icon: "🚨",
    color: "#dc2626",
    description: "Self-harm or suicide risk indicators"
  },
  { 
    key: "operator_fatigue", 
    label: "OPERATOR FATIGUE", 
    icon: "😓",
    color: "#6b7280",
    description: "Operator stress and vicarious trauma"
  },
];

const getLevelColor = (value) => {
  if (value >= 80) return "#dc2626"; // Critical - dark red
  if (value >= 60) return "#ef4444"; // High - red
  if (value >= 40) return "#f59e0b"; // Medium - amber
  if (value >= 20) return "#fbbf24"; // Low-Medium - yellow
  return "#22c55e"; // Low - green
};

const getLevelText = (value) => {
  if (value >= 80) return "CRITICAL";
  if (value >= 60) return "HIGH";
  if (value >= 40) return "MEDIUM";
  if (value >= 20) return "LOW-MED";
  return "LOW";
};

export default function LiveDistressIndicators({ indicators: indicatorData, isLive = false }) {
  const [animatedValues, setAnimatedValues] = useState({});

  useEffect(() => {
    // Initialize animated values
    const initial = {};
    indicators.forEach(ind => {
      initial[ind.key] = indicatorData?.[ind.key] || 0;
    });
    setAnimatedValues(initial);
  }, [indicatorData]);

  return (
    <div className="rounded-lg border border-[#2a2a2a] bg-[#111111] p-5">
      {/* Header */}
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-white tracking-wider">
          LIVE DISTRESS MONITORING
        </h3>
        {isLive && (
          <div className="flex items-center gap-2">
            <span className="h-2 w-2 rounded-full bg-red-500 animate-pulse"></span>
            <span className="text-xs text-red-500 font-bold">LIVE</span>
          </div>
        )}
      </div>

      {/* Indicators Grid */}
      <div className="space-y-4">
        {indicators.map((indicator, index) => {
          const value = indicatorData?.[indicator.key] || 0;
          const levelColor = getLevelColor(value);
          const levelText = getLevelText(value);

          return (
            <motion.div
              key={indicator.key}
              className="space-y-2"
              initial={{ opacity: 0, x: -10 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ duration: 0.3, delay: index * 0.05 }}
            >
              {/* Label Row */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-base">{indicator.icon}</span>
                  <span className="text-xs font-bold text-[#e5e5e5] tracking-wide">
                    {indicator.label}
                  </span>
                </div>
                <div className="flex items-center gap-3">
                  <span 
                    className="text-xs font-bold tracking-wider"
                    style={{ color: levelColor }}
                  >
                    {levelText}
                  </span>
                  <span className="text-xs font-bold text-white w-10 text-right font-mono">
                    {value}%
                  </span>
                </div>
              </div>

              {/* Progress Bar */}
              <div className="relative h-2 rounded-full bg-[#1a1a1a] overflow-hidden">
                <motion.div
                  className="absolute inset-y-0 left-0 rounded-full"
                  style={{ 
                    backgroundColor: levelColor,
                    boxShadow: `0 0 8px ${levelColor}40`
                  }}
                  initial={{ width: 0 }}
                  animate={{ width: `${value}%` }}
                  transition={{ 
                    duration: 0.8, 
                    ease: "easeOut",
                    delay: index * 0.05
                  }}
                />
                
                {/* Pulse effect for high values */}
                {value >= 60 && isLive && (
                  <motion.div
                    className="absolute inset-y-0 left-0 rounded-full"
                    style={{ 
                      backgroundColor: levelColor,
                      width: `${value}%`
                    }}
                    animate={{ 
                      opacity: [0.5, 0.8, 0.5],
                    }}
                    transition={{ 
                      duration: 1.5, 
                      repeat: Infinity,
                      ease: "easeInOut"
                    }}
                  />
                )}
              </div>

              {/* Description (only show for critical indicators) */}
              {value >= 60 && (
                <motion.p 
                  className="text-xs text-[#888888] italic"
                  initial={{ opacity: 0, height: 0 }}
                  animate={{ opacity: 1, height: "auto" }}
                  transition={{ duration: 0.3 }}
                >
                  {indicator.description}
                </motion.p>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Alert Banner for Critical Levels */}
      {Object.entries(indicatorData || {}).some(([key, value]) => 
        key === "suicidal_ideation" && value >= 70
      ) && (
        <motion.div
          className="mt-4 rounded-lg border-2 border-red-600 bg-red-950 p-3"
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.3 }}
        >
          <div className="flex items-center gap-2">
            <span className="text-xl">🚨</span>
            <div>
              <p className="text-sm font-bold text-red-400">CRITICAL ALERT</p>
              <p className="text-xs text-red-300 mt-1">
                Suicidal ideation indicators detected. Follow crisis protocol immediately.
              </p>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}
