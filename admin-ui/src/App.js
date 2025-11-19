import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { adminApi } from './api';
import './App.css';

// مدیریت مسیرهای پایه (Base Routes)
// این بخش برای تعریف مسیرهای API است که کاربران از آن‌ها استفاده می‌کنند
// مثلاً /v1 یا /v2 - هر مسیر می‌تواند مدل‌ها و providerهای خاصی را پشتیبانی کند
function BaseRoutes() {
  const [routes, setRoutes] = useState([]);
  const [pools, setPools] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editingRoute, setEditingRoute] = useState(null);
  const [formData, setFormData] = useState({
    base_url: '',
    name: '',
    proxy_targets: [{ provider_id: '', endpoint_template: '', allowed_models: [], weight: 1 }],
    rate_limits: { per_minute: 100, per_hour: 5000, per_day: 50000, per_ip: {} },
    api_key_pool_id: '',
    routing_strategy: 'ROUND_ROBIN',
    fallback_policy: { on_exhaust: 'TRY_OTHER_PROVIDER', retry_attempts: 2, retry_backoff_ms: 300 },
    enabled: true
  });

  useEffect(() => {
    loadRoutes();
    loadPools();
  }, []);

  const loadRoutes = async () => {
    try {
      const res = await adminApi.get('/admin/base_routes');
      setRoutes(res.data);
    } catch (error) {
      console.error('خطا در بارگذاری مسیرها:', error);
      window.alert('خطا در بارگذاری مسیرها: ' + (error.response?.data?.detail || error.message));
    }
  };

  const loadPools = async () => {
    try {
      const res = await axios.get(`${API_URL}/admin/key_pools`);
      setPools(res.data);
    } catch (error) {
      console.error('خطا در بارگذاری پول‌ها:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (editingRoute) {
        await axios.patch(`${API_URL}/admin/base_routes/${editingRoute.id}`, formData);
        window.alert('مسیر با موفقیت به‌روزرسانی شد');
      } else {
        await axios.post(`${API_URL}/admin/base_routes`, formData);
        window.alert('مسیر جدید با موفقیت ایجاد شد');
      }
      setShowForm(false);
      setEditingRoute(null);
      resetForm();
      loadRoutes();
    } catch (error) {
      window.alert('خطا: ' + (error.response?.data?.detail || error.message));
    }
  };

  const resetForm = () => {
    setFormData({
      base_url: '',
      name: '',
      proxy_targets: [{ provider_id: '', endpoint_template: '', allowed_models: [], weight: 1 }],
      rate_limits: { per_minute: 100, per_hour: 5000, per_day: 50000, per_ip: {} },
      api_key_pool_id: '',
      routing_strategy: 'ROUND_ROBIN',
      fallback_policy: { on_exhaust: 'TRY_OTHER_PROVIDER', retry_attempts: 2, retry_backoff_ms: 300 },
      enabled: true
    });
  };

  const handleEdit = (route) => {
    setEditingRoute(route);
    setFormData({
      base_url: route.base_url,
      name: route.name,
      proxy_targets: route.proxy_targets,
      rate_limits: route.rate_limits,
      api_key_pool_id: route.api_key_pool_id,
      routing_strategy: route.routing_strategy,
      fallback_policy: route.fallback_policy,
      enabled: route.enabled
    });
    setShowForm(true);
  };

  const handleDelete = async (id) => {
    if (!window.confirm('آیا مطمئن هستید که می‌خواهید این مسیر را حذف کنید؟')) return;
    try {
      await axios.delete(`${API_URL}/admin/base_routes/${id}`);
      window.alert('مسیر با موفقیت حذف شد');
      loadRoutes();
    } catch (error) {
      window.alert('خطا: ' + (error.response?.data?.detail || error.message));
    }
  };

  const addProxyTarget = () => {
    setFormData({
      ...formData,
      proxy_targets: [...formData.proxy_targets, { provider_id: '', endpoint_template: '', allowed_models: [], weight: 1 }]
    });
  };

  const removeProxyTarget = (index) => {
    const targets = formData.proxy_targets.filter((_, i) => i !== index);
    setFormData({ ...formData, proxy_targets: targets });
  };

  const updateProxyTarget = (index, field, value) => {
    const targets = [...formData.proxy_targets];
    targets[index][field] = value;
    setFormData({ ...formData, proxy_targets: targets });
  };

  const updateAllowedModels = (index, value) => {
    const targets = [...formData.proxy_targets];
    targets[index].allowed_models = value.split(',').map(m => m.trim()).filter(m => m);
    setFormData({ ...formData, proxy_targets: targets });
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>مسیرهای پایه (Base Routes)</h1>
          <p style={{ color: '#666', fontSize: '14px', marginTop: '5px' }}>
            مسیرهای API که کاربران از آن‌ها استفاده می‌کنند. هر مسیر می‌تواند مدل‌ها و providerهای خاصی را پشتیبانی کند.
          </p>
        </div>
        <button onClick={() => { setShowForm(true); setEditingRoute(null); resetForm(); }}>+ مسیر جدید</button>
      </div>

      {showForm && (
        <div className="modal">
          <div className="modal-content">
            <h2>{editingRoute ? 'ویرایش' : 'ایجاد'} مسیر پایه</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>
                  آدرس پایه (Base URL) * 
                  <span style={{ fontSize: '12px', color: '#666', display: 'block', marginTop: '5px' }}>
                    اولین فیلد - مثال: /v1 یا /v2 - این آدرس باید با / شروع شود
                  </span>
                </label>
                <input
                  type="text"
                  value={formData.base_url}
                  onChange={(e) => setFormData({ ...formData, base_url: e.target.value })}
                  placeholder="/v1"
                  required
                />
              </div>

              <div className="form-group">
                <label>
                  نام مسیر * 
                  <span style={{ fontSize: '12px', color: '#666', display: 'block', marginTop: '5px' }}>
                    نام خوانا برای شناسایی این مسیر (مثلاً: مسیر چت نسخه 1)
                  </span>
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="مسیر چت نسخه 1"
                  required
                />
              </div>

              <div className="form-group">
                <label>
                  پول کلید API * 
                  <span style={{ fontSize: '12px', color: '#666', display: 'block', marginTop: '5px' }}>
                    پولی که کلیدهای API از آن استفاده می‌شوند
                  </span>
                </label>
                <select
                  value={formData.api_key_pool_id}
                  onChange={(e) => setFormData({ ...formData, api_key_pool_id: e.target.value })}
                  required
                >
                  <option value="">انتخاب پول</option>
                  {pools.map(pool => (
                    <option key={pool.id} value={pool.id}>{pool.name}</option>
                  ))}
                </select>
              </div>

              <div className="form-group">
                <label>
                  استراتژی مسیریابی * 
                  <span style={{ fontSize: '12px', color: '#666', display: 'block', marginTop: '5px' }}>
                    روش انتخاب کلید API: Round Robin (چرخشی)، Least Used (کم‌استفاده‌ترین)، Weighted (وزن‌دار)
                  </span>
                </label>
                <select
                  value={formData.routing_strategy}
                  onChange={(e) => setFormData({ ...formData, routing_strategy: e.target.value })}
                  required
                >
                  <option value="ROUND_ROBIN">Round Robin (چرخشی)</option>
                  <option value="LEAST_USED">Least Used (کم‌استفاده‌ترین)</option>
                  <option value="WEIGHTED">Weighted (وزن‌دار)</option>
                </select>
              </div>

              <div className="form-group">
                <label>
                  مقصدهای پروکسی (Proxy Targets) * 
                  <span style={{ fontSize: '12px', color: '#666', display: 'block', marginTop: '5px' }}>
                    لیست providerها و مدل‌هایی که این مسیر پشتیبانی می‌کند. می‌توانید چند provider اضافه کنید.
                  </span>
                </label>
                {formData.proxy_targets.map((target, idx) => (
                  <div key={idx} className="proxy-target">
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                      <strong>Provider {idx + 1}</strong>
                      {formData.proxy_targets.length > 1 && (
                        <button type="button" onClick={() => removeProxyTarget(idx)} style={{ background: '#e74c3c' }}>حذف</button>
                      )}
                    </div>
                    <input
                      type="text"
                      placeholder="شناسه Provider (مثلاً: openai, openrouter)"
                      value={target.provider_id}
                      onChange={(e) => updateProxyTarget(idx, 'provider_id', e.target.value)}
                      required
                    />
                    <input
                      type="text"
                      placeholder="الگوی آدرس (مثلاً: https://api.openai.com/v1/chat/completions)"
                      value={target.endpoint_template}
                      onChange={(e) => updateProxyTarget(idx, 'endpoint_template', e.target.value)}
                      required
                    />
                    <input
                      type="text"
                      placeholder="مدل‌های مجاز (با کاما جدا کنید، مثلاً: gpt-4, gpt-3.5-turbo)"
                      value={target.allowed_models?.join(', ') || ''}
                      onChange={(e) => updateAllowedModels(idx, e.target.value)}
                      required
                    />
                    <input
                      type="number"
                      placeholder="وزن (برای استراتژی Weighted)"
                      value={target.weight || 1}
                      onChange={(e) => updateProxyTarget(idx, 'weight', parseInt(e.target.value) || 1)}
                    />
                  </div>
                ))}
                <button type="button" onClick={addProxyTarget}>+ افزودن Provider</button>
              </div>

              <div className="form-group">
                <label>
                  محدودیت نرخ (Rate Limits)
                  <span style={{ fontSize: '12px', color: '#666', display: 'block', marginTop: '5px' }}>
                    حداکثر تعداد درخواست‌های مجاز در بازه‌های زمانی مختلف
                  </span>
                </label>
                <input
                  type="number"
                  placeholder="در هر دقیقه"
                  value={formData.rate_limits.per_minute}
                  onChange={(e) => setFormData({
                    ...formData,
                    rate_limits: { ...formData.rate_limits, per_minute: parseInt(e.target.value) }
                  })}
                />
                <input
                  type="number"
                  placeholder="در هر روز"
                  value={formData.rate_limits.per_day}
                  onChange={(e) => setFormData({
                    ...formData,
                    rate_limits: { ...formData.rate_limits, per_day: parseInt(e.target.value) }
                  })}
                />
              </div>

              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={formData.enabled}
                    onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                  />
                  فعال
                  <span style={{ fontSize: '12px', color: '#666', display: 'block', marginTop: '5px' }}>
                    اگر غیرفعال باشد، این مسیر در دسترس کاربران نخواهد بود
                  </span>
                </label>
              </div>

              <div className="form-actions">
                <button type="submit">ذخیره</button>
                <button type="button" onClick={() => { setShowForm(false); setEditingRoute(null); }}>لغو</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div style={{ overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ minWidth: '100px' }}>نام</th>
              <th style={{ minWidth: '120px' }}>آدرس پایه</th>
              <th style={{ minWidth: '100px' }}>استراتژی</th>
              <th style={{ minWidth: '80px' }}>وضعیت</th>
              <th style={{ minWidth: '180px' }}>عملیات</th>
            </tr>
          </thead>
          <tbody>
            {routes.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ textAlign: 'center', padding: '40px' }}>
                  هیچ مسیری تعریف نشده است. برای شروع یک مسیر جدید ایجاد کنید.
                </td>
              </tr>
            ) : (
              routes.map(route => (
                <tr key={route.id}>
                  <td><strong>{route.name}</strong></td>
                  <td><code style={{ background: '#f3f4f6', padding: '4px 8px', borderRadius: '4px', fontSize: '0.9rem' }}>{route.base_url}</code></td>
                  <td>
                    <span style={{ 
                      background: '#e0e7ff', 
                      color: '#4338ca', 
                      padding: '4px 12px', 
                      borderRadius: '12px', 
                      fontSize: '0.85rem',
                      fontWeight: '600'
                    }}>
                      {route.routing_strategy === 'ROUND_ROBIN' ? 'چرخشی' : route.routing_strategy === 'LEAST_USED' ? 'کم‌استفاده' : 'وزن‌دار'}
                    </span>
                  </td>
                  <td>
                    {route.enabled ? (
                      <span style={{ 
                        color: '#16a34a', 
                        fontWeight: '700',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}>
                        <span style={{ fontSize: '1.2rem' }}>✓</span> فعال
                      </span>
                    ) : (
                      <span style={{ 
                        color: '#dc2626', 
                        fontWeight: '700',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}>
                        <span style={{ fontSize: '1.2rem' }}>✗</span> غیرفعال
                      </span>
                    )}
                  </td>
                  <td>
                    <button onClick={() => handleEdit(route)}>ویرایش</button>
                    <button onClick={() => handleDelete(route.id)} style={{ background: '#e74c3c' }}>حذف</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// مدیریت پول‌های کلید (Key Pools)
// پول‌ها گروه‌هایی از کلیدهای API هستند که می‌توانید آن‌ها را به مسیرها اختصاص دهید
function KeyPools() {
  const [pools, setPools] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({ name: '' });

  useEffect(() => {
    loadPools();
  }, []);

  const loadPools = async () => {
    try {
      const res = await axios.get(`${API_URL}/admin/key_pools`);
      setPools(res.data);
    } catch (error) {
      console.error('خطا در بارگذاری پول‌ها:', error);
      window.alert('خطا در بارگذاری پول‌ها: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/admin/key_pools`, formData);
      window.alert('پول جدید با موفقیت ایجاد شد');
      setShowForm(false);
      setFormData({ name: '' });
      loadPools();
    } catch (error) {
      window.alert('خطا: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDelete = async (poolId) => {
    if (!window.confirm('آیا مطمئن هستید که می‌خواهید این پول را حذف کنید؟ تمام کلیدهای متصل به این پول نیز حذف خواهند شد.')) {
      return;
    }
    try {
      await axios.delete(`${API_URL}/admin/key_pools/${poolId}`);
      window.alert('پول با موفقیت حذف شد');
      loadPools();
    } catch (error) {
      window.alert('خطا در حذف پول: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>پول‌های کلید (Key Pools)</h1>
          <p style={{ color: '#666', fontSize: '14px', marginTop: '5px' }}>
            پول‌ها گروه‌هایی از کلیدهای API هستند. می‌توانید کلیدهای مختلف را در یک پول قرار دهید و آن را به مسیرها اختصاص دهید.
          </p>
        </div>
        <button onClick={() => setShowForm(true)}>+ پول جدید</button>
      </div>

      {showForm && (
        <div className="modal">
          <div className="modal-content">
            <h2>ایجاد پول کلید</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>
                  نام پول * 
                  <span style={{ fontSize: '12px', color: '#666', display: 'block', marginTop: '5px' }}>
                    نامی برای شناسایی این پول (مثلاً: پول اصلی OpenAI)
                  </span>
                </label>
                <input
                  type="text"
                  value={formData.name}
                  onChange={(e) => setFormData({ name: e.target.value })}
                  placeholder="پول اصلی"
                  required
                />
              </div>
              <div className="form-actions">
                <button type="submit">ایجاد</button>
                <button type="button" onClick={() => setShowForm(false)}>لغو</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div style={{ overflowX: 'auto' }}>
        <table className="data-table">
          <thead>
            <tr>
              <th style={{ minWidth: '200px' }}>نام</th>
              <th style={{ minWidth: '150px' }}>شناسه</th>
              <th style={{ minWidth: '120px' }}>تاریخ ایجاد</th>
              <th style={{ minWidth: '120px' }}>عملیات</th>
            </tr>
          </thead>
          <tbody>
            {pools.length === 0 ? (
              <tr>
                <td colSpan="4" style={{ textAlign: 'center', padding: '40px' }}>
                  هیچ پولی ایجاد نشده است. برای شروع یک پول جدید ایجاد کنید.
                </td>
              </tr>
            ) : (
              pools.map(pool => (
                <tr key={pool.id}>
                  <td><strong style={{ fontSize: '1rem' }}>{pool.name}</strong></td>
                  <td>
                    <code style={{ 
                      background: '#f3f4f6', 
                      padding: '4px 8px', 
                      borderRadius: '4px', 
                      fontSize: '0.85rem',
                      fontFamily: 'monospace'
                    }}>
                      {pool.id.substring(0, 8)}...
                    </code>
                  </td>
                  <td>{new Date(pool.created_at).toLocaleDateString('fa-IR')}</td>
                  <td>
                    <button onClick={() => handleDelete(pool.id)} style={{ background: '#e74c3c' }}>حذف</button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}

// مدیریت کلیدهای API
// این بخش برای افزودن و مدیریت کلیدهای API از providerهای مختلف است
function APIKeys() {
  const [pools, setPools] = useState([]);
  const [selectedPool, setSelectedPool] = useState('');
  const [keys, setKeys] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [formData, setFormData] = useState({
    pool_id: '',
    provider_id: '',
    secret: '',
    priority: 0,
    weight: 1,
    status: 'healthy'
  });

  useEffect(() => {
    loadPools();
  }, []);

  useEffect(() => {
    if (selectedPool) {
      loadKeys(selectedPool);
    } else {
      setKeys([]);
    }
  }, [selectedPool]);

  const loadPools = async () => {
    try {
      const res = await axios.get(`${API_URL}/admin/key_pools`);
      setPools(res.data);
    } catch (error) {
      console.error('خطا در بارگذاری پول‌ها:', error);
    }
  };

  const loadKeys = async (poolId) => {
    try {
      const res = await axios.get(`${API_URL}/admin/key_pools/${poolId}/keys`);
      setKeys(res.data);
    } catch (error) {
      console.error('خطا در بارگذاری کلیدها:', error);
      window.alert('خطا در بارگذاری کلیدها: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/admin/key_pools/${formData.pool_id}/keys`, formData);
      window.alert('کلید با موفقیت افزوده شد');
      setShowForm(false);
      setFormData({ pool_id: '', provider_id: '', secret: '', priority: 0, weight: 1, status: 'healthy' });
      if (formData.pool_id) loadKeys(formData.pool_id);
    } catch (error) {
      window.alert('خطا: ' + (error.response?.data?.detail || error.message));
    }
  };

  const updateKeyStatus = async (keyId, status) => {
    try {
      await axios.patch(`${API_URL}/admin/keys/${keyId}/status`, { status });
      if (selectedPool) loadKeys(selectedPool);
    } catch (error) {
      window.alert('خطا: ' + (error.response?.data?.detail || error.message));
    }
  };

  const deleteKey = async (keyId) => {
    if (!window.confirm('آیا مطمئن هستید که می‌خواهید این کلید را حذف کنید؟ این عمل غیرقابل بازگشت است.')) {
      return;
    }
    try {
      await axios.delete(`${API_URL}/admin/keys/${keyId}`);
      window.alert('کلید با موفقیت حذف شد');
      if (selectedPool) loadKeys(selectedPool);
    } catch (error) {
      window.alert('خطا: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>کلیدهای API</h1>
          <p style={{ color: '#666', fontSize: '14px', marginTop: '5px' }}>
            افزودن و مدیریت کلیدهای API از providerهای مختلف. کلیدها به صورت رمزنگاری شده ذخیره می‌شوند.
          </p>
        </div>
        <button onClick={() => setShowForm(true)}>+ کلید جدید</button>
      </div>

      <div className="form-group" style={{ marginBottom: '20px', background: '#f8f9fa', padding: '15px', borderRadius: '8px' }}>
        <label>
          انتخاب پول
          <span style={{ fontSize: '12px', color: '#666', display: 'block', marginTop: '5px' }}>
            ابتدا یک پول انتخاب کنید تا کلیدهای آن را مشاهده کنید
          </span>
        </label>
        <select value={selectedPool} onChange={(e) => setSelectedPool(e.target.value)} style={{ width: '100%', padding: '10px' }}>
          <option value="">-- یک پول انتخاب کنید --</option>
          {pools.map(pool => (
            <option key={pool.id} value={pool.id}>{pool.name}</option>
          ))}
        </select>
      </div>

      {showForm && (
        <div className="modal">
          <div className="modal-content">
            <h2>افزودن کلید API</h2>
            <form onSubmit={handleSubmit}>
              <div className="form-group">
                <label>
                  پول * 
                  <span style={{ fontSize: '12px', color: '#666', display: 'block', marginTop: '5px' }}>
                    پولی که این کلید به آن تعلق دارد
                  </span>
                </label>
                <select
                  value={formData.pool_id}
                  onChange={(e) => setFormData({ ...formData, pool_id: e.target.value })}
                  required
                >
                  <option value="">انتخاب پول</option>
                  {pools.map(pool => (
                    <option key={pool.id} value={pool.id}>{pool.name}</option>
                  ))}
                </select>
              </div>
              <div className="form-group">
                <label>
                  شناسه Provider * 
                  <span style={{ fontSize: '12px', color: '#666', display: 'block', marginTop: '5px' }}>
                    نام provider (مثلاً: openai, openrouter, anthropic)
                  </span>
                </label>
                <input
                  type="text"
                  value={formData.provider_id}
                  onChange={(e) => setFormData({ ...formData, provider_id: e.target.value })}
                  placeholder="openai"
                  required
                />
              </div>
              <div className="form-group">
                <label>
                  کلید مخفی (Secret) * 
                  <span style={{ fontSize: '12px', color: '#666', display: 'block', marginTop: '5px' }}>
                    کلید API از provider (به صورت رمزنگاری شده ذخیره می‌شود)
                  </span>
                </label>
                <input
                  type="password"
                  value={formData.secret}
                  onChange={(e) => setFormData({ ...formData, secret: e.target.value })}
                  placeholder="sk-..."
                  required
                />
              </div>
              <div className="form-group">
                <label>
                  اولویت
                  <span style={{ fontSize: '12px', color: '#666', display: 'block', marginTop: '5px' }}>
                    عدد بالاتر = اولویت بیشتر (برای انتخاب اول)
                  </span>
                </label>
                <input
                  type="number"
                  value={formData.priority}
                  onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) || 0 })}
                />
              </div>
              <div className="form-group">
                <label>
                  وزن
                  <span style={{ fontSize: '12px', color: '#666', display: 'block', marginTop: '5px' }}>
                    برای استراتژی Weighted - عدد بالاتر = احتمال انتخاب بیشتر
                  </span>
                </label>
                <input
                  type="number"
                  value={formData.weight}
                  onChange={(e) => setFormData({ ...formData, weight: parseInt(e.target.value) || 1 })}
                />
              </div>
              <div className="form-actions">
                <button type="submit">افزودن</button>
                <button type="button" onClick={() => setShowForm(false)}>لغو</button>
              </div>
            </form>
          </div>
        </div>
      )}

      {!selectedPool ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          لطفاً ابتدا یک پول انتخاب کنید
        </div>
      ) : keys.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          این پول هیچ کلیدی ندارد. یک کلید جدید اضافه کنید.
        </div>
      ) : (
        <div style={{ overflowX: 'auto' }}>
          <table className="data-table">
            <thead>
              <tr>
                <th style={{ minWidth: '150px' }}>Provider</th>
                <th style={{ minWidth: '80px' }}>اولویت</th>
                <th style={{ minWidth: '80px' }}>وزن</th>
                <th style={{ minWidth: '100px' }}>وضعیت</th>
                <th style={{ minWidth: '130px' }}>آخرین استفاده</th>
                <th style={{ minWidth: '200px' }}>عملیات</th>
              </tr>
            </thead>
            <tbody>
              {keys.map(key => (
                <tr key={key.id}>
                  <td>
                    <strong style={{ 
                      fontSize: '1rem',
                      color: '#111827'
                    }}>
                      {key.provider_id}
                    </strong>
                  </td>
                  <td>
                    <span style={{ 
                      background: '#dbeafe',
                      color: '#1e40af',
                      padding: '4px 10px',
                      borderRadius: '8px',
                      fontWeight: '700',
                      fontSize: '0.9rem'
                    }}>
                      {key.priority}
                    </span>
                  </td>
                  <td>
                    <span style={{ 
                      background: '#fef3c7',
                      color: '#92400e',
                      padding: '4px 10px',
                      borderRadius: '8px',
                      fontWeight: '700',
                      fontSize: '0.9rem'
                    }}>
                      {key.weight}
                    </span>
                  </td>
                  <td>
                    {key.status === 'healthy' ? (
                      <span style={{ 
                        color: '#16a34a', 
                        fontWeight: '700',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}>
                        ✓ سالم
                      </span>
                    ) : key.status === 'unhealthy' ? (
                      <span style={{ 
                        color: '#ea580c', 
                        fontWeight: '700',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}>
                        ⚠ ناسالم
                      </span>
                    ) : (
                      <span style={{ 
                        color: '#dc2626', 
                        fontWeight: '700',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}>
                        ✗ غیرفعال
                      </span>
                    )}
                  </td>
                  <td>{key.last_used ? new Date(key.last_used).toLocaleDateString('fa-IR') : 'هرگز'}</td>
                  <td style={{ whiteSpace: 'nowrap' }}>
                    <select 
                      value={key.status} 
                      onChange={(e) => updateKeyStatus(key.id, e.target.value)} 
                      style={{ 
                        padding: '6px 10px',
                        marginRight: '10px',
                        borderRadius: '6px',
                        border: '2px solid #e5e7eb',
                        fontSize: '0.85rem',
                        fontWeight: '600',
                        background: 'white',
                        cursor: 'pointer'
                      }}
                    >
                      <option value="healthy">سالم</option>
                      <option value="unhealthy">ناسالم</option>
                      <option value="disabled">غیرفعال</option>
                    </select>
                    <button 
                      onClick={() => deleteKey(key.id)}
                      style={{ 
                        background: '#ef4444', 
                        color: 'white', 
                        border: 'none', 
                        padding: '8px 16px', 
                        borderRadius: '8px', 
                        cursor: 'pointer',
                        fontSize: '0.85rem',
                        fontWeight: '700',
                        transition: 'all 0.2s'
                      }}
                      title="حذف کلید"
                    >
                      حذف
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

// داشبورد متریک‌ها (Metrics Dashboard)
// نمایش آمار و اطلاعات درخواست‌ها، نرخ موفقیت، خطاها و زمان پاسخ
function Metrics() {
  const [metrics, setMetrics] = useState(null);
  const [routes, setRoutes] = useState([]);
  const [selectedRoute, setSelectedRoute] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRoutes();
    loadMetrics();
  }, []);

  useEffect(() => {
    loadMetrics();
  }, [selectedRoute]);

  const loadRoutes = async () => {
    try {
      const res = await axios.get(`${API_URL}/admin/base_routes`);
      setRoutes(res.data);
    } catch (error) {
      console.error('خطا در بارگذاری مسیرها:', error);
    }
  };

  const loadMetrics = async () => {
    setLoading(true);
    try {
      const params = selectedRoute ? { route_id: selectedRoute } : {};
      const res = await axios.get(`${API_URL}/admin/metrics`, { params });
      setMetrics(res.data);
    } catch (error) {
      console.error('خطا در بارگذاری متریک‌ها:', error);
      window.alert('خطا در بارگذاری متریک‌ها: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div style={{ textAlign: 'center', padding: '40px' }}>در حال بارگذاری...</div>;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>آمار و متریک‌ها</h1>
          <p style={{ color: '#666', fontSize: '14px', marginTop: '5px' }}>
            نمایش آمار درخواست‌ها، نرخ موفقیت، خطاها و زمان پاسخ
          </p>
        </div>
        <select value={selectedRoute} onChange={(e) => setSelectedRoute(e.target.value)} style={{ padding: '10px' }}>
          <option value="">همه مسیرها</option>
          {routes.map(route => (
            <option key={route.id} value={route.id}>{route.name}</option>
          ))}
        </select>
      </div>

      <div className="metrics-grid">
        <div className="metric-card">
          <h3>کل درخواست‌ها</h3>
          <p className="metric-value">{metrics?.total_requests || 0}</p>
          <p style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>تعداد کل درخواست‌های دریافتی</p>
        </div>
        <div className="metric-card">
          <h3>نرخ موفقیت</h3>
          <p className="metric-value">{((metrics?.success_rate || 0) * 100).toFixed(2)}%</p>
          <p style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>درصد درخواست‌های موفق (کد 200-299)</p>
        </div>
        <div className="metric-card">
          <h3>تعداد خطا</h3>
          <p className="metric-value" style={{ color: metrics?.error_count > 0 ? '#e74c3c' : '#2c3e50' }}>
            {metrics?.error_count || 0}
          </p>
          <p style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>درخواست‌های ناموفق (کد 400+)</p>
        </div>
        <div className="metric-card">
          <h3>میانگین زمان پاسخ</h3>
          <p className="metric-value">{(metrics?.avg_latency_ms || 0).toFixed(2)}ms</p>
          <p style={{ fontSize: '12px', color: '#666', marginTop: '5px' }}>میانگین زمان پاسخ به میلی‌ثانیه</p>
        </div>
      </div>
    </div>
  );
}

// مدیریت کاربران (User Management)
// این بخش برای مدیریت کاربران و تنظیم quota (محدودیت) برای هر کاربر است
// می‌توانید برای هر کاربر محدودیت درخواست در دقیقه، ساعت و روز تعیین کنید
function UserManagement() {
  const [users, setUsers] = useState([]);
  const [selectedUser, setSelectedUser] = useState(null);
  const [quota, setQuota] = useState(null);
  const [showQuotaForm, setShowQuotaForm] = useState(false);
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [quotaForm, setQuotaForm] = useState({
    per_minute: 10,
    per_hour: 100,
    per_day: 1000
  });
  const [createForm, setCreateForm] = useState({
    email: '',
    password: '',
    name: '',
    is_active: true
  });

  useEffect(() => {
    loadUsers();
  }, []);

  const loadUsers = async () => {
    try {
      const res = await axios.get(`${API_URL}/admin/users`);
      setUsers(res.data);
    } catch (error) {
      window.alert('خطا در بارگذاری کاربران: ' + (error.response?.data?.detail || error.message));
    }
  };

  const loadUserQuota = async (userId) => {
    try {
      const res = await axios.get(`${API_URL}/admin/users/${userId}/quota`);
      setQuota(res.data);
      setQuotaForm({
        per_minute: res.data.per_minute,
        per_hour: res.data.per_hour,
        per_day: res.data.per_day
      });
    } catch (error) {
      if (error.response?.status === 404) {
        setQuota(null);
        setQuotaForm({ per_minute: 10, per_hour: 100, per_day: 1000 });
      } else {
        window.alert('خطا در بارگذاری quota: ' + (error.response?.data?.detail || error.message));
      }
    }
  };

  const handleUserSelect = (user) => {
    setSelectedUser(user);
    loadUserQuota(user.id);
    setShowQuotaForm(false);
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`${API_URL}/admin/users`, createForm);
      window.alert('کاربر با موفقیت ایجاد شد');
      setShowCreateForm(false);
      setCreateForm({ email: '', password: '', name: '', is_active: true });
      loadUsers();
    } catch (error) {
      window.alert('خطا در ایجاد کاربر: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleDeleteUser = async (userId) => {
    if (!window.confirm('آیا مطمئن هستید که می‌خواهید این کاربر را حذف کنید؟ تمام داده‌های مرتبط نیز حذف خواهند شد.')) {
      return;
    }
    try {
      await axios.delete(`${API_URL}/admin/users/${userId}`);
      window.alert('کاربر با موفقیت حذف شد');
      if (selectedUser?.id === userId) {
        setSelectedUser(null);
        setQuota(null);
      }
      loadUsers();
    } catch (error) {
      window.alert('خطا در حذف کاربر: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleToggleUserStatus = async (userId, currentStatus) => {
    try {
      await axios.patch(`${API_URL}/admin/users/${userId}/status`, {
        is_active: !currentStatus
      });
      loadUsers();
      if (selectedUser?.id === userId) {
        setSelectedUser({ ...selectedUser, is_active: !currentStatus });
      }
    } catch (error) {
      window.alert('خطا در تغییر وضعیت: ' + (error.response?.data?.detail || error.message));
    }
  };

  const handleSaveQuota = async (e) => {
    e.preventDefault();
    if (!selectedUser) return;

    try {
      if (quota) {
        await axios.patch(`${API_URL}/admin/users/${selectedUser.id}/quota`, quotaForm);
        window.alert('Quota با موفقیت به‌روزرسانی شد');
      } else {
        await axios.post(`${API_URL}/admin/users/${selectedUser.id}/quota`, {
          user_id: selectedUser.id,
          ...quotaForm
        });
        window.alert('Quota با موفقیت ایجاد شد');
      }
      loadUserQuota(selectedUser.id);
      setShowQuotaForm(false);
    } catch (error) {
      window.alert('خطا: ' + (error.response?.data?.detail || error.message));
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>مدیریت کاربران</h1>
          <p style={{ color: '#666', fontSize: '14px', marginTop: '5px' }}>
            در این بخش می‌توانید کاربران را مدیریت کنید و برای هر کاربر محدودیت درخواست (quota) تعیین کنید.
          </p>
        </div>
        <button onClick={() => setShowCreateForm(true)}>+ کاربر جدید</button>
      </div>

      {showCreateForm && (
        <div className="modal">
          <div className="modal-content">
            <h2>ایجاد کاربر جدید</h2>
            <form onSubmit={handleCreateUser}>
              <div className="form-group">
                <label>
                  ایمیل *
                  <span>آدرس ایمیل برای ورود کاربر</span>
                </label>
                <input
                  type="email"
                  value={createForm.email}
                  onChange={(e) => setCreateForm({ ...createForm, email: e.target.value })}
                  placeholder="user@example.com"
                  required
                />
              </div>
              <div className="form-group">
                <label>
                  رمز عبور *
                  <span>رمز عبور برای ورود کاربر</span>
                </label>
                <input
                  type="password"
                  value={createForm.password}
                  onChange={(e) => setCreateForm({ ...createForm, password: e.target.value })}
                  placeholder="حداقل 6 کاراکتر"
                  required
                  minLength="6"
                />
              </div>
              <div className="form-group">
                <label>
                  نام (اختیاری)
                  <span>نام نمایشی کاربر</span>
                </label>
                <input
                  type="text"
                  value={createForm.name}
                  onChange={(e) => setCreateForm({ ...createForm, name: e.target.value })}
                  placeholder="نام کاربر"
                />
              </div>
              <div className="form-group">
                <label>
                  <input
                    type="checkbox"
                    checked={createForm.is_active}
                    onChange={(e) => setCreateForm({ ...createForm, is_active: e.target.checked })}
                  />
                  حساب کاربری فعال باشد
                </label>
              </div>
              <div className="form-actions">
                <button type="submit">ایجاد کاربر</button>
                <button type="button" onClick={() => setShowCreateForm(false)}>لغو</button>
              </div>
            </form>
          </div>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '25px' }}>
        <div className="card">
          <h3 style={{ marginBottom: '20px' }}>لیست کاربران</h3>
          <div style={{ 
            background: '#f9fafb', 
            border: '2px solid #e5e7eb', 
            borderRadius: '12px', 
            overflow: 'hidden',
            maxHeight: '500px',
            overflowY: 'auto'
          }}>
            {users.length === 0 ? (
              <div style={{ padding: '40px', textAlign: 'center', color: '#9ca3af' }}>
                هیچ کاربری یافت نشد
              </div>
            ) : (
              users.map(user => (
                <div
                  key={user.id}
                  style={{
                    padding: '18px',
                    borderBottom: '1px solid #e5e7eb',
                    background: selectedUser?.id === user.id ? '#e0e7ff' : 'white',
                    transition: 'all 0.2s'
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                    <div 
                      onClick={() => handleUserSelect(user)}
                      style={{ flex: 1, cursor: 'pointer' }}
                    >
                      <div style={{ 
                        fontWeight: '700', 
                        marginBottom: '6px',
                        fontSize: '1rem',
                        color: '#111827'
                      }}>
                        {user.name || user.email}
                      </div>
                      <div style={{ fontSize: '0.85rem', color: '#6b7280', marginBottom: '6px' }}>
                        {user.email}
                      </div>
                      <div style={{ fontSize: '0.8rem', marginTop: '8px' }}>
                        {user.is_active ? (
                          <span style={{ 
                            background: '#d1fae5', 
                            color: '#065f46',
                            padding: '4px 10px',
                            borderRadius: '12px',
                            fontWeight: '700'
                          }}>
                            ✓ فعال
                          </span>
                        ) : (
                          <span style={{ 
                            background: '#fee2e2', 
                            color: '#991b1b',
                            padding: '4px 10px',
                            borderRadius: '12px',
                            fontWeight: '700'
                          }}>
                            ✗ غیرفعال
                          </span>
                        )}
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '8px', flexDirection: 'column' }}>
                      <button
                        onClick={() => handleToggleUserStatus(user.id, user.is_active)}
                        style={{
                          padding: '6px 12px',
                          background: user.is_active ? '#fef3c7' : '#d1fae5',
                          color: user.is_active ? '#92400e' : '#065f46',
                          border: 'none',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          fontSize: '0.8rem',
                          fontWeight: '700',
                          whiteSpace: 'nowrap'
                        }}
                      >
                        {user.is_active ? 'غیرفعال کن' : 'فعال کن'}
                      </button>
                      <button
                        onClick={() => handleDeleteUser(user.id)}
                        style={{
                          padding: '6px 12px',
                          background: '#fee2e2',
                          color: '#991b1b',
                          border: 'none',
                          borderRadius: '8px',
                          cursor: 'pointer',
                          fontSize: '0.8rem',
                          fontWeight: '700'
                        }}
                      >
                        حذف
                      </button>
                    </div>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="card">
          {selectedUser ? (
            <div>
              <h3 style={{ marginBottom: '20px' }}>
                Quota برای {selectedUser.name || selectedUser.email}
              </h3>
              {quota ? (
                <div style={{ 
                  background: 'linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%)', 
                  padding: '20px', 
                  borderRadius: '12px', 
                  marginBottom: '20px',
                  border: '2px solid rgba(102, 126, 234, 0.2)'
                }}>
                  <div style={{ 
                    marginBottom: '15px',
                    paddingBottom: '15px',
                    borderBottom: '1px solid rgba(102, 126, 234, 0.2)'
                  }}>
                    <span style={{ color: '#6b7280', fontSize: '0.9rem' }}>در دقیقه:</span>
                    <span style={{ 
                      float: 'left',
                      fontWeight: '800',
                      fontSize: '1.3rem',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent'
                    }}>
                      {quota.per_minute}
                    </span>
                  </div>
                  <div style={{ 
                    marginBottom: '15px',
                    paddingBottom: '15px',
                    borderBottom: '1px solid rgba(102, 126, 234, 0.2)'
                  }}>
                    <span style={{ color: '#6b7280', fontSize: '0.9rem' }}>در ساعت:</span>
                    <span style={{ 
                      float: 'left',
                      fontWeight: '800',
                      fontSize: '1.3rem',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent'
                    }}>
                      {quota.per_hour}
                    </span>
                  </div>
                  <div>
                    <span style={{ color: '#6b7280', fontSize: '0.9rem' }}>در روز:</span>
                    <span style={{ 
                      float: 'left',
                      fontWeight: '800',
                      fontSize: '1.3rem',
                      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent'
                    }}>
                      {quota.per_day}
                    </span>
                  </div>
                </div>
              ) : (
                <div className="alert alert-warning" style={{ marginBottom: '20px' }}>
                  هنوز quota تنظیم نشده است
                </div>
              )}

              <button
                onClick={() => setShowQuotaForm(!showQuotaForm)}
                className="btn-primary"
                style={{
                  width: '100%',
                  marginBottom: '20px',
                  padding: '12px'
                }}
              >
                {quota ? 'ویرایش Quota' : 'تنظیم Quota'}
              </button>

              {showQuotaForm && (
                <div style={{ background: 'white', padding: '20px', borderRadius: '12px', border: '2px solid #e5e7eb' }}>
                  <form onSubmit={handleSaveQuota}>
                    <div className="form-group">
                      <label>در دقیقه:</label>
                      <input
                        type="number"
                        value={quotaForm.per_minute}
                        onChange={(e) => setQuotaForm({ ...quotaForm, per_minute: parseInt(e.target.value) || 0 })}
                        min="0"
                      />
                    </div>
                    <div className="form-group">
                      <label>در ساعت:</label>
                      <input
                        type="number"
                        value={quotaForm.per_hour}
                        onChange={(e) => setQuotaForm({ ...quotaForm, per_hour: parseInt(e.target.value) || 0 })}
                        min="0"
                      />
                    </div>
                    <div className="form-group">
                      <label>در روز:</label>
                      <input
                        type="number"
                        value={quotaForm.per_day}
                        onChange={(e) => setQuotaForm({ ...quotaForm, per_day: parseInt(e.target.value) || 0 })}
                        min="0"
                      />
                    </div>
                    <div className="form-actions">
                      <button type="submit">ذخیره</button>
                      <button type="button" onClick={() => setShowQuotaForm(false)}>لغو</button>
                    </div>
                  </form>
                </div>
              )}
            </div>
          ) : (
            <div style={{ textAlign: 'center', color: '#999', padding: '40px' }}>
              یک کاربر را انتخاب کنید
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// نمایش لاگ‌های درخواست (Request Logs)
// نمایش تاریخچه تمام درخواست‌های دریافتی با جزئیات کامل
function Logs() {
  const [logs, setLogs] = useState([]);
  const [routes, setRoutes] = useState([]);
  const [filters, setFilters] = useState({ route_id: '', status: '', limit: 100 });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadRoutes();
    loadLogs();
  }, []);

  useEffect(() => {
    loadLogs();
  }, [filters]);

  const loadRoutes = async () => {
    try {
      const res = await axios.get(`${API_URL}/admin/base_routes`);
      setRoutes(res.data);
    } catch (error) {
      console.error('خطا در بارگذاری مسیرها:', error);
    }
  };

  const loadLogs = async () => {
    setLoading(true);
    try {
      const params = {};
      if (filters.route_id) params.route_id = filters.route_id;
      if (filters.status) params.status = filters.status;
      if (filters.limit) params.limit = filters.limit;
      const res = await axios.get(`${API_URL}/admin/logs`, { params });
      setLogs(res.data);
    } catch (error) {
      console.error('خطا در بارگذاری لاگ‌ها:', error);
      window.alert('خطا در بارگذاری لاگ‌ها: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1>لاگ‌های درخواست</h1>
          <p style={{ color: '#666', fontSize: '14px', marginTop: '5px' }}>
            تاریخچه تمام درخواست‌های دریافتی با جزئیات کامل شامل زمان، مسیر، وضعیت و زمان پاسخ
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px' }}>
          <select value={filters.route_id} onChange={(e) => setFilters({ ...filters, route_id: e.target.value })}>
            <option value="">همه مسیرها</option>
            {routes.map(route => (
              <option key={route.id} value={route.id}>{route.name}</option>
            ))}
          </select>
          <input
            type="number"
            placeholder="کد وضعیت"
            value={filters.status}
            onChange={(e) => setFilters({ ...filters, status: e.target.value })}
            style={{ width: '120px' }}
          />
          <input
            type="number"
            placeholder="تعداد"
            value={filters.limit}
            onChange={(e) => setFilters({ ...filters, limit: parseInt(e.target.value) || 100 })}
            style={{ width: '100px' }}
          />
        </div>
      </div>

      {loading ? (
        <div style={{ textAlign: 'center', padding: '40px' }}>در حال بارگذاری...</div>
      ) : logs.length === 0 ? (
        <div style={{ textAlign: 'center', padding: '40px', color: '#666' }}>
          هیچ لاگی یافت نشد
        </div>
      ) : (
        <table className="data-table">
          <thead>
            <tr>
              <th>زمان</th>
              <th>متد</th>
              <th>مسیر</th>
              <th>وضعیت</th>
              <th>زمان پاسخ</th>
              <th>آدرس IP</th>
            </tr>
          </thead>
          <tbody>
            {logs.map(log => (
              <tr key={log.id}>
                <td>{new Date(log.created_at).toLocaleString('fa-IR')}</td>
                <td>{log.method}</td>
                <td>{log.path}</td>
                <td className={log.response_status >= 400 ? 'error' : ''}>
                  {log.response_status >= 400 ? (
                    <span style={{ color: '#e74c3c', fontWeight: 'bold' }}>{log.response_status}</span>
                  ) : (
                    <span style={{ color: '#27ae60' }}>{log.response_status}</span>
                  )}
                </td>
                <td>{log.latency_ms}ms</td>
                <td>{log.client_ip}</td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

// کامپوننت اصلی برنامه
function App() {
  return (
    <Router>
      <div className="app">
        <nav className="sidebar">
          <h2>پنل مدیریت API Proxy</h2>
          <Link to="/">مسیرهای پایه</Link>
          <Link to="/pools">پول‌های کلید</Link>
          <Link to="/keys">کلیدهای API</Link>
          <Link to="/users">مدیریت کاربران</Link>
          <Link to="/metrics">آمار و متریک</Link>
          <Link to="/logs">لاگ‌های درخواست</Link>
        </nav>
        <main className="main-content">
          <Routes>
            <Route path="/" element={<BaseRoutes />} />
            <Route path="/users" element={<UserManagement />} />
            <Route path="/pools" element={<KeyPools />} />
            <Route path="/keys" element={<APIKeys />} />
            <Route path="/metrics" element={<Metrics />} />
            <Route path="/logs" element={<Logs />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
