import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, useNavigate } from 'react-router-dom';
import axios from 'axios';
import './App.css';

const API_URL = process.env.REACT_APP_API_URL || 'https://vwe2.sliplane.app';

axios.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

function AuthPage({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [formData, setFormData] = useState({ email: '', password: '', name: '' });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const endpoint = isLogin ? '/user/login' : '/user/register';
      const response = await axios.post(`${API_URL}${endpoint}`, formData);
      
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
      onLogin(response.data.user);
    } catch (err) {
      setError(err.response?.data?.detail || 'خطا در ورود/ثبت‌نام');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-grid">
        <div className="auth-left">
          <div className="auth-hero">
            <div className="logo-section">
              <div className="logo-icon">
                <svg width="60" height="60" viewBox="0 0 60 60" fill="none">
                  <path d="M30 5L55 17.5V42.5L30 55L5 42.5V17.5L30 5Z" fill="url(#gradient1)" stroke="white" strokeWidth="2"/>
                  <circle cx="30" cy="30" r="8" fill="white"/>
                  <defs>
                    <linearGradient id="gradient1" x1="5" y1="5" x2="55" y2="55">
                      <stop offset="0%" stopColor="#667eea"/>
                      <stop offset="100%" stopColor="#764ba2"/>
                    </linearGradient>
                  </defs>
                </svg>
              </div>
              <h1>API Gateway</h1>
            </div>
            <h2>مدیریت حرفه‌ای API</h2>
            <p>پلتفرم یکپارچه برای مدیریت، نظارت و کنترل درخواست‌های API</p>
            <div className="features">
              <div className="feature-item">
                <span className="feature-icon">⚡</span>
                <span>سرعت بالا</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">🔒</span>
                <span>امنیت کامل</span>
              </div>
              <div className="feature-item">
                <span className="feature-icon">📊</span>
                <span>آمار لحظه‌ای</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="auth-right">
          <div className="auth-card">
            <div className="auth-tabs">
              <button 
                className={isLogin ? 'active' : ''} 
                onClick={() => { setIsLogin(true); setError(''); }}
              >
                ورود
              </button>
              <button 
                className={!isLogin ? 'active' : ''} 
                onClick={() => { setIsLogin(false); setError(''); }}
              >
                ثبت‌نام
              </button>
            </div>
            
            {error && (
              <div className="alert alert-error">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10 0C4.48 0 0 4.48 0 10s4.48 10 10 10 10-4.48 10-10S15.52 0 10 0zm1 15H9v-2h2v2zm0-4H9V5h2v6z"/>
                </svg>
                {error}
              </div>
            )}
            
            <form onSubmit={handleSubmit} className="auth-form">
              {!isLogin && (
                <div className="input-group">
                  <label>نام کاربری</label>
                  <div className="input-wrapper">
                    <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M10 10c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z"/>
                    </svg>
                    <input
                      type="text"
                      value={formData.name}
                      onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                      placeholder="نام خود را وارد کنید"
                    />
                  </div>
                </div>
              )}
              
              <div className="input-group">
                <label>ایمیل</label>
                <div className="input-wrapper">
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M18 4H2C0.9 4 0 4.9 0 6v8c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                  </svg>
                  <input
                    type="email"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    placeholder="example@email.com"
                    required
                  />
                </div>
              </div>
              
              <div className="input-group">
                <label>رمز عبور</label>
                <div className="input-wrapper">
                  <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M15 7h-1V5c0-2.76-2.24-5-5-5S4 2.24 4 5v2H3c-1.1 0-2 .9-2 2v8c0 1.1.9 2 2 2h12c1.1 0 2-.9 2-2V9c0-1.1-.9-2-2-2zM9 14c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2zm3.1-7H5.9V5c0-1.71 1.39-3.1 3.1-3.1 1.71 0 3.1 1.39 3.1 3.1v2z"/>
                  </svg>
                  <input
                    type="password"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    placeholder="رمز عبور خود را وارد کنید"
                    required
                  />
                </div>
              </div>
              
              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? (
                  <span className="spinner"></span>
                ) : (
                  isLogin ? 'ورود به حساب' : 'ایجاد حساب کاربری'
                )}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

function Dashboard({ user, onLogout }) {
  const [apiKeys, setApiKeys] = useState([]);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  const [newKey, setNewKey] = useState(null);
  const [loading, setLoading] = useState(true);
  const [quota, setQuota] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    loadApiKeys();
    loadQuota();
    const interval = setInterval(loadQuota, 5000);
    return () => clearInterval(interval);
  }, []);

  const loadQuota = async () => {
    try {
      const response = await axios.get(`${API_URL}/user/quota`);
      setQuota(response.data);
    } catch (error) {
      console.error('خطا در بارگذاری quota:', error);
    }
  };

  const loadApiKeys = async () => {
    try {
      const response = await axios.get(`${API_URL}/user/api-keys`);
      setApiKeys(response.data);
    } catch (error) {
      console.error('خطا در بارگذاری کلیدها:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateKey = async (e) => {
    e.preventDefault();
    try {
      const response = await axios.post(`${API_URL}/user/api-keys`, {
        name: newKeyName || undefined
      });
      setNewKey(response.data);
      setShowCreateForm(false);
      setNewKeyName('');
      loadApiKeys();
    } catch (error) {
      alert('خطا: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDeleteKey = async (keyId) => {
    if (!window.confirm('آیا مطمئن هستید که می‌خواهید این کلید را حذف کنید؟')) return;
    try {
      await axios.delete(`${API_URL}/user/api-keys/${keyId}`);
      loadApiKeys();
    } catch (error) {
      alert('خطا: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleToggleKey = async (keyId) => {
    try {
      await axios.patch(`${API_URL}/user/api-keys/${keyId}/toggle`);
      loadApiKeys();
    } catch (error) {
      alert('خطا: ' + (error.response?.data?.detail || error.message));
    }
  };

  const getUsagePercent = (used, total) => {
    return Math.min(100, ((used || 0) / total) * 100);
  };

  const getUsageColor = (used, total) => {
    const percent = getUsagePercent(used, total);
    if (percent >= 90) return '#ef4444';
    if (percent >= 70) return '#f59e0b';
    return '#10b981';
  };

  if (loading) {
    return (
      <div className="loading-screen">
        <div className="spinner-large"></div>
        <p>در حال بارگذاری...</p>
      </div>
    );
  }

  return (
    <div className="dashboard-layout">
      <aside className="dashboard-sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
              <path d="M20 3L35 11.5V28.5L20 37L5 28.5V11.5L20 3Z" fill="url(#grad)" stroke="white" strokeWidth="2"/>
              <circle cx="20" cy="20" r="5" fill="white"/>
              <defs>
                <linearGradient id="grad" x1="5" y1="3" x2="35" y2="37">
                  <stop offset="0%" stopColor="#667eea"/>
                  <stop offset="100%" stopColor="#764ba2"/>
                </linearGradient>
              </defs>
            </svg>
            <span>API Gateway</span>
          </div>
        </div>
        
        <nav className="sidebar-nav">
          <button 
            className={activeTab === 'overview' ? 'nav-item active' : 'nav-item'}
            onClick={() => setActiveTab('overview')}
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path d="M3 3h6v6H3V3zm8 0h6v6h-6V3zM3 11h6v6H3v-6zm8 0h6v6h-6v-6z"/>
            </svg>
            <span>داشبورد</span>
          </button>
          
          <button 
            className={activeTab === 'keys' ? 'nav-item active' : 'nav-item'}
            onClick={() => setActiveTab('keys')}
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path d="M12.65 10C11.83 7.67 9.61 6 7 6c-3.31 0-6 2.69-6 6s2.69 6 6 6c2.61 0 4.83-1.67 5.65-4H17v4h4v-4h2v-4H12.65zM7 14c-1.1 0-2-.9-2-2s.9-2 2-2 2 .9 2 2-.9 2-2 2z"/>
            </svg>
            <span>کلیدهای API</span>
          </button>
          
          <button 
            className={activeTab === 'docs' ? 'nav-item active' : 'nav-item'}
            onClick={() => setActiveTab('docs')}
          >
            <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
              <path d="M14 2H6c-1.1 0-2 .9-2 2v16c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM6 4h8v10H6V4z"/>
            </svg>
            <span>مستندات</span>
          </button>
        </nav>
        
        <div className="sidebar-footer">
          <div className="user-profile">
            <div className="user-avatar">
              {(user.name || user.email).charAt(0).toUpperCase()}
            </div>
            <div className="user-info">
              <div className="user-name">{user.name || 'کاربر'}</div>
              <div className="user-email">{user.email}</div>
            </div>
          </div>
          <button className="btn-logout" onClick={onLogout}>
            <svg width="18" height="18" viewBox="0 0 20 20" fill="currentColor">
              <path d="M13 3h-2v10h2V3zm4.83 2.17l-1.42 1.42C17.99 7.86 19 9.81 19 12c0 3.87-3.13 7-7 7s-7-3.13-7-7c0-2.19 1.01-4.14 2.58-5.42L6.17 5.17C4.23 6.82 3 9.26 3 12c0 4.97 4.03 9 9 9s9-4.03 9-9c0-2.74-1.23-5.18-3.17-6.83z"/>
            </svg>
            خروج
          </button>
        </div>
      </aside>
      
      <main className="dashboard-main">
        {activeTab === 'overview' && (
          <div className="dashboard-content">
            <div className="content-header">
              <div>
                <h1>خوش آمدید، {user.name || 'کاربر'} 👋</h1>
                <p>آمار و اطلاعات استفاده از API شما</p>
              </div>
            </div>
            
            <div className="stats-grid">
              <div className="stat-card">
                <div className="stat-header">
                  <div className="stat-icon" style={{background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'}}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                      <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                  </div>
                  <div className="stat-info">
                    <div className="stat-label">در دقیقه</div>
                    <div className="stat-value">
                      {quota ? (quota.usage_this_minute || 0) : 0} / {quota ? quota.per_minute : 10}
                    </div>
                  </div>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{
                      width: `${quota ? getUsagePercent(quota.usage_this_minute, quota.per_minute) : 0}%`,
                      background: quota ? getUsageColor(quota.usage_this_minute, quota.per_minute) : '#10b981'
                    }}
                  ></div>
                </div>
                <div className="stat-footer">
                  باقیمانده: {quota ? Math.max(0, quota.per_minute - (quota.usage_this_minute || 0)) : 10} درخواست
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-header">
                  <div className="stat-icon" style={{background: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'}}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                      <path d="M11.99 2C6.47 2 2 6.48 2 12s4.47 10 9.99 10C17.52 22 22 17.52 22 12S17.52 2 11.99 2zM12 20c-4.42 0-8-3.58-8-8s3.58-8 8-8 8 3.58 8 8-3.58 8-8 8zm.5-13H11v6l5.25 3.15.75-1.23-4.5-2.67z"/>
                    </svg>
                  </div>
                  <div className="stat-info">
                    <div className="stat-label">در ساعت</div>
                    <div className="stat-value">
                      {quota ? (quota.usage_this_hour || 0) : 0} / {quota ? quota.per_hour : 100}
                    </div>
                  </div>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{
                      width: `${quota ? getUsagePercent(quota.usage_this_hour, quota.per_hour) : 0}%`,
                      background: quota ? getUsageColor(quota.usage_this_hour, quota.per_hour) : '#10b981'
                    }}
                  ></div>
                </div>
                <div className="stat-footer">
                  باقیمانده: {quota ? Math.max(0, quota.per_hour - (quota.usage_this_hour || 0)) : 100} درخواست
                </div>
              </div>
              
              <div className="stat-card">
                <div className="stat-header">
                  <div className="stat-icon" style={{background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'}}>
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="white">
                      <path d="M9 11H7v2h2v-2zm4 0h-2v2h2v-2zm4 0h-2v2h2v-2zm2-7h-1V2h-2v2H8V2H6v2H5c-1.11 0-1.99.9-1.99 2L3 20c0 1.1.89 2 2 2h14c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 16H5V9h14v11z"/>
                    </svg>
                  </div>
                  <div className="stat-info">
                    <div className="stat-label">در روز</div>
                    <div className="stat-value">
                      {quota ? (quota.usage_today || 0) : 0} / {quota ? quota.per_day : 1000}
                    </div>
                  </div>
                </div>
                <div className="progress-bar">
                  <div 
                    className="progress-fill" 
                    style={{
                      width: `${quota ? getUsagePercent(quota.usage_today, quota.per_day) : 0}%`,
                      background: quota ? getUsageColor(quota.usage_today, quota.per_day) : '#10b981'
                    }}
                  ></div>
                </div>
                <div className="stat-footer">
                  باقیمانده: {quota ? Math.max(0, quota.per_day - (quota.usage_today || 0)) : 1000} درخواست
                </div>
              </div>
            </div>
            
            <div className="quick-actions">
              <h2>دسترسی سریع</h2>
              <div className="action-cards">
                <button className="action-card" onClick={() => setActiveTab('keys')}>
                  <div className="action-icon">🔑</div>
                  <div className="action-title">کلیدهای API</div>
                  <div className="action-desc">مدیریت کلیدهای دسترسی</div>
                </button>
                <button className="action-card" onClick={() => setActiveTab('docs')}>
                  <div className="action-icon">📚</div>
                  <div className="action-title">مستندات</div>
                  <div className="action-desc">راهنمای استفاده از API</div>
                </button>
                <button className="action-card">
                  <div className="action-icon">📊</div>
                  <div className="action-title">گزارشات</div>
                  <div className="action-desc">آمار و تحلیل داده‌ها</div>
                </button>
              </div>
            </div>
          </div>
        )}

        
        {activeTab === 'keys' && (
          <div className="dashboard-content">
            <div className="content-header">
              <div>
                <h1>کلیدهای API</h1>
                <p>مدیریت کلیدهای دسترسی به API</p>
              </div>
              <button className="btn-primary" onClick={() => setShowCreateForm(true)}>
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10 0C4.48 0 0 4.48 0 10s4.48 10 10 10 10-4.48 10-10S15.52 0 10 0zm5 11h-4v4H9v-4H5V9h4V5h2v4h4v2z"/>
                </svg>
                کلید جدید
              </button>
            </div>
            
            {showCreateForm && (
              <div className="card">
                <h3>ایجاد کلید API جدید</h3>
                <form onSubmit={handleCreateKey}>
                  <div className="input-group">
                    <label>نام کلید (اختیاری)</label>
                    <input
                      type="text"
                      value={newKeyName}
                      onChange={(e) => setNewKeyName(e.target.value)}
                      placeholder="مثلاً: کلید اصلی پروژه"
                    />
                  </div>
                  <div className="form-actions">
                    <button type="submit" className="btn-primary">ایجاد کلید</button>
                    <button type="button" className="btn-secondary" onClick={() => { setShowCreateForm(false); setNewKeyName(''); }}>
                      لغو
                    </button>
                  </div>
                </form>
              </div>
            )}
            
            {apiKeys.length === 0 ? (
              <div className="empty-state-card">
                <div className="empty-icon">🔑</div>
                <h3>هنوز کلیدی ایجاد نکرده‌اید</h3>
                <p>برای شروع استفاده از API، یک کلید جدید ایجاد کنید</p>
                <button className="btn-primary" onClick={() => setShowCreateForm(true)}>
                  ایجاد اولین کلید
                </button>
              </div>
            ) : (
              <div className="keys-grid">
                {apiKeys.map(key => (
                  <div key={key.id} className="key-card">
                    <div className="key-header">
                      <div className="key-title">
                        <div className="key-icon">🔑</div>
                        <div>
                          <h4>{key.name || 'بدون نام'}</h4>
                          <span className="key-id">ID: {key.id.substring(0, 8)}...</span>
                        </div>
                      </div>
                      <div className={`key-status ${key.is_active ? 'active' : 'inactive'}`}>
                        {key.is_active ? 'فعال' : 'غیرفعال'}
                      </div>
                    </div>
                    <div className="key-info">
                      <div className="info-item">
                        <span className="info-label">آخرین استفاده:</span>
                        <span className="info-value">{key.last_used ? new Date(key.last_used).toLocaleDateString('fa-IR') : 'هرگز'}</span>
                      </div>
                      <div className="info-item">
                        <span className="info-label">تاریخ ایجاد:</span>
                        <span className="info-value">{new Date(key.created_at).toLocaleDateString('fa-IR')}</span>
                      </div>
                    </div>
                    <div className="key-actions">
                      <button className="btn-icon" onClick={() => handleToggleKey(key.id)} title={key.is_active ? 'غیرفعال کردن' : 'فعال کردن'}>
                        {key.is_active ? (
                          <svg width="18" height="18" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M10 7c1.66 0 3 1.34 3 3s-1.34 3-3 3-3-1.34-3-3 1.34-3 3-3m0-2C6.69 5 4 7.69 4 10s2.69 5 5 5 5-2.69 5-5-2.69-5-5-5z"/>
                          </svg>
                        ) : (
                          <svg width="18" height="18" viewBox="0 0 20 20" fill="currentColor">
                            <path d="M10 5C5.69 5 2 7.69 2 10s3.69 5 7 5 7-2.69 7-5-3.69-5-7-5zm0 8c-1.66 0-3-1.34-3-3s1.34-3 3-3 3 1.34 3 3-1.34 3-3 3z"/>
                          </svg>
                        )}
                      </button>
                      <button className="btn-icon btn-danger" onClick={() => handleDeleteKey(key.id)} title="حذف">
                        <svg width="18" height="18" viewBox="0 0 20 20" fill="currentColor">
                          <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
                        </svg>
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
        
        {activeTab === 'docs' && (
          <div className="dashboard-content">
            <div className="content-header">
              <div>
                <h1>مستندات API</h1>
                <p>راهنمای استفاده از API Gateway</p>
              </div>
            </div>
            
            <div className="docs-content">
              <div className="card">
                <h3>🚀 شروع سریع</h3>
                <p>برای استفاده از API، کلید خود را در header درخواست‌ها قرار دهید:</p>
                <div className="code-block">
                  <code>Authorization: Bearer YOUR_API_KEY</code>
                </div>
              </div>
              
              <div className="card">
                <h3>📝 مثال استفاده</h3>
                <p>نمونه درخواست با curl:</p>
                <div className="code-block">
                  <pre>{`curl -X POST http://localhost:8000/v1/chat/completions \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "gpt-4",
    "messages": [
      {"role": "user", "content": "Hello!"}
    ]
  }'`}</pre>
                </div>
              </div>
              
              <div className="card">
                <h3>⚙️ پارامترهای درخواست</h3>
                <div className="params-table">
                  <div className="param-row">
                    <div className="param-name">model</div>
                    <div className="param-type">string</div>
                    <div className="param-desc">نام مدل مورد استفاده (مثلاً: gpt-4, gpt-3.5-turbo)</div>
                  </div>
                  <div className="param-row">
                    <div className="param-name">messages</div>
                    <div className="param-type">array</div>
                    <div className="param-desc">آرایه‌ای از پیام‌ها با role و content</div>
                  </div>
                  <div className="param-row">
                    <div className="param-name">temperature</div>
                    <div className="param-type">number</div>
                    <div className="param-desc">میزان خلاقیت پاسخ (0 تا 2، پیش‌فرض: 1)</div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>
      
      {newKey && (
        <div className="modal-overlay" onClick={() => setNewKey(null)}>
          <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>کلید جدید شما</h2>
              <button className="modal-close" onClick={() => setNewKey(null)}>
                <svg width="24" height="24" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M19 6.41L17.59 5 12 10.59 6.41 5 5 6.41 10.59 12 5 17.59 6.41 19 12 13.41 17.59 19 19 17.59 13.41 12z"/>
                </svg>
              </button>
            </div>
            <div className="modal-body">
              <div className="alert alert-warning">
                <svg width="20" height="20" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M1 21h22L12 2 1 21zm12-3h-2v-2h2v2zm0-4h-2v-4h2v4z"/>
                </svg>
                این کلید فقط یک بار نمایش داده می‌شود. لطفاً آن را کپی و در جای امن ذخیره کنید!
              </div>
              <div className="key-display">
                <code>{newKey.key}</code>
                <button className="btn-copy" onClick={() => {
                  navigator.clipboard.writeText(newKey.key);
                  alert('کپی شد!');
                }}>
                  <svg width="18" height="18" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
                  </svg>
                  کپی
                </button>
              </div>
            </div>
            <div className="modal-footer">
              <button className="btn-primary" onClick={() => setNewKey(null)}>متوجه شدم</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function App() {
  const [user, setUser] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const storedUser = localStorage.getItem('user');
    const token = localStorage.getItem('token');
    if (storedUser && token) {
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <div className="app">
      {user ? (
        <Dashboard user={user} onLogout={handleLogout} />
      ) : (
        <AuthPage onLogin={handleLogin} />
      )}
    </div>
  );
}

export default App;

