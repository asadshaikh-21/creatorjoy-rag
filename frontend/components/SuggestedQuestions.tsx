'use client'

interface SuggestedQuestionsProps {
  questions: string[]
  onSelect: (q: string) => void
  disabled: boolean
}

export default function SuggestedQuestions({ questions, onSelect, disabled }: SuggestedQuestionsProps) {
  return (
    <div style={{ marginBottom: '16px' }}>
      <p style={{ fontSize: '11px', color: '#555', marginBottom: '8px', letterSpacing: '0.06em', fontWeight: 600 }}>
        SUGGESTED QUESTIONS
      </p>
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
        {questions.map((q, i) => (
          <button
            key={i}
            onClick={() => onSelect(q)}
            disabled={disabled}
            style={{
              padding: '7px 12px',
              background: '#111', border: '1px solid #222',
              borderRadius: '100px', color: '#aaa',
              fontSize: '12px', cursor: disabled ? 'not-allowed' : 'pointer',
              opacity: disabled ? 0.5 : 1,
              transition: 'all 0.2s',
              whiteSpace: 'nowrap',
            }}
            onMouseEnter={e => {
              if (!disabled) {
                (e.target as HTMLButtonElement).style.borderColor = '#7c6ff7'
                ;(e.target as HTMLButtonElement).style.color = '#a78bfa'
              }
            }}
            onMouseLeave={e => {
              (e.target as HTMLButtonElement).style.borderColor = '#222'
              ;(e.target as HTMLButtonElement).style.color = '#aaa'
            }}
          >
            {q}
          </button>
        ))}
      </div>
    </div>
  )
}