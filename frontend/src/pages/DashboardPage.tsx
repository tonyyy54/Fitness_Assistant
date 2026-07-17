import { AxiosError } from 'axios'
import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import {
  ACCESS_TOKEN_KEY,
  getApiErrorMessage,
} from '../services/api'
import { getWeightPlan, type WeightPlan } from '../services/plan'
import {
  type BodyMetrics,
  getBodyMetrics,
  getProfile,
  type UserProfile,
} from '../services/profile'

function DashboardPage() {
  const navigate = useNavigate()
  const [profile, setProfile] = useState<UserProfile | null>(null)
  const [metrics, setMetrics] = useState<BodyMetrics | null>(null)
  const [plan, setPlan] = useState<WeightPlan | null>(null)
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
        setMetrics(await getBodyMetrics())
        setPlan(await getWeightPlan())
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
            <Link className="text-link" to="/plan">
              减重目标
            </Link>
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

          {!error && (!profile || !metrics) ? (
            <p className="loading-copy">正在读取数据…</p>
          ) : (
            profile &&
            metrics && (
              <div className="metric-grid">
                <article className="metric">
                  <span>当前体重</span>
                  <strong>{profile.current_weight_kg} kg</strong>
                </article>
                <article className="metric">
                  <span>BMI</span>
                  <strong>{metrics.bmi}</strong>
                </article>
                <article className="metric">
                  <span>基础代谢</span>
                  <strong>{metrics.bmr_kcal} kcal</strong>
                </article>
                <article className="metric">
                  <span>每日维持热量</span>
                  <strong>{metrics.maintenance_calories_kcal} kcal</strong>
                </article>
              </div>
            )
          )}

          {profile && metrics && (
            <div className="plan-summary">
              <p className="eyebrow">Weight goal</p>
              {plan ? (
                <>
                  <div className="metric-grid">
                    <article className="metric">
                      <span>目标体重</span>
                      <strong>{plan.target_weight_kg} kg</strong>
                    </article>
                    <article className="metric">
                      <span>建议每日摄入</span>
                      <strong>
                        {plan.recommended_daily_calories} kcal
                      </strong>
                    </article>
                    <article className="metric">
                      <span>每日热量缺口</span>
                      <strong>{plan.daily_calorie_deficit} kcal</strong>
                    </article>
                    <article className="metric">
                      <span>预计时间</span>
                      <strong>{plan.estimated_weeks} 周</strong>
                    </article>
                  </div>
                  {plan.warning && (
                    <p className="form-message form-message--warning">
                      {plan.warning}
                    </p>
                  )}
                  <Link className="secondary-button" to="/plan">
                    修改目标
                  </Link>
                </>
              ) : (
                <div className="empty-state">
                  <p>设置目标体重后，这里会生成每日热量建议。</p>
                  <Link className="secondary-button" to="/plan">
                    设置减重目标
                  </Link>
                </div>
              )}
            </div>
          )}
        </section>
      </main>
    </div>
  )
}

export default DashboardPage
