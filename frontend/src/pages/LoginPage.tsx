import { type FormEvent, useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

import { ACCESS_TOKEN_KEY, getApiErrorMessage } from '../services/api'
import { loginUser } from '../services/auth'
import { getProfile } from '../services/profile'

function LoginPage() {
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  const registrationMessage = (
    location.state as { registrationMessage?: string } | null
  )?.registrationMessage

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      const token = await loginUser(email, password)
      localStorage.setItem(ACCESS_TOKEN_KEY, token.access_token)
      const profile = await getProfile()
      navigate(profile ? '/dashboard' : '/profile')
    } catch (requestError) {
      setError(getApiErrorMessage(requestError))
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="app-page">
      <Link className="brand" to="/login">
        <span className="brand-mark">F</span>
        Fitness Assistant
      </Link>

      <main className="auth-layout">
        <section className="auth-story">
          <div>
            <p className="eyebrow">Your healthier rhythm</p>
            <h1>Small choices. Lasting change.</h1>
            <p>
              用清晰的数据记录身体变化，让每一天的努力都有方向、有反馈。
            </p>
          </div>
          <div className="story-stat">
            <strong>1%</strong>
            <span>每天进步一点，长期结果会很不一样。</span>
          </div>
        </section>

        <section className="auth-panel">
          <p className="eyebrow">Welcome back</p>
          <h2>登录你的账户</h2>
          <p className="panel-intro">继续查看身体档案与减重进度。</p>

          {registrationMessage && (
            <p className="form-message form-message--success">
              {registrationMessage}
            </p>
          )}
          {error && (
            <p className="form-message form-message--error" role="alert">
              {error}
            </p>
          )}

          <form className="form-stack" onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="email">邮箱</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
                required
              />
            </div>
            <div className="field">
              <label htmlFor="password">密码</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="至少 12 位"
                autoComplete="current-password"
                required
              />
            </div>
            <button
              className="primary-button"
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? '登录中…' : '登录'}
            </button>
          </form>

          <p className="switch-copy">
            还没有账户？ <Link to="/register">立即注册</Link>
          </p>
        </section>
      </main>
    </div>
  )
}

export default LoginPage
