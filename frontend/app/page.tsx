'use client'

import { useState } from 'react'
import URLInput from '@/components/URLInput'
import VideoCard from '@/components/VideoCard'
import ChatPanel from '@/components/ChatPanel'
import CostAnalysisCard from '@/components/CostAnalysisCard'
import { ProcessResponse } from '@/lib/api'

export default function Home() {
  const [isProcessing, setIsProcessing] = useState(false)
  const [processedData, setProcessedData] = useState<ProcessResponse | null>(null)

  const handleProcessed = (data: ProcessResponse) => {
    setProcessedData(data)
  }

  return (
    <main
      style={{
        minHeight: '100vh',
        background:
          'radial-gradient(circle at top left, rgba(124,111,247,0.14), transparent 420px), radial-gradient(circle at top right, rgba(6,182,212,0.12), transparent 420px), #08090b',
        color: '#f4f4f5',
        padding: '32px 24px',
      }}
    >
      <div
        style={{
          width: '100%',
          maxWidth: '1540px',
          margin: '0 auto',
        }}
      >
        <URLInput
          onProcessed={handleProcessed}
          isProcessing={isProcessing}
          setIsProcessing={setIsProcessing}
        />

        {processedData && (
          <div
            style={{
              padding: '14px 18px',
              borderRadius: '12px',
              marginBottom: '24px',
              background:
                'linear-gradient(90deg, rgba(0,229,160,0.13), rgba(0,229,160,0.05))',
              border: '1px solid rgba(0,229,160,0.28)',
              color: '#20f5b3',
              fontSize: '13px',
              display: 'flex',
              alignItems: 'center',
              gap: '10px',
              boxShadow: '0 14px 40px rgba(0,0,0,0.28)',
            }}
          >
            <span
              style={{
                width: '22px',
                height: '22px',
                borderRadius: '7px',
                background: 'rgba(32,245,179,0.16)',
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              ✓
            </span>

            <span style={{ lineHeight: 1.5 }}>
              {processedData.message} — {processedData.total_chunks_embedded} chunks embedded into ChromaDB
            </span>

            <span
              style={{
                marginLeft: 'auto',
                fontSize: '11px',
                color: '#8ef7d1',
                fontFamily: 'monospace',
                background: 'rgba(0,0,0,0.28)',
                border: '1px solid rgba(255,255,255,0.06)',
                padding: '4px 9px',
                borderRadius: '999px',
                whiteSpace: 'nowrap',
              }}
            >
              session: {processedData.session_id.slice(0, 8)}...
            </span>
          </div>
        )}

        {processedData ? (
  <>
    <section
      style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '22px',
        marginBottom: '24px',
      }}
    >
      <VideoCard
        video={processedData.video_a}
        label="A"
        url={processedData.video_a.url}
      />
      <VideoCard
        video={processedData.video_b}
        label="B"
        url={processedData.video_b.url}
      />
    </section>

    {/* ✅ ADD IT HERE (right below video cards) */}
    <div style={{ marginBottom: '24px' }}>
      <CostAnalysisCard />
    </div>
  </>
) : (
          <section
            style={{
              display: 'grid',
              gridTemplateColumns: '1fr 1fr',
              gap: '22px',
              marginBottom: '24px',
            }}
          >
            {(['A', 'B'] as const).map((label) => {
              const color = label === 'A' ? '#7c6ff7' : '#06b6d4'

              return (
                <div
                  key={label}
                  style={{
                    background:
                      'linear-gradient(180deg, rgba(255,255,255,0.045), rgba(255,255,255,0.018))',
                    border: '1px solid rgba(255,255,255,0.08)',
                    borderRadius: '16px',
                    minHeight: '300px',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '14px',
                    borderTop: `3px solid ${color}`,
                    boxShadow: '0 18px 50px rgba(0,0,0,0.3)',
                  }}
                >
                  <div
                    style={{
                      width: '54px',
                      height: '54px',
                      borderRadius: '16px',
                      background: `${color}18`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      fontSize: '24px',
                      fontWeight: 800,
                      color,
                      border: `1px solid ${color}40`,
                    }}
                  >
                    {label}
                  </div>

                  <div style={{ textAlign: 'center' }}>
                    <p
                      style={{
                        fontSize: '15px',
                        fontWeight: 700,
                        color: '#d4d4d8',
                        marginBottom: '5px',
                      }}
                    >
                      Video {label}
                    </p>
                    <p style={{ fontSize: '13px', color: '#71717a' }}>
                      Enter URL above to analyze
                    </p>
                  </div>
                </div>
              )
            })}
          </section>
        )}

        {processedData ? (
          <ChatPanel
            sessionId={processedData.session_id}
            suggestedQuestions={processedData.suggested_questions}
          />
        ) : (
          <section
            style={{
              background:
                'linear-gradient(180deg, rgba(255,255,255,0.045), rgba(255,255,255,0.018))',
              border: '1px solid rgba(255,255,255,0.08)',
              borderRadius: '16px',
              minHeight: '320px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexDirection: 'column',
              gap: '12px',
              boxShadow: '0 18px 50px rgba(0,0,0,0.3)',
            }}
          >
            <div style={{ fontSize: '38px' }}>💬</div>
            <p style={{ fontSize: '15px', color: '#d4d4d8', fontWeight: 700 }}>
              Chat will appear after videos are processed
            </p>
            <p style={{ fontSize: '13px', color: '#71717a' }}>
              Ask about engagement, hooks, structure, and improvements.
            </p>
          </section>
        )}

        <footer
          style={{
            marginTop: '28px',
            textAlign: 'center',
            fontSize: '12px',
            color: '#52525b',
          }}
        >
          CreatorJoy RAG · FastAPI + LangChain + ChromaDB + Gemini · Built by Asad Shaikh
        </footer>
      </div>
    </main>
  )
}