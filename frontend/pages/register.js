import { useState } from 'react';
import { useRouter } from 'next/router';
import '../styles/globals.css';

const Register = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const router = useRouter();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    const currentHost = typeof window !== 'undefined' ? window.location.hostname : 'localhost';
    const backendUrl = `http://${currentHost}:8000`;
    
    const response = await fetch(`${backendUrl}/api/users/register/`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ username, email, password }),
    });

    if (response.ok) {
      router.push('/login');
    } else {
      const data = await response.json();
      const errorMsg = data.detail || 'Ошибка регистрации';

      if (data.username && data.username.includes('already exists')) {
        setError('Аккаунт с таким именем пользователя уже существует');
      } else if (data.email && data.email.includes('already exists')) {
        setError('Аккаунт с таким email уже существует');
      } else {
        setError(errorMsg);
      }
    }
  };

  const handleLoginRedirect = () => {
    router.push('/login');
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-800">
      <div className="bg-gray-900 p-8 rounded-lg shadow-md w-full sm:w-96">
        <h1 className="text-3xl font-bold text-center text-white mb-6">Создать аккаунт</h1>
        <form onSubmit={handleRegister}>
          <div className="mb-4">
            <label htmlFor="username" className="block text-sm font-medium text-gray-300">Имя пользователя</label>
            <input
              type="text"
              id="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              required
              className="w-full px-4 py-2 mt-2 border border-gray-700 bg-gray-800 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="mb-4">
            <label htmlFor="email" className="block text-sm font-medium text-gray-300">Электронная почта</label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              className="w-full px-4 py-2 mt-2 border border-gray-700 bg-gray-800 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="mb-6">
            <label htmlFor="password" className="block text-sm font-medium text-gray-300">Пароль</label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              className="w-full px-4 py-2 mt-2 border border-gray-700 bg-gray-800 text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          {error && <p className="text-red-500 text-sm mb-4">{error}</p>}
          <button
            type="submit"
            className="w-full py-2 px-4 bg-blue-500 text-white font-semibold rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-400"
          >
            Зарегистрироваться
          </button>
        </form>
        <div className="mt-4 text-center">
          <button
            onClick={handleLoginRedirect}
            className="text-sm text-blue-500 hover:text-blue-700"
          >
            Уже есть аккаунт? Войти
          </button>
        </div>
      </div>
    </div>
  );
};

export default Register;

