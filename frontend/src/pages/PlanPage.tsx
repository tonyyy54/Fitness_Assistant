import { AxiosError } from 'axios'
import { type FormEvent, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import {
  ACCESS_TOKEN_KEY,
  getApiErrorMessage,
} from '../services/api'
import {
  getWeightPlan,
  saveWeightPlan,
  type WeightPlan,
} from '../services/plan'

function PlanPage() {
  const navigate = useNavigate()
  const [targetWeightKg, setTargetWeightKg] = useState('')
  const [weeklyLossKg, setWeeklyLossKg] = useState('0.5')
  const [plan, setPlan] = useState<WeightPlan | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadPlan() {
      try {
        const loadedPlan = await getWeightPlan()

        if (loadedPlan) {
          setPlan(loadedPlan)
          setTargetWeightKg(String(loadedPlan.target_weight_kg))
          setWeeklyLossKg(String(loadedPlan.weekly_loss_kg))
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

    void loadPlan()
  }, [navigate])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      const savedPlan = await saveWeightPlan({
        target_weight_kg: Number(targetWeightKg),
        weekly_loss_kg: Number(weeklyLossKg),
      })
      setPlan(savedPlan)
    } catch (requestError) {
      setError(getApiErrorMessage(requestError))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="app-page">
      <main className="content-shell">
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
          <p className="eyebrow">Your direction</p>
          <h1>设置减重目标</h1>
          <p className="panel-intro">
            选择可持续的速度。计算结果是规划参考，不是医疗建议。
          </p>

          {error && (
            <p className="form-message form-message--error" role="alert">
              {error}
            </p>
          )}

          {isLoading ? (
            <p className="loading-copy">正在读取减重目标…</p>
          ) : (
            <>
              <form className="profile-grid" onSubmit={handleSubmit}>
                <div className="field">
                  <label htmlFor="target-weight">目标体重（kg）</label>
                  <input
                    id="target-weight"
                    type="number"
                    min="20"
                    max="500"
                    step="0.1"
                    value={targetWeightKg}
                    onChange={(event) =>
                      setTargetWeightKg(event.target.value)
                    }
                    placeholder="例如 70"
                    required
                  />
                </div>
                <div className="field">
                  <label htmlFor="weekly-loss">每周减重速度</label>
                  <select
                    id="weekly-loss"
                    value={weeklyLossKg}
                    onChange={(event) =>
                      setWeeklyLossKg(event.target.value)
                    }
                  >
                    <option value="0.25">0.25 kg（轻缓）</option>
                    <option value="0.5">0.5 kg（推荐）</option>
                    <option value="0.75">0.75 kg（较快）</option>
                    <option value="0.9">0.9 kg（上限）</option>
                  </select>
                </div>
                <button
                  className="primary-button"
                  type="submit"
                  disabled={isSubmitting}
                >
                  {isSubmitting ? '计算中…' : '保存并计算计划'}
                </button>
              </form>

              {plan && (
                <div className="plan-summary">
                  <p className="eyebrow">Your estimate</p>
                  <div className="metric-grid">
                    <article className="metric">
                      <span>建议每日摄入</span>
                      <strong>
                        {plan.recommended_daily_calories} kcal
                      </strong>
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
                  <Link className="secondary-button" to="/dashboard">
                    查看首页
                  </Link>
                </div>
              )}
            </>
          )}
        </section>
      </main>
    </div>
  )
}

export default PlanPage
