'use client'
import { useState } from 'react'
import { processVideos, ProcessResponse } from '@/lib/api'

interface URLInputProps {
  onProcessed: (data: ProcessResponse) => void
  isProcessing: boolean
  setIsProcessing: (v: boolean) => void
}

export default function URLInput({ onProcessed, isProcessing, setIsProcessing }: URLInputProps) {
  const [urlA, setUrlA] = useState('')
  const [urlB, setUrlB] = useState('')
  const [error, setError] = useState('')
  const [status, setStatus] = useState('')

  const handleProcess = async () => {
    if (!urlA.trim() || !urlB.trim()) {
      setError('Please enter both video URLs')
      return
    }
    setError('')
    setStatus('Processing videos...')
    setIsProcessing(true)

    try {
      setStatus('Fetching transcripts and metadata...')
      const data = await processVideos(urlA.trim(), urlB.trim())
      setStatus('Embedding into vector database...')
      await new Promise(r => setTimeout(r, 500))
      setStatus('')
      onProcessed(data)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to process videos')
      setStatus('')
    } finally {
      setIsProcessing(false)
    }
  }

  return (
  <section
    style={{
      background:
        'linear-gradient(180deg, rgba(255,255,255,0.055), rgba(255,255,255,0.022))',
      border: '1px solid rgba(255,255,255,0.09)',
      borderRadius: '18px',
      padding: '30px',
      marginBottom: '26px',
      boxShadow: '0 24px 70px rgba(0,0,0,0.35)',
    }}
  >
    <div
      style={{
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        gap: '20px',
        marginBottom: '24px',
      }}
    >
      <div>
        <h1
          style={{
            fontSize: '26px',
            lineHeight: 1.15,
            fontWeight: 800,
            marginBottom: '8px',
            background: 'linear-gradient(90deg, #8b82ff, #22d3ee)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            letterSpacing: 0,
          }}
        >
          CreatorJoy — RAG Video Analyzer
        </h1>

        <p
          style={{
            fontSize: '14px',
            lineHeight: 1.55,
            color: '#8b95a7',
            maxWidth: '760px',
          }}
        >
          Compare two videos using AI. Get engagement insights, hook analysis, and improvement suggestions.
        </p>
      </div>

      <div
        style={{
          padding: '6px 10px',
          borderRadius: '999px',
          background: 'rgba(32,245,179,0.1)',
          border: '1px solid rgba(32,245,179,0.18)',
          color: '#20f5b3',
          fontSize: '11px',
          fontWeight: 700,
          whiteSpace: 'nowrap',
        }}
      >
        RAG READY
      </div>
    </div>

    <div
      style={{
        display: 'grid',
        gridTemplateColumns: '1fr 1fr',
        gap: '14px',
        marginBottom: '16px',
      }}
    >
      {/* Video A */}
      <div>
        <label
          style={{
            display: 'block',
            fontSize: '11px',
            fontWeight: 800,
            color: '#8b82ff',
            marginBottom: '8px',
            letterSpacing: '0.08em',
          }}
        >
          VIDEO A — YouTube / Instagram
        </label>

        <input
          value={urlA}
          onChange={e => setUrlA(e.target.value)}
          placeholder="https://youtube.com/watch?v=..."
          disabled={isProcessing}
          style={{
            width: '100%',
            height: '44px',
            padding: '0 14px',
            background: 'rgba(7,8,12,0.9)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '11px',
            color: '#f8fafc',
            fontSize: '14px',
            outline: 'none',
            opacity: isProcessing ? 0.6 : 1,
            boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.035)',
          }}
        />
      </div>

      {/* Video B */}
      <div>
        <label
          style={{
            display: 'block',
            fontSize: '11px',
            fontWeight: 800,
            color: '#22d3ee',
            marginBottom: '8px',
            letterSpacing: '0.08em',
          }}
        >
          VIDEO B — YouTube / Instagram
        </label>

        <input
          value={urlB}
          onChange={e => setUrlB(e.target.value)}
          placeholder="https://instagram.com/reel/..."
          disabled={isProcessing}
          style={{
            width: '100%',
            height: '44px',
            padding: '0 14px',
            background: 'rgba(7,8,12,0.9)',
            border: '1px solid rgba(255,255,255,0.1)',
            borderRadius: '11px',
            color: '#f8fafc',
            fontSize: '14px',
            outline: 'none',
            opacity: isProcessing ? 0.6 : 1,
            boxShadow: 'inset 0 1px 0 rgba(255,255,255,0.035)',
          }}
        />
      </div>
    </div>

    {error && (
      <div
        style={{
          padding: '12px 14px',
          borderRadius: '10px',
          marginBottom: '14px',
          background: 'rgba(248,113,113,0.11)',
          border: '1px solid rgba(248,113,113,0.3)',
          color: '#fca5a5',
          fontSize: '13px',
          lineHeight: 1.45,
        }}
      >
        ⚠️ {error}
      </div>
    )}

    {status && (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
          padding: '12px 14px',
          borderRadius: '10px',
          marginBottom: '14px',
          background: 'rgba(124,111,247,0.12)',
          border: '1px solid rgba(124,111,247,0.28)',
          color: '#c4b5fd',
          fontSize: '13px',
        }}
      >
        <div className="spinner" />
        {status}
      </div>
    )}

      <button
        onClick={handleProcess}
        disabled={isProcessing || !urlA.trim() || !urlB.trim()}
        style={{
          width: '100%', padding: '12px',
          background: isProcessing ? '#333' : 'linear-gradient(135deg, #7c6ff7, #06b6d4)',
          color: 'white', border: 'none', borderRadius: '10px',
          fontSize: '14px', fontWeight: 600, cursor: isProcessing ? 'not-allowed' : 'pointer',
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
          transition: 'opacity 0.2s',
          opacity: isProcessing || !urlA.trim() || !urlB.trim() ? 0.6 : 1,
        }}
      >
        {isProcessing ? (
          <><div className="spinner" /> Analyzing Videos...</>
        ) : (
          '⚡ Analyze Videos'
        )}
      </button>
    </section>
  )
}