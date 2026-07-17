import { AxiosError } from 'axios'
import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import {
  ACCESS_TOKEN_KEY,
  getApiErrorMessage,
} from '../services/api'
import { getProfile, type UserProfile } from '../services/profile'

function DashboardPage() {
  const navigate = useNavigate()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadProfile() {
      try {
        const loadedProfile = await getProfile()

        if (!loadedProfile) {
          navigate('/profile', { replace: true })
          return
        }

        setProfile(loadedProfile)
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
      }
    }

    void loadProfile()
  }, [navigate])

  function handleLogout() {
    localStorage.removeItem(ACCESS_TOKEN_KEY)
    navigate('/login', { replace: true })
  }

  return (
    <div className="app-page">
      <main className="content-shell">
        <header className="content-header">
          <Link className="brand" to="/dashboard">
            <span className="brand-mark">F</span>
            Fitness Assistant
          </Link>
          <div className="header-actions">
            <Link className="text-link" to="/profile">
              编辑档案
            </Link>
            <button
              className="text-button"
              type="button"
              onClick={handleLogout}
            >
              退出
            </button>
          </div>
        </header>

        <section className="content-card">
          <p className="eyebrow">Today</p>
          <h1>欢迎回来</h1>
          <p className="panel-intro">
            你的身体档案已经连接到后端数据库。
          </p>

          {error && (
            <p className="form-message form-message--error" role="alert">
              {error}
            </p>
          )}

          {!error && !profile ? (
            <p className="loading-copy">正在读取数据…</p>
          ) : (
            profile && (
              <div className="metric-grid">
                <article className="metric">
                  <span>当前体重</span>
                  <strong>{profile.current_weight_kg} kg</strong>
                </article>
                <article className="metric">
                  <span>身高</span>
                  <strong>{profile.height_cm} cm</strong>
                </article>
              </div>
            )
          )}
        </section>
      </main>
    </div>
  )
}

export default DashboardPage
