import { useCallback, useEffect, useState } from 'react';
import axios from 'axios';
import { 
  Shield, Activity, PlusCircle, User, LogOut, 
  CheckCircle, 
  Clock, Heart, FileText, ChevronRight, Menu,
  LayoutDashboard, ShieldCheck, Users, Settings, RotateCcw,
  Globe, Fingerprint, History, Eye, Home
} from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000';

interface UserData {
  username: string;
  email: string;
  role: string;
}

interface MedicalRecord {
  id: number;
  patient_id: number;
  diagnosis: string;
  treatment: string;
  hash: string;
  previous_hash: string;
  timestamp: string;
  doctor_id: number;
}

function App() {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [user, setUser] = useState<UserData | null>(null);
  const [records, setRecords] = useState<MedicalRecord[]>([]);
  const [integrity, setIntegrity] = useState({ is_valid: true, total_records: 0 });
  const [loading, setLoading] = useState(false);
  const [isSidebarOpen, setSidebarOpen] = useState(true);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');
  const [activeTab, setActiveTab] = useState('dashboard');
  
  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const [registerData, setRegisterData] = useState({ username: '', email: '', password: '', role: 'doctor' });
  const [recordData, setRecordData] = useState({ patient_id: '', diagnosis: '', treatment: '' });

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setRecords([]);
    setActiveTab('dashboard');
  };

  const fetchData = useCallback(async () => {
    if (!token) {
      return;
    }
    setLoading(true);
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } };
      const [recsRes, integrityRes, userRes] = await Promise.all([
        axios.get(`${API_URL}/records/`, config),
        axios.get(`${API_URL}/records/verify`, config),
        axios.get(`${API_URL}/auth/me`, config)
      ]);
      setRecords(recsRes.data.reverse());
      setIntegrity(integrityRes.data);
      setUser(userRes.data);
    } catch (err) {
      if (axios.isAxiosError(err) && err.response?.status === 401) handleLogout();
    } finally {
      setLoading(false);
    }
  }, [token]);

  useEffect(() => {
    if (token) {
      void fetchData();
    }
  }, [fetchData, token]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('username', loginData.username);
      formData.append('password', loginData.password);
      const res = await axios.post(`${API_URL}/auth/login`, formData);
      localStorage.setItem('token', res.data.access_token);
      setToken(res.data.access_token);
      setLoginData({ username: '', password: '' });
    } catch {
      alert('Falha na autenticação.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await axios.post(`${API_URL}/auth/register`, registerData);
      alert('Cadastro realizado com sucesso!');
      setAuthMode('login');
      setRegisterData({ username: '', email: '', password: '', role: 'doctor' });
    } catch {
      alert('Erro ao realizar cadastro.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRecord = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const config = { headers: { Authorization: `Bearer ${token}` } };
      await axios.post(`${API_URL}/records/`, {
        patient_id: parseInt(recordData.patient_id),
        diagnosis: recordData.diagnosis,
        treatment: recordData.treatment
      }, config);
      alert('Bloco minerado com sucesso!');
      setRecordData({ patient_id: '', diagnosis: '', treatment: '' });
      await fetchData();
    } catch {
      alert('Erro ao registrar no Blockchain.');
    } finally {
      setLoading(false);
    }
  };

  // Vistas especializadas
  const renderDoctorDashboard = () => (
    <div className="space-y-8">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="bg-white p-7 rounded-[32px] border border-slate-100 shadow-sm">
          <p className="text-slate-400 text-[10px] font-black uppercase tracking-widest mb-1">Registros Clínicos</p>
          <h3 className="text-3xl font-black text-slate-900">{records.length} Blocos</h3>
          <div className="mt-4 flex items-center gap-2 text-emerald-500 font-bold text-xs">
            <Activity className="w-4 h-4" /> <span>Conexão Estável</span>
          </div>
        </div>
        <div className="bg-white p-7 rounded-[32px] border border-slate-100 shadow-sm">
          <p className="text-slate-400 text-[10px] font-black uppercase tracking-widest mb-1">Integridade SUS</p>
          <h3 className="text-3xl font-black text-slate-900">{integrity.is_valid ? '100%' : 'Erro'}</h3>
          <div className="mt-4 flex items-center gap-2 text-blue-500 font-bold text-xs">
            <ShieldCheck className="w-4 h-4" /> <span>Rede Protegida</span>
          </div>
        </div>
        <div className="bg-white p-7 rounded-[32px] border border-slate-100 shadow-sm">
          <p className="text-slate-400 text-[10px] font-black uppercase tracking-widest mb-1">Carga de Trabalho</p>
          <h3 className="text-3xl font-black text-slate-900">0.4s</h3>
          <div className="mt-4 flex items-center gap-2 text-amber-500 font-bold text-xs">
            <Clock className="w-4 h-4" /> <span>Latência Média</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-12 gap-10">
        <div className="xl:col-span-4">
          <div className="bg-slate-900 rounded-[40px] p-10 text-white shadow-2xl relative overflow-hidden">
            <PlusCircle className="w-12 h-12 mb-6 text-blue-400" />
            <h3 className="text-2xl font-black mb-8">Novo Atendimento</h3>
            <form onSubmit={handleCreateRecord} className="space-y-5">
              <input type="text" placeholder="CPF ou ID do Paciente" className="w-full bg-white/10 border border-white/10 rounded-2xl py-4 px-5 text-white placeholder:text-white/30 outline-none focus:bg-white/20 transition-all" value={recordData.patient_id} onChange={(e) => setRecordData({ ...recordData, patient_id: e.target.value })} />
              <input type="text" placeholder="Diagnóstico" className="w-full bg-white/10 border border-white/10 rounded-2xl py-4 px-5 text-white placeholder:text-white/30 outline-none focus:bg-white/20 transition-all" value={recordData.diagnosis} onChange={(e) => setRecordData({ ...recordData, diagnosis: e.target.value })} />
              <textarea placeholder="Prescrição / Tratamento" rows={3} className="w-full bg-white/10 border border-white/10 rounded-2xl py-4 px-5 text-white placeholder:text-white/30 outline-none focus:bg-white/20 transition-all resize-none" value={recordData.treatment} onChange={(e) => setRecordData({ ...recordData, treatment: e.target.value })} />
              <button type="submit" className="w-full bg-blue-600 text-white font-black py-4 rounded-2xl hover:bg-blue-700 transition-all uppercase text-xs tracking-widest shadow-lg shadow-blue-900/20">Registrar no SUS</button>
            </form>
          </div>
        </div>
        <div className="xl:col-span-8">
          <div className="bg-white rounded-[40px] border border-slate-100 shadow-sm overflow-hidden">
            <div className="p-8 border-b border-slate-50 flex items-center justify-between">
              <h3 className="text-xl font-black text-slate-900">Rede Nacional de Registros</h3>
              <RotateCcw className="w-5 h-5 text-slate-400 cursor-pointer hover:rotate-180 transition-transform duration-500" onClick={fetchData} />
            </div>
            <div className="divide-y divide-slate-50 max-h-[600px] overflow-y-auto">
              {records.map((rec, i) => (
                <div key={rec.id} className="p-8 hover:bg-slate-50 transition-all">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 bg-blue-50 text-blue-600 rounded-xl flex items-center justify-center font-black">#{records.length - i}</div>
                      <div>
                        <p className="text-sm font-black text-slate-900">Paciente ID: {rec.patient_id}</p>
                        <p className="text-[10px] text-slate-400 font-bold uppercase">{new Date(rec.timestamp).toLocaleString()}</p>
                      </div>
                    </div>
                    <span className="text-[10px] font-mono bg-slate-100 px-2 py-1 rounded text-slate-500 truncate max-w-[120px]">{rec.hash}</span>
                  </div>
                  <p className="text-sm font-bold text-slate-700">Dx: {rec.diagnosis}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  const renderPatientDashboard = () => (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div className="bg-blue-600 rounded-[40px] p-12 text-white relative overflow-hidden shadow-2xl shadow-blue-200">
        <Fingerprint className="absolute right-[-20px] top-[-20px] w-64 h-64 text-white/5" />
        <div className="relative z-10 max-w-2xl">
          <h2 className="text-4xl font-black tracking-tight mb-4">Seu Prontuário Digital Único</h2>
          <p className="text-blue-100 text-lg font-medium leading-relaxed opacity-90">
            Bem-vindo, {user?.username}. Seus dados de saúde estão protegidos pela tecnologia Blockchain do SUS, garantindo que seu histórico seja imutável e acessível em qualquer unidade de saúde.
          </p>
          <div className="mt-10 flex gap-4">
            <div className="bg-white/10 backdrop-blur-md px-6 py-4 rounded-3xl border border-white/10">
              <p className="text-[10px] font-black uppercase tracking-widest text-blue-200">Identidade Digital</p>
              <p className="text-xl font-black mt-1 flex items-center gap-2"><CheckCircle className="w-5 h-5 text-emerald-400" /> Ativa</p>
            </div>
            <div className="bg-white/10 backdrop-blur-md px-6 py-4 rounded-3xl border border-white/10">
              <p className="text-[10px] font-black uppercase tracking-widest text-blue-200">Registros no SUS</p>
              <p className="text-xl font-black mt-1">{records.filter(r => r.patient_id === parseInt(user?.username.length.toString() || '0')).length} Blocos</p>
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10">
        <div className="lg:col-span-8">
          <div className="bg-white rounded-[40px] border border-slate-100 shadow-sm overflow-hidden">
            <div className="p-10 border-b border-slate-50 flex items-center justify-between">
              <div>
                <h3 className="text-2xl font-black text-slate-900">Linha do Tempo de Saúde</h3>
                <p className="text-slate-400 text-xs font-bold uppercase tracking-widest mt-1">Sua jornada no Sistema Único de Saúde</p>
              </div>
              <History className="w-6 h-6 text-slate-300" />
            </div>
            <div className="p-10 space-y-8">
              {records
                .filter(rec => user?.role === 'doctor' || rec.patient_id.toString() === user?.username)
                .length === 0 ? (
                <div className="text-center py-20 text-slate-300 font-bold uppercase tracking-widest text-sm">Nenhum registro encontrado no sistema</div>
              ) : (
                records
                  .filter(rec => user?.role === 'doctor' || rec.patient_id.toString() === user?.username)
                  .map((rec) => (
                  <div key={rec.id} className="relative pl-10 before:absolute before:left-0 before:top-0 before:bottom-0 before:w-1 before:bg-slate-100 before:rounded-full">
                    <div className="absolute left-[-6px] top-0 w-4 h-4 rounded-full bg-blue-500 ring-4 ring-white" />
                    <div className="bg-slate-50 p-8 rounded-[32px] border border-slate-100 hover:border-blue-200 transition-all group">
                      <div className="flex justify-between items-start mb-6">
                        <div>
                          <p className="text-[10px] font-black text-blue-500 uppercase tracking-widest mb-1">Diagnóstico Oficial</p>
                          <h4 className="text-xl font-black text-slate-900">{rec.diagnosis}</h4>
                        </div>
                        <div className="text-right">
                          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Data do Registro</p>
                          <p className="text-sm font-bold text-slate-900">{new Date(rec.timestamp).toLocaleDateString()}</p>
                        </div>
                      </div>
                      <div className="bg-white p-6 rounded-2xl border border-slate-200/50 mb-6">
                        <p className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-2 flex items-center gap-2"><FileText className="w-3.5 h-3.5" /> Conduta Médica</p>
                        <p className="text-slate-700 font-medium italic">"{rec.treatment}"</p>
                      </div>
                      <div className="flex items-center justify-between pt-4 border-t border-slate-100">
                        <div className="flex items-center gap-2">
                          <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center"><User className="w-4 h-4 text-slate-500" /></div>
                          <p className="text-xs font-bold text-slate-500">Profissional Responsável #{rec.doctor_id}</p>
                        </div>
                        <button className="flex items-center gap-2 text-[10px] font-black text-blue-600 uppercase tracking-widest hover:translate-x-1 transition-transform">Verificar Integridade <ChevronRight className="w-3 h-3" /></button>
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>

        <div className="lg:col-span-4 space-y-8">
          <div className="bg-white p-10 rounded-[40px] border border-slate-100 shadow-sm">
            <Shield className="w-12 h-12 text-emerald-500 mb-6" />
            <h3 className="text-xl font-black text-slate-900 mb-4">Integridade de Dados</h3>
            <p className="text-slate-500 text-sm leading-relaxed mb-8">Nenhum dado seu pode ser alterado ou deletado. A Blockchain garante a imutabilidade eterna do seu histórico.</p>
            <div className="p-6 bg-emerald-50 rounded-3xl border border-emerald-100">
              <div className="flex justify-between items-center mb-2">
                <span className="text-[10px] font-black text-emerald-600 uppercase">Sincronismo</span>
                <span className="text-xs font-bold text-emerald-600">100%</span>
              </div>
              <div className="w-full h-2 bg-emerald-200 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 w-full" />
              </div>
            </div>
          </div>

          <div className="bg-slate-900 p-10 rounded-[40px] text-white">
            <Eye className="w-10 h-10 text-blue-400 mb-6" />
            <h3 className="text-xl font-black mb-4">Quem Acessou?</h3>
            <p className="text-slate-400 text-sm mb-8">Veja o log de auditoria de todos os profissionais que consultaram seus dados.</p>
            <div className="space-y-4">
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/10">
                <span className="text-xs font-bold">Dr. Rodrigo (Cardio)</span>
                <span className="text-[10px] text-slate-500 uppercase">Há 2h</span>
              </div>
              <div className="flex items-center justify-between p-4 bg-white/5 rounded-2xl border border-white/10">
                <span className="text-xs font-bold">Enf. Maria</span>
                <span className="text-[10px] text-slate-500 uppercase">Ontem</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );

  if (!token) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center p-6 font-sans">
        <div className="w-full max-w-[440px]">
          <div className="flex flex-col items-center mb-8 text-center">
            <div className="w-16 h-16 bg-blue-600 rounded-3xl flex items-center justify-center shadow-2xl shadow-blue-200 mb-6">
              <Shield className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-black text-slate-900 tracking-tight">SUS Blockchain</h1>
            <p className="text-blue-600 font-black uppercase tracking-widest text-[10px] mt-2">Ministério da Saúde</p>
            <p className="text-slate-400 font-bold text-xs mt-1">Governo Federal</p>
          </div>

          <div className="bg-white rounded-[32px] p-10 shadow-2xl shadow-slate-200/50 border border-slate-100">
            <div className="flex p-1.5 bg-slate-100 rounded-2xl mb-8">
              <button onClick={() => setAuthMode('login')} className={`flex-1 py-3 text-[11px] font-black rounded-xl transition-all ${authMode === 'login' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}>ACESSO</button>
              <button onClick={() => setAuthMode('register')} className={`flex-1 py-3 text-[11px] font-black rounded-xl transition-all ${authMode === 'register' ? 'bg-white text-blue-600 shadow-sm' : 'text-slate-500 hover:text-slate-700'}`}>CADASTRO</button>
            </div>

            {authMode === 'login' ? (
              <form onSubmit={handleLogin} className="space-y-6">
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">CPF / Usuário</label>
                  <input type="text" required className="w-full bg-slate-50 border border-slate-200 rounded-2xl py-4 px-5 text-sm focus:ring-4 focus:ring-blue-500/5 outline-none transition-all" value={loginData.username} onChange={(e) => setLoginData({ ...loginData, username: e.target.value })} />
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Senha</label>
                  <input type="password" required className="w-full bg-slate-50 border border-slate-200 rounded-2xl py-4 px-5 text-sm focus:ring-4 focus:ring-blue-500/5 outline-none transition-all" value={loginData.password} onChange={(e) => setLoginData({ ...loginData, password: e.target.value })} />
                </div>
                <button type="submit" disabled={loading} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-black py-5 rounded-2xl shadow-xl shadow-blue-200 transition-all flex items-center justify-center gap-3 uppercase text-xs tracking-widest">
                  {loading ? <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" /> : <>Entrar no Sistema <ChevronRight className="w-4 h-4" /></>}
                </button>
              </form>
            ) : (
              <form onSubmit={handleRegister} className="space-y-5">
                <div className="grid grid-cols-2 gap-4">
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Usuário</label>
                    <input type="text" required className="w-full bg-slate-50 border border-slate-200 rounded-2xl py-4 px-5 text-sm outline-none" value={registerData.username} onChange={(e) => setRegisterData({ ...registerData, username: e.target.value })} />
                  </div>
                  <div className="space-y-2">
                    <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Perfil</label>
                    <select className="w-full bg-slate-50 border border-slate-200 rounded-2xl py-4 px-5 text-sm outline-none appearance-none" value={registerData.role} onChange={(e) => setRegisterData({ ...registerData, role: e.target.value })}>
                      <option value="doctor">Profissional</option>
                      <option value="patient">Cidadão</option>
                    </select>
                  </div>
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">E-mail</label>
                  <input type="email" required className="w-full bg-slate-50 border border-slate-200 rounded-2xl py-4 px-5 text-sm outline-none" value={registerData.email} onChange={(e) => setRegisterData({ ...registerData, email: e.target.value })} />
                </div>
                <div className="space-y-2">
                  <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest ml-1">Senha</label>
                  <input type="password" required className="w-full bg-slate-50 border border-slate-200 rounded-2xl py-4 px-5 text-sm outline-none" value={registerData.password} onChange={(e) => setRegisterData({ ...registerData, password: e.target.value })} />
                </div>
                <button type="submit" disabled={loading} className="w-full bg-blue-600 hover:bg-blue-700 text-white font-black py-5 rounded-2xl shadow-xl shadow-blue-200 transition-all uppercase text-xs tracking-widest">Finalizar Cadastro</button>
              </form>
            )}
          </div>
        </div>
      </div>
    );
  }

  const sidebarItems = user?.role === 'doctor' ? [
    { id: 'dashboard', icon: LayoutDashboard, label: 'Painel de Controle' },
    { id: 'patients', icon: Users, label: 'Atendimentos' },
    { id: 'network', icon: Globe, label: 'Rede SUS' },
    { id: 'security', icon: ShieldCheck, label: 'Segurança' },
  ] : [
    { id: 'dashboard', icon: Heart, label: 'Meu Prontuário' },
    { id: 'security', icon: ShieldCheck, label: 'Minha Segurança' },
    { id: 'settings', icon: Settings, label: 'Configurações' },
  ];

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900 font-sans flex overflow-hidden">
      <aside className={`bg-white border-r border-slate-200 transition-all duration-300 flex flex-col shadow-xl ${isSidebarOpen ? 'w-72' : 'w-24'}`}>
        <div 
          className="p-8 flex items-center gap-4 cursor-pointer hover:opacity-80 transition-opacity"
          onClick={() => setActiveTab('dashboard')}
        >
          <div className="w-10 h-10 bg-blue-600 rounded-2xl flex items-center justify-center shrink-0 shadow-lg shadow-blue-200">
            <Shield className="w-5 h-5 text-white" />
          </div>
          {isSidebarOpen && <span className="font-black text-lg tracking-tight">SUS Blockchain</span>}
        </div>

        <nav className="flex-1 px-4 space-y-2 mt-6">
          {sidebarItems.map((item) => (
            <button key={item.id} onClick={() => setActiveTab(item.id)} className={`w-full flex items-center gap-4 p-4 rounded-2xl transition-all ${activeTab === item.id ? 'bg-blue-50 text-blue-600 font-black shadow-sm' : 'text-slate-500 hover:bg-slate-50 hover:text-slate-900'}`}>
              <item.icon className="w-5 h-5 shrink-0" />
              {isSidebarOpen && <span className="text-sm">{item.label}</span>}
            </button>
          ))}
        </nav>

        <div className="p-4 border-t border-slate-50">
          <button onClick={handleLogout} className="w-full flex items-center gap-4 p-4 rounded-2xl text-slate-400 hover:bg-rose-50 hover:text-rose-600 transition-all group">
            <LogOut className="w-5 h-5 shrink-0" />
            {isSidebarOpen && <span className="text-sm font-bold">Sair</span>}
          </button>
        </div>
      </aside>

      <main className="flex-1 flex flex-col h-screen overflow-hidden">
        <header className="h-24 bg-white/80 backdrop-blur-md border-b border-slate-200 px-10 flex items-center justify-between z-10">
          <div className="flex items-center gap-8">
            <button onClick={() => setSidebarOpen(!isSidebarOpen)} className="p-3 hover:bg-slate-100 rounded-2xl text-slate-500 border border-slate-100 transition-all">
              <Menu className="w-5 h-5" />
            </button>
            <div>
              <h2 className="text-2xl font-black text-slate-900 tracking-tight">{user?.role === 'doctor' ? 'Portal do Profissional' : 'Portal do Cidadão'}</h2>
              <p className="text-[10px] font-black text-blue-600 uppercase tracking-widest mt-1">Ministério da Saúde - Governo Federal</p>
            </div>
          </div>

          <div className="flex items-center gap-6">
            <button 
              onClick={() => setActiveTab('dashboard')}
              className="p-3 hover:bg-slate-100 rounded-2xl text-slate-500 border border-slate-100 transition-all flex items-center gap-2 group"
              title="Página Inicial"
            >
              <Home className="w-5 h-5 group-hover:text-blue-600 transition-colors" />
              <span className="text-[10px] font-black uppercase tracking-widest hidden lg:block">Início</span>
            </button>
            
            <div className="flex items-center gap-6 pl-8 border-l border-slate-100">
            <div className="text-right">
              <p className="text-sm font-black text-slate-900 leading-none mb-1">{user?.username}</p>
              <p className="text-[10px] text-blue-500 font-black uppercase tracking-widest">{user?.role === 'doctor' ? 'Profissional de Saúde' : 'Cidadão Beneficiário'}</p>
            </div>
            <div className="w-12 h-12 bg-blue-50 rounded-2xl flex items-center justify-center border-2 border-white shadow-lg shadow-blue-100 ring-4 ring-blue-50/50">
              <User className="w-6 h-6 text-blue-600" />
            </div>
          </div>
        </div>
      </header>

        <div className="flex-1 overflow-y-auto p-10 bg-slate-50/50">
          {activeTab === 'dashboard' && (user?.role === 'doctor' ? renderDoctorDashboard() : renderPatientDashboard())}
          {activeTab === 'patients' && (
            <div className="p-20 text-center">
              <Users className="w-16 h-16 text-slate-200 mx-auto mb-4" />
              <p className="text-slate-400 font-bold uppercase tracking-widest text-xs">Módulo de Gestão de Prontuários</p>
            </div>
          )}
          {activeTab === 'network' && (
            <div className="p-20 text-center">
              <Globe className="w-16 h-16 text-slate-200 mx-auto mb-4" />
              <p className="text-slate-400 font-bold uppercase tracking-widest text-xs">Mapeamento de Nós da Rede Nacional</p>
            </div>
          )}
          {activeTab === 'security' && (
            <div className="p-20 text-center">
              <ShieldCheck className="w-16 h-16 text-slate-200 mx-auto mb-4" />
              <p className="text-slate-400 font-bold uppercase tracking-widest text-xs">Logs de Auditoria e Chaves Criptográficas</p>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
