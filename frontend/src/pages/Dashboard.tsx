import { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { LogOut, Wallet, User, History, Upload, Shield, Bell, X, Plus, Trash2, Coins } from 'lucide-react';
import { api } from '../api/client';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';

// --- Типы данных ---
interface UserProfile {
  id: number;
  username: string;
  full_name: string;
  group_number: string;
  balance: number;
  role: string;
}

interface Transaction {
  id: number;
  amount: number;
  reason: string;
  created_at: string;
}

interface Post {
  id: number;
  title: string;
  content: string;
  created_at: string;
  image_url?: string;
}

export const Dashboard = () => {
  const { logout } = useAuth();
  const navigate = useNavigate();

  // --- Состояния данных ---
  const [user, setUser] = useState<UserProfile | null>(null);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);

  // --- Состояния Модальных окон ---
  const [isProfileModalOpen, setIsProfileModalOpen] = useState(false);
  const [isPostModalOpen, setIsPostModalOpen] = useState(false);
  const [isAccrueModalOpen, setIsAccrueModalOpen] = useState(false); // <--- Модалка начисления

  // --- Поля форм ---
  // Профиль
  const [editName, setEditName] = useState('');

  // Пост
  const [newPostTitle, setNewPostTitle] = useState('');
  const [newPostContent, setNewPostContent] = useState('');
  const postImageRef = useRef<HTMLInputElement>(null);

  // Начисление баллов
  const [accrueUsername, setAccrueUsername] = useState('');
  const [accrueAmount, setAccrueAmount] = useState('');
  const [accrueReason, setAccrueReason] = useState('');

  // Загрузка файла
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // --- Загрузка всех данных ---
  const fetchData = async () => {
    try {
      // 1. Профиль
      const userRes = await api.get('/auth/me');
      setUser(userRes.data);
      setEditName(userRes.data.full_name);

      // 2. История транзакций
      try {
        const historyRes = await api.get('/ledger/history');
        setTransactions(historyRes.data);
      } catch (e) { console.error("Ошибка загрузки истории", e); }

      // 3. Новости
      try {
        const postsRes = await api.get('/posts/');
        setPosts(postsRes.data);
      } catch (e) { console.error("Ошибка загрузки новостей", e); }

    } catch (error) {
      console.error('Ошибка загрузки дэшборда', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  // --- ФУНКЦИЯ: Обновление профиля ---
  const handleUpdateProfile = async () => {
    try {
      await api.patch('/auth/me', { full_name: editName });
      setUser(prev => prev ? { ...prev, full_name: editName } : null);
      setIsProfileModalOpen(false);
      alert('✅ Профиль обновлен');
    } catch (e) {
      alert('Ошибка обновления профиля');
    }
  };

  // --- ФУНКЦИЯ: Загрузка файла достижения ---
  const handleUploadClick = () => fileInputRef.current?.click();

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    setUploading(true);
    try {
      await api.post('/achievements/upload', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      alert('✅ Файл отправлен на проверку');
    } catch (error) {
      alert('Ошибка загрузки');
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  // --- ФУНКЦИЯ: Создание поста (Админ) ---
  const handleCreatePost = async () => {
    if (!newPostTitle || !newPostContent) return alert('Заполните заголовок и текст');

    const formData = new FormData();
    formData.append('title', newPostTitle);
    formData.append('content', newPostContent);
    if (postImageRef.current?.files?.[0]) {
      formData.append('image', postImageRef.current.files[0]);
    }

    try {
      await api.post('/posts/', formData, { headers: { 'Content-Type': 'multipart/form-data' } });
      setIsPostModalOpen(false);
      setNewPostTitle('');
      setNewPostContent('');
      fetchData(); // Обновляем ленту
    } catch (e) {
      alert('Ошибка создания поста. Возможно, нет прав.');
    }
  };

  const handleDeletePost = async (id: number) => {
    if (!confirm('Удалить новость?')) return;
    try {
      await api.delete(`/posts/${id}`);
      fetchData(); // Обновляем ленту
    } catch (e) {
      alert('Не удалось удалить');
    }
  }

  // --- ФУНКЦИЯ: Начисление баллов (Админ) ---
  const handleAccruePoints = async () => {
    try {
        await api.post('/ledger/accrue', {
            username: accrueUsername,
            amount: Number(accrueAmount),
            reason: accrueReason
        });
        alert(`✅ Успешно начислено ${accrueAmount} пользователю ${accrueUsername}`);
        setIsAccrueModalOpen(false);
        setAccrueUsername('');
        setAccrueAmount('');
        setAccrueReason('');
        fetchData(); // Обновляем свой баланс и историю
    } catch (e: any) {
        alert('Ошибка: ' + (e.response?.data?.detail || 'Не удалось начислить'));
    }
  };


  if (loading) return <div className="min-h-screen bg-slate-950 flex items-center justify-center text-emerald-500">Загрузка системы...</div>;

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans">

      {/* Навигация */}
      <nav className="border-b border-slate-800 bg-slate-900/50 backdrop-blur-md sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <div className="flex items-center gap-2">
            <Shield className="h-6 w-6 text-emerald-500" />
            <span className="font-bold text-xl">КиИБик<span className="text-emerald-500">.SYS</span></span>
          </div>
          <div className="flex items-center gap-4">
            <div className="hidden md:block text-right">
              <p className="text-sm font-medium">{user?.full_name}</p>
              <p className="text-xs text-slate-400">{user?.role === 'admin' ? 'Администратор' : 'Студент'}</p>
            </div>
            <Button variant="ghost" onClick={handleLogout}><LogOut className="h-5 w-5" /></Button>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 py-8">

        {/* КНОПКА АДМИНА: Начислить баллы */}
        {user?.role === 'admin' && (
           <div className="mb-8">
              <Button
                variant="primary"
                onClick={() => setIsAccrueModalOpen(true)}
                className="flex items-center gap-2 px-4 py-2 bg-emerald-600 hover:bg-emerald-700 transition-colors"
              >
                <Coins className="h-4 w-4" />
                Начислить баллы
              </Button>
           </div>
        )}

        {/* Статистика */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          {/* Баланс */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 relative overflow-hidden">
            <div className="absolute top-0 right-0 p-4 opacity-10"><Wallet className="h-24 w-24 text-emerald-500" /></div>
            <p className="text-slate-400 text-sm">Ваш баланс</p>
            <h2 className="text-4xl font-bold mt-2">{user?.balance} <span className="text-emerald-500 text-lg">Kiib</span></h2>
          </div>

          {/* Профиль */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="h-12 w-12 bg-violet-500/10 rounded-full flex items-center justify-center text-violet-500"><User /></div>
              <div>
                <p className="text-sm text-slate-400">Пользователь</p>
                <p className="text-lg font-bold">{user?.username}</p>
              </div>
            </div>
            <Button variant="outline" className="w-full" onClick={() => setIsProfileModalOpen(true)}>Настройки профиля</Button>
          </div>

          {/* Загрузка */}
          <div className="bg-slate-900 border border-slate-800 rounded-xl p-6 flex flex-col items-center text-center">
            <Upload className="h-10 w-10 text-emerald-400 mb-3" />
            <h3 className="font-bold mb-1">Получить баллы</h3>
            <input type="file" ref={fileInputRef} className="hidden" onChange={handleFileChange} />
            <Button variant="primary" className="w-full" onClick={handleUploadClick} disabled={uploading}>
              {uploading ? 'Загрузка...' : 'Загрузить файл'}
            </Button>
          </div>
        </div>

        {/* Контент: История и Новости */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* История (Левая колонка) */}
          <div className="lg:col-span-2 space-y-6">
             <div className="bg-slate-900 border border-slate-800 rounded-xl p-6">
                <h3 className="font-bold mb-4 flex items-center gap-2"><History className="h-5 w-5" /> История транзакций</h3>
                {transactions.length === 0 ? <p className="text-slate-500 text-center py-4">История пуста</p> : (
                  <ul className="space-y-3">
                    {transactions.map(tx => (
                      <li key={tx.id} className="flex justify-between items-center border-b border-slate-800 pb-2 last:border-0">
                        <div>
                          <p className="text-white font-medium">{tx.reason}</p>
                          <p className="text-xs text-slate-500">{new Date(tx.created_at).toLocaleString()}</p>
                        </div>
                        <span className="text-emerald-400 font-bold">+{tx.amount} K</span>
                      </li>
                    ))}
                  </ul>
                )}
             </div>
          </div>

          {/* Новости (Правая колонка) */}
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h3 className="font-bold text-xl flex items-center gap-2"><Bell className="h-5 w-5 text-emerald-400" /> События</h3>
              {user?.role === 'admin' && (
                <Button variant="primary" onClick={() => setIsPostModalOpen(true)} className="p-2 bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-400">
                  <Plus className="h-4 w-4" />
                </Button>
              )}
            </div>

            <div className="space-y-4">
              {posts.length === 0 && <p className="text-slate-500 text-sm">Нет новостей</p>}
              {posts.map(post => (
                <div key={post.id} className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden shadow-lg hover:border-emerald-500/30 transition-colors">
                  {post.image_url && (
                    <img src={`http://127.0.0.1:8000${post.image_url}`} alt="Event" className="w-full h-32 object-cover" />
                  )}
                  <div className="p-4">
                    <div className="flex justify-between items-start">
                      <h4 className="font-bold text-white mb-2">{post.title}</h4>
                      {user?.role === 'admin' && (
                        <button onClick={() => handleDeletePost(post.id)} className="text-red-500 hover:text-red-400 p-1"><Trash2 className="h-4 w-4"/></button>
                      )}
                    </div>
                    <p className="text-sm text-slate-300 whitespace-pre-wrap">{post.content}</p>
                    <p className="text-xs text-slate-500 mt-3">{new Date(post.created_at).toLocaleDateString()}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>
      </main>

      {/* --- МОДАЛКИ --- */}

      {/* 1. Настройки профиля */}
      {isProfileModalOpen && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl w-full max-w-md relative">
            <button onClick={() => setIsProfileModalOpen(false)} className="absolute top-4 right-4 text-slate-400 hover:text-white"><X /></button>
            <h2 className="text-xl font-bold mb-4">Настройки профиля</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-slate-400 mb-1">ФИО</label>
                <input
                  value={editName} onChange={e => setEditName(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white focus:border-emerald-500 outline-none"
                />
              </div>
              <Button className="w-full" variant="primary" onClick={handleUpdateProfile}>Сохранить</Button>
            </div>
          </div>
        </div>
      )}

      {/* 2. Создать пост */}
      {isPostModalOpen && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl w-full max-w-md relative">
            <button onClick={() => setIsPostModalOpen(false)} className="absolute top-4 right-4 text-slate-400 hover:text-white"><X /></button>
            <h2 className="text-xl font-bold mb-4">Новое событие</h2>
            <div className="space-y-4">
              <input
                placeholder="Заголовок"
                value={newPostTitle} onChange={e => setNewPostTitle(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white outline-none"
              />
              <textarea
                placeholder="Текст новости..."
                value={newPostContent} onChange={e => setNewPostContent(e.target.value)}
                className="w-full h-32 bg-slate-950 border border-slate-800 rounded p-2 text-white outline-none resize-none"
              />
              <div>
                <label className="block text-sm text-slate-400 mb-1">Картинка (опционально)</label>
                <input type="file" ref={postImageRef} className="text-sm text-slate-400" />
              </div>
              <Button className="w-full" variant="primary" onClick={handleCreatePost}>Опубликовать</Button>
            </div>
          </div>
        </div>
      )}

      {/* 3. Начислить баллы */}
      {isAccrueModalOpen && (
        <div className="fixed inset-0 bg-black/80 flex items-center justify-center z-50 backdrop-blur-sm p-4">
          <div className="bg-slate-900 border border-slate-800 p-6 rounded-xl w-full max-w-md relative">
            <button onClick={() => setIsAccrueModalOpen(false)} className="absolute top-4 right-4 text-slate-400 hover:text-white"><X /></button>
            <h2 className="text-xl font-bold mb-4 text-emerald-400">Начислить баллы</h2>
            <div className="space-y-4">
              <input
                placeholder="Username студента (напр. admin)"
                value={accrueUsername} onChange={e => setAccrueUsername(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white outline-none focus:border-emerald-500"
              />
              <input
                type="number"
                placeholder="Сумма"
                value={accrueAmount} onChange={e => setAccrueAmount(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white outline-none focus:border-emerald-500"
              />
              <input
                placeholder="Причина (напр. Грант)"
                value={accrueReason} onChange={e => setAccrueReason(e.target.value)}
                className="w-full bg-slate-950 border border-slate-800 rounded p-2 text-white outline-none focus:border-emerald-500"
              />
              <Button className="w-full bg-emerald-600 hover:bg-emerald-700" variant="primary" onClick={handleAccruePoints}>Выполнить транзакцию</Button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};
