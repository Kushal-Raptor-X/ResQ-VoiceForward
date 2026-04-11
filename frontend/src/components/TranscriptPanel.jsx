import { useEffect, useRef } from "react";

export default function TranscriptPanel({ transcript }) {
  const endRef = useRef(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth", block: "end" });
  }, [transcript]);

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="space-y-6">
        {transcript.length === 0 && (
          <div className="text-center text-[#888888] py-12">
            <p className="text-lg">Waiting for call to begin...</p>
            <p className="text-sm mt-2">Transcript will appear here in real-time</p>
          </div>
        )}
        {transcript.map((line, index) => (
          <div key={`${line.time}-${index}`} className="flex gap-4 border-b border-[#1a1a1a] pb-4 last:border-0">
            {/* Timestamp on the left */}
            <div className="flex-shrink-0">
              <span className="font-mono text-xs text-[#555555]">[{line.time}]</span>
            </div>
            
            {/* Speaker and text */}
            <div className="flex-1">
              <div className="mb-2">
                <span 
                  className="text-sm font-bold uppercase tracking-wider" 
                  style={{ 
                    color: line.speaker === "OPERATOR" ? "#22c55e" : "#888888" 
                  }}
                >
                  {line.speaker}:
                </span>
              </div>
              <div className="text-base leading-relaxed text-[#e5e5e5]">
                {line.isRisk ? (
                  <span className="font-medium text-[#f59e0b]">{line.text}</span>
                ) : (
                  <span>{line.text}</span>
                )}
              </div>
            </div>
          </div>
        ))}
        <div ref={endRef} />
      </div>
    </div>
  );
}
