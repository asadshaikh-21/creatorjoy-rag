'use client'
import { VideoInfo } from '@/lib/api'

interface VideoCardProps {
  video: VideoInfo
  label: 'A' | 'B'
  url: string
}

const accent = { A: '#7c6ff7', B: '#06b6d4' }
const accentDim = { A: 'rgba(124,111,247,0.12)', B: 'rgba(6,182,212,0.12)' }

function formatNum(n: number): string {
  if (!n) return '0'
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return n.toString()
}

function getEmbedUrl(url: string): string | null {
  try {
    if (url.includes('youtube.com') || url.includes('youtu.be')) {
      const match = url.match(/(?:v=|youtu\.be\/)([^&?#]+)/)
      if (match) return `https://www.youtube.com/embed/${match[1]}`
    }
  } catch {}
  return null
}

export default function VideoCard({ video, label, url }: VideoCardProps) {
  const meta = video.metadata
  const color = accent[label]
  const dimColor = accentDim[label]
  const embedUrl = getEmbedUrl(url)
  const thumbnailSrc =
  meta.platform === 'instagram' && meta.thumbnail
    ? `http://localhost:5000/api/image-proxy?url=${encodeURIComponent(meta.thumbnail)}`
    : meta.thumbnail

  const stats = [
    { label: 'Views', value: formatNum(meta.views || 0), icon: '👁' },
    { label: 'Likes', value: formatNum(meta.likes || 0), icon: '❤️' },
    { label: 'Comments', value: formatNum(meta.comments || 0), icon: '💬' },
    { label: 'Engagement', value: `${meta.engagement_rate || 0}%`, icon: '📈' },
  ]

  return (
    <div style={{
      background: '#111', border: `1px solid #222`,
      borderRadius: '16px', overflow: 'hidden',
      borderTop: `3px solid ${color}`,
    }}>
      {/* Label */}
      <div style={{
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        padding: '14px 16px',
        background: dimColor,
        borderBottom: '1px solid #1a1a1a',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '28px', height: '28px', borderRadius: '8px',
            background: color, display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontWeight: 800, fontSize: '14px', color: 'white',
          }}>
            {label}
          </div>
          <span style={{ fontSize: '12px', fontWeight: 600, color }}>Video {label}</span>
        </div>
        <span style={{
          fontSize: '10px', padding: '3px 8px', borderRadius: '100px',
          background: dimColor, color, fontWeight: 600,
          border: `1px solid ${color}40`,
          textTransform: 'uppercase', letterSpacing: '0.05em',
        }}>
          {meta.platform || 'youtube'}
        </span>
      </div>

      {/* Video Player */}
    {embedUrl ? (
      <div style={{ position: 'relative', paddingBottom: '56.25%', background: '#000' }}>
        <iframe
          src={embedUrl}
          style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none' }}
          allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope"
          allowFullScreen
        />
      </div>
    ) : meta.thumbnail ? (
      <div style={{ position: 'relative', paddingBottom: '56.25%', background: '#000' }}>
        <img
  src={thumbnailSrc}
  alt={meta.title || 'Video thumbnail'}
  referrerPolicy="no-referrer"
  style={{
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    objectFit: 'cover',
  }}
/>
      </div>
    ) : (
      <div style={{
        height: '160px', background: '#0d0d0d',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '32px',
      }}>
        🎬
      </div>
    )}

      {/* Info */}
      <div style={{ padding: '16px' }}>
        <h3 style={{
          fontSize: '14px', fontWeight: 700, marginBottom: '4px',
          overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
        }}>
          {meta.title || 'Untitled Video'}
        </h3>
        <p style={{ fontSize: '12px', color: '#666', marginBottom: '14px' }}>
          by {meta.creator || 'Unknown'} {meta.follower_count !== undefined && meta.follower_count !== null
  ? `· 👥 ${formatNum(Number(meta.follower_count))} followers`
  : ''}
        </p>

        {/* Stats Grid */}
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
          {stats.map(stat => (
            <div key={stat.label} style={{
              background: '#0d0d0d', border: '1px solid #1e1e1e',
              borderRadius: '10px', padding: '10px 12px',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '2px' }}>
                <span style={{ fontSize: '10px', color: '#555' }}>{stat.label}</span>
                <span style={{ fontSize: '13px' }}>{stat.icon}</span>
              </div>
              <span style={{ fontSize: '16px', fontWeight: 700, color: stat.label === 'Engagement' ? color : '#f0f0f0' }}>
                {stat.value}
              </span>
            </div>
          ))}
        </div>

        {/* Extra meta */}
        <div style={{ marginTop: '10px', display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
          {meta.duration ? (
            <span style={{ fontSize: '11px', padding: '3px 8px', borderRadius: '100px', background: '#1a1a1a', color: '#666' }}>
              ⏱ {Math.floor(meta.duration / 60)}:{String(meta.duration % 60).padStart(2, '0')}
            </span>
          ) : null}
          {meta.upload_date ? (
            <span style={{ fontSize: '11px', padding: '3px 8px', borderRadius: '100px', background: '#1a1a1a', color: '#666' }}>
              📅 {meta.upload_date}
            </span>
          ) : null}
          {video.chunks_count ? (
            <span style={{ fontSize: '11px', padding: '3px 8px', borderRadius: '100px', background: '#1a1a1a', color: '#666' }}>
              🧩 {video.chunks_count} chunks
            </span>
          ) : null}
        </div>

        {/* Hashtags */}
        {meta.hashtags && meta.hashtags.length > 0 && (
          <div style={{ marginTop: '8px', display: 'flex', flexWrap: 'wrap', gap: '4px' }}>
            {meta.hashtags.slice(0, 5).map((tag: string) => (
              <span key={tag} style={{
                fontSize: '10px', padding: '2px 7px', borderRadius: '100px',
                background: dimColor, color, border: `1px solid ${color}30`,
              }}>
                {tag}
              </span>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}