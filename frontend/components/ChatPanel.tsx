'use client'

import { Fragment, useEffect, useRef, useState } from 'react'
import { ChatMessage, Source, streamChat } from '@/lib/api'
import SuggestedQuestions from './SuggestedQuestions'

interface ChatPanelProps {
  sessionId: string
  suggestedQuestions: string[]
}

function SourceBadge({ source }: { source: Source }) {
  const isA = source.video?.includes('A')
  const color = isA ? '#7c6ff7' : '#06b6d4'

  return (
    <span
      style={{
        display: 'inline-flex',
        alignItems: 'center',
        gap: '6px',
        padding: '5px 9px',
        borderRadius: '999px',
        marginRight: '6px',
        marginTop: '7px',
        background: isA ? 'rgba(124,111,247,0.11)' : 'rgba(6,182,212,0.11)',
        border: `1px solid ${color}42`,
        fontSize: '11px',
        color,
        maxWidth: '100%',
      }}
    >
      <strong>{source.video}</strong>
      <span style={{ color: '#9ca3af', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
        {source.title?.slice(0, 42)}
      </span>
    </span>
  )
}

function FormattedText({ text }: { text: string }) {
  return (
    <>
      {text.split('\n').map((line, lineIndex) => {
        const parts = line.split(/(\*\*[^*]+\*\*)/g)

        return (
          <Fragment key={lineIndex}>
            {parts.map((part, partIndex) => {
              if (part.startsWith('**') && part.endsWith('**')) {
                return (
                  <strong key={partIndex} style={{ color: '#ffffff', fontWeight: 800 }}>
                    {part.slice(2, -2)}
                  </strong>
                )
              }

              return <Fragment key={partIndex}>{part}</Fragment>
            })}
            {lineIndex < text.split('\n').length - 1 && <br />}
          </Fragment>
        )
      })}
    </>
  )
}

function Message({ msg }: { msg: ChatMessage }) {
  const isUser = msg.role === 'user'

  return (
    <div
      className="fade-in"
      style={{
        display: 'flex',
        flexDirection: isUser ? 'row-reverse' : 'row',
        gap: '12px',
        marginBottom: '18px',
        alignItems: 'flex-start',
      }}
    >
      <div
        style={{
          width: '34px',
          height: '34px',
          borderRadius: '10px',
          flexShrink: 0,
          background: isUser ? 'rgba(255,255,255,0.08)' : 'linear-gradient(135deg, #7c6ff7, #06b6d4)',
          border: '1px solid rgba(255,255,255,0.08)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '12px',
          fontWeight: 900,
          color: '#fff',
        }}
      >
        {isUser ? 'YOU' : 'AI'}
      </div>

      <div style={{ width: 'fit-content', maxWidth: isUser ? '58%' : '82%' }}>
        <div
          style={{
            padding: isUser ? '13px 16px' : '18px 20px',
            borderRadius: isUser ? '16px 6px 16px 16px' : '6px 16px 16px 16px',
            background: isUser
              ? 'linear-gradient(180deg, rgba(255,255,255,0.095), rgba(255,255,255,0.055))'
              : 'linear-gradient(180deg, rgba(255,255,255,0.055), rgba(255,255,255,0.025))',
            border: '1px solid rgba(255,255,255,0.09)',
            fontSize: '14px',
            lineHeight: 1.75,
            color: '#e5e7eb',
            whiteSpace: 'pre-wrap',
            boxShadow: '0 16px 38px rgba(0,0,0,0.22)',
          }}
        >
          {msg.content ? (
            <FormattedText text={msg.content} />
          ) : (
            <span className="cursor-blink" style={{ color: '#8b82ff' }}>
              Writing...
            </span>
          )}
        </div>

        {msg.sources && msg.sources.length > 0 && (
          <div style={{ marginTop: '6px' }}>
            {msg.sources.map((source, index) => (
              <SourceBadge key={index} source={source} />
            ))}
          </div>
        )}
      </div>
    </div>
  )
}

export default function ChatPanel({ sessionId, suggestedQuestions }: ChatPanelProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [isStreaming, setIsStreaming] = useState(false)
  const bottomRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const sendMessage = async (question: string) => {
    if (!question.trim() || isStreaming) return

    const userMsg: ChatMessage = {
      role: 'user',
      content: question.trim(),
      timestamp: Date.now(),
    }

    const assistantMsg: ChatMessage = {
      role: 'assistant',
      content: '',
      timestamp: Date.now(),
    }

    setMessages((prev) => [...prev, userMsg, assistantMsg])
    setInput('')
    setIsStreaming(true)

    let fullResponse = ''

    await streamChat(
      sessionId,
      question.trim(),
      (token) => {
        fullResponse += token
        setMessages((prev) => {
          const updated = [...prev]
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: fullResponse,
          }
          return updated
        })
      },
      () => {
        setIsStreaming(false)
        inputRef.current?.focus()
      },
      (err) => {
        setMessages((prev) => {
          const updated = [...prev]
          updated[updated.length - 1] = {
            ...updated[updated.length - 1],
            content: `Error: ${err}`,
          }
          return updated
        })
        setIsStreaming(false)
      }
    )
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage(input)
    }
  }

  return (
    <section
      style={{
        background:
          'linear-gradient(180deg, rgba(255,255,255,0.045), rgba(255,255,255,0.018))',
        border: '1px solid rgba(255,255,255,0.09)',
        borderRadius: '18px',
        display: 'flex',
        flexDirection: 'column',
        height: '680px',
        overflow: 'hidden',
        boxShadow: '0 24px 70px rgba(0,0,0,0.34)',
      }}
    >
      <div
        style={{
          padding: '16px 20px',
          borderBottom: '1px solid rgba(255,255,255,0.08)',
          background: 'rgba(10,11,15,0.78)',
          display: 'flex',
          alignItems: 'center',
          gap: '12px',
        }}
      >
        <div
          style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            background: '#20f5b3',
            boxShadow: '0 0 16px rgba(32,245,179,0.9)',
          }}
          className="pulse"
        />
        <div>
          <div style={{ fontSize: '14px', fontWeight: 800, color: '#f8fafc' }}>
            RAG Chat
          </div>
          <div style={{ fontSize: '12px', color: '#7c8598', marginTop: '2px' }}>
            Ask about engagement, hooks, structure, and improvements
          </div>
        </div>
        <span
          style={{
            marginLeft: 'auto',
            fontSize: '11px',
            color: '#9ca3af',
            padding: '5px 10px',
            borderRadius: '999px',
            background: 'rgba(255,255,255,0.06)',
            border: '1px solid rgba(255,255,255,0.07)',
          }}
        >
          {messages.filter((m) => m.role === 'user').length} questions
        </span>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', padding: '24px 20px' }}>
        {messages.length === 0 ? (
          <div style={{ height: '100%', display: 'grid', placeItems: 'center', textAlign: 'center' }}>
            <div>
              <div
                style={{
                  width: '58px',
                  height: '58px',
                  borderRadius: '18px',
                  display: 'grid',
                  placeItems: 'center',
                  margin: '0 auto 14px',
                  background: 'linear-gradient(135deg, rgba(124,111,247,0.18), rgba(6,182,212,0.16))',
                  border: '1px solid rgba(255,255,255,0.08)',
                  color: '#c4b5fd',
                  fontWeight: 900,
                }}
              >
                AI
              </div>
              <p style={{ fontSize: '15px', marginBottom: '5px', color: '#e5e7eb', fontWeight: 800 }}>
                Ready to analyze your videos
              </p>
              <p style={{ fontSize: '13px', color: '#71717a' }}>
                Choose a suggested question or ask your own.
              </p>
            </div>
          </div>
        ) : (
          messages.map((msg, index) => <Message key={index} msg={msg} />)
        )}
        <div ref={bottomRef} />
      </div>

      {suggestedQuestions.length > 0 && messages.length < 2 && (
        <div style={{ padding: '0 18px 14px' }}>
          <SuggestedQuestions questions={suggestedQuestions} onSelect={sendMessage} disabled={isStreaming} />
        </div>
      )}

      <div
        style={{
          padding: '16px',
          borderTop: '1px solid rgba(255,255,255,0.08)',
          background: 'rgba(10,11,15,0.82)',
          display: 'flex',
          gap: '10px',
          alignItems: 'center',
        }}
      >
        <input
          ref={inputRef}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask about engagement, hooks, improvements..."
          disabled={isStreaming}
          style={{
            flex: 1,
            height: '44px',
            padding: '0 14px',
            background: 'rgba(7,8,12,0.9)',
            border: '1px solid rgba(255,255,255,0.09)',
            borderRadius: '12px',
            color: '#f8fafc',
            fontSize: '14px',
            outline: 'none',
            opacity: isStreaming ? 0.7 : 1,
          }}
        />
        <button
          onClick={() => sendMessage(input)}
          disabled={isStreaming || !input.trim()}
          style={{
            height: '44px',
            padding: '0 18px',
            borderRadius: '12px',
            background:
              isStreaming || !input.trim()
                ? 'rgba(255,255,255,0.08)'
                : 'linear-gradient(135deg, #7c6ff7, #06b6d4)',
            color: isStreaming || !input.trim() ? '#71717a' : '#fff',
            border: '1px solid rgba(255,255,255,0.08)',
            fontSize: '13px',
            fontWeight: 800,
            cursor: isStreaming || !input.trim() ? 'not-allowed' : 'pointer',
            display: 'flex',
            alignItems: 'center',
            gap: '7px',
            minWidth: '92px',
            justifyContent: 'center',
          }}
        >
          {isStreaming ? <div className="spinner" /> : 'Send'}
        </button>
      </div>
    </section>
  )
}
