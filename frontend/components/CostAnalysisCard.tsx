'use client'

export default function CostAnalysisCard() {
  const whisperPerMin = 0.006
  const geminiFlashPer1KTokens = 0.00015

  const avgVideoMinutes = 5
  const whisperCost = whisperPerMin * avgVideoMinutes

  const geminiCost = 0.0005 // rough avg per video (very small)
  const totalPerVideo = whisperCost + geminiCost

  const creatorsPerDay = 1000
  const dailyCost = totalPerVideo * creatorsPerDay

  const openAIDaily = 120
  const savings = ((openAIDaily - dailyCost) / openAIDaily) * 100

  return (
    <div style={{
      background: '#111',
      border: '1px solid #222',
      borderRadius: '16px',
      padding: '16px',
      marginTop: '16px'
    }}>
      <h2 style={{ fontSize: '14px', fontWeight: 700, marginBottom: '12px' }}>
        💰 Cost Analysis
      </h2>

      <div style={{ fontSize: '12px', color: '#aaa', marginBottom: '10px' }}>
        Per video analysis breakdown
      </div>

      <div style={{ display: 'grid', gap: '6px', fontSize: '12px' }}>
        <div>🎙 Whisper: $0.006/min × {avgVideoMinutes} min = <b>${whisperCost.toFixed(4)}</b></div>
        <div>🧠 Gemini Embeddings: <b>FREE</b></div>
        <div>⚡ Gemini Flash: ~$0.00015/1K tokens = <b>${geminiCost.toFixed(4)}</b></div>
        <div>🗄 ChromaDB: <b>FREE (self-hosted)</b></div>
      </div>

      <hr style={{ border: '1px solid #222', margin: '12px 0' }} />

      <div style={{ fontSize: '12px', display: 'grid', gap: '6px' }}>
        <div>📦 Per video total: <b>${totalPerVideo.toFixed(4)}</b></div>
        <div>📊 1000 creators/day: <b>${dailyCost.toFixed(2)} / day</b></div>
      </div>

      <div style={{
        marginTop: '12px',
        padding: '10px',
        borderRadius: '10px',
        background: 'rgba(34,197,94,0.1)',
        border: '1px solid rgba(34,197,94,0.3)',
        color: '#22c55e',
        fontWeight: 700,
        fontSize: '13px'
      }}>
        🚀 SAVINGS: ~{savings.toFixed(0)}% cheaper vs OpenAI GPT-4
      </div>
    </div>
  )
}