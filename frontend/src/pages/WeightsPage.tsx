import { AxiosError } from 'axios'
import { type FormEvent, useEffect, useMemo, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import WeightChart from '../components/WeightChart'
import {
  ACCESS_TOKEN_KEY,
  getApiErrorMessage,
} from '../services/api'
import {
  getWeightEntries,
  saveWeightEntry,
  type WeightEntry,
} from '../services/weights'

function localDateString(): string {
  const now = new Date()
  const timezoneOffset = now.getTimezoneOffset() * 60_000
  return new Date(now.getTime() - timezoneOffset)
    .toISOString()
    .slice(0, 10)
}

function formatRecordDate(value: string): string {
  return new Date(`${value}T00:00:00`).toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

function WeightsPage() {
  const navigate = useNavigate()
  const today = useMemo(localDateString, [])
  const [entries, setEntries] = useState<WeightEntry[]>([])
  const [weightKg, setWeightKg] = useState('')
  const [recordedOn, setRecordedOn] = useState(today)
  const [note, setNote] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadEntries() {
      try {
        const loadedEntries = await getWeightEntries()
        setEntries(loadedEntries)

        if (loadedEntries.length > 0) {
          setWeightKg(
            String(loadedEntries[loadedEntries.length - 1].weight_kg),
          )
        }
      } catch (requestError) {
        if (
          requestError instanceof AxiosError &&
          requestError.response?.status === 401
        ) {
          localStorage.removeItem(ACCESS_TOKEN_KEY)
          navigate('/login', { replace: true })
          return
        }

        setError(getApiErrorMessage(requestError))
      } finally {
        setIsLoading(false)
      }
    }

    void loadEntries()
  }, [navigate])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      const savedEntry = await saveWeightEntry({
        weight_kg: Number(weightKg),
        recorded_on: recordedOn,
        note: note.trim() || null,
      })
      setEntries((currentEntries) =>
        [
          ...currentEntries.filter(
            (entry) => entry.recorded_on !== savedEntry.recorded_on,
          ),
          savedEntry,
        ].sort((left, right) =>
          left.recorded_on.localeCompare(right.recorded_on),
        ),
      )
      setNote('')
    } catch (requestError) {
      setError(getApiErrorMessage(requestError))
    } finally {
      setIsSubmitting(false)
    }
  }

  const totalChange =
    entries.length >= 2
      ? entries[entries.length - 1].weight_kg - entries[0].weight_kg
      : null

  return (
    <div className="app-page">
      <main className="content-shell content-shell--wide">
        <header className="content-header">
          <Link className="brand" to="/dashboard">
            <span className="brand-mark">F</span>
            Fitness Assistant
          </Link>
          <Link className="text-link" to="/dashboard">
            返回首页
          </Link>
        </header>

        <section className="content-card">
          <p className="eyebrow">Your progress</p>
          <h1>体重记录与趋势</h1>
          <p className="panel-intro">
            建议在相似时间和条件下测量，以便观察长期趋势。
          </p>

          {error && (
            <p className="form-message form-message--error" role="alert">
              {error}
            </p>
          )}

          {isLoading ? (
            <p className="loading-copy">正在读取体重记录…</p>
          ) : (
            <div className="weight-layout">
              <form className="weight-form" onSubmit={handleSubmit}>
                <div className="field">
                  <label htmlFor="entry-weight">体重（kg）</label>
                  <input
                    id="entry-weight"
                    type="number"
                    min="20"
                    max="500"
                    step="0.1"
                    value={weightKg}
                    onChange={(event) => setWeightKg(event.target.value)}
                    placeholder="例如 79.5"
                    required
                  />
                </div>
                <div className="field">
                  <label htmlFor="entry-date">记录日期</label>
                  <input
                    id="entry-date"
                    type="date"
                    max={today}
                    value={recordedOn}
                    onChange={(event) => setRecordedOn(event.target.value)}
                    required
                  />
                </div>
                <div className="field">
                  <label htmlFor="entry-note">备注（可选）</label>
                  <input
                    id="entry-note"
                    type="text"
                    maxLength={500}
                    value={note}
                    onChange={(event) => setNote(event.target.value)}
                    placeholder="例如：晨起空腹"
                  />
                </div>
                <button
                  className="primary-button"
                  type="submit"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? '保存中…' : '保存体重记录'}
                </button>
              </form>

              <div className="trend-panel">
                <div className="trend-heading">
                  <div>
                    <p className="eyebrow">Trend</p>
                    <h2>最近变化</h2>
                  </div>
                  {totalChange !== null && (
                    <strong
                      className={
                        totalChange <= 0
                          ? 'trend-change trend-change--down'
                          : 'trend-change trend-change--up'
                      }
                    >
                      {totalChange > 0 ? '+' : ''}
                      {totalChange.toFixed(1)} kg
                    </strong>
                  )}
                </div>
                <WeightChart entries={entries} />

                {entries.length > 0 && (
                  <section className="daily-history">
                    <div className="daily-history__heading">
                      <h2>每日明细</h2>
                      <span>最近 {entries.length} 条</span>
                    </div>
                    <div className="daily-history__list">
                      {[...entries].reverse().map((entry, reverseIndex) => {
                        const originalIndex =
                          entries.length - 1 - reverseIndex
                        const previousEntry =
                          originalIndex > 0
                            ? entries[originalIndex - 1]
                            : null
                        const change = previousEntry
                          ? entry.weight_kg - previousEntry.weight_kg
                          : null

                        return (
                          <article
                            className="daily-history__row"
                            key={entry.id}
                          >
                            <div>
                              <strong>
                                {formatRecordDate(entry.recorded_on)}
                              </strong>
                              {entry.note && <span>{entry.note}</span>}
                            </div>
                            <div className="daily-history__measurement">
                              <strong>{entry.weight_kg} kg</strong>
                              {change !== null && (
                                <span
                                  className={
                                    change <= 0
                                      ? 'daily-change daily-change--down'
                                      : 'daily-change daily-change--up'
                                  }
                                >
                                  {change > 0 ? '+' : ''}
                                  {change.toFixed(1)} kg
                                </span>
                              )}
                            </div>
                          </article>
                        )
                      })}
                    </div>
                  </section>
                )}
              </div>
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default WeightsPage
