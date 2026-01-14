import React, { useState } from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { sendTestEmail } from '../lib/api';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { Switch } from '../components/ui/switch';
import { Avatar, AvatarFallback, AvatarImage } from '../components/ui/avatar';
import { Separator } from '../components/ui/separator';
import { 
  User,
  Mail,
  Moon,
  Sun,
  Bell,
  Shield,
  Info,
  Send,
  Loader2
} from 'lucide-react';
import { motion } from 'framer-motion';
import { toast } from 'sonner';

const SettingsPage = () => {
  const { user, dbUser } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [sendingTest, setSendingTest] = useState(false);

  const handleTestEmail = async () => {
    setSendingTest(true);
    try {
      const response = await sendTestEmail();
      toast.success(`Correo de prueba enviado a ${response.data.email}`);
    } catch (error) {
      console.error('Error sending test email:', error);
      toast.error('Error al enviar correo de prueba');
    } finally {
      setSendingTest(false);
    }
  };

  const getInitials = (name) => {
    if (!name) return 'U';
    return name
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  };

  return (
    <div className="space-y-6" data-testid="settings-page">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold tracking-tight">Configuración</h1>
        <p className="text-muted-foreground">
          Administra tu perfil y preferencias
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        {/* Profile Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <User className="w-5 h-5" />
                Perfil
              </CardTitle>
              <CardDescription>
                Información de tu cuenta
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center gap-4">
                <Avatar className="w-20 h-20">
                  <AvatarImage src={user?.photoURL} alt={user?.displayName} />
                  <AvatarFallback className="bg-primary text-primary-foreground text-xl">
                    {getInitials(user?.displayName || dbUser?.display_name)}
                  </AvatarFallback>
                </Avatar>
                <div>
                  <h3 className="text-lg font-semibold">
                    {user?.displayName || dbUser?.display_name || 'Usuario'}
                  </h3>
                  <p className="text-sm text-muted-foreground flex items-center gap-1">
                    <Mail className="w-4 h-4" />
                    {user?.email}
                  </p>
                </div>
              </div>

              <Separator />

              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">ID de usuario</span>
                  <span className="text-sm font-mono">{dbUser?.id?.slice(0, 8)}...</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Proveedor</span>
                  <span className="text-sm">Google</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Cuenta verificada</span>
                  <span className="text-sm text-green-500 flex items-center gap-1">
                    <Shield className="w-4 h-4" />
                    Sí
                  </span>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Appearance Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                {theme === 'dark' ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
                Apariencia
              </CardTitle>
              <CardDescription>
                Personaliza la interfaz
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="dark-mode">Modo oscuro</Label>
                  <p className="text-sm text-muted-foreground">
                    Activar tema oscuro en la aplicación
                  </p>
                </div>
                <Switch
                  id="dark-mode"
                  checked={theme === 'dark'}
                  onCheckedChange={toggleTheme}
                  data-testid="dark-mode-switch"
                />
              </div>

              <Separator />

              <div className="p-4 rounded-lg bg-secondary/50">
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium">Preferencia del sistema</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Tu preferencia de tema se guardará y se aplicará automáticamente en tus próximas visitas.
                    </p>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Notifications Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Bell className="w-5 h-5" />
                Notificaciones por Email
              </CardTitle>
              <CardDescription>
                Configuración de recordatorios
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="p-4 rounded-lg bg-amber-500/10 border border-amber-500/20">
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-amber-500">Estado del servicio</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Los correos se envían automáticamente según la configuración de cada evento.
                    </p>
                  </div>
                </div>
              </div>

              <Separator />

              <div>
                <Button 
                  onClick={handleTestEmail} 
                  disabled={sendingTest}
                  className="w-full"
                  variant="outline"
                >
                  {sendingTest ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Enviando...
                    </>
                  ) : (
                    <>
                      <Send className="w-4 h-4 mr-2" />
                      Enviar Correo de Prueba
                    </>
                  )}
                </Button>
                <p className="text-xs text-muted-foreground mt-2 text-center">
                  Se enviará un correo de prueba a tu dirección registrada
                </p>
              </div>

              <Separator />

              <div className="p-4 rounded-lg bg-secondary/50">
                <div className="flex items-start gap-3">
                  <Info className="w-5 h-5 text-amber-500 flex-shrink-0 mt-0.5" />
                  <div>
                    <p className="text-sm font-medium text-amber-500">Configuración SMTP</p>
                    <p className="text-xs text-muted-foreground mt-1">
                      Para habilitar el envío de correos, configura las credenciales SMTP en el archivo .env del backend.
                    </p>
                    <ul className="text-xs text-muted-foreground mt-2 space-y-1">
                      <li>• SMTP_HOST (ej: smtp.gmail.com)</li>
                      <li>• SMTP_PORT (ej: 587)</li>
                      <li>• SMTP_USER (tu correo)</li>
                      <li>• SMTP_PASSWORD (contraseña de aplicación)</li>
                    </ul>
                  </div>
                </div>
              </div>

              <div className="text-sm text-muted-foreground">
                <p>El sistema envía recordatorios automáticamente según los intervalos que configures en cada evento.</p>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* About Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Info className="w-5 h-5" />
                Acerca de
              </CardTitle>
              <CardDescription>
                Información del sistema
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Aplicación</span>
                  <span className="text-sm font-medium">RemindSender</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Versión</span>
                  <span className="text-sm font-mono">1.0.0</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Stack</span>
                  <span className="text-sm">React + FastAPI + MongoDB</span>
                </div>
              </div>

              <Separator />

              <p className="text-xs text-muted-foreground">
                Sistema de gestión de eventos con recordatorios automáticos por correo electrónico. 
                Los correos se envían según los intervalos configurados en cada evento.
              </p>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  );
};

export default SettingsPage;
