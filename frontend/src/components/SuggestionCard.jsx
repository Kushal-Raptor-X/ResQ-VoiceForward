export default function SuggestionCard(props) {
  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-[#2a2a2a] bg-[#111111] p-6">
        <h3 className="text-sm font-bold text-white">SUGGESTED RESPONSE</h3>
        <blockquote className="mt-3 text-base italic leading-relaxed text-[#e5e5e5]">
          "{props.suggestedResponse}"
        </blockquote>
        <div className="mt-4">
          <p className="text-sm font-bold text-white">NOTE:</p>
          <p className="mt-1 text-sm text-[#b0b0b0]">{props.operatorNote}</p>
        </div>
        
        <div className="mt-6 flex gap-3">
          <button
            onClick={props.onAccept}
            className="flex-1 rounded bg-green-600 px-4 py-2 text-sm font-bold text-white hover:bg-green-700 transition-colors"
          >
            ✓ ACCEPT
          </button>
          <button
            onClick={props.onModify}
            className="flex-1 rounded bg-amber-600 px-4 py-2 text-sm font-bold text-white hover:bg-amber-700 transition-colors"
          >
            ✎ MODIFY
          </button>
          <button
            onClick={props.onReject}
            className="flex-1 rounded bg-red-600 px-4 py-2 text-sm font-bold text-white hover:bg-red-700 transition-colors"
          >
            ✗ REJECT
          </button>
        </div>
      </div>
    </div>
  );
}
