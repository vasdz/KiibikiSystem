import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { ShieldCheck, Lock, User } from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';

export const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Отправляем форму как x-www-form-urlencoded (требование OAuth2)
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await api.post('/auth/login', formData, {
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded'
        }
    });

      // Сохраняем токен и роль
      login(response.data.access_token, response.data.role);

      // Редирект в зависимости от роли
      if (response.data.role === 'admin') {
        // Админов можно сразу на дашборд (пока сделаем просто /)
        navigate('/');
      } else {
        navigate('/');
      }

    } catch (err: any) {
      if (err.response?.status === 429) {
        setError('Слишком много попыток. Подождите минуту.');
      } else {
        setError('Неверный логин или пароль');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[url('https://images.unsplash.com/photo-1550751827-4bd374c3f58b?q=80&w=2070&auto=format&fit=crop')] bg-cover bg-center">
      {/* Темный оверлей */}
      <div className="absolute inset-0 bg-slate-950/80 backdrop-blur-sm" />

      <div className="relative w-full max-w-md p-8 bg-slate-900/50 border border-slate-800 rounded-2xl shadow-2xl backdrop-blur-md">
        <div className="flex flex-col items-center mb-8">
          <div className="h-16 w-16 bg-primary/10 rounded-full flex items-center justify-center mb-4 border border-primary/20">
            <ShieldCheck className="h-8 w-8 text-primary" />
          </div>
          <h1 className="text-2xl font-bold text-white tracking-tight">КиИБ Secure Access</h1>
          <p className="text-slate-400 text-sm mt-1">Введите данные студенческого билета</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <div className="relative">
              <User className="absolute left-3 top-3 h-4 w-4 text-slate-500" />
              <Input
                type="text"
                placeholder="Номер студ. билета (43К...)"
                className="pl-10"
                value={username}
                onChange={(e: React.ChangeEvent<HTMLInputElement>) => setUsername(e.target.value)}
                required
              />
            </div>
          </div>

          <div className="space-y-2">
            <div className="relative">
              <Lock className="absolute left-3 top-3 h-4 w-4 text-slate-500" />
              <Input
                type="password"
                placeholder="Пароль"
                className="pl-10"
                value={password}
                 onChange={(e: React.ChangeEvent<HTMLInputElement>) => setPassword(e.target.value)}
                required
              />
            </div>
          </div>

          {error && (
            <div className="p-3 rounded-md bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center">
              {error}
            </div>
          )}

          <Button type="submit" className="w-full" isLoading={loading}>
            Войти в систему
          </Button>
        </form>

        <div className="mt-6 text-center text-xs text-slate-600">
          Secure connection established. Ed25519 signatures active.
        </div>
      </div>
    </div>
  );
};
