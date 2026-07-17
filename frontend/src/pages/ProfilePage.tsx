import { AxiosError } from 'axios'
import { type FormEvent, useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import {
  ACCESS_TOKEN_KEY,
  getApiErrorMessage,
} from '../services/api'
import {
  type ActivityLevel,
  type BiologicalSex,
  getProfile,
  saveProfile,
} from '../services/profile'

function ProfilePage() {
  const navigate = useNavigate()
  const [biologicalSex, setBiologicalSex] = useState<
    BiologicalSex | ''
  >('')
  const [birthDate, setBirthDate] = useState('')
  const [heightCm, setHeightCm] = useState('')
  const [currentWeightKg, setCurrentWeightKg] = useState('')
  const [activityLevel, setActivityLevel] = useState<ActivityLevel | ''>('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    async function loadProfile() {
      try {
        const profile = await getProfile()

        if (profile) {
          setBiologicalSex(profile.biological_sex)
          setBirthDate(profile.birth_date)
          setHeightCm(String(profile.height_cm))
          setCurrentWeightKg(String(profile.current_weight_kg))
          setActivityLevel(profile.activity_level)
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

    void loadProfile()
  }, [navigate])

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()

    if (!biologicalSex || !activityLevel) {
      setError('请填写完整的身体档案。')
      return
    }

    setError('')
    setIsSubmitting(true)

    try {
      await saveProfile({
        biological_sex: biologicalSex,
        birth_date: birthDate,
        height_cm: Number(heightCm),
        current_weight_kg: Number(currentWeightKg),
        activity_level: activityLevel,
      })
      navigate('/dashboard')
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
          <p className="eyebrow">Your baseline</p>
          <h1>填写身体档案</h1>
          <p className="panel-intro">
            这些信息将用于计算基础代谢和每日热量建议。
          </p>

          {error && (
            <p className="form-message form-message--error" role="alert">
              {error}
            </p>
          )}

          {isLoading ? (
            <p className="loading-copy">正在读取身体档案…</p>
          ) : (
            <form className="profile-grid" onSubmit={handleSubmit}>
              <div className="field">
                <label htmlFor="sex">生理性别</label>
                <select
                  id="sex"
                  value={biologicalSex}
                  onChange={(event) =>
                    setBiologicalSex(event.target.value as BiologicalSex)
                  }
                  required
                >
                  <option value="" disabled>
                    请选择
                  </option>
                  <option value="male">男性</option>
                  <option value="female">女性</option>
                </select>
              </div>
              <div className="field">
                <label htmlFor="birth-date">出生日期</label>
                <input
                  id="birth-date"
                  type="date"
                  value={birthDate}
                  onChange={(event) => setBirthDate(event.target.value)}
                  required
                />
              </div>
              <div className="field">
                <label htmlFor="height">身高（cm）</label>
                <input
                  id="height"
                  type="number"
                  min="50"
                  max="300"
                  step="0.1"
                  value={heightCm}
                  onChange={(event) => setHeightCm(event.target.value)}
                  placeholder="175"
                  required
                />
              </div>
              <div className="field">
                <label htmlFor="weight">当前体重（kg）</label>
                <input
                  id="weight"
                  type="number"
                  min="20"
                  max="500"
                  step="0.1"
                  value={currentWeightKg}
                  onChange={(event) => setCurrentWeightKg(event.target.value)}
                  placeholder="75.0"
                  required
                />
              </div>
              <div className="field">
                <label htmlFor="activity">日常活动水平</label>
                <select
                  id="activity"
                  value={activityLevel}
                  onChange={(event) =>
                    setActivityLevel(event.target.value as ActivityLevel)
                  }
                  required
                >
                  <option value="" disabled>
                    请选择
                  </option>
                  <option value="sedentary">几乎不运动</option>
                  <option value="lightly_active">每周运动 1～3 次</option>
                  <option value="moderately_active">每周运动 3～5 次</option>
                  <option value="very_active">每周运动 6～7 次</option>
                  <option value="extra_active">
                    高强度训练或体力劳动
                  </option>
                </select>
              </div>
              <button
                className="primary-button"
                type="submit"
                disabled={isSubmitting}
              >
                {isSubmitting ? '保存中…' : '保存身体档案'}
              </button>
            </form>
          )}
        </section>
      </main>
    </div>
  )
}

export default ProfilePage
