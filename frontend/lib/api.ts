import axios from 'axios'

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000'

export const api = axios.create({
  baseURL: API_BASE,
  timeout: 120000,
})

export interface VideoMetadata {
  title: string
  creator: string
  views: number
  likes: number
  comments: number
  engagement_rate: number
  duration: number
  platform: string
  url: string
  thumbnail?: string
  upload_date?: string
  hashtags?: string[]
  follower_count?: string | number
}

export interface VideoInfo {
  url: string
  metadata: VideoMetadata
  transcript_preview: string
  chunks_count: number
}

export interface ProcessResponse {
  success: boolean
  session_id: string
  video_a: VideoInfo
  video_b: VideoInfo
  total_chunks_embedded: number
  message: string
  suggested_questions: string[]
}

export interface Source {
  video: string
  title: string
  chunk: string
}

export interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  timestamp: number
}

export async function processVideos(videoAUrl: string, videoBUrl: string): Promise<ProcessResponse> {
  const { data } = await api.post('/api/process-videos', {
    video_a_url: videoAUrl,
    video_b_url: videoBUrl,
  })
  return data
}

export async function streamChat(
  sessionId: string,
  question: string,
  onToken: (token: string) => void,
  onDone: () => void,
  onError: (err: string) => void
) {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      session_id: sessionId,
      question,
      stream: true,
    }),
  })

  if (!response.ok) {
    onError('Failed to connect to chat API')
    return
  }

  const reader = response.body?.getReader()
  const decoder = new TextDecoder()

  if (!reader) {
    onError('No response body')
    return
  }

  while (true) {
    const { done, value } = await reader.read()
    if (done) break

    const chunk = decoder.decode(value, { stream: true })
    const lines = chunk.split('\n')

    for (const line of lines) {
      if (!line.startsWith('data: ')) continue
      try {
        const json = JSON.parse(line.slice(6))
        if (json.type === 'token') onToken(json.content)
        if (json.type === 'done') onDone()
        if (json.type === 'error') onError(json.message)
      } catch {}
    }
  }
}