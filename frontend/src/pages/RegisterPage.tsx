import { type FormEvent, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'

import { getApiErrorMessage } from '../services/api'
import { registerUser } from '../services/auth'

function RegisterPage() {
  const navigate = useNavigate()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    setError('')
    setIsSubmitting(true)

    try {
      await registerUser(email, password)
      navigate('/login', {
        replace: true,
        state: {
          registrationMessage: '注册成功，请使用新账户登录。',
        },
      })
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
            <p className="eyebrow">Start with clarity</p>
            <h1>Your plan begins with you.</h1>
            <p>
              建立账户后填写身体档案，我们会逐步计算适合你的减重目标与每日计划。
            </p>
          </div>
          <div className="story-stat">
            <strong>38</strong>
            <span>项后端自动化测试正在守护你的数据。</span>
          </div>
        </section>

        <section className="auth-panel">
          <p className="eyebrow">Create account</p>
          <h2>创建新账户</h2>
          <p className="panel-intro">只需要邮箱和安全密码即可开始。</p>

          {error && (
            <p className="form-message form-message--error" role="alert">
              {error}
            </p>
          )}

          <form className="form-stack" onSubmit={handleSubmit}>
            <div className="field">
              <label htmlFor="register-email">邮箱</label>
              <input
                id="register-email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
                required
              />
            </div>
            <div className="field">
              <label htmlFor="register-password">密码</label>
              <input
                id="register-password"
                type="password"
                value={password}
                onChange={(event) => setPassword(event.target.value)}
                placeholder="至少 12 位"
                minLength={12}
                maxLength={128}
                autoComplete="new-password"
                required
              />
            </div>
            <button
              className="primary-button"
              type="submit"
              disabled={isSubmitting}
            >
              {isSubmitting ? '注册中…' : '注册'}
            </button>
          </form>

          <p className="switch-copy">
            已经有账户？ <Link to="/login">返回登录</Link>
          </p>
        </section>
      </main>
    </div>
  )
}

export default RegisterPage
